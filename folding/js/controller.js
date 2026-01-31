/**
 * UI Controller for the folding engine
 * Manages application state, mode switching, and user interactions
 */

import { easeInOutCubic, MAX_FOLD_ANGLE } from './math.js';
import { createFold, getFoldLabel, FOLD_DIRECTION, ORIGAMI_PRESETS, loadPreset, getPresetNames } from './folds.js';
import { FoldingRenderer, updateTurntable } from './renderer.js';

/**
 * Controller class for the folding application
 */
export class FoldingController {
    /**
     * @param {Object} options - Configuration options
     * @param {HTMLElement} options.rootElement - Paper root element
     * @param {HTMLElement} options.turntable - Turntable element
     * @param {HTMLElement} options.sceneContainer - Scene container element
     * @param {number} options.paperSize - Size of paper in pixels
     * @param {Object[]} options.initialFolds - Initial fold sequence
     */
    constructor(options) {
        this.paperSize = options.paperSize || 300;
        this.folds = options.initialFolds || [];
        this.appMode = 'config';
        this.viewRotation = { x: 30, y: 0 };
        this.isDragging = false;
        this.lastMouse = { x: 0, y: 0 };
        
        // DOM elements
        this.turntable = options.turntable;
        this.sceneContainer = options.sceneContainer;
        
        // Create renderer
        this.renderer = new FoldingRenderer(options.rootElement, this.paperSize);
        
        // UI elements (set later via setUIElements)
        this.uiElements = {};
        
        // Callbacks
        this.onFoldsChange = null;
    }

    /**
     * Set UI element references
     * @param {Object} elements - UI element references
     */
    setUIElements(elements) {
        this.uiElements = elements;
    }

    /**
     * Initialize the controller
     */
    init() {
        this.setupMouseInteraction();
        this.switchMode('config');
        updateTurntable(this.turntable, this.viewRotation);
    }

    /**
     * Setup mouse interaction for scene rotation
     */
    setupMouseInteraction() {
        this.sceneContainer.addEventListener('mousedown', (e) => {
            this.isDragging = true;
            this.lastMouse = { x: e.clientX, y: e.clientY };
        });

        window.addEventListener('mouseup', () => {
            this.isDragging = false;
        });

        window.addEventListener('mousemove', (e) => {
            if (!this.isDragging) return;
            
            const dx = e.clientX - this.lastMouse.x;
            const dy = e.clientY - this.lastMouse.y;
            this.lastMouse = { x: e.clientX, y: e.clientY };

            this.viewRotation.y += dx * 0.5;
            this.viewRotation.x -= dy * 0.5;
            this.viewRotation.x = Math.max(-80, Math.min(80, this.viewRotation.x));

            updateTurntable(this.turntable, this.viewRotation);
        });
    }

    /**
     * Switch application mode
     * @param {string} mode - 'config' or 'play'
     */
    switchMode(mode) {
        this.appMode = mode;
        
        // Update UI toggle buttons
        if (this.uiElements.btnModeConfig) {
            this.uiElements.btnModeConfig.classList.toggle('active', mode === 'config');
        }
        if (this.uiElements.btnModePlay) {
            this.uiElements.btnModePlay.classList.toggle('active', mode === 'play');
        }

        // Toggle panels
        if (this.uiElements.configDrawer) {
            this.uiElements.configDrawer.classList.toggle('open', mode === 'config');
        }
        if (this.uiElements.playBar) {
            this.uiElements.playBar.classList.toggle('visible', mode === 'play');
        }
        
        if (mode === 'config') {
            this.applyConfigState();
        } else {
            if (this.uiElements.masterSlider) {
                this.uiElements.masterSlider.value = 0;
                this.uiElements.masterSlider.max = this.folds.length * 100;
            }
            this.applyPlayState(0);
        }
    }

    /**
     * Apply config state - show all folds at target angles
     */
    applyConfigState() {
        this.folds.forEach(f => f.currentAngle = f.targetAngle);
        this.renderer.render(this.folds);
        this.renderFoldList();
    }

    /**
     * Apply play state - interpolate folds based on progress
     * @param {number} progressRaw - Progress value (0 to folds.length * 100)
     */
    applyPlayState(progressRaw) {
        const totalProgress = progressRaw / 100;

        this.folds.forEach((f, i) => {
            let localT = Math.max(0, Math.min(1, totalProgress - i));
            localT = easeInOutCubic(localT);
            f.currentAngle = localT * f.targetAngle;
        });
        
        const progressPercent = this.folds.length > 0 
            ? Math.floor(totalProgress * 100 / this.folds.length) 
            : 0;
        
        if (this.uiElements.progressText) {
            this.uiElements.progressText.innerText = `Sequence: ${progressPercent}%`;
        }
        
        this.renderer.render(this.folds);
    }

    /**
     * Render the fold list in the config drawer
     */
    renderFoldList() {
        const container = this.uiElements.foldList;
        if (!container) return;
        
        container.innerHTML = '';
        
        if (this.uiElements.stepCount) {
            this.uiElements.stepCount.innerText = `${this.folds.length} steps`;
        }

        this.folds.forEach((fold, index) => {
            const el = document.createElement('div');
            el.className = 'fold-item';
            
            const label = getFoldLabel(fold.type);
            const position = fold.position !== undefined ? fold.position : 50;
            const direction = fold.direction || FOLD_DIRECTION.MOUNTAIN;
            const directionIcon = direction === FOLD_DIRECTION.MOUNTAIN ? '⛰️' : '🏔️';

            el.innerHTML = `
                <div class="fold-item-header">
                    <span>${index + 1}. ${label} ${directionIcon}</span>
                    <span class="btn-delete" data-index="${index}">🗑️</span>
                </div>
                <div class="fold-controls">
                    <div class="fold-control-row">
                        <label class="control-label">Angle</label>
                        <input type="range" min="0" max="${MAX_FOLD_ANGLE}" value="${fold.targetAngle}" 
                               data-index="${index}" class="fold-angle-slider">
                        <span class="control-value">${fold.targetAngle}°</span>
                    </div>
                    <div class="fold-control-row">
                        <label class="control-label">Position</label>
                        <input type="range" min="10" max="90" value="${position}" 
                               data-index="${index}" class="fold-position-slider">
                        <span class="control-value">${position}%</span>
                    </div>
                    <div class="fold-control-row">
                        <label class="control-label">Direction</label>
                        <select data-index="${index}" class="fold-direction-select">
                            <option value="mountain" ${direction === FOLD_DIRECTION.MOUNTAIN ? 'selected' : ''}>⛰️ Mountain</option>
                            <option value="valley" ${direction === FOLD_DIRECTION.VALLEY ? 'selected' : ''}>🏔️ Valley</option>
                        </select>
                    </div>
                </div>
            `;
            
            // Attach event listeners
            el.querySelector('.btn-delete').addEventListener('click', () => {
                this.removeFold(index);
            });
            
            el.querySelector('.fold-angle-slider').addEventListener('input', (e) => {
                this.updateFoldAngle(index, parseInt(e.target.value));
            });
            
            el.querySelector('.fold-position-slider').addEventListener('input', (e) => {
                this.updateFoldPosition(index, parseInt(e.target.value));
            });
            
            el.querySelector('.fold-direction-select').addEventListener('change', (e) => {
                this.updateFoldDirection(index, e.target.value);
            });
            
            container.appendChild(el);
        });

        // Try to update lucide icons if available
        try { 
            if (typeof lucide !== 'undefined') lucide.createIcons(); 
        } catch(e) {
            // Icon loading is optional, log for debugging only
        }
    }

    /**
     * Add a new fold
     * @param {string} type - Fold type
     */
    addFold(type) {
        this.folds.push(createFold(type, 135, 50, FOLD_DIRECTION.MOUNTAIN));
        if (this.appMode === 'config') {
            this.applyConfigState();
        }
        if (this.onFoldsChange) this.onFoldsChange(this.folds);
    }

    /**
     * Remove a fold
     * @param {number} index - Index of fold to remove
     */
    removeFold(index) {
        this.folds.splice(index, 1);
        if (this.appMode === 'config') {
            this.applyConfigState();
        }
        if (this.onFoldsChange) this.onFoldsChange(this.folds);
    }

    /**
     * Update fold angle
     * @param {number} index - Fold index
     * @param {number} angle - New angle value
     */
    updateFoldAngle(index, angle) {
        this.folds[index].targetAngle = angle;
        this.folds[index].currentAngle = angle;
        this.renderer.render(this.folds);
        this.renderFoldList();
        if (this.onFoldsChange) this.onFoldsChange(this.folds);
    }

    /**
     * Update fold position
     * @param {number} index - Fold index
     * @param {number} position - New position value (0-100%)
     */
    updateFoldPosition(index, position) {
        this.folds[index].position = position;
        this.renderer.render(this.folds);
        this.renderFoldList();
        if (this.onFoldsChange) this.onFoldsChange(this.folds);
    }

    /**
     * Update fold direction
     * @param {number} index - Fold index
     * @param {string} direction - New direction ('mountain' or 'valley')
     */
    updateFoldDirection(index, direction) {
        this.folds[index].direction = direction;
        this.renderer.render(this.folds);
        this.renderFoldList();
        if (this.onFoldsChange) this.onFoldsChange(this.folds);
    }

    /**
     * Load a preset pattern
     * @param {string} presetName - Name of the preset to load
     */
    loadPreset(presetName) {
        const folds = loadPreset(presetName);
        this.folds = folds;
        if (this.appMode === 'config') {
            this.applyConfigState();
        }
        if (this.onFoldsChange) this.onFoldsChange(this.folds);
    }

    /**
     * Get available preset names
     * @returns {string[]} Array of preset names
     */
    getPresetNames() {
        return getPresetNames();
    }

    /**
     * Get preset info
     * @param {string} name - Preset name
     * @returns {Object} Preset info
     */
    getPresetInfo(name) {
        return ORIGAMI_PRESETS[name];
    }

    /**
     * Export current folds as JSON
     * @returns {string} JSON string of current folds
     */
    exportFolds() {
        return JSON.stringify({
            version: 1,
            name: 'Custom Pattern',
            folds: this.folds.map(f => ({
                type: f.type,
                targetAngle: f.targetAngle,
                position: f.position || 50,
                direction: f.direction || FOLD_DIRECTION.MOUNTAIN
            }))
        }, null, 2);
    }

    /**
     * Import folds from JSON
     * @param {string} jsonString - JSON string to import
     * @returns {boolean} Success status
     */
    importFolds(jsonString) {
        try {
            const data = JSON.parse(jsonString);
            if (!data.folds || !Array.isArray(data.folds)) {
                return false;
            }
            
            this.folds = data.folds.map((f, i) => ({
                id: Date.now() + i,
                type: f.type,
                targetAngle: f.targetAngle,
                currentAngle: 0,
                position: f.position || 50,
                direction: f.direction || FOLD_DIRECTION.MOUNTAIN
            }));
            
            if (this.appMode === 'config') {
                this.applyConfigState();
            }
            if (this.onFoldsChange) this.onFoldsChange(this.folds);
            return true;
        } catch (e) {
            console.error('Failed to import folds:', e);
            return false;
        }
    }

    /**
     * Toggle crease pattern visibility
     * @param {boolean} visible - Whether to show crease pattern
     */
    setCreasePatternVisible(visible) {
        this.renderer.setCreasePatternVisible(visible);
        this.renderer.render(this.folds);
    }

    /**
     * Animate to a target progress
     * @param {number} targetPercent - Target percentage (0 or 100)
     */
    animateTo(targetPercent) {
        const slider = this.uiElements.masterSlider;
        if (!slider) return;
        
        const start = parseFloat(slider.value);
        const end = targetPercent === 100 ? this.folds.length * 100 : 0;
        const duration = 1000;
        const startTime = performance.now();

        const step = (now) => {
            const elapsed = now - startTime;
            const t = Math.min(1, elapsed / duration);
            const smoothT = 1 - Math.pow(1 - t, 3);
            
            const current = start + (end - start) * smoothT;
            slider.value = current;
            this.applyPlayState(current);

            if (t < 1) requestAnimationFrame(step);
        };
        
        requestAnimationFrame(step);
    }

    /**
     * Get current folds
     * @returns {Object[]} Current fold array
     */
    getFolds() {
        return this.folds;
    }

    /**
     * Set folds
     * @param {Object[]} folds - New fold array
     */
    setFolds(folds) {
        this.folds = folds;
        if (this.appMode === 'config') {
            this.applyConfigState();
        }
    }
}
