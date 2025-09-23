import pytest
import asyncio
from core.data_sources.fxcm_forexconnect_provider import FXCMForexConnectProvider, MockFXCMForexConnectProvider

@pytest.fixture
def mock_provider():
    """Provides a mock FXCM ForexConnect provider for testing."""
    config = {
        "username": "testuser",
        "password": "testpassword",
        "connection_type": "Demo"
    }
    return MockFXCMForexConnectProvider(config)

@pytest.mark.asyncio
async def test_mock_provider_connect_disconnect(mock_provider):
    """Test connection and disconnection of the mock provider."""
    assert not mock_provider.is_connected
    connected = await mock_provider.connect()
    assert connected
    assert mock_provider.is_connected
    await mock_provider.disconnect()
    assert not mock_provider.is_connected

@pytest.mark.asyncio
async def test_mock_provider_get_live_prices(mock_provider):
    """Test getting live prices from the mock provider."""
    await mock_provider.connect()
    prices = await mock_provider.get_live_prices(['EURUSD', 'GBPUSD'])
    assert 'EURUSD' in prices
    assert 'GBPUSD' in prices
    assert 'bid' in prices['EURUSD']
    assert 'ask' in prices['EURUSD']
    await mock_provider.disconnect()

@pytest.mark.asyncio
async def test_mock_provider_get_historical_data(mock_provider):
    """Test getting historical data from the mock provider."""
    await mock_provider.connect()
    df = await mock_provider.get_historical_data('EURUSD', 'H1', count=100)
    assert not df.empty
    assert len(df) == 100
    assert 'open' in df.columns
    assert 'high' in df.columns
    assert 'low' in df.columns
    assert 'close' in df.columns
    await mock_provider.disconnect()

@pytest.mark.asyncio
async def test_mock_provider_get_account_summary(mock_provider):
    """Test getting account summary from the mock provider."""
    await mock_provider.connect()
    summary = await mock_provider.get_account_summary()
    assert 'account_info' in summary
    assert 'positions' in summary
    assert summary['account_info']['account_id'] == 'MOCK123456'
    await mock_provider.disconnect()
