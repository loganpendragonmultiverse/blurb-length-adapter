from __future__ import annotations

import json
import re
from pathlib import Path
from typing import Any

WORD = re.compile(r"\S+")


def metrics(text: str) -> dict[str, int]:
    return {
        "words": len(WORD.findall(text)),
        "characters": len(text),
        "characters_without_spaces": len(re.sub(r"\s", "", text)),
    }


def load_workspace(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict) or data.get("version") != 1:
        raise ValueError("workspace must be a version 1 object")
    if not isinstance(data.get("source"), str) or not data["source"].strip():
        raise ValueError("workspace requires a supplied source blurb")
    profiles = data.get("profiles")
    if not isinstance(profiles, list) or not profiles:
        raise ValueError("profiles must be a non-empty list")
    seen: set[str] = set()
    for profile in profiles:
        if (
            not isinstance(profile, dict)
            or not isinstance(profile.get("id"), str)
            or not isinstance(profile.get("label"), str)
        ):
            raise TypeError("each profile requires string id and label")
        if profile["id"] in seen:
            raise ValueError(f"duplicate profile id: {profile['id']}")
        limits = [profile.get("max_words"), profile.get("max_characters")]
        if all(limit is None for limit in limits) or any(
            limit is not None and (not isinstance(limit, int) or limit <= 0) for limit in limits
        ):
            raise ValueError(f"profile {profile['id']} requires positive limits")
        seen.add(profile["id"])
    variants = data.get("variants", {})
    if not isinstance(variants, dict) or any(
        key not in seen or not isinstance(value, str) for key, value in variants.items()
    ):
        raise TypeError("variants must map known profile ids to strings")
    return data


def evaluate(data: dict[str, Any]) -> dict[str, Any]:
    variants = data.get("variants", {})
    results = []
    for profile in data["profiles"]:
        text = variants.get(profile["id"], "")
        values = metrics(text)
        violations = []
        if profile.get("max_words") and values["words"] > profile["max_words"]:
            violations.append(f"{values['words'] - profile['max_words']} words over")
        if profile.get("max_characters") and values["characters"] > profile["max_characters"]:
            violations.append(f"{values['characters'] - profile['max_characters']} characters over")
        status = "missing" if not text.strip() else "over-limit" if violations else "within-limit"
        results.append(
            {
                "id": profile["id"],
                "label": profile["label"],
                "limits": {
                    key: profile[key] for key in ("max_words", "max_characters") if key in profile
                },
                "text": text,
                "metrics": values,
                "status": status,
                "violations": violations,
            }
        )
    return {
        "version": 1,
        "source": data["source"],
        "source_metrics": metrics(data["source"]),
        "profiles": results,
    }


def render_markdown(result: dict[str, Any]) -> str:
    source = result["source_metrics"]
    lines = [
        "# Blurb Length Workspace",
        "",
        f"Source: **{source['words']} words · {source['characters']} characters**",
        "",
        "> " + result["source"].replace("\n", "\n> "),
        "",
    ]
    for profile in result["profiles"]:
        limits = ", ".join(
            f"{value} {key.replace('max_', '')} maximum" for key, value in profile["limits"].items()
        )
        lines.extend(
            [f"## {profile['label']}", "", f"Status: **{profile['status']}** · {limits}", ""]
        )
        if profile["text"]:
            lines.extend(
                [
                    profile["text"],
                    "",
                    f"Current: {profile['metrics']['words']} words · {profile['metrics']['characters']} characters",
                ]
            )
            if profile["violations"]:
                lines.append("Review: " + "; ".join(profile["violations"]))
        else:
            lines.append("_Write the adapted blurb here._")
        lines.append("")
    return "\n".join(lines).rstrip() + "\n"
