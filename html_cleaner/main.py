# -*- coding: utf-8 -*-

"""
Anki Add-on: HTML Cleaner

Main module

Cleans and minifies HTML content of current field, removing extraneous
tags and attributes copied over from apps like Word, etc.

Copyright: (c) Glutanimate 2017
License: GNU AGPL, version 3 or later; http://www.gnu.org/copyleft/gpl.html
"""

### USER CONFIGURATION START ###

## BASIC

html_clean_hotkey = "Alt+M"
html_paste_hotkey = "Alt+V"

## ADVANCED

# Html tags to preserve
keep_tags = ['blockquote', 'a', 'img', 'em', 'b', 'p', 'strong',
        'h1', 'h2', 'h3', 'h4', 'h5', 'ul', 'ol', 'li', 'sub', 'sup',
        'abbr', 'acronym', 'dl', 'dt', 'dd', 'cite',
        'dft', 'br', 'table', 'tr', 'td', 'th', 'thead',
        'tbody', 'tfoot', 'div', 'span', 'u', 'i']

# Tag attributes to preserve
keep_attrs = [ 'style', 'rev', 'prompt', 'color', 'colspan', 
        'usemap', 'cols', 'accept', 'datetime', 'char', 
        'accept-charset', 'shape', 'href', 'hreflang', 
        'selected', 'frame', 'type', 'alt', 'nowrap', 
        'border', 'axis', 'compact', 'rows', 'checked',
        'for', 'start', 'hspace', 'charset', 'ismap', 'label',
        'target', 'method', 'readonly', 'rel', 'valign', 'scope',
        'size', 'cellspacing', 'cite', 'media', 'multiple', 'src',
        'rules', 'nohref', 'action', 'rowspan', 'abbr', 'span', 'height',
        'enctype', 'lang', 'disabled', 'name', 'charoff', 'clear', 'summary',
        'value', 'longdesc', 'headers', 'vspace', 'noshade', 'coords', 'width',
        'maxlength', 'cellpadding', 'title', 'align', 'dir', 'tabindex']

# Styles to preserve in the style attribute
keep_styles = ["color", "background", "font-weight", "font-family",
                "font-style", "font-size", "text-decoration", "margin-left"]

### USER CONFIGURATION END ###

import sys
import os
import re

# import modules from local path
# (insert needed in order to skip system packages)
sys.path.insert(0, os.path.dirname(__file__))
import bleach

from htmllaundry import cleaners, sanitize
# Htmllaundry depends on lxml which we cannot ship with this add-on
# If we can't import htmllaundry we will skip using it further down below
try:
    from htmllaundry import cleaners, sanitize
    LAUNDROMAT = True
except ImportError:
    LAUNDROMAT = False

from aqt.qt import *
from aqt.editor import Editor
from anki.hooks import wrap
from anki.utils import json


# insert linebreak after regex match
brtags = (r"(</(div|p|br|li|ul|ol|blockquote|tr|"
            "table|thead|tfoot|tbody|h[1-9]|)>)([^\n])")


def laundryHtml(html):
    """Clean using htmllaundry/lxml"""
    # docs: http://lxml.de/api/lxml.html.clean.Cleaner-class.html
    cleaner = cleaners.LaundryCleaner(
                allow_tags = keep_tags,
                safe_attrs = keep_attrs,
                page_structure = False,
                remove_unknown_tags = False,
                safe_attrs_only = True,
                add_nofollow = False,
                scripts = True,
                javascript = True,
                comments = True,
                style = True,
                links = False,
                meta = False,
                processing_instructions = True,
                frames = False,
                annoying_tags = True)
    
    return sanitize(html, cleaner)


def bleachHtml(html):
    """Clean using bleach/html5lib"""
    # docs: https://bleach.readthedocs.io/en/latest/clean.html
    cleaned = bleach.clean(html,
        tags = keep_tags,
        attributes = keep_attrs,
        styles = keep_styles,
        strip = True)

    return cleaned


def cleanHtml(html):
    """Clean HTML with cleaners and custom regexes"""
    html = html.replace("\n", " ")
    if LAUNDROMAT:
        html = laundryHtml(html)
    cleaned = bleachHtml(html)

    # remove empty style attributes, try to pretty-format tags
    cleaned = cleaned.replace('<div><br></div>', '<br>')
    cleaned = cleaned.replace(' style=""', '').replace("\n", "")
    cleaned = re.sub(brtags, r"\1\n\3", cleaned)

    return cleaned


def onHtmlClean(self):
    """Executed on button press"""
    modifiers = self.mw.app.queryKeyboardModifiers()
    shift_and_click = modifiers == Qt.ShiftModifier
    if shift_and_click:
        self.onFieldUndo()
        return
    self.saveNow()
    n = self.currentField
    html = self.note.fields[n]
    if not html:
        return 

    self._fieldUndo = (n, html)

    cleaned = cleanHtml(html)

    self.note.fields[n] = cleaned
    self.loadNote()
    self.web.setFocus()
    self.web.eval("focusField(%d);" % n)


def onFieldUndo(self):
    """Executued on undo toggle"""
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


def setupButtons(self):
    """Add buttons to editor"""
    self._addButton("clean_html", lambda: self.onHtmlClean(),
        text="cH",
        tip="Clean HTML ({})<br>Undo with shift-click".format(html_clean_hotkey),
        key=html_clean_hotkey)
    t = QShortcut(QKeySequence("Shift+"+html_clean_hotkey), self.parentWindow)
    t.activated.connect(lambda: self.onFieldUndo())
    t = QShortcut(QKeySequence(html_paste_hotkey), self.parentWindow)
    t.activated.connect(lambda: self.onHtmlPaste())


Editor.onHtmlPaste = onHtmlPaste
Editor.onFieldUndo = onFieldUndo
Editor.onHtmlClean = onHtmlClean
Editor.setupButtons = wrap(Editor.setupButtons, setupButtons)