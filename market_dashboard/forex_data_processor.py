import pandas as pd
import numpy as np
from dataclasses import dataclass
from typing import Dict, List, Optional
from datetime import datetime

import talib

@dataclass
class MarketSignal:
    pair: str
    timestamp: datetime
    trend: str
    strength: float
    entry_price: float
    stop_loss: float
    take_profit: float
    position_size: float
    risk_reward: float
    confidence: float
    expected_return: float

class ForexDataProcessor:
    def __init__(self, currency_wrapper):
        """Initialize with currency wrapper instance"""
        self.currency = currency_wrapper
        self.market_data = pd.DataFrame()
        self.signals = pd.DataFrame()
        

        self.position_config = {
            'EUR': {'base_lot': 100000, 'risk_factor': 1.0},
            'GBP': {'base_lot': 80000, 'risk_factor': 1.2},
            'USD': {'base_lot': 100000, 'risk_factor': 1.0},
            'JPY': {'base_lot': 10000000, 'risk_factor': 0.8},
            'CHF': {'base_lot': 100000, 'risk_factor': 0.9},
            'AUD': {'base_lot': 100000, 'risk_factor': 1.3},
            'NZD': {'base_lot': 100000, 'risk_factor': 1.4},
            'CAD': {'base_lot': 100000, 'risk_factor': 1.1}
        }

    def load_market_data(self):
        """Load and process market data with proper signal strength calculation"""
        pairs = self.currency.get_available_pairs()
        data_list = []

        for pair in pairs:
            try:
                summary = self.currency.get_summary(pair)
                if summary:
                    base, quote = pair.split('/')
                    

                    pos_params = self._calculate_position_parameters(
                        base, summary['current_rate'], summary['volatility']
                    )
                    

                    signal_strength = self._calculate_signal_strength(summary, pos_params)
                    
                    data_list.append({
                        'pair': pair,
                        'base_currency': base,
                        'quote_currency': quote,
                        'current_rate': summary['current_rate'],
                        'day_change': summary['day_change_pct'],
                        'trend': summary['trend'],
                        'rsi': summary['rsi'],
                        'volatility': summary['volatility'],
                        'macd_signal': summary['macd_signal'],
                        'position_size': pos_params['position_size'],
                        'entry_price': pos_params['entry_price'],
                        'take_profit': pos_params['take_profit'],
                        'stop_loss': pos_params['stop_loss'],
                        'risk_reward': pos_params['risk_reward'],
                        'expected_return': pos_params['expected_return'],
                        'signal_strength': signal_strength,
                        'timestamp': datetime.now()
                    })
            except Exception as e:
                print(f"Error processing {pair}: {str(e)}")

        return pd.DataFrame(data_list)
    
    def _calculate_dynamic_distances(self, volatility, atr, daily_range, base_currency):
        """
        Calculate dynamic stop and profit distances based on volatility, ATR, daily range, and base currency.
        Parameters:
        volatility (float): The current volatility of the market.
        atr (float): The Average True Range (ATR) value.
        daily_range (float): The daily range of the currency pair.
        base_currency (str): The base currency code (e.g., 'USD', 'EUR').
        Returns:
        tuple: A tuple containing the calculated stop distance and profit distance.
        """

        currency_multipliers = {
            'JPY': {'stop': 1.4, 'profit': 2.2},
            'EUR': {'stop': 1.2, 'profit': 2.5},
            'GBP': {'stop': 1.3, 'profit': 2.3},
            'USD': {'stop': 1.2, 'profit': 2.4},
            'CHF': {'stop': 1.3, 'profit': 2.2},
            'AUD': {'stop': 1.5, 'profit': 2.1},
            'NZD': {'stop': 1.5, 'profit': 2.1},
            'CAD': {'stop': 1.4, 'profit': 2.2},
            'SGD': {'stop': 1.3, 'profit': 2.3},
            'HKD': {'stop': 1.2, 'profit': 2.4},
            'NOK': {'stop': 1.4, 'profit': 2.2},
            'SEK': {'stop': 1.3, 'profit': 2.3},
            'DKK': {'stop': 1.2, 'profit': 2.5},
            'ZAR': {'stop': 1.5, 'profit': 2.0},
            'MXN': {'stop': 1.6, 'profit': 1.9},
            'TRY': {'stop': 1.7, 'profit': 1.8},
            'RUB': {'stop': 1.8, 'profit': 1.7},
            'INR': {'stop': 1.5, 'profit': 2.0},
            'BRL': {'stop': 1.6, 'profit': 1.9},
            'CNY': {'stop': 1.4, 'profit': 2.2},
            'KRW': {'stop': 1.3, 'profit': 2.3},
            'TWD': {'stop': 1.2, 'profit': 2.4},
            'MYR': {'stop': 1.5, 'profit': 2.1},
            'IDR': {'stop': 1.6, 'profit': 1.9},
            'THB': {'stop': 1.4, 'profit': 2.2},
            'PHP': {'stop': 1.5, 'profit': 2.0},
            'PLN': {'stop': 1.3, 'profit': 2.3},
            'HUF': {'stop': 1.4, 'profit': 2.2},
            'CZK': {'stop': 1.3, 'profit': 2.3},
            'ILS': {'stop': 1.2, 'profit': 2.4},
            'SAR': {'stop': 1.5, 'profit': 2.1},
            'AED': {'stop': 1.4, 'profit': 2.2},
            'QAR': {'stop': 1.3, 'profit': 2.3},
            'KWD': {'stop': 1.2, 'profit': 2.4},
            'BHD': {'stop': 1.3, 'profit': 2.3},
            'OMR': {'stop': 1.2, 'profit': 2.4},
            'JOD': {'stop': 1.3, 'profit': 2.3},
            'EGP': {'stop': 1.5, 'profit': 2.0},
            'NGN': {'stop': 1.6, 'profit': 1.9},
            'KES': {'stop': 1.5, 'profit': 2.0},
            'GHS': {'stop': 1.6, 'profit': 1.9},
            'TZS': {'stop': 1.5, 'profit': 2.0},
            'UGX': {'stop': 1.6, 'profit': 1.9},
            'ZMW': {'stop': 1.7, 'profit': 1.8},
            'MAD': {'stop': 1.5, 'profit': 2.0},
            'DZD': {'stop': 1.6, 'profit': 1.9},
            'TND': {'stop': 1.5, 'profit': 2.0},
            'LBP': {'stop': 1.7, 'profit': 1.8},
            'JMD': {'stop': 1.6, 'profit': 1.9},
            'TTD': {'stop': 1.5, 'profit': 2.0},
            'BBD': {'stop': 1.6, 'profit': 1.9},
            'BZD': {'stop': 1.5, 'profit': 2.0},
            'BMD': {'stop': 1.4, 'profit': 2.2},
            'BSD': {'stop': 1.4, 'profit': 2.2},
            'KYD': {'stop': 1.3, 'profit': 2.3},
            'XCD': {'stop': 1.4, 'profit': 2.2},
            'ANG': {'stop': 1.3, 'profit': 2.3},
            'AWG': {'stop': 1.3, 'profit': 2.3},
            'BIF': {'stop': 1.6, 'profit': 1.9},
            'CDF': {'stop': 1.7, 'profit': 1.8},
            'DJF': {'stop': 1.5, 'profit': 2.0},
            'ERN': {'stop': 1.6, 'profit': 1.9},
            'ETB': {'stop': 1.7, 'profit': 1.8},
            'GMD': {'stop': 1.6, 'profit': 1.9},
            'GNF': {'stop': 1.7, 'profit': 1.8},
            'LSL': {'stop': 1.6, 'profit': 1.9},
            'LRD': {'stop': 1.7, 'profit': 1.8},
            'MWK': {'stop': 1.6, 'profit': 1.9},
            'MRO': {'stop': 1.7, 'profit': 1.8},
            'MUR': {'stop': 1.6, 'profit': 1.9},
            'MZN': {'stop': 1.7, 'profit': 1.8},
            'NAD': {'stop': 1.6, 'profit': 1.9},
            'RWF': {'stop': 1.7, 'profit': 1.8},
            'SCR': {'stop': 1.6, 'profit': 1.9},
            'SLL': {'stop': 1.7, 'profit': 1.8},
            'SOS': {'stop': 1.6, 'profit': 1.9},
            'SSP': {'stop': 1.7, 'profit': 1.8},
            'SDG': {'stop': 1.6, 'profit': 1.9},
            'SZL': {'stop': 1.6, 'profit': 1.9},
            'TJS': {'stop': 1.7, 'profit': 1.8},
            'TMT': {'stop': 1.6, 'profit': 1.9},
            'UGX': {'stop': 1.6, 'profit': 1.9},
            'UZS': {'stop': 1.7, 'profit': 1.8},
            'VND': {'stop': 1.6, 'profit': 1.9},
            'XAF': {'stop': 1.6, 'profit': 1.9},
            'XOF': {'stop': 1.6, 'profit': 1.9},
            'XPF': {'stop': 1.6, 'profit': 1.9},
            'YER': {'stop': 1.7, 'profit': 1.8},
            'ZWL': {'stop': 1.7, 'profit': 1.8},
        }
        
        mult = currency_multipliers.get(base_currency, {'stop': 1.3, 'profit': 2.3})
        

        if volatility < 0.005:
            stop_distance = max(atr * mult['stop'], daily_range * 0.1)
            profit_mult = mult['profit'] * 1.1 
        elif volatility < 0.01:
            stop_distance = max(atr * mult['stop'] * 1.2, daily_range * 0.15)
            profit_mult = mult['profit']
        else:
            stop_distance = max(atr * mult['stop'] * 1.4, daily_range * 0.2)
            profit_mult = mult['profit'] * 0.9  
        
        profit_distance = stop_distance * profit_mult
        return stop_distance, profit_distance
    
    def get_price_data(self, pair: str, look_back: int = 252) -> pd.DataFrame:
        """Retrieve historical price data for a currency pair"""

        if self.currency is None:
            raise ValueError("Currency wrapper not initialized")

        return self.currency.fetch_currency_rate(pair, period=f"{look_back}d")
        
    
    def _calculate_signal_strength(self, summary, pos_params):
        """Calculate comprehensive signal strength score"""
        score = 0
        

        if summary['trend'] == 'Bullish' and summary['macd_signal'] == 'Buy':
            score += 30
        elif summary['trend'] == 'Bearish' and summary['macd_signal'] == 'Sell':
            score += 30
        

        if summary['trend'] == 'Bullish':
            if summary['rsi'] < 30:
                score += 25  
            elif summary['rsi'] < 45:
                score += 15
        else:
            if summary['rsi'] > 70:
                score += 25  
            elif summary['rsi'] > 55:
                score += 15
        

        rr_score = min(pos_params['risk_reward'] * 10, 25)
        score += rr_score
        

        vol_score = (1 - (summary['volatility'] / 0.02)) * 20  
        score += max(min(vol_score, 20), 0)
        
        return score
        
    def _calculate_signal_strength(self, summary, pos_params):
        """Calculate comprehensive signal strength score"""
        score = 0
        

        if summary['trend'] == 'Bullish' and summary['macd_signal'] == 'Buy':
            score += 30
        elif summary['trend'] == 'Bearish' and summary['macd_signal'] == 'Sell':
            score += 30
        
 
        if summary['trend'] == 'Bullish':
            if summary['rsi'] < 30:
                score += 25 
            elif summary['rsi'] < 45:
                score += 15
        else:
            if summary['rsi'] > 70:
                score += 25
            elif summary['rsi'] > 55:
                score += 15
        

        rr_score = min(pos_params['risk_reward'] * 10, 25)
        score += rr_score
        

        vol_score = (1 - (summary['volatility'] / 0.02)) * 20 
        score += max(min(vol_score, 20), 0)
        
        return score

    def _calculate_position_parameters(self, base_currency, current_price, volatility):
        """
        Calculate advanced position parameters including dynamic position sizing and risk management.
        
        Args:
            base_currency (str): Base currency of the pair
            current_price (float): Current market price
            volatility (float): Current volatility measure
            
        Returns:
            dict: Complete position parameters including size, entry, exits, and risk metrics
        """

        config = self.position_config.get(base_currency, {'base_lot': 100000, 'risk_factor': 1.0})
        base_lot = config['base_lot']
        risk_factor = config['risk_factor']
        

        atr = volatility * current_price
        daily_range = atr * np.sqrt(252) 
        

        volatility_adjustment = 1.0
        if volatility > 0.015: 
            volatility_adjustment = 0.7
        elif volatility > 0.008:  
            volatility_adjustment = 0.85
        elif volatility < 0.004:  
            volatility_adjustment = 1.2
            
      
        currency_volatility = {
            'JPY': 1.2, 
            'CHF': 0.9, 
            'EUR': 1.0,
            'GBP': 0.95,
            'USD': 1.0,
            'AUD': 0.85,
            'NZD': 0.85,
            'CAD': 0.9
        }
        
        currency_adj = currency_volatility.get(base_currency, 1.0)
        adjusted_position = base_lot * volatility_adjustment * currency_adj
        

        if volatility < 0.005:
            stop_distance = max(atr * 1.2, daily_range * 0.1)
            profit_distance = stop_distance * 2.8  
        elif volatility < 0.01:  
            stop_distance = max(atr * 1.5, daily_range * 0.15)
            profit_distance = stop_distance * 2.3
        else:  
            stop_distance = max(atr * 2.0, daily_range * 0.2)
            profit_distance = stop_distance * 1.8
        
        
        min_pip_value = 0.0001 if 'JPY' not in base_currency else 0.01
        stop_distance, profit_distance = self._calculate_dynamic_distances(
            volatility, atr, daily_range, base_currency
        )
        

        entry_main = current_price
        entry_scale_1 = current_price * 0.9995 
        entry_scale_2 = current_price * 0.9990 
        

        risk_amount = stop_distance * adjusted_position
        potential_return = profit_distance * adjusted_position
        risk_reward_ratio = profit_distance / stop_distance
        expected_value = (risk_reward_ratio * 0.45 - 0.55) * risk_amount
        
        # Generate confidence score
        confidence_score = min(
            (risk_reward_ratio * 20) +  
            (1/volatility * 30) +      
            (adjusted_position/base_lot * 25) + 
            25,  
            100 
        )
        
        return {
            'position_size': adjusted_position,
            'entry_price': entry_main,
            'entry_scale_1': entry_scale_1,
            'entry_scale_2': entry_scale_2,
            'stop_loss': entry_main - stop_distance,
            'take_profit': entry_main + profit_distance,
            'risk_reward': risk_reward_ratio,
            'confidence': confidence_score,
            'expected_return': expected_value,
            'risk_amount': risk_amount,
            'volatility_class': 'Low' if volatility < 0.005 else 'Medium' if volatility < 0.01 else 'High',
            'position_adjustment': volatility_adjustment,
            'currency_adjustment': currency_adj,
        }

    def get_top_opportunities(self, min_risk_reward=1.5):
        """Get top trading opportunities based on signal strength"""
        if self.market_data.empty:
            self.load_market_data()
            
        opportunities = self.market_data[
            self.market_data['risk_reward'] >= min_risk_reward
        ].sort_values('signal_strength', ascending=False)
        
        return opportunities

    def format_trade_recommendation(self, row):
        """Format a trade recommendation into a readable string"""
        return (
            f"Trade {row['pair']} | "
            f"Signal Strength: {row['signal_strength']:.1f} | "
            f"Entry: {row['entry_price']:.4f} | "
            f"Stop: {row['stop_loss']:.4f} | "
            f"Target: {row['take_profit']:.4f} | "
            f"R/R: {row['risk_reward']:.1f} | "
            f"Size: {row['position_size']:,.0f} {row['base_currency']}"
        )

if __name__ == "__main__":
    from yahoo_currency_wrapper import YahooCurrencyWrapper
    
    processor = ForexDataProcessor(YahooCurrencyWrapper())
    data = processor.load_market_data()
    opportunities = processor.get_top_opportunities()
    
    print("\nTop Trading Opportunities:")
    for _, opportunity in opportunities.head().iterrows():
        print(processor.format_trade_recommendation(opportunity))