# -*- coding: utf-8 -*-

# HTML Cleaner Add-on for Anki
#
# Copyright (C) 2016-2020  Aristotelis P. <https://glutanimate.com/>
# Copyright (C) 2020  Arthur Milchior <arthur@milchior.fr>
# Copyright (C) 2020  ijgnd <https://github.com/ijgnd>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the license file that accompanied this program.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# NOTE: This program is subject to certain additional terms pursuant to
# Section 7 of the GNU Affero General Public License.  You should have
# received a copy of these additional terms immediately following the
# terms and conditions of the GNU Affero General Public License that
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.

"""
Initializes add-on components.
"""

import aqt
from aqt import mw
from aqt.qt import QAction

from . import browser, editor
from .conf_dialog import MyConfigWindow
from .config import getUserOption

aqt.dialogs.register_dialog("html_cleaner_config", MyConfigWindow, None)


def onAdjustSettings():
    aqt.dialogs.open("html_cleaner_config", mw)


if getUserOption("config window: show experimental config window"):
    action = QAction(mw)
    action.setText("Html Cleaner: Adjust Clean settings")
    mw.form.menuTools.addAction(action)
    action.triggered.connect(onAdjustSettings)
