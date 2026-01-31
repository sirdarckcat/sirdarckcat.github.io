/**
 * Main application entry point for the Origami Simulator
 * Initializes the controller and wires up UI elements
 */

import { FoldingController } from './controller.js';
import { getDefaultFolds, ORIGAMI_PRESETS } from './folds.js';

// Global controller reference
let controller = null;

/**
 * Initialize the folding application
 * @returns {FoldingController} The initialized controller
 */
export function initFoldingApp() {
    // Get DOM elements
    const rootElement = document.getElementById('paper-root');
    const turntable = document.getElementById('turntable');
    const sceneContainer = document.getElementById('scene-container');
    
    // Create controller
    controller = new FoldingController({
        rootElement,
        turntable,
        sceneContainer,
        paperSize: 300,
        initialFolds: getDefaultFolds()
    });
    
    // Set UI elements
    controller.setUIElements({
        btnModeConfig: document.getElementById('btn-mode-config'),
        btnModePlay: document.getElementById('btn-mode-play'),
        configDrawer: document.getElementById('config-drawer'),
        playBar: document.getElementById('play-bar'),
        foldList: document.getElementById('fold-list'),
        stepCount: document.getElementById('step-count'),
        masterSlider: document.getElementById('master-slider'),
        progressText: document.getElementById('progress-text'),
        presetSelector: document.getElementById('preset-selector')
    });
    
    // Setup slider event
    const masterSlider = document.getElementById('master-slider');
    if (masterSlider) {
        masterSlider.addEventListener('input', (e) => {
            controller.applyPlayState(parseFloat(e.target.value));
        });
    }
    
    // Populate preset selector
    populatePresetSelector();
    
    // Initialize
    controller.init();
    
    // Expose global functions for HTML onclick handlers
    window.switchMode = (mode) => controller.switchMode(mode);
    window.addFold = (type) => controller.addFold(type);
    window.removeFold = (index) => controller.removeFold(index);
    window.updateFoldAngle = (index, val) => controller.updateFoldAngle(index, parseInt(val));
    window.animateTo = (percent) => controller.animateTo(percent);
    window.loadSelectedPreset = loadSelectedPreset;
    window.exportPattern = exportPattern;
    window.importPattern = importPattern;
    
    // Initialize Lucide icons if available
    try { 
        if (typeof lucide !== 'undefined') lucide.createIcons(); 
    } catch(e) { 
        console.warn('Lucide icons not available'); 
    }
    
    return controller;
}

/**
 * Populate the preset selector dropdown
 */
function populatePresetSelector() {
    const selector = document.getElementById('preset-selector');
    if (!selector) return;
    
    // Clear existing options except the first
    selector.innerHTML = '<option value="">-- Select a pattern --</option>';
    
    // Add presets
    for (const [key, preset] of Object.entries(ORIGAMI_PRESETS)) {
        const option = document.createElement('option');
        option.value = key;
        option.textContent = `${preset.name}`;
        option.title = preset.description;
        selector.appendChild(option);
    }
}

/**
 * Load the selected preset from the dropdown
 */
function loadSelectedPreset() {
    const selector = document.getElementById('preset-selector');
    if (!selector || !controller) return;
    
    const presetName = selector.value;
    if (presetName) {
        controller.loadPreset(presetName);
        // Switch to config mode to see the result
        controller.switchMode('config');
    }
}

/**
 * Export current pattern as JSON
 */
function exportPattern() {
    if (!controller) return;
    
    const json = controller.exportFolds();
    
    // Create download link
    const blob = new Blob([json], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'origami-pattern.json';
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
}

/**
 * Import pattern from JSON file
 */
function importPattern() {
    if (!controller) return;
    
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.json';
    
    input.onchange = (e) => {
        const file = e.target.files[0];
        if (!file) return;
        
        const reader = new FileReader();
        reader.onload = (event) => {
            const success = controller.importFolds(event.target.result);
            if (!success) {
                alert('Failed to import pattern. Please check the file format.');
            }
        };
        reader.readAsText(file);
    };
    
    input.click();
}

// Auto-initialize when DOM is ready if this is the main script
if (typeof document !== 'undefined' && document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFoldingApp);
} else if (typeof document !== 'undefined') {
    // DOM already loaded
    initFoldingApp();
}
