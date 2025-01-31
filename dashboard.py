import streamlit as st
import pandas as pd
from data_fetch import get_yfinance_data, get_alpha_vantage_data, create_comparison_table

def main():
    st.set_page_config(page_title="Stock KPI Dashboard", layout="centered")

    # Custom CSS for styling
    st.markdown(
        """
        <style>
            body {
                background-color: #1E1E1E;
                color: #FFFFFF;
                font-family: 'Segoe UI', sans-serif;
            }
            .table-container {
                background: #2E2E2E;
                padding: 20px;
                border-radius: 12px;
                box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
                margin-top: 20px;
            }
            .table-header {
                font-size: 24px;
                font-weight: bold;
                margin-bottom: 10px;
                text-align: center;
                color: #F0A500;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                font-size: 14px;
                margin: auto;
            }
            th, td {
                border: 1px solid #444;
                padding: 8px;
                text-align: center;
            }
            th {
                background-color: #333;
                color: #FFFFFF;
            }
            td {
                background-color: #1E1E1E;
            }
            .highlight {
                color: #F0A500;
                font-weight: bold;
            }
            .valuation { color: #F39C12; }         /* Orange */
            .profitability { color: #27AE60; }     /* Green */
            .growth { color: #3498DB; }            /* Blue */
            .enterprise { color: #9B59B6; }        /* Purple */
            .market { color: #E74C3C; }            /* Red */
            .notes-column {
                width: 300px;
                text-align: left;
            }
        </style>
        """,
        unsafe_allow_html=True,
    )

    st.title("📊 Stock KPI Dashboard")

    tickers_input = st.text_input("Enter up to 3 stock tickers separated by commas (e.g., META, AAPL, MSFT):")

    if tickers_input:
        tickers = [t.strip().upper() for t in tickers_input.split(",")][:3]

        # Fetch data for each ticker
        all_data = {}
        for ticker in tickers:
            yfinance_data = get_yfinance_data(ticker)
            alpha_vantage_data = get_alpha_vantage_data(ticker)
            all_data[ticker] = {**yfinance_data, **alpha_vantage_data}

        # Generate comparison table
        df = create_comparison_table(tickers, all_data)

        # Apply CSS classes based on KPI category
        def get_kpi_css_class(kpi):
            class_map = {
                'Forward P/E Ratio': 'valuation',
                'TTM P/E Ratio': 'valuation',
                'PEG Ratio (5yr expected)': 'valuation',
                'Gross Margin (%)': 'profitability',
                'Net Margin (%)': 'profitability',
                'TTM Revenue Growth (%)': 'growth',
                'Current Year Rev Growth (Est, %)': 'growth',
                'Enterprise Value/Revenue': 'enterprise',
                'Enterprise Value/EBITDA': 'enterprise',
                'Market Cap (B)': 'market',
                'Enterprise Value (B)': 'market',
            }
            return class_map.get(kpi, '')

        # Convert to HTML with dynamic CSS classes for KPI rows
        rows_html = ""
        for _, row in df.iterrows():
            css_class = get_kpi_css_class(row['KPI'])
            row_html = f"<tr><td class='highlight {css_class}'>{row['KPI']}</td>"
            for ticker in tickers:
                row_html += f"<td>{row[ticker]}</td>"
            row_html += f"<td class='notes-column'>{row['Notes']}</td></tr>"
            rows_html += row_html

        # Final table HTML
        table_html = f"""
        <div class="table-container">
            <div class="table-header">Key Stock Metrics Comparison</div>
            <table>
                <thead>
                    <tr>
                        <th class='highlight'>KPI</th>
                        {"".join(f"<th>{ticker}</th>" for ticker in tickers)}
                        <th class='notes-column'>Notes</th>
                    </tr>
                </thead>
                <tbody>
                    {rows_html}
                </tbody>
            </table>
        </div>
        """

        # Render the HTML table
        st.write(table_html, unsafe_allow_html=True)

if __name__ == "__main__":
    main()
