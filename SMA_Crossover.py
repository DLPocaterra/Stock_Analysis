import yfinance as yf
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from datetime import datetime
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

def get_valid_date(prompt):
    while True:
        date_str = input(prompt)
        if not date_str:
            return None
        try:
            datetime.strptime(date_str, "%Y-%m-%d")
            return date_str
        except ValueError:
            print("Incorrect date format. Please enter the date in YYYY-MM-DD format.")

def fetch_stock_data(ticker, start_date, end_date):
    logging.info(f"Downloading data for {ticker} from {start_date} to {end_date}")
    stock_data = yf.download(ticker, start=start_date, end=end_date)
    if stock_data.empty:
        raise ValueError("No data fetched. Please check the ticker symbol and date range.")
    return stock_data

def calculate_smas(stock_data, short_window=5, long_window=20):
    if len(stock_data) < long_window:
        raise ValueError("Not enough data points to calculate the long SMA.")
    
    stock_data["SMA_Short"] = stock_data["Close"].rolling(window=short_window).mean()
    stock_data["SMA_Long"] = stock_data["Close"].rolling(window=long_window).mean()
    stock_data.dropna(inplace=True)
    stock_data["bullish"] = np.where(stock_data["SMA_Short"] > stock_data["SMA_Long"], 1.0, 0.0)
    stock_data["crossover"] = stock_data["bullish"].diff()
    return stock_data

def plot_crossover(stock_data, ticker):
    fig = plt.figure(figsize=(12, 8))
    ax1 = fig.add_subplot(111, ylabel="Price in $")

    stock_data["Close"].plot(ax=ax1, color='b', lw=2., label="Close")
    stock_data["SMA_Short"].plot(ax=ax1, color='r', lw=2., label='SMA Short')
    stock_data["SMA_Long"].plot(ax=ax1, color='g', lw=2., label='SMA Long')
    
    ax1.plot(stock_data.loc[stock_data.crossover == 1.0].index, 
             stock_data.Close[stock_data.crossover == 1.0],
             "^", markersize=10, color='g', label='Buy')    

    ax1.plot(stock_data.loc[stock_data.crossover == -1.0].index, 
             stock_data.Close[stock_data.crossover == -1.0],
             "v", markersize=10, color='r', label='Sell')

    plt.legend()
    plt.title(f'{ticker} SMA Crossover')

    save_plot = input("Do you want to save the plot? (y/n): ").lower()
    if save_plot == 'y':
        filename = f"{ticker}_SMA_Crossover.png"
        plt.savefig(filename)
        logging.info(f"Plot saved as {filename}")

    plt.show()

def main():
    try:
        ticker = input("Enter stock ticker: ").upper().strip()
        if not ticker:
            raise ValueError("Ticker symbol cannot be empty.")

        start_date = get_valid_date("Enter start date (YYYY-MM-DD): ")
        if not start_date:
            raise ValueError("Start date is required.")

        end_date = get_valid_date("Enter end date (YYYY-MM-DD) or press Enter for today: ")
        if not end_date:
            end_date = datetime.today().strftime("%Y-%m-%d")

        if start_date >= end_date:
            raise ValueError("Start date must be earlier than end date.")

        short_window_input = input("Enter short SMA window (default 5): ")
        long_window_input = input("Enter long SMA window (default 20): ")

        short_window = int(short_window_input) if short_window_input.strip() else 5
        long_window = int(long_window_input) if long_window_input.strip() else 20

        if short_window >= long_window:
            raise ValueError("Short window must be less than long window.")

        stock_data = fetch_stock_data(ticker, start_date, end_date)

        stock_data = calculate_smas(stock_data, short_window, long_window)

        plot_crossover(stock_data, ticker)

    except ValueError as e:
        logging.error(f"Value Error: {e}")
    except Exception as e:
        logging.error(f"An unexpected error has occurred: {e}")

if __name__ == "__main__":
    main()