import logging
import requests
import pandas as pd
import mplfinance as mpf

def fetch_binance_data(symbol="BTCUSDT", interval="15m", limit=48):
    """
    Fetches candlestick data from Binance.
    """
    url = f"https://api.binance.com/api/v3/klines?symbol={symbol}&interval={interval}&limit={limit}"
    try:
        response = requests.get(url)
        data = response.json()
        # Check for errors in the response
        if isinstance(data, dict) and data.get("code"):
            logging.error(f"Error fetching data: {data}")
            return None

        # Binance returns: [open_time, open, high, low, close, volume, close_time, ...]
        df = pd.DataFrame(data, columns=[
            "open_time", "open", "high", "low", "close", "volume",
            "close_time", "quote_asset_volume", "num_trades",
            "taker_buy_base_asset_volume", "taker_buy_quote_asset_volume", "ignore"
        ])

        # Convert open_time to datetime and set it as index
        df["open_time"] = pd.to_datetime(df["open_time"], unit="ms")
        df.set_index("open_time", inplace=True)

        # Convert numeric columns to float
        df = df.astype(float)
        return df
    except Exception as e:
        logging.error(f"Exception while fetching Binance data: {e}")
        return None

def main():
    # Fetch data from Binance
    df = fetch_binance_data()

    # Define RGB colors
    red = (255/255, 0/255, 0/255)       # Pure red
    black = (0/255, 0/255, 0/255)       # Pure black
    white = (255/255, 255/255, 255/255) # Pure white

    custom_style = mpf.make_marketcolors(
        up=black,  # Empty (white) boxes with black lines
        down=red,  # Red boxes with red lines
        edge=black,  # Edge color for the candles
        wick='inherit',  # Wick color
        volume='inherit'  # Volume color
    )
    
    mpf_style = mpf.make_mpf_style(
        marketcolors=custom_style,
        facecolor='white',  # Background color of the chart
        edgecolor='black',  # Border color of the chart
        figcolor='white'  # Figure background color
    )

    # Plot the candlestick chart
    fig, axes = mpf.plot(
        df,
        type='candle',
        style=mpf_style,
        volume=False,
        figsize=(8, 4.8),  # Set fixed figure size in inches (corresponding to 800x480px)
        returnfig=True,  # Return the figure and axes objects
        show_nontrading=False,  # Hide non-trading periods (if applicable)
        tight_layout=True
    )

    # Save the figure with high DPI (e.g., 300)
    fig.savefig('btcusdt_chart.png', dpi=100, facecolor='white', edgecolor='black')

if __name__ == "__main__":
    main()
