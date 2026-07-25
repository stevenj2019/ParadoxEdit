from PyQt5.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem, QPushButton

from App.GUI.Widgets.FileDialogues import gfx_files_folder_selector, gfx_files_file_selector

class FileFolderSelectorWidget(QWidget):
    def __init__(self):
        super().__init__()
        self._file_list = list()

        self.layout = QVBoxLayout(self)
        self.setLayout(self.layout)
        
        self.file_list_item = QTreeWidget()
        self.file_list_item.setColumnCount(1)
        self.file_list_item.setHeaderLabel("Folder(s)")
        self.layout.addWidget(self.file_list_item)

        self.buttons = QHBoxLayout()
        self.add_folder_button = QPushButton("Add Folder", self)
        self.add_folder_button.clicked.connect(self._add_folder_to_input_list)
        self.buttons.addWidget(self.add_folder_button)
        self.add_file_button = QPushButton("Add File", self)
        self.add_file_button.clicked.connect(self._add_file_to_input_list)
        self.buttons.addWidget(self.add_file_button)
        self.remove_entry_button = QPushButton("Delete Selected", self)
        self.remove_entry_button.clicked.connect(self._remove_selected_from_input_list)
        self.buttons.addWidget(self.remove_entry_button)
        self.layout.addLayout(self.buttons)

    @property
    def file_list(self):
        return self._file_list

    def _add_folder_to_input_list(self):
        path, _ = gfx_files_folder_selector(self)
        self._file_list.append(path)
        item = QTreeWidgetItem([path])
        self.file_list_item.invisibleRootItem().addChild(item)

    def _add_file_to_input_list(self):
        path, _ = gfx_files_file_selector(self)
        if path:
            self._file_list.append(path)
            item = QTreeWidgetItem([path])
            self.file_list_item.invisibleRootItem().addChild(item)
    
    def _remove_selected_from_input_list(self):
        item = self.file_list_item.currentItem()
        if item is None:
            return
        index = self.file_list_item.indexOfTopLevelItem(item)
        if index == -1:
            return
        self._file_list.pop(index)
        self.file_list_item.takeTopLevelItem(index)