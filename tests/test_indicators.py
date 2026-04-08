import unittest

import numpy as np
import pandas as pd
import pytest

from akshare_one.indicators import (
    get_ad,
    get_adosc,
    get_adx,
    get_apo,
    get_aroon,
    get_aroonosc,
    get_atr,
    get_bollinger_bands,
    get_bop,
    get_cci,
    get_cmo,
    get_dx,
    get_ema,
    get_macd,
    get_mfi,
    get_minus_di,
    get_minus_dm,
    get_mom,
    get_obv,
    get_plus_di,
    get_plus_dm,
    get_ppo,
    get_roc,
    get_rocp,
    get_rocr,
    get_rocr100,
    get_rsi,
    get_sar,
    get_sma,
    get_stoch,
    get_trix,
    get_tsf,
    get_ultosc,
    get_willr,
)
from akshare_one.modules.indicators import TALIB_AVAILABLE


class TestIndicators(unittest.TestCase):
    def setUp(self):
        # Use a predictable series for easier debugging if needed
        data = {
            "open": np.arange(100, 200, 1.0),
            "high": np.arange(101, 201, 1.0),
            "low": np.arange(99, 199, 1.0),
            "close": np.arange(100, 200, 1.0),
            "volume": np.arange(1000, 2000, 10.0),
        }
        self.df = pd.DataFrame(data)

    # Explicitly test simple implementation
    def test_simple_sma(self):
        result = get_sma(self.df, 20, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("sma" in result.columns)
        self.assertTrue(result.iloc[:19]["sma"].isna().all())
        self.assertFalse(result.iloc[19:]["sma"].isna().any())

    def test_simple_ema(self):
        result = get_ema(self.df, 20, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("ema" in result.columns)
        self.assertTrue(result.iloc[:19]["ema"].isna().all())
        self.assertFalse(result.iloc[19:]["ema"].isna().any())

    def test_simple_rsi(self):
        result = get_rsi(self.df, 14, calculator_type="simple")
        self.assertTrue("rsi" in result.columns)
        self.assertTrue(result.iloc[:14]["rsi"].isna().all())
        self.assertFalse(result.iloc[14:]["rsi"].isna().any())

    def test_simple_macd(self):
        result = get_macd(self.df, 12, 26, 9, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertEqual(set(result.columns), {"macd", "signal", "histogram"})
        self.assertTrue(result.iloc[:25]["macd"].isna().all())
        self.assertTrue(result.iloc[:33]["signal"].isna().all())
        self.assertTrue(result.iloc[:33]["histogram"].isna().all())

    def test_simple_bollinger_bands(self):
        result = get_bollinger_bands(self.df, 20, 2, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertEqual(set(result.columns), {"upper_band", "middle_band", "lower_band"})
        self.assertTrue(result.iloc[:19]["upper_band"].isna().all())
        self.assertFalse(result.iloc[19:]["upper_band"].isna().any())

    def test_simple_stoch(self):
        result = get_stoch(self.df, 14, 3, 3, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertEqual(set(result.columns), {"slow_k", "slow_d"})
        # Test handling of zero range (high == low)
        df_zero_range = self.df.copy()
        df_zero_range["high"] = df_zero_range["low"]
        result_zero = get_stoch(df_zero_range, 14, 3, 3, calculator_type="simple")
        self.assertEqual(len(result_zero), len(df_zero_range))
        self.assertTrue(not result_zero["slow_k"].isna().all())  # Should handle zero range

    def test_simple_atr(self):
        result = get_atr(self.df, 14, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("atr" in result.columns)

    def test_simple_willr(self):
        result = get_willr(self.df, 14, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("willr" in result.columns)
        # Test handling of zero range (high == low)
        df_zero_range = self.df.copy()
        df_zero_range["high"] = df_zero_range["low"]
        result_zero = get_willr(df_zero_range, 14, calculator_type="simple")
        self.assertEqual(len(result_zero), len(df_zero_range))

    def test_simple_cci(self):
        result = get_cci(self.df, 14, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("cci" in result.columns)

    def test_simple_adx(self):
        result = get_adx(self.df, 14, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("adx" in result.columns)

    def test_simple_ad(self):
        result = get_ad(self.df, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("ad" in result.columns)
        # Test handling of zero range (high == low)
        df_zero_range = self.df.copy()
        df_zero_range["high"] = df_zero_range["low"]
        result_zero = get_ad(df_zero_range, calculator_type="simple")
        self.assertEqual(len(result_zero), len(df_zero_range))
        self.assertTrue(not result_zero["ad"].isna().all())  # Should handle zero range

    def test_talib_sma(self):
        result = get_sma(self.df, 20, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("sma" in result.columns)
        self.assertTrue(result.iloc[:19]["sma"].isna().all())
        self.assertFalse(result.iloc[19:]["sma"].isna().any())

    def test_talib_ema(self):
        result = get_ema(self.df, 20, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("ema" in result.columns)
        self.assertTrue(result.iloc[:19]["ema"].isna().all())
        self.assertFalse(result.iloc[19:]["ema"].isna().any())

    def test_talib_rsi(self):
        result = get_rsi(self.df, 14, calculator_type="talib")
        self.assertTrue("rsi" in result.columns)
        self.assertTrue(result.iloc[:14]["rsi"].isna().all())
        self.assertFalse(result.iloc[14:]["rsi"].isna().any())

    def test_talib_macd(self):
        result = get_macd(self.df, 12, 26, 9, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertEqual(set(result.columns), {"macd", "signal", "histogram"})
        self.assertTrue(result.iloc[:25]["macd"].isna().all())
        self.assertTrue(result.iloc[:33]["signal"].isna().all())
        self.assertTrue(result.iloc[:33]["histogram"].isna().any())

    def test_talib_bollinger_bands(self):
        result = get_bollinger_bands(self.df, 20, 2, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertEqual(set(result.columns), {"upper_band", "middle_band", "lower_band"})
        self.assertTrue(result.iloc[:19]["upper_band"].isna().all())
        self.assertFalse(result.iloc[19:]["upper_band"].isna().any())

    def test_talib_stoch(self):
        result = get_stoch(self.df, 14, 3, 3, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertEqual(set(result.columns), {"slow_k", "slow_d"})

    def test_talib_atr(self):
        result = get_atr(self.df, 14, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("atr" in result.columns)
        self.assertTrue(result.iloc[:13]["atr"].isna().all())
        self.assertFalse(result.iloc[14:]["atr"].isna().any())

    def test_talib_cci(self):
        result = get_cci(self.df, 14, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("cci" in result.columns)

    def test_talib_adx(self):
        result = get_adx(self.df, 14, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("adx" in result.columns)

    def test_talib_willr(self):
        result = get_willr(self.df, 14, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("willr" in result.columns)

    def test_talib_ad(self):
        result = get_ad(self.df, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("ad" in result.columns)

    def test_talib_adosc(self):
        result = get_adosc(self.df, 3, 10, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("adosc" in result.columns)

    def test_talib_obv(self):
        result = get_obv(self.df, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("obv" in result.columns)

    def test_talib_mom(self):
        result = get_mom(self.df, 10, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("mom" in result.columns)

    def test_talib_sar(self):
        result = get_sar(self.df, 0.02, 0.2, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("sar" in result.columns)

    def test_talib_tsf(self):
        result = get_tsf(self.df, 14, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("tsf" in result.columns)

    def test_talib_apo(self):
        result = get_apo(self.df, 12, 26, 0, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("apo" in result.columns)

    def test_talib_aroon(self):
        result = get_aroon(self.df, 14, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("aroon_down" in result.columns)
        self.assertTrue("aroon_up" in result.columns)

    def test_talib_aroonosc(self):
        result = get_aroonosc(self.df, 14, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("aroonosc" in result.columns)

    def test_talib_bop(self):
        result = get_bop(self.df, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("bop" in result.columns)

    def test_talib_cmo(self):
        result = get_cmo(self.df, 14, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("cmo" in result.columns)

    def test_talib_dx(self):
        result = get_dx(self.df, 14, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("dx" in result.columns)

    def test_talib_mfi(self):
        result = get_mfi(self.df, 14, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("mfi" in result.columns)

    def test_talib_minus_di(self):
        result = get_minus_di(self.df, 14, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("minus_di" in result.columns)

    def test_talib_minus_dm(self):
        result = get_minus_dm(self.df, 14, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("minus_dm" in result.columns)

    def test_talib_plus_di(self):
        result = get_plus_di(self.df, 14, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("plus_di" in result.columns)

    def test_talib_plus_dm(self):
        result = get_plus_dm(self.df, 14, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("plus_dm" in result.columns)

    def test_talib_ppo(self):
        result = get_ppo(self.df, 12, 26, 0, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("ppo" in result.columns)

    def test_talib_roc(self):
        result = get_roc(self.df, 10, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("roc" in result.columns)

    def test_talib_rocp(self):
        result = get_rocp(self.df, 10, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("rocp" in result.columns)

    def test_talib_rocr(self):
        result = get_rocr(self.df, 10, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("rocr" in result.columns)

    def test_talib_rocr100(self):
        result = get_rocr100(self.df, 10, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("rocr100" in result.columns)

    def test_talib_trix(self):
        result = get_trix(self.df, 30, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("trix" in result.columns)

    def test_talib_ultosc(self):
        result = get_ultosc(self.df, 7, 14, 28, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("ultosc" in result.columns)

    # Additional tests for edge cases in simple implementation
    def test_simple_bop_edge_case(self):
        result = get_bop(self.df, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("bop" in result.columns)
        # Test handling of zero range (high == low)
        df_zero_range = self.df.copy()
        df_zero_range["high"] = df_zero_range["low"]
        result_zero = get_bop(df_zero_range, calculator_type="simple")
        self.assertEqual(len(result_zero), len(df_zero_range))
        self.assertTrue(not result_zero["bop"].isna().all())  # Should handle zero range

    def test_simple_mfi_edge_case(self):
        result = get_mfi(self.df, 14, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("mfi" in result.columns)
        # Test handling of zero negative money flow
        df_constant_price = self.df.copy()
        df_constant_price["close"] = 100  # All prices are the same
        result_zero = get_mfi(df_constant_price, 14, calculator_type="simple")
        self.assertEqual(len(result_zero), len(df_constant_price))
        self.assertTrue(not result_zero["mfi"].isna().all())  # Should handle zero negative flow

    def test_simple_dx_edge_case(self):
        result = get_dx(self.df, 14, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("dx" in result.columns)
        # Test handling of zero DI sum
        df_flat = self.df.copy()
        df_flat["high"] = df_flat["low"]  # No directional movement
        result_zero = get_dx(df_flat, 14, calculator_type="simple")
        self.assertEqual(len(result_zero), len(df_flat))
        self.assertTrue(not result_zero["dx"].isna().all())  # Should handle zero DI sum

    def test_simple_cmo_edge_case(self):
        result = get_cmo(self.df, 14, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("cmo" in result.columns)
        # Test handling of zero price movement
        df_flat = self.df.copy()
        df_flat["close"] = 100  # No price movement
        result_zero = get_cmo(df_flat, 14, calculator_type="simple")
        self.assertEqual(len(result_zero), len(df_flat))
        self.assertTrue(not result_zero["cmo"].isna().all())  # Should handle zero movement

    def test_simple_ultosc_edge_case(self):
        result = get_ultosc(self.df, 7, 14, 28, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("ultosc" in result.columns)
        # Test handling of zero true range
        df_flat = self.df.copy()
        df_flat["high"] = df_flat["low"]  # Zero true range
        result_zero = get_ultosc(df_flat, 7, 14, 28, calculator_type="simple")
        self.assertEqual(len(result_zero), len(df_flat))
        self.assertTrue(not result_zero["ultosc"].isna().all())  # Should handle zero TR

    def test_simple_sar_edge_case(self):
        result = get_sar(self.df, 0.02, 0.2, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("sar" in result.columns)
        # Test handling of flat market
        df_flat = self.df.copy()
        df_flat["high"] = df_flat["low"] = df_flat["close"]  # Flat market
        result_zero = get_sar(df_flat, 0.02, 0.2, calculator_type="simple")
        self.assertEqual(len(result_zero), len(df_flat))
        self.assertTrue(not result_zero["sar"].isna().all())  # Should handle flat market

    # Tests for other simple implementation functions not covered above
    def test_simple_adosc(self):
        result = get_adosc(self.df, 3, 10, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("adosc" in result.columns)

    def test_simple_obv(self):
        result = get_obv(self.df, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("obv" in result.columns)

    def test_simple_mom(self):
        result = get_mom(self.df, 10, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("mom" in result.columns)

    def test_simple_tsf(self):
        result = get_tsf(self.df, 14, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("tsf" in result.columns)

    def test_simple_apo(self):
        result = get_apo(self.df, 12, 26, 0, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("apo" in result.columns)

    def test_simple_aroon(self):
        result = get_aroon(self.df, 14, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("aroon_up" in result.columns)
        self.assertTrue("aroon_down" in result.columns)

    def test_simple_aroonosc(self):
        result = get_aroonosc(self.df, 14, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("aroonosc" in result.columns)

    def test_simple_ppo(self):
        result = get_ppo(self.df, 12, 26, 0, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("ppo" in result.columns)

    def test_simple_roc(self):
        result = get_roc(self.df, 10, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("roc" in result.columns)

    def test_simple_rocp(self):
        result = get_rocp(self.df, 10, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("rocp" in result.columns)

    def test_simple_rocr(self):
        result = get_rocr(self.df, 10, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("rocr" in result.columns)

    def test_simple_rocr100(self):
        result = get_rocr100(self.df, 10, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("rocr100" in result.columns)

    def test_simple_trix(self):
        result = get_trix(self.df, 30, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("trix" in result.columns)

    def test_simple_minus_di(self):
        result = get_minus_di(self.df, 14, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("minus_di" in result.columns)

    def test_simple_minus_dm(self):
        result = get_minus_dm(self.df, 14, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("minus_dm" in result.columns)

    def test_simple_plus_di(self):
        result = get_plus_di(self.df, 14, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("plus_di" in result.columns)

    def test_simple_plus_dm(self):
        result = get_plus_dm(self.df, 14, calculator_type="simple")
        self.assertEqual(len(result), len(self.df))
        self.assertTrue("plus_dm" in result.columns)

    # Talib-specific comprehensive tests with golden samples
    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_macd_calculation(self):
        result = get_macd(self.df, 12, 26, 9, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertIn("macd", result.columns)
        self.assertIn("signal", result.columns)
        self.assertIn("histogram", result.columns)
        macd_values = result["macd"].dropna()
        signal_values = result["signal"].dropna()
        histogram_values = result["histogram"].dropna()
        self.assertEqual(len(macd_values), len(signal_values))
        self.assertEqual(len(histogram_values), len(signal_values))
        for i in range(len(histogram_values)):
            expected_histogram = macd_values.iloc[i] - signal_values.iloc[i]
            self.assertAlmostEqual(histogram_values.iloc[i], expected_histogram, places=6)

    def test_talib_macd_with_missing_data(self):
        df_missing = self.df.copy()
        df_missing.loc[10:20, "close"] = np.nan
        result = get_macd(df_missing, 12, 26, 9, calculator_type="talib")
        self.assertEqual(len(result), len(df_missing))
        self.assertIn("macd", result.columns)

    def test_talib_rsi_calculation(self):
        result = get_rsi(self.df, 14, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertIn("rsi", result.columns)
        rsi_values = result["rsi"].dropna()
        for rsi_value in rsi_values:
            self.assertGreaterEqual(rsi_value, 0)
            self.assertLessEqual(rsi_value, 100)

    def test_talib_rsi_boundary_values(self):
        df_uptrend = pd.DataFrame(
            {
                "open": np.arange(100, 200, 1.0),
                "high": np.arange(101, 201, 1.0),
                "low": np.arange(99, 199, 1.0),
                "close": np.arange(100, 200, 1.0),
                "volume": np.arange(1000, 2000, 10.0),
            }
        )
        result_up = get_rsi(df_uptrend, 14, calculator_type="talib")
        rsi_values = result_up["rsi"].dropna()
        self.assertTrue((rsi_values > 50).any())
        df_downtrend = pd.DataFrame(
            {
                "open": np.arange(200, 100, -1.0),
                "high": np.arange(201, 101, -1.0),
                "low": np.arange(199, 99, -1.0),
                "close": np.arange(200, 100, -1.0),
                "volume": np.arange(1000, 2000, 10.0),
            }
        )
        result_down = get_rsi(df_downtrend, 14, calculator_type="talib")
        rsi_values_down = result_down["rsi"].dropna()
        self.assertTrue((rsi_values_down < 50).any())

    def test_talib_boll_calculation(self):
        result = get_bollinger_bands(self.df, 20, 2, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertIn("upper_band", result.columns)
        self.assertIn("middle_band", result.columns)
        self.assertIn("lower_band", result.columns)
        for i in range(20, len(self.df)):
            upper = result["upper_band"].iloc[i]
            middle = result["middle_band"].iloc[i]
            lower = result["lower_band"].iloc[i]
            if not (np.isnan(upper) or np.isnan(middle) or np.isnan(lower)):
                self.assertGreaterEqual(upper, middle)
                self.assertGreaterEqual(middle, lower)

    def test_talib_boll_upper_lower(self):
        window = 20
        std_dev = 2
        result = get_bollinger_bands(self.df, window, std_dev, calculator_type="talib")
        for i in range(window, len(self.df)):
            upper = result["upper_band"].iloc[i]
            lower = result["lower_band"].iloc[i]
            if not (np.isnan(upper) or np.isnan(lower)):
                expected_bandwidth = upper - lower
                self.assertGreater(expected_bandwidth, 0)

    def test_talib_kdj_calculation(self):
        result = get_stoch(self.df, 14, 3, 3, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertIn("slow_k", result.columns)
        self.assertIn("slow_d", result.columns)
        k_values = result["slow_k"].dropna()
        d_values = result["slow_d"].dropna()
        for k_val in k_values:
            self.assertGreaterEqual(k_val, 0)
            self.assertLessEqual(k_val, 100)
        for d_val in d_values:
            self.assertGreaterEqual(d_val, 0)
            self.assertLessEqual(d_val, 100)

    def test_talib_atr_calculation(self):
        result = get_atr(self.df, 14, calculator_type="talib")
        self.assertEqual(len(result), len(self.df))
        self.assertIn("atr", result.columns)
        atr_values = result["atr"].dropna()
        for atr_val in atr_values:
            self.assertGreater(atr_val, 0)

    def test_talib_ema_sma_calculation(self):
        ema_result = get_ema(self.df, 20, calculator_type="talib")
        sma_result = get_sma(self.df, 20, calculator_type="talib")
        self.assertEqual(len(ema_result), len(self.df))
        self.assertEqual(len(sma_result), len(self.df))
        self.assertIn("ema", ema_result.columns)
        self.assertIn("sma", sma_result.columns)
        ema_values = ema_result["ema"].dropna()
        sma_values = sma_result["sma"].dropna()
        expected_sma_19 = np.mean(self.df["close"].iloc[0:20])
        self.assertAlmostEqual(sma_values.iloc[0], expected_sma_19, places=5)

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_empty_dataframe_handling(self):
        empty_df = pd.DataFrame(
            {
                "open": [],
                "high": [],
                "low": [],
                "close": [],
                "volume": [],
            }
        )
        with self.assertRaises((KeyError, IndexError, ValueError)):
            get_macd(empty_df, 12, 26, 9, calculator_type="talib")
        with self.assertRaises((KeyError, IndexError, ValueError)):
            get_rsi(empty_df, 14, calculator_type="talib")
        with self.assertRaises((KeyError, IndexError, ValueError)):
            get_bollinger_bands(empty_df, 20, 2, calculator_type="talib")

    def test_talib_sma_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": [10, 11, 12, 13, 14, 15],
                "high": [11, 12, 13, 14, 15, 16],
                "low": [9, 10, 11, 12, 13, 14],
                "close": [10, 11, 12, 13, 14, 15],
                "volume": [1000, 1100, 1200, 1300, 1400, 1500],
            }
        )
        result = get_sma(test_data, 3, calculator_type="talib")
        expected_sma_2 = (10 + 11 + 12) / 3
        self.assertAlmostEqual(result["sma"].iloc[2], expected_sma_2, places=5)

    def test_talib_ema_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": [10, 11, 12, 13, 14, 15],
                "high": [11, 12, 13, 14, 15, 16],
                "low": [9, 10, 11, 12, 13, 14],
                "close": [10, 11, 12, 13, 14, 15],
                "volume": [1000, 1100, 1200, 1300, 1400, 1500],
            }
        )
        result = get_ema(test_data, 3, calculator_type="talib")
        ema_values = result["ema"].dropna()
        self.assertGreater(len(ema_values), 0)

    def test_talib_atr_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
                "high": [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26],
                "low": [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
                "close": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
                "volume": [1000] * 16,
            }
        )
        result = get_atr(test_data, 14, calculator_type="talib")
        atr_values = result["atr"].dropna()
        self.assertGreater(len(atr_values), 0)

    def test_talib_unavailable_fallback(self):
        if not TALIB_AVAILABLE:
            result_rsi = get_rsi(self.df, 14, calculator_type="talib")
            self.assertIn("rsi", result_rsi.columns)
            result_macd = get_macd(self.df, 12, 26, 9, calculator_type="talib")
            self.assertIn("macd", result_macd.columns)

    def test_talib_macd_signal_line_calculation(self):
        result = get_macd(self.df, 12, 26, 9, calculator_type="talib")
        signal_values = result["signal"].dropna()
        self.assertGreater(len(signal_values), 0)

    def test_talib_boll_bandwidth(self):
        result = get_bollinger_bands(self.df, 20, 2, calculator_type="talib")
        for i in range(25, len(self.df)):
            if not result["upper_band"].iloc[i]:
                continue
            upper = result["upper_band"].iloc[i]
            lower = result["lower_band"].iloc[i]
            middle = result["middle_band"].iloc[i]
            if not (np.isnan(upper) or np.isnan(lower) or np.isnan(middle)):
                self.assertGreater(upper, lower)
                self.assertAlmostEqual(middle, (upper + lower) / 2, places=5)


import pytest


@pytest.fixture
def sample_ohlcv_data():
    """提供标准OHLCV测试数据"""
    np.random.seed(42)
    n = 100
    base_price = 100.0
    close_prices = base_price + np.cumsum(np.random.randn(n) * 0.5)
    high_prices = close_prices + np.abs(np.random.randn(n) * 0.3)
    low_prices = close_prices - np.abs(np.random.randn(n) * 0.3)
    open_prices = close_prices + np.random.randn(n) * 0.2
    volumes = np.random.randint(1000000, 2000000, n)

    return pd.DataFrame(
        {"open": open_prices, "high": high_prices, "low": low_prices, "close": close_prices, "volume": volumes}
    )


@pytest.fixture
def small_ohlcv_data():
    """提供小型OHLCV测试数据（用于边界测试）"""
    return pd.DataFrame(
        {
            "open": [10.0, 10.5, 11.0, 10.8, 11.2],
            "high": [10.5, 11.0, 11.2, 11.0, 11.5],
            "low": [9.8, 10.2, 10.8, 10.5, 11.0],
            "close": [10.3, 10.8, 11.0, 10.9, 11.3],
            "volume": [1000000, 1100000, 1200000, 1150000, 1250000],
        }
    )


@pytest.fixture
def empty_dataframe():
    """提供空DataFrame"""
    return pd.DataFrame({"open": [], "high": [], "low": [], "close": [], "volume": []})


@pytest.fixture
def dataframe_with_nan():
    """提供包含NaN的DataFrame"""
    df = pd.DataFrame(
        {
            "open": [10.0, 10.5, np.nan, 10.8, 11.2],
            "high": [10.5, 11.0, 11.2, np.nan, 11.5],
            "low": [9.8, np.nan, 10.8, 10.5, 11.0],
            "close": [10.3, 10.8, np.nan, 10.9, 11.3],
            "volume": [1000000, 1100000, 1200000, 1150000, np.nan],
        }
    )
    return df


class TestTalibSMA:
    def test_talib_sma_calculation(self, sample_ohlcv_data):
        result = get_sma(sample_ohlcv_data, 20, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "sma" in result.columns
        assert result.iloc[:19]["sma"].isna().all()
        assert not result.iloc[19:]["sma"].isna().any()

    def test_talib_sma_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": [10, 11, 12, 13, 14, 15],
                "high": [11, 12, 13, 14, 15, 16],
                "low": [9, 10, 11, 12, 13, 14],
                "close": [10, 11, 12, 13, 14, 15],
                "volume": [1000] * 6,
            }
        )
        result = get_sma(test_data, 3, calculator_type="talib")
        expected_sma = (10 + 11 + 12) / 3
        assert abs(result["sma"].iloc[2] - expected_sma) < 0.0001

    def test_talib_sma_boundary_values(self, small_ohlcv_data):
        result = get_sma(small_ohlcv_data, 2, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "sma" in result.columns

    def test_talib_sma_missing_data(self, dataframe_with_nan):
        result = get_sma(dataframe_with_nan, 3, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "sma" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_sma_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_sma(empty_dataframe, 20, calculator_type="talib")


class TestTalibEMA:
    def test_talib_ema_calculation(self, sample_ohlcv_data):
        result = get_ema(sample_ohlcv_data, 20, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "ema" in result.columns
        assert result.iloc[:19]["ema"].isna().all()
        assert not result.iloc[19:]["ema"].isna().any()

    def test_talib_ema_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": [10, 11, 12, 13, 14, 15],
                "high": [11, 12, 13, 14, 15, 16],
                "low": [9, 10, 11, 12, 13, 14],
                "close": [10, 11, 12, 13, 14, 15],
                "volume": [1000] * 6,
            }
        )
        result = get_ema(test_data, 3, calculator_type="talib")
        ema_values = result["ema"].dropna()
        assert len(ema_values) > 0

    def test_talib_ema_boundary_values(self, small_ohlcv_data):
        result = get_ema(small_ohlcv_data, 2, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "ema" in result.columns

    def test_talib_ema_missing_data(self, dataframe_with_nan):
        result = get_ema(dataframe_with_nan, 3, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "ema" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_ema_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_ema(empty_dataframe, 20, calculator_type="talib")


class TestTalibRSI:
    def test_talib_rsi_calculation(self, sample_ohlcv_data):
        result = get_rsi(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "rsi" in result.columns
        rsi_values = result["rsi"].dropna()
        assert all(0 <= val <= 100 for val in rsi_values)

    def test_talib_rsi_with_known_values(self):
        uptrend_data = pd.DataFrame(
            {
                "open": np.arange(100, 150, 1.0),
                "high": np.arange(101, 151, 1.0),
                "low": np.arange(99, 149, 1.0),
                "close": np.arange(100, 150, 1.0),
                "volume": [1000000] * 50,
            }
        )
        result = get_rsi(uptrend_data, 14, calculator_type="talib")
        rsi_values = result["rsi"].dropna()
        assert any(val > 50 for val in rsi_values)

    def test_talib_rsi_boundary_values(self):
        downtrend_data = pd.DataFrame(
            {
                "open": np.arange(150, 100, -1.0),
                "high": np.arange(151, 101, -1.0),
                "low": np.arange(149, 99, -1.0),
                "close": np.arange(150, 100, -1.0),
                "volume": [1000000] * 50,
            }
        )
        result = get_rsi(downtrend_data, 14, calculator_type="talib")
        rsi_values = result["rsi"].dropna()
        assert any(val < 50 for val in rsi_values)

    def test_talib_rsi_missing_data(self, dataframe_with_nan):
        result = get_rsi(dataframe_with_nan, 14, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "rsi" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_rsi_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_rsi(empty_dataframe, 14, calculator_type="talib")


class TestTalibMACD:
    def test_talib_macd_calculation(self, sample_ohlcv_data):
        result = get_macd(sample_ohlcv_data, 12, 26, 9, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "macd" in result.columns
        assert "signal" in result.columns
        assert "histogram" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_macd_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": np.arange(100, 150, 1.0),
                "high": np.arange(101, 151, 1.0),
                "low": np.arange(99, 149, 1.0),
                "close": np.arange(100, 150, 1.0),
                "volume": [1000000] * 50,
            }
        )
        result = get_macd(test_data, 12, 26, 9, calculator_type="talib")
        macd_values = result["macd"].dropna()
        signal_values = result["signal"].dropna()
        histogram_values = result["histogram"].dropna()
        assert len(macd_values) == len(signal_values)
        assert len(histogram_values) == len(signal_values)

    def test_talib_macd_boundary_values(self, small_ohlcv_data):
        result = get_macd(small_ohlcv_data, 2, 3, 2, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "macd" in result.columns

    def test_talib_macd_missing_data(self, dataframe_with_nan):
        result = get_macd(dataframe_with_nan, 12, 26, 9, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "macd" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_macd_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_macd(empty_dataframe, 12, 26, 9, calculator_type="talib")


class TestTalibBOLL:
    def test_talib_boll_calculation(self, sample_ohlcv_data):
        result = get_bollinger_bands(sample_ohlcv_data, 20, 2, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "upper_band" in result.columns
        assert "middle_band" in result.columns
        assert "lower_band" in result.columns

    def test_talib_boll_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30],
                "high": [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31],
                "low": [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29],
                "close": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30],
                "volume": [1000] * 21,
            }
        )
        result = get_bollinger_bands(test_data, 20, 2, calculator_type="talib")
        upper = result["upper_band"].iloc[20]
        middle = result["middle_band"].iloc[20]
        lower = result["lower_band"].iloc[20]
        assert upper >= middle >= lower

    def test_talib_boll_boundary_values(self, small_ohlcv_data):
        result = get_bollinger_bands(small_ohlcv_data, 2, 1, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "upper_band" in result.columns

    def test_talib_boll_missing_data(self, dataframe_with_nan):
        result = get_bollinger_bands(dataframe_with_nan, 20, 2, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "upper_band" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_boll_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_bollinger_bands(empty_dataframe, 20, 2, calculator_type="talib")


class TestTalibKDJ:
    def test_talib_kdj_calculation(self, sample_ohlcv_data):
        result = get_stoch(sample_ohlcv_data, 9, 3, 3, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "slow_k" in result.columns
        assert "slow_d" in result.columns

    def test_talib_kdj_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": np.arange(100, 130, 1.0),
                "high": np.arange(101, 131, 1.0),
                "low": np.arange(99, 129, 1.0),
                "close": np.arange(100, 130, 1.0),
                "volume": [1000000] * 30,
            }
        )
        result = get_stoch(test_data, 9, 3, 3, calculator_type="talib")
        k_values = result["slow_k"].dropna()
        d_values = result["slow_d"].dropna()
        assert all(0 <= val <= 100 for val in k_values)
        assert all(0 <= val <= 100 for val in d_values)

    def test_talib_kdj_boundary_values(self, small_ohlcv_data):
        result = get_stoch(small_ohlcv_data, 2, 2, 2, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "slow_k" in result.columns

    def test_talib_kdj_missing_data(self, dataframe_with_nan):
        result = get_stoch(dataframe_with_nan, 9, 3, 3, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "slow_k" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_kdj_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_stoch(empty_dataframe, 9, 3, 3, calculator_type="talib")


class TestTalibATR:
    def test_talib_atr_calculation(self, sample_ohlcv_data):
        result = get_atr(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "atr" in result.columns
        atr_values = result["atr"].dropna()
        assert all(val > 0 for val in atr_values)

    def test_talib_atr_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
                "high": [11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26],
                "low": [9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24],
                "close": [10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25],
                "volume": [1000] * 16,
            }
        )
        result = get_atr(test_data, 14, calculator_type="talib")
        atr_values = result["atr"].dropna()
        assert len(atr_values) > 0

    def test_talib_atr_boundary_values(self, small_ohlcv_data):
        result = get_atr(small_ohlcv_data, 2, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "atr" in result.columns

    def test_talib_atr_missing_data(self, dataframe_with_nan):
        result = get_atr(dataframe_with_nan, 14, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "atr" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_atr_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_atr(empty_dataframe, 14, calculator_type="talib")


class TestTalibCCI:
    def test_talib_cci_calculation(self, sample_ohlcv_data):
        result = get_cci(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "cci" in result.columns

    def test_talib_cci_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": np.arange(100, 130, 1.0),
                "high": np.arange(101, 131, 1.0),
                "low": np.arange(99, 129, 1.0),
                "close": np.arange(100, 130, 1.0),
                "volume": [1000000] * 30,
            }
        )
        result = get_cci(test_data, 14, calculator_type="talib")
        cci_values = result["cci"].dropna()
        assert len(cci_values) > 0

    def test_talib_cci_boundary_values(self, small_ohlcv_data):
        result = get_cci(small_ohlcv_data, 2, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "cci" in result.columns

    def test_talib_cci_missing_data(self, dataframe_with_nan):
        result = get_cci(dataframe_with_nan, 14, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "cci" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_cci_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_cci(empty_dataframe, 14, calculator_type="talib")


class TestTalibOBV:
    def test_talib_obv_calculation(self, sample_ohlcv_data):
        result = get_obv(sample_ohlcv_data, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "obv" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_obv_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": [10, 11, 12, 13, 14],
                "high": [11, 12, 13, 14, 15],
                "low": [9, 10, 11, 12, 13],
                "close": [10, 11, 12, 13, 14],
                "volume": [1000, 1100, 1200, 1300, 1400],
            }
        )
        result = get_obv(test_data, calculator_type="talib")
        obv_values = result["obv"]
        assert len(obv_values) == 5
        assert obv_values.iloc[0] == 1000

    def test_talib_obv_boundary_values(self, small_ohlcv_data):
        result = get_obv(small_ohlcv_data, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "obv" in result.columns

    def test_talib_obv_missing_data(self, dataframe_with_nan):
        result = get_obv(dataframe_with_nan, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "obv" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_obv_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_obv(empty_dataframe, calculator_type="talib")


class TestTalibMOM:
    def test_talib_mom_calculation(self, sample_ohlcv_data):
        result = get_mom(sample_ohlcv_data, 10, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "mom" in result.columns

    def test_talib_mom_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": np.arange(100, 120, 1.0),
                "high": np.arange(101, 121, 1.0),
                "low": np.arange(99, 119, 1.0),
                "close": np.arange(100, 120, 1.0),
                "volume": [1000000] * 20,
            }
        )
        result = get_mom(test_data, 10, calculator_type="talib")
        mom_values = result["mom"].dropna()
        assert len(mom_values) > 0

    def test_talib_mom_boundary_values(self, small_ohlcv_data):
        result = get_mom(small_ohlcv_data, 2, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "mom" in result.columns

    def test_talib_mom_missing_data(self, dataframe_with_nan):
        result = get_mom(dataframe_with_nan, 10, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "mom" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_mom_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_mom(empty_dataframe, 10, calculator_type="talib")


class TestTalibROC:
    def test_talib_roc_calculation(self, sample_ohlcv_data):
        result = get_roc(sample_ohlcv_data, 10, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "roc" in result.columns

    def test_talib_roc_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": np.arange(100, 120, 1.0),
                "high": np.arange(101, 121, 1.0),
                "low": np.arange(99, 119, 1.0),
                "close": np.arange(100, 120, 1.0),
                "volume": [1000000] * 20,
            }
        )
        result = get_roc(test_data, 10, calculator_type="talib")
        roc_values = result["roc"].dropna()
        assert len(roc_values) > 0

    def test_talib_roc_boundary_values(self, small_ohlcv_data):
        result = get_roc(small_ohlcv_data, 2, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "roc" in result.columns

    def test_talib_roc_missing_data(self, dataframe_with_nan):
        result = get_roc(dataframe_with_nan, 10, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "roc" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_roc_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_roc(empty_dataframe, 10, calculator_type="talib")


class TestTalibWILLR:
    def test_talib_willr_calculation(self, sample_ohlcv_data):
        result = get_willr(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "willr" in result.columns

    def test_talib_willr_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": np.arange(100, 130, 1.0),
                "high": np.arange(101, 131, 1.0),
                "low": np.arange(99, 129, 1.0),
                "close": np.arange(100, 130, 1.0),
                "volume": [1000000] * 30,
            }
        )
        result = get_willr(test_data, 14, calculator_type="talib")
        willr_values = result["willr"].dropna()
        assert all(-100 <= val <= 0 for val in willr_values)

    def test_talib_willr_boundary_values(self, small_ohlcv_data):
        result = get_willr(small_ohlcv_data, 2, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "willr" in result.columns

    def test_talib_willr_missing_data(self, dataframe_with_nan):
        result = get_willr(dataframe_with_nan, 14, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "willr" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_willr_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_willr(empty_dataframe, 14, calculator_type="talib")


class TestTalibADX:
    def test_talib_adx_calculation(self, sample_ohlcv_data):
        result = get_adx(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "adx" in result.columns

    def test_talib_adx_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": np.arange(100, 130, 1.0),
                "high": np.arange(101, 131, 1.0),
                "low": np.arange(99, 129, 1.0),
                "close": np.arange(100, 130, 1.0),
                "volume": [1000000] * 30,
            }
        )
        result = get_adx(test_data, 14, calculator_type="talib")
        adx_values = result["adx"].dropna()
        assert len(adx_values) > 0

    def test_talib_adx_boundary_values(self, small_ohlcv_data):
        result = get_adx(small_ohlcv_data, 2, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "adx" in result.columns

    def test_talib_adx_missing_data(self, dataframe_with_nan):
        result = get_adx(dataframe_with_nan, 14, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "adx" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_adx_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_adx(empty_dataframe, 14, calculator_type="talib")


class TestTalibCMO:
    def test_talib_cmo_calculation(self, sample_ohlcv_data):
        result = get_cmo(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "cmo" in result.columns

    def test_talib_cmo_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": np.arange(100, 130, 1.0),
                "high": np.arange(101, 131, 1.0),
                "low": np.arange(99, 129, 1.0),
                "close": np.arange(100, 130, 1.0),
                "volume": [1000000] * 30,
            }
        )
        result = get_cmo(test_data, 14, calculator_type="talib")
        cmo_values = result["cmo"].dropna()
        assert len(cmo_values) > 0

    def test_talib_cmo_boundary_values(self, small_ohlcv_data):
        result = get_cmo(small_ohlcv_data, 2, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "cmo" in result.columns

    def test_talib_cmo_missing_data(self, dataframe_with_nan):
        result = get_cmo(dataframe_with_nan, 14, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "cmo" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_cmo_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_cmo(empty_dataframe, 14, calculator_type="talib")


class TestTalibTRIX:
    def test_talib_trix_calculation(self, sample_ohlcv_data):
        result = get_trix(sample_ohlcv_data, 30, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "trix" in result.columns

    def test_talib_trix_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": np.arange(100, 150, 1.0),
                "high": np.arange(101, 151, 1.0),
                "low": np.arange(99, 149, 1.0),
                "close": np.arange(100, 150, 1.0),
                "volume": [1000000] * 50,
            }
        )
        result = get_trix(test_data, 30, calculator_type="talib")
        trix_values = result["trix"].dropna()
        assert len(trix_values) > 0

    def test_talib_trix_boundary_values(self, small_ohlcv_data):
        result = get_trix(small_ohlcv_data, 2, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "trix" in result.columns

    def test_talib_trix_missing_data(self, dataframe_with_nan):
        result = get_trix(dataframe_with_nan, 30, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "trix" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_trix_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_trix(empty_dataframe, 30, calculator_type="talib")


class TestTalibAD:
    def test_talib_ad_calculation(self, sample_ohlcv_data):
        result = get_ad(sample_ohlcv_data, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "ad" in result.columns

    def test_talib_ad_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": [10, 11, 12, 13, 14],
                "high": [11, 12, 13, 14, 15],
                "low": [9, 10, 11, 12, 13],
                "close": [10, 11, 12, 13, 14],
                "volume": [1000, 1100, 1200, 1300, 1400],
            }
        )
        result = get_ad(test_data, calculator_type="talib")
        ad_values = result["ad"]
        assert len(ad_values) == 5

    def test_talib_ad_boundary_values(self, small_ohlcv_data):
        result = get_ad(small_ohlcv_data, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "ad" in result.columns

    def test_talib_ad_missing_data(self, dataframe_with_nan):
        result = get_ad(dataframe_with_nan, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "ad" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_ad_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_ad(empty_dataframe, calculator_type="talib")


class TestTalibADOSC:
    def test_talib_adosc_calculation(self, sample_ohlcv_data):
        result = get_adosc(sample_ohlcv_data, 3, 10, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "adosc" in result.columns

    def test_talib_adosc_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": np.arange(100, 120, 1.0),
                "high": np.arange(101, 121, 1.0),
                "low": np.arange(99, 119, 1.0),
                "close": np.arange(100, 120, 1.0),
                "volume": np.arange(1000, 1200, 10),
            }
        )
        result = get_adosc(test_data, 3, 10, calculator_type="talib")
        adosc_values = result["adosc"].dropna()
        assert len(adosc_values) > 0

    def test_talib_adosc_boundary_values(self, small_ohlcv_data):
        result = get_adosc(small_ohlcv_data, 2, 3, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "adosc" in result.columns

    def test_talib_adosc_missing_data(self, dataframe_with_nan):
        result = get_adosc(dataframe_with_nan, 3, 10, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "adosc" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_adosc_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_adosc(empty_dataframe, 3, 10, calculator_type="talib")


class TestTalibSAR:
    def test_talib_sar_calculation(self, sample_ohlcv_data):
        result = get_sar(sample_ohlcv_data, 0.02, 0.2, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "sar" in result.columns

    def test_talib_sar_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": np.arange(100, 150, 1.0),
                "high": np.arange(101, 151, 1.0),
                "low": np.arange(99, 149, 1.0),
                "close": np.arange(100, 150, 1.0),
                "volume": [1000000] * 50,
            }
        )
        result = get_sar(test_data, 0.02, 0.2, calculator_type="talib")
        sar_values = result["sar"].dropna()
        assert len(sar_values) > 0

    def test_talib_sar_boundary_values(self, small_ohlcv_data):
        result = get_sar(small_ohlcv_data, 0.01, 0.1, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "sar" in result.columns

    def test_talib_sar_missing_data(self, dataframe_with_nan):
        result = get_sar(dataframe_with_nan, 0.02, 0.2, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "sar" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_sar_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_sar(empty_dataframe, 0.02, 0.2, calculator_type="talib")


class TestTalibTSF:
    def test_talib_tsf_calculation(self, sample_ohlcv_data):
        result = get_tsf(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "tsf" in result.columns

    def test_talib_tsf_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": np.arange(100, 130, 1.0),
                "high": np.arange(101, 131, 1.0),
                "low": np.arange(99, 129, 1.0),
                "close": np.arange(100, 130, 1.0),
                "volume": [1000000] * 30,
            }
        )
        result = get_tsf(test_data, 14, calculator_type="talib")
        tsf_values = result["tsf"].dropna()
        assert len(tsf_values) > 0

    def test_talib_tsf_boundary_values(self, small_ohlcv_data):
        result = get_tsf(small_ohlcv_data, 2, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "tsf" in result.columns

    def test_talib_tsf_missing_data(self, dataframe_with_nan):
        result = get_tsf(dataframe_with_nan, 14, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "tsf" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_tsf_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_tsf(empty_dataframe, 14, calculator_type="talib")


class TestTalibAPO:
    def test_talib_apo_calculation(self, sample_ohlcv_data):
        result = get_apo(sample_ohlcv_data, 12, 26, 0, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "apo" in result.columns

    def test_talib_apo_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": np.arange(100, 150, 1.0),
                "high": np.arange(101, 151, 1.0),
                "low": np.arange(99, 149, 1.0),
                "close": np.arange(100, 150, 1.0),
                "volume": [1000000] * 50,
            }
        )
        result = get_apo(test_data, 12, 26, 0, calculator_type="talib")
        apo_values = result["apo"].dropna()
        assert len(apo_values) > 0

    def test_talib_apo_boundary_values(self, small_ohlcv_data):
        result = get_apo(small_ohlcv_data, 2, 3, 0, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "apo" in result.columns

    def test_talib_apo_missing_data(self, dataframe_with_nan):
        result = get_apo(dataframe_with_nan, 12, 26, 0, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "apo" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_apo_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_apo(empty_dataframe, 12, 26, 0, calculator_type="talib")


class TestTalibAROON:
    def test_talib_aroon_calculation(self, sample_ohlcv_data):
        result = get_aroon(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "aroon_down" in result.columns
        assert "aroon_up" in result.columns

    def test_talib_aroon_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": np.arange(100, 130, 1.0),
                "high": np.arange(101, 131, 1.0),
                "low": np.arange(99, 129, 1.0),
                "close": np.arange(100, 130, 1.0),
                "volume": [1000000] * 30,
            }
        )
        result = get_aroon(test_data, 14, calculator_type="talib")
        aroon_up_values = result["aroon_up"].dropna()
        aroon_down_values = result["aroon_down"].dropna()
        assert len(aroon_up_values) > 0
        assert len(aroon_down_values) > 0

    def test_talib_aroon_boundary_values(self, small_ohlcv_data):
        result = get_aroon(small_ohlcv_data, 2, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "aroon_up" in result.columns

    def test_talib_aroon_missing_data(self, dataframe_with_nan):
        result = get_aroon(dataframe_with_nan, 14, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "aroon_up" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_aroon_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_aroon(empty_dataframe, 14, calculator_type="talib")


class TestTalibAROONOSC:
    def test_talib_aroonosc_calculation(self, sample_ohlcv_data):
        result = get_aroonosc(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "aroonosc" in result.columns

    def test_talib_aroonosc_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": np.arange(100, 130, 1.0),
                "high": np.arange(101, 131, 1.0),
                "low": np.arange(99, 129, 1.0),
                "close": np.arange(100, 130, 1.0),
                "volume": [1000000] * 30,
            }
        )
        result = get_aroonosc(test_data, 14, calculator_type="talib")
        aroonosc_values = result["aroonosc"].dropna()
        assert len(aroonosc_values) > 0

    def test_talib_aroonosc_boundary_values(self, small_ohlcv_data):
        result = get_aroonosc(small_ohlcv_data, 2, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "aroonosc" in result.columns

    def test_talib_aroonosc_missing_data(self, dataframe_with_nan):
        result = get_aroonosc(dataframe_with_nan, 14, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "aroonosc" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_aroonosc_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_aroonosc(empty_dataframe, 14, calculator_type="talib")


class TestTalibBOP:
    def test_talib_bop_calculation(self, sample_ohlcv_data):
        result = get_bop(sample_ohlcv_data, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "bop" in result.columns

    def test_talib_bop_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": [10, 11, 12, 13, 14],
                "high": [11, 12, 13, 14, 15],
                "low": [9, 10, 11, 12, 13],
                "close": [10, 11, 12, 13, 14],
                "volume": [1000, 1100, 1200, 1300, 1400],
            }
        )
        result = get_bop(test_data, calculator_type="talib")
        bop_values = result["bop"]
        assert len(bop_values) == 5

    def test_talib_bop_boundary_values(self, small_ohlcv_data):
        result = get_bop(small_ohlcv_data, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "bop" in result.columns

    def test_talib_bop_missing_data(self, dataframe_with_nan):
        result = get_bop(dataframe_with_nan, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "bop" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_bop_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_bop(empty_dataframe, calculator_type="talib")


class TestTalibDX:
    def test_talib_dx_calculation(self, sample_ohlcv_data):
        result = get_dx(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "dx" in result.columns

    def test_talib_dx_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": np.arange(100, 130, 1.0),
                "high": np.arange(101, 131, 1.0),
                "low": np.arange(99, 129, 1.0),
                "close": np.arange(100, 130, 1.0),
                "volume": [1000000] * 30,
            }
        )
        result = get_dx(test_data, 14, calculator_type="talib")
        dx_values = result["dx"].dropna()
        assert len(dx_values) > 0

    def test_talib_dx_boundary_values(self, small_ohlcv_data):
        result = get_dx(small_ohlcv_data, 2, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "dx" in result.columns

    def test_talib_dx_missing_data(self, dataframe_with_nan):
        result = get_dx(dataframe_with_nan, 14, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "dx" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_dx_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_dx(empty_dataframe, 14, calculator_type="talib")


class TestTalibMFI:
    def test_talib_mfi_calculation(self, sample_ohlcv_data):
        result = get_mfi(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "mfi" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_mfi_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": np.arange(100, 130, 1.0),
                "high": np.arange(101, 131, 1.0),
                "low": np.arange(99, 129, 1.0),
                "close": np.arange(100, 130, 1.0),
                "volume": np.arange(1000000, 1030000, 100),
            }
        )
        result = get_mfi(test_data, 14, calculator_type="talib")
        mfi_values = result["mfi"].dropna()
        assert len(mfi_values) > 0

    def test_talib_mfi_boundary_values(self, small_ohlcv_data):
        result = get_mfi(small_ohlcv_data, 2, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "mfi" in result.columns

    def test_talib_mfi_missing_data(self, dataframe_with_nan):
        result = get_mfi(dataframe_with_nan, 14, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "mfi" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_mfi_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_mfi(empty_dataframe, 14, calculator_type="talib")


class TestTalibMinusDI:
    def test_talib_minus_di_calculation(self, sample_ohlcv_data):
        result = get_minus_di(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "minus_di" in result.columns

    def test_talib_minus_di_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": np.arange(100, 130, 1.0),
                "high": np.arange(101, 131, 1.0),
                "low": np.arange(99, 129, 1.0),
                "close": np.arange(100, 130, 1.0),
                "volume": [1000000] * 30,
            }
        )
        result = get_minus_di(test_data, 14, calculator_type="talib")
        minus_di_values = result["minus_di"].dropna()
        assert len(minus_di_values) > 0

    def test_talib_minus_di_boundary_values(self, small_ohlcv_data):
        result = get_minus_di(small_ohlcv_data, 2, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "minus_di" in result.columns

    def test_talib_minus_di_missing_data(self, dataframe_with_nan):
        result = get_minus_di(dataframe_with_nan, 14, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "minus_di" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_minus_di_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_minus_di(empty_dataframe, 14, calculator_type="talib")


class TestTalibMinusDM:
    def test_talib_minus_dm_calculation(self, sample_ohlcv_data):
        result = get_minus_dm(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "minus_dm" in result.columns

    def test_talib_minus_dm_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": np.arange(100, 130, 1.0),
                "high": np.arange(101, 131, 1.0),
                "low": np.arange(99, 129, 1.0),
                "close": np.arange(100, 130, 1.0),
                "volume": [1000000] * 30,
            }
        )
        result = get_minus_dm(test_data, 14, calculator_type="talib")
        minus_dm_values = result["minus_dm"].dropna()
        assert len(minus_dm_values) > 0

    def test_talib_minus_dm_boundary_values(self, small_ohlcv_data):
        result = get_minus_dm(small_ohlcv_data, 2, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "minus_dm" in result.columns

    def test_talib_minus_dm_missing_data(self, dataframe_with_nan):
        result = get_minus_dm(dataframe_with_nan, 14, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "minus_dm" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_minus_dm_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_minus_dm(empty_dataframe, 14, calculator_type="talib")


class TestTalibPlusDI:
    def test_talib_plus_di_calculation(self, sample_ohlcv_data):
        result = get_plus_di(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "plus_di" in result.columns

    def test_talib_plus_di_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": np.arange(100, 130, 1.0),
                "high": np.arange(101, 131, 1.0),
                "low": np.arange(99, 129, 1.0),
                "close": np.arange(100, 130, 1.0),
                "volume": [1000000] * 30,
            }
        )
        result = get_plus_di(test_data, 14, calculator_type="talib")
        plus_di_values = result["plus_di"].dropna()
        assert len(plus_di_values) > 0

    def test_talib_plus_di_boundary_values(self, small_ohlcv_data):
        result = get_plus_di(small_ohlcv_data, 2, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "plus_di" in result.columns

    def test_talib_plus_di_missing_data(self, dataframe_with_nan):
        result = get_plus_di(dataframe_with_nan, 14, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "plus_di" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_plus_di_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_plus_di(empty_dataframe, 14, calculator_type="talib")


class TestTalibPlusDM:
    def test_talib_plus_dm_calculation(self, sample_ohlcv_data):
        result = get_plus_dm(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "plus_dm" in result.columns

    def test_talib_plus_dm_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": np.arange(100, 130, 1.0),
                "high": np.arange(101, 131, 1.0),
                "low": np.arange(99, 129, 1.0),
                "close": np.arange(100, 130, 1.0),
                "volume": [1000000] * 30,
            }
        )
        result = get_plus_dm(test_data, 14, calculator_type="talib")
        plus_dm_values = result["plus_dm"].dropna()
        assert len(plus_dm_values) > 0

    def test_talib_plus_dm_boundary_values(self, small_ohlcv_data):
        result = get_plus_dm(small_ohlcv_data, 2, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "plus_dm" in result.columns

    def test_talib_plus_dm_missing_data(self, dataframe_with_nan):
        result = get_plus_dm(dataframe_with_nan, 14, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "plus_dm" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_plus_dm_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_plus_dm(empty_dataframe, 14, calculator_type="talib")


class TestTalibPPO:
    def test_talib_ppo_calculation(self, sample_ohlcv_data):
        result = get_ppo(sample_ohlcv_data, 12, 26, 0, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "ppo" in result.columns

    def test_talib_ppo_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": np.arange(100, 150, 1.0),
                "high": np.arange(101, 151, 1.0),
                "low": np.arange(99, 149, 1.0),
                "close": np.arange(100, 150, 1.0),
                "volume": [1000000] * 50,
            }
        )
        result = get_ppo(test_data, 12, 26, 0, calculator_type="talib")
        ppo_values = result["ppo"].dropna()
        assert len(ppo_values) > 0

    def test_talib_ppo_boundary_values(self, small_ohlcv_data):
        result = get_ppo(small_ohlcv_data, 2, 3, 0, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "ppo" in result.columns

    def test_talib_ppo_missing_data(self, dataframe_with_nan):
        result = get_ppo(dataframe_with_nan, 12, 26, 0, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "ppo" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_ppo_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_ppo(empty_dataframe, 12, 26, 0, calculator_type="talib")


class TestTalibROCP:
    def test_talib_rocp_calculation(self, sample_ohlcv_data):
        result = get_rocp(sample_ohlcv_data, 10, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "rocp" in result.columns

    def test_talib_rocp_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": np.arange(100, 120, 1.0),
                "high": np.arange(101, 121, 1.0),
                "low": np.arange(99, 119, 1.0),
                "close": np.arange(100, 120, 1.0),
                "volume": [1000000] * 20,
            }
        )
        result = get_rocp(test_data, 10, calculator_type="talib")
        rocp_values = result["rocp"].dropna()
        assert len(rocp_values) > 0

    def test_talib_rocp_boundary_values(self, small_ohlcv_data):
        result = get_rocp(small_ohlcv_data, 2, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "rocp" in result.columns

    def test_talib_rocp_missing_data(self, dataframe_with_nan):
        result = get_rocp(dataframe_with_nan, 10, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "rocp" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_rocp_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_rocp(empty_dataframe, 10, calculator_type="talib")


class TestTalibROCR:
    def test_talib_rocr_calculation(self, sample_ohlcv_data):
        result = get_rocr(sample_ohlcv_data, 10, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "rocr" in result.columns

    def test_talib_rocr_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": np.arange(100, 120, 1.0),
                "high": np.arange(101, 121, 1.0),
                "low": np.arange(99, 119, 1.0),
                "close": np.arange(100, 120, 1.0),
                "volume": [1000000] * 20,
            }
        )
        result = get_rocr(test_data, 10, calculator_type="talib")
        rocr_values = result["rocr"].dropna()
        assert len(rocr_values) > 0

    def test_talib_rocr_boundary_values(self, small_ohlcv_data):
        result = get_rocr(small_ohlcv_data, 2, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "rocr" in result.columns

    def test_talib_rocr_missing_data(self, dataframe_with_nan):
        result = get_rocr(dataframe_with_nan, 10, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "rocr" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_rocr_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_rocr(empty_dataframe, 10, calculator_type="talib")


class TestTalibROCR100:
    def test_talib_rocr100_calculation(self, sample_ohlcv_data):
        result = get_rocr100(sample_ohlcv_data, 10, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "rocr100" in result.columns

    def test_talib_rocr100_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": np.arange(100, 120, 1.0),
                "high": np.arange(101, 121, 1.0),
                "low": np.arange(99, 119, 1.0),
                "close": np.arange(100, 120, 1.0),
                "volume": [1000000] * 20,
            }
        )
        result = get_rocr100(test_data, 10, calculator_type="talib")
        rocr100_values = result["rocr100"].dropna()
        assert len(rocr100_values) > 0

    def test_talib_rocr100_boundary_values(self, small_ohlcv_data):
        result = get_rocr100(small_ohlcv_data, 2, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "rocr100" in result.columns

    def test_talib_rocr100_missing_data(self, dataframe_with_nan):
        result = get_rocr100(dataframe_with_nan, 10, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "rocr100" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_rocr100_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_rocr100(empty_dataframe, 10, calculator_type="talib")


class TestTalibULTOSC:
    def test_talib_ultosc_calculation(self, sample_ohlcv_data):
        result = get_ultosc(sample_ohlcv_data, 7, 14, 28, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "ultosc" in result.columns

    def test_talib_ultosc_with_known_values(self):
        test_data = pd.DataFrame(
            {
                "open": np.arange(100, 150, 1.0),
                "high": np.arange(101, 151, 1.0),
                "low": np.arange(99, 149, 1.0),
                "close": np.arange(100, 150, 1.0),
                "volume": [1000000] * 50,
            }
        )
        result = get_ultosc(test_data, 7, 14, 28, calculator_type="talib")
        ultosc_values = result["ultosc"].dropna()
        assert len(ultosc_values) > 0

    def test_talib_ultosc_boundary_values(self, small_ohlcv_data):
        result = get_ultosc(small_ohlcv_data, 2, 3, 4, calculator_type="talib")
        assert len(result) == len(small_ohlcv_data)
        assert "ultosc" in result.columns

    def test_talib_ultosc_missing_data(self, dataframe_with_nan):
        result = get_ultosc(dataframe_with_nan, 7, 14, 28, calculator_type="talib")
        assert len(result) == len(dataframe_with_nan)
        assert "ultosc" in result.columns

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_ultosc_empty_dataframe(self, empty_dataframe):
        with pytest.raises((KeyError, IndexError, ValueError)):
            get_ultosc(empty_dataframe, 7, 14, 28, calculator_type="talib")


class TestTalibModuleImport:
    """测试 talib 模块的导入和基础结构"""

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_module_can_be_imported(self):
        """测试模块可以被导入（需要 TA-Lib）"""
        from akshare_one.modules.indicators.talib import TalibIndicatorCalculator

        assert TalibIndicatorCalculator is not None

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_ma_type_mapping_exists(self):
        """测试 MA_TYPE_MAPPING 存在（需要 TA-Lib）"""
        from akshare_one.modules.indicators.talib import MA_TYPE_MAPPING

        assert isinstance(MA_TYPE_MAPPING, dict)
        assert len(MA_TYPE_MAPPING) > 0

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_indicator_calculator_is_subclass(self):
        """测试 TalibIndicatorCalculator 是 BaseIndicatorCalculator 的子类（需要 TA-Lib）"""
        from akshare_one.modules.indicators.talib import TalibIndicatorCalculator
        from akshare_one.modules.indicators.base import BaseIndicatorCalculator

        assert issubclass(TalibIndicatorCalculator, BaseIndicatorCalculator)

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_indicator_calculator_has_all_methods(self):
        """测试 TalibIndicatorCalculator 包含所有必要的方法（需要 TA-Lib）"""
        from akshare_one.modules.indicators.talib import TalibIndicatorCalculator

        calculator = TalibIndicatorCalculator

        required_methods = [
            "calculate_sma",
            "calculate_ema",
            "calculate_rsi",
            "calculate_macd",
            "calculate_bollinger_bands",
            "calculate_stoch",
            "calculate_atr",
            "calculate_cci",
            "calculate_adx",
            "calculate_willr",
            "calculate_ad",
            "calculate_adosc",
            "calculate_obv",
            "calculate_mom",
            "calculate_sar",
            "calculate_tsf",
            "calculate_apo",
            "calculate_aroon",
            "calculate_aroonosc",
            "calculate_bop",
            "calculate_cmo",
            "calculate_dx",
            "calculate_mfi",
            "calculate_minus_di",
            "calculate_minus_dm",
            "calculate_plus_di",
            "calculate_plus_dm",
            "calculate_ppo",
            "calculate_roc",
            "calculate_rocp",
            "calculate_rocr",
            "calculate_rocr100",
            "calculate_trix",
            "calculate_ultosc",
        ]

        for method_name in required_methods:
            assert hasattr(calculator, method_name), f"Missing method: {method_name}"
            assert callable(getattr(calculator, method_name)), f"Method {method_name} is not callable"

    @pytest.mark.skipif(not TALIB_AVAILABLE, reason="TA-Lib not installed")
    def test_talib_indicator_calculator_method_signatures(self):
        """测试方法的签名符合预期（需要 TA-Lib）"""
        from akshare_one.modules.indicators.talib import TalibIndicatorCalculator
        import inspect

        calculator = TalibIndicatorCalculator

        sma_sig = inspect.signature(calculator.calculate_sma)
        assert "df" in sma_sig.parameters
        assert "window" in sma_sig.parameters

        macd_sig = inspect.signature(calculator.calculate_macd)
        assert "df" in macd_sig.parameters
        assert "fast" in macd_sig.parameters
        assert "slow" in macd_sig.parameters
        assert "signal" in macd_sig.parameters

    def test_indicator_factory_exists_without_talib(self):
        """测试 IndicatorFactory 存在（不需要 TA-Lib）"""
        from akshare_one.modules.indicators import IndicatorFactory

        assert IndicatorFactory is not None

    def test_simple_calculator_available_without_talib(self):
        """测试 SimpleCalculator 可用（不需要 TA-Lib）"""
        from akshare_one.modules.indicators import SimpleIndicatorCalculator

        assert SimpleIndicatorCalculator is not None

    def test_talib_available_flag_exists(self):
        """测试 TALIB_AVAILABLE 标记存在"""
        from akshare_one.modules.indicators import TALIB_AVAILABLE

        assert isinstance(TALIB_AVAILABLE, bool)

    def test_base_calculator_available_without_talib(self):
        """测试 BaseIndicatorCalculator 可用（不需要 TA-Lib）"""
        from akshare_one.modules.indicators import BaseIndicatorCalculator

        assert BaseIndicatorCalculator is not None


class TestTalibFallbackBehavior:
    """测试 TA-Lib 未安装时的 fallback 行为"""

    def test_talib_unavailable_marker(self):
        """测试 TALIB_AVAILABLE 标记"""
        from akshare_one.modules.indicators import TALIB_AVAILABLE

        assert isinstance(TALIB_AVAILABLE, bool)

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_to_simple_when_talib_not_available(self, sample_ohlcv_data):
        """当 TA-Lib 不可用时，自动 fallback 到 simple 实现"""
        result = get_sma(sample_ohlcv_data, 20, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "sma" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_macd_when_talib_not_available(self, sample_ohlcv_data):
        """测试 MACD fallback"""
        result = get_macd(sample_ohlcv_data, 12, 26, 9, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "macd" in result.columns
        assert "signal" in result.columns
        assert "histogram" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_rsi_when_talib_not_available(self, sample_ohlcv_data):
        """测试 RSI fallback"""
        result = get_rsi(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "rsi" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_boll_when_talib_not_available(self, sample_ohlcv_data):
        """测试 BOLL fallback"""
        result = get_bollinger_bands(sample_ohlcv_data, 20, 2, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "upper_band" in result.columns
        assert "middle_band" in result.columns
        assert "lower_band" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_stoch_when_talib_not_available(self, sample_ohlcv_data):
        """测试 STOCH (KDJ) fallback"""
        result = get_stoch(sample_ohlcv_data, 9, 3, 3, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "slow_k" in result.columns
        assert "slow_d" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_atr_when_talib_not_available(self, sample_ohlcv_data):
        """测试 ATR fallback"""
        result = get_atr(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "atr" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_cci_when_talib_not_available(self, sample_ohlcv_data):
        """测试 CCI fallback"""
        result = get_cci(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "cci" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_obv_when_talib_not_available(self, sample_ohlcv_data):
        """测试 OBV fallback"""
        result = get_obv(sample_ohlcv_data, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "obv" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_mom_when_talib_not_available(self, sample_ohlcv_data):
        """测试 MOM fallback"""
        result = get_mom(sample_ohlcv_data, 10, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "mom" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_roc_when_talib_not_available(self, sample_ohlcv_data):
        """测试 ROC fallback"""
        result = get_roc(sample_ohlcv_data, 10, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "roc" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_willr_when_talib_not_available(self, sample_ohlcv_data):
        """测试 WILLR fallback"""
        result = get_willr(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "willr" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_adx_when_talib_not_available(self, sample_ohlcv_data):
        """测试 ADX fallback"""
        result = get_adx(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "adx" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_cmo_when_talib_not_available(self, sample_ohlcv_data):
        """测试 CMO fallback"""
        result = get_cmo(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "cmo" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_trix_when_talib_not_available(self, sample_ohlcv_data):
        """测试 TRIX fallback"""
        result = get_trix(sample_ohlcv_data, 30, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "trix" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_ema_when_talib_not_available(self, sample_ohlcv_data):
        """测试 EMA fallback"""
        result = get_ema(sample_ohlcv_data, 20, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "ema" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_ad_when_talib_not_available(self, sample_ohlcv_data):
        """测试 AD fallback"""
        result = get_ad(sample_ohlcv_data, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "ad" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_adosc_when_talib_not_available(self, sample_ohlcv_data):
        """测试 ADOSC fallback"""
        result = get_adosc(sample_ohlcv_data, 3, 10, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "adosc" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_sar_when_talib_not_available(self, sample_ohlcv_data):
        """测试 SAR fallback"""
        result = get_sar(sample_ohlcv_data, 0.02, 0.2, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "sar" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_tsf_when_talib_not_available(self, sample_ohlcv_data):
        """测试 TSF fallback"""
        result = get_tsf(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "tsf" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_apo_when_talib_not_available(self, sample_ohlcv_data):
        """测试 APO fallback"""
        result = get_apo(sample_ohlcv_data, 12, 26, 0, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "apo" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_aroon_when_talib_not_available(self, sample_ohlcv_data):
        """测试 AROON fallback"""
        result = get_aroon(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "aroon_up" in result.columns
        assert "aroon_down" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_aroonosc_when_talib_not_available(self, sample_ohlcv_data):
        """测试 AROONOSC fallback"""
        result = get_aroonosc(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "aroonosc" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_bop_when_talib_not_available(self, sample_ohlcv_data):
        """测试 BOP fallback"""
        result = get_bop(sample_ohlcv_data, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "bop" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_dx_when_talib_not_available(self, sample_ohlcv_data):
        """测试 DX fallback"""
        result = get_dx(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "dx" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_mfi_when_talib_not_available(self, sample_ohlcv_data):
        """测试 MFI fallback"""
        result = get_mfi(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "mfi" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_minus_di_when_talib_not_available(self, sample_ohlcv_data):
        """测试 MINUS_DI fallback"""
        result = get_minus_di(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "minus_di" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_minus_dm_when_talib_not_available(self, sample_ohlcv_data):
        """测试 MINUS_DM fallback"""
        result = get_minus_dm(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "minus_dm" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_plus_di_when_talib_not_available(self, sample_ohlcv_data):
        """测试 PLUS_DI fallback"""
        result = get_plus_di(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "plus_di" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_plus_dm_when_talib_not_available(self, sample_ohlcv_data):
        """测试 PLUS_DM fallback"""
        result = get_plus_dm(sample_ohlcv_data, 14, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "plus_dm" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_ppo_when_talib_not_available(self, sample_ohlcv_data):
        """测试 PPO fallback"""
        result = get_ppo(sample_ohlcv_data, 12, 26, 0, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "ppo" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_rocp_when_talib_not_available(self, sample_ohlcv_data):
        """测试 ROCP fallback"""
        result = get_rocp(sample_ohlcv_data, 10, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "rocp" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_rocr_when_talib_not_available(self, sample_ohlcv_data):
        """测试 ROCR fallback"""
        result = get_rocr(sample_ohlcv_data, 10, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "rocr" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_rocr100_when_talib_not_available(self, sample_ohlcv_data):
        """测试 ROCR100 fallback"""
        result = get_rocr100(sample_ohlcv_data, 10, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "rocr100" in result.columns

    @pytest.mark.skipif(TALIB_AVAILABLE, reason="This test requires TA-Lib to be unavailable")
    def test_fallback_ultosc_when_talib_not_available(self, sample_ohlcv_data):
        """测试 ULTOSC fallback"""
        result = get_ultosc(sample_ohlcv_data, 7, 14, 28, calculator_type="talib")
        assert len(result) == len(sample_ohlcv_data)
        assert "ultosc" in result.columns
