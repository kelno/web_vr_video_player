const PREFERENCES_STORAGE_KEY = "web-vr-video-player.preferences";

function readPreferences() {
    try {
        const serializedPreferences = globalThis.localStorage?.getItem(
            PREFERENCES_STORAGE_KEY
        );
        if (serializedPreferences === null) {
            return {};
        }
        const preferences = JSON.parse(serializedPreferences);
        return preferences !== null && typeof preferences === "object" && !Array.isArray(preferences)
            ? preferences
            : {};
    } catch {
        // Storage can be unavailable in private browsing or blocked by policy.
        return {};
    }
}

export function loadPreference(name, { legacyStorageKey } = {}) {
    const preferences = readPreferences();
    if (Object.hasOwn(preferences, name)) {
        return preferences[name];
    }

    try {
        const legacyValue = legacyStorageKey
            ? globalThis.localStorage?.getItem(legacyStorageKey)
            : null;
        if (legacyValue !== null && legacyValue !== undefined) {
            savePreference(name, legacyValue);
            return legacyValue;
        }
    } catch {
        // Use the configured default when the old storage entry cannot be read.
    }
    return null;
}

export function savePreference(name, value) {
    try {
        const preferences = readPreferences();
        preferences[name] = value;
        globalThis.localStorage?.setItem(
            PREFERENCES_STORAGE_KEY,
            JSON.stringify(preferences)
        );
    } catch {
        // A failed save must not prevent the feature itself from working.
    }
}
