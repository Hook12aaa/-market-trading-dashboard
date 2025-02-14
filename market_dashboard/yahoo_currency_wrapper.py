import yfinance as yf
import pandas as pd
from currency_pair_generator import CurrencyPairGenerator
import numpy as np
from datetime import datetime, timedelta

class YahooCurrencyWrapper:
    def __init__(self):
        self.generator = CurrencyPairGenerator()
        generated_pairs = self.generator.generate_all_pairs()
        self.common_pairs = {}
        
        for category in generated_pairs['forex_pairs'].values():
            self.common_pairs.update(category)

    def format_symbol(self, symbol):
        if symbol.endswith('=X'):
            return symbol
        if '/' in symbol:
            return symbol.replace('/', '') + '=X'
        return symbol + '=X'

    def fetch_currency_rate(self, symbol, start=None, end=None, period='1d', interval='1m'):
        formatted_symbol = self.format_symbol(symbol)
        try:
            ticker = yf.Ticker(formatted_symbol)
            
            if start and end:
                df = ticker.history(start=start, end=end, interval=interval)
            else:
                df = ticker.history(period=period, interval=interval)
            
            if df.empty:
                return pd.DataFrame()
            return df
            
        except Exception as e:
            raise Exception(f"Error fetching {symbol}: {str(e)}")

    def get_summary(self, symbol, period='1d', date=None):
        try:
            if date:
                if isinstance(date, datetime):
                        date = date.strftime("%Y-%m-%d")
                start_date = datetime.strptime(date, '%Y-%m-%d')
                end_date = start_date + timedelta(days=1)
                df = self.fetch_currency_rate(symbol, start=start_date, end=end_date)
            else:
                df = self.fetch_currency_rate(symbol, period=period)
            if df.empty:
                raise Exception("No data available")

            current_price = df['Close'].iloc[-1]
            prev_price = df['Close'].iloc[-2] if len(df) > 1 else df['Close'].iloc[-1]
            day_change = ((current_price / prev_price) - 1) * 100

            delta = df['Close'].diff()
            gain = (delta.where(delta > 0, 0)).rolling(window=14).mean()
            loss = (-delta.where(delta < 0, 0)).rolling(window=14).mean()
            rs = gain / loss
            rsi = 100 - (100 / (1 + rs)).fillna(50)

            sma_20 = df['Close'].rolling(window=20).mean()
            sma_50 = df['Close'].rolling(window=50).mean()

            exp1 = df['Close'].ewm(span=12, adjust=False).mean()
            exp2 = df['Close'].ewm(span=26, adjust=False).mean()
            macd = exp1 - exp2
            signal_line = macd.ewm(span=9, adjust=False).mean()

            returns = df['Close'].pct_change().dropna()
            if len(returns) > 0:
                volatility = returns.std() * np.sqrt(252)
            else:
                volatility = 0.0

            volatility = 0.0 if np.isnan(volatility) else volatility
            rsi_value = 50.0 if np.isnan(rsi.iloc[-1]) else rsi.iloc[-1]
            macd_last = macd.iloc[-1] if not np.isnan(macd.iloc[-1]) else 0
            signal_last = signal_line.iloc[-1] if not np.isnan(signal_line.iloc[-1]) else 0

            recent_high = df['High'].tail(20).max()
            recent_low = df['Low'].tail(20).min()

            summary = {
                'current_rate': current_price,
                'day_change_pct': day_change,
                'rsi': rsi_value,
                'trend': 'Bullish' if sma_20.iloc[-1] > sma_50.iloc[-1] else 'Bearish',
                'macd_signal': 'Buy' if macd_last > signal_last else 'Sell',
                'volatility': volatility,
                'support': recent_low,
                'resistance': recent_high,
                'volume': df['Volume'].iloc[-1] if 'Volume' in df else 0
            }
            return summary

        except Exception as e:
            raise Exception(f"Error in summary for {symbol}: {str(e)}")

    def get_correlation_matrix(self, symbols, period='1mo'):
        data = {}
        for symbol in symbols:
            try:
                df = self.fetch_currency_rate(symbol, period=period)
                if df is not None and not df.empty:
                    data[symbol] = df['Close']
            except Exception as e:
                print(f"Error fetching {symbol}: {str(e)}")
                
        if data:
            return pd.DataFrame(data).corr()
        return None

    def calculate_pip_value(self, symbol, amount=1000):
        try:
            rate = self.get_current_rate(symbol)
            
            pip_size = 0.01 if 'JPY' in symbol else 0.0001
            pip_value = pip_size * amount
            
            if symbol.startswith('USD'):
                pip_value = pip_value / rate
            elif symbol.endswith('USD'):
                pip_value = pip_value
            else:
                usd_rate = self.get_current_rate(f"{symbol.split('/')[1]}/USD")
                pip_value = pip_value * usd_rate
                
            return pip_value
            
        except Exception as e:
            raise Exception(f"Error calculating pip value: {str(e)}")

    def get_current_rate(self, symbol):
        df = self.fetch_currency_rate(symbol, period='1d')
        if df is not None and not df.empty:
            return df['Close'].iloc[-1]
        return None
    
    def get_pair_categories(self):
        return list(self.generator.generate_all_pairs()['forex_pairs'].keys())

    def get_available_pairs(self, category=None):
        if category:
            pairs = self.generator.generate_all_pairs()['forex_pairs'].get(category, {})
            return sorted(pairs.keys())
        return sorted(self.common_pairs.keys())
    
    def get_historic_data(self, symbol, start_date, end_date, interval='1d'):
        try:
            df = self.fetch_currency_rate(symbol, start=start_date, end=end_date, interval=interval)
            if df.empty:
                raise Exception("No data available")
            return df
        except Exception as e:
            raise Exception(f"Error fetching historical data for {symbol}: {str(e)}")

if __name__ == "__main__":
    currency = YahooCurrencyWrapper()
    
    try:
        df = currency.get_historic_data('EUR/USD', '2021-01-01', '2021-01-31', interval='1d')
        print(df)
    except Exception as e:
        print(f"Error: {e}")

    print("Available categories:", currency.get_pair_categories())
    print("\nMajor pairs:", currency.get_available_pairs('major_pairs'))

    try:
        summary = currency.get_summary('EUR/USD')
        print("\nEUR/USD Summary:")
        for key, value in summary.items():
            print(f"{key}: {value}")
    except Exception as e:
        print(f"Error: {e}")