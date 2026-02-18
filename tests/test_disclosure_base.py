"""
Unit tests for DisclosureProvider base class.

Tests the data standardization methods specific to disclosure data.
"""

from src.akshare_one.modules.disclosure.base import DisclosureProvider


class TestDisclosureProviderStandardization:
    """Test data standardization methods in DisclosureProvider."""
    
    def test_standardize_category_chinese(self):
        """Test category standardization with Chinese input."""
        assert DisclosureProvider.standardize_category('分红') == 'dividend'
        assert DisclosureProvider.standardize_category('派息') == 'dividend'
        assert DisclosureProvider.standardize_category('红利') == 'dividend'
        assert DisclosureProvider.standardize_category('回购') == 'repurchase'
        assert DisclosureProvider.standardize_category('股份回购') == 'repurchase'
        assert DisclosureProvider.standardize_category('退市') == 'st'
        assert DisclosureProvider.standardize_category('风险') == 'st'
        assert DisclosureProvider.standardize_category('重大事项') == 'major_event'
        assert DisclosureProvider.standardize_category('重大公告') == 'major_event'
        assert DisclosureProvider.standardize_category('全部') == 'all'
    
    def test_standardize_category_english(self):
        """Test category standardization with English input."""
        assert DisclosureProvider.standardize_category('dividend') == 'dividend'
        assert DisclosureProvider.standardize_category('repurchase') == 'repurchase'
        assert DisclosureProvider.standardize_category('buyback') == 'repurchase'
        assert DisclosureProvider.standardize_category('st') == 'st'
        assert DisclosureProvider.standardize_category('delist') == 'st'
        assert DisclosureProvider.standardize_category('major') == 'major_event'
        assert DisclosureProvider.standardize_category('all') == 'all'
    
    def test_standardize_category_case_insensitive(self):
        """Test category standardization is case-insensitive."""
        assert DisclosureProvider.standardize_category('DIVIDEND') == 'dividend'
        assert DisclosureProvider.standardize_category('Repurchase') == 'repurchase'
        assert DisclosureProvider.standardize_category('ST') == 'st'
        assert DisclosureProvider.standardize_category('ALL') == 'all'
    
    def test_standardize_category_with_whitespace(self):
        """Test category standardization handles whitespace."""
        assert DisclosureProvider.standardize_category('  dividend  ') == 'dividend'
        assert DisclosureProvider.standardize_category('\tdividend\n') == 'dividend'
    
    def test_standardize_category_unknown(self):
        """Test category standardization with unknown input."""
        assert DisclosureProvider.standardize_category('unknown') == 'all'
        assert DisclosureProvider.standardize_category('xyz') == 'all'
        assert DisclosureProvider.standardize_category('') == 'all'
    
    def test_standardize_dividend_ratio_valid(self):
        """Test dividend ratio calculation with valid inputs."""
        # 1 yuan dividend, 10 yuan price = 10% yield
        assert DisclosureProvider.standardize_dividend_ratio(1.0, 10.0) == 10.0
        
        # 0.5 yuan dividend, 20 yuan price = 2.5% yield
        assert DisclosureProvider.standardize_dividend_ratio(0.5, 20.0) == 2.5
        
        # 2 yuan dividend, 50 yuan price = 4% yield
        assert DisclosureProvider.standardize_dividend_ratio(2.0, 50.0) == 4.0
    
    def test_standardize_dividend_ratio_none_inputs(self):
        """Test dividend ratio calculation with None inputs."""
        assert DisclosureProvider.standardize_dividend_ratio(None, 10.0) is None
        assert DisclosureProvider.standardize_dividend_ratio(1.0, None) is None
        assert DisclosureProvider.standardize_dividend_ratio(None, None) is None
    
    def test_standardize_dividend_ratio_zero_price(self):
        """Test dividend ratio calculation with zero price."""
        assert DisclosureProvider.standardize_dividend_ratio(1.0, 0.0) is None
    
    def test_standardize_dividend_ratio_precision(self):
        """Test dividend ratio calculation precision (4 decimal places)."""
        # 1/3 = 0.3333...
        result = DisclosureProvider.standardize_dividend_ratio(1.0, 300.0)
        assert result == 0.3333
    
    def test_standardize_repurchase_progress_chinese(self):
        """Test repurchase progress standardization with Chinese input."""
        assert DisclosureProvider.standardize_repurchase_progress('计划回购') == 'planned'
        assert DisclosureProvider.standardize_repurchase_progress('拟回购') == 'planned'
        assert DisclosureProvider.standardize_repurchase_progress('正在进行') == 'in_progress'
        assert DisclosureProvider.standardize_repurchase_progress('实施中') == 'in_progress'
        assert DisclosureProvider.standardize_repurchase_progress('已完成') == 'completed'
        assert DisclosureProvider.standardize_repurchase_progress('结束') == 'completed'
        assert DisclosureProvider.standardize_repurchase_progress('已取消') == 'cancelled'
        assert DisclosureProvider.standardize_repurchase_progress('终止') == 'cancelled'
    
    def test_standardize_repurchase_progress_english(self):
        """Test repurchase progress standardization with English input."""
        assert DisclosureProvider.standardize_repurchase_progress('plan') == 'planned'
        assert DisclosureProvider.standardize_repurchase_progress('in progress') == 'in_progress'
        assert DisclosureProvider.standardize_repurchase_progress('complete') == 'completed'
        assert DisclosureProvider.standardize_repurchase_progress('cancelled') == 'cancelled'
    
    def test_standardize_repurchase_progress_case_insensitive(self):
        """Test repurchase progress standardization is case-insensitive."""
        assert DisclosureProvider.standardize_repurchase_progress('PLAN') == 'planned'
        assert DisclosureProvider.standardize_repurchase_progress('In Progress') == 'in_progress'
        assert DisclosureProvider.standardize_repurchase_progress('COMPLETE') == 'completed'
    
    def test_standardize_repurchase_progress_unknown(self):
        """Test repurchase progress standardization with unknown input."""
        assert DisclosureProvider.standardize_repurchase_progress('unknown') == 'unknown'
        assert DisclosureProvider.standardize_repurchase_progress('xyz') == 'unknown'
        assert DisclosureProvider.standardize_repurchase_progress('') == 'unknown'
    
    def test_standardize_st_type_valid(self):
        """Test ST type standardization with valid inputs."""
        assert DisclosureProvider.standardize_st_type('ST') == 'ST'
        assert DisclosureProvider.standardize_st_type('*ST') == '*ST'
        assert DisclosureProvider.standardize_st_type('SST') == 'SST'
        assert DisclosureProvider.standardize_st_type('S*ST') == 'S*ST'
    
    def test_standardize_st_type_case_insensitive(self):
        """Test ST type standardization is case-insensitive."""
        assert DisclosureProvider.standardize_st_type('st') == 'ST'
        assert DisclosureProvider.standardize_st_type('*st') == '*ST'
        assert DisclosureProvider.standardize_st_type('sst') == 'SST'
        assert DisclosureProvider.standardize_st_type('s*st') == 'S*ST'
    
    def test_standardize_st_type_with_stock_name(self):
        """Test ST type standardization with full stock name."""
        assert DisclosureProvider.standardize_st_type('ST华谊') == 'ST'
        assert DisclosureProvider.standardize_st_type('*ST海润') == '*ST'
        assert DisclosureProvider.standardize_st_type('SST前锋') == 'SST'
        assert DisclosureProvider.standardize_st_type('S*ST昌鱼') == 'S*ST'
    
    def test_standardize_st_type_normal(self):
        """Test ST type standardization with normal stocks."""
        assert DisclosureProvider.standardize_st_type('正常') == 'normal'
        assert DisclosureProvider.standardize_st_type('normal') == 'normal'
        assert DisclosureProvider.standardize_st_type('平安银行') == 'normal'
        assert DisclosureProvider.standardize_st_type('') == 'normal'
    
    def test_standardize_st_type_priority(self):
        """Test ST type standardization priority (S*ST > *ST > SST > ST)."""
        # S*ST should be detected first
        assert DisclosureProvider.standardize_st_type('S*ST') == 'S*ST'
        # *ST should be detected before ST
        assert DisclosureProvider.standardize_st_type('*ST') == '*ST'
        # SST should be detected before ST
        assert DisclosureProvider.standardize_st_type('SST') == 'SST'
    
    def test_standardize_risk_level_critical(self):
        """Test risk level standardization for critical risks."""
        assert DisclosureProvider.standardize_risk_level('退市风险') == 'critical'
        assert DisclosureProvider.standardize_risk_level('delist') == 'critical'
        assert DisclosureProvider.standardize_risk_level('终止上市') == 'critical'
        assert DisclosureProvider.standardize_risk_level('critical') == 'critical'
        assert DisclosureProvider.standardize_risk_level('严重') == 'critical'
    
    def test_standardize_risk_level_high(self):
        """Test risk level standardization for high risks."""
        assert DisclosureProvider.standardize_risk_level('*ST') == 'high'
        assert DisclosureProvider.standardize_risk_level('S*ST') == 'high'
        assert DisclosureProvider.standardize_risk_level('high') == 'high'
        assert DisclosureProvider.standardize_risk_level('高风险') == 'high'
    
    def test_standardize_risk_level_medium(self):
        """Test risk level standardization for medium risks."""
        assert DisclosureProvider.standardize_risk_level('ST') == 'medium'
        assert DisclosureProvider.standardize_risk_level('SST') == 'medium'
        assert DisclosureProvider.standardize_risk_level('medium') == 'medium'
        assert DisclosureProvider.standardize_risk_level('中等风险') == 'medium'
    
    def test_standardize_risk_level_low(self):
        """Test risk level standardization for low risks."""
        assert DisclosureProvider.standardize_risk_level('正常') == 'low'
        assert DisclosureProvider.standardize_risk_level('low') == 'low'
        assert DisclosureProvider.standardize_risk_level('') == 'low'
        assert DisclosureProvider.standardize_risk_level('unknown') == 'low'
    
    def test_standardize_risk_level_case_insensitive(self):
        """Test risk level standardization is case-insensitive."""
        assert DisclosureProvider.standardize_risk_level('DELIST') == 'critical'
        assert DisclosureProvider.standardize_risk_level('HIGH') == 'high'
        assert DisclosureProvider.standardize_risk_level('MEDIUM') == 'medium'
        assert DisclosureProvider.standardize_risk_level('LOW') == 'low'
    
    def test_standardize_risk_level_priority(self):
        """Test risk level standardization priority (critical > high > medium > low)."""
        # Critical should be detected first
        assert DisclosureProvider.standardize_risk_level('退市风险*ST') == 'critical'
        # High should be detected before medium
        assert DisclosureProvider.standardize_risk_level('*ST风险') == 'high'
        # Medium should be detected before low
        assert DisclosureProvider.standardize_risk_level('ST风险') == 'medium'
