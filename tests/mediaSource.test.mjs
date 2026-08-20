import assert from "node:assert/strict";
import test from "node:test";

import {
    clearMediaSource,
    hasMediaSource,
    setMediaSource,
} from "../src/mediaSource.mjs";

function createVideo(source = "") {
    const video = {
        attributes: source ? { src: source } : {},
        loadCalls: 0,
        pauseCalls: 0,
        playCalls: 0,
        getAttribute(name) {
            return this.attributes[name] ?? null;
        },
        removeAttribute(name) {
            delete this.attributes[name];
        },
        load() {
            this.loadCalls++;
        },
        pause() {
            this.pauseCalls++;
        },
        play() {
            this.playCalls++;
            return Promise.resolve();
        },
        set src(value) {
            this.attributes.src = value;
        },
    };

    return video;
}

test("sets and plays a new source once", async () => {
    const video = createVideo();

    await setMediaSource(video, "videos/example.mp4");

    assert.equal(video.getAttribute("src"), "videos/example.mp4");
    assert.equal(video.loadCalls, 1);
    assert.equal(video.pauseCalls, 0);
    assert.equal(video.playCalls, 1);
});

test("does not reload an already selected source", async () => {
    const video = createVideo("videos/example.mp4");

    await setMediaSource(video, "videos/example.mp4");

    assert.equal(video.loadCalls, 0);
    assert.equal(video.pauseCalls, 0);
    assert.equal(video.playCalls, 1);
});

test("clears an active source", () => {
    const video = createVideo("videos/example.mp4");

    clearMediaSource(video);

    assert.equal(hasMediaSource(video), false);
    assert.equal(video.pauseCalls, 1);
    assert.equal(video.loadCalls, 1);
});
