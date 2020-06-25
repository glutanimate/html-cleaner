import os
import re
import sys

import bleach
from anki.hooks import wrap
from anki.utils import json
from aqt.qt import *

from .config import getUserOption

# import modules from local path
# (insert needed in order to skip system packages)
folder = os.path.dirname(__file__)
libfolder = os.path.join(folder, "_vendor")
sys.path.insert(0, libfolder)




# insert linebreak after regex match
brtags = (
    r"(</(div|p|br|li|ul|ol|blockquote|tr|"
    "table|thead|tfoot|tbody|h[1-9])>|<br>)([^\n])"
)


def laundryHtml(html, tags, attributes):
    """Clean using htmllaundry/lxml"""
    # docs: http://lxml.de/api/lxml.html.clean.Cleaner-class.html

    cleaner = cleaners.LaundryCleaner(
        allow_tags=tags,
        safe_attrs=attributes,
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


def bleachHtml(html, tags, attributes, styles):
    """Clean using bleach/html5lib"""
    # docs: https://bleach.readthedocs.io/en/latest/clean.html

    cleaned = bleach.clean(
        html, tags=tags, attributes=attributes, styles=styles, strip=True,
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


def cleanHtml(html, tags, attributes, styles, use_html_laundry):
    """Clean HTML with cleaners and custom regexes"""
    html = html.replace("\n", " ")
    # both bleach and htmllaundry eat "<br />"...
    html = html.replace("<br />", "<br>")

    if use_html_laundry and LAUNDROMAT:
        # lxml.clean will munch <br> tags for some reason, even though
        # they're whitelisted. This is an ugly workaround, but it works.
        html = html.replace("<br>", "|||LBR|||").replace("</br>", "|||LBR|||")
        html = laundryHtml(html, tags, attributes)
        html = html.replace("|||LBR|||", "<br>")
    html = bleachHtml(html, tags, attributes, styles)

    # remove empty style attributes, try to pretty-format tags
    html = html.replace("<div><br></div>", "<br>")
    html = html.replace(' style=""', "")
    html = re.sub(brtags, r"\1\n\3", html)

    return html


def cleanHtml_regular_use(html):
    group = getUserOption("clean_active_settings_group")
    tags = getUserOption("clean_settings").get(group).get("keep_tags")
    attributes = getUserOption("clean_settings").get(group).get("keep_attrs")
    styles = getUserOption("clean_settings").get(group).get("keep_styles")
    use_html_laundry = getUserOption("Use_html_laundry")
    return cleanHtml(html, tags, attributes, styles, use_html_laundry)
