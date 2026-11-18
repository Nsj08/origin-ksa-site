# Third-party licenses

Inventory captured 18 November 2026 in Riyadh. It covers the final Astro 7.4.12 lockfile, the Python 3.12 verification environment and the separate QA tools.

| Input | SHA-256 |
| --- | --- |
| [pnpm-lock.yaml](../pnpm-lock.yaml) | `e8df3e5b867eec166bf6fcfd14d5838d22b8a992c5c2f3444ebbbed1724f6e36` |
| [requirements.txt](../requirements.txt) | `47d023d1bad7f9bc4bfb8115f088aad1f68a7210c12f1b1ddb8ecf63c4e82f4a` |
| [QA package-lock.json](../scripts/qa/package-lock.json) | `9c9421d4dd8ad1c4ec9108877ac223dd870ecf845fccc5896eb92200f6d5e28f` |

## Browser assets and notices

- **IBM Plex Sans and IBM Plex Sans Arabic, Fontsource 5.3.0.** The compiled CSS references the local Latin and Arabic font subsets, with WOFF and WOFF2 files. Both packages declare SIL Open Font License 1.1. The published copies preserve each font’s own copyright and complete license. [IBM Plex Sans](../public/licenses/ibm-plex-sans-OFL-1.1.txt) · [IBM Plex Sans Arabic](../public/licenses/ibm-plex-sans-arabic-OFL-1.1.txt)
- **Fuse.js 7.5.0.** The search script bundles this version in the static browser JS. Its package metadata, upstream license file and distributed module all specify Apache-2.0. The site publishes the exact license and preserves the module’s copyright header as a plain-text notice. [Apache 2.0 text](../public/licenses/fuse-js-Apache-2.0.txt) · [Copyright notice](../public/licenses/fuse-js-notice.txt)
- Both versions of Terms of Use link to these notices. The dependency inventory below identifies packages used in the browser. Astro, Vite, native canvas libraries, type checking and the Python pipeline run at build or verification time. The static artifact contains their generated outputs where applicable, such as CSS, HTML, data and PNG cards.
- Node's ICU/CLDR Arabic region labels supplied an input to localized trade data. The Unicode license notice and version details are maintained with the repository data pipeline. [Unicode license](../pipeline/UNICODE_LICENSE.txt) · [Unicode CLDR language and territory data](https://cldr.unicode.org/)

## JavaScript lockfile scope

All 346 package-version entries in the lockfile's `packages` section were matched to license metadata. Installed metadata supplied 269 records. Exact-version npm registry metadata supplied the other 77, including optional packages for Linux, Windows, Android and other targets. Each registry result agreed with the lockfile's integrity hash. The license counts are 305 MIT, 14 ISC, 8 BSD-2-Clause, 7 Apache-2.0, 4 BSD-3-Clause, 3 BlueOak-1.0.0, 2 OFL-1.1, 2 CC0-1.0 and 1 0BSD. Platform-restricted optional entries appear with their lockfile conditions. These are package-level declarations. They describe the packages, with separate upstream notices applying to bundled native components in the local build tools. [npm registry](https://registry.npmjs.org/) · [pnpm lockfile](../pnpm-lock.yaml)

The Blue Oak packages are `common-ancestor-path@2.0.0`, `lru-cache@11.5.3` and `sax@1.6.1`. The CC0 entries are the two `mdn-data` versions and the 0BSD entry is `tslib@2.9.1`. All six run at build or verification time. The OFL fonts are the two explicitly redistributed font packages. The lockfile excludes the Vite dependency on the optional Lightning CSS engine, and the build selects PostCSS. [Astro config](../astro.config.mjs)

## Python 3.12

The trade pipeline uses the standard library. The Python lock pins JSON validation and test libraries, including every transitive dependency and platform markers. CI verifies the downloaded wheel hashes during installation. The license metadata below was read from Python 3.12 installations and the published Colorama release.

| Package | Version | License | Use |
| --- | --- | --- | --- |
| jsonschema | 4.26.0 | MIT | Required, data validation |
| pytest | 9.2.0 | MIT | Required, unit testing |
| attrs | 26.1.0 | MIT | jsonschema and referencing |
| iniconfig | 2.3.1 | MIT | pytest |
| jsonschema-specifications | 2025.9.1 | MIT | jsonschema |
| packaging | 26.3 | Apache-2.0 OR BSD-2-Clause | pytest |
| pluggy | 1.7.0 | MIT | pytest |
| Pygments | 2.21.0 | BSD-2-Clause | pytest |
| referencing | 0.37.0 | MIT | jsonschema and jsonschema-specifications |
| rpds-py | 2026.9.1 | MIT | jsonschema and referencing |
| typing_extensions | 4.16.0 | PSF-2.0 | referencing on Python 3.12 |
| colorama | 0.4.6 | BSD-3-Clause | pytest on Windows, verified via release metadata |

The local work also used pypdf 7.1.0 (BSD-3-Clause) to read the WCO PDF and PyYAML 6.0.3 (MIT) to parse the lockfile for this audit. They are standalone tooling. Python wheels, libraries and tooling remain outside the generated site. [Python requirements](../requirements.txt) · [Colorama release](https://pypi.org/project/colorama/0.4.6/)

## Separate QA environment

CI installs axe-core 4.14.1 (MPL-2.0), Lighthouse CI 0.16.1 (Apache-2.0) and html-validate 11.21.1 (MIT) using `npm ci --prefix scripts/qa`. The QA lock records 350 package paths, including optional platform packages and their integrity hashes. Playwright is pinned in the site lock. Chromium, Firefox, WebKit and GitHub Actions are external verification tools. The QA packages and verification browsers run outside the published site. [QA lock](../scripts/qa/package-lock.json) · [CI workflow](../.github/workflows/site.yml)

In addition to MIT, ISC, Apache and BSD licenses, the QA lock records BlueOak-1.0.0, PSF-2.0, MPL-2.0, MIT OR CC0-1.0, FSL-1.1-Apache-2.0 and 0BSD. The frozen QA installation reported zero known vulnerabilities at the low audit threshold on 18 November 2026. An OSV batch check of the exact Python verification pins also returned zero advisories on that date. [OSV](https://osv.dev/)

## Security audit and preview

GitHub withdrew GHSA-fc5q-39xc-vjpf on 18 November 2026. CVE.org still listed the CVE as published, NVD listed it as awaiting analysis, and npm continued to flag the official Picomatch versions 2.3.2 and 4.0.7. The maintainers listed no patched official release. [GitHub advisory](https://github.com/advisories/GHSA-fc5q-39xc-vjpf) · [Maintainer response](https://github.com/micromatch/picomatch/pull/235#issuecomment-6315749381) · [CVE.org](https://www.cve.org/CVERecord?id=CVE-2026-112366) · [NVD](https://nvd.nist.gov/vuln/detail/CVE-2026-112366)

The two exact version overrides replace both release lines with the MIT-licensed fork `@ryotsu/picomatch@4.0.7-a`. The patched parser removes the outer repeat when it recognizes a single branch with an unrestricted star and treats unsupported risky forms as literals. The fork retains Picomatch’s option to turn off the recursion safeguard and includes changes to POSIX bracket negation and globstar matching. The site builds from literal file patterns and uses Fuse.js for public search. The fork does not ship in the static site. Remove the overrides when Astro’s dependency tree resolves to an appropriate official release, then rerun the frozen build and both audits. [Dependency overrides](../pnpm-workspace.yaml) · [Fork source](https://github.com/ryotsu-kankichi/secured-picomatch/tree/3ab5a7627d480259e3d9ca67fbc14c125d374f0e)

npm verified the fork’s registry signature and provenance attestation. Its published executable files, manifest and license matched the attested source commit `3ab5a7627d480259e3d9ca67fbc14c125d374f0e`. The lock pins `sha512-JroBFEmaejC7szGSfqOhF1QZHLKvX2wTA1+fWyfkpy3BjzdQKNPLKa2FtgeKVUDy5/UPUNkXEeCHJ5ZRBMLTVA==`. The unmodified `pnpm audit --audit-level low` reported zero known vulnerabilities for the updated graph. [Registry metadata](https://registry.npmjs.org/@ryotsu%2fpicomatch/4.0.7-a) · [npm provenance](https://registry.npmjs.org/-/npm/v1/attestations/@ryotsu%2fpicomatch@4.0.7-a) · [CI workflow](../.github/workflows/site.yml)

An isolated temporary build used `SITE_URL=https://nsj08.github.io/origin-ksa/`. The build check passed on all 60 HTML pages and resolved their internal links and fragments. Additional checks verified 60 canonicals, 312 hreflang, Open Graph and CSS references, the sitemap and robots pointer, along with all four notices in both languages. Local generated targets resolved beneath `/origin-ksa/`. The production `dist` directory was outside the test.

## Reproduce the package metadata

Use `pnpm install --frozen-lockfile` to materialize this machine's dependencies, then parse the `packages` mapping in `pnpm-lock.yaml`. The optional PyYAML 6.0.3 utility can parse the file in a disposable Python environment. Enumerate package names and versions by splitting each key on the last `@`. Read each physical package's `package.json` under `node_modules/.pnpm/*/node_modules`, matching its `name` and `version` to the key. For any missing entry, request `https://registry.npmjs.org/<encoded-name>/<version>` and compare its `dist.integrity` with the lockfile's `resolution.integrity`. The table records the `license` declaration and any `os`, `cpu` or `libc` conditions in the lock. The metadata source column can vary by host. Versions, conditions and license declarations can be checked against the same lockfile digest.

For Python, install `requirements.txt` with `python -m pip install --require-hashes --only-binary=:all: -r requirements.txt` into a fresh 3.12 environment and inspect `importlib.metadata` for each distribution's version and `License-Expression` or `License` field. `Requires-Dist` records the Windows-only Colorama dependency. To repeat the advisory check, run `pnpm audit --audit-level low --json` against the final lockfile. Advisories can change after the recorded date.

## Complete pnpm package inventory

| Package | Version | License | Use | Platform conditions | Metadata |
| --- | --- | --- | --- | --- | --- |
| `@astrojs/astro2tsx` | 0.1.4 | MIT | Build or test | — | installed |
| `@astrojs/check` | 0.9.12 | MIT | Build or test | — | installed |
| `@astrojs/compiler-binding-android-arm64` | 0.5.3 | MIT | Build or test | os android; cpu arm64 | registry |
| `@astrojs/compiler-binding-darwin-arm64` | 0.5.3 | MIT | Build or test | os darwin; cpu arm64 | installed |
| `@astrojs/compiler-binding-darwin-x64` | 0.5.3 | MIT | Build or test | os darwin; cpu x64 | registry |
| `@astrojs/compiler-binding-linux-arm64-gnu` | 0.5.3 | MIT | Build or test | os linux; cpu arm64; libc glibc | registry |
| `@astrojs/compiler-binding-linux-arm64-musl` | 0.5.3 | MIT | Build or test | os linux; cpu arm64; libc musl | registry |
| `@astrojs/compiler-binding-linux-x64-gnu` | 0.5.3 | MIT | Build or test | os linux; cpu x64; libc glibc | registry |
| `@astrojs/compiler-binding-linux-x64-musl` | 0.5.3 | MIT | Build or test | os linux; cpu x64; libc musl | registry |
| `@astrojs/compiler-binding-wasm32-wasi` | 0.5.3 | MIT | Build or test | cpu wasm32 | registry |
| `@astrojs/compiler-binding-win32-arm64-msvc` | 0.5.3 | MIT | Build or test | os win32; cpu arm64 | registry |
| `@astrojs/compiler-binding-win32-x64-msvc` | 0.5.3 | MIT | Build or test | os win32; cpu x64 | registry |
| `@astrojs/compiler-binding` | 0.5.3 | MIT | Build or test | — | installed |
| `@astrojs/compiler-rs` | 0.5.3 | MIT | Build or test | — | installed |
| `@astrojs/internal-helpers` | 0.13.2 | MIT | Build or test | — | installed |
| `@astrojs/language-server` | 2.17.3 | MIT | Build or test | — | installed |
| `@astrojs/markdown-satteri` | 0.4.10 | MIT | Build or test | — | installed |
| `@astrojs/prism` | 4.1.2 | MIT | Build or test | — | installed |
| `@astrojs/runtime` | 0.1.1 | MIT | Build or test | — | installed |
| `@astrojs/telemetry` | 3.4.2 | MIT | Build or test | — | installed |
| `@astrojs/vite-plugin-astro` | 0.1.3 | MIT | Build or test | — | installed |
| `@astrojs/yaml2ts` | 0.2.4 | MIT | Build or test | — | installed |
| `@babel/helper-string-parser` | 7.29.14 | MIT | Build or test | — | installed |
| `@babel/helper-validator-identifier` | 7.29.7 | MIT | Build or test | — | installed |
| `@babel/parser` | 7.29.14 | MIT | Build or test | — | installed |
| `@babel/types` | 7.29.14 | MIT | Build or test | — | installed |
| `@bruits/satteri-android-arm64` | 0.11.7 | MIT | Build or test | os android; cpu arm64 | registry |
| `@bruits/satteri-darwin-arm64` | 0.11.7 | MIT | Build or test | os darwin; cpu arm64 | installed |
| `@bruits/satteri-darwin-x64` | 0.11.7 | MIT | Build or test | os darwin; cpu x64 | registry |
| `@bruits/satteri-freebsd-x64` | 0.11.7 | MIT | Build or test | os freebsd; cpu x64 | registry |
| `@bruits/satteri-linux-arm64-gnu` | 0.11.7 | MIT | Build or test | os linux; cpu arm64; libc glibc | registry |
| `@bruits/satteri-linux-arm64-musl` | 0.11.7 | MIT | Build or test | os linux; cpu arm64; libc musl | registry |
| `@bruits/satteri-linux-x64-gnu` | 0.11.7 | MIT | Build or test | os linux; cpu x64; libc glibc | registry |
| `@bruits/satteri-linux-x64-musl` | 0.11.7 | MIT | Build or test | os linux; cpu x64; libc musl | registry |
| `@bruits/satteri-wasm32-wasi` | 0.11.7 | MIT | Build or test | cpu wasm32 | registry |
| `@bruits/satteri-win32-arm64-msvc` | 0.11.7 | MIT | Build or test | os win32; cpu arm64 | registry |
| `@bruits/satteri-win32-x64-msvc` | 0.11.7 | MIT | Build or test | os win32; cpu x64 | registry |
| `@capsizecss/unpack` | 4.0.1 | MIT | Build or test | — | installed |
| `@clack/core` | 1.6.0 | MIT | Build or test | — | installed |
| `@clack/prompts` | 1.9.0 | MIT | Build or test | — | installed |
| `@emmetio/abbreviation` | 2.3.3 | MIT | Build or test | — | installed |
| `@emmetio/css-abbreviation` | 2.1.8 | MIT | Build or test | — | installed |
| `@emmetio/css-parser` | 0.4.1 | MIT | Build or test | — | installed |
| `@emmetio/html-matcher` | 1.3.0 | ISC | Build or test | — | installed |
| `@emmetio/scanner` | 1.0.4 | MIT | Build or test | — | installed |
| `@emmetio/stream-reader-utils` | 0.1.0 | MIT | Build or test | — | installed |
| `@emmetio/stream-reader` | 2.2.0 | MIT | Build or test | — | installed |
| `@emnapi/core` | 1.11.1 | MIT | Build or test | — | registry |
| `@emnapi/core` | 1.11.3 | MIT | Build or test | — | installed |
| `@emnapi/core` | 2.0.0-beta.2 | MIT | Build or test | — | registry |
| `@emnapi/runtime` | 1.11.1 | MIT | Build or test | — | registry |
| `@emnapi/runtime` | 1.11.3 | MIT | Build or test | — | installed |
| `@emnapi/runtime` | 2.0.0-beta.2 | MIT | Build or test | — | registry |
| `@emnapi/wasi-threads` | 1.2.2 | MIT | Build or test | — | registry |
| `@emnapi/wasi-threads` | 1.2.3 | MIT | Build or test | — | installed |
| `@emnapi/wasi-threads` | 2.2.0 | MIT | Build or test | — | registry |
| `@esbuild/aix-ppc64` | 0.28.2 | MIT | Build or test | os aix; cpu ppc64 | registry |
| `@esbuild/android-arm64` | 0.28.2 | MIT | Build or test | os android; cpu arm64 | registry |
| `@esbuild/android-arm` | 0.28.2 | MIT | Build or test | os android; cpu arm | registry |
| `@esbuild/android-x64` | 0.28.2 | MIT | Build or test | os android; cpu x64 | registry |
| `@esbuild/darwin-arm64` | 0.28.2 | MIT | Build or test | os darwin; cpu arm64 | installed |
| `@esbuild/darwin-x64` | 0.28.2 | MIT | Build or test | os darwin; cpu x64 | registry |
| `@esbuild/freebsd-arm64` | 0.28.2 | MIT | Build or test | os freebsd; cpu arm64 | registry |
| `@esbuild/freebsd-x64` | 0.28.2 | MIT | Build or test | os freebsd; cpu x64 | registry |
| `@esbuild/linux-arm64` | 0.28.2 | MIT | Build or test | os linux; cpu arm64 | registry |
| `@esbuild/linux-arm` | 0.28.2 | MIT | Build or test | os linux; cpu arm | registry |
| `@esbuild/linux-ia32` | 0.28.2 | MIT | Build or test | os linux; cpu ia32 | registry |
| `@esbuild/linux-loong64` | 0.28.2 | MIT | Build or test | os linux; cpu loong64 | registry |
| `@esbuild/linux-mips64el` | 0.28.2 | MIT | Build or test | os linux; cpu mips64el | registry |
| `@esbuild/linux-ppc64` | 0.28.2 | MIT | Build or test | os linux; cpu ppc64 | registry |
| `@esbuild/linux-riscv64` | 0.28.2 | MIT | Build or test | os linux; cpu riscv64 | registry |
| `@esbuild/linux-s390x` | 0.28.2 | MIT | Build or test | os linux; cpu s390x | registry |
| `@esbuild/linux-x64` | 0.28.2 | MIT | Build or test | os linux; cpu x64 | registry |
| `@esbuild/netbsd-arm64` | 0.28.2 | MIT | Build or test | os netbsd; cpu arm64 | registry |
| `@esbuild/netbsd-x64` | 0.28.2 | MIT | Build or test | os netbsd; cpu x64 | registry |
| `@esbuild/openbsd-arm64` | 0.28.2 | MIT | Build or test | os openbsd; cpu arm64 | registry |
| `@esbuild/openbsd-x64` | 0.28.2 | MIT | Build or test | os openbsd; cpu x64 | registry |
| `@esbuild/openharmony-arm64` | 0.28.2 | MIT | Build or test | os openharmony; cpu arm64 | registry |
| `@esbuild/sunos-x64` | 0.28.2 | MIT | Build or test | os sunos; cpu x64 | registry |
| `@esbuild/win32-arm64` | 0.28.2 | MIT | Build or test | os win32; cpu arm64 | registry |
| `@esbuild/win32-ia32` | 0.28.2 | MIT | Build or test | os win32; cpu ia32 | registry |
| `@esbuild/win32-x64` | 0.28.2 | MIT | Build or test | os win32; cpu x64 | registry |
| `@fontsource/ibm-plex-sans-arabic` | 5.3.0 | OFL-1.1 | Browser | — | installed |
| `@fontsource/ibm-plex-sans` | 5.3.0 | OFL-1.1 | Browser | — | installed |
| `@jridgewell/sourcemap-codec` | 1.6.0 | MIT | Build or test | — | installed |
| `@napi-rs/canvas-android-arm64` | 0.1.100 | MIT | Build or test | os android; cpu arm64 | registry |
| `@napi-rs/canvas-darwin-arm64` | 0.1.100 | MIT | Build or test | os darwin; cpu arm64 | installed |
| `@napi-rs/canvas-darwin-x64` | 0.1.100 | MIT | Build or test | os darwin; cpu x64 | registry |
| `@napi-rs/canvas-linux-arm-gnueabihf` | 0.1.100 | MIT | Build or test | os linux; cpu arm | registry |
| `@napi-rs/canvas-linux-arm64-gnu` | 0.1.100 | MIT | Build or test | os linux; cpu arm64; libc glibc | registry |
| `@napi-rs/canvas-linux-arm64-musl` | 0.1.100 | MIT | Build or test | os linux; cpu arm64; libc musl | registry |
| `@napi-rs/canvas-linux-riscv64-gnu` | 0.1.100 | MIT | Build or test | os linux; cpu riscv64; libc glibc | registry |
| `@napi-rs/canvas-linux-x64-gnu` | 0.1.100 | MIT | Build or test | os linux; cpu x64; libc glibc | registry |
| `@napi-rs/canvas-linux-x64-musl` | 0.1.100 | MIT | Build or test | os linux; cpu x64; libc musl | registry |
| `@napi-rs/canvas-win32-arm64-msvc` | 0.1.100 | MIT | Build or test | os win32; cpu arm64 | registry |
| `@napi-rs/canvas-win32-x64-msvc` | 0.1.100 | MIT | Build or test | os win32; cpu x64 | registry |
| `@napi-rs/canvas` | 0.1.100 | MIT | Build or test | — | installed |
| `@napi-rs/wasm-runtime` | 1.2.4 | MIT | Build or test | — | installed |
| `@napi-rs/wasm-runtime` | 1.2.6 | MIT | Build or test | — | registry |
| `@napi-rs/wasm-runtime` | 1.2.7 | MIT | Build or test | — | registry |
| `@oslojs/encoding` | 1.1.0 | MIT | Build or test | — | installed |
| `@oxc-project/types` | 0.156.0 | MIT | Build or test | — | installed |
| `@playwright/test` | 1.65.1 | Apache-2.0 | Build or test | — | installed |
| `@rolldown/binding-android-arm-eabi` | 1.2.19 | MIT | Build or test | os android; cpu arm | registry |
| `@rolldown/binding-android-arm64` | 1.2.19 | MIT | Build or test | os android; cpu arm64 | registry |
| `@rolldown/binding-darwin-arm64` | 1.2.19 | MIT | Build or test | os darwin; cpu arm64 | installed |
| `@rolldown/binding-darwin-x64` | 1.2.19 | MIT | Build or test | os darwin; cpu x64 | registry |
| `@rolldown/binding-freebsd-x64` | 1.2.19 | MIT | Build or test | os freebsd; cpu x64 | registry |
| `@rolldown/binding-linux-arm-gnueabihf` | 1.2.19 | MIT | Build or test | os linux; cpu arm | registry |
| `@rolldown/binding-linux-arm64-gnu` | 1.2.19 | MIT | Build or test | os linux; cpu arm64; libc glibc | registry |
| `@rolldown/binding-linux-arm64-musl` | 1.2.19 | MIT | Build or test | os linux; cpu arm64; libc musl | registry |
| `@rolldown/binding-linux-ppc64-gnu` | 1.2.19 | MIT | Build or test | os linux; cpu ppc64; libc glibc | registry |
| `@rolldown/binding-linux-s390x-gnu` | 1.2.19 | MIT | Build or test | os linux; cpu s390x; libc glibc | registry |
| `@rolldown/binding-linux-x64-gnu` | 1.2.19 | MIT | Build or test | os linux; cpu x64; libc glibc | registry |
| `@rolldown/binding-linux-x64-musl` | 1.2.19 | MIT | Build or test | os linux; cpu x64; libc musl | registry |
| `@rolldown/binding-openharmony-arm64` | 1.2.19 | MIT | Build or test | os openharmony; cpu arm64 | registry |
| `@rolldown/binding-wasm32-wasi` | 1.2.19 | MIT | Build or test | cpu wasm32 | registry |
| `@rolldown/binding-win32-arm64-msvc` | 1.2.19 | MIT | Build or test | os win32; cpu arm64 | registry |
| `@rolldown/binding-win32-x64-msvc` | 1.2.19 | MIT | Build or test | os win32; cpu x64 | registry |
| `@rolldown/pluginutils` | 1.1.1 | MIT | Build or test | — | installed |
| `@ryotsu/picomatch` | 4.0.7-a | MIT | Build or test | — | installed |
| `@shikijs/core` | 4.6.0 | MIT | Build or test | — | installed |
| `@shikijs/engine-javascript` | 4.6.0 | MIT | Build or test | — | installed |
| `@shikijs/engine-oniguruma` | 4.6.0 | MIT | Build or test | — | installed |
| `@shikijs/langs` | 4.6.0 | MIT | Build or test | — | installed |
| `@shikijs/primitive` | 4.6.0 | MIT | Build or test | — | installed |
| `@shikijs/themes` | 4.6.0 | MIT | Build or test | — | installed |
| `@shikijs/types` | 4.6.0 | MIT | Build or test | — | installed |
| `@shikijs/vscode-textmate` | 10.1.0 | MIT | Build or test | — | installed |
| `@tybys/wasm-util` | 0.10.5 | MIT | Build or test | — | installed |
| `@types/estree-jsx` | 1.0.5 | MIT | Build or test | — | installed |
| `@types/estree` | 1.0.10 | MIT | Build or test | — | installed |
| `@types/hast` | 3.0.5 | MIT | Build or test | — | installed |
| `@types/mdast` | 4.0.4 | MIT | Build or test | — | installed |
| `@types/nlcst` | 2.0.3 | MIT | Build or test | — | installed |
| `@types/node` | 24.19.2 | MIT | Build or test | — | installed |
| `@types/unist` | 3.0.3 | MIT | Build or test | — | installed |
| `@ungap/structured-clone` | 1.4.0 | ISC | Build or test | — | installed |
| `@volar/kit` | 2.4.31 | MIT | Build or test | — | installed |
| `@volar/language-core` | 2.4.31 | MIT | Build or test | — | installed |
| `@volar/language-server` | 2.4.31 | MIT | Build or test | — | installed |
| `@volar/language-service` | 2.4.31 | MIT | Build or test | — | installed |
| `@volar/source-map` | 2.4.31 | MIT | Build or test | — | installed |
| `@volar/typescript` | 2.4.31 | MIT | Build or test | — | installed |
| `@vscode/emmet-helper` | 2.11.0 | MIT | Build or test | — | installed |
| `@vscode/l10n` | 0.0.18 | MIT | Build or test | — | installed |
| `ajv-draft-04` | 1.0.0 | MIT | Build or test | — | installed |
| `ajv-i18n` | 4.2.0 | MIT | Build or test | — | installed |
| `ajv` | 8.20.0 | MIT | Build or test | — | installed |
| `am-i-vibing` | 0.5.0 | MIT | Build or test | — | installed |
| `ansi-regex` | 6.6.0 | MIT | Build or test | — | installed |
| `ansi-styles` | 6.2.3 | MIT | Build or test | — | installed |
| `anymatch` | 3.1.3 | ISC | Build or test | — | installed |
| `aria-query` | 5.3.2 | Apache-2.0 | Build or test | — | installed |
| `astro` | 7.4.12 | MIT | Build or test | — | installed |
| `axobject-query` | 4.1.0 | Apache-2.0 | Build or test | — | installed |
| `bail` | 2.0.2 | MIT | Build or test | — | installed |
| `boolbase` | 1.0.0 | ISC | Build or test | — | installed |
| `ccount` | 2.0.1 | MIT | Build or test | — | installed |
| `character-entities-html4` | 2.1.0 | MIT | Build or test | — | installed |
| `character-entities-legacy` | 3.0.0 | MIT | Build or test | — | installed |
| `chokidar` | 5.0.0 | MIT | Build or test | — | installed |
| `ci-info` | 4.5.0 | MIT | Build or test | — | installed |
| `cliui` | 9.0.1 | ISC | Build or test | — | installed |
| `clsx` | 2.1.1 | MIT | Build or test | — | installed |
| `comma-separated-tokens` | 2.0.3 | MIT | Build or test | — | installed |
| `commander` | 11.1.0 | MIT | Build or test | — | installed |
| `common-ancestor-path` | 2.0.0 | BlueOak-1.0.0 | Build or test | — | installed |
| `cookie-es` | 1.2.3 | MIT | Build or test | — | installed |
| `cookie` | 2.0.2 | MIT | Build or test | — | installed |
| `crossws` | 0.3.5 | MIT | Build or test | — | installed |
| `css-select` | 6.0.0 | BSD-2-Clause | Build or test | — | installed |
| `css-tree` | 2.2.1 | MIT | Build or test | — | installed |
| `css-tree` | 3.2.1 | MIT | Build or test | — | installed |
| `css-what` | 7.0.0 | BSD-2-Clause | Build or test | — | installed |
| `csso` | 5.0.5 | MIT | Build or test | — | installed |
| `defu` | 6.1.7 | MIT | Build or test | — | installed |
| `dequal` | 2.0.3 | MIT | Build or test | — | installed |
| `destr` | 2.0.5 | MIT | Build or test | — | installed |
| `devalue` | 6.0.3 | MIT | Build or test | — | installed |
| `devlop` | 1.1.0 | MIT | Build or test | — | installed |
| `diff` | 9.0.0 | BSD-3-Clause | Build or test | — | installed |
| `dom-serializer` | 2.0.0 | MIT | Build or test | — | installed |
| `domelementtype` | 2.3.0 | BSD-2-Clause | Build or test | — | installed |
| `domhandler` | 5.0.3 | BSD-2-Clause | Build or test | — | installed |
| `domutils` | 3.2.2 | BSD-2-Clause | Build or test | — | installed |
| `dset` | 3.1.4 | MIT | Build or test | — | installed |
| `emmet` | 2.4.11 | MIT | Build or test | — | installed |
| `emoji-regex` | 10.6.0 | MIT | Build or test | — | installed |
| `entities` | 4.5.0 | BSD-2-Clause | Build or test | — | installed |
| `es-module-lexer` | 3.0.5 | MIT | Build or test | — | installed |
| `esbuild` | 0.28.2 | MIT | Build or test | — | installed |
| `escalade` | 3.2.0 | MIT | Build or test | — | installed |
| `extend` | 3.0.2 | MIT | Build or test | — | installed |
| `fast-deep-equal` | 3.1.3 | MIT | Build or test | — | installed |
| `fast-string-truncated-width` | 3.0.3 | MIT | Build or test | — | installed |
| `fast-string-width` | 3.0.2 | MIT | Build or test | — | installed |
| `fast-uri` | 3.1.9 | BSD-3-Clause | Build or test | — | installed |
| `fast-wrap-ansi` | 0.2.2 | MIT | Build or test | — | installed |
| `fdir` | 6.5.0 | MIT | Build or test | — | installed |
| `flattie` | 1.1.1 | MIT | Build or test | — | installed |
| `fnv1a-64` | 0.1.2 | MIT | Build or test | — | installed |
| `fontace` | 0.4.1 | MIT | Build or test | — | installed |
| `fontkitten` | 1.0.3 | MIT | Build or test | — | installed |
| `fsevents` | 2.3.3 | MIT | Build or test | os darwin | installed |
| `fuse.js` | 7.5.0 | Apache-2.0 | Browser | — | installed |
| `get-caller-file` | 2.0.5 | ISC | Build or test | — | installed |
| `get-east-asian-width` | 1.7.0 | MIT | Build or test | — | installed |
| `get-tsconfig` | 5.0.0-beta.6 | MIT | Build or test | — | installed |
| `github-slugger` | 2.0.0 | ISC | Build or test | — | installed |
| `h3` | 1.15.11 | MIT | Build or test | — | installed |
| `hast-util-to-html` | 9.0.6 | MIT | Build or test | — | installed |
| `hast-util-whitespace` | 3.0.0 | MIT | Build or test | — | installed |
| `html-escaper` | 3.0.3 | MIT | Build or test | — | installed |
| `html-void-elements` | 3.0.0 | MIT | Build or test | — | installed |
| `http-cache-semantics` | 4.3.0 | BSD-2-Clause | Build or test | — | installed |
| `iron-webcrypto` | 1.2.1 | MIT | Build or test | — | installed |
| `is-docker` | 4.0.0 | MIT | Build or test | — | installed |
| `is-plain-obj` | 4.1.0 | MIT | Build or test | — | installed |
| `json-schema-traverse` | 1.0.0 | MIT | Build or test | — | installed |
| `jsonc-parser` | 2.3.1 | MIT | Build or test | — | installed |
| `jsonc-parser` | 3.3.1 | MIT | Build or test | — | installed |
| `kleur` | 4.1.5 | MIT | Build or test | — | installed |
| `lru-cache` | 11.5.3 | BlueOak-1.0.0 | Build or test | — | installed |
| `magic-string` | 1.4.5 | MIT | Build or test | — | installed |
| `magicast` | 0.5.5 | MIT | Build or test | — | installed |
| `mdast-util-to-hast` | 13.2.2 | MIT | Build or test | — | installed |
| `mdn-data` | 2.0.28 | CC0-1.0 | Build or test | — | installed |
| `mdn-data` | 2.27.1 | CC0-1.0 | Build or test | — | installed |
| `micromark-util-character` | 2.1.1 | MIT | Build or test | — | installed |
| `micromark-util-encode` | 2.0.1 | MIT | Build or test | — | installed |
| `micromark-util-sanitize-uri` | 2.0.1 | MIT | Build or test | — | installed |
| `micromark-util-symbol` | 2.0.1 | MIT | Build or test | — | installed |
| `micromark-util-types` | 2.0.3 | MIT | Build or test | — | installed |
| `mri` | 1.2.0 | MIT | Build or test | — | installed |
| `mrmime` | 2.0.1 | MIT | Build or test | — | installed |
| `muggle-string` | 0.4.1 | MIT | Build or test | — | installed |
| `nanoid` | 3.3.20 | MIT | Build or test | — | installed |
| `neotraverse` | 1.0.2 | MIT | Build or test | — | installed |
| `nlcst-to-string` | 4.0.0 | MIT | Build or test | — | installed |
| `node-fetch-native` | 1.6.7 | MIT | Build or test | — | installed |
| `node-mock-http` | 1.0.5 | MIT | Build or test | — | installed |
| `normalize-path` | 3.0.0 | MIT | Build or test | — | installed |
| `nth-check` | 2.1.1 | BSD-2-Clause | Build or test | — | installed |
| `obug` | 3.0.0 | MIT | Build or test | — | installed |
| `ofetch` | 1.5.1 | MIT | Build or test | — | installed |
| `oniguruma-parser` | 0.12.2 | MIT | Build or test | — | installed |
| `oniguruma-to-es` | 4.3.6 | MIT | Build or test | — | installed |
| `p-limit` | 7.3.3 | MIT | Build or test | — | installed |
| `p-queue` | 10.0.0 | MIT | Build or test | — | installed |
| `package-manager-detector` | 1.9.0 | MIT | Build or test | — | installed |
| `path-browserify` | 1.0.1 | MIT | Build or test | — | installed |
| `piccolore` | 0.1.3 | ISC | Build or test | — | installed |
| `picocolors` | 1.1.1 | ISC | Build or test | — | installed |
| `playwright-core` | 1.65.1 | Apache-2.0 | Build or test | — | installed |
| `playwright` | 1.65.1 | Apache-2.0 | Build or test | — | installed |
| `postcss` | 8.5.33 | MIT | Build or test | — | installed |
| `prettier` | 3.10.1 | MIT | Build or test | — | installed |
| `prismjs` | 1.30.0 | MIT | Build or test | — | installed |
| `process-ancestry` | 0.1.0 | MIT | Build or test | — | installed |
| `property-information` | 7.2.0 | MIT | Build or test | — | installed |
| `radix3` | 1.1.2 | MIT | Build or test | — | installed |
| `readdirp` | 5.1.1 | MIT | Build or test | — | installed |
| `regex-recursion` | 6.0.2 | MIT | Build or test | — | installed |
| `regex-utilities` | 2.3.0 | MIT | Build or test | — | installed |
| `regex` | 6.1.0 | MIT | Build or test | — | installed |
| `request-light` | 0.5.8 | MIT | Build or test | — | installed |
| `request-light` | 0.7.0 | MIT | Build or test | — | installed |
| `require-from-string` | 2.0.2 | MIT | Build or test | — | installed |
| `resolve-pkg-maps` | 1.0.0 | MIT | Build or test | — | installed |
| `retext-smartypants` | 6.2.0 | MIT | Build or test | — | installed |
| `rolldown` | 1.2.19 | MIT | Build or test | — | installed |
| `satteri` | 0.11.7 | MIT | Build or test | — | installed |
| `sax` | 1.6.1 | BlueOak-1.0.0 | Build or test | — | installed |
| `semver` | 7.8.6 | ISC | Build or test | — | installed |
| `shiki` | 4.6.0 | MIT | Build or test | — | installed |
| `sisteransi` | 2.0.0 | MIT | Build or test | — | installed |
| `smol-toml` | 1.9.1 | BSD-3-Clause | Build or test | — | installed |
| `source-map-js` | 1.2.2 | BSD-3-Clause | Build or test | — | installed |
| `space-separated-tokens` | 2.0.2 | MIT | Build or test | — | installed |
| `std-env` | 4.3.0 | MIT | Build or test | — | installed |
| `string-width` | 7.2.0 | MIT | Build or test | — | installed |
| `string-width` | 8.3.0 | MIT | Build or test | — | installed |
| `stringify-entities` | 4.0.4 | MIT | Build or test | — | installed |
| `strip-ansi` | 7.2.0 | MIT | Build or test | — | installed |
| `svgo` | 4.1.0 | MIT | Build or test | — | installed |
| `tiny-inflate` | 1.0.3 | MIT | Build or test | — | installed |
| `tinyclip` | 1.0.3 | MIT | Build or test | — | installed |
| `tinyexec` | 1.3.1 | MIT | Build or test | — | installed |
| `tinyglobby` | 0.2.17 | MIT | Build or test | — | installed |
| `tinyps` | 0.5.2 | MIT | Build or test | — | installed |
| `trim-lines` | 3.0.1 | MIT | Build or test | — | installed |
| `trough` | 2.2.0 | MIT | Build or test | — | installed |
| `tslib` | 2.9.1 | 0BSD | Build or test | — | installed |
| `typesafe-path` | 0.2.2 | MIT | Build or test | — | installed |
| `typescript-auto-import-cache` | 0.3.6 | MIT | Build or test | — | installed |
| `typescript` | 6.0.3 | Apache-2.0 | Build or test | — | installed |
| `ufo` | 1.6.4 | MIT | Build or test | — | installed |
| `ultrahtml` | 1.7.0 | MIT | Build or test | — | installed |
| `uncrypto` | 0.1.3 | MIT | Build or test | — | installed |
| `undici-types` | 7.24.6 | MIT | Build or test | — | installed |
| `undici` | 8.12.4 | MIT | Build or test | — | installed |
| `unified` | 11.0.5 | MIT | Build or test | — | installed |
| `unifont` | 1.0.3 | MIT | Build or test | — | installed |
| `unist-util-is` | 6.0.1 | MIT | Build or test | — | installed |
| `unist-util-position` | 5.0.0 | MIT | Build or test | — | installed |
| `unist-util-stringify-position` | 4.0.0 | MIT | Build or test | — | installed |
| `unist-util-visit-parents` | 6.1.0 | MIT | Build or test | — | installed |
| `unist-util-visit` | 5.2.0 | MIT | Build or test | — | installed |
| `unstorage` | 1.17.6 | MIT | Build or test | — | installed |
| `verkit` | 0.5.0 | MIT | Build or test | — | installed |
| `vfile-message` | 4.0.4 | MIT | Build or test | — | installed |
| `vfile` | 6.0.3 | MIT | Build or test | — | installed |
| `vite` | 8.3.8 | MIT | Build or test | — | installed |
| `vitefu` | 1.1.4 | MIT | Build or test | — | installed |
| `volar-service-css` | 0.0.71 | MIT | Build or test | — | installed |
| `volar-service-emmet` | 0.0.71 | MIT | Build or test | — | installed |
| `volar-service-html` | 0.0.71 | MIT | Build or test | — | installed |
| `volar-service-prettier` | 0.0.71 | MIT | Build or test | — | installed |
| `volar-service-typescript-twoslash-queries` | 0.0.71 | MIT | Build or test | — | installed |
| `volar-service-typescript` | 0.0.71 | MIT | Build or test | — | installed |
| `volar-service-yaml` | 0.0.71 | MIT | Build or test | — | installed |
| `vscode-css-languageservice` | 6.3.10 | MIT | Build or test | — | installed |
| `vscode-html-languageservice` | 5.6.2 | MIT | Build or test | — | installed |
| `vscode-json-languageservice` | 4.1.8 | MIT | Build or test | — | installed |
| `vscode-jsonrpc` | 10.0.0 | MIT | Build or test | — | installed |
| `vscode-jsonrpc` | 8.2.0 | MIT | Build or test | — | installed |
| `vscode-languageserver-protocol` | 3.17.5 | MIT | Build or test | — | installed |
| `vscode-languageserver-protocol` | 3.18.5 | MIT | Build or test | — | installed |
| `vscode-languageserver-textdocument` | 1.0.16 | MIT | Build or test | — | installed |
| `vscode-languageserver-types` | 3.17.5 | MIT | Build or test | — | installed |
| `vscode-languageserver-types` | 3.18.5 | MIT | Build or test | — | installed |
| `vscode-languageserver` | 9.0.1 | MIT | Build or test | — | installed |
| `vscode-nls` | 5.2.0 | MIT | Build or test | — | installed |
| `vscode-uri` | 3.2.0 | MIT | Build or test | — | installed |
| `wrap-ansi` | 9.0.2 | MIT | Build or test | — | installed |
| `xxhash-wasm` | 1.1.0 | MIT | Build or test | — | installed |
| `y18n` | 5.0.8 | ISC | Build or test | — | installed |
| `yaml-language-server` | 1.23.0 | MIT | Build or test | — | installed |
| `yaml` | 2.8.3 | ISC | Build or test | — | installed |
| `yaml` | 2.9.1 | ISC | Build or test | — | installed |
| `yargs-parser` | 22.0.0 | ISC | Build or test | — | installed |
| `yargs` | 18.2.0 | MIT | Build or test | — | installed |
| `yocto-queue` | 1.2.2 | MIT | Build or test | — | installed |
| `zod` | 4.6.7 | MIT | Build or test | — | installed |
| `zwitch` | 2.0.4 | MIT | Build or test | — | installed |
