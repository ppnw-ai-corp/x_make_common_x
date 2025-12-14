"""Qt-specific Neon Kabuki theming helpers shared across PySide6 surfaces."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, cast

from x_make_common_x.neon_palette import load_neon_palette

try:  # pragma: no cover - PySide6 availability depends on workstation
    import PySide6.QtCore as _QtCoreRaw
    import PySide6.QtGui as _QtGuiRaw
    import PySide6.QtWidgets as _QtWidgetsRaw
except ModuleNotFoundError as exc:  # pragma: no cover - surfaced at the UI entrypoint
    raise RuntimeError(
        "PySide6 is required for neon_qt_theme; install it before importing this module."
    ) from exc

QtCore = cast("Any", _QtCoreRaw)
QtGui = cast("Any", _QtGuiRaw)
QtWidgets = cast("Any", _QtWidgetsRaw)


@dataclass(frozen=True, slots=True)
class NeonSwatch:
    """Single accent option for the neon control surfaces."""

    name: str
    hex_value: str


class NeonTheme(QtCore.QObject):
    """Centralized palette + stylesheet builder for the Tron-inspired UI."""

    theme_changed = QtCore.Signal(str)

    def __init__(self) -> None:
        super().__init__()
        palette = load_neon_palette()
        self._palette = palette
        self._background_hex = palette.role_value("surface_01", "#03060f") or "#03060f"
        self._surface_hex = palette.role_value("surface_02", "#050a16") or "#050a16"
        self._surface_alt_hex = palette.role_value("surface_03", "#0a0f21") or "#0a0f21"
        self._header_hex = palette.role_value("surface_header", "#0a152d") or "#0a152d"
        self._gridline_hex = palette.role_value("gridlines", "rgba(255, 255, 255, 0.08)") or "rgba(255, 255, 255, 0.08)"
        self._border_hex = palette.role_value("outline", "rgba(255, 255, 255, 0.45)") or "rgba(255, 255, 255, 0.45)"
        self._text_primary = palette.role_value("text_primary", "#f5f6ff") or "#f5f6ff"
        self._text_muted = palette.role_value("text_secondary", "#b3c1ff") or "#b3c1ff"
        self._scroll_track_hex = palette.role_value("scroll_track", "#0b1124") or "#0b1124"
        self._swatches: tuple[NeonSwatch, ...] = tuple(
            NeonSwatch(entry.name, entry.hex_value) for entry in palette.swatches
        )
        if not self._swatches:
            raise RuntimeError("neon palette does not define any swatches")
        self._accent_index = 0
        self._style_sheet = ""
        self._state_backgrounds: dict[str, QtGui.QColor] = {}
        self._state_text: dict[str, QtGui.QColor] = {}
        self._accent_hex = self._swatches[self._accent_index].hex_value
        self._accent_glow_hex = self._accent_hex
        self._accent_dim_hex = self._accent_hex
        self._accent_soft_hex = self._accent_hex
        self._accent_panel_hex = self._accent_hex
        self._accent_bloom_rgba = self._rgba_string(QtGui.QColor(self._accent_hex), 0.45)
        self._accent_halo_rgba = self._rgba_string(QtGui.QColor(self._accent_hex), 0.15)
        self._accent_selection_rgba = "rgba(255, 255, 255, 0.25)"
        self._accent_outline_rgba = "rgba(255, 255, 255, 0.45)"
        self._build_palette()

    @staticmethod
    def _mix(color_a: QtGui.QColor, color_b: QtGui.QColor, ratio: float) -> QtGui.QColor:
        clamped = max(0.0, min(1.0, ratio))
        inverse = 1.0 - clamped
        red = int(color_a.red() * clamped + color_b.red() * inverse)
        green = int(color_a.green() * clamped + color_b.green() * inverse)
        blue = int(color_a.blue() * clamped + color_b.blue() * inverse)
        return QtGui.QColor(red, green, blue)

    @staticmethod
    def _rgba_string(color: QtGui.QColor, alpha: float) -> str:
        clamped = max(0.0, min(1.0, alpha))
        alpha_255 = int(clamped * 255)
        return f"rgba({color.red()}, {color.green()}, {color.blue()}, {alpha_255})"

    def _build_palette(self) -> None:
        accent = QtGui.QColor(self._swatches[self._accent_index].hex_value)
        base = QtGui.QColor("#050812")
        night = QtGui.QColor("#0f1428")
        self._accent_hex = accent.name()
        self._accent_glow_hex = self._mix(accent, QtGui.QColor("#ffffff"), 0.45).name()
        self._accent_dim_hex = self._mix(accent, base, 0.18).name()
        self._accent_soft_hex = self._mix(accent, night, 0.35).name()
        self._accent_panel_hex = self._mix(accent, QtGui.QColor("#13021f"), 0.55).name()
        self._accent_bloom_rgba = self._rgba_string(accent, 0.55)
        self._accent_halo_rgba = self._rgba_string(accent, 0.2)
        self._accent_selection_rgba = self._rgba_string(accent, 0.35)
        self._accent_outline_rgba = self._rgba_string(accent, 0.65)

        self._state_backgrounds = {
            "unknown": self._mix(QtGui.QColor("#141c33"), accent, 0.15),
            "passed": self._mix(accent, night, 0.35),
            "failed": self._mix(QtGui.QColor("#ff3b6a"), QtGui.QColor("#1c0715"), 0.2),
            "skipped": self._mix(QtGui.QColor("#1a2238"), QtGui.QColor("#2d3148"), 0.5),
        }
        self._state_text = {
            "unknown": QtGui.QColor("#a8b4ff"),
            "passed": QtGui.QColor("#07101d"),
            "failed": QtGui.QColor(self._accent_hex),
            "skipped": QtGui.QColor("#d5defd"),
        }
        self._style_sheet = self._compose_stylesheet()

    def _compose_stylesheet(self) -> str:
        return f"""
QWidget, QMainWindow, QWidget#ControlCenterRoot, QWidget#UnifiedCommandCenterWindow {{
    background-color: {self._background_hex};
    color: {self._text_primary};
    font-family: 'Bahnschrift', 'Segoe UI', 'Helvetica Neue', sans-serif;
    font-size: 13px;
}}
QLabel#SummaryLabel {{
    color: {self._text_muted};
    font-size: 14px;
}}
QLabel#SectionLabel {{
    color: {self._text_primary};
    text-transform: uppercase;
    letter-spacing: 0.12em;
    font-size: 11px;
}}
QPlainTextEdit, QLineEdit {{
    background-color: {self._surface_hex};
    border: 1px solid {self._accent_outline_rgba};
    border-radius: 12px;
    padding: 6px 10px;
}}
QPlainTextEdit#ActivityLog {{
    background-color: {self._surface_alt_hex};
    border-color: {self._accent_outline_rgba};
}}
QPushButton {{
    background-color: transparent;
    border: 1px solid {self._accent_outline_rgba};
    border-radius: 18px;
    padding: 8px 20px;
    font-weight: 600;
    letter-spacing: 0.08em;
}}
QPushButton:hover {{
    border-color: {self._accent_glow_hex};
    color: {self._accent_glow_hex};
}}
QPushButton:pressed {{
    background-color: {self._accent_soft_hex};
}}
QFrame#PalettePickerFrame {{
    background-color: {self._surface_alt_hex};
    border: 1px solid {self._accent_outline_rgba};
    border-radius: 18px;
    padding: 12px;
}}
QTabWidget::pane {{
    border: 1px solid {self._accent_outline_rgba};
    background-color: {self._surface_hex};
    border-radius: 18px;
    margin: 12px;
    padding: 8px;
}}
QTabWidget::tab-bar {{
    alignment: center;
}}
QTabBar::tab {{
    background-color: {self._accent_panel_hex};
    color: {self._text_primary};
    border: 1px solid {self._accent_outline_rgba};
    border-radius: 18px;
    padding: 6px 24px;
    margin: 0px 6px;
    min-width: 140px;
    letter-spacing: 0.08em;
}}
QTabBar::tab:selected {{
    background-color: {self._accent_hex};
    color: {self._background_hex};
    border-color: {self._accent_glow_hex};
}}
QTabBar::tab:hover {{
    color: {self._accent_glow_hex};
    border-color: {self._accent_glow_hex};
}}
QTabBar::tab:!selected {{
    opacity: 0.8;
}}
QTabBar::tear {{
    background: transparent;
}}
QTableWidget, QTableView {{
    background-color: {self._surface_hex};
    alternate-background-color: {self._surface_alt_hex};
    border: 1px solid {self._accent_outline_rgba};
    gridline-color: {self._gridline_hex};
    selection-background-color: {self._accent_selection_rgba};
    selection-color: {self._background_hex};
}}
QHeaderView::section {{
    background-color: {self._header_hex};
    color: {self._text_primary};
    padding: 8px 10px;
    border: 0px;
    border-right: 1px solid {self._accent_outline_rgba};
}}
QMenuBar {{
    background-color: {self._background_hex};
    color: {self._text_primary};
}}
QMenuBar::item:pressed, QMenuBar::item:selected {{
    background-color: {self._accent_dim_hex};
}}
QMenu {{
    background-color: {self._surface_hex};
    border: 1px solid {self._accent_outline_rgba};
}}
QMenu::item:selected {{
    background-color: {self._accent_soft_hex};
}}
QToolTip {{
    background-color: {self._surface_alt_hex};
    color: {self._text_primary};
    border: 1px solid {self._accent_outline_rgba};
}}
QScrollBar:horizontal, QScrollBar:vertical {{
    background: {self._scroll_track_hex};
    border: none;
    margin: 0px;
}}
QScrollBar::handle:horizontal, QScrollBar::handle:vertical {{
    background: {self._accent_dim_hex};
    border-radius: 6px;
    border: 1px solid {self._accent_outline_rgba};
}}
QScrollBar::handle:horizontal:hover, QScrollBar::handle:vertical:hover {{
    background: {self._accent_hex};
}}
"""

    def style_sheet(self) -> str:
        return self._style_sheet

    def swatches(self) -> tuple[NeonSwatch, ...]:
        return self._swatches

    def accent_hex(self) -> str:
        return self._accent_hex

    def accent_name(self) -> str:
        return self._swatches[self._accent_index].name

    def accent_index(self) -> int:
        return self._accent_index

    def accent_outline_rgba(self) -> str:
        return self._accent_outline_rgba

    def accent_glow_hex(self) -> str:
        return self._accent_glow_hex

    def accent_dim_hex(self) -> str:
        return self._accent_dim_hex

    def accent_soft_hex(self) -> str:
        return self._accent_soft_hex

    def surface_hex(self) -> str:
        return self._surface_hex

    def border_hex(self) -> str:
        return self._border_hex

    def glow_hex(self) -> str:
        return self._accent_glow_hex

    def cell_background(self, state: str) -> QtGui.QColor:
        return self._state_backgrounds.get(state, self._state_backgrounds["unknown"])

    def cell_text(self, state: str) -> QtGui.QColor:
        return self._state_text.get(state, QtGui.QColor(self._text_primary))

    def set_accent_index(self, index: int) -> None:
        if index == self._accent_index:
            return
        if index < 0 or index >= len(self._swatches):
            return
        self._accent_index = index
        self._build_palette()
        self.theme_changed.emit(self._accent_hex)


class PalettePicker(QtWidgets.QFrame):
    """Compact 4x4 neon palette grid with kawaii-inspired labels."""

    def __init__(self, theme: NeonTheme, parent: object | None = None) -> None:
        super().__init__(parent)
        self.setObjectName("PalettePickerFrame")
        self._theme = theme
        self._buttons: list[QtWidgets.QToolButton] = []
        self._selection_label = QtWidgets.QLabel()
        self._build_layout()
        self._theme.theme_changed.connect(self._sync_from_theme)
        self._sync_from_theme(self._theme.accent_hex())

    def _build_layout(self) -> None:
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(6)

        header = QtWidgets.QHBoxLayout()
        title = QtWidgets.QLabel("Neon Accent")
        title.setProperty("class", "picker-title")
        header.addWidget(title)
        header.addStretch(1)
        self._selection_label.setText(self._theme.accent_name())
        header.addWidget(self._selection_label)
        layout.addLayout(header)

        grid = QtWidgets.QGridLayout()
        grid.setSpacing(6)
        for index, swatch in enumerate(self._theme.swatches()):
            button = QtWidgets.QToolButton()
            button.setCheckable(True)
            button.setAutoExclusive(True)
            button.setFixedSize(30, 30)
            button.setToolTip(swatch.name)
            button.clicked.connect(  # type: ignore[attr-defined]
                lambda _checked=False, idx=index: self._theme.set_accent_index(idx)
            )
            self._buttons.append(button)
            grid.addWidget(button, index // 4, index % 4)
        layout.addLayout(grid)
        self.setLayout(layout)

    def _sync_from_theme(self, _accent_hex: str) -> None:
        self._selection_label.setText(self._theme.accent_name())
        for index, (button, swatch) in enumerate(zip(self._buttons, self._theme.swatches())):
            active = index == self._theme.accent_index()
            border = self._theme.accent_outline_rgba() if active else "rgba(255, 255, 255, 0.2)"
            button.setChecked(active)
            button.setStyleSheet(
                f"""
QToolButton {{
    border: 2px solid {border};
    border-radius: 15px;
    background-color: {swatch.hex_value};
}}
QToolButton:checked {{
    border-color: {border};
}}
"""
            )


__all__ = ["NeonSwatch", "NeonTheme", "PalettePicker"]
