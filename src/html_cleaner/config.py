# -*- coding: utf-8 -*-

# HTML Cleaner Add-on for Anki
#
# Copyright (C) 2016-2020  Aristotelis P. <https://glutanimate.com/>
# Copyright (C) 2020  Arthur Milchior <arthur@milchior.fr>
# Copyright (C) 2020  ijgnd <https://github.com/ijgnd>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version, with the additions
# listed at the end of the license file that accompanied this program.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
#
# NOTE: This program is subject to certain additional terms pursuant to
# Section 7 of the GNU Affero General Public License.  You should have
# received a copy of these additional terms immediately following the
# terms and conditions of the GNU Affero General Public License that
# accompanied this program.
#
# If not, please request a copy through one of the means of contact
# listed here: <https://glutanimate.com/contact/>.
#
# Any modifications to this file must keep this entire header intact.


import os

from aqt import mw

addon_path = os.path.dirname(__file__)
user_files = os.path.join(addon_path, "user_files")

userOption = None
foldername = mw.addonManager.addonFromModule(__name__)
default = mw.addonManager.addonConfigDefaults(foldername)


def _getUserOption():
    global userOption
    # workaround: for occasional error "'NoneType' object is not subscriptable" in  current[key] = current_default[key]
    global default
    if default is None:
        default = mw.addonManager.addonConfigDefaults(foldername)
    if userOption is None:
        userOption = mw.addonManager.getConfig(__name__)


def getUserOption(keys=None):
    """Get the user option if it is set. Otherwise return the default
    value and add it to the config.

    When an add-on was updated, new config keys were not added. This
    was a problem because user never discover those configs. By adding
    it to the config file, users will see the option and can configure it.

    If keys is a list of string [key1, key2, ... keyn], it means that
    config[key1], ..., config[key1]..[key n-1] are dicts and we want
    to get config[key1]..[keyn]

    """
    _getUserOption()
    if keys is None:
        return userOption
    if isinstance(keys, str):
        keys = [keys]

    # Path in the list of dict
    current = userOption
    current_default = default
    change = False
    for key in keys:
        assert isinstance(current, dict)
        if key not in current:
            current[key] = current_default[key]
            # Raise KeyError if key is not in this sub dictionnary of the default config.
            # Raise TypeError: object is not subscriptable if it's not a dictionnary
            change = True
        if isinstance(current_default, dict) and key in current_default:
            current_default = current_default[key]
        else:
            current_default = None
        current = current[key]

    if change:
        writeConfig()
    return current


def writeConfig():
    mw.addonManager.writeConfig(__name__, userOption)


def update(_):
    global userOption, fromName
    userOption = None
    fromName = None


mw.addonManager.setConfigUpdatedAction(__name__, update)

fromName = None


def getFromName(name):
    global fromName
    if fromName is None:
        fromName = dict()
        for dic in getUserOption("columns"):
            fromName[dic["name"]] = dic
    return fromName.get(name)


def setUserOption(key, value):
    _getUserOption()
    userOption[key] = value
    writeConfig()


def wcs(key, newvalue, addnew=False):
    config = mw.addonManager.getConfig(__name__)
    if not (key in config or addnew):
        return False
    else:
        config[key] = newvalue
        mw.addonManager.writeConfig(__name__, config)
        update(None)
        return True
