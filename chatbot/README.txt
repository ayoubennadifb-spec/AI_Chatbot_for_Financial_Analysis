BCG GenAI Consulting — GFC Financial Chatbot
=============================================
Author  : Ayoub (Junior Data Scientist, BCG GenAI Team)
Manager : Aisha (Senior Data Scientist)
Client  : Global Finance Corp. (GFC)

─────────────────────────────────────────────
HOW TO RUN
─────────────────────────────────────────────
Requirements:
  pip install pandas

Run the chatbot:
  python financial_chatbot.py

─────────────────────────────────────────────
HOW IT WORKS
─────────────────────────────────────────────
The chatbot uses rule-based intent detection:

1. The user's query is converted to lowercase.
2. Keywords are matched against intent categories
   (revenue, net_income, assets, cash_flow, growth, summary, compare).
3. Company names (Microsoft, Tesla, Apple) and fiscal years (2021–2023)
   are extracted from the query automatically.
4. The matched handler fetches the relevant data from a pandas DataFrame
   built from manually extracted 10-K filings and returns a formatted response.

This approach is more flexible than exact-string matching — users can
phrase queries naturally as long as they include a recognized keyword.

─────────────────────────────────────────────
PREDEFINED QUERY CATEGORIES
─────────────────────────────────────────────
1. Revenue       — total revenue, sales, year-over-year
2. Net Income    — profitability, margins, earnings
3. Assets        — balance sheet, liabilities, debt ratio, equity
4. Cash Flow     — operating cash flow, CF margin
5. Growth        — YoY revenue and net income growth rates
6. Summary       — financial health narrative per company
7. Compare       — side-by-side FY2023 comparison table
8. Help          — lists all available query types

─────────────────────────────────────────────
EXAMPLE QUERIES
─────────────────────────────────────────────
  "What is Apple's total revenue?"
  "Show Microsoft revenue for 2022"
  "What is Tesla's net income growth?"
  "Compare all companies"
  "Summarize Apple's financial health"
  "What are Microsoft's total assets for 2023?"
  "Show Tesla cash flow trend"
  "help"

─────────────────────────────────────────────
DATA SOURCES
─────────────────────────────────────────────
All financial data manually extracted from SEC EDGAR 10-K filings:
  • Microsoft (CIK 0000789019) — FY2021, FY2022, FY2023
  • Tesla     (CIK 0001318605) — FY2021, FY2022, FY2023
  • Apple     (CIK 0000320193) — FY2021, FY2022, FY2023

Figures reported in billions USD.

─────────────────────────────────────────────
LIMITATIONS
─────────────────────────────────────────────
1. Rule-based only — cannot answer questions outside predefined categories.
2. No NLP model — relies on keyword matching, so unusual phrasing may fail.
3. Data is static — not connected to live financial feeds.
4. Covers only 3 companies and 3 fiscal years (FY2021–FY2023).
5. Text-only interface — no charts or visual output in the CLI.

─────────────────────────────────────────────
FUTURE ENHANCEMENTS (for production version)
─────────────────────────────────────────────
- Integrate an LLM (e.g., Claude/GPT) for true natural language understanding
- Connect to SEC EDGAR API or financial data APIs for real-time data
- Add a web UI (Flask/Streamlit) for a more user-friendly interface
- Expand coverage to more companies and financial metrics
- Add RAG (Retrieval-Augmented Generation) over full 10-K PDF documents
