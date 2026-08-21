import assert from "node:assert/strict";
import test from "node:test";

import {
    clearMediaSource,
    hasMediaSource,
    isCurrentMediaSource,
    setMediaSource,
} from "../src/mediaSource.mjs";

function createVideo(source = "") {
    const video = {
        attributes: source ? { src: source } : {},
        loadCalls: 0,
        pauseCalls: 0,
        playCalls: 0,
        currentSrc: source,
        ownerDocument: { baseURI: "https://player.example/" },
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
            this.currentSrc = value;
        },
    };

    return video;
}

test("sets and plays a new source once", async () => {
    const video = createVideo();

    const { sourceChanged, playback } = setMediaSource(
        video,
        "videos/example.mp4"
    );
    await playback;

    assert.equal(sourceChanged, true);
    assert.equal(video.getAttribute("src"), "videos/example.mp4");
    assert.equal(video.loadCalls, 1);
    assert.equal(video.pauseCalls, 0);
    assert.equal(video.playCalls, 1);
});

test("does not reload an already selected source", async () => {
    const video = createVideo("videos/example.mp4");

    const { sourceChanged, playback } = setMediaSource(
        video,
        "videos/example.mp4"
    );
    await playback;

    assert.equal(video.loadCalls, 0);
    assert.equal(sourceChanged, false);
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

test("matches the browser's active source after URL resolution", () => {
    const video = createVideo("https://player.example/media/example.mp4");

    assert.equal(
        isCurrentMediaSource(video, "/media/example.mp4"),
        true
    );
    assert.equal(
        isCurrentMediaSource(video, "/media/other.mp4"),
        false
    );
});
