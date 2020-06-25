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

from anki.utils import stripHTML

from aqt import gui_hooks
from aqt.browser import Browser
from aqt.qt import (
    QCheckBox,
    QComboBox,
    QDialog,
    QDialogButtonBox,
    QHBoxLayout,
    QKeySequence,
    QLabel,
    Qt,
    QVBoxLayout,
    QShortcut,
)
from aqt.utils import tooltip

from .clean import cleanHtml_regular_use
from .config import getUserOption


class BatchCleanDialog(QDialog):
    """Browser batch editing dialog"""

    def __init__(self, browser, nids):
        QDialog.__init__(self, parent=browser)
        self.browser = browser
        self.nids = nids
        self._setupUi()

    def _setupUi(self):
        flabel = QLabel("In this field:")
        self.fsel = QComboBox()
        fields = self._getFields()
        self.fsel.addItems(fields)
        self.cb = QCheckBox()
        self.cb.setText("transform to plain text")
        f_hbox = QHBoxLayout()
        f_hbox.addWidget(flabel)
        f_hbox.addWidget(self.fsel)
        f_hbox.addWidget(self.cb)
        f_hbox.setAlignment(Qt.AlignLeft)

        button_box = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel,
            orientation=Qt.Horizontal,
            parent=self,
        )

        bottom_hbox = QHBoxLayout()
        bottom_hbox.addWidget(button_box)

        vbox_main = QVBoxLayout()
        vbox_main.addLayout(f_hbox)
        vbox_main.addLayout(bottom_hbox)
        self.setLayout(vbox_main)
        self.setWindowTitle("Batch Clean Selected Notes")
        button_box.rejected.connect(self.reject)
        button_box.accepted.connect(self.accept)
        self.rejected.connect(self.reject)
        self.accepted.connect(self.accept)
        self.fsel.setFocus()

    def _getFields(self):
        nid = self.nids[0]
        mw = self.browser.mw
        model = mw.col.getNote(nid).model()
        fields = mw.col.models.fieldNames(model)
        return fields

    def reject(self):
        self.close()

    def accept(self):
        if self.cb.isChecked():
            func = stripHTML
        else:
            func = cleanHtml_regular_use
        self.browser.mw.checkpoint("batch edit")
        self.browser.mw.progress.start()
        self.browser.model.beginReset()
        fld_name = self.fsel.currentText()
        cnt = 0
        for nid in self.nids:
            note = self.browser.mw.col.getNote(nid)
            cleaned = func(note[fld_name])
            if cleaned != note[fld_name]:
                cnt += 1
                note[fld_name] = cleaned
                note.flush()
        self.browser.model.endReset()
        self.browser.mw.requireReset()
        self.browser.mw.progress.finish()
        self.browser.mw.reset()
        self.close()
        tooltip(f"{cnt} notes cleaned")

    def closeEvent(self, evt):
        evt.accept()


def onBatchClean(browser):
    nids = browser.selectedNotes()
    if not nids:
        tooltip("No cards selected.")
        return
    dialog = BatchCleanDialog(browser, nids)
    dialog.exec_()


def add_menu(browser):
    menu = browser.form.menuEdit
    menu.addSeparator()
    a = menu.addAction("Batch clean HTML...")
    cut = getUserOption("shortcut_browser_batch_clean")
    if cut:
        a.setShortcut(QKeySequence(cut))
    a.triggered.connect(lambda _, b=browser: onBatchClean(b))


gui_hooks.browser_menus_did_init.append(add_menu)
