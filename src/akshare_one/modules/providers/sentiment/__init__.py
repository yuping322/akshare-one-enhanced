"""Sentiment providers."""
from .base import SentimentFactory, SentimentProvider
from .eastmoney import EastmoneySentimentProvider

__all__ = ["SentimentFactory", "SentimentProvider", "EastmoneySentimentProvider"]
