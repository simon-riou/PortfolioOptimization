import yfinance as yf
import pandas as pd
import requests
from bs4 import BeautifulSoup

# Tickers dynamics

def get_data_sources():
    return {
        "CAC 40": get_cac40_tickers(),
        "S&P 500": get_snp500_tickers(),
        "Cryptomonnaies": get_crypto_tickers(),
    }

def get_cac40_tickers():
    url = "https://live.euronext.com//en/ajax/getStockIndexCompositionBlockContent/FR0003500008-XPAR"
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    table = soup.find("table", id="ewl-stock-index-composition-block-table")
    symbols = []
    if table:
        rows = table.find("tbody").find_all("tr")
        for row in rows:
            cols = row.find_all("td")
            if len(cols) >= 3:
                symbol = cols[2].text.strip()
                symbols.append(symbol + ".PA")
    return symbols

def get_snp500_tickers():
    snp500 = pd.read_html('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')[0]
    return snp500.Symbol.to_list()

def get_crypto_tickers():
    num_currencies = 250
    url = f"https://finance.yahoo.com/crypto?offset=0&count={num_currencies}"
    headers = {"User-Agent": "Mozilla/5.0",}
    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")
    symbols = []
    for row in soup.find_all("tr"):
        cols = row.find_all("td")
        if len(cols) >= 2:
            symbol = cols[0].text.strip()
            if symbol:
                symbols.append(symbol)

    return symbols

def get_combined_data(tickers, start, end):
    if not tickers:
        return pd.DataFrame()
    data = yf.download(tickers, start=start, end=end, auto_adjust=True)["Close"]
    return data.ffill().bfill().dropna(axis=1)