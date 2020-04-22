# -*- coding: utf-8 -*-

"""
Anki Add-on: HTML Cleaner

Main module

Cleans and minifies HTML content of current field, removing extraneous
tags and attributes copied over from apps like Word, etc.

Copyright: (c) Glutanimate 2017
License: GNU AGPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
"""
from aqt import gui_hooks
from .config import getUserOption
from aqt import mw
from aqt.webview import WebContent

import sys
import os
import re

# import modules from local path
# (insert needed in order to skip system packages)
sys.path.insert(0, os.path.dirname(__file__))
import bleach


# Htmllaundry depends on lxml which we cannot ship on all platforms
# If we can't import htmllaundry we will skip using it further down below
if getUserOption("use_html_laundry"):
    try:
        from htmllaundry import cleaners, sanitize
        LAUNDROMAT = True
    except ImportError:
        LAUNDROMAT = False


from aqt.qt import *
from aqt.editor import Editor
from anki.hooks import addHook
from anki.utils import json


# insert linebreak after regex match
brtags = (r"(</(div|p|br|li|ul|ol|blockquote|tr|"
    "table|thead|tfoot|tbody|h[1-9])>|<br>)([^\n])")


def laundryHtml(html):
    """Clean using htmllaundry/lxml"""
    # docs: http://lxml.de/api/lxml.html.clean.Cleaner-class.html

    cleaner = cleaners.LaundryCleaner(
                allow_tags = getUserOption("keep_tags"),
                safe_attrs = getUserOption("keep_attrs"),
                processing_instructions = True,
                meta = True,
                scripts = True,
                comments = True,
                javascript = True,
                annoying_tags = True,
                page_structure=False,
                remove_unknown_tags=False,
                safe_attrs_only = False,
                add_nofollow = False,
                style = False,
                links = False,
                frames = False)
    
    return sanitize(html, cleaner)


def bleachHtml(html):
    """Clean using bleach/html5lib"""
    # docs: https://bleach.readthedocs.io/en/latest/clean.html
    
    cleaned = bleach.clean(html,
        tags = getUserOption("keep_tags"),
        attributes = getUserOption("keep_attrs"),
        styles = getUserOption("keep_styles"),
        strip = True)

    return cleaned


def cleanHtml(html):
    """Clean HTML with cleaners and custom regexes"""
    html = html.replace("\n", " ")
    # both bleach and htmllaundry eat "<br />"...
    html = html.replace("<br />", "<br>")
    
    if getUserOption("use_html_laundry") and LAUNDROMAT:
        # lxml.clean will munch <br> tags for some reason, even though
        # they're whitelisted. This is an ugly workaround, but it works.
        html = html.replace("<br>", "|||LBR|||").replace("</br>", "|||LBR|||")
        html = laundryHtml(html)
        html = html.replace("|||LBR|||", "<br>")
    html = bleachHtml(html)

    # remove empty style attributes, try to pretty-format tags
    html = html.replace('<div><br></div>', '<br>')
    html = html.replace(' style=""', '')
    html = re.sub(brtags, r"\1\n\3", html)

    return html

    field = note.fields[ord]
    note.fields[ord] = cleanHtml(field)
    self._fieldUndo = (ord, html)
    print(f"field changed: {note.fields[ord] == field}")
    note.flush()

def onHtmlClean(self):
    """Executed on button press"""
    modifiers = self.mw.app.queryKeyboardModifiers()
    shift_and_click = modifiers == Qt.ShiftModifier
    if shift_and_click:
        self.onFieldUndo()
        return
    n = self.currentField
    self.clean_field(n)

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


def setupButtons(righttopbtns, editor):
    """Add buttons to editor"""
    html_clean_hotkey = getUserOption("html_clean_hotkey")
    html_paste_hotkey = getUserOption("html_paste_hotkey")
    righttopbtns.append(
        editor.addButton(icon="clean_html",
                         cmd="clean_html",
                         func=onHtmlClean,
                         label="cH",
                         tip="Clean HTML ({})<br>Undo with shift-click".format(html_clean_hotkey),
                         keys=html_clean_hotkey)
    )
    t = QShortcut(QKeySequence("Shift+"+html_clean_hotkey), editor.parentWindow)
    t.activated.connect(lambda: editor.onFieldUndo())
    t = QShortcut(QKeySequence(html_paste_hotkey), editor.parentWindow)
    t.activated.connect(lambda: editor.onHtmlPaste())


Editor.onHtmlPaste = onHtmlPaste
Editor.onFieldUndo = onFieldUndo
Editor.onHtmlClean = onHtmlClean
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
