/**
 * Unit tests for folds.js
 */

import { 
    getFoldLine, 
    getRotationAxis, 
    getFoldLabel, 
    createFold, 
    getDefaultFolds 
} from './folds.js';
import { INV_ROOT_2 } from './math.js';
import { TestRunner, assertEqual, assertApproxEqual, assertTrue } from './math.test.js';

const foldsTests = new TestRunner('Folds Module Tests');

// getFoldLine Tests
foldsTests.test('getFoldLine returns correct horizontal fold line', () => {
    const line = getFoldLine('horizontal', 300);
    assertEqual(line.nx, 0);
    assertEqual(line.ny, 1);
    assertEqual(line.c, -150);
    assertEqual(line.axis, 'X');
});

foldsTests.test('getFoldLine returns correct vertical fold line', () => {
    const line = getFoldLine('vertical', 300);
    assertEqual(line.nx, 1);
    assertEqual(line.ny, 0);
    assertEqual(line.c, -150);
    assertEqual(line.axis, 'Y');
});

foldsTests.test('getFoldLine returns correct diag1 fold line', () => {
    const line = getFoldLine('diag1', 300);
    assertApproxEqual(line.nx, INV_ROOT_2, 0.0001);
    assertApproxEqual(line.ny, -INV_ROOT_2, 0.0001);
    assertEqual(line.c, 0);
    assertEqual(line.axis, 'D1');
});

foldsTests.test('getFoldLine returns correct diag2 fold line', () => {
    const line = getFoldLine('diag2', 300);
    assertApproxEqual(line.nx, INV_ROOT_2, 0.0001);
    assertApproxEqual(line.ny, INV_ROOT_2, 0.0001);
    assertApproxEqual(line.c, -300 * INV_ROOT_2, 0.0001);
    assertEqual(line.axis, 'D2');
});

foldsTests.test('getFoldLine returns horizontal for unknown type', () => {
    const line = getFoldLine('unknown', 300);
    assertEqual(line.axis, 'X');
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
});

// createFold Tests
foldsTests.test('createFold creates fold with correct properties', () => {
    const fold = createFold('horizontal', 90);
    assertEqual(fold.type, 'horizontal');
    assertEqual(fold.targetAngle, 90);
    assertEqual(fold.currentAngle, 90);
    assertTrue(fold.id > 0, 'ID should be positive number');
});

foldsTests.test('createFold uses default angle of 135', () => {
    const fold = createFold('vertical');
    assertEqual(fold.targetAngle, 135);
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

export { foldsTests };
