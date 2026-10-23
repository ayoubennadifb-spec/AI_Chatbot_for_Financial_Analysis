"""
Rule-Based Response Generator
==============================
Generates structured, data-driven responses from the financial DataFrame
based on detected intent and extracted entities.
Falls back gracefully when specific data is unavailable.
"""

import pandas as pd


def _fmt(val: float) -> str:
    return f"${val:.2f}B"


def _pct(val: float) -> str:
    return f"{val:.1f}%"


def _sign(val: float) -> str:
    return f"{val:+.1f}%"


# ── Intent handlers ──────────────────────────────────────────────────────────

def revenue(df: pd.DataFrame, company: str, year: int) -> str:
    if company and year:
        row = df[(df['company'] == company) & (df['year'] == year)]
        if row.empty:
            return f"No revenue data found for {company} in FY{year}."
        r = row.iloc[0]
        growth = f" (YoY growth: {_sign(r['revenue_growth'])})" if not pd.isna(r['revenue_growth']) else ""
        return (
            f"**{company} — Total Revenue FY{year}**\n\n"
            f"- Revenue: **{_fmt(r['revenue'])}**{growth}\n"
            f"- Net Income: {_fmt(r['net_income'])}\n"
            f"- Profit Margin: {_pct(r['profit_margin'])}"
        )

    if company:
        sub = df[df['company'] == company].sort_values('year')
        lines = [f"**{company} — Revenue Trend (FY2021–FY2023)**\n"]
        for _, r in sub.iterrows():
            growth = f" | YoY: {_sign(r['revenue_growth'])}" if not pd.isna(r['revenue_growth']) else ""
            lines.append(f"- FY{int(r['year'])}: **{_fmt(r['revenue'])}**{growth}")
        return '\n'.join(lines)

    fy2023 = df[df['year'] == 2023].sort_values('revenue', ascending=False)
    lines = ["**Revenue Comparison — FY2023**\n"]
    for _, r in fy2023.iterrows():
        lines.append(f"- {r['company']}: **{_fmt(r['revenue'])}** (margin: {_pct(r['profit_margin'])})")
    return '\n'.join(lines)


def net_income(df: pd.DataFrame, company: str, year: int) -> str:
    if company and year:
        row = df[(df['company'] == company) & (df['year'] == year)]
        if row.empty:
            return f"No net income data found for {company} in FY{year}."
        r = row.iloc[0]
        change = f" (YoY change: {_sign(r['net_income_growth'])})" if not pd.isna(r['net_income_growth']) else ""
        return (
            f"**{company} — Net Income FY{year}**\n\n"
            f"- Net Income: **{_fmt(r['net_income'])}**{change}\n"
            f"- Profit Margin: {_pct(r['profit_margin'])}\n"
            f"- Revenue: {_fmt(r['revenue'])}"
        )

    if company:
        sub = df[df['company'] == company].sort_values('year')
        lines = [f"**{company} — Net Income Trend (FY2021–FY2023)**\n"]
        for _, r in sub.iterrows():
            change = f" | YoY: {_sign(r['net_income_growth'])}" if not pd.isna(r['net_income_growth']) else ""
            lines.append(f"- FY{int(r['year'])}: **{_fmt(r['net_income'])}** (margin: {_pct(r['profit_margin'])}){change}")
        return '\n'.join(lines)

    fy2023 = df[df['year'] == 2023].sort_values('net_income', ascending=False)
    lines = ["**Net Income Comparison — FY2023**\n"]
    for _, r in fy2023.iterrows():
        lines.append(f"- {r['company']}: **{_fmt(r['net_income'])}** ({_pct(r['profit_margin'])} margin)")
    return '\n'.join(lines)


def assets(df: pd.DataFrame, company: str, year: int) -> str:
    if company and year:
        row = df[(df['company'] == company) & (df['year'] == year)]
        if row.empty:
            return f"No balance sheet data found for {company} in FY{year}."
        r = row.iloc[0]
        risk = "HIGH (intentional leverage strategy)" if r['debt_ratio'] > 0.7 else \
               "MODERATE" if r['debt_ratio'] > 0.5 else "LOW"
        return (
            f"**{company} — Balance Sheet FY{year}**\n\n"
            f"- Total Assets: **{_fmt(r['total_assets'])}**\n"
            f"- Total Liabilities: {_fmt(r['total_liabilities'])}\n"
            f"- Shareholders' Equity: {_fmt(r['equity'])}\n"
            f"- Debt Ratio: {r['debt_ratio']:.2f} ({_pct(r['debt_ratio']*100)}) — Risk: {risk}"
        )

    if company:
        sub = df[df['company'] == company].sort_values('year')
        lines = [f"**{company} — Balance Sheet Trend (FY2021–FY2023)**\n"]
        for _, r in sub.iterrows():
            lines.append(
                f"- FY{int(r['year'])}: Assets {_fmt(r['total_assets'])} | "
                f"Liabilities {_fmt(r['total_liabilities'])} | Debt Ratio {r['debt_ratio']:.2f}"
            )
        return '\n'.join(lines)

    fy2023 = df[df['year'] == 2023].sort_values('debt_ratio')
    lines = ["**Assets & Debt Ratio Comparison — FY2023**\n"]
    for _, r in fy2023.iterrows():
        lines.append(f"- {r['company']}: Assets {_fmt(r['total_assets'])} | Debt Ratio {r['debt_ratio']:.2f}")
    return '\n'.join(lines)


def cash_flow(df: pd.DataFrame, company: str, year: int) -> str:
    if company and year:
        row = df[(df['company'] == company) & (df['year'] == year)]
        if row.empty:
            return f"No cash flow data found for {company} in FY{year}."
        r = row.iloc[0]
        return (
            f"**{company} — Operating Cash Flow FY{year}**\n\n"
            f"- Operating Cash Flow: **{_fmt(r['operating_cf'])}**\n"
            f"- Cash Flow Margin: {_pct(r['cf_margin'])} of revenue\n"
            f"- Revenue: {_fmt(r['revenue'])}"
        )

    if company:
        sub = df[df['company'] == company].sort_values('year')
        lines = [f"**{company} — Operating Cash Flow Trend (FY2021–FY2023)**\n"]
        for _, r in sub.iterrows():
            lines.append(f"- FY{int(r['year'])}: **{_fmt(r['operating_cf'])}** (CF margin: {_pct(r['cf_margin'])})")
        return '\n'.join(lines)

    fy2023 = df[df['year'] == 2023].sort_values('operating_cf', ascending=False)
    lines = ["**Operating Cash Flow Comparison — FY2023**\n"]
    for _, r in fy2023.iterrows():
        lines.append(f"- {r['company']}: **{_fmt(r['operating_cf'])}** ({_pct(r['cf_margin'])} margin)")
    return '\n'.join(lines)


def growth(df: pd.DataFrame, company: str, year: int) -> str:
    if company:
        sub = df[(df['company'] == company) & (df['year'] > 2021)].sort_values('year')
        lines = [f"**{company} — Year-over-Year Growth**\n"]
        for _, r in sub.iterrows():
            lines.append(
                f"- FY{int(r['year'])}: Revenue {_sign(r['revenue_growth'])} | "
                f"Net Income {_sign(r['net_income_growth'])}"
            )
        return '\n'.join(lines)

    sub = df[df['year'] == 2023][['company', 'revenue_growth', 'net_income_growth']]
    lines = ["**YoY Growth Comparison (FY2022 → FY2023)**\n"]
    for _, r in sub.iterrows():
        lines.append(
            f"- {r['company']}: Revenue {_sign(r['revenue_growth'])} | "
            f"Net Income {_sign(r['net_income_growth'])}"
        )
    return '\n'.join(lines)


def summary(company: str) -> str:
    summaries = {
        'Microsoft': (
            "**Microsoft — Financial Health Summary**\n\n"
            "Microsoft demonstrates **stable, high-margin growth** driven by Azure cloud and enterprise software.\n\n"
            "- Revenue grew **26%** from FY2021 to FY2023 ($168B → $212B)\n"
            "- Net profit margin consistently **~34%** — exceptional for any industry\n"
            "- Debt ratio stable at **~50%**, indicating well-managed leverage\n"
            "- Generates **~$88B** in operating cash flow annually\n\n"
            "**Overall verdict: STRONG financial health.**"
        ),
        'Tesla': (
            "**Tesla — Financial Health Summary**\n\n"
            "Tesla shows **explosive growth with improving but pressured profitability**.\n\n"
            "- Revenue grew **81%** from FY2021 to FY2023 ($54B → $98B)\n"
            "- Net profit margin improved from 10% to **15%**, but OCF dipped in FY2023\n"
            "- Low debt ratio **~40%** reflects a healthy balance sheet\n"
            "- FY2023 cash flow decline reflects margin pressure from price cuts and competition\n\n"
            "**Overall verdict: HIGH GROWTH but VOLATILE.**"
        ),
        'Apple': (
            "**Apple — Financial Health Summary**\n\n"
            "Apple is a **cash-generating machine** with a mature, slightly slowing top line.\n\n"
            "- Revenue peaked at $394B (FY2022), slight dip to **$383B in FY2023**\n"
            "- Net profit margin **~25%**, driven by premium pricing and services growth\n"
            "- High debt ratio (**~82%**) is intentional — Apple borrows cheaply to fund share buybacks\n"
            "- **$114B operating cash flow** in FY2023 — world-class capital generation\n\n"
            "**Overall verdict: STRONG with deliberate leverage strategy.**"
        ),
    }

    if company and company in summaries:
        return summaries[company]

    return (
        "**Financial Health Summary — All Companies (FY2021–FY2023)**\n\n" +
        '\n\n---\n\n'.join(summaries.values())
    )


def compare(df: pd.DataFrame) -> str:
    fy = df[df['year'] == 2023]
    rows = []
    for _, r in fy.sort_values('revenue', ascending=False).iterrows():
        rows.append(
            f"**{r['company']}**\n"
            f"- Revenue: {_fmt(r['revenue'])} | Net Income: {_fmt(r['net_income'])}\n"
            f"- Profit Margin: {_pct(r['profit_margin'])} | Debt Ratio: {r['debt_ratio']:.2f}\n"
            f"- Operating Cash Flow: {_fmt(r['operating_cf'])} | CF Margin: {_pct(r['cf_margin'])}"
        )
    return "**FY2023 Cross-Company Comparison**\n\n" + '\n\n'.join(rows)


def help_text() -> str:
    return (
        "**GFC Financial Chatbot — Available Queries**\n\n"
        "You can ask me about Microsoft, Tesla, and Apple for FY2021–FY2023.\n\n"
        "**Topics I can answer:**\n"
        "- **Revenue** — total revenue, sales, turnover\n"
        "- **Net Income** — profit, earnings, margins\n"
        "- **Assets** — balance sheet, liabilities, debt ratio, equity\n"
        "- **Cash Flow** — operating cash flow, cash generation\n"
        "- **Growth** — year-over-year revenue and income growth\n"
        "- **Summary** — overall financial health assessment\n"
        "- **Compare** — side-by-side comparison of all three companies\n\n"
        "**Example questions:**\n"
        "- *What is Apple's total revenue for 2023?*\n"
        "- *How has Tesla's net income changed over time?*\n"
        "- *Compare all companies*\n"
        "- *Summarize Microsoft's financial health*\n"
        "- *What is Tesla's debt ratio in 2022?*"
    )


def fallback(query: str) -> str:
    return (
        f"I wasn't able to find a specific answer for: *\"{query}\"*\n\n"
        "Try asking about **revenue**, **net income**, **assets**, **cash flow**, "
        "**growth**, or a **summary**. You can also type **help** to see all options."
    )


# ── Main dispatch ────────────────────────────────────────────────────────────

def generate(intent: str, df: pd.DataFrame, company: str, year: int, query: str) -> str:
    if intent == 'revenue':    return revenue(df, company, year)
    if intent == 'net_income': return net_income(df, company, year)
    if intent == 'assets':     return assets(df, company, year)
    if intent == 'cash_flow':  return cash_flow(df, company, year)
    if intent == 'growth':     return growth(df, company, year)
    if intent == 'summary':    return summary(company)
    if intent == 'compare':    return compare(df)
    if intent == 'help':       return help_text()
    return fallback(query)
