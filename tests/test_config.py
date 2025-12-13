"""
Tests for widget configuration module.
"""

import pytest

from widgets.config import (
    BaseWidgetConfig,
    DevelopmentWidgetConfig,
    ProductionWidgetConfig,
    StaticWidgetConfig,
    UnitTestWidgetConfig,
    create_widget_config
)


class TestBaseWidgetConfig:
    """Tests for BaseWidgetConfig class."""
    
    def test_default_values(self):
        """Should have default host and port."""
        config = BaseWidgetConfig()
        assert config.HOST == 'localhost'
        assert config.PORT == 5001
        assert config.DEBUG is False
    
    def test_get_base_url(self):
        """Should construct base URL."""
        config = BaseWidgetConfig()
        assert config.get_base_url() == "http://localhost:5001"
    
    def test_get_component_url(self):
        """Should construct component URL."""
        config = BaseWidgetConfig()
        url = config.get_component_url("gaussian_kde_visualizer")
        assert url == "http://localhost:5001/components/gaussian_kde_visualizer/gaussian-kde-visualizer.js"


class TestDevelopmentWidgetConfig:
    """Tests for DevelopmentWidgetConfig class."""
    
    def test_default_development_config(self):
        """Should use default host and port."""
        config = DevelopmentWidgetConfig()
        assert config.HOST == 'localhost'
        assert config.PORT == 5001
        assert config.DEBUG is True
        assert config.ENV == 'development'
    
    def test_custom_host_and_port(self):
        """Should allow custom host and port."""
        config = DevelopmentWidgetConfig(host='0.0.0.0', port=8080)
        assert config.HOST == '0.0.0.0'
        assert config.PORT == 8080
        assert config.get_base_url() == "http://0.0.0.0:8080"


class TestProductionWidgetConfig:
    """Tests for ProductionWidgetConfig class."""
    
    def test_custom_base_url(self):
        """Should use provided base URL."""
        config = ProductionWidgetConfig(base_url="https://widgets.example.com")
        assert config.ENV == 'production'
        assert config.get_base_url() == "https://widgets.example.com"
    
    def test_get_component_url(self):
        """Should construct component URL with custom base."""
        config = ProductionWidgetConfig(base_url="https://widgets.example.com")
        url = config.get_component_url("gaussian_kde_visualizer")
        expected = "https://widgets.example.com/components/gaussian_kde_visualizer/gaussian-kde-visualizer.js"
        assert url == expected


class TestStaticWidgetConfig:
    """Tests for StaticWidgetConfig class."""
    
    def test_default_static_prefix(self):
        """Should use default /static prefix."""
        config = StaticWidgetConfig()
        assert config.get_base_url() == "/static"
        assert config.ENV == 'static'
    
    def test_custom_static_prefix(self):
        """Should allow custom static URL prefix."""
        config = StaticWidgetConfig(static_url_prefix="https://cdn.example.com/static")
        assert config.get_base_url() == "https://cdn.example.com/static"
    
    def test_get_component_url(self):
        """Should construct static component URL."""
        config = StaticWidgetConfig(static_url_prefix="/static")
        url = config.get_component_url("gaussian_kde_visualizer")
        assert url == "/static/widgets/gaussian-kde-visualizer.js"
    
    def test_get_component_url_with_cdn(self):
        """Should work with CDN URLs."""
        config = StaticWidgetConfig(static_url_prefix="https://cdn.example.com/static")
        url = config.get_component_url("gaussian_kde_visualizer")
        assert url == "https://cdn.example.com/static/widgets/gaussian-kde-visualizer.js"


class TestUnitTestWidgetConfig:
    """Tests for UnitTestWidgetConfig class."""
    
    def test_default_mock_url(self):
        """Should use default mock URL."""
        config = UnitTestWidgetConfig()
        assert config.TESTING is True
        assert config.ENV == 'testing'
        assert config.get_base_url() == "http://test.local:5001"
    
    def test_custom_mock_url(self):
        """Should allow custom mock URL."""
        config = UnitTestWidgetConfig(mock_base_url="http://custom.test:9000")
        assert config.get_base_url() == "http://custom.test:9000"


class TestCreateWidgetConfig:
    """Tests for create_widget_config factory function."""
    
    def test_create_development_config(self):
        """Should create DevelopmentWidgetConfig."""
        config = create_widget_config('development')
        assert isinstance(config, DevelopmentWidgetConfig)
    
    def test_create_production_config(self):
        """Should create ProductionWidgetConfig."""
        config = create_widget_config('production', base_url='https://example.com')
        assert isinstance(config, ProductionWidgetConfig)
    
    def test_create_static_config(self):
        """Should create StaticWidgetConfig."""
        config = create_widget_config('static')
        assert isinstance(config, StaticWidgetConfig)
    
    def test_create_testing_config(self):
        """Should create UnitTestWidgetConfig."""
        config = create_widget_config('testing')
        assert isinstance(config, UnitTestWidgetConfig)
    
    def test_default_to_development(self):
        """Should default to development."""
        config = create_widget_config()
        assert isinstance(config, DevelopmentWidgetConfig)
