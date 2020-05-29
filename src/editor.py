# -*- coding: utf-8 -*-

"""
Anki Add-on: HTML Cleaner

Main module

Cleans and minifies HTML content of current field, removing extraneous
tags and attributes copied over from apps like Word, etc.

Copyright: (c) Glutanimate 2017
           (c) Arthur Milchior 2020
           (c) ijgnd 2020

License: GNU AGPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
"""

import json

from anki.utils import stripHTML

from aqt import gui_hooks
from aqt import mw
from aqt.editor import Editor
from aqt.webview import WebContent
from aqt.qt import (
    QClipboard,
    QCursor,
    QKeySequence,
    QMenu,
    QShortcut,
    Qt,
)
from aqt.utils import askUser

from .clean import cleanHtml_regular_use
from .config import getUserOption
from .custom_editors import DupeIgnoringEditor, ShortcutLessNonEditableEditor


mw.addonManager.setWebExports(__name__, r".*(css|js)")
addon_package = mw.addonManager.addonFromModule(__name__)


def process_all_fields(self, func):
    self._fieldUndo = None
    for n in range(len(self.note.fields)):
        if not self.note.fields[n]:
            continue
        self.note.fields[n] = func(self.note.fields[n])
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
    mime = self.web.mungeClip(mode=QClipboard.Clipboard)
    html = mime.html()
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
    ["Shortcut editor: clean current field", "&Clean current field", clean_field_helper],
    ["Shortcut editor: clean all fields", "Clean &all fields", onHtmlCleanAll],
    ["Shortcut editor: transform current field to plain text", "&Transform current field to plain text", transform_field_helper],
    ["Shortcut editor: transform all fields to plain text", "Transform all fields to &plain text", tranform_all],
    ["Shortcut editor: paste cleaned html", "paste cleaned html", onHtmlPaste],
    ["Shortcut editor: current field UNDO", "current field UNDO", onFieldUndo],
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
    if getUserOption("Shortcut editor: Menu wider fields"):
        m.setStyleSheet(basic_stylesheet)
    for userconfig, text, func in template:
        cut = getUserOption(userconfig)
        if cut:
            text += f"({cut})"
        a = m.addAction(text)
        a.triggered.connect(lambda _, e=editor, f=func: f(e))
    m.exec_(QCursor.pos())


def setupButtons(righttopbtns, editor):
    cut = getUserOption("Shortcut editor: Menu show")
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
    if not isinstance(context, (Editor, DupeIgnoringEditor, ShortcutLessNonEditableEditor)):
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
