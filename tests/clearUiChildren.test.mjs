import assert from "node:assert/strict";
import test from "node:test";

import clearUiChildren from "../src/ui/clearUiChildren.mjs";

function createChild(name, cleared) {
    return {
        name,
        clear() {
            cleared.push(name);
        },
    };
}

test("clears and removes every direct UI child", () => {
    const cleared = [];
    const first = createChild("first", cleared);
    const second = createChild("second", cleared);
    const container = {
        children: [first, second],
        remove(child) {
            this.children.splice(this.children.indexOf(child), 1);
        },
    };

    clearUiChildren(container);

    assert.deepEqual(cleared, ["first", "second"]);
    assert.deepEqual(container.children, []);
});
