import json
import os

from anki.lang import _
from anki.utils import (
    guid64,
    timestampID,
)

import aqt
from aqt import mw
from aqt.editor import Editor
from aqt.qt import (
    QDialog,
    Qt,
)
from aqt.utils import (
    askUser,
    getOnlyText,
    restoreGeom,
    saveGeom,
    shortcut,
    showInfo,
    tooltip,
)

from .clean import cleanHtml
from .config import getUserOption, user_files, wcs
from .editor import process_all_fields  # process_all_fields(self, func)
from .forms import config_widgets_editors
from .forms import settings_select_group


class ShortcutLessEditor(Editor):
    def setupShortcuts(self):
        return
    
    def checkValid(self):
        # no red background for duplicates
        return


class DupeIgnoringEditor(Editor):   
    def checkValid(self):
        # no red background for duplicates
        return


# from classes add-on
class SelectDialog(QDialog):
    def __init__(self, parent=None, alternatives=[]):
        self.parent = parent
        QDialog.__init__(self, parent, Qt.Window)
        self.dialog = settings_select_group.Ui_Dialog()
        self.dialog.setupUi(self)
        self.dialog.list_categories.addItems(alternatives)
        self.dialog.list_categories.itemDoubleClicked.connect(self.accept)

    def accept(self):
        self.sel = self.dialog.list_categories.currentItem().text()
        QDialog.accept(self)


class MyConfigWindow(QDialog):
    silentlyClose = True  # dialog manager

    def __init__(self, parent):
        QDialog.__init__(self, parent, Qt.Window)
        self.parent = parent
        mw.setupDialogGC(self)
        self.form = config_widgets_editors.Ui_Dialog()
        self.form.setupUi(self)
        self.setWindowTitle("Anki Add-on: Html Cleaner clean settings")
        self.resize(800, 1300)
        restoreGeom(self, "html_cleTRaner_conf_window")
        self.mw = mw
        
        self.editor_old = ShortcutLessEditor(self.mw, self.form.widget_original, self, True)
        self.clean_ed = DupeIgnoringEditor(self.mw, self.form.widget_cleaned, self, True)


        # bottom
        for f in getUserOption("nids_for_previewing_settings"):
            self.form.bot_cb_recent_notes.addItem(str(f))
        self.other_note_into_editor(firstrun=True)
        # initial run must before the next line or the editor_did_load_note hooks are run once more
        # so that I get another entry of Arthurs "clean" next a field name
        self.form.bot_cb_recent_notes.currentIndexChanged.connect(self.other_note_into_editor)    
        self.form.bot_pb_add_note.clicked.connect(self.add_note)
        self.form.bot_pb_remove.clicked.connect(self.remove_note)
        self.form.bot_pb_ok.clicked.connect(self.accept)
        self.form.bot_pb_cancel.clicked.connect(self.reject)

        # sidebar
        self.clean_settings = getUserOption("clean_settings")
        self.active_settings_group = getUserOption("clean_active_settings_group")
        self.current_config = self.clean_settings[self.active_settings_group]
        if self.active_settings_group not in self.clean_settings:
            showInfo(("Invalid config detected: the group set in 'clean_active_settings_group' "
                      'must be in "clean_settings". Update/Repair your config. Aborting'))
            self.reject()
        self.form.conf_pb_group.setText(self.active_settings_group)
        self.form.conf_pb_group.clicked.connect(self.on_config_group_change)
        self.populate_versions()
        self.form.conf_pb_backup.setVisible(False)
        self.form.conf_pb_backup.clicked.connect(self.backup_current_vals)
        self.form.conf_pb_save.clicked.connect(self.save_current_vals)

        self.set_conf_text()  # initial run must before the next line or the editor_did_load_note hooks are run once more
                              # so that I get another entry of Arthurs "clean" next a field name
        self.form.conf_pte_conf.textChanged.connect(self.update_clean_ed)
        self.show()

    def reopen(self, parent):  # dialog manager
        pass

    ##### sidebar

    def on_config_group_change(self):
        if not askUser(("Changing the active config group will discard all changes for the "
                        "currently active group. Proceed?")):
            return
        e = SelectDialog(self, list(self.clean_settings.keys()))
        if e.exec():
            self.active_settings_group = e.sel
            self.current_config = self.clean_settings[self.active_settings_group]       
            self.set_conf_text()
            self.other_note_into_editor()

    def set_conf_text(self):
        fmted = json.dumps(self.current_config, ensure_ascii=False, sort_keys=True, indent=4, separators=(",", ": "))
        self.form.conf_pte_conf.setPlainText(fmted)

    def conf_text_to_dict(self):
        txt = self.form.conf_pte_conf.toPlainText()
        # old/simple Anki add-on config validation code
        try:
            new_conf = json.loads(txt)
        except Exception as e:
            showInfo(_("Invalid configuration: ") + repr(e))
            return
        if not isinstance(new_conf, dict):
            showInfo(_("Invalid configuration: top level object must be a map"))
            return
        self.current_config = new_conf

    def populate_versions(self):
        self.form.conf_cb_old.setVisible(False)  # setParent(None)
        self.form.conf_ql_versions.setVisible(False) # setParent(None)
        return
        # TODO
        self.form.conf_cb_old.clear()
        folder = os.path.join(user_files, self.active_settings_group)
        files = sorted(os.listdir(folder), reverse=True)
        for f in files:
            self.form.conf_cb_old.addItem(f)

    def backup_current_vals(self):
        pass

    def save_current_vals(self):
        self.conf_text_to_dict()  #  updates self.current_config
        self.clean_settings[self.active_settings_group] = self.current_config
        wcs("clean_settings", self.clean_settings)

    ##### bottom  
        
    def add_note(self):
        newnid = getOnlyText("Enter Note Id (nid) of note to display here")
        if not newnid:
            return
        try:
            newnid = int(newnid)
        except:
            tooltip("a note id must consist of 13 digits only. Aborting ...")
            return
        else:
            if not mw.col.db.scalar(f"select * from notes where id={newnid}"):
                tooltip(f"No note with the id {newnid} exists. Aborting ...")
                return
        cbr = self.form.bot_cb_recent_notes
        cbr.addItem(str(newnid))
        cbr.setCurrentIndex(cbr.count()-1)

    def remove_note(self):
        cbr = self.form.bot_cb_recent_notes
        idx = cbr.currentIndex()
        cbr.removeItem(idx)
        if not cbr.count():  # not needed because index changes when there are notes
            self.other_note_into_editor()  

    def other_note_into_editor(self, firstrun=False):
        if not self.form.bot_cb_recent_notes.count():
            if firstrun:
                pass  # it will be set because of the text change
            else: # clean
                self.editor_old.setNote(None)
                self.clean_ed.setNote(None)
                self.current_note = None
            return
        nid = int(self.form.bot_cb_recent_notes.currentText())
        self.current_note = mw.col.getNote(nid)
        # to make sure that no accidental edits are saved make a new temporary note ?? side-effects?
        self.current_note.id = timestampID(mw.col.db, "notes")
        self.current_note.guid = guid64()
        self.editor_old.setNote(self.current_note, focusTo=0)
        self.clean_ed.setNote(self.current_note, focusTo=0)

    def update_clean_ed(self):
        if not self.current_note:
            print('returning form udpate_clean_ed')
            return
        self.conf_text_to_dict()
        missing = []
        tags = self.current_config.get("keep_tags")
        if tags is None:
            missing.append("keep_tags")
        attributes = self.current_config.get("keep_attrs")
        if attributes is None:
            missing.append("keep_attrs")
        styles = self.current_config.get("keep_styles")
        if styles is None:
            missing.append("keep_styles")
        if missing:
            showInfo(( "Something in the config from the sidebar is wrong: The following keys are"
                      f'missing: {", ".join(missing)}.'))
            return
        use_html_laundry = False
        # TODO maybe get contents from old editor?
        for n in range(len(self.current_note.fields)):
            self.clean_ed.note.fields[n] = cleanHtml(self.current_note.fields[n], tags, attributes, styles, use_html_laundry)
        self.clean_ed.loadNote()

    def reject(self):
        saveGeom(self, "html_cleaner_conf_window")
        aqt.dialogs.markClosed("html_cleaner_config")
        QDialog.reject(self)

    def accept(self):
        self.conf_text_to_dict()  #  updates self.current_config
        self.clean_settings[self.active_settings_group] = self.current_config
        wcs("clean_settings", self.clean_settings)
        
        cbr = self.form.bot_cb_recent_notes
        AllItems = [int(cbr.itemText(i)) for i in range(cbr.count())]
        wcs("nids_for_previewing_settings", AllItems)
        
        saveGeom(self, "html_cleaner_conf_window")
        aqt.dialogs.markClosed("html_cleaner_config")
        QDialog.accept(self)
