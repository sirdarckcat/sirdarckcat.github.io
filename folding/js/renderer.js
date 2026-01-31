/**
 * DOM rendering logic for the folding engine
 * Handles building the 3D paper fold tree
 */

import { splitPolygon, polygonToClipPath, polygonToMirroredClipPath, createSquarePolygon } from './math.js';
import { getFoldLine, getRotationAxis } from './folds.js';

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
        const line = getFoldLine(fold.type, this.paperSize);
        const split = splitPolygon(geometry, line);
        
        // Case 1: No cut (Entirely static)
        if (!split.movingPoly) {
            return this.buildNode(folds, foldIndex + 1, split.staticPoly);
        }
        
        // Case 2: No cut (Entirely moving)
        if (!split.staticPoly) {
            const wrapper = document.createElement('div');
            wrapper.className = 'fold-group';
            const movingWrapper = this.createMovingWrapper(line, fold.currentAngle);
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
        
        const movingWrapper = this.createMovingWrapper(line, fold.currentAngle);
        const movingChild = this.buildNode(folds, foldIndex + 1, split.movingPoly);
        if (movingChild) movingWrapper.appendChild(movingChild);

        group.appendChild(staticWrapper);
        group.appendChild(movingWrapper);
        return group;
    }

    /**
     * Create a wrapper element for the moving part of a fold
     * @param {Object} lineDef - Fold line definition
     * @param {number} angle - Current fold angle in degrees
     * @returns {HTMLElement} Moving wrapper element
     */
    createMovingWrapper(lineDef, angle) {
        const div = document.createElement('div');
        div.className = 'fold-moving';
        
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
        front.className = 'face-front paper-leaf';
        front.style.clipPath = clip;
        
        const back = document.createElement('div');
        back.className = 'face-back paper-leaf';
        back.style.clipPath = mirroredClip;

        div.appendChild(back);
        div.appendChild(front);
        return div;
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
