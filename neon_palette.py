"""Shared data loader for the Neon Kabuki Cherry Petal palette."""

from __future__ import annotations

import json
import os
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

_PALETTE_ENV_VAR = "NEON_KABUKI_PALETTE_PATH"
_PRIMARY_ACCENT_ROLE = "primary_accent"
_ROLES_KEY = "roles"
_SWATCHES_KEY = "swatches"


class NeonPaletteError(RuntimeError):
    """Raised when the palette payload is missing or malformed."""

    @classmethod
    def missing_role(cls, role: str) -> NeonPaletteError:
        return cls(f"{role} role missing from neon palette")

    @classmethod
    def empty_section(cls, section: str) -> NeonPaletteError:
        return cls(f"no {section} defined in neon palette payload")

    @classmethod
    def missing_array(cls, key: str) -> NeonPaletteError:
        return cls(f"palette JSON missing '{key}' array")

    @classmethod
    def missing_file(cls, path: Path) -> NeonPaletteError:
        return cls(f"missing neon palette file: {path}")

    @classmethod
    def invalid_json(cls, path: Path) -> NeonPaletteError:
        return cls(f"invalid neon palette JSON: {path}")


@dataclass(frozen=True, slots=True)
class PaletteRole:
    role: str
    name: str
    value: str
    usage: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class PaletteSwatch:
    name: str
    hex_value: str


@dataclass(frozen=True, slots=True)
class NeonPalette:
    theme: str
    codename: str
    version: str
    updated_at: str
    owner: str
    description: str
    picker_grid: str
    roles: Mapping[str, PaletteRole]
    swatches: tuple[PaletteSwatch, ...]
    notes: tuple[str, ...]

    def role_value(self, role: str, default: str | None = None) -> str | None:
        entry = self.roles.get(role)
        if entry:
            return entry.value
        return default

    def primary_accent(self) -> str:
        value = self.role_value(_PRIMARY_ACCENT_ROLE)
        if not value:
            raise NeonPaletteError.missing_role(_PRIMARY_ACCENT_ROLE)
        return value


def _default_palette_path() -> Path:
    """Locate the palette JSON relative to the monorepo root.

    x_make_common_x lives at `<repo_root>/x_make_common_x`, so stepping one level up
    lands at the workspace root even when the repo is cloned elsewhere.
    """

    root = Path(__file__).resolve().parents[1]
    return (
        root
        / "x_0_make_ppnw_dot_ai_website_x"
        / "branding"
        / "palettes"
        / "neon_kabuki.json"
    )


def resolve_palette_path() -> Path:
    override = os.environ.get(_PALETTE_ENV_VAR)
    if override:
        return Path(override).expanduser().resolve()
    return _default_palette_path()


def _parse_roles(payload: Sequence[Mapping[str, Any]]) -> Mapping[str, PaletteRole]:
    roles: dict[str, PaletteRole] = {}
    for item in payload:
        role = str(item.get("role") or "").strip()
        name = str(item.get("name") or role or "role")
        usage = tuple(
            str(value) for value in item.get("usage", []) if str(value).strip()
        )
        value = str(item.get("hex") or item.get("rgba") or "").strip()
        if not role or not value:
            continue
        roles[role] = PaletteRole(role=role, name=name, value=value, usage=usage)
    if not roles:
        raise NeonPaletteError.empty_section(_ROLES_KEY)
    return roles


def _parse_swatches(payload: Sequence[Mapping[str, Any]]) -> tuple[PaletteSwatch, ...]:
    swatches: list[PaletteSwatch] = []
    for item in payload:
        name = str(item.get("name") or "").strip()
        hex_value = str(item.get("hex") or "").strip()
        if not name or not hex_value:
            continue
        swatches.append(PaletteSwatch(name=name, hex_value=hex_value))
    if not swatches:
        raise NeonPaletteError.empty_section(_SWATCHES_KEY)
    return tuple(swatches)


def _load_raw_palette(path: Path) -> Mapping[str, Any]:
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError as exc:  # pragma: no cover - depends on workstation
        raise NeonPaletteError.missing_file(path) from exc
    except json.JSONDecodeError as exc:  # pragma: no cover - malformed file
        raise NeonPaletteError.invalid_json(path) from exc


@lru_cache(maxsize=1)
def load_neon_palette(path: str | Path | None = None) -> NeonPalette:
    target_path = Path(path) if path else resolve_palette_path()
    payload = _load_raw_palette(target_path)
    roles_payload = payload.get(_ROLES_KEY)
    swatches_payload = payload.get(_SWATCHES_KEY)
    if not isinstance(roles_payload, Sequence) or isinstance(
        roles_payload, (str, bytes)
    ):
        raise NeonPaletteError.missing_array(_ROLES_KEY)
    if not isinstance(swatches_payload, Sequence) or isinstance(
        swatches_payload, (str, bytes)
    ):
        raise NeonPaletteError.missing_array(_SWATCHES_KEY)

    roles = _parse_roles(roles_payload)  # type: ignore[arg-type]
    swatches = _parse_swatches(swatches_payload)  # type: ignore[arg-type]

    notes_payload = payload.get("notes")
    notes: tuple[str, ...]
    if isinstance(notes_payload, Sequence) and not isinstance(
        notes_payload, (str, bytes)
    ):
        notes = tuple(
            str(entry).strip() for entry in notes_payload if str(entry).strip()
        )
    else:
        notes = ()

    return NeonPalette(
        theme=str(payload.get("theme") or "Neon Kabuki Cherry Petal"),
        codename=str(payload.get("codename") or "Sakura Nova Control Surface 1.0"),
        version=str(payload.get("version") or "1.0.0"),
        updated_at=str(payload.get("updated_at") or ""),
        owner=str(payload.get("owner") or "Make All Experience Guild"),
        description=str(payload.get("description") or ""),
        picker_grid=str(payload.get("picker_grid") or "4x4"),
        roles=roles,
        swatches=swatches,
        notes=notes,
    )


__all__ = [
    "NeonPalette",
    "NeonPaletteError",
    "PaletteRole",
    "PaletteSwatch",
    "load_neon_palette",
    "resolve_palette_path",
]
