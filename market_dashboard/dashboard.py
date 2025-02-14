import time
from datetime import datetime
import random
import os
import pandas as pd
import numpy as np
from rich.live import Live
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich.layout import Layout
from rich import box
from rich.progress import Progress
from forex_data_processor import ForexDataProcessor
from yahoo_currency_wrapper import YahooCurrencyWrapper
import sys

class MarketOpportunityDashboard:
    def __init__(self):
        """
        Initializes the Dashboard class.
        Attributes:
            console (Console): An instance of the Console class for displaying output.
            wrapper (YahooCurrencyWrapper): An instance of YahooCurrencyWrapper for fetching currency data.
            processor (ForexDataProcessor): An instance of ForexDataProcessor for processing forex data.
            market_data (pd.DataFrame): A DataFrame to store market data.
            opportunity_cache (pd.DataFrame): A DataFrame to cache trading opportunities.
            last_update (datetime or None): The timestamp of the last update. Initially set to None.
            update_interval (int): The interval in seconds for updating market data. Default is 60 seconds.
            trading_config (dict): A dictionary containing trading thresholds:
                - min_risk_reward (float): Minimum risk-reward ratio.
                - min_confidence (int): Minimum confidence level.
                - max_volatility (float): Maximum acceptable volatility.
                - rsi_oversold (int): RSI value indicating oversold conditions.
                - rsi_overbought (int): RSI value indicating overbought conditions.
        """
        self.console = Console()
        self.wrapper = YahooCurrencyWrapper()
        self.processor = ForexDataProcessor(self.wrapper)
        self.market_data = pd.DataFrame()
        self.opportunity_cache = pd.DataFrame()
        self.last_update = None
        self.update_interval = 60
        
        
        self.trading_config = {
            'min_risk_reward': 1.5,
            'min_confidence': 60,
            'max_volatility': 0.02,
            'rsi_oversold': 30,
            'rsi_overbought': 70
        }
        
        self.initialize_dashboard()

    def initialize_dashboard(self):
        """
        Initializes the trading dashboard by loading market data and analyzing opportunities.
        This method performs the following steps:
        1. Loads market data using the processor and updates the progress.
        2. Analyzes trading opportunities and updates the progress.
        3. Records the time of the last update.
        Uses the Progress context manager to display progress for each task.
        """
        with Progress() as progress:
            task1 = progress.add_task("[cyan]Loading market data...", total=100)
            self.market_data = self.processor.load_market_data()
            progress.update(task1, completed=50)
            
            task2 = progress.add_task("[green]Analyzing opportunities...", total=100)
            self.analyze_opportunities()
            progress.update(task2, completed=100)
            
            self.last_update = datetime.now()

    def analyze_opportunities(self)->None:
        """
        Analyzes trading opportunities based on market data and calculates opportunity scores.
        This method processes the market data to identify potential trading opportunities.
        It calculates position parameters for each market data row and uses an enhanced
        scoring system to evaluate the opportunities. The results are stored in the
        `opportunity_cache` attribute, sorted by the opportunity score in descending order.
        Returns:
            None
        """
        if self.market_data.empty:
            return

        opportunities = []
        for _, row in self.market_data.iterrows():
            trade_params = self.processor._calculate_position_parameters(
                row['base_currency'],
                row['current_rate'],
                row['volatility']
            )
            

            score = self._calculate_opportunity_score(row, trade_params)
            
            opportunities.append({
                **row.to_dict(),
                **trade_params,
                'opportunity_score': score
            })
        
        self.opportunity_cache = pd.DataFrame(opportunities).sort_values(
            'opportunity_score', ascending=False
        )

    def _calculate_opportunity_score(self, row:dict, trade_params:dict)->int:
        """
        Calculate comprehensive opportunity score based on various trading parameters.
        The score is calculated based on the following criteria:
        - Trend alignment (0-30 points): 
          - Adds 30 points if the trend is 'Bullish' and expected return is positive.
          - Adds 30 points if the trend is 'Bearish' and expected return is negative.
        - RSI conditions (0-20 points): 
          - Adds 20 points if the trend is 'Bullish' and RSI is below the oversold threshold.
          - Adds 20 points if the trend is 'Bearish' and RSI is above the overbought threshold.
        - Risk/Reward ratio (0-25 points): 
          - Adds points based on the risk/reward ratio, up to a maximum of 25 points.
        - Volatility conditions (0-15 points): 
          - Adds points based on the inverse of the volatility, up to a maximum of 15 points.
        - Market momentum (0-10 points): 
          - Adds points based on the absolute value of the day's change, up to a maximum of 10 points.
        The final score is capped at 100 points.
        Args:
            row (dict): A dictionary containing market data for a specific trading instrument.
            trade_params (dict): A dictionary containing trading parameters such as expected return and risk/reward ratio.
        Returns:
            int: The calculated opportunity score, ranging from 0 to 100.
        """
        """Calculate comprehensive opportunity score"""
        score = 0
        

        if row['trend'] == 'Bullish' and trade_params['expected_return'] > 0:
            score += 30
        elif row['trend'] == 'Bearish' and trade_params['expected_return'] < 0:
            score += 30
        

        if row['trend'] == 'Bullish' and row['rsi'] < self.trading_config['rsi_oversold']:
            score += 20
        elif row['trend'] == 'Bearish' and row['rsi'] > self.trading_config['rsi_overbought']:
            score += 20
        

        rr_score = min(trade_params['risk_reward'] * 10, 25)
        score += rr_score
        

        vol_score = (1 - (row['volatility'] / self.trading_config['max_volatility'])) * 15
        score += max(vol_score, 0)
        
        momentum_score = abs(row['day_change']) * 2
        score += min(momentum_score, 10)
        
        return min(score, 100)

    def generate_market_overview_table(self)->Table:
        """
        Generates a table displaying an overview of the currency market.
        The table includes various columns such as Pair, Rate, 24h %, Trend, RSI, Vol, Position, Entry, T/P, S/L, R/R, and Score.
        Each column is styled and justified according to the specifications provided in the columns list.
        Returns:
            Table: A rich Table object containing the market overview data.
        Note:
            The table is populated with data from the `opportunity_cache` if it is not empty.
        """
        table = Table(
            title="🌍 Currency Market Overview",
            box=box.ROUNDED,
            title_style="bold magenta"
        )
        

        columns = [
            ("Pair", "cyan", "center"),
            ("Rate", "green", "right"),
            ("24h %", None, "right"),
            ("Trend", None, "center"),
            ("RSI", None, "right"),
            ("Vol", None, "right"),
            ("Position", None, "right"),
            ("Entry", None, "right"),
            ("T/P", None, "right"),
            ("S/L", None, "right"),
            ("R/R", None, "center"),
            ("Score", None, "right")
        ]
        
        for name, style, justify in columns:
            table.add_column(name, style=style, justify=justify)
        
    
        if not self.opportunity_cache.empty:
            for _, row in self.opportunity_cache.iterrows():
                self._add_market_row(table, row)
        
        return table

    def _add_market_row(self, table:Table, row:dict)->None:
        """
        Add a single market row with enhanced formatting to the provided table.
        Args:
            table (Table): The table object to which the row will be added.
            row (dict): A dictionary containing market data for a single row. 
                Expected keys include:
                    - 'pair' (str): The trading pair.
                    - 'current_rate' (float): The current exchange rate.
                    - 'day_change' (float): The percentage change in the rate for the day.
                    - 'trend' (str): The market trend, either 'Bullish' or 'Bearish'.
                    - 'rsi' (float): The Relative Strength Index value.
                    - 'volatility' (float): The market volatility.
                    - 'position_size' (float): The size of the trading position.
                    - 'entry_price' (float): The entry price for the trade.
                    - 'take_profit' (float): The take profit price.
                    - 'stop_loss' (float): The stop loss price.
                    - 'risk_reward' (float): The risk-reward ratio.
                    - 'opportunity_score' (int): The opportunity score for the trade.
        Returns:
            None
        """



        trend_emoji = "🚀" if row['trend'] == 'Bullish' else "🔻"
        rsi_emoji = self._get_rsi_emoji(row['rsi'])
        vol_emoji = self._get_volatility_emoji(row['volatility'])
        score_emoji = self._get_score_emoji(row['opportunity_score'])
        

        change_style = "green" if row['day_change'] > 0 else "red"
        score_style = "green" if row['opportunity_score'] >= 70 else (
            "yellow" if row['opportunity_score'] >= 50 else "red"
        )
        
        table.add_row(
            row['pair'],
            f"{row['current_rate']:.4f}",
            f"[{change_style}]{row['day_change']:+.2f}%",
            f"{row['trend']} {trend_emoji}",
            f"{row['rsi']:.1f} {rsi_emoji}",
            f"{row['volatility']:.3f} {vol_emoji}",
            f"{row['position_size']:,.0f}",
            f"{row['entry_price']:.4f}",
            f"{row['take_profit']:.4f}",
            f"{row['stop_loss']:.4f}",
            f"{row['risk_reward']:.1f}",
            f"[{score_style}]{row['opportunity_score']:.0f} {score_emoji}"
        )

    def _get_score_emoji(self, score:int)->str:
        """
        Returns an emoji representation of the score.

        Args:
            score (int): The score to be evaluated.

        Returns:
            str: A string containing emojis representing the score.
                 - "⭐⭐⭐" for scores 80 and above.
                 - "⭐⭐" for scores 60 to 79.
                 - "⭐" for scores 40 to 59.
                 - "❗" for scores below 40.
        """
        if score >= 80: return "⭐⭐⭐"
        if score >= 60: return "⭐⭐"
        if score >= 40: return "⭐"
        return "❗"

    def _get_rsi_emoji(self, rsi:int)->str:
        """
        Returns an emoji representation based on the Relative Strength Index (RSI) value.

        Args:
            rsi (int): The RSI value to evaluate.

        Returns:
            str: An emoji string representing the RSI state:
                 - "🔥" if RSI is greater than the overbought threshold.
                 - "🧊" if RSI is less than the oversold threshold.
                 - "✨" if RSI is within normal range.
        """
        if rsi > self.trading_config['rsi_overbought']: return "🔥"
        if rsi < self.trading_config['rsi_oversold']: return "🧊"
        return "✨"

    def _get_volatility_emoji(self, volatility:float)->str:
        """
        Returns an emoji representing the level of market volatility.

        Args:
            volatility (float): The volatility value to evaluate.

        Returns:
            str: An emoji string representing the volatility level.
                - "😴" for volatility less than 0.005
                - "🎯" for volatility between 0.005 and 0.01
                - "🌋" for volatility 0.01 or higher
        """
        if volatility < 0.005: return "😴"
        if volatility < 0.01: return "🎯"
        return "🌋"

    def create_header(self)->Panel:
        """
        Create an enhanced header with detailed market statistics.
        This method generates a header panel that includes the current time, 
        the status of the market data update, and detailed market statistics 
        if available. The status indicates whether the data is live, delayed, 
        or offline based on the age of the last update.
        Returns:
            Panel: A rich Panel object containing the formatted header with 
            market statistics and update status.
        """
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        update_age = (datetime.now() - self.last_update).seconds
        
        if not self.opportunity_cache.empty:
            stats = self._generate_market_stats()
            status = (
                f"[green]Live[/green]" if update_age < random.randint(0, self.update_interval)
                else f"[yellow]Delayed ({update_age}s)[/yellow]"
            )
        else:
            stats = "No market data available"
            status = "[red]Offline[/red]"

        return Panel(
            f"🕒 Last Update: {current_time} | Status: {status}\n{stats}",
            title="Market Summary",
            style="bold white"
        )

    def _generate_market_stats(self):
        df = self.opportunity_cache
        strong_opps = len(df[df['opportunity_score'] >= 70])
        moderate_opps = len(df[df['opportunity_score'].between(50, 70)])
        
        return (
            f"[cyan]Pairs: {len(df)}[/cyan] | "
            f"[green]Strong Opportunities: {strong_opps}[/green] | "
            f"[yellow]Moderate Opportunities: {moderate_opps}[/yellow] | "
            f"[blue]Average Score: {df['opportunity_score'].mean():.1f}[/blue]"
        )

    def create_footer(self):
        """Create enhanced footer with detailed trade recommendations"""
        if not self.opportunity_cache.empty:
            top_trades = self.opportunity_cache.head(3)
            recommendations = []
            
            for _, trade in top_trades.iterrows():
                rec = (
                    f"{'🥇' if trade.name == 0 else '🥈' if trade.name == 1 else '🥉'} "
                    f"{'Buy' if trade['trend'] == 'Bullish' else 'Sell'} "
                    f"{trade['position_size']:,.0f} {trade['pair']} @ "
                    f"{trade['current_rate']:.4f} → {trade['take_profit']:.4f} "
                    f"(Score: {trade['opportunity_score']:.0f}, "
                    f"R/R: {trade['risk_reward']:.1f})"
                )
                recommendations.append(rec)
            
            footer_text = "\n".join(recommendations)
        else:
            footer_text = "No trading opportunities available"

        return Panel(
            footer_text,
            title="Top Trading Opportunities",
            style="bold green"
        )
    
    def generate_layout(self):
        """Generate enhanced dashboard layout"""
        layout = Layout()
        layout.split(
            Layout(self.create_header(), size=4),
            Layout(self.generate_market_overview_table()),
            Layout(self.create_footer(), size=4)
        )
        return layout

    def refresh_data(self):
        """Refresh market data"""
        self.market_data = self.processor.load_market_data()

    def run_dashboard(self):
        """Run the live dashboard with periodic updates"""
        try:
            with Live(self.generate_layout(), refresh_per_second=1) as live:
                update_counter = 0
                while True:
                    if update_counter >= random.randint(30, 90):
                        self.refresh_data()
                        update_counter = 0
                    live.update(self.generate_layout())
                    time.sleep(1)
                    update_counter += 1
        except KeyboardInterrupt:
            self.console.print("\n[bold green]Dashboard closed. Happy trading! 👋[/bold green]")
            sys.exit(0)

if __name__ == "__main__":
    os.system('cls' if os.name == 'nt' else 'clear')
    console = Console()
    console.print("[bold cyan]Initializing Enhanced Forex Trading Dashboard...[/bold cyan]")
    
    dashboard = MarketOpportunityDashboard()
    dashboard.run_dashboard()