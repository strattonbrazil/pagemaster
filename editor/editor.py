import os
from PyQt4 import QtGui, QtCore, QtWebKit, uic
from functools import partial

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
        self.connect(self.removeImageButton, QtCore.SIGNAL("released()"), self.removeImage)
        self.connect(self.addOptionButton, QtCore.SIGNAL("released()"), self.addOption)
        self.connect(self.contentArea, QtCore.SIGNAL("textChanged()"), self.updateContent)

    def setPage(self, page):
        self._currentPage = page

        if page is None:
            self.stack.setCurrentWidget(self.labelWidget)
            return

        self._mapCurrentPage()
        
        #self.contentArea.setText(page.content)
        #self.setImage(page.imagePath)

        #self.addOptionButton.setEnabled(len(self._eligibleOptions()) > 0)

        #self._updateOptionsBox()

    def _mapCurrentPage(self):
        page = self._currentPage

        self.titleButton.setText('Title: ' + page.title())
        self.setImage(page.imagePath())

    def _updateOptionsBox(self):
        # clear previous items
        layout = self.optionsBox.layout()
        while layout.count() > 0:
            item = layout.takeAt(0)
            item.widget().deleteLater()

        for i,option in enumerate(self._currentPage.options):
            optionBlock = OptionBlock(self, option['text'])

            def updateCallback(optionBlock):
                dialog = QtGui.QInputDialog()
                dialog.setWindowTitle('Update Option Text')
                dialog.setTextValue(optionBlock.optionButton.text())
                if not dialog.exec_(): # TODO: check against enum
                    return

                self._currentPage.options[i]['text'] = unicode(dialog.textValue())
                optionBlock.optionButton.setText(dialog.textValue())

            def deleteCallback(i):
                del self._currentPage.options[i]
                self._updateOptionsBox()

            optionBlock.setUpdateCallback(partial(updateCallback, optionBlock))
            optionBlock.setDeleteCallback(partial(deleteCallback, i))

            self.optionsBox.layout().addWidget(optionBlock)

        self.stack.setCurrentWidget(self.pageEditWidget)

    def updateTitle(self):
        title = self._currentPage.title()

        dialog = QtGui.QInputDialog()
        dialog.setWindowTitle('Update Title')
        dialog.setTextValue(title)
        if not dialog.exec_(): # TODO: check against enum
            return

        updateTitle = str(dialog.textValue())

        if updateTitle == '':
            return

        #self.titleButton.setText('Title: ' + updateTitle)

        self._currentPage.setTitle(updateTitle)

        self._mapCurrentPage()

    def updateImage(self):
        settings = QtCore.QSettings()
        lastImageDir = settings.value('lastUploadImageDir').toString()

        imagePath = QtGui.QFileDialog.getOpenFileName(self, 'Select image file', lastImageDir, "Images (*.png *.jpg")
        if imagePath:
            self._currentPage.imagePath = str(imagePath)
            self.setImage(imagePath)

            settings.setValue('lastUploadImageDir', QtCore.QFileInfo(imagePath).canonicalPath())
        

    def removeImage(self):
        self._currentPage.imagePath = ''
        self.setImage(None)

    def setImage(self, imagePath):
        if imagePath:
            icon = QtGui.QIcon(imagePath)
            self.imageButton.setIcon(icon)
            self.imageButton.setIconSize(QtCore.QSize(256,256))

            self.imageButton.setText('')
            self.removeImageButton.show()
        else:
            self.imageButton.setIcon(QtGui.QIcon())
            self.imageButton.setText('Select Image')
            self.removeImageButton.hide()

    def updateContent(self):
        self._currentPage.content = unicode(self.contentArea.toPlainText())

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

class OptionBlock(QtGui.QWidget):
    def __init__(self, parent, text):
        super(OptionBlock, self).__init__(parent)

        scriptPath = os.path.dirname(os.path.realpath(__file__))
        uic.loadUi(scriptPath + '/option_block.ui', self)

        self.optionButton.setText(text)

    def setUpdateCallback(self, callback):
        self.connect(self.optionButton, QtCore.SIGNAL("released()"), callback)

    def setDeleteCallback(self, callback):
        self.connect(self.deleteButton, QtCore.SIGNAL("released()"), callback)
