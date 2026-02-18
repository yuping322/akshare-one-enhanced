"""Utility functions for akshare-one."""


def convert_xieqiu_symbol(symbol: str) -> str:
    """Convert symbol to XueQiu format.

    Args:
        symbol: Stock symbol in various formats
                 - A-shares: 600000, 000001, 300001, 688001
                 - B-shares: 900901, 200002
                 - Northbound: HK00001
                 - US stocks: AAPL, MSFT

    Returns:
        XueQiu formatted symbol:
        - SH600000 (Shanghai)
        - SZ000001 (Shenzhen)
        - SH688001 (STAR Market)
        - BJ430047 (Beijing Stock Exchange)
        - HK00700 (Hong Kong)
        - US tickers remain unchanged

    Examples:
        >>> convert_xieqiu_symbol("600000")
        'SH600000'
        >>> convert_xieqiu_symbol("000001")
        'SZ000001'
        >>> convert_xieqiu_symbol("AAPL")
        'AAPL'
    """
    if not symbol:
        return symbol

    # Already in XueQiu format
    if symbol.startswith(("SH", "SZ", "BJ", "HK")) and len(symbol) > 2:
        return symbol

    # A-shares: Shanghai (600xxx, 601xxx, 603xxx, 605xxx, 688xxx)
    if symbol.startswith("6") or symbol.startswith("68"):
        return f"SH{symbol}"

    # A-shares: Shenzhen (000xxx, 001xxx, 002xxx, 003xxx, 300xxx, 301xxx)
    if symbol.startswith(("0", "3")):
        return f"SZ{symbol}"

    # Beijing Stock Exchange (8xxxxx, 4xxxxx)
    if symbol.startswith(("8", "4")):
        return f"BJ{symbol}"

    # Shanghai B-shares (900xxx)
    if symbol.startswith("9"):
        return f"SH{symbol}"

    # Shenzhen B-shares (200xxx)
    if symbol.startswith("2"):
        return f"SZ{symbol}"

    # Hong Kong stocks (numeric, typically 5 digits)
    if symbol.isdigit() and len(symbol) <= 5:
        return f"HK{symbol.zfill(5)}"

    # US stocks and others: return as-is
    return symbol


def normalize_symbol(symbol: str) -> str:
    """Normalize stock symbol to standard format.

    Removes exchange prefix and returns clean symbol.

    Args:
        symbol: Symbol in various formats (SH600000, 600000.SH, etc.)

    Returns:
        Clean symbol (e.g., "600000")

    Examples:
        >>> normalize_symbol("SH600000")
        '600000'
        >>> normalize_symbol("600000.SH")
        '600000'
    """
    if not symbol:
        return symbol

    # Remove common prefixes
    for prefix in ["SH", "SZ", "BJ", "HK"]:
        if symbol.startswith(prefix):
            return symbol[len(prefix) :]

    # Remove suffixes
    if "." in symbol:
        return symbol.split(".")[0]

    return symbol


def detect_market(symbol: str) -> str:
    """Detect stock market from symbol.

    Args:
        symbol: Stock symbol

    Returns:
        Market code: sh, sz, bj, hk, us, or unknown

    Examples:
        >>> detect_market("600000")
        'sh'
        >>> detect_market("000001")
        'sz'
        >>> detect_market("AAPL")
        'us'
    """
    if not symbol:
        return "unknown"

    # Remove prefix if present
    clean = normalize_symbol(symbol)

    if clean.startswith("6") or clean.startswith("9"):
        return "sh"
    elif clean.startswith(("0", "2", "3")):
        return "sz"
    elif clean.startswith(("8", "4")):
        return "bj"
    elif clean.isdigit() and len(clean) <= 5:
        return "hk"
    elif clean.isalpha():
        return "us"

    return "unknown"


__all__ = ["convert_xieqiu_symbol", "normalize_symbol", "detect_market"]
