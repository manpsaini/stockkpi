import yfinance as yf
import pandas as pd
from alpha_vantage.fundamentaldata import FundamentalData

ALPHA_VANTAGE_API_KEY = 'KK6WXBRIGHPQP9J2'

KPI_NOTES = {
    'Forward P/E Ratio': "Price vs next year's earnings. Tech avg: 20-35x",
    'TTM P/E Ratio': "Price vs trailing earnings. SaaS avg: 30-50x",
    'PEG Ratio (5yr expected)': "P/E vs growth rate. Fair value: 1.0x",
    'Gross Margin (%)': "Revenue left after COGS. SaaS avg: 70-85%",
    'Net Margin (%)': "Profit after all expenses. Strong: >20%",
    'TTM Revenue Growth (%)': "Trailing 12-month revenue growth. SaaS avg: 15-30%",
    'Current Year Rev Growth (Est, %)': "Analyst consensus for current fiscal year. Healthy: >10%",
    'Enterprise Value/Revenue': "EV vs revenue. SaaS avg: 8-12x",
    'Enterprise Value/EBITDA': "EV vs EBITDA. SaaS avg: 20-30x",
    'Market Cap (B)': "Total market value of shares. Context: Compare to peers",
    'Enterprise Value (B)': "Total company value (debt + equity - cash)"
}

def get_yfinance_data(ticker):
    try:
        stock = yf.Ticker(ticker)
        info = stock.info
        financials = stock.financials

        ttm_revenue = financials.loc['Total Revenue'].iloc[0] if 'Total Revenue' in financials.index else 0

        return {
            'Forward P/E Ratio': round(info.get('forwardPE', 0), 1),
            'TTM P/E Ratio': round(info.get('trailingPE', 0), 1),
            'PEG Ratio (5yr expected)': 'N/A',
            'Gross Margin (%)': round(info.get('grossMargins', 0) * 100, 1),
            'Net Margin (%)': (
                round((info.get('netIncomeToCommon', 0) / info.get('totalRevenue', 1)) * 100, 1)
                if info.get('totalRevenue', 0) > 0 else 'N/A'
            ),
            'TTM Revenue Growth (%)': (
                round((financials.loc['Total Revenue'].iloc[0] / financials.loc['Total Revenue'].iloc[1] - 1) * 100, 1)
                if 'Total Revenue' in financials.index and financials.loc['Total Revenue'].iloc[1] > 0 else 'N/A'
            ),
            'Current Year Rev Growth (Est, %)': round(info.get('revenueGrowth', 0) * 100, 1),
            'Enterprise Value/Revenue': (
                round(info.get('enterpriseValue', 0) / ttm_revenue, 1) if ttm_revenue > 0 else 'N/A'
            ),
            'Enterprise Value/EBITDA': (
                round(info.get('enterpriseValue', 0) / info.get('ebitda', 1), 1) if info.get('ebitda', 0) > 0 else 'N/A'
            ),
            'Market Cap (B)': round(info.get('marketCap', 0) / 1e9, 1),
            'Enterprise Value (B)': round(info.get('enterpriseValue', 0) / 1e9, 1)
        }
    except Exception as e:
        print(f"Error fetching {ticker}: {e}")
        return {}

def get_alpha_vantage_data(ticker):
    try:
        fd = FundamentalData(ALPHA_VANTAGE_API_KEY)
        company_data, _ = fd.get_company_overview(ticker)
        return {
            'PEG Ratio (5yr expected)': round(float(company_data.get('PEGRatio', 0)), 1) if company_data.get('PEGRatio') else 'N/A'
        }
    except Exception as e:
        print(f"Alpha Vantage error for {ticker}: {e}")
        return {'PEG Ratio (5yr expected)': 'N/A'}

def create_comparison_table(tickers, all_data):
    """
    Create a comparison table with KPI data.
    """
    kpis = [
        'Forward P/E Ratio', 'TTM P/E Ratio', 'PEG Ratio (5yr expected)',
        'Gross Margin (%)', 'Net Margin (%)',
        'TTM Revenue Growth (%)', 'Current Year Rev Growth (Est, %)',
        'Enterprise Value/Revenue', 'Enterprise Value/EBITDA',
        'Market Cap (B)', 'Enterprise Value (B)'
    ]

    rows = []
    for kpi in kpis:
        row = {'KPI': kpi, 'Notes': KPI_NOTES.get(kpi, '')}
        for ticker in tickers:
            row[ticker] = all_data[ticker].get(kpi, 'N/A')
        rows.append(row)

    return pd.DataFrame(rows)
