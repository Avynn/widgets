"""
Blog integration utilities for web components.

Provides helper functions to easily embed web components in blog posts.
Now uses dependency injection via WidgetConfig for environment-aware URLs.
"""

from pathlib import Path
from typing import Dict, Optional

from config import BaseWidgetConfig, DevelopmentWidgetConfig


def component_script_tag(component_id: str, config: BaseWidgetConfig) -> str:
    """
    Generate a script tag to include a component.
    
    Args:
        component_id: The ID of the component (e.g., 'gaussian_kde_visualizer')
        config: Widget configuration with base URL
        
    Returns:
        HTML script tag as a string
    """
    component_url = config.get_component_url(component_id)
    return f'<script src="{component_url}"></script>'


def component_tag(component_id: str, attributes: Optional[Dict[str, str]] = None) -> str:
    """
    Generate the HTML custom element tag for a component.
    
    Args:
        component_id: The ID of the component (e.g., 'gaussian_kde_visualizer')
        attributes: Optional dictionary of attributes to add to the tag
        
    Returns:
        HTML custom element tag as a string
    """
    tag_name = component_id.replace('_', '-')
    
    if attributes:
        attrs_str = ' '.join([f'{k}="{v}"' for k, v in attributes.items()])
        return f'<{tag_name} {attrs_str}></{tag_name}>'
    else:
        return f'<{tag_name}></{tag_name}>'


def embed_component(component_id: str, 
                    config: BaseWidgetConfig,
                    attributes: Optional[Dict[str, str]] = None) -> str:
    """
    Generate complete HTML to embed a component in a blog post.
    
    Args:
        component_id: The ID of the component (e.g., 'gaussian_kde_visualizer')
        config: Widget configuration with base URL
        attributes: Optional dictionary of attributes to add to the tag
        
    Returns:
        Complete HTML string with script and element tag
        
    Example:
        >>> from config import DevelopmentWidgetConfig
        >>> config = DevelopmentWidgetConfig()
        >>> embed_component('gaussian_kde_visualizer', config, {'autoplay': 'true'})
    """
    script = component_script_tag(component_id, config)
    tag = component_tag(component_id, attributes)
    
    return f"""{script}
{tag}"""


def markdown_component_block(component_id: str,
                             config: BaseWidgetConfig,
                             attributes: Optional[Dict[str, str]] = None) -> str:
    """
    Generate a markdown-safe HTML block for embedding in markdown blog posts.
    
    Args:
        component_id: The ID of the component
        config: Widget configuration with base URL
        attributes: Optional dictionary of attributes
        
    Returns:
        HTML block that can be inserted into markdown
    """
    html = embed_component(component_id, config, attributes)
    
    return f"""
<!-- Web Component: {component_id} -->
<div class="component-embed">
{html}
</div>
"""


# Example usage for common components
def get_examples(config: Optional[BaseWidgetConfig] = None) -> Dict[str, Dict[str, str]]:
    """
    Get example HTML for common components.
    
    Args:
        config: Widget configuration. If None, uses DevelopmentWidgetConfig.
        
    Returns:
        Dictionary of component examples
    """
    if config is None:
        config = DevelopmentWidgetConfig()
    
    return {
        'gaussian_kde_visualizer': {
            'basic': embed_component('gaussian_kde_visualizer', config),
            'autoplay': embed_component('gaussian_kde_visualizer', config, {'autoplay': 'true'}),
            'custom_data': embed_component('gaussian_kde_visualizer', config, {
                'data': '[1.5, 2.3, 1.8, 3.2, 2.9, 2.1, 3.5, 2.8]',
                'bandwidth': '0.3'
            })
        }
    }


if __name__ == '__main__':
    # Print examples with development config
    config = DevelopmentWidgetConfig()
    examples = get_examples(config)
    
    print("=== Blog Component Integration Examples ===\n")
    
    for component, example_dict in examples.items():
        print(f"\n{component.replace('_', ' ').title()}:")
        print("-" * 50)
        for name, code in example_dict.items():
            print(f"\n{name.title()}:")
            print(code)
