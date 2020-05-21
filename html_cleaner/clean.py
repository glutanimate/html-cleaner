import sys
import os
import re

# import modules from local path
# (insert needed in order to skip system packages)
sys.path.insert(0, os.path.dirname(__file__))
import bleach

from aqt.qt import *
from anki.hooks import wrap
from anki.utils import json

from .config import getUserOption


# insert linebreak after regex match
brtags = (
    r"(</(div|p|br|li|ul|ol|blockquote|tr|"
    "table|thead|tfoot|tbody|h[1-9])>|<br>)([^\n])"
)


def laundryHtml(html):
    """Clean using htmllaundry/lxml"""
    # docs: http://lxml.de/api/lxml.html.clean.Cleaner-class.html

    cleaner = cleaners.LaundryCleaner(
        allow_tags=getUserOption("keep_tags"),
        safe_attrs=getUserOption("keep_attrs"),
        processing_instructions=True,
        meta=True,
        scripts=True,
        comments=True,
        javascript=True,
        annoying_tags=True,
        page_structure=False,
        remove_unknown_tags=False,
        safe_attrs_only=False,
        add_nofollow=False,
        style=False,
        links=False,
        frames=False,
    )

    return sanitize(html, cleaner)


def bleachHtml(html):
    """Clean using bleach/html5lib"""
    # docs: https://bleach.readthedocs.io/en/latest/clean.html

    cleaned = bleach.clean(
        html,
        tags=getUserOption("keep_tags"),
        attributes=getUserOption("keep_attrs"),
        styles=getUserOption("keep_styles"),
        strip=True,
    )

    return cleaned


# Htmllaundry depends on lxml which we cannot ship on all platforms
# If we can't import htmllaundry we will skip using it further down below
try:
    from htmllaundry import cleaners, sanitize
except ImportError:
    LAUNDROMAT = False
else:
    LAUNDROMAT = True


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
    html = html.replace("<div><br></div>", "<br>")
    html = html.replace(' style=""', "")
    html = re.sub(brtags, r"\1\n\3", html)

    return html
