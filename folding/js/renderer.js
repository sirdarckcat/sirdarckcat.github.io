/**
 * DOM rendering logic for the folding engine
 * Handles building the 3D paper fold tree
 */

import { splitPolygon, polygonToClipPath, polygonToMirroredClipPath, createSquarePolygon } from './math.js';
import { getFoldLine, getRotationAxis, getEffectiveAngle, FOLD_DIRECTION } from './folds.js';

/**
 * Renderer class for the folding visualization
 */
export class FoldingRenderer {
    /**
     * @param {HTMLElement} rootElement - The root DOM element for rendering
     * @param {number} paperSize - Size of the paper in pixels
     */
    constructor(rootElement, paperSize = 300) {
        this.rootElement = rootElement;
        this.paperSize = paperSize;
        this.showCreasePattern = false; // Toggle for crease pattern overlay
    }

    /**
     * Render the complete fold tree
     * @param {Object[]} folds - Array of fold objects
     */
    render(folds) {
        const initialPoly = createSquarePolygon(this.paperSize);
        this.rootElement.innerHTML = '';
        const tree = this.buildNode(folds, 0, initialPoly);
        if (tree) {
            this.rootElement.appendChild(tree);
        }
        
        // Optionally render crease pattern overlay
        if (this.showCreasePattern) {
            this.renderCreasePattern(folds);
        }
    }

    /**
     * Recursively build a fold node
     * @param {Object[]} folds - Array of fold objects
     * @param {number} foldIndex - Current fold index
     * @param {Vec2[]} geometry - Current polygon geometry
     * @returns {HTMLElement|null} DOM element or null
     */
    buildNode(folds, foldIndex, geometry) {
        if (foldIndex >= folds.length || !geometry) {
            return this.createLeaf(geometry);
        }

        const fold = folds[foldIndex];
        // Use position if available, default to 50 (center)
        const position = fold.position !== undefined ? fold.position : 50;
        const line = getFoldLine(fold.type, this.paperSize, position);
        const split = splitPolygon(geometry, line);
        
        // Get effective angle (considering mountain/valley direction)
        const effectiveAngle = fold.direction === FOLD_DIRECTION.VALLEY 
            ? -Math.abs(fold.currentAngle) 
            : Math.abs(fold.currentAngle);
        
        // Case 1: No cut (Entirely static)
        if (!split.movingPoly) {
            return this.buildNode(folds, foldIndex + 1, split.staticPoly);
        }
        
        // Case 2: No cut (Entirely moving)
        if (!split.staticPoly) {
            const wrapper = document.createElement('div');
            wrapper.className = 'fold-group';
            const movingWrapper = this.createMovingWrapper(line, effectiveAngle, fold);
            const child = this.buildNode(folds, foldIndex + 1, split.movingPoly);
            if (child) movingWrapper.appendChild(child);
            wrapper.appendChild(movingWrapper);
            return wrapper;
        }

        // Case 3: Standard fold (polygon is split)
        const group = document.createElement('div');
        group.className = 'fold-group';

        const staticWrapper = document.createElement('div');
        staticWrapper.className = 'fold-static';
        const staticChild = this.buildNode(folds, foldIndex + 1, split.staticPoly);
        if (staticChild) staticWrapper.appendChild(staticChild);
        
        const movingWrapper = this.createMovingWrapper(line, effectiveAngle, fold);
        const movingChild = this.buildNode(folds, foldIndex + 1, split.movingPoly);
        if (movingChild) movingWrapper.appendChild(movingChild);

        group.appendChild(staticWrapper);
        group.appendChild(movingWrapper);
        return group;
    }

    /**
     * Create a wrapper element for the moving part of a fold
     * @param {Object} lineDef - Fold line definition
     * @param {number} angle - Current fold angle in degrees (can be negative for valley)
     * @param {Object} fold - The fold object (for additional styling)
     * @returns {HTMLElement} Moving wrapper element
     */
    createMovingWrapper(lineDef, angle, fold) {
        const div = document.createElement('div');
        div.className = 'fold-moving';
        
        // Add direction class for potential styling
        if (fold && fold.direction) {
            div.classList.add(`fold-${fold.direction}`);
        }
        
        const axis = getRotationAxis(lineDef.axis);
        div.style.transformOrigin = lineDef.origin;
        div.style.transform = `rotate3d(${axis}, -${angle}deg)`;
        return div;
    }

    /**
     * Create a leaf element (actual paper face with front and back)
     * @param {Vec2[]} geometry - Polygon geometry for clipping
     * @returns {HTMLElement} Leaf element with front and back faces
     */
    createLeaf(geometry) {
        const div = document.createElement('div');
        div.className = 'paper-leaf';
        
        const clip = polygonToClipPath(geometry);
        const mirroredClip = polygonToMirroredClipPath(geometry, this.paperSize);
        
        const front = document.createElement('div');
        front.className = 'face-front';
        front.style.clipPath = clip;
        
        const back = document.createElement('div');
        back.className = 'face-back';
        back.style.clipPath = mirroredClip;

        div.appendChild(back);
        div.appendChild(front);
        return div;
    }

    /**
     * Render crease pattern overlay (optional visualization)
     * @param {Object[]} folds - Array of fold objects
     */
    renderCreasePattern(folds) {
        const overlay = document.createElement('div');
        overlay.className = 'crease-pattern-overlay';
        overlay.style.cssText = `
            position: absolute;
            top: 0; left: 0;
            width: 100%; height: 100%;
            pointer-events: none;
            z-index: 100;
        `;
        
        folds.forEach((fold, index) => {
            const position = fold.position !== undefined ? fold.position : 50;
            const line = getFoldLine(fold.type, this.paperSize, position);
            
            if (line.p1 && line.p2) {
                const creaseLine = document.createElement('div');
                creaseLine.className = `crease-line crease-${fold.direction || 'mountain'}`;
                
                const x1 = line.p1.x, y1 = line.p1.y;
                const x2 = line.p2.x, y2 = line.p2.y;
                const length = Math.sqrt((x2-x1)**2 + (y2-y1)**2);
                const angle = Math.atan2(y2-y1, x2-x1) * 180 / Math.PI;
                
                creaseLine.style.cssText = `
                    position: absolute;
                    left: ${x1}px;
                    top: ${y1}px;
                    width: ${length}px;
                    height: 2px;
                    background: ${fold.direction === 'valley' ? '#ef4444' : '#22c55e'};
                    transform-origin: 0 50%;
                    transform: rotate(${angle}deg);
                    opacity: 0.7;
                `;
                
                overlay.appendChild(creaseLine);
            }
        });
        
        this.rootElement.appendChild(overlay);
    }

    /**
     * Toggle crease pattern visibility
     * @param {boolean} show - Whether to show the crease pattern
     */
    setCreasePatternVisible(show) {
        this.showCreasePattern = show;
    }
}

/**
 * Update the turntable rotation
 * @param {HTMLElement} turntable - Turntable element
 * @param {Object} rotation - Rotation state {x, y}
 */
export function updateTurntable(turntable, rotation) {
    turntable.style.transform = `rotateX(${rotation.x}deg) rotateY(${rotation.y}deg)`;
}
