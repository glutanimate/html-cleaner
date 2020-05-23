# -*- coding: utf-8 -*-

"""
Copyright: (c) Glutanimate 2017
           (c) ijgnd 2020

License: GNU AGPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
"""

import aqt
from aqt import mw
from aqt.qt import (
    QAction,
)

from . import editor
from . import browser
from .conf_dialog import MyConfigWindow


aqt.dialogs.register_dialog("html_cleaner_config", MyConfigWindow, None)


def onAdjustSettings():
    d = MyConfigWindow(mw)
    d.show()


action = QAction(mw)
action.setText("Html Cleaner: Adjust Clean settings")
mw.form.menuTools.addAction(action)
action.triggered.connect(onAdjustSettings)

