# Vendored dependencies

## `three-mesh-ui-6.5.31.tgz`

`vendor/three-mesh-ui-6.5.31.tgz` is the exact package previously installed
from the `michal-repo/three-mesh-ui` fork at commit
`bd5a8970c50721e882c81f8a1b01ce0b77b1ade3`. Its package version is `6.5.31`.

It is committed so `npm ci` does not need Git or Git-over-SSH access on a
deployment server. Some managed deployment environments disable Git package
fetches, which would otherwise prevent a clean install.

The npm-registry release, `three-mesh-ui@6.5.4`, is older than this fork. When
tested with this project’s `three@0.185.1`, Webpack reported that
`BoxBufferGeometry` was no longer exported by Three.js and the player compiled
with problems instead of rendering its UI. Keep this tarball until a compatible
maintained replacement has been verified.

Before removing it:

1. Test the candidate package with this project’s current Three.js version.
2. Confirm `npm run build` has no ThreeMeshUI compatibility warnings.
3. Test the file browser, playback controls, and WebXR mode on the target
   desktop browser and headset.
4. Change `package.json` to the registry dependency, regenerate the lockfile,
   then remove this tarball and this note.

The package is MIT licensed; its own `LICENSE` remains inside the tarball.
