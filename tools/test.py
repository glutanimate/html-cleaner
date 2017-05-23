# -*- coding: utf-8 -*-

import re
import sys
# import modules from local path
# (insert needed in order to skip system packages)
sys.path.insert(0, "../html_cleaner")
import bleach


html  = u"""
<div><b>EXAMPLE 1</b></div>
<!--StartFragment--><span style='font-size:15.0pt;mso-bidi-font-size:12.0pt;font-family:""Times New Roman"",""serif"";color:black;mso-ansi-language:EN;mso-fareast-language:EN;mso-bidi-language: SW-AS'>LOREM DOLOR <b style=""mso-bidi-font-weight:normal"">SIT</b> <u>AMET</u></span><!--EndFragment-->
<div><b>EXAMPLE 2</b></div>
<span style="color: rgb(51, 51, 51);font-family: SpiegelSansWeb, Calibri, Candara, Arial, Helvetica, sans-serif;font-size: 18px">Lorem ipsum doler sit amet&nbsp;</span><a href="http://www.spiegel.de/" title="Lorem" class="text-link-int lp-text-link-int" style="color: rgb(153, 0, 0); font-family: SpiegelSansWeb, Calibri, Candara, Arial, Helvetica, sans-serif; font-size: 18px;">Lorem ipsum</a><span style="color: rgb(51, 51, 51); font-family: SpiegelSansWeb, Calibri, Candara, Arial, Helvetica, sans-serif; font-size: 18px;">&nbsp;ipsum dolore sit amet.</span>
"""

# Html tags to preserve
keep_tags = ['blockquote', 'a', 'img', 'em', 'b', 'p', 'strong',
        'h1', 'h2', 'h3', 'h4', 'h5', 'ul', 'ol', 'li', 'sub', 'sup',
        'abbr', 'acronym', 'dl', 'dt', 'dd', 'cite',
        'dft', 'br', 'table', 'tr', 'td', 'th', 'thead',
        'tbody', 'tfoot', 'div', 'span']

# Tag attributes to preserve
keep_attrs = ['rev', 'prompt', 'color', 'colspan', 'accesskey', 
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
        'maxlength', 'cellpadding', 'title', 'align', 'dir', 'tabindex', 'style']

# Styles to preserve in the style attribute
keep_styles = ["color", "background", "font-weight", "font-family",
                "font-style", "font-size"]


# insert linebreak after regex match
brtags = (r"(</(div|p|br|li|ul|ol|blockquote|tr|"
            "table|thead|tfoot|tbody|h[1-9]|)>)([^\n])")

cleaned = bleach.clean(html.replace("\n", ""),
        tags = keep_tags,
        attributes = keep_attrs,
        styles = keep_styles,
        strip = True
        )
cleaned = cleaned.replace(' style=""', '').replace("\n", "")
cleaned = re.sub(brtags, r"\1\n\3", cleaned)
print cleaned