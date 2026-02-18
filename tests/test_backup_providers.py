"""
Unit tests for backup data providers (新增备用数据源测试).

This test module covers the newly added backup providers:
- blockdeal: sina
- disclosure: sina
- esg: sina
- fundflow: sina
- goodwill: sina
- futures: eastmoney
- insider: eastmoney
- lhb: sina
- limitup: sina
- margin: sina
- northbound: sina
- options: eastmoney
- pledge: sina
- macro: sina
"""


from akshare_one.modules.blockdeal.factory import BlockDealFactory
from akshare_one.modules.blockdeal.sina import SinaBlockDealProvider
from akshare_one.modules.disclosure.factory import DisclosureFactory
from akshare_one.modules.disclosure.sina import SinaDisclosureProvider
from akshare_one.modules.esg.factory import ESGFactory
from akshare_one.modules.esg.sina import SinaESGProvider
from akshare_one.modules.fundflow.factory import FundFlowFactory
from akshare_one.modules.fundflow.sina import SinaFundFlowProvider
from akshare_one.modules.futures.eastmoney import (
    EastmoneyFuturesHistoricalProvider,
    EastmoneyFuturesRealtimeProvider,
)
from akshare_one.modules.futures.factory import FuturesDataFactory
from akshare_one.modules.goodwill.factory import GoodwillFactory
from akshare_one.modules.goodwill.sina import SinaGoodwillProvider
from akshare_one.modules.insider.eastmoney import EastmoneyInsiderProvider
from akshare_one.modules.insider.factory import InsiderDataFactory
from akshare_one.modules.lhb.factory import DragonTigerFactory
from akshare_one.modules.lhb.sina import SinaLHBProvider
from akshare_one.modules.limitup.factory import LimitUpDownFactory
from akshare_one.modules.limitup.sina import SinaLimitUpDownProvider
from akshare_one.modules.macro.factory import MacroFactory
from akshare_one.modules.macro.sina import SinaMacroProvider
from akshare_one.modules.margin.factory import MarginFactory
from akshare_one.modules.margin.sina import SinaMarginProvider
from akshare_one.modules.northbound.factory import NorthboundFactory
from akshare_one.modules.northbound.sina import SinaNorthboundProvider
from akshare_one.modules.options.eastmoney import EastmoneyOptionsProvider
from akshare_one.modules.options.factory import OptionsDataFactory
from akshare_one.modules.pledge.factory import EquityPledgeFactory
from akshare_one.modules.pledge.sina import SinaEquityPledgeProvider


class TestBlockDealSinaProvider:
    """Test Sina block deal provider."""

    def test_factory_registration(self):
        """Test that sina provider is registered."""
        provider = BlockDealFactory.get_provider('sina')
        assert isinstance(provider, SinaBlockDealProvider)

    def test_provider_metadata(self):
        """Test provider metadata."""
        provider = SinaBlockDealProvider()
        assert provider.get_source_name() == 'sina'
        assert provider.get_data_type() == 'blockdeal'


class TestDisclosureSinaProvider:
    """Test Sina disclosure provider."""

    def test_factory_registration(self):
        """Test that sina provider is registered."""
        provider = DisclosureFactory.get_provider('sina')
        assert isinstance(provider, SinaDisclosureProvider)

    def test_provider_metadata(self):
        """Test provider metadata."""
        provider = SinaDisclosureProvider()
        assert provider.get_source_name() == 'sina'
        assert provider.get_data_type() == 'disclosure'


class TestESGSinaProvider:
    """Test Sina ESG provider."""

    def test_factory_registration(self):
        """Test that sina provider is registered."""
        provider = ESGFactory.get_provider('sina')
        assert isinstance(provider, SinaESGProvider)

    def test_provider_metadata(self):
        """Test provider metadata."""
        provider = SinaESGProvider()
        assert provider.get_source_name() == 'sina'
        assert provider.get_data_type() == 'esg'


class TestFundflowSinaProvider:
    """Test Sina fundflow provider."""

    def test_factory_registration(self):
        """Test that sina provider is registered."""
        provider = FundFlowFactory.get_provider('sina')
        assert isinstance(provider, SinaFundFlowProvider)

    def test_provider_metadata(self):
        """Test provider metadata."""
        provider = SinaFundFlowProvider()
        assert provider.get_source_name() == 'sina'
        assert provider.get_data_type() == 'fundflow'


class TestGoodwillSinaProvider:
    """Test Sina goodwill provider."""

    def test_factory_registration(self):
        """Test that sina provider is registered."""
        provider = GoodwillFactory.get_provider('sina')
        assert isinstance(provider, SinaGoodwillProvider)

    def test_provider_metadata(self):
        """Test provider metadata."""
        provider = SinaGoodwillProvider()
        assert provider.get_source_name() == 'sina'
        assert provider.get_data_type() == 'goodwill'


class TestFuturesEastmoneyProvider:
    """Test Eastmoney futures provider."""

    def test_factory_registration_historical(self):
        """Test that eastmoney historical provider is registered."""
        provider = FuturesDataFactory.get_historical_provider('eastmoney', symbol='CU')
        assert isinstance(provider, EastmoneyFuturesHistoricalProvider)

    def test_factory_registration_realtime(self):
        """Test that eastmoney realtime provider is registered."""
        provider = FuturesDataFactory.get_realtime_provider('eastmoney', symbol='CU')
        assert isinstance(provider, EastmoneyFuturesRealtimeProvider)

    def test_historical_provider_metadata(self):
        """Test historical provider metadata."""
        provider = EastmoneyFuturesHistoricalProvider(symbol='CU')
        assert provider.get_source_name() == 'eastmoney'

    def test_realtime_provider_metadata(self):
        """Test realtime provider metadata."""
        provider = EastmoneyFuturesRealtimeProvider(symbol='CU')
        assert provider.get_source_name() == 'eastmoney'


class TestInsiderEastmoneyProvider:
    """Test Eastmoney insider provider."""

    def test_factory_registration(self):
        """Test that eastmoney provider is registered."""
        provider = InsiderDataFactory.get_provider('eastmoney', symbol='600000')
        assert isinstance(provider, EastmoneyInsiderProvider)

    def test_provider_metadata(self):
        """Test provider metadata."""
        provider = EastmoneyInsiderProvider(symbol='600000')
        assert provider.get_source_name() == 'eastmoney'


class TestLHBSinaProvider:
    """Test Sina LHB provider."""

    def test_factory_registration(self):
        """Test that sina provider is registered."""
        provider = DragonTigerFactory.get_provider('sina')
        assert isinstance(provider, SinaLHBProvider)

    def test_provider_metadata(self):
        """Test provider metadata."""
        provider = SinaLHBProvider()
        assert provider.get_source_name() == 'sina'
        assert provider.get_data_type() == 'lhb'


class TestLimitUpSinaProvider:
    """Test Sina limit up/down provider."""

    def test_factory_registration(self):
        """Test that sina provider is registered."""
        provider = LimitUpDownFactory.get_provider('sina')
        assert isinstance(provider, SinaLimitUpDownProvider)

    def test_provider_metadata(self):
        """Test provider metadata."""
        provider = SinaLimitUpDownProvider()
        assert provider.get_source_name() == 'sina'
        assert provider.get_data_type() == 'limitup'


class TestMarginSinaProvider:
    """Test Sina margin provider."""

    def test_factory_registration(self):
        """Test that sina provider is registered."""
        provider = MarginFactory.get_provider('sina')
        assert isinstance(provider, SinaMarginProvider)

    def test_provider_metadata(self):
        """Test provider metadata."""
        provider = SinaMarginProvider()
        assert provider.get_source_name() == 'sina'
        assert provider.get_data_type() == 'margin'


class TestNorthboundSinaProvider:
    """Test Sina northbound provider."""

    def test_factory_registration(self):
        """Test that sina provider is registered."""
        provider = NorthboundFactory.get_provider('sina')
        assert isinstance(provider, SinaNorthboundProvider)

    def test_provider_metadata(self):
        """Test provider metadata."""
        provider = SinaNorthboundProvider()
        assert provider.get_source_name() == 'sina'
        assert provider.get_data_type() == 'northbound'


class TestOptionsEastmoneyProvider:
    """Test Eastmoney options provider."""

    def test_factory_registration(self):
        """Test that eastmoney provider is registered."""
        provider = OptionsDataFactory.get_provider('eastmoney', underlying_symbol='510300')
        assert isinstance(provider, EastmoneyOptionsProvider)

    def test_provider_metadata(self):
        """Test provider metadata."""
        provider = EastmoneyOptionsProvider(underlying_symbol='510300')
        assert provider.get_source_name() == 'eastmoney'


class TestPledgeSinaProvider:
    """Test Sina pledge provider."""

    def test_factory_registration(self):
        """Test that sina provider is registered."""
        provider = EquityPledgeFactory.get_provider('sina')
        assert isinstance(provider, SinaEquityPledgeProvider)

    def test_provider_metadata(self):
        """Test provider metadata."""
        provider = SinaEquityPledgeProvider()
        assert provider.get_source_name() == 'sina'
        assert provider.get_data_type() == 'pledge'


class TestMacroSinaProvider:
    """Test Sina macro provider."""

    def test_factory_registration(self):
        """Test that sina provider is registered."""
        provider = MacroFactory.get_provider('sina')
        assert isinstance(provider, SinaMacroProvider)

    def test_provider_metadata(self):
        """Test provider metadata."""
        provider = SinaMacroProvider()
        assert provider.get_source_name() == 'sina'
        assert provider.get_data_type() == 'macro'


class TestMultipleSourcesAvailable:
    """Test that multiple sources are now available for each module."""

    def test_blockdeal_multiple_sources(self):
        """Test block deal has multiple sources."""
        sources = BlockDealFactory.list_sources()
        assert len(sources) >= 2
        assert 'eastmoney' in sources
        assert 'sina' in sources

    def test_disclosure_multiple_sources(self):
        """Test disclosure has multiple sources."""
        sources = DisclosureFactory.get_available_sources()
        assert len(sources) >= 2
        assert 'eastmoney' in sources
        assert 'sina' in sources

    def test_esg_multiple_sources(self):
        """Test ESG has multiple sources."""
        sources = ESGFactory.list_sources()
        assert len(sources) >= 2
        assert 'eastmoney' in sources
        assert 'sina' in sources

    def test_fundflow_multiple_sources(self):
        """Test fundflow has multiple sources."""
        sources = FundFlowFactory.list_sources()
        assert len(sources) >= 2
        assert 'eastmoney' in sources
        assert 'sina' in sources

    def test_goodwill_multiple_sources(self):
        """Test goodwill has multiple sources."""
        sources = GoodwillFactory.list_sources()
        assert len(sources) >= 2
        assert 'eastmoney' in sources
        assert 'sina' in sources

    def test_futures_multiple_sources(self):
        """Test futures has multiple sources."""
        assert 'eastmoney' in FuturesDataFactory._historical_providers
        assert 'sina' in FuturesDataFactory._historical_providers

    def test_insider_multiple_sources(self):
        """Test insider has multiple sources."""
        assert 'eastmoney' in InsiderDataFactory._providers
        assert 'xueqiu' in InsiderDataFactory._providers

    def test_lhb_multiple_sources(self):
        """Test LHB has multiple sources."""
        sources = DragonTigerFactory.list_sources()
        assert len(sources) >= 2
        assert 'eastmoney' in sources
        assert 'sina' in sources

    def test_limitup_multiple_sources(self):
        """Test limitup has multiple sources."""
        sources = LimitUpDownFactory.list_sources()
        assert len(sources) >= 2
        assert 'eastmoney' in sources
        assert 'sina' in sources

    def test_margin_multiple_sources(self):
        """Test margin has multiple sources."""
        sources = MarginFactory.list_sources()
        assert len(sources) >= 2
        assert 'eastmoney' in sources
        assert 'sina' in sources

    def test_northbound_multiple_sources(self):
        """Test northbound has multiple sources."""
        sources = NorthboundFactory.list_sources()
        assert len(sources) >= 2
        assert 'eastmoney' in sources
        assert 'sina' in sources

    def test_options_multiple_sources(self):
        """Test options has multiple sources."""
        assert 'eastmoney' in OptionsDataFactory._providers
        assert 'sina' in OptionsDataFactory._providers

    def test_pledge_multiple_sources(self):
        """Test pledge has multiple sources."""
        sources = EquityPledgeFactory.list_sources()
        assert len(sources) >= 2
        assert 'eastmoney' in sources
        assert 'sina' in sources

    def test_macro_multiple_sources(self):
        """Test macro has multiple sources."""
        sources = MacroFactory.list_sources()
        assert len(sources) >= 2
        assert 'official' in sources
        assert 'sina' in sources
