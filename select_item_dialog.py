from PySide6 import QtWidgets, QtCore


class SelectItemDialog(QtWidgets.QDialog):
    def __init__(self, item_dict: dict, parent=None):
        super(SelectItemDialog, self).__init__(parent)

        self.option_items = item_dict

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
        self.setLayout(self.layout)

    def get_selected_items(self):
        items = self.listWidget.selectedItems()
        selection_dict = {}
        for item in items:
            selection_dict[item.text()] = self.option_items[item.text()]
        return selection_dict