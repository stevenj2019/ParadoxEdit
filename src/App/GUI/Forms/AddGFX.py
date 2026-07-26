import os
from pathlib import Path

from ParadoxParser import ParadoxScriptParser as PDXFile
from ParadoxParser.ParadoxNodes import GenericBlock, GenericComment

from PyQt5.QtWidgets import (QDialog, QFormLayout, QHBoxLayout, QTreeWidget, QTreeWidgetItem, 
                             QPushButton, QLabel, QLineEdit, QCheckBox, QComboBox)

from App.Loading.Models import FileReference, IconFile
from App.Contexts.Base import ParadoxContext
from App.Contracts import BlockMutationRequest, FileMutationRequest
from App.Contracts.Enums import ChangeState
from App.PDXFactory.Blocks.Sprites import GFX_icon, GFX_shine_icon
from App.GUI.Widgets.FileDialogues import gfx_save_folder_selector
from App.GUI.Widgets.PopupModels import form_missing_value
from App.GUI.Widgets.CustomWidgets import FileFolderSelectorWidget

class AddNewGFXForm(QDialog):
    def __init__(self, app_controller, file):
        super().__init__()
        self.app_controller = app_controller
        self.source = file.directory.source
        self.interface_directory = self.source.directories[Path("interface")]
        self.file_list:list = []
        self.save_location:Path = None
        self.save_file:PDXFile = file

        self.setWindowTitle("Add New GFX to file")
        self.resize(550, 250)
        self.setLayout(QFormLayout())
        self.form = self.layout()

        self.file_selector = FileFolderSelectorWidget()
        self.form.addRow(self.file_selector)

        self.save_to_file_label = QLabel("GFX Definition:")
        self.file_dropdown = QComboBox()
        for file in self.interface_directory.iter_files():
            self.file_dropdown.addItem(
                file.file.filename,
                userData=file
            )
            if file is self.save_file:
                self.file_dropdown.setCurrentIndex(
                    self.file_dropdown.count()-1
                )
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

    def _change_save_file(self, index):
        self.save_file = self.file_dropdown.itemData(index)

    def _select_save_folder(self):
        path, exists = gfx_save_folder_selector(self, str(self.source.file_path / "gfx"))
        if exists:
            self.storage_folder_path_element_text.setText(path)
    
    def _submit(self):
        self.file_list = self.file_selector.file_list
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
        
        def generate_icon_files(save_to, sprites):
            icons = list()
            for sprite in sprites:
                new_name = sprite.name if sprite.name.startswith("GFX_") else f"GFX_{sprite.name}"
                new_path = Path(os.path.join(save_to, new_name))
                directory = new_path.relative_to(self.source.file_path).parent
                directory = self.source.directories[directory]

                new_file = FileReference(
                    directory, 
                    IconFile.add(new_path, sprite), 
                    ParadoxContext, 
                    False
                )
                icons.append(new_file)
            return icons

        def generate_blocks(get_shines, sprite, file_path):
            icon_file = sprite.file
            sprite_name = icon_file.filepath.stem
            sprite_path = icon_file.filepath.relative_to(file_path)
            if get_shines:
                return [GenericComment(f"Focus Icon for: {icon_file.filepath.stem}"),
                                        GFX_icon(sprite_name, sprite_path), 
                                        GFX_shine_icon(sprite_name, sprite_path)]
            else:
                return [GFX_icon(sprite_name, sprite_path)]

        try:
            sprite_block = next(node for node in self.save_file.file.nodes
                                if (isinstance(node, GenericBlock) 
                                    and node.key.lower() == "spritetypes"))
        except StopIteration:
            #warning
            return
    
        if not self.storage_folder_path_element_text.text().strip() or not self.file_list:
            form_missing_value(self)
            return
        for path in self.file_list:
            image_collection_loop(sprites, path)
        icons = generate_icon_files(self.storage_folder_path_element_text.text(), sprites)
        base_dir = self.source.file_path
        generate_shines = self.is_focus_type_check.isChecked()


        with self.app_controller.batch_manager():
            for icon in icons:
                blocks = generate_blocks(generate_shines, icon, base_dir)
                for block in blocks:
                    self.app_controller.request_block_mutation.emit(
                        BlockMutationRequest.add(sprite_block, len(sprite_block.nodes)+1, block, self.save_file)
                    )
                self.app_controller.request_file_change.emit(
                    FileMutationRequest(
                        icon.directory, icon, ChangeState.ADDED
                    )
                )
        self.accept()