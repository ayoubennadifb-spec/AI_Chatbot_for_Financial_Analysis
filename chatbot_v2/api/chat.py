"""
Flask Chat API Blueprint
========================
POST /api/chat   — NLP -> ML -> RAG -> LLM pipeline
GET  /api/health — health + cache stats
"""

from flask import Blueprint, request, jsonify, current_app
import time
import logging

from nlp.entity_extractor   import extract_entities
from nlp.intent_classifier  import predict as classify_intent
from response               import rule_based, llm_adapter
from cache                  import response_cache

logger  = logging.getLogger(__name__)
chat_bp = Blueprint('chat', __name__)


@chat_bp.route('/api/health', methods=['GET'])
def health():
    return jsonify({
        'status':  'ok',
        'message': 'GFC Financial Chatbot is running.',
        'cache':   response_cache.stats(),
    })


@chat_bp.route('/api/chat', methods=['POST'])
def chat():
    start   = time.time()
    payload = request.get_json(silent=True) or {}
    query   = (payload.get('query') or '').strip()

    if not query:
        return jsonify({'error': 'Query cannot be empty.'}), 400

    # 1. NLP — extract entities
    entities = extract_entities(query)
    company  = entities['company']
    year     = entities['year']

    # 2. ML — classify intent
    intent, confidence = classify_intent(query)

    logger.info('query=%r intent=%s confidence=%.2f company=%s year=%s',
                query, intent, confidence, company, year)

    # 3. Cache check — skip LLM if identical query was seen recently
    cached = response_cache.get(query, intent)
    if cached:
        logger.info('cache_hit query=%r', query)
        elapsed = round((time.time() - start) * 1000, 1)
        return jsonify({
            'response':   cached,
            'intent':     intent,
            'confidence': round(confidence, 3),
            'entities':   entities,
            'context':    '',
            'elapsed_ms': elapsed,
            'cached':     True,
        })

    # 4. RAG — retrieve relevant context passages
    retriever = current_app.config['RETRIEVER']
    context   = retriever.get_context(
        query   = query,
        top_k   = current_app.config.get('RAG_TOP_K', 5),
        company = company,
        topic   = intent if intent not in ('help', 'compare', 'summary') else None,
    )

    # 5. Build grounded context (exact data + RAG passages)
    df         = current_app.config['DATAFRAME']
    structured = rule_based.generate(intent, df, company, year, query)
    full_context = (
        f"EXACT DATA (use these numbers only):\n{structured}\n\n"
        f"ADDITIONAL CONTEXT:\n{context}"
    )

    # 6. LLM response generation with rule-based fallback
    try:
        response = llm_adapter.generate(query=query, context=full_context)
        response_cache.set(query, intent, response)
    except Exception as e:
        logger.warning('LLM failed, using rule-based fallback: %s', e)
        response = structured

    elapsed = round((time.time() - start) * 1000, 1)
    logger.info('response_time_ms=%.1f cached=False', elapsed)

    return jsonify({
        'response':   response,
        'intent':     intent,
        'confidence': round(confidence, 3),
        'entities':   entities,
        'context':    context,
        'elapsed_ms': elapsed,
        'cached':     False,
    })
