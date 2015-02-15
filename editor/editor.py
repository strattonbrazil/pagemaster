import os
from PyQt4 import QtGui, QtCore, QtWebKit, uic

from optionsdialog import OptionsDialog

class WorkspaceEditor(QtGui.QWidget):
    NO_IMAGE_TEXT = '(click to assign an image)'
    def __init__(self, workspace):
        super(WorkspaceEditor, self).__init__(workspace)

        self._workspace = workspace

        scriptPath = os.path.dirname(os.path.realpath(__file__))
        uic.loadUi(scriptPath + '/editor.ui', self)

        self.connect(self.titleButton, QtCore.SIGNAL("released()"), self.updateTitle)
        self.connect(self.imageButton, QtCore.SIGNAL("released()"), self.updateImage)
        self.connect(self.addOptionButton, QtCore.SIGNAL("released()"), self.addOption)
        self.connect(self.contentArea, QtCore.SIGNAL("textChanged()"), self.updateContent)

    def setPage(self, page):
        self._currentPage = page

        if page is None:
            self.stack.setCurrentWidget(self.labelWidget)
            return

        self.titleButton.setText('Title: ' + page.title)
        self.contentArea.setText(page.content)

        self.addOptionButton.setEnabled(len(self._eligibleOptions()) > 0)

        self._updateOptionsBox()

    def _updateOptionsBox(self):
        # clear previous items
        layout = self.optionsBox.layout()
        while layout.count() > 0:
            item = layout.takeAt(0)
            item.widget().deleteLater()

        for option in self._currentPage.options:
            optionButton = QtGui.QPushButton(option['text'], self)
            def foo():
                print('nope')
            self.connect(optionButton, QtCore.SIGNAL("released()"), foo)
            self.optionsBox.layout().addWidget(optionButton)

        self.stack.setCurrentWidget(self.pageEditWidget)

    def updateTitle(self):
        title = self._currentPage.title

        dialog = QtGui.QInputDialog()
        dialog.setWindowTitle('Update Title')
        dialog.setTextValue(title)
        if not dialog.exec_(): # TODO: check against enum
            return

        updateTitle = str(dialog.textValue())

        if updateTitle == '':
            return

        self.titleButton.setText('Title: ' + updateTitle)

        self._currentPage.title = updateTitle
        
        self._workspace.update()

    def updateImage(self):
        imagePath = QtGui.QFileDialog.getOpenFileName(self)
        if imagePath:
            self._currentPage.imagePath = imagePath

        self._workspace.update()

    def updateContent(self):
        self._currentPage.content = str(self.contentArea.toPlainText())

    def addOption(self, dstPage=None):
        # add option to the provide page
        if dstPage:
            optionText, success = QtGui.QInputDialog.getText(self, 'Option Text', 'Enter the option text to the next page')
            if success:
                self._currentPage.options.append(
                    { 'text' : str(optionText),
                      'id' : dstPage.id })
        else:
            options = {}
            for option in self._eligibleOptions():
                options[option] = {}

            dialog = OptionsDialog(self, options)
            if dialog.exec_(): # TODO: check against enum
                optionTitle = dialog.option()
                workspace = self._workspace

                self._currentPage.options.append(
                    { 'text' : 'text to go to',
                      'id' : optionTitle })
        
        self._updateOptionsBox()

    def _eligibleOptions(self): # return list of eligible pages
        options = []

        currentOptions = self._currentPage.options
        for page in self._workspace.story.getPages():
            if page.id != self._currentPage.id:
                for text, pageId in currentOptions:
                    if page.id == pageId:
                        break
                else:
                    options.append(page.id)

        return options
