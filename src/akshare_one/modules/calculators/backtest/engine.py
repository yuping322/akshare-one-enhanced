"""
Backtest execution engine.
"""

import pandas as pd


class BacktestEngine:
    """Simple backtest execution engine."""

    def __init__(self, initial_capital: float = 1_000_000):
        self.initial_capital = initial_capital
        self.capital = initial_capital
        self.positions: dict[str, int] = {}
        self.trades: list[dict] = []

    def run(self, data: pd.DataFrame, signals: pd.Series, **kwargs) -> pd.DataFrame:
        """Run backtest on historical data with signals."""
        portfolio_values = []
        for date, signal in signals.items():
            if date not in data.index:
                continue
            row = data.loc[date]
            if signal > 0:
                self._buy(row.get("close", 0), date)
            elif signal < 0:
                self._sell(row.get("close", 0), date)
            portfolio_values.append(
                {
                    "date": date,
                    "value": self._portfolio_value(row.get("close", 0)),
                }
            )
        return pd.DataFrame(portfolio_values).set_index("date")

    def _buy(self, price: float, date: str):
        """Execute buy order."""
        if price <= 0:
            return
        shares = int(self.capital // price)
        if shares > 0:
            cost = shares * price
            self.capital -= cost
            self.positions["stock"] = self.positions.get("stock", 0) + shares
            self.trades.append({"date": date, "action": "buy", "price": price, "shares": shares})

    def _sell(self, price: float, date: str):
        """Execute sell order."""
        shares = self.positions.get("stock", 0)
        if shares > 0:
            revenue = shares * price
            self.capital += revenue
            self.positions["stock"] = 0
            self.trades.append({"date": date, "action": "sell", "price": price, "shares": shares})

    def _portfolio_value(self, current_price: float) -> float:
        """Calculate current portfolio value."""
        shares = self.positions.get("stock", 0)
        return self.capital + shares * current_price
