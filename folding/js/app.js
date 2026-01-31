/**
 * Main application entry point for the folding engine
 * Initializes the controller and wires up UI elements
 */

import { FoldingController } from './controller.js';
import { getDefaultFolds } from './folds.js';

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
    const controller = new FoldingController({
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
        progressText: document.getElementById('progress-text')
    });
    
    // Setup slider event
    const masterSlider = document.getElementById('master-slider');
    if (masterSlider) {
        masterSlider.addEventListener('input', (e) => {
            controller.applyPlayState(parseFloat(e.target.value));
        });
    }
    
    // Initialize
    controller.init();
    
    // Expose global functions for HTML onclick handlers
    window.switchMode = (mode) => controller.switchMode(mode);
    window.addFold = (type) => controller.addFold(type);
    window.removeFold = (index) => controller.removeFold(index);
    window.updateFoldAngle = (index, val) => controller.updateFoldAngle(index, parseInt(val));
    window.animateTo = (percent) => controller.animateTo(percent);
    
    // Initialize Lucide icons if available
    try { 
        if (typeof lucide !== 'undefined') lucide.createIcons(); 
    } catch(e) { 
        console.warn('Lucide icons not available'); 
    }
    
    return controller;
}

// Auto-initialize when DOM is ready if this is the main script
if (typeof document !== 'undefined' && document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initFoldingApp);
} else if (typeof document !== 'undefined') {
    // DOM already loaded
    initFoldingApp();
}
