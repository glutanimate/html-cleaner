# -*- coding: utf-8 -*-

import re
import sys
# import modules from local path
# (insert needed in order to skip system packages)
sys.path.insert(0, "../html_cleaner")
import bleach


# Htmllaundry depends on lxml which we cannot ship on all platforms
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
<span style="color: rgb(51, 51, 51);font-family: SpiegelSansWeb, Calibri, Candara, Arial, Helvetica, sans-serif;font-size: 18px">Lorem ipsum doler sit amet&nbsp;</span><a href="http://www.spiegel.de/" title="Lorem" class="text-link-int lp-text-link-int" style="color: rgb(153, 0, 0); font-family: SpiegelSansWeb, Calibri, Candara, Arial, Helvetica, sans-serif; font-size: 18px;">Lorem ipsum</a><span style="color: rgb(51, 51, 51); font-family: SpiegelSansWeb, Calibri, Candara, Arial, Helvetica, sans-serif; font-size: 18px;">&nbsp;ipsum dolore sit amet.</span>
<div><b>EXAMPLE 3</b></div>
<!--StartFragment--><span style="font-size:12.0pt;line-height:100%;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;;mso-fareast-font-family:&quot;Times New Roman&quot;;mso-fareast-theme-font:minor-fareast;color:black;mso-ansi-language:DE;mso-fareast-language:DE;mso-bidi-language:AR-SA">Überschrift</span><div><span style="font-size:12.0pt;line-height:100%;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;;mso-fareast-font-family:&quot;Times New Roman&quot;;mso-fareast-theme-font:minor-fareast;color:black;mso-ansi-language:DE;mso-fareast-language:DE;mso-bidi-language:AR-SA"><br></span></div>
<div>Das ist der <b>erste</b>&nbsp;Beispielsatz an
dieser Stelle.</div>
<p class="MsoNormal" align="left" style="margin:0cm;margin-bottom:.0001pt;
text-align:left;text-indent:0cm;line-height:normal"><o:p></o:p></p>
<span style="font-size:12.0pt;line-height:100%;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;;mso-fareast-font-family:&quot;Times New Roman&quot;;mso-fareast-theme-font:minor-fareast;color:black;mso-ansi-language:DE;mso-fareast-language:DE;mso-bidi-language:
AR-SA">Das ist der zweite
Beispielsatz</span><!--EndFragment--><div><span style="font-size:12.0pt;line-height:100%;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;;mso-fareast-font-family:&quot;Times New Roman&quot;;mso-fareast-theme-font:minor-fareast;color:black;mso-ansi-language:DE;mso-fareast-language:DE;mso-bidi-language:
AR-SA"><br></span></div>
<div><span style="font-size:12.0pt;line-height:100%;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;;mso-fareast-font-family:&quot;Times New Roman&quot;;mso-fareast-theme-font:minor-fareast;color:black;mso-ansi-language:DE;mso-fareast-language:DE;mso-bidi-language:
AR-SA"><br></span></div>
<div><span style="font-size:12.0pt;line-height:100%;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;;mso-fareast-font-family:&quot;Times New Roman&quot;;mso-fareast-theme-font:minor-fareast;color:black;mso-ansi-language:DE;mso-fareast-language:DE;mso-bidi-language:
AR-SA"><br></span></div>
<div><span style="font-size:12.0pt;line-height:100%;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;;mso-fareast-font-family:&quot;Times New Roman&quot;;mso-fareast-theme-font:minor-fareast;color:black;mso-ansi-language:DE;mso-fareast-language:DE;mso-bidi-language:
AR-SA"><br></span></div>
<div><span style="font-size:12.0pt;line-height:100%;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;;mso-fareast-font-family:&quot;Times New Roman&quot;;mso-fareast-theme-font:minor-fareast;color:black;mso-ansi-language:DE;mso-fareast-language:DE;mso-bidi-language:
AR-SA"><!--StartFragment--><span style="font-size:12.0pt;line-height:100%;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;;mso-fareast-font-family:&quot;Times New Roman&quot;;mso-fareast-theme-font:minor-fareast;color:black;mso-ansi-language:DE;mso-fareast-language:DE;mso-bidi-language:AR-SA">Das ist ein
dritter Satz.&nbsp;</span><!--EndFragment--></span></div>
<div><span style="font-size:12.0pt;line-height:100%;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;;mso-fareast-font-family:&quot;Times New Roman&quot;;mso-fareast-theme-font:minor-fareast;color:black;mso-ansi-language:DE;mso-fareast-language:DE;mso-bidi-language:
AR-SA"><br></span></div>
<div><span style="font-size:12.0pt;line-height:100%;font-family:&quot;Times New Roman&quot;,&quot;serif&quot;;mso-fareast-font-family:&quot;Times New Roman&quot;;mso-fareast-theme-font:minor-fareast;color:black;mso-ansi-language:DE;mso-fareast-language:DE;mso-bidi-language:
AR-SA"><br></span></div>
<div><img src="paste-921834426494981.jpg"></div>"""


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
    "table|thead|tfoot|tbody|h[1-9])>|<br>)([^\n])")

use_html_laundry = False


def laundryHtml(html):
    """Clean using htmllaundry/lxml"""
    # docs: http://lxml.de/api/lxml.html.clean.Cleaner-class.html

    cleaner = cleaners.LaundryCleaner(
                allow_tags = keep_tags,
                safe_attrs = keep_attrs,
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
        tags = keep_tags,
        attributes = keep_attrs,
        styles = keep_styles,
        strip = True)

    return cleaned


def cleanHtml(html):
    """Clean HTML with cleaners and custom regexes"""
    html = html.replace("\n", " ")
    # both bleach and htmllaundry eat "<br />"...
    html = html.replace("<br />", "<br>")
    
    if use_html_laundry and LAUNDROMAT:
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

cleaned = cleanHtml(html)

print cleaned