"""
Configuration classes for widget server and integration.

Provides dependency injection for environment-specific URLs
and widget server settings.
"""

import os
from typing import Optional


class BaseWidgetConfig:
    """Base configuration for widget server."""
    
    def __init__(self):
        """Initialize base widget configuration."""
        self.HOST = 'localhost'
        self.PORT = 5001
        self.DEBUG = False
    
    def get_base_url(self) -> str:
        """Get the base URL for the widget server."""
        return f"http://{self.HOST}:{self.PORT}"
    
    def get_component_url(self, component_id: str) -> str:
        """
        Get the URL for a specific component's JavaScript file.
        
        Args:
            component_id: The component ID (e.g., 'gaussian_kde_visualizer')
            
        Returns:
            URL to the component's JavaScript file
        """
        script_name = component_id.replace('_', '-')
        return f"{self.get_base_url()}/components/{component_id}/{script_name}.js"


class DevelopmentWidgetConfig(BaseWidgetConfig):
    """Configuration for local development."""
    
    def __init__(self, host: str = 'localhost', port: int = 5001):
        """
        Initialize development configuration.
        
        Args:
            host: Host to bind to
            port: Port to listen on
        """
        super().__init__()
        self.HOST = host
        self.PORT = port
        self.DEBUG = True
        self.ENV = 'development'


class ProductionWidgetConfig(BaseWidgetConfig):
    """Configuration for production deployment."""
    
    def __init__(self, base_url: str):
        """
        Initialize production configuration.
        
        Args:
            base_url: Base URL for the widget server in production
        """
        super().__init__()
        self._base_url = base_url
        self.ENV = 'production'
        
        # Detect if running on Cloud Run
        self.IS_CLOUD_RUN = os.environ.get('K_SERVICE') is not None
    
    def get_base_url(self) -> str:
        """Return the configured base URL."""
        return self._base_url
    
    def get_component_url(self, component_id: str) -> str:
        """
        Get the URL for a specific component in production.
        
        In production, widgets might be served from CDN or static hosting.
        This can be overridden based on deployment strategy.
        """
        script_name = component_id.replace('_', '-')
        return f"{self._base_url}/components/{component_id}/{script_name}.js"


class StaticWidgetConfig(BaseWidgetConfig):
    """Configuration for widgets served from blog's static directory."""
    
    def __init__(self, static_url_prefix: str = "/static"):
        """
        Initialize static configuration.
        
        This is used when widgets are copied to the blog's static directory
        and served directly (as is currently done in production).
        
        Args:
            static_url_prefix: URL prefix for static files (e.g., '/static' or CDN URL)
        """
        super().__init__()
        self._static_url_prefix = static_url_prefix
        self.ENV = 'static'
    
    def get_base_url(self) -> str:
        """Return the static URL prefix."""
        return self._static_url_prefix
    
    def get_component_url(self, component_id: str) -> str:
        """
        Get the URL for a component served from static directory.
        
        Args:
            component_id: The component ID
            
        Returns:
            Static URL path to the component
        """
        script_name = component_id.replace('_', '-')
        return f"{self._static_url_prefix}/widgets/{script_name}.js"


class UnitTestWidgetConfig(BaseWidgetConfig):
    """Configuration for testing."""
    
    def __init__(self, mock_base_url: Optional[str] = None):
        """
        Initialize test configuration.
        
        Args:
            mock_base_url: Optional mock base URL for testing
        """
        super().__init__()
        self._mock_base_url = mock_base_url or "http://test.local:5001"
        self.TESTING = True
        self.ENV = 'testing'
    
    def get_base_url(self) -> str:
        """Return the mock base URL."""
        return self._mock_base_url


def create_widget_config(environment: Optional[str] = None, **kwargs) -> BaseWidgetConfig:
    """
    Factory function to create appropriate widget config.
    
    Args:
        environment: Environment name ('development', 'production', 'static', 'testing')
        **kwargs: Additional arguments for specific config classes
        
    Returns:
        Appropriate configuration instance
        
    Examples:
        >>> config = create_widget_config('development')
        >>> config = create_widget_config('production', base_url='https://widgets.example.com')
        >>> config = create_widget_config('static', static_url_prefix='/static')
        >>> config = create_widget_config('testing', mock_base_url='http://test:5001')
    """
    if environment is None:
        environment = 'development'
    
    env_lower = environment.lower()
    
    if env_lower == 'production':
        return ProductionWidgetConfig(**kwargs)
    elif env_lower == 'static':
        return StaticWidgetConfig(**kwargs)
    elif env_lower == 'testing':
        return UnitTestWidgetConfig(**kwargs)
    else:
        return DevelopmentWidgetConfig(**kwargs)
