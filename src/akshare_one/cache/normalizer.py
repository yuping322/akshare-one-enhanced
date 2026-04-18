"""Symbol normalization for akshare_one.

Converts between different Chinese stock code formats:
- 6-digit: "600000"
- Prefix: "sh600000", "sz000001"
- JQ (JoinQuant) format: "600000.XSHG", "000001.XSHE"
"""

SYMBOL_ZFILL_WIDTH = 6


class SymbolNormalizer:
    """Unified symbol normalization.

    All methods accept any supported format and return the requested format.
    """

    @staticmethod
    def normalize(symbol: str) -> str:
        """Normalize to 6-digit pure numeric code.

        Args:
            symbol: Stock code in any supported format.

        Returns:
            6-digit zero-padded string.

        Example:
            >>> SymbolNormalizer.normalize("sh600000")
            '600000'
            >>> SymbolNormalizer.normalize("000001.XSHE")
            '000001'
        """
        s = symbol.upper().strip()
        if s.startswith(("SH", "SZ")):
            s = s[2:]
        if ".XSHG" in s or ".XSHE" in s:
            s = s.split(".")[0]
        return s.zfill(SYMBOL_ZFILL_WIDTH)

    @staticmethod
    def to_jq(symbol: str) -> str:
        """Convert to JoinQuant format (CODE.XSHG or CODE.XSHE).

        Shanghai exchange (codes starting with 6 or 9) uses .XSHG.
        Shenzhen exchange uses .XSHE.

        Args:
            symbol: Stock code in any supported format.

        Returns:
            JoinQuant format string.

        Example:
            >>> SymbolNormalizer.to_jq("600000")
            '600000.XSHG'
            >>> SymbolNormalizer.to_jq("sz000001")
            '000001.XSHE'
        """
        s = SymbolNormalizer.normalize(symbol)
        exchange = "XSHG" if s.startswith(("6", "9")) else "XSHE"
        return f"{s}.{exchange}"

    @staticmethod
    def to_prefix(symbol: str) -> str:
        """Convert to prefix format (shCODE or szCODE).

        Shanghai exchange (codes starting with 6 or 9) uses "sh".
        Shenzhen exchange uses "sz".

        Args:
            symbol: Stock code in any supported format.

        Returns:
            Prefix format string.

        Example:
            >>> SymbolNormalizer.to_prefix("600000.XSHG")
            'sh600000'
            >>> SymbolNormalizer.to_prefix("000001")
            'sz000001'
        """
        s = SymbolNormalizer.normalize(symbol)
        prefix = "sh" if s.startswith(("6", "9")) else "sz"
        return f"{prefix}{s}"
