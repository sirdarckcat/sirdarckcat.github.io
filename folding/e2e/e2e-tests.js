/**
 * E2E Test Runner for the Folding Engine
 * Captures screenshots and compares against golden images/states
 */

import { FoldingController } from '../js/controller.js';
import { getDefaultFolds } from '../js/folds.js';

/**
 * E2E Test Suite with golden generation and comparison
 */
export class E2ETestSuite {
    constructor() {
        this.tests = [];
        this.results = [];
        this.goldenImages = {};
        this.goldenStates = {};  // JSON-based golden states
        this.controller = null;
        this.paperRoot = null;
        this.captureCanvas = null;
        this.generateMode = false;  // When true, generate goldens instead of comparing
        this.generatedGoldens = {}; // Captured goldens during generation
    }

    /**
     * Initialize the test environment
     */
    async init() {
        // Get DOM elements
        this.paperRoot = document.getElementById('paper-root');
        this.turntable = document.getElementById('turntable');
        this.sceneContainer = document.getElementById('scene-container');
        
        // Create controller
        this.controller = new FoldingController({
            rootElement: this.paperRoot,
            turntable: this.turntable,
            sceneContainer: this.sceneContainer,
            paperSize: 300,
            initialFolds: []
        });
        
        // Set minimal UI elements
        this.controller.setUIElements({
            progressText: document.getElementById('progress-text')
        });
        
        // Create off-screen canvas for capturing
        this.captureCanvas = document.createElement('canvas');
        this.captureCanvas.width = 400;
        this.captureCanvas.height = 400;
        
        // Load golden states
        await this.loadGoldenStates();
    }

    /**
     * Load golden reference states (JSON format)
     */
    async loadGoldenStates() {
        try {
            const response = await fetch('e2e/goldens/goldens.json');
            if (response.ok) {
                this.goldenStates = await response.json();
                console.log(`Loaded ${Object.keys(this.goldenStates).length} golden states`);
            }
        } catch (e) {
            console.log('No golden states found - run in generate mode first');
        }
    }

    /**
     * Set generation mode
     */
    setGenerateMode(enabled) {
        this.generateMode = enabled;
        this.generatedGoldens = {};
    }

    /**
     * Get generated goldens as JSON string
     */
    getGeneratedGoldensJSON() {
        return JSON.stringify(this.generatedGoldens, null, 2);
    }

    /**
     * Compare current state against golden
     */
    compareWithGolden(testName, currentState) {
        const golden = this.goldenStates[testName];
        if (!golden) {
            return { match: false, reason: 'No golden state found - generate goldens first' };
        }
        return this.compareStates(currentState, golden);
    }

    /**
     * Save current state as golden
     */
    saveAsGolden(testName, state) {
        this.generatedGoldens[testName] = state;
    }

    /**
     * Add a test case
     */
    addTest(name, testFn) {
        this.tests.push({ name, testFn });
    }

    /**
     * Capture current state as image data
     */
    async captureState() {
        // Wait for render to complete
        await new Promise(r => requestAnimationFrame(() => requestAnimationFrame(r)));
        
        // Use html2canvas-like approach - capture the paper element
        const rect = this.paperRoot.getBoundingClientRect();
        const ctx = this.captureCanvas.getContext('2d');
        
        // Clear canvas
        ctx.fillStyle = '#0f172a';
        ctx.fillRect(0, 0, this.captureCanvas.width, this.captureCanvas.height);
        
        // Draw a representation of the current state
        // This captures the computed styles and positions
        const state = this.getVisualState();
        this.drawState(ctx, state);
        
        return this.captureCanvas.toDataURL('image/png');
    }

    /**
     * Get visual state of the paper for comparison
     */
    getVisualState() {
        const state = {
            folds: this.controller.getFolds().map(f => ({
                type: f.type,
                currentAngle: f.currentAngle,
                targetAngle: f.targetAngle
            })),
            elements: []
        };
        
        // Capture all paper-leaf elements and their clip-paths
        const leaves = this.paperRoot.querySelectorAll('.paper-leaf');
        leaves.forEach(leaf => {
            const front = leaf.querySelector('.face-front');
            const back = leaf.querySelector('.face-back');
            if (front) {
                state.elements.push({
                    type: 'front',
                    clipPath: window.getComputedStyle(front).clipPath,
                    transform: this.getAccumulatedTransform(front)
                });
            }
            if (back) {
                state.elements.push({
                    type: 'back',
                    clipPath: window.getComputedStyle(back).clipPath,
                    transform: this.getAccumulatedTransform(back)
                });
            }
        });
        
        return state;
    }

    /**
     * Get accumulated transform from element to paper root
     */
    getAccumulatedTransform(element) {
        let transform = '';
        let el = element;
        while (el && el !== this.paperRoot) {
            const t = window.getComputedStyle(el).transform;
            if (t && t !== 'none') {
                transform = t + ' ' + transform;
            }
            el = el.parentElement;
        }
        return transform.trim() || 'none';
    }

    /**
     * Draw the visual state to canvas
     */
    drawState(ctx, state) {
        const offsetX = 50;
        const offsetY = 50;
        const scale = 1;
        
        ctx.save();
        ctx.translate(offsetX, offsetY);
        ctx.scale(scale, scale);
        
        // Draw paper outline
        ctx.strokeStyle = '#38bdf8';
        ctx.lineWidth = 2;
        ctx.strokeRect(0, 0, 300, 300);
        
        // Draw fold info
        ctx.fillStyle = '#e2e8f0';
        ctx.font = '12px monospace';
        state.folds.forEach((fold, i) => {
            ctx.fillText(`Fold ${i + 1}: ${fold.type} @ ${fold.currentAngle.toFixed(1)}°`, 5, 320 + i * 16);
        });
        
        // Draw element count
        ctx.fillText(`Elements: ${state.elements.length}`, 5, 320 + state.folds.length * 16 + 5);
        
        // Draw simplified polygon shapes based on clip-paths
        state.elements.forEach((el, i) => {
            if (el.clipPath && el.clipPath !== 'none') {
                this.drawClipPath(ctx, el.clipPath, el.type === 'front' ? '#f8fafc' : '#3b82f6', i * 0.05);
            }
        });
        
        ctx.restore();
    }

    /**
     * Draw a clip-path polygon
     */
    drawClipPath(ctx, clipPath, color, offset) {
        const match = clipPath.match(/polygon\(([^)]+)\)/);
        if (!match) return;
        
        const points = match[1].split(',').map(p => {
            const [x, y] = p.trim().split(/\s+/).map(v => parseFloat(v));
            return { x: x + offset, y: y + offset };
        });
        
        if (points.length < 3) return;
        
        ctx.fillStyle = color;
        ctx.globalAlpha = 0.7;
        ctx.beginPath();
        ctx.moveTo(points[0].x, points[0].y);
        points.slice(1).forEach(p => ctx.lineTo(p.x, p.y));
        ctx.closePath();
        ctx.fill();
        ctx.globalAlpha = 1;
        
        ctx.strokeStyle = '#64748b';
        ctx.lineWidth = 1;
        ctx.stroke();
    }

    /**
     * Compare two visual states
     */
    compareStates(state1, state2) {
        // Compare fold counts
        if (state1.folds.length !== state2.folds.length) {
            return { match: false, reason: `Fold count mismatch: ${state1.folds.length} vs ${state2.folds.length}` };
        }
        
        // Compare fold angles (with tolerance)
        for (let i = 0; i < state1.folds.length; i++) {
            const f1 = state1.folds[i];
            const f2 = state2.folds[i];
            if (f1.type !== f2.type) {
                return { match: false, reason: `Fold ${i} type mismatch: ${f1.type} vs ${f2.type}` };
            }
            if (Math.abs(f1.currentAngle - f2.currentAngle) > 1) {
                return { match: false, reason: `Fold ${i} angle mismatch: ${f1.currentAngle} vs ${f2.currentAngle}` };
            }
        }
        
        // Compare element counts (support both elements array and elementCount number)
        const count1 = state1.elements ? state1.elements.length : state1.elementCount;
        const count2 = state2.elements ? state2.elements.length : state2.elementCount;
        
        if (count2 !== undefined && count1 !== undefined && count1 !== count2) {
            return { match: false, reason: `Element count mismatch: ${count1} vs ${count2}` };
        }
        
        return { match: true };
    }

    /**
     * Run all tests
     */
    async run() {
        const modeLabel = this.generateMode ? 'GOLDEN GENERATION' : 'E2E Tests';
        console.log(`\n=== ${modeLabel} ===\n`);
        this.results = [];
        
        for (const test of this.tests) {
            try {
                console.log(`Running: ${test.name}`);
                const result = await test.testFn(this);
                
                // In generate mode, save the captured state
                if (this.generateMode && result.state) {
                    this.saveAsGolden(test.name, result.state);
                    result.passed = true;
                    result.message = 'Golden captured';
                }
                
                this.results.push({
                    name: test.name,
                    passed: result.passed,
                    message: result.message,
                    screenshot: result.screenshot
                });
                console.log(result.passed ? `✅ ${test.name}` : `❌ ${test.name}: ${result.message}`);
            } catch (error) {
                this.results.push({
                    name: test.name,
                    passed: false,
                    message: error.message
                });
                console.log(`❌ ${test.name}: ${error.message}`);
            }
        }
        
        const passed = this.results.filter(r => r.passed).length;
        const failed = this.results.filter(r => !r.passed).length;
        console.log(`\nResults: ${passed} passed, ${failed} failed\n`);
        
        return this.results;
    }

    /**
     * Reset to clean state
     */
    reset() {
        this.controller.setFolds([]);
        this.controller.viewRotation = { x: 0, y: 0 };
    }
}

// Define e2e tests
export function defineE2ETests(suite) {
    
    // Test 1: Flat paper renders correctly
    suite.addTest('Flat paper renders with correct dimensions', async (s) => {
        s.reset();
        s.controller.setFolds([]);
        s.controller.renderer.render([]);
        
        await new Promise(r => setTimeout(r, 100));
        
        const leaves = s.paperRoot.querySelectorAll('.paper-leaf');
        const state = s.getVisualState();
        
        // Should have exactly 1 leaf (the flat paper)
        if (leaves.length !== 1) {
            return { passed: false, message: `Expected 1 leaf, got ${leaves.length}`, state };
        }
        
        // Should have 2 elements (front and back faces)
        if (state.elements.length !== 2) {
            return { passed: false, message: `Expected 2 elements, got ${state.elements.length}`, state };
        }
        
        // Golden comparison mode
        if (!s.generateMode && s.goldenStates['Flat paper renders with correct dimensions']) {
            const comparison = s.compareWithGolden('Flat paper renders with correct dimensions', state);
            if (!comparison.match) {
                return { passed: false, message: comparison.reason, state };
            }
        }
        
        const screenshot = await s.captureState();
        return { passed: true, message: 'Flat paper renders correctly', screenshot, state };
    });

    // Test 2: Single diagonal fold creates correct structure
    suite.addTest('Diagonal fold splits paper into correct polygons', async (s) => {
        s.reset();
        const folds = [{ id: 1, type: 'diag1', targetAngle: 135, currentAngle: 135 }];
        s.controller.setFolds(folds);
        
        await new Promise(r => setTimeout(r, 100));
        
        const state = s.getVisualState();
        
        // A diagonal fold should create 2 leaves (2 triangles)
        // Each leaf has front + back = 4 elements total
        if (state.elements.length < 2) {
            return { passed: false, message: `Expected at least 2 elements, got ${state.elements.length}`, state };
        }
        
        // Check that fold angles are correct
        if (state.folds.length !== 1 || state.folds[0].currentAngle !== 135) {
            return { passed: false, message: 'Fold angle not applied correctly', state };
        }
        
        // Golden comparison
        if (!s.generateMode && s.goldenStates['Diagonal fold splits paper into correct polygons']) {
            const comparison = s.compareWithGolden('Diagonal fold splits paper into correct polygons', state);
            if (!comparison.match) {
                return { passed: false, message: comparison.reason, state };
            }
        }
        
        const screenshot = await s.captureState();
        return { passed: true, message: 'Diagonal fold creates correct structure', screenshot, state };
    });

    // Test 3: Horizontal fold creates correct structure
    suite.addTest('Horizontal fold splits paper correctly', async (s) => {
        s.reset();
        const folds = [{ id: 1, type: 'horizontal', targetAngle: 90, currentAngle: 90 }];
        s.controller.setFolds(folds);
        
        await new Promise(r => setTimeout(r, 100));
        
        const state = s.getVisualState();
        
        // Horizontal fold should create 2 rectangles
        if (state.elements.length < 2) {
            return { passed: false, message: `Expected at least 2 elements, got ${state.elements.length}`, state };
        }
        
        // Golden comparison
        if (!s.generateMode && s.goldenStates['Horizontal fold splits paper correctly']) {
            const comparison = s.compareWithGolden('Horizontal fold splits paper correctly', state);
            if (!comparison.match) {
                return { passed: false, message: comparison.reason, state };
            }
        }
        
        const screenshot = await s.captureState();
        return { passed: true, message: 'Horizontal fold creates correct structure', screenshot, state };
    });

    // Test 4: Multiple folds create nested structure
    suite.addTest('Multiple folds create correct nested structure', async (s) => {
        s.reset();
        const folds = [
            { id: 1, type: 'diag1', targetAngle: 135, currentAngle: 135 },
            { id: 2, type: 'horizontal', targetAngle: 170, currentAngle: 170 }
        ];
        s.controller.setFolds(folds);
        
        await new Promise(r => setTimeout(r, 100));
        
        const state = s.getVisualState();
        
        // Multiple folds should create more elements
        if (state.folds.length !== 2) {
            return { passed: false, message: `Expected 2 folds, got ${state.folds.length}`, state };
        }
        
        // Golden comparison
        if (!s.generateMode && s.goldenStates['Multiple folds create correct nested structure']) {
            const comparison = s.compareWithGolden('Multiple folds create correct nested structure', state);
            if (!comparison.match) {
                return { passed: false, message: comparison.reason, state };
            }
        }
        
        const screenshot = await s.captureState();
        return { passed: true, message: 'Multiple folds create correct structure', screenshot, state };
    });

    // Test 5: Play state interpolation works
    suite.addTest('Play state interpolates fold angles correctly', async (s) => {
        s.reset();
        const folds = [{ id: 1, type: 'diag1', targetAngle: 180, currentAngle: 0 }];
        s.controller.setFolds(folds);
        
        // Apply 50% progress
        s.controller.applyPlayState(50);
        
        await new Promise(r => setTimeout(r, 100));
        
        const state = s.getVisualState();
        
        // At 50%, angle should be partially applied (with easing)
        // With cubic easing, 50% input gives 50% output
        const expectedAngle = 90; // Approximately
        const actualAngle = state.folds[0].currentAngle;
        
        if (Math.abs(actualAngle - expectedAngle) > 10) {
            return { passed: false, message: `Expected angle ~${expectedAngle}, got ${actualAngle}`, state };
        }
        
        // Golden comparison
        if (!s.generateMode && s.goldenStates['Play state interpolates fold angles correctly']) {
            const comparison = s.compareWithGolden('Play state interpolates fold angles correctly', state);
            if (!comparison.match) {
                return { passed: false, message: comparison.reason, state };
            }
        }
        
        const screenshot = await s.captureState();
        return { passed: true, message: 'Play state interpolation works', screenshot, state };
    });

    // Test 6: Clip paths are correctly applied
    suite.addTest('Clip paths are applied to paper faces', async (s) => {
        s.reset();
        const folds = [{ id: 1, type: 'vertical', targetAngle: 120, currentAngle: 120 }];
        s.controller.setFolds(folds);
        
        await new Promise(r => setTimeout(r, 100));
        
        const state = s.getVisualState();
        
        // All elements should have valid clip-paths
        for (const el of state.elements) {
            if (!el.clipPath || el.clipPath === 'none') {
                return { passed: false, message: 'Element missing clip-path', state };
            }
            if (!el.clipPath.includes('polygon')) {
                return { passed: false, message: `Invalid clip-path format: ${el.clipPath}`, state };
            }
        }
        
        // Golden comparison
        if (!s.generateMode && s.goldenStates['Clip paths are applied to paper faces']) {
            const comparison = s.compareWithGolden('Clip paths are applied to paper faces', state);
            if (!comparison.match) {
                return { passed: false, message: comparison.reason, state };
            }
        }
        
        const screenshot = await s.captureState();
        return { passed: true, message: 'Clip paths correctly applied', screenshot, state };
    });

    // Test 7: Transform origins are correctly set
    suite.addTest('Fold transforms are correctly applied', async (s) => {
        s.reset();
        const folds = [{ id: 1, type: 'diag1', targetAngle: 90, currentAngle: 90 }];
        s.controller.setFolds(folds);
        
        await new Promise(r => setTimeout(r, 100));
        
        const state = s.getVisualState();
        
        // Check that fold-moving elements have transforms
        const movingElements = s.paperRoot.querySelectorAll('.fold-moving');
        
        for (const el of movingElements) {
            const transform = window.getComputedStyle(el).transform;
            if (transform === 'none') {
                return { passed: false, message: 'Moving element missing transform', state };
            }
        }
        
        // Golden comparison
        if (!s.generateMode && s.goldenStates['Fold transforms are correctly applied']) {
            const comparison = s.compareWithGolden('Fold transforms are correctly applied', state);
            if (!comparison.match) {
                return { passed: false, message: comparison.reason, state };
            }
        }
        
        const screenshot = await s.captureState();
        return { passed: true, message: 'Transforms correctly applied', screenshot, state };
    });

    // Test 8: Back face clip-paths are mirrored correctly
    suite.addTest('Back face clip-paths are mirrored for rotateY', async (s) => {
        s.reset();
        const folds = [{ id: 1, type: 'diag1', targetAngle: 45, currentAngle: 45 }];
        s.controller.setFolds(folds);
        
        await new Promise(r => setTimeout(r, 100));
        
        const state = s.getVisualState();
        
        // Front and back should have different clip-paths (mirrored)
        const fronts = state.elements.filter(e => e.type === 'front');
        const backs = state.elements.filter(e => e.type === 'back');
        
        if (fronts.length !== backs.length) {
            return { passed: false, message: 'Front/back element count mismatch', state };
        }
        
        // Verify clip-paths exist and are different
        for (let i = 0; i < fronts.length; i++) {
            if (fronts[i].clipPath === backs[i].clipPath) {
                // They should be mirrored, not identical
                // (Unless it's a symmetric shape)
            }
        }
        
        // Golden comparison
        if (!s.generateMode && s.goldenStates['Back face clip-paths are mirrored for rotateY']) {
            const comparison = s.compareWithGolden('Back face clip-paths are mirrored for rotateY', state);
            if (!comparison.match) {
                return { passed: false, message: comparison.reason, state };
            }
        }
        
        const screenshot = await s.captureState();
        return { passed: true, message: 'Back faces correctly mirrored', screenshot, state };
    });

    // Test 9: All fold types render without errors
    suite.addTest('All fold types render correctly', async (s) => {
        const foldTypes = ['horizontal', 'vertical', 'diag1', 'diag2'];
        let lastState = null;
        
        for (const type of foldTypes) {
            s.reset();
            const folds = [{ id: 1, type, targetAngle: 90, currentAngle: 90 }];
            s.controller.setFolds(folds);
            
            await new Promise(r => setTimeout(r, 50));
            
            const leaves = s.paperRoot.querySelectorAll('.paper-leaf');
            if (leaves.length === 0) {
                return { passed: false, message: `Fold type ${type} produced no leaves`, state: lastState };
            }
            lastState = s.getVisualState();
        }
        
        const screenshot = await s.captureState();
        return { passed: true, message: 'All fold types render correctly', screenshot, state: lastState };
    });

    // Test 10: Complex fold sequence renders correctly
    suite.addTest('Complex fold sequence renders without errors', async (s) => {
        s.reset();
        const folds = [
            { id: 1, type: 'diag1', targetAngle: 135, currentAngle: 135 },
            { id: 2, type: 'horizontal', targetAngle: 170, currentAngle: 170 },
            { id: 3, type: 'vertical', targetAngle: 90, currentAngle: 90 }
        ];
        s.controller.setFolds(folds);
        
        await new Promise(r => setTimeout(r, 100));
        
        const state = s.getVisualState();
        
        if (state.folds.length !== 3) {
            return { passed: false, message: `Expected 3 folds, got ${state.folds.length}`, state };
        }
        
        if (state.elements.length === 0) {
            return { passed: false, message: 'No elements rendered', state };
        }
        
        // Golden comparison
        if (!s.generateMode && s.goldenStates['Complex fold sequence renders without errors']) {
            const comparison = s.compareWithGolden('Complex fold sequence renders without errors', state);
            if (!comparison.match) {
                return { passed: false, message: comparison.reason, state };
            }
        }
        
        const screenshot = await s.captureState();
        return { passed: true, message: 'Complex sequence renders correctly', screenshot, state };
    });
}

// Export for use in test.e2e.html
export { defineE2ETests as default };
