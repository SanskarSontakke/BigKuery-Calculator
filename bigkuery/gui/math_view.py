"""
MathView - KaTeX-backed math renderer.

Renders a list of LaTeX strings inside a lightweight QWebEngineView using a
bundled, offline copy of KaTeX. Exposes ``KATEX_AVAILABLE`` so the rest of the
GUI can gracefully fall back to plain HTML labels when PyQt6-WebEngine (or the
bundled assets) are not present.
"""

from __future__ import annotations

import os
import json

_ASSETS_DIR = os.path.join(os.path.dirname(__file__), "assets")
_HOST_HTML = os.path.join(_ASSETS_DIR, "katex_host.html")
_KATEX_JS = os.path.join(_ASSETS_DIR, "katex", "katex.min.js")

# Allow forcing the HTML fallback (e.g. headless test/CI environments, where
# QtWebEngine's compositor cannot run under the 'offscreen' Qt platform).
_DISABLED = os.environ.get("BIGKUERY_DISABLE_KATEX", "").lower() in ("1", "true", "yes")

if _DISABLED:
    _WEBENGINE_OK = False
else:
    try:
        from PyQt6.QtWebEngineWidgets import QWebEngineView
        from PyQt6.QtWebEngineCore import QWebEngineSettings
        _WEBENGINE_OK = True
    except Exception:
        _WEBENGINE_OK = False

# KaTeX rendering is only available when both the engine and the bundled assets
# are present. The GUI checks this flag to decide between LaTeX and HTML output.
KATEX_AVAILABLE = (
    _WEBENGINE_OK
    and os.path.exists(_HOST_HTML)
    and os.path.exists(_KATEX_JS)
)


if KATEX_AVAILABLE:
    from PyQt6.QtCore import QUrl, pyqtSignal, QTimer
    from PyQt6.QtGui import QColor

    class MathView(QWebEngineView):
        """A small web view that renders LaTeX lines via KaTeX and self-sizes."""

        # Emitted with (width, height) once content has been measured.
        content_resized = pyqtSignal(int, int)

        def __init__(self, parent=None):
            super().__init__(parent)
            self._ready = False
            self._pending = None  # lines queued before the page finished loading

            # Transparent background so the card colour shows through.
            self.page().setBackgroundColor(QColor(0, 0, 0, 0))

            settings = self.settings()
            settings.setAttribute(
                QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, True
            )
            settings.setAttribute(
                QWebEngineSettings.WebAttribute.ShowScrollBars, False
            )
            self.setStyleSheet("background: transparent;")
            self.setMinimumSize(40, 24)

            self.loadFinished.connect(self._on_loaded)
            self.load(QUrl.fromLocalFile(_HOST_HTML))

        def _on_loaded(self, ok: bool):
            self._ready = True
            if self._pending is not None:
                lines, wrap = self._pending
                self._pending = None
                self._render(lines, wrap)

        def set_lines(self, lines, wrap=False):
            """Render the given LaTeX strings (queued until the page is ready).

            When ``wrap`` is True, content is capped to a max width and wraps
            instead of growing arbitrarily wide.
            """
            if not self._ready:
                self._pending = (list(lines), bool(wrap))
                return
            self._render(list(lines), bool(wrap))

        def _render(self, lines, wrap=False):
            payload = json.dumps(list(lines))
            self.page().runJavaScript(f"renderLines({payload}, {json.dumps(bool(wrap))});", self._apply_size)
            # Re-measure shortly after, in case web-font loading reflowed the content.
            QTimer.singleShot(140, self._remeasure)

        def _remeasure(self):
            self.page().runJavaScript("measure();", self._apply_size)

        def _apply_size(self, size):
            try:
                w, h = int(size[0]), int(size[1])
            except (TypeError, ValueError, IndexError):
                return
            w = max(40, w + 8)
            h = max(24, h + 8)
            if w == self.width() and h == self.height():
                return
            self.setFixedSize(w, h)
            self.content_resized.emit(w, h)
