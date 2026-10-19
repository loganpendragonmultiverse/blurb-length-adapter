# Blurb Length Adapter

> ⭐ **Gold Star Project**
> I consider this project complete. Fixes, maintenance and good new ideas are still welcome.
> [About Gold Stars](https://www.loganpendragonforge.com/open-source/?gold=1)
>
> Measure supplied blurbs against your own length profiles while you edit the wording yourself.

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

## 1.1.0 - 2026-10-16

Profiles accept `"character_count": "all"` (the default) or `"exclude-whitespace"`. For example, `{"id":"short","label":"Short","max_characters":100,"character_count":"exclude-whitespace"}` excludes characters matched by Python's Unicode `str.isspace()` policy (the same policy as the existing `characters_without_spaces` measurement): tabs, line breaks, nonbreaking spaces and em spaces are excluded; zero-width spaces are counted. Counts are Unicode code points, so combining marks and each code point in an emoji sequence count separately. Word limits still use whitespace-separated words. JSON and Markdown identify the policy and counted total for every profile. No copy is generated or truncated, and these policies are not marketplace certification.

## 1.1.1 — October 19, 2026

Output files are created exclusively. Existing files, source inputs and symlink destinations are refused, including files created by another writer after validation. Ordinary file errors return exit code 2 with a message. A failed write may leave a partial new report; inspect it and retry with a new destination. This does not provide transactions through power loss.

Profile IDs and labels must be nonblank text. Each supplied limit must be a positive integer; JSON booleans are rejected. IDs are kept exactly as authored and must be unique.
