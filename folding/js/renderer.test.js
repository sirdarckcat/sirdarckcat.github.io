/**
 * Unit tests for renderer.js
 * Tests rendering logic in isolation using mock DOM elements
 */

import { FoldingRenderer, updateTurntable } from './renderer.js';
import { Vec2, createSquarePolygon } from './math.js';
import { TestRunner, assertEqual, assertTrue } from './math.test.js';

const rendererTests = new TestRunner('Renderer Module Tests');

// Mock DOM element for testing
function createMockElement() {
    return {
        innerHTML: '',
        style: {},
        className: '',
        children: [],
        appendChild(child) {
            this.children.push(child);
            return child;
        }
    };
}

// FoldingRenderer Tests
rendererTests.test('FoldingRenderer constructor sets paperSize', () => {
    const mockRoot = createMockElement();
    const renderer = new FoldingRenderer(mockRoot, 400);
    assertEqual(renderer.paperSize, 400);
});

rendererTests.test('FoldingRenderer uses default paperSize of 300', () => {
    const mockRoot = createMockElement();
    const renderer = new FoldingRenderer(mockRoot);
    assertEqual(renderer.paperSize, 300);
});

rendererTests.test('FoldingRenderer.render clears root element', () => {
    // This test requires a DOM environment, skip in pure Node
    if (typeof document === 'undefined') {
        console.log('   (Skipping - requires DOM)');
        return;
    }
    
    const root = document.createElement('div');
    root.innerHTML = '<div>old content</div>';
    const renderer = new FoldingRenderer(root, 300);
    renderer.render([]);
    
    // After rendering with no folds, root should have new content
    assertTrue(root.innerHTML !== '<div>old content</div>');
});

rendererTests.test('FoldingRenderer.createLeaf returns element with front and back faces', () => {
    if (typeof document === 'undefined') {
        console.log('   (Skipping - requires DOM)');
        return;
    }
    
    const root = document.createElement('div');
    const renderer = new FoldingRenderer(root, 300);
    const geometry = createSquarePolygon(300);
    const leaf = renderer.createLeaf(geometry);
    
    assertTrue(leaf !== null, 'Leaf should not be null');
    assertEqual(leaf.className, 'paper-leaf');
    assertEqual(leaf.children.length, 2, 'Leaf should have 2 children (front and back)');
});

rendererTests.test('FoldingRenderer.createMovingWrapper sets correct transform', () => {
    if (typeof document === 'undefined') {
        console.log('   (Skipping - requires DOM)');
        return;
    }
    
    const root = document.createElement('div');
    const renderer = new FoldingRenderer(root, 300);
    const lineDef = { axis: 'X', origin: '50% 50%' };
    const wrapper = renderer.createMovingWrapper(lineDef, 90);
    
    assertEqual(wrapper.className, 'fold-moving');
    assertEqual(wrapper.style.transformOrigin, '50% 50%');
    assertTrue(wrapper.style.transform.includes('rotate3d'));
    assertTrue(wrapper.style.transform.includes('-90deg'));
});

rendererTests.test('FoldingRenderer.render with single fold creates fold structure', () => {
    if (typeof document === 'undefined') {
        console.log('   (Skipping - requires DOM)');
        return;
    }
    
    const root = document.createElement('div');
    const renderer = new FoldingRenderer(root, 300);
    const folds = [
        { type: 'horizontal', currentAngle: 45 }
    ];
    
    renderer.render(folds);
    
    // Root should have content after render
    assertTrue(root.children.length > 0, 'Root should have children after render');
});

// updateTurntable Tests
rendererTests.test('updateTurntable sets correct transform', () => {
    if (typeof document === 'undefined') {
        console.log('   (Skipping - requires DOM)');
        return;
    }
    
    const turntable = document.createElement('div');
    const rotation = { x: 30, y: 45 };
    
    updateTurntable(turntable, rotation);
    
    assertEqual(turntable.style.transform, 'rotateX(30deg) rotateY(45deg)');
});

rendererTests.test('updateTurntable handles negative rotations', () => {
    if (typeof document === 'undefined') {
        console.log('   (Skipping - requires DOM)');
        return;
    }
    
    const turntable = document.createElement('div');
    const rotation = { x: -45, y: -90 };
    
    updateTurntable(turntable, rotation);
    
    assertEqual(turntable.style.transform, 'rotateX(-45deg) rotateY(-90deg)');
});

export { rendererTests };
