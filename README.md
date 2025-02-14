# Market Trading Dashboard

A real-time forex market monitoring dashboard built with Python, providing live currency pair analysis, technical indicators, and visual market insights.

## Project Context

This project represents was part of my early 2025 journey into financial market analysis and Python development. Built as a personal learning tool, it combines:

- Learning about Forex trading and technical analysis
- Exploring real-world financial data through Yahoo Finance's API
- Practicing Python development with modern libraries
- Creating an intuitive terminal-based UI for market data visualization

The dashboard serves as both a learning platform and a practical tool, helping me understand:

- How to process and visualize live market data
- Basic trading concepts and indicators
- Real-time data handling in Python
- Building interactive terminal applications

## Features

- **Real-Time Market Overview**:
  - Live currency rates and 24-hour changes
  - Visual trend indicators (🚀 bullish, 🔻 bearish)
  - RSI conditions (🔥 overbought, 🧊 oversold, ✨ neutral)
  - Volatility levels (😴 low, 🎯 medium, 🌋 high)
  - Opportunity scoring (⭐⭐⭐ high, ⭐⭐ medium, ⭐ low)

- **Technical Analysis**:
  - Current rates and daily changes
  - Trend analysis with moving averages
  - RSI (Relative Strength Index)
  - Volatility measurements
  - Support and resistance levels

- **Trading Parameters**:
  - Position size recommendations
  - Entry price calculations
  - Take-profit and stop-loss levels
  - Risk/reward ratios
  - Opportunity scores (0-100)

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/market-trading-dashboard.git
cd market-trading-dashboard

# Install the package
pip install -e .
```

## Usage

### Command Line Interface

```bash
# Basic usage
market-dashboard

# With custom update interval (in seconds)
market-dashboard --update-interval 30

# With custom risk/reward threshold
market-dashboard --min-risk-reward 2.0

# Clear terminal before starting
market-dashboard --clear
```

### Python API

```python
from market_dashboard import YahooCurrencyWrapper, MarketOpportunityDashboard

# Initialize components
wrapper = YahooCurrencyWrapper()
dashboard = MarketOpportunityDashboard()

# Run the live dashboard
dashboard.run_dashboard()
```

## Dashboard Components

### Market Summary Header

- Last update timestamp
- Data freshness status (Live/Delayed/Offline)
- Available pairs count
- Trading opportunity statistics

### Market Overview Table

- Currency pair symbols
- Current rates and daily changes
- Technical indicators
- Position parameters
- Risk/reward ratios
- Opportunity scores

### Trading Opportunities Footer

- Top 3 trading opportunities
- Medal indicators (🥇 1st, 🥈 2nd, 🥉 3rd)
- Quick position recommendations
- Key metrics summary

## Configuration

```python
dashboard = MarketOpportunityDashboard()
dashboard.trading_config.update({
    'min_risk_reward': 1.5,
    'min_confidence': 60,
    'max_volatility': 0.02,
    'rsi_oversold': 30,
    'rsi_overbought': 70
})
```

## Development

### Project Structure
```

market_dashboard/
├── __init__.py
├── cli.py                  # Command-line interface
├── dashboard.py            # Main dashboard implementation
├── yahoo_currency_wrapper.py  # Market data provider
└── forex_data_processor.py   # Data analysis tools
```

### Running Tests

```bash
pytest tests/
```

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Disclaimer

Had to add this in for anyone looking to use it make market decisions:
This software is for educational and informational purposes only. Trading forex carries significant risks. Always conduct proper research and consult with a licensed financial advisor before making trading decisions.

Trading is risky don't lose your money!
