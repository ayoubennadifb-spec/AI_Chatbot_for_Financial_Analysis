# GFC Financial Chatbot v2 — Production-Ready

**BCG GenAI Consulting Team | Client: Global Finance Corp.**

## Quick Start

```bash
pip install -r requirements.txt
python app.py
```

Open http://localhost:5000

## Architecture

```
User query
    │
    ▼
NLP Entity Extractor      ← extracts company name + fiscal year (regex)
    │
    ▼
ML Intent Classifier      ← TF-IDF + Logistic Regression (8 intent classes)
    │
    ▼
RAG Retriever             ← TF-IDF cosine similarity over 37 financial passages
    │
    ▼
Rule-Based Response Gen   ← structured markdown responses from pandas DataFrame
    │
    ▼
Flask REST API            ← POST /api/chat → JSON
    │
    ▼
Chat UI (HTML/CSS/JS)     ← dark finance theme, quick buttons, debug panel
```

## Components

| Module | Technology | Purpose |
|---|---|---|
| `nlp/entity_extractor.py` | Regex | Extract company + year from query |
| `nlp/intent_classifier.py` | TF-IDF + LogisticRegression | Classify query intent (8 classes) |
| `rag/corpus_builder.py` | Pandas | Convert DataFrame to text passages |
| `rag/retriever.py` | TF-IDF + cosine similarity | Semantic search over corpus |
| `response/rule_based.py` | Pandas + string templates | Generate formatted responses |
| `api/chat.py` | Flask Blueprint | REST endpoint orchestration |
| `frontend/` | HTML/CSS/JS | Chat UI with dark finance theme |

## Supported Intents

- `revenue` — total revenue, sales trends
- `net_income` — profitability, margins
- `assets` — balance sheet, debt ratio, equity
- `cash_flow` — operating cash flow
- `growth` — year-over-year changes
- `summary` — financial health assessment
- `compare` — cross-company FY2023 table
- `help` — available queries

## Coverage

Companies: Microsoft · Tesla · Apple
Data: SEC EDGAR 10-K filings FY2021–FY2023
