"""
Web Components Gallery Server

Hosts a gallery of reusable web components for quick review and testing.
Each component supports light/dark modes and can be embedded in blog posts.
"""

from pathlib import Path
from flask import Flask, render_template, send_from_directory

app = Flask(__name__)

# Path to component directories
COMPONENTS_DIR = Path(__file__).parent


def discover_components():
    """Discover all web components in subdirectories."""
    components = []
    
    for item in COMPONENTS_DIR.iterdir():
        if item.is_dir() and not item.name.startswith(('.', '__')):
            # Look for component.json metadata file
            metadata_file = item / "component.json"
            if metadata_file.exists():
                import json
                with open(metadata_file) as f:
                    metadata = json.load(f)
                    metadata['id'] = item.name
                    components.append(metadata)
            else:
                # Create basic metadata from directory
                components.append({
                    'id': item.name,
                    'name': item.name.replace('_', ' ').title(),
                    'description': f'Component: {item.name}',
                    'version': '1.0.0'
                })
    
    return sorted(components, key=lambda x: x['name'])


@app.route('/')
def index():
    """Gallery home page showing all components."""
    components = discover_components()
    return render_template('index.html', components=components)


@app.route('/component/<component_id>')
def component_detail(component_id):
    """Individual component demo page."""
    component_path = COMPONENTS_DIR / component_id
    
    if not component_path.exists():
        return "Component not found", 404
    
    # Load metadata
    metadata_file = component_path / "component.json"
    if metadata_file.exists():
        import json
        with open(metadata_file) as f:
            metadata = json.load(f)
    else:
        metadata = {
            'name': component_id.replace('_', ' ').title(),
            'description': f'Component: {component_id}',
            'version': '1.0.0'
        }
    
    metadata['id'] = component_id
    
    return render_template('component.html', component=metadata)


@app.route('/components/<path:filepath>')
def serve_component_file(filepath):
    """Serve component files (JS, CSS, etc.)."""
    return send_from_directory(COMPONENTS_DIR, filepath)


if __name__ == '__main__':
    app.run(debug=True, port=5001, host='0.0.0.0')
