# -*- coding: utf-8 -*-

import re
import sys
# import modules from local path
# (insert needed in order to skip system packages)
sys.path.insert(0, "../html_cleaner")
import bleach


# Htmllaundry depends on lxml which we cannot ship with this add-on
# for that reason we have to check if we can import htmllaundry.
# If we can't we will skip using htmllaundry further down below
try:
    from htmllaundry import cleaners, sanitize
    LAUNDROMAT = True
except ImportError:
    LAUNDROMAT = False


html  = u"""<div><b>EXAMPLE 1</b></div>
<!--StartFragment--><span style='font-size:15.0pt;mso-bidi-font-size:12.0pt;font-family:""Times New Roman"",""serif"";color:black;mso-ansi-language:EN;mso-fareast-language:EN;mso-bidi-language: SW-AS'>LOREM DOLOR <b style=""mso-bidi-font-weight:normal"">SIT</b> <u>AMET</u></span><!--EndFragment-->
<div><b>EXAMPLE 2</b></div>
<span style="color: rgb(51, 51, 51);font-family: SpiegelSansWeb, Calibri, Candara, Arial, Helvetica, sans-serif;font-size: 18px">Lorem ipsum doler sit amet&nbsp;</span><a href="http://www.spiegel.de/" title="Lorem" class="text-link-int lp-text-link-int" style="color: rgb(153, 0, 0); font-family: SpiegelSansWeb, Calibri, Candara, Arial, Helvetica, sans-serif; font-size: 18px;">Lorem ipsum</a><span style="color: rgb(51, 51, 51); font-family: SpiegelSansWeb, Calibri, Candara, Arial, Helvetica, sans-serif; font-size: 18px;">&nbsp;ipsum dolore sit amet.</span>"""


# Html tags to preserve
keep_tags = ['blockquote', 'a', 'img', 'em', 'b', 'p', 'strong',
        'h1', 'h2', 'h3', 'h4', 'h5', 'ul', 'ol', 'li', 'sub', 'sup',
        'abbr', 'acronym', 'dl', 'dt', 'dd', 'cite',
        'dft', 'br', 'table', 'tr', 'td', 'th', 'thead',
        'tbody', 'tfoot', 'div', 'u', 'i']

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
        'maxlength', 'cellpadding', 'title', 'dir', 'tabindex']

# Styles to preserve in the style attribute
keep_styles = ["margin-left"]

# insert linebreak after regex match
brtags = (r"(</(div|p|br|li|ul|ol|blockquote|tr|"
            "table|thead|tfoot|tbody|h[1-9]|)>)([^\n])")


def laundryHtml(html):
    cleaner = cleaners.LaundryCleaner(
                page_structure=False,
                remove_unknown_tags=False,
                allow_tags = keep_tags,
                safe_attrs = keep_attrs,
                safe_attrs_only=True,
                add_nofollow=False,
                scripts=True,
                javascript=True,
                comments=True,
                style=True,
                links=False,
                meta=False,
                processing_instructions=True,
                frames=False,
                annoying_tags=True)
    
    return sanitize(html, cleaner)


def bleachHtml(html):
    cleaned = bleach.clean(html,
        tags = keep_tags,
        attributes = keep_attrs,
        styles = keep_styles,
        strip = True
        )
    return cleaned


def cleanHtml(html):
    html = html.replace("\n", " ")
    if LAUNDROMAT:
        html = laundryHtml(html)
    cleaned = bleachHtml(html)

    # remove empty style attributes, try to pretty-format tags
    cleaned = cleaned.replace('<div><br></div>', '<br>')
    cleaned = cleaned.replace(' style=""', '').replace("\n", "")
    cleaned = re.sub(brtags, r"\1\n\3", cleaned)

    return cleaned

cleaned = cleanHtml(html)

print cleaned