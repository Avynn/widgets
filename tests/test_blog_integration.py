"""
Tests for blog integration helpers.
"""

import pytest

from blog_integration import (
    component_script_tag,
    component_tag,
    embed_component,
    markdown_component_block,
    get_examples
)
from config import (
    DevelopmentWidgetConfig,
    ProductionWidgetConfig,
    StaticWidgetConfig
)


class TestComponentScriptTag:
    """Tests for component_script_tag function."""
    
    def test_script_tag_development(self, dev_widget_config, component_id):
        """Should generate script tag with development URL."""
        tag = component_script_tag(component_id, dev_widget_config)
        expected = '<script src="http://localhost:5001/components/gaussian_kde_visualizer/gaussian-kde-visualizer.js"></script>'
        assert tag == expected
    
    def test_script_tag_production(self, prod_widget_config, component_id):
        """Should generate script tag with production URL."""
        tag = component_script_tag(component_id, prod_widget_config)
        expected = '<script src="https://widgets.example.com/components/gaussian_kde_visualizer/gaussian-kde-visualizer.js"></script>'
        assert tag == expected
    
    def test_script_tag_static(self, static_widget_config, component_id):
        """Should generate script tag with static URL."""
        tag = component_script_tag(component_id, static_widget_config)
        expected = '<script src="/static/widgets/gaussian-kde-visualizer.js"></script>'
        assert tag == expected


class TestComponentTag:
    """Tests for component_tag function."""
    
    def test_tag_without_attributes(self, component_id):
        """Should generate basic custom element tag."""
        tag = component_tag(component_id)
        assert tag == '<gaussian-kde-visualizer></gaussian-kde-visualizer>'
    
    def test_tag_with_attributes(self, component_id):
        """Should generate tag with attributes."""
        attrs = {'autoplay': 'true', 'bandwidth': '0.3'}
        tag = component_tag(component_id, attrs)
        
        assert tag.startswith('<gaussian-kde-visualizer')
        assert tag.endswith('</gaussian-kde-visualizer>')
        assert 'autoplay="true"' in tag
        assert 'bandwidth="0.3"' in tag
    
    def test_tag_underscores_to_hyphens(self):
        """Should convert underscores to hyphens in tag name."""
        tag = component_tag("my_custom_component")
        assert tag == '<my-custom-component></my-custom-component>'


class TestEmbedComponent:
    """Tests for embed_component function."""
    
    def test_embed_basic(self, dev_widget_config, component_id):
        """Should generate complete embed HTML."""
        html = embed_component(component_id, dev_widget_config)
        
        assert '<script src=' in html
        assert '<gaussian-kde-visualizer></gaussian-kde-visualizer>' in html
        assert 'http://localhost:5001' in html
    
    def test_embed_with_attributes(self, dev_widget_config, component_id):
        """Should include attributes in embed."""
        attrs = {'autoplay': 'true'}
        html = embed_component(component_id, dev_widget_config, attrs)
        
        assert 'autoplay="true"' in html
    
    def test_embed_production(self, prod_widget_config, component_id):
        """Should use production URLs."""
        html = embed_component(component_id, prod_widget_config)
        assert 'https://widgets.example.com' in html


class TestMarkdownComponentBlock:
    """Tests for markdown_component_block function."""
    
    def test_markdown_block(self, dev_widget_config, component_id):
        """Should generate markdown-safe HTML block."""
        html = markdown_component_block(component_id, dev_widget_config)
        
        assert '<!-- Web Component:' in html
        assert '<div class="component-embed">' in html
        assert '</div>' in html
        assert '<script src=' in html
    
    def test_markdown_block_with_attributes(self, dev_widget_config, component_id):
        """Should include attributes in markdown block."""
        attrs = {'data': '[1,2,3]'}
        html = markdown_component_block(component_id, dev_widget_config, attrs)
        
        assert 'data="[1,2,3]"' in html


class TestGetExamples:
    """Tests for get_examples function."""
    
    def test_get_examples_default_config(self):
        """Should return examples with default development config."""
        examples = get_examples()
        
        assert 'gaussian_kde_visualizer' in examples
        assert 'basic' in examples['gaussian_kde_visualizer']
        assert 'autoplay' in examples['gaussian_kde_visualizer']
        assert 'custom_data' in examples['gaussian_kde_visualizer']
    
    def test_get_examples_custom_config(self, prod_widget_config):
        """Should use provided config."""
        examples = get_examples(prod_widget_config)
        
        basic_example = examples['gaussian_kde_visualizer']['basic']
        assert 'https://widgets.example.com' in basic_example
    
    def test_examples_contain_valid_html(self, dev_widget_config):
        """Examples should contain valid HTML."""
        examples = get_examples(dev_widget_config)
        
        for component, example_dict in examples.items():
            for name, html in example_dict.items():
                assert '<script' in html
                assert '</script>' in html
                # Check for component tag (may have attributes)
                tag_name = component.replace('_', '-')
                assert f'<{tag_name}' in html or f'<{tag_name}>' in html


class TestIntegrationScenarios:
    """Integration tests for common usage scenarios."""
    
    def test_blog_development_workflow(self, dev_widget_config):
        """Test typical development workflow."""
        component_id = "gaussian_kde_visualizer"
        
        # Generate embed code for blog post
        html = markdown_component_block(component_id, dev_widget_config)
        
        # Verify it contains necessary elements
        assert 'localhost:5001' in html
        assert '<gaussian-kde-visualizer>' in html
    
    def test_blog_production_workflow(self):
        """Test production workflow with static files."""
        config = StaticWidgetConfig(static_url_prefix="https://cdn.example.com/static")
        component_id = "gaussian_kde_visualizer"
        
        # Generate embed code
        html = embed_component(component_id, config)
        
        # Should use CDN URL
        assert 'https://cdn.example.com/static/widgets/gaussian-kde-visualizer.js' in html
        assert '<gaussian-kde-visualizer>' in html
