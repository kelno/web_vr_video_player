import FontJSON from "../assets/fonts/Roboto-Regular-msdf.json";

const supportedCharacters = new Set(FontJSON.info.charset);

/**
 * ThreeMeshUI does not gracefully handle a character missing from its MSDF
 * font: it logs a warning, then throws while looking up that glyph. Library
 * labels come from user-controlled filenames, so replace only unsupported
 * display characters and leave the original file paths untouched.
 */
export function sanitizeFontText(value) {
    return Array.from(String(value)).map((character) => {
        return supportedCharacters.has(character) || /\s/.test(character)
            ? character
            : "?";
    }).join("");
}
