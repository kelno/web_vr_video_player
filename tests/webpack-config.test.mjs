import assert from "node:assert/strict";
import { createRequire } from "node:module";
import test from "node:test";

const require = createRequire(import.meta.url);
const { parseIni, playerConfig } = require("../webpack.config.js");

test("keeps local library paths separate from web and player settings", () => {
    const config = parseIni(`
[library]
videos_path=/library

[web]
site_url_prefix=/vr-player

[player]
default_sbs_zoom=75.5
`);

    assert.equal(config.library.videos_path, "/library");
    assert.equal(config.web.site_url_prefix, "/vr-player");
    assert.deepEqual(playerConfig(config), { defaultSbsZoom: 75.5 });
});

test("uses the established SBS zoom when the setting is absent or invalid", () => {
    assert.deepEqual(playerConfig({}), { defaultSbsZoom: 100 });
    assert.deepEqual(
        playerConfig({ player: { default_sbs_zoom: "181" } }),
        { defaultSbsZoom: 100 }
    );
});
