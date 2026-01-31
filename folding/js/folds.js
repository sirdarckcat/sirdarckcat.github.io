/**
 * Fold definitions and fold line calculations
 * Enhanced for arbitrary fold positions and mountain/valley folds
 */

import { INV_ROOT_2, Vec2 } from './math.js';

/**
 * Fold direction types
 */
export const FOLD_DIRECTION = {
    MOUNTAIN: 'mountain',  // Fold towards viewer (positive angle)
    VALLEY: 'valley'       // Fold away from viewer (negative angle)
};

/**
 * Get the fold line definition for a given fold type at a specific position
 * @param {string} type - Fold type: 'horizontal', 'vertical', 'diag1', 'diag2', 'custom'
 * @param {number} paperSize - Size of the paper
 * @param {number} position - Position of fold (0-100, where 50 is center)
 * @param {Object} customLine - Custom line definition for 'custom' type {p1, p2}
 * @returns {Object} Line definition {nx, ny, c, axis, origin, p1, p2}
 */
export function getFoldLine(type, paperSize, position = 50, customLine = null) {
    // Convert position percentage to actual coordinate
    const pos = (position / 100) * paperSize;
    
    switch (type) {
        case 'horizontal': {
            // Horizontal fold at position: y = pos
            const p1 = new Vec2(0, pos);
            const p2 = new Vec2(paperSize, pos);
            return { 
                nx: 0, 
                ny: 1, 
                c: -pos, 
                axis: 'X', 
                origin: `50% ${position}%`,
                p1, p2
            };
        }
        
        case 'vertical': {
            // Vertical fold at position: x = pos
            const p1 = new Vec2(pos, 0);
            const p2 = new Vec2(pos, paperSize);
            return { 
                nx: 1, 
                ny: 0, 
                c: -pos, 
                axis: 'Y', 
                origin: `${position}% 50%`,
                p1, p2
            };
        }
        
        case 'diag1': {
            // Diagonal \ from top-left towards bottom-right
            // Line passes through (pos, 0) and (0, pos) - offset diagonal
            // For center (pos=50%), line is x - y = 0
            const offset = pos - paperSize / 2;
            const p1 = new Vec2(0, -offset);
            const p2 = new Vec2(paperSize, paperSize - offset);
            return { 
                nx: INV_ROOT_2, 
                ny: -INV_ROOT_2, 
                c: offset * INV_ROOT_2, 
                axis: 'D1', 
                origin: '50% 50%',
                p1, p2
            };
        }
        
        case 'diag2': {
            // Diagonal / from top-right towards bottom-left
            // For center (pos=50%), line is x + y = paperSize
            const targetSum = (position / 50) * paperSize;
            const p1 = new Vec2(0, targetSum);
            const p2 = new Vec2(targetSum, 0);
            return { 
                nx: INV_ROOT_2, 
                ny: INV_ROOT_2, 
                c: -targetSum * INV_ROOT_2, 
                axis: 'D2', 
                origin: '50% 50%',
                p1, p2
            };
        }
        
        case 'custom': {
            // Custom fold line defined by two points
            if (!customLine || !customLine.p1 || !customLine.p2) {
                return getFoldLine('horizontal', paperSize, position);
            }
            const { p1, p2 } = customLine;
            // Calculate line normal
            const dx = p2.x - p1.x;
            const dy = p2.y - p1.y;
            const len = Math.sqrt(dx * dx + dy * dy);
            if (len < 0.001) {
                return getFoldLine('horizontal', paperSize, position);
            }
            // Normal is perpendicular to direction
            const nx = -dy / len;
            const ny = dx / len;
            const c = -(nx * p1.x + ny * p1.y);
            
            // Determine axis based on line angle
            const angle = Math.atan2(dy, dx) * 180 / Math.PI;
            let axis = 'X';
            if (Math.abs(angle) < 22.5 || Math.abs(angle) > 157.5) axis = 'X';
            else if (Math.abs(angle - 90) < 22.5 || Math.abs(angle + 90) < 22.5) axis = 'Y';
            else if (angle > 0) axis = 'D1';
            else axis = 'D2';
            
            return { nx, ny, c, axis, origin: '50% 50%', p1, p2 };
        }
        
        default:
            return getFoldLine('horizontal', paperSize, position);
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
        case 'custom': return 'CUSTOM';
        default: return type.toUpperCase();
    }
}

/**
 * Get fold direction label
 * @param {string} direction - Fold direction
 * @returns {string} Display label with symbol
 */
export function getFoldDirectionLabel(direction) {
    return direction === FOLD_DIRECTION.MOUNTAIN ? '⛰️ Mountain' : '🏔️ Valley';
}

/**
 * Create a new fold object with extended properties
 * @param {string} type - Fold type
 * @param {number} targetAngle - Target fold angle (positive for mountain, negative for valley)
 * @param {number} position - Position of fold line (0-100%)
 * @param {string} direction - Fold direction (mountain/valley)
 * @returns {Object} Fold object
 */
export function createFold(type, targetAngle = 135, position = 50, direction = FOLD_DIRECTION.MOUNTAIN) {
    return {
        id: Date.now(),
        type: type,
        targetAngle: targetAngle,
        currentAngle: targetAngle,
        position: position,
        direction: direction
    };
}

/**
 * Get the effective angle based on fold direction
 * @param {Object} fold - Fold object
 * @returns {number} Effective angle (positive or negative)
 */
export function getEffectiveAngle(fold) {
    const angle = Math.abs(fold.currentAngle);
    return fold.direction === FOLD_DIRECTION.VALLEY ? -angle : angle;
}

/**
 * Default fold sequence for initial state
 * @returns {Object[]} Array of fold objects
 */
export function getDefaultFolds() {
    return [
        { id: 1, type: 'diag1', targetAngle: 135, currentAngle: 0, position: 50, direction: FOLD_DIRECTION.MOUNTAIN },
        { id: 2, type: 'horizontal', targetAngle: 170, currentAngle: 0, position: 50, direction: FOLD_DIRECTION.MOUNTAIN }
    ];
}

/**
 * Preset origami patterns
 */
export const ORIGAMI_PRESETS = {
    'blank': {
        name: 'Blank Paper',
        description: 'Start with a fresh sheet',
        folds: []
    },
    'simple-fold': {
        name: 'Simple Half Fold',
        description: 'Basic fold in half',
        folds: [
            { type: 'horizontal', targetAngle: 180, position: 50, direction: FOLD_DIRECTION.MOUNTAIN }
        ]
    },
    'triangle': {
        name: 'Triangle',
        description: 'Fold corner to corner',
        folds: [
            { type: 'diag1', targetAngle: 180, position: 50, direction: FOLD_DIRECTION.MOUNTAIN }
        ]
    },
    'paper-airplane-simple': {
        name: 'Simple Paper Airplane',
        description: 'Classic dart airplane',
        folds: [
            { type: 'vertical', targetAngle: 180, position: 50, direction: FOLD_DIRECTION.VALLEY },
            { type: 'diag1', targetAngle: 160, position: 25, direction: FOLD_DIRECTION.MOUNTAIN },
            { type: 'diag2', targetAngle: 160, position: 75, direction: FOLD_DIRECTION.MOUNTAIN }
        ]
    },
    'fortune-teller': {
        name: 'Fortune Teller Base',
        description: 'Corners to center',
        folds: [
            { type: 'diag1', targetAngle: 180, position: 50, direction: FOLD_DIRECTION.VALLEY },
            { type: 'diag2', targetAngle: 180, position: 50, direction: FOLD_DIRECTION.VALLEY }
        ]
    },
    'waterbomb-base': {
        name: 'Waterbomb Base',
        description: 'Classic origami base',
        folds: [
            { type: 'horizontal', targetAngle: 180, position: 50, direction: FOLD_DIRECTION.VALLEY },
            { type: 'vertical', targetAngle: 180, position: 50, direction: FOLD_DIRECTION.VALLEY },
            { type: 'diag1', targetAngle: 180, position: 50, direction: FOLD_DIRECTION.MOUNTAIN },
            { type: 'diag2', targetAngle: 180, position: 50, direction: FOLD_DIRECTION.MOUNTAIN }
        ]
    }
};

/**
 * Get all available preset names
 * @returns {string[]} Array of preset keys
 */
export function getPresetNames() {
    return Object.keys(ORIGAMI_PRESETS);
}

/**
 * Load a preset by name
 * @param {string} presetName - Key from ORIGAMI_PRESETS
 * @returns {Object[]} Array of fold objects with IDs
 */
export function loadPreset(presetName) {
    const preset = ORIGAMI_PRESETS[presetName];
    if (!preset) return [];
    
    return preset.folds.map((fold, index) => ({
        id: Date.now() + index,
        type: fold.type,
        targetAngle: fold.targetAngle,
        currentAngle: 0,
        position: fold.position || 50,
        direction: fold.direction || FOLD_DIRECTION.MOUNTAIN
    }));
}
