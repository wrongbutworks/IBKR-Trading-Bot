"""Windows GUI entry point and process-level safety setup.

The entry point creates the Qt application, follows the operating-system color
scheme, acquires the portable-folder single-instance lock, constructs the
controller/window, and releases process resources on shutdown. Trading decisions
remain in the strategy and controller layers.
"""

from __future__ import annotations

import sys
from typing import Any, Optional

from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QIcon, QPalette
from PySide6.QtWidgets import QApplication, QMessageBox, QStyleFactory

from app.controller import TradingController
from app.gui import (
    DARK_FUSION_PALETTE_COLORS,
    DARK_MODE_APP_PROPERTY,
    LIGHT_FUSION_PALETTE_COLORS,
    MainWindow,
)
from app.lockfile import SingleInstanceError, SingleInstanceLock
from app.paths import resource_path


def _color_scheme_dark_state(scheme: Any) -> Optional[bool]:
    """Translate a Qt color-scheme enum to ``True``/``False`` when known."""
    color_scheme_enum = getattr(Qt, "ColorScheme", None)
    if color_scheme_enum is None:
        return None
    dark = getattr(color_scheme_enum, "Dark", None)
    light = getattr(color_scheme_enum, "Light", None)
    try:
        if dark is not None and scheme == dark:
            return True
        if light is not None and scheme == light:
            return False
    except Exception:
        return None
    return None


def _system_prefers_dark(app: QApplication) -> bool:
    """Detect the current OS color scheme with a palette fallback."""
    try:
        style_hints = app.styleHints()
        color_scheme = getattr(style_hints, "colorScheme", None)
        if callable(color_scheme):
            resolved = _color_scheme_dark_state(color_scheme())
            if resolved is not None:
                return resolved
    except Exception:
        pass

    # The fallback covers platforms or Qt builds where colorScheme() is not
    # exposed. It is evaluated before this module installs its own palette.
    try:
        palette_getter = getattr(app, "palette", None)
        palette = palette_getter() if callable(palette_getter) else None
        if palette is not None:
            window_color = palette.color(QPalette.Window)
            lightness = getattr(window_color, "lightness", None)
            if callable(lightness):
                return int(lightness()) < 128
    except Exception:
        pass
    return False


def _apply_application_palette(app: QApplication, dark: Optional[bool] = None) -> bool:
    """Apply the Fusion palette for the detected light or dark system theme."""
    dark = _system_prefers_dark(app) if dark is None else bool(dark)
    app.setStyle(QStyleFactory.create("Fusion"))
    palette = QPalette()
    colors = DARK_FUSION_PALETTE_COLORS if dark else LIGHT_FUSION_PALETTE_COLORS
    for role_name, color in colors.items():
        palette.setColor(getattr(QPalette, role_name), QColor(color))
    app.setPalette(palette)
    app.setProperty(DARK_MODE_APP_PROPERTY, dark)
    return dark


def _apply_application_icon(app: QApplication) -> None:
    """Apply the packaged/source BouncyBot icon when the asset is available."""
    icon_path = resource_path("Images", "BouncyBot_app_icon.png")
    if icon_path.is_file():
        app.setWindowIcon(QIcon(str(icon_path)))


def _install_system_theme_hook(app: QApplication, window: MainWindow) -> None:
    """Keep the running application synchronized with OS theme changes."""
    try:
        style_hints = app.styleHints()
        signal = getattr(style_hints, "colorSchemeChanged", None)
        connect = getattr(signal, "connect", None)
    except Exception:
        return
    if not callable(connect):
        return

    def apply_scheme(scheme: Any = None) -> None:
        dark = _color_scheme_dark_state(scheme)
        if dark is None:
            dark = _system_prefers_dark(app)
        _apply_application_palette(app, dark)
        apply_theme = getattr(window, "apply_system_theme", None)
        if callable(apply_theme):
            apply_theme(dark)

    connect(apply_scheme)
    # Retain the callback for bindings/test doubles that do not hold a strong
    # reference to Python slots connected to a C++ signal.
    setattr(window, "_system_theme_callback", apply_scheme)


def _install_session_shutdown_hook(app: QApplication, window: MainWindow) -> None:
    """Connect Qt session management to the window's durable shutdown save."""
    signal = getattr(app, "commitDataRequest", None)
    connect = getattr(signal, "connect", None)
    if not callable(connect):
        return
    direct_connection = getattr(
        getattr(Qt, "ConnectionType", Qt),
        "DirectConnection",
        getattr(Qt, "DirectConnection", None),
    )
    try:
        if direct_connection is None:
            connect(window.handle_system_shutdown)
        else:
            connect(window.handle_system_shutdown, direct_connection)
    except TypeError:
        # Minimal Qt doubles and older bindings may expose only the one-argument
        # connect form. The production PySide6 path uses DirectConnection.
        connect(window.handle_system_shutdown)


def main() -> int:
    app = QApplication(sys.argv)
    _apply_application_palette(app)
    _apply_application_icon(app)
    lock = SingleInstanceLock()
    try:
        lock.acquire()
    except SingleInstanceError as exc:
        QMessageBox.critical(None, "BouncyBot - IBKR Portable Trading Bot already running", str(exc))
        return 2
    controller = None
    try:
        controller = TradingController()
        window = MainWindow(controller)
        _install_system_theme_hook(app, window)
        _install_session_shutdown_hook(app, window)
        window.show()
        return app.exec()
    finally:
        try:
            if controller is not None:
                shutdown = getattr(controller, "shutdown", None)
                if callable(shutdown):
                    try:
                        shutdown()
                    except Exception:
                        pass
        finally:
            lock.release()


if __name__ == "__main__":
    raise SystemExit(main())
