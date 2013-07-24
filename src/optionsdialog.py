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

        self.connect(self._optionsList.selectionModel(), 
                     QtCore.SIGNAL("currentChanged(const QModelIndex&, const QModelIndex&)"),
                     self._updateAddButton)

        # TODO: wire escape to close dialog

        # and accept/cancel buttons
        #
        footer = QtGui.QWidget()
        footer.setLayout(QtGui.QHBoxLayout())
        layout.addWidget(footer)
        footer.layout().addStretch()
        self._addOptionButton = QtGui.QPushButton('Add Option')
        self._addOptionButton.setEnabled(False)
        self.connect(self._addOptionButton, QtCore.SIGNAL("released()"), self.accept)
        footer.layout().addWidget(self._addOptionButton)

    def _updateAddButton(self, current, previous):
        # if valid selection
        self._addOptionButton.setEnabled(True)

    def option(self):
        indexes = self._optionsList.selectionModel().selectedIndexes()
        return str(self._optionsList.model().data(indexes[0]).toString())

# TODO: wire text change to filter list
# TODO: wire list selection to change button
        
