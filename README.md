## HTML Cleaner Add-on for Anki

Cleans and minifies HTML content of the current field, removing extraneous tags and attributes copied over from apps like Word, Chrome, etc.

## Usage

The add-on comes with a button and two hotkeys:

- Clicking on the *cH* button in the editor will clean the HTML code of the active field. The same functionality can also be invoked via <kbd>Alt</kbd> + <kbd>H</kbd>
- Shift-clicking the button or combining the aforementioned hotkey with Shift will undo the changes to the current field. (Anki's inbuilt undo functionality does not work with the add-on. This is a limitation that can't be solved trivially, I'm afraid.)
- <kbd>Alt</kbd> + <kbd>V</kbd> will clean the clipboard selection and paste the processed text into the current field

## Configuration

The add-on's HTML processing is highly configurable. All options can be accessed by editing the configuration section of `html_cleaner/main.py`.

## Platform Support

*htmllaundry availability*

HTML processing is provided by the Bleach library on all platforms. The add-on can also be configured to use the [`htmllaundry` library](https://github.com/wichert/htmllaundry) which can improve the cleaning results under under some circumstances.

`htmllaundry` depends on `lxml` which Anki unfortunately does not ship with. In contrast to the other libraries included in this add-on, `lxml` cannot be easily be packaged for all platforms because it needs to be compiled. For that reason `htmllaundry` support is only available on Windows and Linux right now.

*Issues with symlinks on Linux*

Because HTML cleaner comes with precompiled libraries on Linux, invoking the add-on from a symlinked Windows partition (e.g. NTFS) might lead to a permission error. The reason for this is that the executable bit is sometimes turned off by default for Windows partitions. If you run into this problem you can either look into adjusting your partition mounting settings or moving the add-ons directory to one of your Linux drives.

## License and Credits

*Cloze Overlapper* is *Copyright © 2016-2017 [Aristotelis P.](https://github.com/Glutanimate)*

This add-on was developed on a commission by a fellow Anki user. All credit for the original idea goes to them.

I'm always happy for new add-on commissions. If you'd like to hire my services to work an add-on or new feature, please feel free to reach out to me through *ankiglutanimate [αt] gmail . com*.

Licensed under the [GNU AGPL v3](https://www.gnu.org/licenses/agpl.html).

This add-on would not not have been possible without the following open-source libraries:

- [Bleach](https://github.com/mozilla/bleach) 2.0.0. Copyright (c) 2014-2017 Mozilla Foundation. Licensed under the Apache License 2.0
- [html5lib](https://github.com/html5lib/) 0.999999999. Copyright (c) 2006-2013 James Graham and other contributors. Licensed under the MIT license.
- [htmllaundry](https://github.com/wichert/htmllaundry) 2.1. Copyright (c) 2010-2016 Wichert Akkerman. Licensed under the BSD license.
- [lxml](http://lxml.de/) 3.7.3. Copyright (c) Infrae. Licensed under the BSD license.
- [webencodings](https://github.com/gsnedders/python-webencodings) 0.5.1. Copyright (c) 2012-2017 Geoffrey Sneddon. Licensed under the BSD license.
- [six](https://github.com/benjaminp/six) 1.10.0. Copyright (c) 2010-2015 Benjamin Peterson. Licensed under the MIT license