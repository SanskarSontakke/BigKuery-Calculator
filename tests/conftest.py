"""Shared pytest configuration.

QtWebEngine cannot run under the headless 'offscreen' Qt platform used for the
test suite, so we force the HTML fallback renderer. The live KaTeX rendering
path is exercised by running the actual application on a real display.
"""

import os
import tempfile

# Must be set before any bigkuery.gui module is imported.
os.environ.setdefault("BIGKUERY_DISABLE_KATEX", "1")

# Isolate QSettings to a throwaway location so tests neither read nor clobber the
# user's real saved workspaces/settings (and stay independent of prior app runs).
from PyQt6.QtCore import QSettings

_TMP_SETTINGS = tempfile.mkdtemp(prefix="bigkuery_test_settings_")
QSettings.setDefaultFormat(QSettings.Format.IniFormat)
QSettings.setPath(
    QSettings.Format.IniFormat, QSettings.Scope.UserScope, _TMP_SETTINGS
)
