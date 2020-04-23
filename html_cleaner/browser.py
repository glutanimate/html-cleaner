from aqt import gui_hooks
from aqt.browser import Browser
from aqt.utils import tooltip
from aqt.qt import QLabel, QDialog, QHBoxLayout, QDialogButtonBox, QComboBox, QVBoxLayout, QKeySequence, QShortcut, Qt
from .clean import cleanHtml
from .config import getUserOption

class BatchCleanDialog(QDialog):
    """Browser batch editing dialog"""

    def __init__(self, browser, nids):
        QDialog.__init__(self, parent=browser)
        self.browser = browser
        self.nids = nids
        self._setupUi()

    def _setupUi(self):
        flabel = QLabel("In this field:")
        self.fsel = QComboBox()
        fields = self._getFields()
        self.fsel.addItems(fields)
        f_hbox = QHBoxLayout()
        f_hbox.addWidget(flabel)
        f_hbox.addWidget(self.fsel)
        f_hbox.setAlignment(Qt.AlignLeft)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok|QDialogButtonBox.Cancel, orientation=Qt.Horizontal, parent=self)


        bottom_hbox = QHBoxLayout()
        bottom_hbox.addWidget(button_box)

        vbox_main = QVBoxLayout()
        vbox_main.addLayout(f_hbox)
        vbox_main.addLayout(bottom_hbox)
        self.setLayout(vbox_main)
        self.setWindowTitle("Batch Clean Selected Notes")
        button_box.rejected.connect(self.reject)
        button_box.accepted.connect(self.accept)
        self.rejected.connect(self.reject)
        self.accepted.connect(self.accept)
        self.fsel.setFocus()

    def _getFields(self):
        nid = self.nids[0]
        mw = self.browser.mw
        model = mw.col.getNote(nid).model()
        fields = mw.col.models.fieldNames(model)
        return fields

    def reject(self):
        self.close()

    def accept(self):
        self.browser.mw.checkpoint("batch edit")
        self.browser.mw.progress.start()
        self.browser.model.beginReset()
        fld_name = self.fsel.currentText()
        cnt = 0
        for nid in self.nids:
            note = self.browser.mw.col.getNote(nid)
            cleaned = cleanHtml(note[fld_name])
            if cleaned != note[fld_name]:
                cnt += 1
                note[fld_name] = cleaned
                note.flush()
        self.browser.model.endReset()
        self.browser.mw.requireReset()
        self.browser.mw.progress.finish()
        self.browser.mw.reset()
        self.close()
        tooltip(f"{cnt} notes cleaned")

    def closeEvent(self, evt):
        evt.accept()


def onBatchClean(browser):
    nids = browser.selectedNotes()
    if not nids:
        tooltip("No cards selected.")
        return
    dialog = BatchCleanDialog(browser, nids)
    dialog.exec_()

def add_menu(browser):
    menu = browser.form.menuEdit
    menu.addSeparator()
    a = menu.addAction('Batch clean HTML...')
    a.setShortcut(QKeySequence(getUserOption("html_batch_clean_hotkey")))
    a.triggered.connect(lambda _, b=browser: onBatchClean(b))


gui_hooks.browser_menus_did_init.append(add_menu)
