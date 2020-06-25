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

import json

from anki.utils import stripHTML
from aqt import gui_hooks, mw
from aqt.editor import Editor
from aqt.qt import QClipboard, QCursor, QKeySequence, QMenu, QShortcut
from aqt.utils import askUser
from aqt.webview import WebContent

from .clean import cleanHtml_regular_use
from .config import getUserOption
from .custom_editors import DupeIgnoringEditor, ShortcutLessNonEditableEditor

mw.addonManager.setWebExports(__name__, r"web/.*")
addon_package = mw.addonManager.addonFromModule(__name__)


def process_all_fields(self, func):
    self._fieldUndo = None
    for n in range(len(self.note.fields)):
        if not self.note.fields[n]:
            continue
        self.note.fields[n] = func(self.note.fields[n])
    if not self.addMode:
        self.note.flush()
    self.loadNote()
    self.web.setFocus()
    self.web.eval("focusField(%d);" % n)


def onHtmlCleanAll(self):
    msg = "Clean ALL html fields of this note. This action cannot be undone. Proceed?"
    if not askUser(msg):
        return
    self.saveNow(lambda: 0)
    process_all_fields(self, cleanHtml_regular_use)


def process_field(self, n, func):
    self.saveNow(lambda: 0)
    html = self.note.fields[n]
    if not html:
        return
    self._fieldUndo = (n, html)
    cleaned = func(html)
    self.note.fields[n] = cleaned
    self.loadNote()
    self.web.setFocus()
    self.web.eval("focusField(%d);" % n)


def clean_field(self, n):
    self.saveNow(lambda: 0)
    process_field(self, n, cleanHtml_regular_use)


def clean_field_helper(editor):
    n = editor.currentField
    if isinstance(n, int):
        clean_field(editor, n)


# TODO: in some cases gets plain text with linesbreaks from clip.mimeData().text()
# whereas Anki's stripHTML and the following remove_html_with_bs4 fail
# not better than striphtml
"""
from bs4 import BeautifulSoup
def remove_html_with_bs4(code):
    soup = BeautifulSoup(code, "html.parser")
    out =  soup.text
    return out
"""


def tranform_all(self):
    msg = "Transform ALL fields of this note to plain text. This action cannot be undone. Proceed?"
    if not askUser(msg):
        return
    self.saveNow(lambda: 0)
    process_all_fields(self, stripHTML)


def transform_field(self, n):
    self.saveNow(lambda: 0)
    process_field(self, n, stripHTML)


def transform_field_helper(editor):
    n = editor.currentField
    if isinstance(n, int):
        transform_field(editor, n)


def onFieldUndo(self):
    """Executed on undo toggle"""
    if not hasattr(self, "_fieldUndo") or not self._fieldUndo:
        return
    n, html = self._fieldUndo
    self.note.fields[n] = html
    self.loadNote()
    self.web.setFocus()
    self.web.eval("focusField(%d);" % n)


def onSetNote(self, note, hide, focus):
    """Reset undo contents"""
    self._fieldUndo = None


def onHtmlPaste(self):
    """Executed on paste hotkey"""
    mime = self.mw.app.clipboard().mimeData(mode=QClipboard.Clipboard)
    html, internal = self.web._processMime(mime)
    if not html:
        return
    cleaned = cleanHtml_regular_use(html)
    self.web.eval(
        """
        var customPasteHTML = function(html) {
            setFormat("inserthtml", html);
        };
        var customFilterHTML = function(html) {
            // wrap it in <top> as we aren't allowed to change top level elements
            var top = $.parseHTML("<ankitop>" + html + "</ankitop>")[0];
            filterNode(top);
            var outHtml = top.innerHTML;
            // get rid of nbsp
            outHtml = outHtml.replace(/&nbsp;/ig, " ");
            return outHtml;
        };
        customPasteHTML(%s);
        """
        % json.dumps(cleaned)
    )


template = [
    [
        "shortcut_editor_clean_current_field",
        "&Clean current field",
        clean_field_helper,
    ],
    ["shortcut_editor_clean_all_fields", "Clean &all fields", onHtmlCleanAll],
    [
        "shortcut_editor_transform_current_field_plain_text",
        "&Transform current field to plain text",
        transform_field_helper,
    ],
    [
        "shortcut_editor_transform_all_fields_plain_text",
        "Transform all fields to &plain text",
        tranform_all,
    ],
    ["shortcut_editor_paste_cleaned_html", "paste cleaned html", onHtmlPaste],
    ["shortcut_editor_current_field_undo", "current field UNDO", onFieldUndo],
]


basic_stylesheet = """
QMenu::item {
    padding-top: 7px;
    padding-bottom: 7px;
    padding-right: 5px;
    padding-left: 5px;
    font-size: 15px;
}
QMenu::item:selected {
    color: black;
    background-color: #D9CD6D;
}
"""


def clean_html_menu(editor):
    m = QMenu(editor.mw)
    if getUserOption("shortcut_editor_menu_wider_fields"):
        m.setStyleSheet(basic_stylesheet)
    for userconfig, text, func in template:
        cut = getUserOption(userconfig)
        if cut:
            text += f"({cut})"
        a = m.addAction(text)
        a.triggered.connect(lambda _, e=editor, f=func: f(e))
    m.exec_(QCursor.pos())


def setupButtons(righttopbtns, editor):
    cut = getUserOption("shortcut_editor_menu_show")
    tip = "Clean HTML"
    if cut:
        tip += "(%s)".format(cut)
    righttopbtns.append(
        editor.addButton(
            icon="",
            cmd="clean_html",
            func=lambda e=editor: clean_html_menu(e),
            label="cH",
            tip=tip,
            keys=cut,
        )
    )
    for cut, text, func in template:
        cut = getUserOption(cut)
        if not cut:
            continue
        t = QShortcut(QKeySequence(cut), editor.parentWindow)
        t.activated.connect(lambda e=editor, f=func: f(e))


gui_hooks.editor_did_init_buttons.append(setupButtons)


def on_webview_will_set_content(web_content: WebContent, context):
    if not isinstance(
        context, (Editor, DupeIgnoringEditor, ShortcutLessNonEditableEditor)
    ):
        return
    web_content.js.append(f"/_addons/{addon_package}/js.js")


gui_hooks.webview_will_set_content.append(on_webview_will_set_content)


def loadNote(self):
    if not self.note:
        return
    self.web.eval(f"setCleanFields()")


gui_hooks.editor_did_load_note.append(loadNote)


def on_js_message(handled, cmd, editor):
    if not isinstance(editor, Editor):
        return handled
    if cmd.startswith("clean:"):
        if editor.note is None:
            return (True, None)
        idx = int(cmd[len("clean:") :])
        clean_field(editor, idx)
        return (True, None)
    return handled


gui_hooks.webview_did_receive_js_message.append(on_js_message)
