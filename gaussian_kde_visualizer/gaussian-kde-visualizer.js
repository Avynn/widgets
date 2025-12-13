/**
 * Gaussian KDE Visualizer - Material Design 3
 * 
 * An interactive web component that visualizes Kernel Density Estimation
 * with Material Design 3 styling and smooth animations.
 * 
 * Features:
 * - Material Design 3 color system
 * - Light and dark theme support
 * - Smooth easing animations following Material Motion guidelines
 * - Responsive design
 * - Shadow DOM encapsulation
 */

class GaussianKDEVisualizer extends HTMLElement {
  constructor() {
    super();
    this.attachShadow({ mode: 'open' });
    
    // Drag state
    this.draggedPointIndex = -1;
    this.isDragging = false;
    
    // Transition state for smooth KDE updates
    this.isTransitioning = false;
    this.transitionProgress = 0;
    this.transitionFrames = 15;
    this.oldKDE = null;
    this.newKDE = null;
    
    // Shuffle animation state
    this.isShuffling = false;
    this.shuffleProgress = 0;
    this.shuffleFrames = 60;
    this.oldData = null;
    this.newData = null;
    this.oldXMin = null;
    this.oldXMax = null;
    this.oldYMax = null;
    this.targetXMin = null;
    this.targetXMax = null;
    this.targetYMax = null;
    
    // Store initial state for reset
    this.initialData = null;
    this.initialBandwidth = null;
    this.initialXMin = null;
    this.initialXMax = null;
    this.initialYMax = null;
    
    // Theme
    this.currentTheme = 'light';
    
    // Bandwidth control
    this.autoBandwidth = true;
    this.manualBandwidth = 0.5;
  }

  static get observedAttributes() {
    return ['data', 'bandwidth', 'bandwidth-mode', 'width', 'height', 'theme'];
  }

  connectedCallback() {
    this.render();
    this.parseData();
    this.setupCanvas();
    this.setupControls();
    this.setupThemeListener();
    this.updateTheme();
    this.updateSampleCount();
    
    // Set toggle state based on bandwidth mode
    const bandwidthToggle = this.shadowRoot.querySelector('#bandwidthToggle');
    if (bandwidthToggle) {
      bandwidthToggle.checked = !this.autoBandwidth;
    }
    
    this.updateBandwidthControls();
    this.drawFrame();
  }

  updateSampleCount() {
    const sampleCountEl = this.shadowRoot.querySelector('#sampleCount');
    if (sampleCountEl) {
      sampleCountEl.textContent = this.data.length;
    }
  }

  disconnectedCallback() {
    // Cleanup if needed
  }

  attributeChangedCallback(name, oldValue, newValue) {
    if (oldValue === newValue) return;
    
    if (name === 'theme') {
      this.updateTheme();
    }
  }

  setupThemeListener() {
    // Listen for theme changes from the parent document
    window.addEventListener('themechange', (e) => {
      this.currentTheme = e.detail.theme;
      this.updateTheme();
      this.drawFrame();
    });
    
    // Detect initial theme from document
    const docTheme = document.documentElement.getAttribute('data-theme');
    if (docTheme) {
      this.currentTheme = docTheme;
    }
  }

  updateTheme() {
    const theme = this.getAttribute('theme') || this.currentTheme;
    this.currentTheme = theme;
    
    // Update CSS custom properties based on theme
    const root = this.shadowRoot.host;
    root.setAttribute('data-theme', theme);
  }

  parseData() {
    const dataAttr = this.getAttribute('data');
    if (dataAttr) {
      try {
        this.data = JSON.parse(dataAttr);
      } catch (e) {
        this.data = dataAttr.split(',').map(x => parseFloat(x.trim()));
      }
    } else {
      // Default sample data
      this.data = [
        0.4967, -0.1383, 0.6477, 1.5230, -0.2342, -0.2341, 1.5792, 0.7674,
        -0.4695, 0.5426, -0.4634, -0.4657, 0.2420, -1.9133, -1.7249, -0.5623,
        -1.0128, 0.3142, -0.9080, -1.4123
      ];
    }

    const calculatedBandwidth = this.calculateBandwidth();
    this.bandwidth = parseFloat(this.getAttribute('bandwidth')) || calculatedBandwidth;
    this.manualBandwidth = calculatedBandwidth;
    
    // Check for bandwidth-mode attribute
    const bandwidthMode = this.getAttribute('bandwidth-mode');
    if (bandwidthMode === 'manual') {
      this.autoBandwidth = false;
      // If manual mode and bandwidth is specified, use it
      if (this.getAttribute('bandwidth')) {
        this.manualBandwidth = this.bandwidth;
      } else {
        this.manualBandwidth = calculatedBandwidth;
        this.bandwidth = calculatedBandwidth;
      }
    } else {
      this.autoBandwidth = true;
    }
    
    this.nSamples = this.data.length;
    
    // Store initial state for reset
    if (this.initialData === null) {
      this.initialData = [...this.data];
    }
  }

  calculateBandwidth() {
    const n = this.data.length;
    const std = this.standardDeviation(this.data);
    return 1.06 * std * Math.pow(n, -0.2);
  }

  standardDeviation(arr) {
    const mean = arr.reduce((a, b) => a + b) / arr.length;
    const variance = arr.reduce((sum, val) => sum + Math.pow(val - mean, 2), 0) / arr.length;
    return Math.sqrt(variance);
  }

  setupCanvas() {
    this.canvas = this.shadowRoot.querySelector('#canvas');
    this.ctx = this.canvas.getContext('2d');
    
    const width = parseInt(this.getAttribute('width')) || 800;
    const height = parseInt(this.getAttribute('height')) || 500;
    
    // Handle high DPI displays
    const dpr = window.devicePixelRatio || 1;
    this.canvas.width = width * dpr;
    this.canvas.height = height * dpr;
    this.canvas.style.width = width + 'px';
    this.canvas.style.height = height + 'px';
    this.ctx.scale(dpr, dpr);
    
    this.canvasWidth = width;
    this.canvasHeight = height;
    
    // Set up coordinate system
    const dataMin = Math.min(...this.data);
    const dataMax = Math.max(...this.data);
    
    this.xMin = dataMin - 3 * this.bandwidth;
    this.xMax = dataMax + 3 * this.bandwidth;
    this.xRange = this.xMax - this.xMin;
    
    this.yMax = this.calculateMaxKDE() * 1.1;
    
    this.padding = { top: 60, right: 60, bottom: 80, left: 80 };
    this.plotWidth = width - this.padding.left - this.padding.right;
    this.plotHeight = height - this.padding.top - this.padding.bottom;
    
    // Store initial coordinate system for reset
    if (this.initialXMin === null) {
      this.initialXMin = this.xMin;
      this.initialXMax = this.xMax;
      this.initialYMax = this.yMax;
      this.initialBandwidth = this.bandwidth;
    }
  }

  calculateMaxKDE() {
    const x = this.linspace(this.xMin, this.xMax, 200);
    let maxDensity = 0;
    
    x.forEach(xi => {
      let density = 0;
      this.data.forEach(sample => {
        density += this.gaussian(xi, sample, this.bandwidth);
      });
      density /= this.nSamples;
      maxDensity = Math.max(maxDensity, density);
    });
    
    return maxDensity;
  }

  setupControls() {
    const addBtn = this.shadowRoot.querySelector('#addBtn');
    const removeBtn = this.shadowRoot.querySelector('#removeBtn');
    const shuffleBtn = this.shadowRoot.querySelector('#shuffleBtn');
    const sortAscBtn = this.shadowRoot.querySelector('#sortAscBtn');
    const sortDescBtn = this.shadowRoot.querySelector('#sortDescBtn');
    const resetBtn = this.shadowRoot.querySelector('#resetBtn');
    const bandwidthToggle = this.shadowRoot.querySelector('#bandwidthToggle');
    const bandwidthSlider = this.shadowRoot.querySelector('#bandwidthSlider');
    const bandwidthValue = this.shadowRoot.querySelector('#bandwidthValue');
    
    addBtn.addEventListener('click', () => {
      this.addSample();
    });
    
    removeBtn.addEventListener('click', () => {
      this.removeSample();
    });
    
    shuffleBtn.addEventListener('click', () => {
      this.shuffleData();
    });
    
    sortAscBtn.addEventListener('click', () => {
      this.sortData('asc');
    });
    
    sortDescBtn.addEventListener('click', () => {
      this.sortData('desc');
    });
    
    resetBtn.addEventListener('click', () => {
      this.resetToInitial();
    });
    
    bandwidthToggle.addEventListener('change', (e) => {
      this.autoBandwidth = !e.target.checked;
      this.updateBandwidthControls();
      if (this.autoBandwidth) {
        this.setBandwidth(this.calculateBandwidth());
      } else {
        this.setBandwidth(this.manualBandwidth);
      }
    });
    
    bandwidthSlider.addEventListener('input', (e) => {
      const value = parseFloat(e.target.value);
      this.manualBandwidth = value;
      bandwidthValue.textContent = value.toFixed(3);
      if (!this.autoBandwidth) {
        this.setBandwidth(value);
      }
    });
    
    // Mouse event handlers for dragging points
    this.canvas.addEventListener('mousedown', (e) => this.handleMouseDown(e));
    this.canvas.addEventListener('mousemove', (e) => this.handleMouseMove(e));
    this.canvas.addEventListener('mouseup', (e) => this.handleMouseUp(e));
    this.canvas.addEventListener('mouseleave', (e) => this.handleMouseUp(e));
    
    // Touch event handlers for mobile
    this.canvas.addEventListener('touchstart', (e) => this.handleTouchStart(e));
    this.canvas.addEventListener('touchmove', (e) => this.handleTouchMove(e));
    this.canvas.addEventListener('touchend', (e) => this.handleTouchEnd(e));
  }



  addSample() {
    // Generate a new random sample within the current data range
    const mean = this.data.reduce((a, b) => a + b) / this.data.length;
    const std = this.standardDeviation(this.data);
    const newSample = mean + (Math.random() - 0.5) * 2 * std;
    
    this.startTransition(() => {
      this.data.push(newSample);
      this.nSamples = this.data.length;
      if (this.autoBandwidth) {
        this.bandwidth = this.calculateBandwidth();
        this.manualBandwidth = this.bandwidth;
        this.updateBandwidthControls();
      }
      this.updateCoordinateSystem();
      this.updateSampleCount();
    });
  }

  removeSample() {
    if (this.data.length <= 1) return;
    
    this.startTransition(() => {
      this.data.pop();
      this.nSamples = this.data.length;
      if (this.autoBandwidth) {
        this.bandwidth = this.calculateBandwidth();
        this.manualBandwidth = this.bandwidth;
        this.updateBandwidthControls();
      }
      this.updateCoordinateSystem();
      this.updateSampleCount();
    });
  }

  shuffleData() {
    if (this.isShuffling || this.isTransitioning) return;
    
    // Store old data positions
    this.oldData = [...this.data];
    
    // Fisher-Yates shuffle
    this.newData = [...this.data];
    for (let i = this.newData.length - 1; i > 0; i--) {
      const j = Math.floor(Math.random() * (i + 1));
      [this.newData[i], this.newData[j]] = [this.newData[j], this.newData[i]];
    }
    
    // Start shuffle animation
    this.isShuffling = true;
    this.shuffleProgress = 0;
    this.animateShuffle();
  }

  sortData(direction) {
    if (this.isShuffling || this.isTransitioning) return;
    
    // Store old data positions
    this.oldData = [...this.data];
    
    // Sort data
    this.newData = [...this.data];
    if (direction === 'asc') {
      this.newData.sort((a, b) => a - b);
    } else {
      this.newData.sort((a, b) => b - a);
    }
    
    // Start shuffle animation (reuse same animation)
    this.isShuffling = true;
    this.shuffleProgress = 0;
    this.animateShuffle();
  }

  resetToInitial() {
    if (this.isShuffling || this.isTransitioning) return;
    
    // Store old data and coordinate system
    this.oldData = [...this.data];
    this.oldXMin = this.xMin;
    this.oldXMax = this.xMax;
    this.oldYMax = this.yMax;
    
    // Reset to initial data
    this.newData = [...this.initialData];
    
    // Set target coordinate system
    this.targetXMin = this.initialXMin;
    this.targetXMax = this.initialXMax;
    this.targetYMax = this.initialYMax;
    
    // Update sample count immediately
    this.nSamples = this.newData.length;
    this.updateSampleCount();
    
    // Reset bandwidth to auto
    this.autoBandwidth = true;
    const bandwidthToggle = this.shadowRoot.querySelector('#bandwidthToggle');
    if (bandwidthToggle) bandwidthToggle.checked = false;
    this.updateBandwidthControls();
    
    // Start shuffle animation
    this.isShuffling = true;
    this.shuffleProgress = 0;
    this.animateShuffle();
  }

  animateShuffle() {
    if (!this.isShuffling) return;
    
    this.shuffleProgress++;
    const normalizedProgress = this.shuffleProgress / this.shuffleFrames;
    const easedProgress = this.easeInOutCubic(normalizedProgress);
    
    this.drawShuffleFrame(easedProgress);
    
    if (this.shuffleProgress >= this.shuffleFrames) {
      this.isShuffling = false;
      this.data = [...this.newData];
      this.nSamples = this.data.length;
      
      // Finalize coordinate system if targets are set
      if (this.targetXMin !== null) {
        this.xMin = this.targetXMin;
        this.xMax = this.targetXMax;
        this.xRange = this.xMax - this.xMin;
        this.yMax = this.targetYMax;
        this.bandwidth = this.initialBandwidth;
      }
      
      this.oldData = null;
      this.newData = null;
      this.oldXMin = null;
      this.oldXMax = null;
      this.oldYMax = null;
      this.targetXMin = null;
      this.targetXMax = null;
      this.targetYMax = null;
      this.drawFrame();
    } else {
      requestAnimationFrame(() => this.animateShuffle());
    }
  }

  updateCoordinateSystem() {
    const dataMin = Math.min(...this.data);
    const dataMax = Math.max(...this.data);
    
    this.xMin = dataMin - 3 * this.bandwidth;
    this.xMax = dataMax + 3 * this.bandwidth;
    this.xRange = this.xMax - this.xMin;
    this.yMax = this.calculateMaxKDE() * 1.1;
  }
  
  updateBandwidthControls() {
    const bandwidthSlider = this.shadowRoot.querySelector('#bandwidthSlider');
    const bandwidthValue = this.shadowRoot.querySelector('#bandwidthValue');
    const sliderContainer = this.shadowRoot.querySelector('.bandwidth-slider-container');
    
    if (this.autoBandwidth) {
      sliderContainer.style.opacity = '0.5';
      sliderContainer.style.pointerEvents = 'none';
      bandwidthSlider.disabled = true;
    } else {
      sliderContainer.style.opacity = '1';
      sliderContainer.style.pointerEvents = 'auto';
      bandwidthSlider.disabled = false;
    }
    
    bandwidthSlider.value = this.manualBandwidth;
    bandwidthValue.textContent = this.manualBandwidth.toFixed(3);
  }
  
  setBandwidth(newBandwidth) {
    if (this.isTransitioning || this.isShuffling) return;
    
    const oldBandwidth = this.bandwidth;
    if (Math.abs(oldBandwidth - newBandwidth) < 0.001) return;
    
    this.startTransition(() => {
      this.bandwidth = newBandwidth;
      this.updateCoordinateSystem();
    });
  }

  startTransition(updateCallback) {
    // Capture current KDE state
    const resolution = 300;
    const x = this.linspace(this.xMin, this.xMax, resolution);
    this.oldKDE = x.map(xi => {
      let density = 0;
      this.data.forEach(sample => {
        density += this.gaussian(xi, sample, this.bandwidth);
      });
      return density / this.nSamples;
    });
    
    // Apply the update
    updateCallback();
    
    // Capture new KDE state
    const newX = this.linspace(this.xMin, this.xMax, resolution);
    this.newKDE = newX.map(xi => {
      let density = 0;
      this.data.forEach(sample => {
        density += this.gaussian(xi, sample, this.bandwidth);
      });
      return density / this.nSamples;
    });
    
    // Start transition animation
    this.isTransitioning = true;
    this.transitionProgress = 0;
    this.animateTransition();
  }

  animateTransition() {
    if (!this.isTransitioning) return;
    
    this.transitionProgress++;
    const normalizedProgress = this.transitionProgress / this.transitionFrames;
    const easedProgress = this.easeInOutCubic(normalizedProgress);
    
    this.drawTransitionFrame(easedProgress);
    
    if (this.transitionProgress >= this.transitionFrames) {
      this.isTransitioning = false;
      this.oldKDE = null;
      this.newKDE = null;
      this.drawFrame();
    } else {
      requestAnimationFrame(() => this.animateTransition());
    }
  }

  // Material Motion easing function
  easeInOutCubic(t) {
    return t < 0.5 
      ? 4 * t * t * t 
      : 1 - Math.pow(-2 * t + 2, 3) / 2;
  }

  drawFrame() {
    // Clear canvas
    this.ctx.clearRect(0, 0, this.canvasWidth, this.canvasHeight);
    
    // Draw components
    this.drawGrid();
    this.drawAxes();
    this.drawKDE();
    this.drawSamplePoints();
    this.drawInfoCard();
    this.drawTitle();
  }

  drawTransitionFrame(progress) {
    // Clear canvas
    this.ctx.clearRect(0, 0, this.canvasWidth, this.canvasHeight);
    
    // Draw components
    this.drawGrid();
    this.drawAxes();
    this.drawTransitioningKDE(progress);
    this.drawSamplePoints();
    this.drawInfoCard();
    this.drawTitle();
  }

  drawShuffleFrame(progress) {
    // Interpolate coordinate system if targets are set
    if (this.targetXMin !== null) {
      this.xMin = this.oldXMin + (this.targetXMin - this.oldXMin) * progress;
      this.xMax = this.oldXMax + (this.targetXMax - this.oldXMax) * progress;
      this.xRange = this.xMax - this.xMin;
      this.yMax = this.oldYMax + (this.targetYMax - this.oldYMax) * progress;
    }
    
    // Clear canvas
    this.ctx.clearRect(0, 0, this.canvasWidth, this.canvasHeight);
    
    // Draw components
    this.drawGrid();
    this.drawAxes();
    this.drawShufflingKDE(progress);
    this.drawShufflingSamplePoints(progress);
    this.drawInfoCard();
    this.drawTitle();
  }

  drawTransitioningKDE(progress) {
    if (!this.oldKDE || !this.newKDE) return;
    
    const resolution = 300;
    const x = this.linspace(this.xMin, this.xMax, resolution);
    const ctx = this.ctx;
    const colors = this.getThemeColors();
    
    // Interpolate between old and new KDE
    const interpolatedKDE = this.oldKDE.map((oldVal, i) => {
      const newVal = this.newKDE[i] || 0;
      return oldVal + (newVal - oldVal) * progress;
    });
    
    // Draw the interpolated KDE
    ctx.fillStyle = colors.primary;
    ctx.globalAlpha = 0.3;
    ctx.strokeStyle = colors.primary;
    ctx.lineWidth = 2;
    
    ctx.beginPath();
    for (let i = 0; i < x.length; i++) {
      const px = this.xToPixel(x[i]);
      const py = this.yToPixel(interpolatedKDE[i]);
      
      if (i === 0) {
        ctx.moveTo(px, py);
      } else {
        ctx.lineTo(px, py);
      }
    }
    
    // Close path to baseline
    const baseY = this.padding.top + this.plotHeight;
    ctx.lineTo(this.xToPixel(x[x.length - 1]), baseY);
    ctx.lineTo(this.xToPixel(x[0]), baseY);
    ctx.closePath();
    ctx.fill();
    ctx.globalAlpha = 1.0;
    ctx.stroke();
  }

  getThemeColors() {
    if (this.currentTheme === 'dark') {
      return {
        primary: '#D0BCFF',
        onPrimary: '#381E72',
        primaryContainer: '#4F378B',
        onSurface: '#E6E0E9',
        onSurfaceVariant: '#CAC4D0',
        outline: '#938F99',
        outlineVariant: '#49454F',
        surface: '#1C1B1F',
        surfaceContainer: '#211F26',
        error: '#F2B8B5',
        background: '#141218'
      };
    } else {
      return {
        primary: '#6750A4',
        onPrimary: '#FFFFFF',
        primaryContainer: '#EADDFF',
        onSurface: '#1D1B20',
        onSurfaceVariant: '#49454F',
        outline: '#79747E',
        outlineVariant: '#CAC4D0',
        surface: '#FFFBFE',
        surfaceContainer: '#F3EDF7',
        error: '#B3261E',
        background: '#FEF7FF'
      };
    }
  }

  drawGrid() {
    const ctx = this.ctx;
    const colors = this.getThemeColors();
    
    ctx.strokeStyle = colors.outlineVariant;
    ctx.lineWidth = 0.5;
    
    // Horizontal grid lines
    for (let i = 0; i <= 5; i++) {
      const y = this.padding.top + (i / 5) * this.plotHeight;
      ctx.beginPath();
      ctx.moveTo(this.padding.left, y);
      ctx.lineTo(this.padding.left + this.plotWidth, y);
      ctx.stroke();
    }
    
    // Vertical grid lines
    for (let i = 0; i <= 10; i++) {
      const x = this.padding.left + (i / 10) * this.plotWidth;
      ctx.beginPath();
      ctx.moveTo(x, this.padding.top);
      ctx.lineTo(x, this.padding.top + this.plotHeight);
      ctx.stroke();
    }
  }

  drawAxes() {
    const ctx = this.ctx;
    const colors = this.getThemeColors();
    
    ctx.strokeStyle = colors.outline;
    ctx.lineWidth = 2;
    
    // X-axis
    ctx.beginPath();
    ctx.moveTo(this.padding.left, this.padding.top + this.plotHeight);
    ctx.lineTo(this.padding.left + this.plotWidth, this.padding.top + this.plotHeight);
    ctx.stroke();
    
    // Y-axis
    ctx.beginPath();
    ctx.moveTo(this.padding.left, this.padding.top);
    ctx.lineTo(this.padding.left, this.padding.top + this.plotHeight);
    ctx.stroke();
    
    // Axis labels
    ctx.fillStyle = colors.onSurfaceVariant;
    ctx.font = '14px Roboto, system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Value', this.padding.left + this.plotWidth / 2, this.canvasHeight - 20);
    
    ctx.save();
    ctx.translate(20, this.padding.top + this.plotHeight / 2);
    ctx.rotate(-Math.PI / 2);
    ctx.fillText('Density', 0, 0);
    ctx.restore();
    
    // Tick marks and labels
    ctx.font = '12px Roboto, system-ui, sans-serif';
    const numTicks = 5;
    for (let i = 0; i <= numTicks; i++) {
      // X-axis ticks
      const xVal = this.xMin + (i / numTicks) * this.xRange;
      const xPos = this.xToPixel(xVal);
      ctx.beginPath();
      ctx.moveTo(xPos, this.padding.top + this.plotHeight);
      ctx.lineTo(xPos, this.padding.top + this.plotHeight + 6);
      ctx.stroke();
      ctx.fillText(xVal.toFixed(1), xPos, this.padding.top + this.plotHeight + 20);
      
      // Y-axis ticks
      const yVal = (i / numTicks) * this.yMax;
      const yPos = this.yToPixel(yVal);
      ctx.beginPath();
      ctx.moveTo(this.padding.left - 6, yPos);
      ctx.lineTo(this.padding.left, yPos);
      ctx.stroke();
      ctx.textAlign = 'right';
      ctx.fillText(yVal.toFixed(2), this.padding.left - 10, yPos + 4);
      ctx.textAlign = 'center';
    }
  }

  drawTitle() {
    const ctx = this.ctx;
    const colors = this.getThemeColors();
    
    ctx.fillStyle = colors.onSurface;
    ctx.font = '500 18px Roboto, system-ui, sans-serif';
    ctx.textAlign = 'center';
    ctx.fillText('Gaussian Kernel Density Estimation', this.canvasWidth / 2, 30);
  }

  drawKDE() {
    const resolution = 300;
    const x = this.linspace(this.xMin, this.xMax, resolution);
    const colors = this.generateMaterialColors(this.nSamples);
    
    let cumulativeHeight = new Array(resolution).fill(0);
    
    // Draw each individual kernel stacked on top of each other
    for (let idx = 0; idx < this.data.length; idx++) {
      const kernel = x.map(xi => this.gaussian(xi, this.data[idx], this.bandwidth) / this.nSamples);
      this.drawFilledKernel(x, cumulativeHeight, kernel, colors[idx], 0.7);
      
      // Update cumulative height for next kernel
      for (let i = 0; i < resolution; i++) {
        cumulativeHeight[i] += kernel[i];
      }
    }
  }

  drawShufflingKDE(progress) {
    const resolution = 300;
    const x = this.linspace(this.xMin, this.xMax, resolution);
    const colors = this.generateMaterialColors(this.nSamples);
    
    // Interpolate bandwidth if we're resetting
    const currentBandwidth = this.targetXMin !== null ?
      this.bandwidth + (this.initialBandwidth - this.bandwidth) * progress :
      this.bandwidth;
    
    let cumulativeHeight = new Array(resolution).fill(0);
    
    // Draw each kernel transitioning from old to new position
    for (let idx = 0; idx < this.oldData.length; idx++) {
      // Interpolate between old and new data point positions
      const oldPos = this.oldData[idx];
      const newPos = this.newData[idx];
      const currentPos = oldPos + (newPos - oldPos) * progress;
      
      const kernel = x.map(xi => this.gaussian(xi, currentPos, currentBandwidth) / this.nSamples);
      this.drawFilledKernel(x, cumulativeHeight, kernel, colors[idx], 0.7);
      
      // Update cumulative height for next kernel
      for (let i = 0; i < resolution; i++) {
        cumulativeHeight[i] += kernel[i];
      }
    }
  }

  drawFilledKernel(x, baseline, kernel, color, alpha) {
    const ctx = this.ctx;
    const colors = this.getThemeColors();
    
    ctx.fillStyle = color;
    ctx.globalAlpha = alpha;
    ctx.strokeStyle = this.currentTheme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)';
    ctx.lineWidth = 0.5;
    
    ctx.beginPath();
    // Draw baseline path
    for (let i = 0; i < x.length; i++) {
      const px = this.xToPixel(x[i]);
      const py1 = this.yToPixel(baseline[i]);
      
      if (i === 0) {
        ctx.moveTo(px, py1);
      } else {
        ctx.lineTo(px, py1);
      }
    }
    
    // Draw top path (baseline + kernel)
    for (let i = x.length - 1; i >= 0; i--) {
      const px = this.xToPixel(x[i]);
      const py2 = this.yToPixel(baseline[i] + kernel[i]);
      ctx.lineTo(px, py2);
    }
    
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    ctx.globalAlpha = 1.0;
  }

  generateMaterialColors(n) {
    // Material Design 3 inspired color palette
    const lightPalette = [
      '#6750A4', '#7D5260', '#815610', '#006C51', '#00629E',
      '#984061', '#00687A', '#8B5000', '#4C662B', '#D62114'
    ];
    
    const darkPalette = [
      '#D0BCFF', '#EFB8C8', '#FFB951', '#52DCC0', '#83D0FF',
      '#FFB1C8', '#4DD9E8', '#FFB86E', '#BDD99B', '#FFB4A9'
    ];
    
    const palette = this.currentTheme === 'dark' ? darkPalette : lightPalette;
    
    return Array.from({ length: n }, (_, i) => {
      return palette[i % palette.length];
    });
  }

  drawFilledKernel(x, baseline, kernel, color, alpha) {
    const ctx = this.ctx;
    const colors = this.getThemeColors();
    
    ctx.fillStyle = color;
    ctx.globalAlpha = alpha * 0.7;
    ctx.strokeStyle = this.currentTheme === 'dark' ? 'rgba(255,255,255,0.1)' : 'rgba(0,0,0,0.05)';
    ctx.lineWidth = 0.5;
    
    ctx.beginPath();
    for (let i = 0; i < x.length; i++) {
      const px = this.xToPixel(x[i]);
      const py1 = this.yToPixel(baseline[i]);
      
      if (i === 0) {
        ctx.moveTo(px, py1);
      } else {
        ctx.lineTo(px, py1);
      }
    }
    
    for (let i = x.length - 1; i >= 0; i--) {
      const px = this.xToPixel(x[i]);
      const py2 = this.yToPixel(baseline[i] + kernel[i]);
      ctx.lineTo(px, py2);
    }
    
    ctx.closePath();
    ctx.fill();
    ctx.stroke();
    ctx.globalAlpha = 1.0;
  }

  drawSamplePoints() {
    const ctx = this.ctx;
    const colors = this.getThemeColors();
    
    for (let i = 0; i < this.data.length; i++) {
      const px = this.xToPixel(this.data[i]);
      const py = this.padding.top + this.plotHeight;
      const isDragged = (i === this.draggedPointIndex && this.isDragging);
      
      // Draw point marker with highlight for dragged point
      ctx.beginPath();
      const radius = isDragged ? 6 : 4;
      ctx.arc(px, py + 15, radius, 0, 2 * Math.PI);
      ctx.fillStyle = isDragged ? colors.error : colors.primary;
      
      if (isDragged) {
        ctx.shadowColor = colors.error;
        ctx.shadowBlur = 8;
        ctx.shadowOffsetY = 0;
      }
      
      ctx.fill();
      
      ctx.shadowColor = 'transparent';
      ctx.shadowBlur = 0;
      
      // Draw tick line
      ctx.beginPath();
      ctx.moveTo(px, py);
      ctx.lineTo(px, py + 10);
      ctx.lineWidth = isDragged ? 3 : 2;
      ctx.strokeStyle = isDragged ? colors.error : colors.primary;
      ctx.stroke();
    }
  }

  drawShufflingSamplePoints(progress) {
    const ctx = this.ctx;
    const colors = this.getThemeColors();
    const py = this.padding.top + this.plotHeight;
    
    for (let i = 0; i < this.oldData.length; i++) {
      // Interpolate position
      const oldPos = this.oldData[i];
      const newPos = this.newData[i];
      const currentPos = oldPos + (newPos - oldPos) * progress;
      const px = this.xToPixel(currentPos);
      
      // Draw point marker
      ctx.beginPath();
      ctx.arc(px, py + 15, 4, 0, 2 * Math.PI);
      ctx.fillStyle = colors.primary;
      ctx.fill();
      
      // Draw tick line
      ctx.beginPath();
      ctx.moveTo(px, py);
      ctx.lineTo(px, py + 10);
      ctx.lineWidth = 2;
      ctx.strokeStyle = colors.primary;
      ctx.stroke();
    }
  }

  drawInfoCard() {
    const ctx = this.ctx;
    const colors = this.getThemeColors();
    
    // Card background
    const boxX = this.padding.left + 16;
    const boxY = this.padding.top + 16;
    const boxWidth = 220;
    const boxHeight = 50;
    const borderRadius = 12;
    
    // Draw elevated card
    ctx.shadowColor = 'rgba(0, 0, 0, 0.2)';
    ctx.shadowBlur = 8;
    ctx.shadowOffsetY = 2;
    
    ctx.fillStyle = colors.surfaceContainer;
    ctx.beginPath();
    this.roundRect(ctx, boxX, boxY, boxWidth, boxHeight, borderRadius);
    ctx.fill();
    
    ctx.shadowColor = 'transparent';
    ctx.shadowBlur = 0;
    ctx.shadowOffsetY = 0;
    
    // Border
    ctx.strokeStyle = colors.outlineVariant;
    ctx.lineWidth = 1;
    ctx.stroke();
    
    // Text content
    ctx.fillStyle = colors.onSurface;
    ctx.font = '500 14px Roboto, system-ui, sans-serif';
    ctx.textAlign = 'left';
    ctx.fillText('KDE Parameters', boxX + 16, boxY + 24);
    
    ctx.font = '400 13px Roboto, system-ui, sans-serif';
    ctx.fillStyle = colors.onSurfaceVariant;
    ctx.fillText(`Bandwidth: ${this.bandwidth.toFixed(3)}`, boxX + 16, boxY + 41);
  }

  roundRect(ctx, x, y, width, height, radius) {
    ctx.moveTo(x + radius, y);
    ctx.arcTo(x + width, y, x + width, y + height, radius);
    ctx.arcTo(x + width, y + height, x, y + height, radius);
    ctx.arcTo(x, y + height, x, y, radius);
    ctx.arcTo(x, y, x + width, y, radius);
  }

  gaussian(x, mean, std) {
    const variance = std * std;
    return (1 / Math.sqrt(2 * Math.PI * variance)) * Math.exp(-Math.pow(x - mean, 2) / (2 * variance));
  }

  linspace(start, end, num) {
    const step = (end - start) / (num - 1);
    return Array.from({ length: num }, (_, i) => start + i * step);
  }

  xToPixel(x) {
    return this.padding.left + ((x - this.xMin) / this.xRange) * this.plotWidth;
  }

  yToPixel(y) {
    return this.padding.top + this.plotHeight - (y / this.yMax) * this.plotHeight;
  }

  getMousePos(e) {
    const rect = this.canvas.getBoundingClientRect();
    return {
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    };
  }

  getTouchPos(e) {
    const rect = this.canvas.getBoundingClientRect();
    const touch = e.touches[0];
    return {
      x: touch.clientX - rect.left,
      y: touch.clientY - rect.top
    };
  }

  findPointAtPosition(pos) {
    const py = this.padding.top + this.plotHeight + 15;
    const clickRadius = 15;
    
    for (let i = 0; i < this.data.length; i++) {
      const px = this.xToPixel(this.data[i]);
      const distance = Math.sqrt(Math.pow(pos.x - px, 2) + Math.pow(pos.y - py, 2));
      
      if (distance <= clickRadius) {
        return i;
      }
    }
    return -1;
  }

  handleMouseDown(e) {
    if (this.isTransitioning || this.isShuffling) return;
    
    const pos = this.getMousePos(e);
    const pointIndex = this.findPointAtPosition(pos);
    
    if (pointIndex !== -1) {
      this.isDragging = true;
      this.draggedPointIndex = pointIndex;
      this.canvas.style.cursor = 'grabbing';
    }
  }

  handleMouseMove(e) {
    const pos = this.getMousePos(e);
    
    if (this.isDragging && this.draggedPointIndex !== -1) {
      // Convert pixel position to data value
      const dataValue = this.pixelToX(pos.x);
      this.data[this.draggedPointIndex] = dataValue;
      
      // Recalculate bandwidth only in auto mode
      if (this.autoBandwidth) {
        this.bandwidth = this.calculateBandwidth();
        this.manualBandwidth = this.bandwidth;
        this.updateBandwidthControls();
      }
      this.updateCoordinateSystem();
      this.drawFrame();
    } else if (!this.isTransitioning && !this.isShuffling) {
      // Update cursor when hovering over points
      const pointIndex = this.findPointAtPosition(pos);
      this.canvas.style.cursor = pointIndex !== -1 ? 'grab' : 'default';
    }
  }

  handleMouseUp(e) {
    if (this.isDragging) {
      this.isDragging = false;
      this.draggedPointIndex = -1;
      this.canvas.style.cursor = 'default';
    }
  }

  handleTouchStart(e) {
    e.preventDefault();
    if (this.isTransitioning || this.isShuffling) return;
    
    const pos = this.getTouchPos(e);
    const pointIndex = this.findPointAtPosition(pos);
    
    if (pointIndex !== -1) {
      this.isDragging = true;
      this.draggedPointIndex = pointIndex;
    }
  }

  handleTouchMove(e) {
    e.preventDefault();
    if (this.isDragging && this.draggedPointIndex !== -1) {
      const pos = this.getTouchPos(e);
      const dataValue = this.pixelToX(pos.x);
      this.data[this.draggedPointIndex] = dataValue;
      
      // Recalculate bandwidth only in auto mode
      if (this.autoBandwidth) {
        this.bandwidth = this.calculateBandwidth();
        this.manualBandwidth = this.bandwidth;
        this.updateBandwidthControls();
      }
      this.updateCoordinateSystem();
      this.drawFrame();
    }
  }

  handleTouchEnd(e) {
    e.preventDefault();
    if (this.isDragging) {
      this.isDragging = false;
      this.draggedPointIndex = -1;
    }
  }

  pixelToX(px) {
    return this.xMin + ((px - this.padding.left) / this.plotWidth) * this.xRange;
  }

  render() {
    const width = this.getAttribute('width') || '800';
    const height = this.getAttribute('height') || '500';
    
    this.shadowRoot.innerHTML = `
      <style>
        :host {
          display: block;
          font-family: 'Roboto', system-ui, -apple-system, sans-serif;
          --md-elevation-1: 0px 1px 2px rgba(0, 0, 0, 0.3), 0px 1px 3px 1px rgba(0, 0, 0, 0.15);
          --md-elevation-2: 0px 1px 2px rgba(0, 0, 0, 0.3), 0px 2px 6px 2px rgba(0, 0, 0, 0.15);
        }

        :host([data-theme="light"]) {
          --surface: #FFFBFE;
          --on-surface: #1D1B20;
          --surface-container: #F3EDF7;
          --primary: #6750A4;
          --on-primary: #FFFFFF;
          --outline: #79747E;
          --outline-variant: #CAC4D0;
        }

        :host([data-theme="dark"]) {
          --surface: #1C1B1F;
          --on-surface: #E6E0E9;
          --surface-container: #211F26;
          --primary: #D0BCFF;
          --on-primary: #381E72;
          --outline: #938F99;
          --outline-variant: #49454F;
        }
        
        .container {
          background: var(--surface);
          border-radius: 16px;
          padding: 24px;
          box-shadow: var(--md-elevation-1);
          transition: background-color 0.3s cubic-bezier(0.4, 0, 0.2, 1),
                      box-shadow 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        canvas {
          display: block;
          width: 100%;
          border-radius: 12px;
          background: var(--surface);
          margin-bottom: 20px;
          touch-action: none;
        }
        
        .sample-controls {
          display: flex;
          gap: 12px;
          align-items: center;
          justify-content: center;
          padding: 12px 16px;
          background: var(--surface-container);
          border-radius: 12px;
          border: 1px solid var(--outline-variant);
        }

        .sample-controls label {
          font-size: 14px;
          color: var(--on-surface);
          font-weight: 500;
          margin-right: 8px;
        }

        .icon-btn {
          display: inline-flex;
          align-items: center;
          justify-content: center;
          background: var(--primary);
          color: var(--on-primary);
          border: none;
          padding: 8px;
          border-radius: 50%;
          cursor: pointer;
          font-family: 'Roboto', system-ui, sans-serif;
          transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
          box-shadow: var(--md-elevation-1);
          width: 36px;
          height: 36px;
        }

        .icon-btn:hover {
          box-shadow: var(--md-elevation-2);
          transform: scale(1.05);
        }

        .icon-btn:active {
          transform: scale(0.95);
        }

        .shuffle-btn {
          margin-left: 8px;
        }

        .sort-btn {
          margin-left: 4px;
        }

        .reset-btn {
          margin-left: 8px;
        }
        
        .bandwidth-controls {
          display: flex;
          gap: 12px;
          align-items: center;
          justify-content: center;
          padding: 12px 16px;
          background: var(--surface-container);
          border-radius: 12px;
          border: 1px solid var(--outline-variant);
          margin-top: 12px;
        }
        
        .bandwidth-controls label {
          font-size: 14px;
          color: var(--on-surface);
          font-weight: 500;
        }
        
        .toggle-container {
          display: flex;
          align-items: center;
          gap: 8px;
        }
        
        .toggle-switch {
          position: relative;
          width: 44px;
          height: 24px;
        }
        
        .toggle-switch input {
          opacity: 0;
          width: 0;
          height: 0;
        }
        
        .toggle-slider {
          position: absolute;
          cursor: pointer;
          top: 0;
          left: 0;
          right: 0;
          bottom: 0;
          background-color: var(--outline-variant);
          transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          border-radius: 12px;
        }
        
        .toggle-slider:before {
          position: absolute;
          content: "";
          height: 16px;
          width: 16px;
          left: 4px;
          bottom: 4px;
          background-color: var(--surface);
          transition: 0.3s cubic-bezier(0.4, 0, 0.2, 1);
          border-radius: 50%;
        }
        
        input:checked + .toggle-slider {
          background-color: var(--primary);
        }
        
        input:checked + .toggle-slider:before {
          transform: translateX(20px);
        }
        
        .bandwidth-slider-container {
          display: flex;
          align-items: center;
          gap: 12px;
          flex: 1;
          max-width: 400px;
          transition: opacity 0.3s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .bandwidth-slider {
          flex: 1;
          height: 4px;
          border-radius: 2px;
          background: var(--outline-variant);
          outline: none;
          -webkit-appearance: none;
          appearance: none;
        }
        
        .bandwidth-slider::-webkit-slider-thumb {
          -webkit-appearance: none;
          appearance: none;
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: var(--primary);
          cursor: pointer;
          box-shadow: var(--md-elevation-1);
          transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .bandwidth-slider::-webkit-slider-thumb:hover {
          transform: scale(1.1);
          box-shadow: var(--md-elevation-2);
        }
        
        .bandwidth-slider::-moz-range-thumb {
          width: 20px;
          height: 20px;
          border-radius: 50%;
          background: var(--primary);
          cursor: pointer;
          border: none;
          box-shadow: var(--md-elevation-1);
          transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1);
        }
        
        .bandwidth-slider::-moz-range-thumb:hover {
          transform: scale(1.1);
          box-shadow: var(--md-elevation-2);
        }
        
        .bandwidth-value {
          font-size: 14px;
          color: var(--on-surface);
          font-weight: 500;
          min-width: 50px;
          text-align: right;
        }
      </style>
      
      <div class="container">
        <canvas id="canvas"></canvas>
        <div class="sample-controls">
          <label>Samples: <span id="sampleCount"></span></label>
          <button id="removeBtn" class="icon-btn">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M19 13H5v-2h14v2z"/>
            </svg>
          </button>
          <button id="addBtn" class="icon-btn">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M19 13h-6v6h-2v-6H5v-2h6V5h2v6h6v2z"/>
            </svg>
          </button>
          <button id="shuffleBtn" class="icon-btn shuffle-btn">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M10.59 9.17L5.41 4 4 5.41l5.17 5.17 1.42-1.41zM14.5 4l2.04 2.04L4 18.59 5.41 20 17.96 7.46 20 9.5V4h-5.5zm.33 9.41l-1.41 1.41 3.13 3.13L14.5 20H20v-5.5l-2.04 2.04-3.13-3.13z"/>
            </svg>
          </button>
          <button id="sortAscBtn" class="icon-btn sort-btn" title="Sort Left to Right">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M3 18h6v-2H3v2zM3 6v2h18V6H3zm0 7h12v-2H3v2z"/>
            </svg>
          </button>
          <button id="sortDescBtn" class="icon-btn sort-btn" title="Sort Right to Left">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M3 18h18v-2H3v2zM3 6v2h12V6H3zm0 7h6v-2H3v2z"/>
            </svg>
          </button>
          <button id="resetBtn" class="icon-btn reset-btn" title="Reset to Initial State">
            <svg viewBox="0 0 24 24" width="20" height="20" fill="currentColor">
              <path d="M12 5V1L7 6l5 5V7c3.31 0 6 2.69 6 6s-2.69 6-6 6-6-2.69-6-6H4c0 4.42 3.58 8 8 8s8-3.58 8-8-3.58-8-8-8z"/>
            </svg>
          </button>
        </div>
        <div class="bandwidth-controls">
          <label>Bandwidth:</label>
          <div class="toggle-container">
            <span style="font-size: 12px; color: var(--on-surface);">Auto</span>
            <label class="toggle-switch">
              <input type="checkbox" id="bandwidthToggle">
              <span class="toggle-slider"></span>
            </label>
            <span style="font-size: 12px; color: var(--on-surface);">Manual</span>
          </div>
          <div class="bandwidth-slider-container">
            <input type="range" id="bandwidthSlider" class="bandwidth-slider" 
                   min="0.1" max="2.0" step="0.01" value="0.5">
            <span class="bandwidth-value" id="bandwidthValue">0.500</span>
          </div>
        </div>
      </div>
    `;
  }
}

// Register the custom element
customElements.define('gaussian-kde-visualizer', GaussianKDEVisualizer);
