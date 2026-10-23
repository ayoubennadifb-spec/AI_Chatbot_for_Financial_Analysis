"""
RAG Retriever — with disk persistence
======================================
Saves/loads the TF-IDF index to disk via joblib.
Cold start: builds + saves. Warm start: loads in <100ms.
"""

import numpy as np
import joblib
import hashlib
import json
import logging
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

logger = logging.getLogger(__name__)


def _corpus_hash(passages: list[dict]) -> str:
    """Fingerprint the corpus so we rebuild if data changes."""
    raw = json.dumps([p['text'] for p in passages], sort_keys=True)
    return hashlib.md5(raw.encode()).hexdigest()[:12]


class Retriever:
    def __init__(self, passages: list[dict], cache_dir: Path = None):
        self.passages = passages
        self._texts   = [p['text'] for p in passages]
        self._load_or_build(cache_dir)

    def _load_or_build(self, cache_dir: Path):
        if cache_dir is None:
            self._build()
            return

        h         = _corpus_hash(self.passages)
        vec_path  = cache_dir / f'rag_vectorizer_{h}.joblib'
        mat_path  = cache_dir / f'rag_matrix_{h}.joblib'

        if vec_path.exists() and mat_path.exists():
            logger.info('[RAG] Loading index from disk (hash=%s)', h)
            self._vectorizer = joblib.load(vec_path)
            self._matrix     = joblib.load(mat_path)
        else:
            logger.info('[RAG] Building new index (hash=%s)', h)
            self._build()
            joblib.dump(self._vectorizer, vec_path)
            joblib.dump(self._matrix,     mat_path)
            logger.info('[RAG] Index saved to disk')

    def _build(self):
        self._vectorizer = TfidfVectorizer(ngram_range=(1, 2), min_df=1)
        self._matrix     = self._vectorizer.fit_transform(self._texts)

    def retrieve(self, query: str, top_k: int = 5,
                 company: str = None, topic: str = None) -> list[dict]:
        candidates = self.passages
        if company:
            candidates = [p for p in candidates if p['company'] in (company, 'All')]
        if topic:
            candidates = [p for p in candidates if p['topic'] == topic]
        if not candidates:
            candidates = self.passages

        candidate_texts  = [p['text'] for p in candidates]
        candidate_matrix = self._vectorizer.transform(candidate_texts)
        query_vec        = self._vectorizer.transform([query])
        scores           = cosine_similarity(query_vec, candidate_matrix).flatten()

        top_indices = np.argsort(scores)[::-1][:top_k]
        return [
            {**candidates[i], 'score': float(scores[i])}
            for i in top_indices if scores[i] > 0
        ]

    def get_context(self, query: str, top_k: int = 5,
                    company: str = None, topic: str = None) -> str:
        results = self.retrieve(query, top_k=top_k, company=company, topic=topic)
        return '\n'.join(r['text'] for r in results)
