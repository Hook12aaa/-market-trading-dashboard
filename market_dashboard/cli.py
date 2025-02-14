import argparse
import os
import sys
from rich.console import Console
from .dashboard import MarketOpportunityDashboard

def parse_args():
    parser = argparse.ArgumentParser(description="Market Trading Dashboard")
    parser.add_argument(
        "--update-interval",
        type=int,
        default=60,
        help="Data update interval in seconds (default: 60)",
    )
    parser.add_argument(
        "--min-risk-reward",
        type=float,
        default=1.5,
        help="Minimum risk/reward ratio for opportunities (default: 1.5)",
    )
    parser.add_argument(
        "--clear",
        action="store_true",
        help="Clear terminal before starting dashboard",
    )
    return parser.parse_args()

def main():
    args = parse_args()
    
    if args.clear:
        os.system('cls' if os.name == 'nt' else 'clear')
    
    console = Console()
    console.print("[bold cyan]Initializing Market Trading Dashboard...[/bold cyan]")
    
    try:
        dashboard = MarketOpportunityDashboard()
        dashboard.update_interval = args.update_interval
        dashboard.trading_config['min_risk_reward'] = args.min_risk_reward
        dashboard.run_dashboard()
    except KeyboardInterrupt:
        console.print("\n[bold green]Dashboard closed. Happy trading! 👋[/bold green]")
        sys.exit(0)
    except Exception as e:
        console.print(f"[bold red]Error: {str(e)}[/bold red]")
        sys.exit(1)

if __name__ == "__main__":
    main()
