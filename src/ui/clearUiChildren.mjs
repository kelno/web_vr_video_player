/**
 * Dispose and remove each direct Three-Mesh-UI child from a container.
 *
 * Three-Mesh-UI's public `clear()` method traverses the child subtree and
 * releases its UI update state, geometry, and materials. Copy the children
 * first because `remove()` changes the live Object3D children collection.
 */
export default function clearUiChildren(container) {
    const children = [...container.children];

    for (const child of children) {
        if (typeof child.clear !== "function") {
            throw new TypeError("Expected a Three-Mesh-UI child with a clear() method.");
        }

        child.clear();
        container.remove(child);
    }
}
