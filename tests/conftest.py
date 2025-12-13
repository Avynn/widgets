"""
Shared test fixtures for widget tests.
"""

import pytest

from widgets.config import (
    DevelopmentWidgetConfig,
    ProductionWidgetConfig,
    StaticWidgetConfig,
    UnitTestWidgetConfig
)


@pytest.fixture
def dev_widget_config():
    """Development widget configuration."""
    return DevelopmentWidgetConfig()


@pytest.fixture
def prod_widget_config():
    """Production widget configuration."""
    return ProductionWidgetConfig(base_url="https://widgets.example.com")


@pytest.fixture
def static_widget_config():
    """Static widget configuration."""
    return StaticWidgetConfig(static_url_prefix="/static")


@pytest.fixture
def test_widget_config():
    """Test widget configuration."""
    return UnitTestWidgetConfig(mock_base_url="http://test.local:5001")


@pytest.fixture
def component_id():
    """Sample component ID for testing."""
    return "gaussian_kde_visualizer"
