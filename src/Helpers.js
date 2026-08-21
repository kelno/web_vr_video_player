import {
    clearMediaSource,
    hasMediaSource,
    isCurrentMediaSource,
    setMediaSource,
} from "./mediaSource.mjs";

const LANG = require("./lang.json");

let selected_lang = "en";

export function videoSrcExists() {
    return hasMediaSource(document.getElementById("video"));
}

export function setVideoSrc(src) {
    return setMediaSource(document.getElementById("video"), src);
}

export function isCurrentVideoSrc(src) {
    return isCurrentMediaSource(document.getElementById("video"), src);
}

export function removeVideoSrc() {
    clearMediaSource(document.getElementById("video"));
}

export function getWordFromLang(key) {
    return LANG[selected_lang][key];
}
