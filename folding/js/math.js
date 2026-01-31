/**
 * Math utilities for the folding engine
 * Contains vector math, polygon operations, and clip-path generation
 */

// Pre-computed constants
export const INV_ROOT_2 = 1 / Math.sqrt(2); // 1/√2 for diagonal fold calculations
export const MAX_FOLD_ANGLE = 179; // Maximum fold angle (179° prevents complete 180° fold-back)

/**
 * 2D Vector class for geometry calculations
 */
export class Vec2 {
    constructor(x, y) {
        this.x = x;
        this.y = y;
    }

    /**
     * Linear interpolation between two vectors
     * @param {Vec2} v1 - Start vector
     * @param {Vec2} v2 - End vector
     * @param {number} t - Interpolation factor (0-1)
     * @returns {Vec2} Interpolated vector
     */
    static lerp(v1, v2, t) {
        return new Vec2(
            v1.x + (v2.x - v1.x) * t,
            v1.y + (v2.y - v1.y) * t
        );
    }

    /**
     * Check equality with another vector (with tolerance)
     * @param {Vec2} other - Vector to compare
     * @param {number} epsilon - Tolerance for comparison
     * @returns {boolean}
     */
    equals(other, epsilon = 0.001) {
        return Math.abs(this.x - other.x) < epsilon && 
               Math.abs(this.y - other.y) < epsilon;
    }
}

/**
 * Cubic ease-in-out function for smooth animations
 * @param {number} t - Input value (0-1)
 * @returns {number} Eased value (0-1)
 */
export function easeInOutCubic(t) {
    return t < 0.5 ? 4 * t * t * t : 1 - Math.pow(-2 * t + 2, 3) / 2;
}

/**
 * Split a polygon by a line into two parts
 * @param {Vec2[]} polygon - Array of vertices
 * @param {Object} line - Line definition {nx, ny, c} where nx*x + ny*y + c = 0
 * @returns {Object} {staticPoly, movingPoly} - The two resulting polygons (or null if polygon doesn't cross line)
 */
export function splitPolygon(polygon, line) {
    let front = []; // Moving side (positive side of line)
    let back = [];  // Static side (negative side of line)
    
    // Line equation: nx*x + ny*y + c = 0
    // If > 0, point is in front (moving side)
    const distance = (p) => (line.nx * p.x) + (line.ny * p.y) + line.c;

    for (let i = 0; i < polygon.length; i++) {
        const current = polygon[i];
        const next = polygon[(i + 1) % polygon.length];
        
        const dCurrent = distance(current);
        const dNext = distance(next);

        // Add current point to appropriate side(s) with tolerance
        if (dCurrent >= -0.001) front.push(current);
        if (dCurrent <= 0.001) back.push(current);

        // Check for intersection between current and next
        if ((dCurrent > 0 && dNext < 0) || (dCurrent < 0 && dNext > 0)) {
            const t = dCurrent / (dCurrent - dNext);
            const intersection = Vec2.lerp(current, next, t);
            front.push(intersection);
            back.push(intersection);
        }
    }
    
    // A valid polygon needs at least 3 vertices
    if (front.length < 3) front = null;
    if (back.length < 3) back = null;

    return { staticPoly: back, movingPoly: front };
}

/**
 * Convert a polygon to a CSS clip-path string
 * @param {Vec2[]|null} poly - Array of vertices or null
 * @returns {string} CSS clip-path polygon string or 'none'
 */
export function polygonToClipPath(poly) {
    if (!poly) return 'none';
    return `polygon(${poly.map(p => `${p.x}px ${p.y}px`).join(', ')})`;
}

/**
 * Convert a polygon to a mirrored CSS clip-path string
 * Used for the back face which is rotated 180deg on Y axis
 * @param {Vec2[]|null} poly - Array of vertices or null
 * @param {number} paperSize - Size of the paper (for mirroring calculation)
 * @returns {string} CSS clip-path polygon string with mirrored X coordinates
 */
export function polygonToMirroredClipPath(poly, paperSize) {
    if (!poly) return 'none';
    // Mirror X coordinates around the center to compensate for rotateY(180deg)
    return `polygon(${poly.map(p => `${paperSize - p.x}px ${p.y}px`).join(', ')})`;
}

/**
 * Create initial square polygon for paper
 * @param {number} size - Size of the square
 * @returns {Vec2[]} Array of 4 vertices
 */
export function createSquarePolygon(size) {
    return [
        new Vec2(0, 0),
        new Vec2(size, 0),
        new Vec2(size, size),
        new Vec2(0, size)
    ];
}
