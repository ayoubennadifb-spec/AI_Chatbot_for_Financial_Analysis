"""
GFC Financial Chatbot — Flask Application Factory
==================================================
Run dev:        python app.py
Run production: gunicorn wsgi:app --workers 4
"""

import sys
import os
import logging
sys.path.insert(0, os.path.dirname(__file__))

from flask import Flask, send_from_directory
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

import config
from data.financial_data  import load as load_data
from rag.corpus_builder   import build_corpus
from rag.retriever        import Retriever
from nlp                  import intent_classifier
from api.chat             import chat_bp


def create_app() -> Flask:
    app = Flask(__name__, static_folder='frontend/static', static_url_path='/static')

    # ── Structured logging ─────────────────────────────────────────────────
    logging.basicConfig(
        level   = logging.INFO,
        format  = '%(asctime)s [%(levelname)s] %(name)s: %(message)s',
        datefmt = '%Y-%m-%d %H:%M:%S',
    )
    logger = logging.getLogger(__name__)

    # ── Rate limiting ──────────────────────────────────────────────────────
    limiter = Limiter(
        get_remote_address,
        app             = app,
        default_limits  = [config.RATE_LIMIT],
        storage_uri     = 'memory://',
    )
    limiter.limit(config.RATE_LIMIT)(chat_bp)

    # ── Startup: data pipeline with disk-cached models ─────────────────────
    logger.info('Loading financial data...')
    df = load_data()

    logger.info('Building RAG corpus...')
    corpus = build_corpus(df)

    logger.info('Loading/building RAG index (%d passages)...', len(corpus))
    retriever = Retriever(corpus, cache_dir=config.MODEL_CACHE_DIR)

    logger.info('Loading/training ML intent classifier...')
    intent_classifier.init(cache_dir=config.MODEL_CACHE_DIR)

    # ── Store shared objects ───────────────────────────────────────────────
    app.config['DATAFRAME'] = df
    app.config['RETRIEVER'] = retriever
    app.config['RAG_TOP_K'] = config.RAG_TOP_K

    # ── Blueprints ─────────────────────────────────────────────────────────
    app.register_blueprint(chat_bp)

    # ── Frontend ───────────────────────────────────────────────────────────
    @app.route('/')
    def index():
        return send_from_directory('frontend', 'index.html')

    @app.route('/favicon.ico')
    def favicon():
        return '', 204

    logger.info('GFC Financial Chatbot ready on port %d', config.PORT)
    return app


if __name__ == '__main__':
    app = create_app()
    app.run(host=config.HOST, port=config.PORT, debug=config.DEBUG)
