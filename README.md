# Origin KSA · منشأ

Origin KSA is a bilingual reference for Saudi buyers of pumps, valves and their parts. The static site compares reported import origins and shows the status of reviewed local manufacturing and procurement evidence. Its six-digit customs groups can cover several different models.

## Build the reviewed site

Use Node 24, pnpm 10.34.9 and Python 3.12. From this directory, run:

```sh
npx --yes pnpm@10.34.9 install --frozen-lockfile
python3.12 -m venv .venv
.venv/bin/python -m pip install --require-hashes --only-binary=:all: -r requirements.txt
npm run check
npm run build
npm run preview
```

The first check downloads the official Saudi import records from UN Comtrade, validates the reviewed release pins and creates local chart inputs. Allow several minutes for the rate-limited requests. A mismatch stops the build so the publisher can investigate a revision. The built site displays its charts and search results from local assets.

Methods explains the calculations, dates and limitations. The public CSV contains calculated indicators. The [source file fingerprints](public/source-fingerprints.csv) identify the original responses used in the published analysis. Current provider responses can differ from those retrieved for the release. [UN Comtrade data policy](https://uncomtrade.org/docs/policy-on-comtrade-data-use/)

## Checks and ownership

`.venv/bin/python -m pytest -q` verifies the formulas and approval rules. The [verification workflow](.github/workflows/site.yml) includes browser, accessibility, performance and dependency checks. Public company and Mandatory List entries require the owner's source review. No sign-in is needed to use the site.

```sh
npm ci --prefix scripts/qa
npx --yes pnpm@10.34.9 audit --audit-level low
npm audit --prefix scripts/qa --audit-level low
```

© 2026 Nawaf Aljasser. AI tools helped draft the site, code, explanations and translations. The owner controls publication and approval. The [code licence](LICENSE), [content and dataset terms](LICENSE-CONTENT.md) and [third-party notices](docs/THIRD_PARTY_LICENSES.md) describe their respective scopes.
