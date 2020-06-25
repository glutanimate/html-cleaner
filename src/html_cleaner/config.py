import os
import sys

from aqt import mw
from aqt.utils import showWarning


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
