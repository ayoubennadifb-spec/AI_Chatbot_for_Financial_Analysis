"""
RAG Corpus Builder
==================
Converts the structured financial DataFrame into a list of natural-language
text passages — one per row + additional derived-insight passages.
These passages are indexed by the retriever for semantic search.
"""

import pandas as pd


def build_corpus(df: pd.DataFrame) -> list[dict]:
    """
    Returns a list of passage dicts:
        {'text': str, 'company': str, 'year': int, 'topic': str}
    """
    passages = []

    for _, row in df.iterrows():
        c = row['company']
        y = int(row['year'])

        # Revenue passage
        passages.append({
            'text': (
                f"{c}'s total revenue in fiscal year {y} was ${row['revenue']:.2f} billion. "
                f"The net profit margin was {row['profit_margin']:.1f}%, meaning {c} kept "
                f"${row['net_income']:.2f} billion as net income."
            ),
            'company': c, 'year': y, 'topic': 'revenue'
        })

        # Balance sheet passage
        passages.append({
            'text': (
                f"{c}'s balance sheet for FY{y}: total assets were ${row['total_assets']:.2f}B, "
                f"total liabilities were ${row['total_liabilities']:.2f}B, and shareholders' equity "
                f"was ${row['equity']:.2f}B. The debt ratio was {row['debt_ratio']:.2f} "
                f"({row['debt_ratio']*100:.1f}% of assets financed by liabilities)."
            ),
            'company': c, 'year': y, 'topic': 'assets'
        })

        # Cash flow passage
        passages.append({
            'text': (
                f"{c} generated ${row['operating_cf']:.2f}B in operating cash flow in FY{y}, "
                f"representing a cash flow margin of {row['cf_margin']:.1f}% of revenue. "
                f"This measures the company's ability to convert revenue into real cash."
            ),
            'company': c, 'year': y, 'topic': 'cash_flow'
        })

        # Growth passage (only for years with prior data)
        if not pd.isna(row.get('revenue_growth')):
            passages.append({
                'text': (
                    f"{c}'s revenue grew by {row['revenue_growth']:+.1f}% in FY{y} compared to FY{y-1}, "
                    f"going from ${df[(df['company']==c)&(df['year']==y-1)]['revenue'].values[0]:.2f}B "
                    f"to ${row['revenue']:.2f}B. Net income changed by "
                    f"{row['net_income_growth']:+.1f}% in the same period."
                ),
                'company': c, 'year': y, 'topic': 'growth'
            })

    # Cross-company comparison passages (FY2023)
    fy2023 = df[df['year'] == 2023]
    best_margin   = fy2023.loc[fy2023['profit_margin'].idxmax()]
    best_revenue  = fy2023.loc[fy2023['revenue'].idxmax()]
    best_cf       = fy2023.loc[fy2023['operating_cf'].idxmax()]
    lowest_debt   = fy2023.loc[fy2023['debt_ratio'].idxmin()]

    passages.append({
        'text': (
            f"In FY2023, {best_revenue['company']} had the highest revenue at "
            f"${best_revenue['revenue']:.2f}B. {best_margin['company']} had the highest "
            f"profit margin at {best_margin['profit_margin']:.1f}%. "
            f"{best_cf['company']} generated the most operating cash flow at "
            f"${best_cf['operating_cf']:.2f}B. {lowest_debt['company']} had the lowest "
            f"debt ratio at {lowest_debt['debt_ratio']:.2f}."
        ),
        'company': 'All', 'year': 2023, 'topic': 'compare'
    })

    # Financial health summaries
    health_summaries = {
        'Microsoft': (
            "Microsoft shows stable, high-margin growth driven by Azure cloud and enterprise software. "
            "Revenue grew 26% from FY2021 to FY2023 ($168B to $212B). Net profit margin consistently ~34%. "
            "Debt ratio stable at ~50%, generating ~$88B in annual operating cash flow. "
            "Financial health: STRONG."
        ),
        'Tesla': (
            "Tesla shows explosive growth with improving but pressured profitability. "
            "Revenue grew 81% from FY2021 to FY2023 ($54B to $98B). "
            "Net profit margin improved from 10% to 15%, but operating cash flow dipped in FY2023 "
            "due to price cuts and rising competition. Debt ratio low at ~40%. "
            "Financial health: HIGH GROWTH but VOLATILE."
        ),
        'Apple': (
            "Apple is a cash-generating machine with a mature, slightly slowing revenue base. "
            "Revenue peaked at $394B in FY2022, dipping to $383B in FY2023. "
            "Net profit margin ~25%, driven by premium pricing and growing services revenue. "
            "High debt ratio (~82%) is intentional — Apple borrows cheaply to fund share buybacks. "
            "$114B operating cash flow in FY2023 is world-class. Financial health: STRONG."
        ),
    }
    for company, text in health_summaries.items():
        passages.append({'text': text, 'company': company, 'year': 0, 'topic': 'summary'})

    return passages
