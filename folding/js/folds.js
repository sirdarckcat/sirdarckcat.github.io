/**
 * Fold definitions and fold line calculations
 */

import { INV_ROOT_2 } from './math.js';

/**
 * Get the fold line definition for a given fold type
 * @param {string} type - Fold type: 'horizontal', 'vertical', 'diag1', 'diag2'
 * @param {number} paperSize - Size of the paper
 * @returns {Object} Line definition {nx, ny, c, axis, origin}
 */
export function getFoldLine(type, paperSize) {
    const c = paperSize / 2;

    switch (type) {
        case 'horizontal':
            // Horizontal fold: y > center moves
            return { nx: 0, ny: 1, c: -c, axis: 'X', origin: '50% 50%' };
        
        case 'vertical':
            // Vertical fold: x > center moves
            return { nx: 1, ny: 0, c: -c, axis: 'Y', origin: '50% 50%' };
        
        case 'diag1':
            // Diagonal \ (TopLeft to BottomRight): Top-Right moves (x > y)
            return { nx: INV_ROOT_2, ny: -INV_ROOT_2, c: 0, axis: 'D1', origin: '50% 50%' };
        
        case 'diag2':
            // Diagonal / (TopRight to BottomLeft): Bottom-Right moves (x + y > size)
            return { nx: INV_ROOT_2, ny: INV_ROOT_2, c: -paperSize * INV_ROOT_2, axis: 'D2', origin: '50% 50%' };
        
        default:
            // Default to horizontal
            return { nx: 0, ny: 1, c: -c, axis: 'X', origin: '50% 50%' };
    }
}

/**
 * Get the 3D rotation axis for a fold line
 * @param {string} axis - Axis type from fold line definition
 * @returns {string} CSS rotate3d axis string
 */
export function getRotationAxis(axis) {
    switch (axis) {
        case 'X': return '1, 0, 0';  // Horizontal fold axis
        case 'Y': return '0, 1, 0';  // Vertical fold axis
        case 'D1': return '1, 1, 0'; // Diagonal \ axis
        case 'D2': return '-1, 1, 0'; // Diagonal / axis
        default: return '1, 0, 0';
    }
}

/**
 * Get human-readable label for fold type
 * @param {string} type - Fold type
 * @returns {string} Display label
 */
export function getFoldLabel(type) {
    switch (type) {
        case 'horizontal': return 'HORIZONTAL';
        case 'vertical': return 'VERTICAL';
        case 'diag1': return 'DIAGONAL \\';
        case 'diag2': return 'DIAGONAL /';
        default: return type.toUpperCase();
    }
}

/**
 * Create a new fold object
 * @param {string} type - Fold type
 * @param {number} targetAngle - Target fold angle
 * @returns {Object} Fold object
 */
export function createFold(type, targetAngle = 135) {
    return {
        id: Date.now(),
        type: type,
        targetAngle: targetAngle,
        currentAngle: targetAngle
    };
}

/**
 * Default fold sequence for initial state
 * @returns {Object[]} Array of fold objects
 */
export function getDefaultFolds() {
    return [
        { id: 1, type: 'diag1', targetAngle: 135, currentAngle: 0 },
        { id: 2, type: 'horizontal', targetAngle: 170, currentAngle: 0 }
    ];
}
