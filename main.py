import yfinance as yf
from datetime import datetime, timedelta
import pandas as pd
pd.options.mode.chained_assignment = None  # default='warn'

class colors:
    BOLD = '\033[1m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    BLUE = '\033[34m'
    RESET = '\033[0m'


def main():
    ticker_input = input('Enter stock symbol: ')
    ticker = yf.Ticker(ticker_input)

    oi = int(input('Enter open interest threshold: '))
    days = int(input('Enter # of days to search: '))
        
    try:
        stock_price = ticker.info['regularMarketPrice']
    except KeyError:
        # Fallback: use history to get the latest close price
        stock_price = ticker.history(period="1d")['Close'][0]
    
    print('------------------------------------------------------------')
    print(f'Searching for: {ticker}')
    print(f"Stock price: {stock_price}")
    print('------------------------------------------------------------')

    
    # Get all available option expiration dates
    option_dates = ticker.options
    
    # Define a threshold for high open interest (adjustable as needed)
    open_interest_threshold = oi
    
    # Loop through the next 30 days of option chains
    for date in option_dates:
        exp_date = datetime.strptime(date, "%Y-%m-%d")
        if exp_date <= datetime.now() + timedelta(days=days):
            print(f"\n{colors.BOLD}{colors.BLUE}Options chain for expiration date: {date}{bcolors.RESET}")
            opt_chain = ticker.option_chain(date)
            
            # Filter calls and puts with higher open interest and OTM
            otm_calls = opt_chain.calls[(opt_chain.calls['openInterest'] > open_interest_threshold) & (opt_chain.calls['inTheMoney'] == False)]
            otm_puts = opt_chain.puts[(opt_chain.puts['openInterest'] > open_interest_threshold) & (opt_chain.puts['inTheMoney'] == False)]
            
            # Calculate % OTM for calls and puts
            if not otm_calls.empty:
                otm_calls['% OTM'] = ((otm_calls['strike'] - stock_price) / stock_price) * 100
                print(f"{colors.GREEN}OTM Calls with High Open Interest ({date}):")
                print(otm_calls[['contractSymbol', 'strike', 'lastPrice', 'openInterest', '% OTM']])
             
            if not otm_puts.empty:
                otm_puts['% OTM'] = ((stock_price - otm_puts['strike']) / stock_price) * 100
                print(f"{colors.RED}OTM Puts with High Open Interest ({date}):")
                print(otm_puts[['contractSymbol', 'strike', 'lastPrice', 'openInterest', '% OTM']])

if __name__ == '__main__':
    main()
