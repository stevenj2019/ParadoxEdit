import os
import shutil
from pathlib import Path

from ParadoxParser import ParadoxScriptParser as PDXFile
from ParadoxParser.ParadoxNodes import GenericBlock, GenericComment

from PyQt5.QtWidgets import (QDialog, QFormLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem, 
                             QPushButton, QLabel, QLineEdit, QCheckBox, QComboBox)

# from App.Contexts.GFX import GFXDirectoryContext
from App.Contracts import BlockMutationRequest
from App.PDXFactory.Blocks.Sprites import GFX_icon, GFX_shine_icon
from App.GUI.Widgets.FileDialogues import (gfx_files_folder_selector, gfx_files_file_selector, 
                                           gfx_save_folder_selector)
from App.GUI.Widgets.PopupModels import GFX_file_copying_warn, form_missing_value

CATEGORY = "GFXDirectoryContext"
class AddNewGFXForm(QDialog):
    def __init__(self, app_controller, file):
        super().__init__()
        self.app_controller = app_controller
        self.mod = app_controller.registry.mod
        self.category = app_controller.registry.get_category(CATEGORY)
        self.file_list:list = []
        self.save_location:Path = None
        self.save_file:PDXFile = file

        self.setWindowTitle("Add New GFX to file")
        self.resize(550, 250)
        self.setLayout(QFormLayout())
        self.form = self.layout()

        self.file_list_item = QTreeWidget()
        self.file_list_item.setColumnCount(1)
        self.file_list_item.setHeaderLabel("Folder(s)")
        self.form.addRow(self.file_list_item)
        
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
        self.form.addRow(self.buttons)

        self.save_to_file_label = QLabel("GFX Definition:")
        self.file_dropdown = QComboBox()
        # for index, _file in enumerate(self.category.files.values()):
        for index, file in enumerate(self.category.files.values()):
            self.file_dropdown.addItem(file.filename)
            if file is self.save_file:
                self.file_dropdown.setCurrentIndex(index)
        self.save_to_file_label.setBuddy(self.file_dropdown)
        self.file_dropdown.currentIndexChanged.connect(self._change_save_file)
        self.form.addRow(self.save_to_file_label, self.file_dropdown)

        self.storage_folder_path_label = QLabel("GFX Location:")
        self.storage_folder_path_element = QHBoxLayout()
        self.storage_folder_path_element_text = QLineEdit()
        self.storage_folder_path_element_button = QPushButton("...")
        self.storage_folder_path_element.addWidget(self.storage_folder_path_element_text)
        self.storage_folder_path_element.addWidget(self.storage_folder_path_element_button)
        self.storage_folder_path_element_button.clicked.connect(self._select_save_folder)
        self.form.addRow(self.storage_folder_path_label, self.storage_folder_path_element)

        self.is_focus_type_label = QLabel("Focus Icon?")
        self.is_focus_type_check = QCheckBox()
        self.is_focus_type_label.setBuddy(self.is_focus_type_check)
        self.form.addRow(self.is_focus_type_label, self.is_focus_type_check)

        self.submit_button = QPushButton("Continue")
        self.form.addRow(self.submit_button)
        self.submit_button.clicked.connect(self._submit)
        self.exec_()

    def _add_folder_to_input_list(self):
        path, _ = gfx_files_folder_selector(self)
        self.file_list.append(path)
        item = QTreeWidgetItem([path])
        self.file_list_item.invisibleRootItem().addChild(item)

    def _add_file_to_input_list(self):
        path, _ = gfx_files_file_selector(self)
        if path:
            self.file_list.append(path)
            item = QTreeWidgetItem([path])
        self.file_list_item.invisibleRootItem().addChild(item)
    
    def _remove_selected_from_input_list(self):
        item = self.file_list_item.currentItem()
        if item is None:
            return
        index = self.file_list_item.indexOfTopLevelItem(item)
        if index == -1:
            return
        self.file_list.pop(index)
        self.file_list_item.takeTopLevelItem(index)

    def _change_save_file(self, index):
        file = self.file_dropdown.itemText(index)
        self.save_file = self.category.files[file]

    def _select_save_folder(self):
        path, _ = gfx_save_folder_selector(self, str(self.mod.file_path / "gfx"))
        if path:
            self.storage_folder_path_element_text.setText(path)
        return 
    
    def _submit(self):
        sprites = []
        def image_collection_loop(sprites, path):
            path = Path(path)
            if path.is_dir():
                for root, dirs, files in os.walk(path):
                    for name in dirs:
                        image_collection_loop(sprites, os.path.join(root, name))
                    for name in files:
                        if name.endswith("dds") or name.endswith("png"):
                            sprites.append(Path(os.path.join(root, name)))
            else:
                if path.suffix in (".dds", ".png"):
                    sprites.append(Path(path))
            return sprites
        
        def copy_file_to_new_directory(save_to, sprites):
            sprite_paths = list()
            for sprite in sprites:
                new_name = sprite.name if sprite.name.startswith("GFX_") else f"GFX_{sprite.name}"
                new_sprite = Path(os.path.join(save_to, new_name))

                shutil.copyfile(sprite, new_sprite)
                sprite_paths.append(new_sprite)
            return sprite_paths
        
        def generate_blocks(get_shines, sprite, file_path):
            sprite_name = sprite.stem
            sprite_path = sprite.relative_to(file_path)
            if get_shines:
                return [GenericComment(f"Focus Icon for: {sprite.stem}"),
                                        GFX_icon(sprite_name, sprite_path), 
                                        GFX_shine_icon(sprite_name, sprite_path)]
            else:
                return [GFX_icon(sprite_name, sprite_path)]

        try:
            sprite_block = next(node for node in self.save_file.nodes
                                if (isinstance(node, GenericBlock) 
                                    and node.key.lower() == "spritetypes"))
        except StopIteration:
            #warning
            return
        if GFX_file_copying_warn(self):
            if not self.storage_folder_path_element_text.text().strip() or not self.file_list:
                form_missing_value(self)
                return
            for path in self.file_list:
                image_collection_loop(sprites, path)
            sprites = copy_file_to_new_directory(self.storage_folder_path_element_text.text(), sprites)
            base_dir = self.app_controller.registry.mod.file_path
            generate_shines = self.is_focus_type_check.isChecked()

            with self.app_controller.batch_manager():
                for sprite in sprites:
                    blocks = generate_blocks(generate_shines, sprite, base_dir)
                    for block in blocks:
                        self.app_controller.request_block_mutation.emit(
                            BlockMutationRequest.add(sprite_block, len(sprite_block.nodes)+1, block, self.save_file)
                        )
            self.accept()