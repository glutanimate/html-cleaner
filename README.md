## HTML Cleaner Add-on for Anki

Cleans and minifies HTML content of the current field, removing extraneous tags and attributes copied over from apps like Word, Chrome, etc.

## Usage

The add-on comes with a button and two hotkeys:

- Clicking on the *cH* button in the editor will clean the HTML code of the active field. The same functionality can also be invoked via <kbd>Alt</kbd> + <kbd>H</kbd>
- Shift-clicking the button or combining the aforementioned hotkey with Shift will undo the changes to the current field. (Anki's inbuilt undo functionality does not work with the add-on. This is a limitation that can't be solved trivially, I'm afraid.)
- <kbd>Alt</kbd> + <kbd>V</kbd> will clean the clipboard selection and paste the processed text into the current field

## Configuration

The add-on's HTML processing is highly configurable. All options can be accessed by editing the configuration section of `html_cleaner/main.py`.

## License and Credits

*Cloze Overlapper* is *Copyright © 2016-2017 [Aristotelis P.](https://github.com/Glutanimate)*

Licensed under the [GNU AGPL v3](https://www.gnu.org/licenses/agpl.html).

This add-on would not not have been possible without the following open-source libraries:

- [Bleach](https://github.com/mozilla/bleach) 2.0.0. Copyright (c) 2014-2017 Mozilla Foundation. Licensed under the Apache License 2.0
- [html5lib](https://github.com/html5lib/) 0.999999999. Copyright (c) 2006-2013 James Graham and other contributors. Licensed under the MIT license.
- [webencodings](https://github.com/gsnedders/python-webencodings) 0.5.1. Copyright (c) 2012-2017 Geoffrey Sneddon. Licensed under the BSD license.
- [six](https://github.com/benjaminp/six) 1.10.0. Copyright (c) 2010-2015 Benjamin Peterson. Licensed under the MIT license