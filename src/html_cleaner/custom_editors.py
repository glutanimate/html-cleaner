from aqt import AnkiQt
from aqt.editor import Editor


class ShortcutLessNonEditableEditor(Editor):
    def setNote(self, note, hide=True, focusTo=None):
        super().setNote(note, hide, focusTo)
        self.web.eval("makeNonContentEditable()")

    def setupShortcuts(self):
        return

    def checkValid(self):
        # no red background for duplicates
        return


class DupeIgnoringEditor(Editor):
    def checkValid(self):
        # no red background for duplicates
        return
