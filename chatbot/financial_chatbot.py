"""
BCG GenAI Consulting -- AI-Powered Financial Chatbot
====================================================
Client   : Global Finance Corp. (GFC)
Author   : Ayoub (Junior Data Scientist, BCG GenAI Team)
Manager  : Aisha (Senior Data Scientist)

Description:
    Rule-based financial chatbot that answers predefined queries about
    Microsoft, Tesla, and Apple using 10-K data from FY2021-FY2023.
    Supports flexible keyword matching so users don't need exact phrasing.
"""

import pandas as pd

# ─────────────────────────────────────────────
# 1. FINANCIAL DATA (from Task 1 analysis)
# ─────────────────────────────────────────────

data = {
    'Company': [
        'Microsoft', 'Microsoft', 'Microsoft',
        'Tesla',     'Tesla',     'Tesla',
        'Apple',     'Apple',     'Apple'
    ],
    'Fiscal Year': [2021, 2022, 2023, 2021, 2022, 2023, 2021, 2022, 2023],
    'Total Revenue (B)':          [168.09, 198.27, 211.92,  53.82,  81.46,  97.69, 365.82, 394.33, 383.29],
    'Net Income (B)':             [ 61.27,  72.74,  72.36,   5.52,  12.56,  14.97,  94.68,  99.80,  96.99],
    'Total Assets (B)':           [333.78, 364.84, 411.98,  62.13,  82.34, 106.62, 351.00, 352.76, 352.58],
    'Total Liabilities (B)':      [191.79, 198.30, 205.75,  30.55,  36.44,  43.00, 287.91, 302.08, 290.44],
    'Operating Cash Flow (B)':    [ 76.74,  89.04,  87.91,  11.50,  14.48,  13.26, 104.04, 122.15, 114.00],
}

df = pd.DataFrame(data)
df = df.sort_values(['Company', 'Fiscal Year']).reset_index(drop=True)

# Derived metrics
df['Net Profit Margin (%)']   = (df['Net Income (B)'] / df['Total Revenue (B)']) * 100
df['Debt Ratio']              = df['Total Liabilities (B)'] / df['Total Assets (B)']
df['Shareholders Equity (B)'] = df['Total Assets (B)'] - df['Total Liabilities (B)']
df['Revenue Growth (%)']      = df.groupby('Company')['Total Revenue (B)'].pct_change() * 100
df['Net Income Growth (%)']   = df.groupby('Company')['Net Income (B)'].pct_change() * 100

COMPANIES = ['microsoft', 'tesla', 'apple']
YEARS     = [2021, 2022, 2023]


# ─────────────────────────────────────────────
# 2. HELPER UTILITIES
# ─────────────────────────────────────────────

def detect_company(query: str) -> str | None:
    """Return the company name mentioned in the query, or None."""
    q = query.lower()
    for c in COMPANIES:
        if c in q:
            return c.capitalize()
    return None


def detect_year(query: str) -> int | None:
    """Return the fiscal year mentioned in the query, or None."""
    for y in YEARS:
        if str(y) in query:
            return y
    return None


def get_row(company: str, year: int) -> pd.Series:
    return df[(df['Company'] == company) & (df['Fiscal Year'] == year)].iloc[0]


def fmt(value: float, suffix: str = 'B') -> str:
    return f"${value:.2f}{suffix}"


# ─────────────────────────────────────────────
# 3. RESPONSE HANDLERS
# ─────────────────────────────────────────────

def handle_revenue(query: str) -> str:
    company = detect_company(query)
    year    = detect_year(query)

    if company and year:
        row = get_row(company, year)
        return (f"{company}'s total revenue in FY{year} was {fmt(row['Total Revenue (B)'])}.\n"
                f"  Net Profit Margin: {row['Net Profit Margin (%)']:.1f}%")

    if company:
        sub = df[df['Company'] == company][['Fiscal Year', 'Total Revenue (B)', 'Revenue Growth (%)']].copy()
        lines = [f"{company} -- Total Revenue (FY2021-FY2023):"]
        for _, r in sub.iterrows():
            growth = f"  |  YoY Growth: {r['Revenue Growth (%)']:+.1f}%" if not pd.isna(r['Revenue Growth (%)']) else ""
            lines.append(f"  FY{int(r['Fiscal Year'])}: {fmt(r['Total Revenue (B)'])}{growth}")
        return '\n'.join(lines)

    # All companies latest year
    latest = df[df['Fiscal Year'] == 2023][['Company', 'Total Revenue (B)']].copy()
    lines = ["Total Revenue -- FY2023 Comparison:"]
    for _, r in latest.iterrows():
        lines.append(f"  {r['Company']:<12} {fmt(r['Total Revenue (B)'])}")
    return '\n'.join(lines)


def handle_net_income(query: str) -> str:
    company = detect_company(query)
    year    = detect_year(query)

    if company and year:
        row = get_row(company, year)
        return (f"{company}'s net income in FY{year} was {fmt(row['Net Income (B)'])}.\n"
                f"  Net Profit Margin: {row['Net Profit Margin (%)']:.1f}%")

    if company:
        sub = df[df['Company'] == company][['Fiscal Year', 'Net Income (B)', 'Net Income Growth (%)']].copy()
        lines = [f"{company} -- Net Income (FY2021-FY2023):"]
        for _, r in sub.iterrows():
            growth = f"  |  YoY Change: {r['Net Income Growth (%)']:+.1f}%" if not pd.isna(r['Net Income Growth (%)']) else ""
            lines.append(f"  FY{int(r['Fiscal Year'])}: {fmt(r['Net Income (B)'])}{growth}")
        return '\n'.join(lines)

    latest = df[df['Fiscal Year'] == 2023][['Company', 'Net Income (B)', 'Net Profit Margin (%)']].copy()
    lines = ["Net Income -- FY2023 Comparison:"]
    for _, r in latest.iterrows():
        lines.append(f"  {r['Company']:<12} {fmt(r['Net Income (B)'])}  (margin: {r['Net Profit Margin (%)']:.1f}%)")
    return '\n'.join(lines)


def handle_assets(query: str) -> str:
    company = detect_company(query)
    year    = detect_year(query)

    if company and year:
        row = get_row(company, year)
        return (f"{company} FY{year} Balance Sheet Summary:\n"
                f"  Total Assets      : {fmt(row['Total Assets (B)'])}\n"
                f"  Total Liabilities : {fmt(row['Total Liabilities (B)'])}\n"
                f"  Shareholders Equity: {fmt(row['Shareholders Equity (B)'])}\n"
                f"  Debt Ratio        : {row['Debt Ratio']:.2f} ({row['Debt Ratio']*100:.1f}%)")

    if company:
        sub = df[df['Company'] == company][['Fiscal Year', 'Total Assets (B)', 'Total Liabilities (B)', 'Debt Ratio']].copy()
        lines = [f"{company} -- Assets & Liabilities (FY2021-FY2023):"]
        for _, r in sub.iterrows():
            lines.append(f"  FY{int(r['Fiscal Year'])}: Assets {fmt(r['Total Assets (B)'])}  |  "
                         f"Liabilities {fmt(r['Total Liabilities (B)'])}  |  Debt Ratio {r['Debt Ratio']:.2f}")
        return '\n'.join(lines)

    latest = df[df['Fiscal Year'] == 2023][['Company', 'Total Assets (B)', 'Debt Ratio']].copy()
    lines = ["Total Assets & Debt Ratio -- FY2023:"]
    for _, r in latest.iterrows():
        lines.append(f"  {r['Company']:<12} Assets: {fmt(r['Total Assets (B)'])}  |  Debt Ratio: {r['Debt Ratio']:.2f}")
    return '\n'.join(lines)


def handle_cash_flow(query: str) -> str:
    company = detect_company(query)
    year    = detect_year(query)

    if company and year:
        row = get_row(company, year)
        margin = (row['Operating Cash Flow (B)'] / row['Total Revenue (B)']) * 100
        return (f"{company}'s operating cash flow in FY{year} was {fmt(row['Operating Cash Flow (B)'])}.\n"
                f"  Cash Flow Margin: {margin:.1f}% of revenue")

    if company:
        sub = df[df['Company'] == company][['Fiscal Year', 'Operating Cash Flow (B)', 'Total Revenue (B)']].copy()
        lines = [f"{company} -- Operating Cash Flow (FY2021-FY2023):"]
        for _, r in sub.iterrows():
            margin = (r['Operating Cash Flow (B)'] / r['Total Revenue (B)']) * 100
            lines.append(f"  FY{int(r['Fiscal Year'])}: {fmt(r['Operating Cash Flow (B)'])}  (CF margin: {margin:.1f}%)")
        return '\n'.join(lines)

    latest = df[df['Fiscal Year'] == 2023][['Company', 'Operating Cash Flow (B)']].copy()
    lines = ["Operating Cash Flow -- FY2023 Comparison:"]
    for _, r in latest.iterrows():
        lines.append(f"  {r['Company']:<12} {fmt(r['Operating Cash Flow (B)'])}")
    return '\n'.join(lines)


def handle_growth(query: str) -> str:
    company = detect_company(query)

    if company:
        sub = df[df['Company'] == company][
            ['Fiscal Year', 'Revenue Growth (%)', 'Net Income Growth (%)']
        ].dropna()
        lines = [f"{company} -- Year-over-Year Growth:"]
        for _, r in sub.iterrows():
            lines.append(f"  FY{int(r['Fiscal Year'])}: Revenue {r['Revenue Growth (%)']:+.1f}%  |  "
                         f"Net Income {r['Net Income Growth (%)']:+.1f}%")
        return '\n'.join(lines)

    # All companies
    sub = df[df['Fiscal Year'] == 2023][['Company', 'Revenue Growth (%)', 'Net Income Growth (%)']].copy()
    lines = ["YoY Growth FY2022→FY2023:"]
    for _, r in sub.iterrows():
        lines.append(f"  {r['Company']:<12} Revenue: {r['Revenue Growth (%)']:+.1f}%  |  "
                     f"Net Income: {r['Net Income Growth (%)']:+.1f}%")
    return '\n'.join(lines)


def handle_summary(query: str) -> str:
    company = detect_company(query)

    summaries = {
        'Microsoft': (
            "Microsoft shows stable, high-margin growth driven by Azure cloud and enterprise software.\n"
            "  * Revenue grew 26% over FY2021-FY2023 ($168B → $212B)\n"
            "  * Net profit margin consistently ~34% -- exceptional for any industry\n"
            "  * Debt ratio stable at ~50%, well-managed leverage\n"
            "  * Generates ~$88B in operating cash flow annually\n"
            "  → Financial health: STRONG"
        ),
        'Tesla': (
            "Tesla shows explosive growth with improving but pressured profitability.\n"
            "  * Revenue grew 81% over FY2021-FY2023 ($54B → $98B)\n"
            "  * Net profit margin improved from 10% to 15%, but OCF dipped in FY2023\n"
            "  * Debt ratio low at ~40%, healthy balance sheet\n"
            "  * FY2023 OCF decline reflects margin pressure from price cuts\n"
            "  → Financial health: GROWING but VOLATILE"
        ),
        'Apple': (
            "Apple is a cash-generating machine with a mature, slightly slowing top line.\n"
            "  * Revenue peaked at $394B (FY2022), slight dip to $383B in FY2023\n"
            "  * Net profit margin ~25%, driven by premium pricing and services\n"
            "  * High debt ratio (~82%) is intentional -- funds share buybacks cheaply\n"
            "  * $114B operating cash flow in FY2023 -- world-class capital generation\n"
            "  → Financial health: STRONG with deliberate leverage strategy"
        )
    }

    if company and company in summaries:
        return f"{company} -- Financial Health Summary:\n{summaries[company]}"

    lines = ["Financial Health Summary -- All Companies (FY2021-FY2023):"]
    for c, s in summaries.items():
        lines.append(f"\n{'─'*50}\n{c}:\n{s}")
    return '\n'.join(lines)


def handle_compare(query: str) -> str:
    fy2023 = df[df['Fiscal Year'] == 2023].copy()
    lines = [
        "─" * 62,
        f"{'Metric':<30} {'Microsoft':>10} {'Tesla':>10} {'Apple':>10}",
        "─" * 62,
    ]
    metrics = [
        ('Total Revenue (B)',       'Revenue ($B)',        'fmt'),
        ('Net Income (B)',          'Net Income ($B)',     'fmt'),
        ('Net Profit Margin (%)',   'Profit Margin',       'pct'),
        ('Total Assets (B)',        'Total Assets ($B)',   'fmt'),
        ('Debt Ratio',              'Debt Ratio',          'ratio'),
        ('Operating Cash Flow (B)', 'Op. Cash Flow ($B)', 'fmt'),
    ]
    for col, label, style in metrics:
        row_vals = {r['Company']: r[col] for _, r in fy2023.iterrows()}
        def fmtv(v, s):
            if s == 'fmt':   return f"${v:.1f}B"
            if s == 'pct':   return f"{v:.1f}%"
            if s == 'ratio': return f"{v:.2f}"
        lines.append(
            f"{label:<30} "
            f"{fmtv(row_vals['Microsoft'], style):>10} "
            f"{fmtv(row_vals['Tesla'], style):>10} "
            f"{fmtv(row_vals['Apple'], style):>10}"
        )
    lines.append("─" * 62)
    return '\n'.join(lines)


def handle_help() -> str:
    return """
Available queries -- you can ask in natural language:

  📊 REVENUE
     "What is Apple's total revenue?"
     "Show Microsoft revenue for 2022"
     "Compare revenue across all companies"

  💰 NET INCOME
     "What is Tesla's net income?"
     "How has Apple's net income changed?"

  🏦 ASSETS & LIABILITIES
     "What are Microsoft's total assets?"
     "Show Tesla's balance sheet for 2023"

  💵 CASH FLOW
     "What is Apple's operating cash flow?"
     "Show Tesla cash flow trend"

  📈 GROWTH
     "What is Microsoft's revenue growth?"
     "Show growth for all companies"

  🔍 SUMMARY / HEALTH
     "Summarize Apple's financial health"
     "Give me a summary of all companies"

  ⚖️  COMPARE
     "Compare all companies"
     "Show comparison table"

  ❓ HELP
     "help" or "?"

  Type 'exit' or 'quit' to leave.
"""


# ─────────────────────────────────────────────
# 4. MAIN CHATBOT ROUTER
# ─────────────────────────────────────────────

INTENT_KEYWORDS = {
    'revenue':   ['revenue', 'sales', 'turnover', 'income from operations'],
    'net_income':['net income', 'profit', 'earnings', 'net profit', 'bottom line'],
    'assets':    ['asset', 'liabilit', 'balance sheet', 'equity', 'debt ratio'],
    'cash_flow': ['cash flow', 'operating cash', 'cashflow', 'ocf'],
    'growth':    ['growth', 'grew', 'increase', 'change', 'trend', 'year over year', 'yoy'],
    'summary':   ['summary', 'summarize', 'health', 'overview', 'performance', 'how is', 'how did'],
    'compare':   ['compare', 'comparison', 'versus', 'vs', 'all companies', 'table'],
    'help':      ['help', '?', 'what can you', 'queries', 'commands'],
}


def route(query: str) -> str:
    q = query.lower().strip()

    if q in ('exit', 'quit', 'bye', 'q'):
        return '__EXIT__'

    for intent, keywords in INTENT_KEYWORDS.items():
        if any(kw in q for kw in keywords):
            if intent == 'revenue':    return handle_revenue(q)
            if intent == 'net_income': return handle_net_income(q)
            if intent == 'assets':     return handle_assets(q)
            if intent == 'cash_flow':  return handle_cash_flow(q)
            if intent == 'growth':     return handle_growth(q)
            if intent == 'summary':    return handle_summary(q)
            if intent == 'compare':    return handle_compare(q)
            if intent == 'help':       return handle_help()

    return (
        "Sorry, I didn't understand that query.\n"
        "Try asking about: revenue, net income, assets, cash flow, growth, or summary.\n"
        "Type 'help' to see all available queries."
    )


# ─────────────────────────────────────────────
# 5. MAIN LOOP
# ─────────────────────────────────────────────

BANNER = """
================================================================
   BCG GenAI -- GFC Financial Analysis Chatbot
   Companies: Microsoft | Tesla | Apple
   Data: 10-K Filings FY2021 - FY2023
   Type 'help' for available queries | 'exit' to quit
================================================================
"""

if __name__ == '__main__':
    print(BANNER)
    while True:
        try:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            response = route(user_input)
            if response == '__EXIT__':
                print("Chatbot: Goodbye! Have a great day.")
                break
            print(f"\nChatbot:\n{response}\n")
        except (KeyboardInterrupt, EOFError):
            print("\nChatbot: Session ended.")
            break
