from PyQt4 import QtGui, QtCore, QtWebKit

from optionsdialog import OptionsDialog

class WorkspaceEditor(QtGui.QWidget):
    NO_IMAGE_TEXT = '(click to assign an image)'
    def __init__(self, workspace):
        super(WorkspaceEditor, self).__init__(workspace)

        self._workspace = workspace

        self.setLayout(QtGui.QVBoxLayout())
        self._stack = QtGui.QStackedWidget()
        self.layout().addWidget(self._stack)

        self._labelWidget = QtGui.QLabel("Select a page to edit...")
        self._stack.addWidget(self._labelWidget)

        self._pageEditWidget = QtGui.QWidget()
        self._stack.addWidget(self._pageEditWidget)
        pageEditLayout = QtGui.QVBoxLayout()
        self._pageEditWidget.setLayout(pageEditLayout)
#        self.setLayout(layout)

        self._titleButton = QtGui.QPushButton()
        self._imageButton = QtGui.QPushButton(WorkspaceEditor.NO_IMAGE_TEXT)
        self._textArea = QtGui.QTextEdit()
        self._optionsBox = QtGui.QWidget()
        self._addOptionButton = QtGui.QPushButton('Add Option')

        self.connect(self._titleButton, QtCore.SIGNAL("released()"), self.updateTitle)
        self.connect(self._imageButton, QtCore.SIGNAL("released()"), self.updateImage)
        self.connect(self._addOptionButton, QtCore.SIGNAL("released()"), self.addOption)
        self.connect(self._textArea, QtCore.SIGNAL("textChanged()"), self.updateContent)

        pageEditLayout.addWidget(self._titleButton)
        pageEditLayout.addWidget(self._imageButton)

        pageEditLayout.addWidget(QtGui.QLabel('Text'))
        pageEditLayout.addWidget(self._textArea)

        pageEditLayout.addWidget(QtGui.QLabel('Options'))
        pageEditLayout.addWidget(self._optionsBox)

        pageEditLayout.addWidget(self._addOptionButton)

    def updatePage(self, title):
        if title is None:
            self._stack.setCurrentWidget(self._labelWidget)
            return

        content = self._workspace.story['pages'][title]['content']

        self._titleButton.setText('Title: ' + title)
        self._textArea.setText(content)

        self._addOptionButton.setEnabled(len(self._eligibleOptions()) > 0)

        self._stack.setCurrentWidget(self._pageEditWidget)

    def _parseTitle(self):
        return str(self._titleButton.text().replace('Title: ', ''))

    def updateTitle(self):
        title = self._parseTitle()

        dialog = QtGui.QInputDialog()
        dialog.setWindowTitle('Update Title')
        dialog.setTextValue(title)
        if not dialog.exec_(): # TODO: check against enum
            return

        updateTitle = str(dialog.textValue())

        if updateTitle == '':
            return

        for title in self._workspace.story['pages']:
            if updateTitle == title:
                print('page with that name already exists')
                return

        pageInfo = self._workspace.story['pages'].pop(title)
        self._workspace.story['pages'][updateTitle] = pageInfo
        
        self._workspace.update()

    def updateImage(self):
        print('update image')

    def updateContent(self):
        title = self._parseTitle()
        self._workspace.story['pages'][title]['content'] = self._textArea.toPlainText()

    def addOption(self):
        options = {}
        for option in self._eligibleOptions():
            options[option] = {}

        dialog = OptionsDialog(self, options)
        if not dialog.exec_(): # TODO: check against enum
            return
        

    def _eligibleOptions(self): # return list of eligible pages
        title = self._parseTitle()

        options = []

        for otherTitle in self._workspace.story['pages']:
            if otherTitle != title:
                # TODO: should not add if already linked as option
                options.append(otherTitle)

        return options
