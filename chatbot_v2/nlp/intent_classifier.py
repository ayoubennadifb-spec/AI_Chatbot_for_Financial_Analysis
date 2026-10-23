"""
ML Intent Classifier
====================
TF-IDF + Logistic Regression trained at startup on synthetic labeled examples.
Classifies user queries into one of 8 intent categories.
"""

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.pipeline import Pipeline
import numpy as np

# ── Training data (synthetic labeled examples) ──────────────────────────────

INTENTS = {
    'revenue': [
        "What is the total revenue?",
        "Show me Apple's revenue",
        "How much did Microsoft earn in sales?",
        "What were Tesla's total sales in 2022?",
        "Revenue figures for Apple",
        "How much revenue did Tesla generate?",
        "Tell me about Microsoft's turnover",
        "What is Apple's income from sales?",
        "Give me the revenue breakdown",
        "Total sales for 2023",
        "How did revenue change over the years?",
        "What is the annual revenue?",
        "Show revenue trend for Tesla",
    ],
    'net_income': [
        "What is the net income?",
        "How profitable is Apple?",
        "Show me Tesla's profit",
        "What were Microsoft's earnings?",
        "Net profit for Apple 2023",
        "How much did they make after taxes?",
        "What is the bottom line?",
        "Tell me about profitability",
        "How has net income changed?",
        "Profit margin for Microsoft",
        "What is Apple's net profit margin?",
        "Earnings trend for Tesla",
        "How profitable is the company?",
        "What is the profit percentage?",
    ],
    'assets': [
        "What are the total assets?",
        "Show me the balance sheet",
        "How much does Apple owe?",
        "What are Microsoft's liabilities?",
        "Tell me about the debt",
        "What is the debt ratio?",
        "How leveraged is Tesla?",
        "Shareholders equity for Apple",
        "What is the equity value?",
        "How much debt does Microsoft have?",
        "Total liabilities for Tesla",
        "Balance sheet overview",
        "Assets and liabilities breakdown",
        "How is the company financed?",
    ],
    'cash_flow': [
        "What is the operating cash flow?",
        "How much cash did Apple generate?",
        "Show me Tesla's cash flow",
        "Cash flow from operations",
        "How liquid is Microsoft?",
        "What is the cash flow margin?",
        "Cash generation for Apple",
        "Operating cash for Tesla 2023",
        "How much cash does the company produce?",
        "Free cash flow analysis",
        "Cash flow trend for Microsoft",
        "Is the company cash flow positive?",
    ],
    'growth': [
        "What is the revenue growth?",
        "How fast is Tesla growing?",
        "Year over year growth for Apple",
        "Show me the growth rate",
        "How did Microsoft grow?",
        "Revenue increase over time",
        "Growth trend analysis",
        "How much has income increased?",
        "YoY change in revenue",
        "Is Tesla growing faster than Apple?",
        "What is the compound growth?",
        "Growth comparison between companies",
        "How quickly is the company expanding?",
    ],
    'summary': [
        "Summarize Apple's financial health",
        "Give me an overview of Microsoft",
        "How is Tesla performing overall?",
        "What is the financial status?",
        "Tell me about Apple's performance",
        "Overall financial summary",
        "Financial health assessment",
        "How is the company doing?",
        "Give me a quick overview",
        "What should I know about Tesla?",
        "Assess Microsoft's financial position",
        "Company performance overview",
        "Is Apple in good financial shape?",
    ],
    'compare': [
        "Compare all companies",
        "Which company is more profitable?",
        "Show a comparison table",
        "Microsoft vs Apple vs Tesla",
        "How do they compare?",
        "Side by side comparison",
        "Who has the highest revenue?",
        "Compare profitability across companies",
        "Which company has the best margins?",
        "Comparison of all three companies",
        "Benchmark comparison",
        "Who is the strongest financially?",
        "Rank the companies by revenue",
    ],
    'help': [
        "help",
        "what can you do?",
        "show available commands",
        "what queries can I ask?",
        "how do I use this chatbot?",
        "list all options",
        "what are the features?",
        "guide me",
        "I need assistance",
        "show me examples",
    ],
}

# ── Build training corpus ────────────────────────────────────────────────────

_X_train, _y_train = [], []
for intent, examples in INTENTS.items():
    for example in examples:
        _X_train.append(example)
        _y_train.append(intent)

# ── Train or load pipeline from disk ─────────────────────────────────────────

import joblib, hashlib, logging
from pathlib import Path

logger = logging.getLogger(__name__)

def _model_path(cache_dir: Path) -> Path:
    h = hashlib.md5(''.join(_X_train).encode()).hexdigest()[:12]
    return cache_dir / f'intent_classifier_{h}.joblib'

def _load_or_train(cache_dir: Path = None) -> Pipeline:
    if cache_dir:
        path = _model_path(cache_dir)
        if path.exists():
            logger.info('[ML] Loading classifier from disk')
            return joblib.load(path)
    logger.info('[ML] Training classifier')
    p = Pipeline([
        ('tfidf', TfidfVectorizer(ngram_range=(1, 2), min_df=1)),
        ('clf',   LogisticRegression(max_iter=1000, C=1.0, random_state=42)),
    ])
    p.fit(_X_train, _y_train)
    if cache_dir:
        joblib.dump(p, _model_path(cache_dir))
        logger.info('[ML] Classifier saved to disk')
    return p

_pipeline     = _load_or_train()   # default: no cache (safe for import)
INTENT_LABELS = list(INTENTS.keys())


def init(cache_dir: Path):
    """Call once at app startup with cache_dir to enable disk persistence."""
    global _pipeline
    _pipeline = _load_or_train(cache_dir)


def predict(query: str) -> tuple[str, float]:
    """
    Classify query into an intent.
    Returns (intent_label, confidence_score).
    """
    proba = _pipeline.predict_proba([query])[0]
    idx   = int(np.argmax(proba))
    label = _pipeline.classes_[idx]
    conf  = float(proba[idx])
    return label, conf
