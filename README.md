# Web Components Gallery

A gallery of reusable web components with Material Design 3 styling. Each component supports both light and dark themes and can be easily embedded in blog posts.

## Features

- 🎨 **Material Design 3** - Latest Google Material Design guidelines
- 🌓 **Theme Support** - Automatic light/dark mode switching
- 📦 **Self-Contained** - Each component is a standalone web component
- 🔌 **Easy Embedding** - Simple integration with blog posts
- 🎯 **Shadow DOM** - Encapsulated styles prevent conflicts
- ⚡ **Fast Development** - Quick preview and testing gallery

## Project Structure

```
widgets/
├── app.py                      # Flask gallery server
├── requirements.txt            # Python dependencies
├── blog_integration.py         # Blog embedding helpers
├── templates/                  # HTML templates
│   ├── base.html              # Base template with theme switching
│   ├── index.html             # Gallery home page
│   └── component.html         # Individual component demo page
├── static/                     # Static assets
│   └── style.css              # Material Design 3 styles
└── [component_name]/          # Component directories
    ├── component.json         # Component metadata
    └── [component-name].js    # Web component implementation
```

## Getting Started

### Running the Gallery

1. Install dependencies:

```bash
cd widgets
pip install -r requirements.txt
```

2. Start the server:

```bash
python app.py
```

3. Open your browser to `http://localhost:5001`

### Creating a New Component

1. Create a new directory in `widgets/`:

```bash
mkdir widgets/my_new_component
```

2. Create `component.json`:

```json
{
  "name": "My New Component",
  "description": "Description of what it does",
  "version": "1.0.0",
  "supportsThemes": true
}
```

3. Create the web component JavaScript file:

```javascript
// widgets/my_new_component/my-new-component.js

class MyNewComponent extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: "open" });
  }

  connectedCallback() {
    this.render();
    this.setupThemeListener();
  }

  setupThemeListener() {
    window.addEventListener("themechange", (e) => {
      this.updateTheme(e.detail.theme);
    });

    const docTheme = document.documentElement.getAttribute("data-theme");
    this.updateTheme(docTheme || "light");
  }

  updateTheme(theme) {
    this.shadowRoot.host.setAttribute("data-theme", theme);
  }

  render() {
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
        }
        
        :host([data-theme="light"]) {
          --surface: #FFFBFE;
          --on-surface: #1D1B20;
        }
        
        :host([data-theme="dark"]) {
          --surface: #1C1B1F;
          --on-surface: #E6E0E9;
        }
        
        .container {
          background: var(--surface);
          color: var(--on-surface);
          padding: 20px;
          border-radius: 12px;
        }
      </style>
      
      <div class="container">
        <h2>My New Component</h2>
        <p>Content goes here</p>
      </div>
    `;
  }
}

customElements.define("my-new-component", MyNewComponent);
```

4. The component will automatically appear in the gallery!

## Embedding in Blog Posts

### Method 1: Using Python Helpers

```python
from widgets.blog_integration import embed_component

# Basic embedding
html = embed_component('gaussian_kde_visualizer')

# With attributes
html = embed_component('gaussian_kde_visualizer', attributes={
    'autoplay': 'true',
    'width': '800',
    'height': '500'
})
```

### Method 2: Direct HTML

```html
<!-- Include the script -->
<script src="http://localhost:5001/components/gaussian_kde_visualizer/gaussian-kde-visualizer.js"></script>

<!-- Use the component -->
<gaussian-kde-visualizer autoplay="true"></gaussian-kde-visualizer>
```

### Method 3: In Markdown

```markdown
<!-- Web Component -->
<div class="component-embed">
<script src="http://localhost:5001/components/gaussian_kde_visualizer/gaussian-kde-visualizer.js"></script>
<gaussian-kde-visualizer autoplay="true"></gaussian-kde-visualizer>
</div>
```

## Available Components

### Gaussian KDE Visualizer

Interactive visualization of Gaussian Kernel Density Estimation.

**Features:**

- Animated sample-by-sample construction
- Material Design 3 styling
- Play/pause controls
- Speed adjustment
- Custom data support

**Usage:**

```html
<gaussian-kde-visualizer
  data="[1.5, 2.3, 1.8, 3.2, 2.9]"
  bandwidth="0.3"
  autoplay="true"
>
</gaussian-kde-visualizer>
```

**Attributes:**

- `data` - Array of data points (JSON or comma-separated)
- `bandwidth` - KDE bandwidth (auto-calculated if not provided)
- `width` - Canvas width in pixels (default: 800)
- `height` - Canvas height in pixels (default: 500)
- `autoplay` - Start animation automatically (default: false)

## Material Design 3 Guidelines

All components follow Material Design 3 principles:

### Color System

- Light and dark theme support
- Primary, secondary, and surface colors
- Proper contrast ratios for accessibility

### Typography

- Roboto font family
- Material Design 3 type scale
- Appropriate font weights and sizes

### Elevation & Shadows

- Three elevation levels
- Proper shadow application
- Smooth transitions

### Motion

- Easing curves: `cubic-bezier(0.4, 0, 0.2, 1)`
- Appropriate animation durations
- Meaningful motion feedback

## Development Tips

### Theme Support

Always implement theme switching in your components:

```javascript
setupThemeListener() {
  window.addEventListener('themechange', (e) => {
    this.currentTheme = e.detail.theme;
    this.redraw(); // Update your component
  });
}
```

### Material Design Colors

Use CSS custom properties for theming:

```css
:host([data-theme="light"]) {
  --md-sys-color-primary: #6750a4;
  --md-sys-color-surface: #fffbfe;
  /* ... other colors */
}

:host([data-theme="dark"]) {
  --md-sys-color-primary: #d0bcff;
  --md-sys-color-surface: #1c1b1f;
  /* ... other colors */
}
```

### Responsive Design

Make components responsive:

```css
@media (max-width: 600px) {
  .container {
    padding: 12px;
  }
}
```

---

## License

MIT License - See [LICENSE](LICENSE) for details.

## Contributing

Contributions are welcome! Each component should:

1. Follow Material Design 3 guidelines
2. Support both light and dark themes
3. Use Shadow DOM for encapsulation
4. Be fully self-contained (no external dependencies)
5. Include proper documentation in `component.json`
6. Work when embedded in other pages

## Resources

- [Material Design 3](https://m3.material.io/)
- [Web Components](https://developer.mozilla.org/en-US/docs/Web/Web_Components)
- [Shadow DOM](https://developer.mozilla.org/en-US/docs/Web/Web_Components/Using_shadow_DOM)
- [Custom Elements](https://developer.mozilla.org/en-US/docs/Web/Web_Components/Using_custom_elements)
