"""
Source-of-truth financial data from 10-K filings (FY2021-FY2023).
All monetary values in billions USD.
"""

import pandas as pd

RAW = [
    # Microsoft (FY ends June 30)
    {'company': 'Microsoft', 'year': 2021, 'revenue': 168.09, 'net_income': 61.27,
     'total_assets': 333.78, 'total_liabilities': 191.79, 'operating_cf': 76.74},
    {'company': 'Microsoft', 'year': 2022, 'revenue': 198.27, 'net_income': 72.74,
     'total_assets': 364.84, 'total_liabilities': 198.30, 'operating_cf': 89.04},
    {'company': 'Microsoft', 'year': 2023, 'revenue': 211.92, 'net_income': 72.36,
     'total_assets': 411.98, 'total_liabilities': 205.75, 'operating_cf': 87.91},

    # Tesla (FY ends December 31)
    {'company': 'Tesla',     'year': 2021, 'revenue':  53.82, 'net_income':  5.52,
     'total_assets':  62.13, 'total_liabilities':  30.55, 'operating_cf': 11.50},
    {'company': 'Tesla',     'year': 2022, 'revenue':  81.46, 'net_income': 12.56,
     'total_assets':  82.34, 'total_liabilities':  36.44, 'operating_cf': 14.48},
    {'company': 'Tesla',     'year': 2023, 'revenue':  97.69, 'net_income': 14.97,
     'total_assets': 106.62, 'total_liabilities':  43.00, 'operating_cf': 13.26},

    # Apple (FY ends September 30)
    {'company': 'Apple',     'year': 2021, 'revenue': 365.82, 'net_income': 94.68,
     'total_assets': 351.00, 'total_liabilities': 287.91, 'operating_cf': 104.04},
    {'company': 'Apple',     'year': 2022, 'revenue': 394.33, 'net_income': 99.80,
     'total_assets': 352.76, 'total_liabilities': 302.08, 'operating_cf': 122.15},
    {'company': 'Apple',     'year': 2023, 'revenue': 383.29, 'net_income': 96.99,
     'total_assets': 352.58, 'total_liabilities': 290.44, 'operating_cf': 114.00},
]


def load() -> pd.DataFrame:
    """Return enriched DataFrame with derived financial metrics."""
    df = pd.DataFrame(RAW).sort_values(['company', 'year']).reset_index(drop=True)

    df['profit_margin']      = (df['net_income'] / df['revenue']) * 100
    df['debt_ratio']         = df['total_liabilities'] / df['total_assets']
    df['equity']             = df['total_assets'] - df['total_liabilities']
    df['cf_margin']          = (df['operating_cf'] / df['revenue']) * 100
    df['revenue_growth']     = df.groupby('company')['revenue'].pct_change() * 100
    df['net_income_growth']  = df.groupby('company')['net_income'].pct_change() * 100

    return df


COMPANIES = ['Microsoft', 'Tesla', 'Apple']
YEARS     = [2021, 2022, 2023]
