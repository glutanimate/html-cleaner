# -*- coding: utf-8 -*-

"""
Anki Add-on: HTML Cleaner

Main module

Cleans and minifies HTML content of current field, removing extraneous
tags and attributes copied over from apps like Word, etc.

Copyright: (c) Glutanimate 2017
License: GNU AGPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
"""

import json

from aqt import gui_hooks
from aqt import mw
from aqt.editor import Editor
from aqt.webview import WebContent
from aqt.qt import (
    QClipboard,
    QKeySequence, 
    QShortcut, 
    Qt,
)

from .clean import cleanHtml
from .config import getUserOption




def onHtmlClean(self):
    """Executed on button press"""
    self.saveNow(lambda:0)
    modifiers = self.mw.app.queryKeyboardModifiers()
    shift_and_click = modifiers == Qt.ShiftModifier
    if shift_and_click:
        self.onFieldUndo()
        return
    self._fieldUndo = None
    for n in range(len(self.note.fields)):
        if not self.note.fields[n]:
            continue
        self.note.fields[n] = cleanHtml(self.note.fields[n])
    self.note.flush()
    self.loadNote()
    self.web.setFocus()
    self.web.eval("focusField(%d);" % n)
Editor.onHtmlClean = onHtmlClean


def clean_field(self, n):
    self.saveNow(lambda:0)
    html = self.note.fields[n]
    if not html:
        return 

    self._fieldUndo = (n, html)

    cleaned = cleanHtml(html)

    self.note.fields[n] = cleaned
    self.loadNote()
    self.web.setFocus()
    self.web.eval("focusField(%d);" % n)
Editor.clean_field = clean_field


def onFieldUndo(self):
    """Executed on undo toggle"""
    if not hasattr(self, "_fieldUndo") or not self._fieldUndo:
        return
    n, html = self._fieldUndo
    self.note.fields[n] = html
    self.loadNote()
    self.web.setFocus()
    self.web.eval("focusField(%d);" % n)
Editor.onFieldUndo = onFieldUndo


def onSetNote(self, note, hide, focus):
    """Reset undo contents"""
    self._fieldUndo = None


def onHtmlPaste(self):
    """Executed on paste hotkey"""
    mime = self.web.mungeClip(mode=QClipboard.Clipboard)
    html = mime.html()
    if not html:
        return
    cleaned = cleanHtml(html)
    self.web.eval("""
        var pasteHTML = function(html) {
            setFormat("inserthtml", html);
        };
        var filterHTML = function(html) {
            // wrap it in <top> as we aren't allowed to change top level elements
            var top = $.parseHTML("<ankitop>" + html + "</ankitop>")[0];
            filterNode(top);
            var outHtml = top.innerHTML;
            // get rid of nbsp
            outHtml = outHtml.replace(/&nbsp;/ig, " ");
            return outHtml;
        };
        pasteHTML(%s);
        """ % json.dumps(cleaned))
Editor.onHtmlPaste = onHtmlPaste


def setupButtons(righttopbtns, editor):
    """Add buttons to editor"""
    html_clean_hotkey = getUserOption("html_clean_hotkey")
    html_paste_hotkey = getUserOption("html_paste_hotkey")
    righttopbtns.append(
        editor.addButton(icon="clean_html",
                         cmd="clean_html",
                         func=onHtmlClean,
                         label="cH",
                         tip="Clean HTML ({})".format(html_clean_hotkey),
                         keys=html_clean_hotkey)
    )
    t = QShortcut(QKeySequence("Shift+"+html_clean_hotkey), editor.parentWindow)
    t.activated.connect(lambda: editor.onFieldUndo())
    t = QShortcut(QKeySequence(html_paste_hotkey), editor.parentWindow)
    t.activated.connect(lambda: editor.onHtmlPaste())
gui_hooks.editor_did_init_buttons.append(setupButtons)


mw.addonManager.setWebExports(__name__, r".*(css|js)")
addon_package = mw.addonManager.addonFromModule(__name__)
def on_webview_will_set_content(web_content: WebContent, context):
    if not isinstance(context, Editor):
        return
    web_content.js.append(
        f"/_addons/{addon_package}/js.js")
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
        idx = int(cmd[len("clean:"):])
        editor.clean_field(idx)
        return (True, None)
    return handled
gui_hooks.webview_did_receive_js_message.append(on_js_message)
