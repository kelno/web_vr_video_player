/**
 * Keep source changes on the one HTMLMediaElement used by the renderer. Using
 * the video element's `src` property avoids an empty nested <source> candidate
 * being selected before the user has chosen a video.
 */
export function hasMediaSource(video) {
    return Boolean(video.getAttribute("src"));
}

export function setMediaSource(video, source) {
    if (typeof source !== "string" || source.length === 0) {
        throw new TypeError("A media source must be a non-empty string.");
    }

    if (video.getAttribute("src") !== source) {
        if (hasMediaSource(video)) {
            video.pause();
        }

        video.src = source;
        video.load();
    }

    return video.play();
}

export function clearMediaSource(video) {
    if (!hasMediaSource(video)) {
        return;
    }

    video.pause();
    video.removeAttribute("src");
    video.load();
}
