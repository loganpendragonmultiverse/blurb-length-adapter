# Blurb Length Adapter

[![CI](https://github.com/loganpendragonmultiverse/blurb-length-adapter/actions/workflows/ci.yml/badge.svg)](https://github.com/loganpendragonmultiverse/blurb-length-adapter/actions/workflows/ci.yml)

Blurb Length Adapter creates structured editing containers for adapting one supplied blurb to multiple word and character limits. It records the source, target profiles, current variants, measurements, missing drafts, and over-limit warnings.

## Three-minute start

```bash
python -m pip install .
blurb-adapter examples/workspace.json --output worksheet.md
blurb-adapter examples/workspace.json --format json
```

Profiles may set a maximum word count, character count, or both. The Markdown worksheet preserves the original blurb and provides a clearly measured section for every target.

## Editorial boundary

The tool does not generate, summarize, truncate, or rewrite marketing copy. It provides containers and measurements for human editing, so meaning and tone remain under the writer's control. Counts use whitespace-delimited words and Unicode string characters; individual marketplaces may count differently.

Requires Python 3.10 or newer. Development checks use Ruff, pytest with branch coverage, and package builds.

Part of the [Logan Pendragon Forge open-source collection](https://www.loganpendragonforge.com/open-source/). Licensed under the [MIT License](LICENSE).
