/**
 * Unit tests for folds.js
 */

import { 
    getFoldLine, 
    getRotationAxis, 
    getFoldLabel, 
    createFold, 
    getDefaultFolds,
    FOLD_DIRECTION,
    ORIGAMI_PRESETS,
    getPresetNames,
    loadPreset
} from './folds.js';
import { INV_ROOT_2 } from './math.js';
import { TestRunner, assertEqual, assertApproxEqual, assertTrue } from './math.test.js';

const foldsTests = new TestRunner('Folds Module Tests');

// getFoldLine Tests - updated for position parameter
foldsTests.test('getFoldLine returns correct horizontal fold line at center', () => {
    const line = getFoldLine('horizontal', 300, 50);
    assertEqual(line.nx, 0);
    assertEqual(line.ny, 1);
    assertEqual(line.c, -150);
    assertEqual(line.axis, 'X');
});

foldsTests.test('getFoldLine returns correct vertical fold line at center', () => {
    const line = getFoldLine('vertical', 300, 50);
    assertEqual(line.nx, 1);
    assertEqual(line.ny, 0);
    assertEqual(line.c, -150);
    assertEqual(line.axis, 'Y');
});

foldsTests.test('getFoldLine returns correct diag1 fold line at center', () => {
    const line = getFoldLine('diag1', 300, 50);
    assertApproxEqual(line.nx, INV_ROOT_2, 0.0001);
    assertApproxEqual(line.ny, -INV_ROOT_2, 0.0001);
    assertEqual(line.axis, 'D1');
});

foldsTests.test('getFoldLine returns correct diag2 fold line at center', () => {
    const line = getFoldLine('diag2', 300, 50);
    assertApproxEqual(line.nx, INV_ROOT_2, 0.0001);
    assertApproxEqual(line.ny, INV_ROOT_2, 0.0001);
    assertEqual(line.axis, 'D2');
});

foldsTests.test('getFoldLine returns horizontal for unknown type', () => {
    const line = getFoldLine('unknown', 300, 50);
    assertEqual(line.axis, 'X');
});

// Position parameter tests
foldsTests.test('getFoldLine horizontal at 25% position', () => {
    const line = getFoldLine('horizontal', 300, 25);
    assertEqual(line.c, -75); // 25% of 300 = 75
});

foldsTests.test('getFoldLine vertical at 75% position', () => {
    const line = getFoldLine('vertical', 300, 75);
    assertEqual(line.c, -225); // 75% of 300 = 225
});

foldsTests.test('getFoldLine includes p1 and p2 endpoints', () => {
    const line = getFoldLine('horizontal', 300, 50);
    assertTrue(line.p1 !== undefined, 'p1 should be defined');
    assertTrue(line.p2 !== undefined, 'p2 should be defined');
    assertEqual(line.p1.y, 150);
    assertEqual(line.p2.y, 150);
});

// getRotationAxis Tests
foldsTests.test('getRotationAxis returns correct axis for X', () => {
    assertEqual(getRotationAxis('X'), '1, 0, 0');
});

foldsTests.test('getRotationAxis returns correct axis for Y', () => {
    assertEqual(getRotationAxis('Y'), '0, 1, 0');
});

foldsTests.test('getRotationAxis returns correct axis for D1', () => {
    assertEqual(getRotationAxis('D1'), '1, 1, 0');
});

foldsTests.test('getRotationAxis returns correct axis for D2', () => {
    assertEqual(getRotationAxis('D2'), '-1, 1, 0');
});

// getFoldLabel Tests
foldsTests.test('getFoldLabel returns correct labels', () => {
    assertEqual(getFoldLabel('horizontal'), 'HORIZONTAL');
    assertEqual(getFoldLabel('vertical'), 'VERTICAL');
    assertEqual(getFoldLabel('diag1'), 'DIAGONAL \\');
    assertEqual(getFoldLabel('diag2'), 'DIAGONAL /');
    assertEqual(getFoldLabel('custom'), 'CUSTOM');
});

// createFold Tests - updated for new parameters
foldsTests.test('createFold creates fold with correct properties', () => {
    const fold = createFold('horizontal', 90, 50, FOLD_DIRECTION.MOUNTAIN);
    assertEqual(fold.type, 'horizontal');
    assertEqual(fold.targetAngle, 90);
    assertEqual(fold.currentAngle, 90);
    assertEqual(fold.position, 50);
    assertEqual(fold.direction, FOLD_DIRECTION.MOUNTAIN);
    assertTrue(fold.id > 0, 'ID should be positive number');
});

foldsTests.test('createFold uses default angle of 135', () => {
    const fold = createFold('vertical');
    assertEqual(fold.targetAngle, 135);
});

foldsTests.test('createFold uses default position of 50', () => {
    const fold = createFold('vertical');
    assertEqual(fold.position, 50);
});

foldsTests.test('createFold uses default direction of mountain', () => {
    const fold = createFold('vertical');
    assertEqual(fold.direction, FOLD_DIRECTION.MOUNTAIN);
});

// FOLD_DIRECTION Tests
foldsTests.test('FOLD_DIRECTION has mountain and valley', () => {
    assertEqual(FOLD_DIRECTION.MOUNTAIN, 'mountain');
    assertEqual(FOLD_DIRECTION.VALLEY, 'valley');
});

// getDefaultFolds Tests
foldsTests.test('getDefaultFolds returns array with 2 folds', () => {
    const folds = getDefaultFolds();
    assertEqual(folds.length, 2);
});

foldsTests.test('getDefaultFolds first fold is diag1', () => {
    const folds = getDefaultFolds();
    assertEqual(folds[0].type, 'diag1');
    assertEqual(folds[0].targetAngle, 135);
});

foldsTests.test('getDefaultFolds second fold is horizontal', () => {
    const folds = getDefaultFolds();
    assertEqual(folds[1].type, 'horizontal');
    assertEqual(folds[1].targetAngle, 170);
});

// Preset Tests
foldsTests.test('ORIGAMI_PRESETS contains expected patterns', () => {
    assertTrue(ORIGAMI_PRESETS['blank'] !== undefined, 'blank preset should exist');
    assertTrue(ORIGAMI_PRESETS['triangle'] !== undefined, 'triangle preset should exist');
    assertTrue(ORIGAMI_PRESETS['waterbomb-base'] !== undefined, 'waterbomb-base preset should exist');
});

foldsTests.test('getPresetNames returns array of preset keys', () => {
    const names = getPresetNames();
    assertTrue(Array.isArray(names), 'Should return array');
    assertTrue(names.includes('blank'), 'Should include blank');
    assertTrue(names.includes('triangle'), 'Should include triangle');
});

foldsTests.test('loadPreset returns array of fold objects', () => {
    const folds = loadPreset('triangle');
    assertTrue(Array.isArray(folds), 'Should return array');
    assertEqual(folds.length, 1);
    assertEqual(folds[0].type, 'diag1');
});

foldsTests.test('loadPreset returns empty array for unknown preset', () => {
    const folds = loadPreset('nonexistent');
    assertEqual(folds.length, 0);
});

foldsTests.test('loadPreset assigns unique IDs to folds', () => {
    const folds = loadPreset('waterbomb-base');
    const ids = folds.map(f => f.id);
    const uniqueIds = [...new Set(ids)];
    assertEqual(ids.length, uniqueIds.length);
});

export { foldsTests };
