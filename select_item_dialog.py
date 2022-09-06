from PySide6 import QtWidgets, QtCore
from PySide6.QtWidgets import QDialogButtonBox


class SelectItemDialog(QtWidgets.QDialog):
    def __init__(self, item_dict: dict, title_message="Please select an option...", parent=None):
        super(SelectItemDialog, self).__init__(parent)

        self.option_items = item_dict
        self.setWindowTitle(title_message)

        self.layout = QtWidgets.QVBoxLayout()
        self.listWidget = QtWidgets.QListWidget()
        self.listWidget.setSelectionMode(
            QtWidgets.QAbstractItemView.ExtendedSelection
        )
        self.listWidget.setGeometry(QtCore.QRect(10, 10, 211, 291))
        for option in item_dict:
            item = QtWidgets.QListWidgetItem(str(option))
            self.listWidget.addItem(item)
        self.layout.addWidget(self.listWidget)

        self.buttonBox = QDialogButtonBox(QDialogButtonBox.Ok)
        self.buttonBox.accepted.connect(self.close)
        self.layout.addWidget(self.buttonBox)

        self.setLayout(self.layout)

    def get_selected_items(self):
        items = self.listWidget.selectedItems()
        selection_dict = {}
        for item in items:
            selection_dict[item.text()] = self.option_items[item.text()]
        return selection_dict
