from PyQt4 import QtGui, QtCore, QtWebKit

class OptionsDialog(QtGui.QDialog):
    def __init__(self, parent, options):
        super(OptionsDialog, self).__init__(parent)

        self.setWindowTitle('Add Option')

        layout = QtGui.QVBoxLayout()
        self.setLayout(layout)

        self._searchInput = QtGui.QLineEdit()
        layout.addWidget(self._searchInput)

        self._optionsList = QtGui.QListView()
        layout.addWidget(self._optionsList)
        model = QtGui.QStandardItemModel()
        self._optionsList.setModel(model)

        for option in options:
            item = QtGui.QStandardItem(option)
            model.appendRow(item)

        # TODO: wire escape to close dialog

        # and accept/cancel buttons
        #
        footer = QtGui.QWidget()
        footer.setLayout(QtGui.QHBoxLayout())
        layout.addWidget(footer)
        footer.layout().addStretch()
        self._addOptionButton = QtGui.QPushButton('Add Option')
        self._addOptionButton.setEnabled(False)
        self.connect(self._addOptionsButton, QtCore.SIGNAL("released()"), self._accepted)
        footer.layout().addWidget(self._addOptionButton)

    def _addOptionAccepted(self):
        print('add valid option')

# TODO: wire text change to filter list
# TODO: wire list selection to change button
        
