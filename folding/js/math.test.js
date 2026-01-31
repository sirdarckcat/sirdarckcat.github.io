/**
 * Unit tests for math.js
 */

import { 
    Vec2, 
    easeInOutCubic, 
    splitPolygon, 
    polygonToClipPath, 
    polygonToMirroredClipPath,
    createSquarePolygon,
    INV_ROOT_2,
    MAX_FOLD_ANGLE
} from './math.js';

/**
 * Simple test runner
 */
export class TestRunner {
    constructor(name) {
        this.name = name;
        this.tests = [];
        this.passed = 0;
        this.failed = 0;
    }

    test(description, fn) {
        this.tests.push({ description, fn });
    }

    async run() {
        console.log(`\n=== ${this.name} ===\n`);
        const results = [];

        for (const { description, fn } of this.tests) {
            try {
                await fn();
                this.passed++;
                results.push({ description, passed: true });
                console.log(`✅ ${description}`);
            } catch (error) {
                this.failed++;
                results.push({ description, passed: false, error: error.message });
                console.log(`❌ ${description}`);
                console.error(`   ${error.message}`);
            }
        }

        console.log(`\nResults: ${this.passed} passed, ${this.failed} failed\n`);
        return results;
    }
}

/**
 * Assertion helpers
 */
export function assertEqual(actual, expected, message = '') {
    if (actual !== expected) {
        throw new Error(`${message} Expected ${expected}, got ${actual}`);
    }
}

export function assertApproxEqual(actual, expected, epsilon = 0.001, message = '') {
    if (Math.abs(actual - expected) > epsilon) {
        throw new Error(`${message} Expected ~${expected}, got ${actual}`);
    }
}

export function assertTrue(condition, message = '') {
    if (!condition) {
        throw new Error(message || 'Expected true, got false');
    }
}

export function assertFalse(condition, message = '') {
    if (condition) {
        throw new Error(message || 'Expected false, got true');
    }
}

// Create test runner for math tests
const mathTests = new TestRunner('Math Module Tests');

// Vec2 Tests
mathTests.test('Vec2 constructor creates vector with x and y', () => {
    const v = new Vec2(3, 4);
    assertEqual(v.x, 3);
    assertEqual(v.y, 4);
});

mathTests.test('Vec2.lerp interpolates between two vectors at t=0', () => {
    const v1 = new Vec2(0, 0);
    const v2 = new Vec2(10, 20);
    const result = Vec2.lerp(v1, v2, 0);
    assertEqual(result.x, 0);
    assertEqual(result.y, 0);
});

mathTests.test('Vec2.lerp interpolates between two vectors at t=1', () => {
    const v1 = new Vec2(0, 0);
    const v2 = new Vec2(10, 20);
    const result = Vec2.lerp(v1, v2, 1);
    assertEqual(result.x, 10);
    assertEqual(result.y, 20);
});

mathTests.test('Vec2.lerp interpolates between two vectors at t=0.5', () => {
    const v1 = new Vec2(0, 0);
    const v2 = new Vec2(10, 20);
    const result = Vec2.lerp(v1, v2, 0.5);
    assertEqual(result.x, 5);
    assertEqual(result.y, 10);
});

mathTests.test('Vec2.equals returns true for equal vectors', () => {
    const v1 = new Vec2(3.0001, 4.0001);
    const v2 = new Vec2(3.0002, 4.0002);
    assertTrue(v1.equals(v2, 0.001));
});

mathTests.test('Vec2.equals returns false for different vectors', () => {
    const v1 = new Vec2(3, 4);
    const v2 = new Vec2(5, 6);
    assertFalse(v1.equals(v2, 0.001));
});

// Easing Tests
mathTests.test('easeInOutCubic returns 0 for t=0', () => {
    assertEqual(easeInOutCubic(0), 0);
});

mathTests.test('easeInOutCubic returns 1 for t=1', () => {
    assertEqual(easeInOutCubic(1), 1);
});

mathTests.test('easeInOutCubic returns 0.5 for t=0.5', () => {
    assertEqual(easeInOutCubic(0.5), 0.5);
});

mathTests.test('easeInOutCubic is smooth (derivative exists)', () => {
    // Check that values are monotonically increasing
    let prev = 0;
    for (let t = 0.1; t <= 1; t += 0.1) {
        const current = easeInOutCubic(t);
        assertTrue(current > prev, `Expected ${current} > ${prev} at t=${t}`);
        prev = current;
    }
});

// Constants Tests
mathTests.test('INV_ROOT_2 is approximately 0.7071', () => {
    assertApproxEqual(INV_ROOT_2, 0.7071, 0.0001);
});

mathTests.test('MAX_FOLD_ANGLE is 179', () => {
    assertEqual(MAX_FOLD_ANGLE, 179);
});

// Polygon Split Tests
mathTests.test('splitPolygon splits square horizontally at center', () => {
    const square = createSquarePolygon(100);
    const line = { nx: 0, ny: 1, c: -50 }; // y = 50
    const result = splitPolygon(square, line);
    
    assertTrue(result.staticPoly !== null, 'Static poly should exist');
    assertTrue(result.movingPoly !== null, 'Moving poly should exist');
    assertEqual(result.staticPoly.length, 4, 'Static should be quadrilateral');
    assertEqual(result.movingPoly.length, 4, 'Moving should be quadrilateral');
});

mathTests.test('splitPolygon splits square diagonally', () => {
    const square = createSquarePolygon(100);
    const line = { nx: INV_ROOT_2, ny: -INV_ROOT_2, c: 0 }; // x = y diagonal
    const result = splitPolygon(square, line);
    
    assertTrue(result.staticPoly !== null, 'Static poly should exist');
    assertTrue(result.movingPoly !== null, 'Moving poly should exist');
});

mathTests.test('splitPolygon returns null for movingPoly when polygon is entirely on static side', () => {
    const square = [
        new Vec2(0, 0), new Vec2(10, 0), 
        new Vec2(10, 10), new Vec2(0, 10)
    ];
    // Line at y = 100 (far above the square)
    const line = { nx: 0, ny: 1, c: -100 };
    const result = splitPolygon(square, line);
    
    assertTrue(result.movingPoly === null, 'Moving poly should be null');
    assertTrue(result.staticPoly !== null, 'Static poly should exist');
});

// Clip Path Tests
mathTests.test('polygonToClipPath generates valid CSS', () => {
    const poly = [new Vec2(0, 0), new Vec2(100, 0), new Vec2(100, 100)];
    const result = polygonToClipPath(poly);
    assertEqual(result, 'polygon(0px 0px, 100px 0px, 100px 100px)');
});

mathTests.test('polygonToClipPath returns none for null', () => {
    assertEqual(polygonToClipPath(null), 'none');
});

mathTests.test('polygonToMirroredClipPath mirrors X coordinates', () => {
    const poly = [new Vec2(0, 0), new Vec2(100, 0), new Vec2(100, 100)];
    const result = polygonToMirroredClipPath(poly, 300);
    // X coordinates should be mirrored: 0 -> 300, 100 -> 200
    assertEqual(result, 'polygon(300px 0px, 200px 0px, 200px 100px)');
});

mathTests.test('polygonToMirroredClipPath returns none for null', () => {
    assertEqual(polygonToMirroredClipPath(null, 300), 'none');
});

// Square Polygon Tests
mathTests.test('createSquarePolygon creates correct vertices', () => {
    const square = createSquarePolygon(100);
    assertEqual(square.length, 4);
    assertTrue(square[0].equals(new Vec2(0, 0)));
    assertTrue(square[1].equals(new Vec2(100, 0)));
    assertTrue(square[2].equals(new Vec2(100, 100)));
    assertTrue(square[3].equals(new Vec2(0, 100)));
});

export { mathTests };
