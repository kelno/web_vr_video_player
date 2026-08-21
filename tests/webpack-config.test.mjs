import assert from "node:assert/strict";
import { createRequire } from "node:module";
import test from "node:test";

const require = createRequire(import.meta.url);
const { parseIni, playerConfig } = require("../webpack.config.js");

test("reads the player zoom separately from video serving settings", () => {
    const config = parseIni(`
[videos]
videos_path=/library

[player]
default_sbs_zoom=75.5
`);

    assert.equal(config.videos.videos_path, "/library");
    assert.deepEqual(playerConfig(config), { defaultSbsZoom: 75.5 });
});

test("uses the established SBS zoom when the setting is absent or invalid", () => {
    assert.deepEqual(playerConfig({}), { defaultSbsZoom: 100 });
    assert.deepEqual(
        playerConfig({ player: { default_sbs_zoom: "181" } }),
        { defaultSbsZoom: 100 }
    );
});
