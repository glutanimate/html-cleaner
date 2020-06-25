<!-- BANNER -->

HTML Cleaner is an add-on for Anki.

![](https://raw.githubusercontent.com/glutanimate/html-cleaner/master/screenshots/screenshot.png)

### USAGE

The add-on comes with a button and two hotkeys:

- Clicking on the *cH* button in the editor will clean the HTML code of the active field. The same functionality can also be invoked via a custom shortcut that you can configure in the add-on config.
- Shift-clicking the button or combining the aforementioned hotkey with Shift will undo the changes to the current field. (Anki's inbuilt undo functionality does not work with the add-on. This is a limitation that can't be solved trivially, I'm afraid.)
- <kbd>Alt</kbd> + <kbd>V</kbd> will clean the clipboard selection and paste the processed text into the current field

### CONFIGURATION

The add-on's HTML processing is highly configurable. All options can be accessed by editing the configuration section of `html_cleaner/main.py`.

## PLATFORM SUPPORT

*htmllaundry availability*

HTML processing is provided by the Bleach library on all platforms. The add-on can also be configured to use the [`htmllaundry` library](https://github.com/wichert/htmllaundry) which can improve the cleaning results under under some circumstances.

`htmllaundry` depends on `lxml` which Anki unfortunately does not ship with. In contrast to the other libraries included in this add-on, `lxml` cannot be easily be packaged for all platforms because it needs to be compiled. For that reason `htmllaundry` support is only available on Windows and Linux right now (2020-05).

*Issues with symlinks on Linux*

Because HTML cleaner comes with precompiled libraries on Linux, invoking the add-on from a symlinked Windows partition (e.g. NTFS) might lead to a permission error. The reason for this is that the executable bit is sometimes turned off by default for Windows partitions. If you run into this problem you can either look into adjusting your partition mounting settings or moving the add-ons directory to one of your Linux drives.

<!-- CHANGELOG -->

<!-- SUPPORT -->

### CREDITS AND LICENSE

*Copyright © 2016-2020 [Aristotelis P.](https://glutanimate.com/)  (Glutanimate)*

This add-on was commissioned by a fellow Anki user who would like to remain anonymous. All credit for the original idea goes to them.

Licensed under the _GNU AGPLv3_, extended by a number of additional terms. This program is distributed in the hope that it will be useful, but WITHOUT ANY WARRANTY. For more information on the license please see the [LICENSE file](https://github.com/glutanimate/html-cleaner/blob/master/LICENSE) accompanying this add-on. The source code is available on [![GitHub icon](https://glutanimate.com/logos/github.svg) GitHub](https://github.com/glutanimate/html-cleaner). Pull requests and other contributions are welcome!

<!-- RESOURCES -->

<!-- FUNDING -->
