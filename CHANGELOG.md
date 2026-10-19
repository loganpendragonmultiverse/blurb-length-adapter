# Changelog

## 1.1.1 - 2026-10-19

- Create outputs exclusively and refuse dangling symlinks; preserve concurrently created files.
- Document ordinary file-error behavior and partial-output limits.
- Reject boolean limits and blank profile IDs or labels; retain Unicode counting policies.

## 1.1.0 - 2026-10-16

- Added explicit per-profile all-character and Unicode-whitespace-excluding character policies, with policy and counted totals in reports.
- Preserved default counts and word limits; covered Unicode, exact limits and invalid policies with synthetic tests.

## 1.0.0 - 2026-07-26

- Added versioned blurb workspaces and custom length profiles.
- Added source and variant word and character measurements.
- Added missing, within-limit, and over-limit review states.
