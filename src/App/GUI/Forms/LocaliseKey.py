from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import AppController

from pathlib import Path

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QShowEvent
from PyQt5.QtWidgets import (
    QComboBox,
    QDialog,
    QFormLayout,
    QLabel,
    QPushButton,
    QTextEdit,
)

from App.Contracts import BlockMutationRequest, NodeMutationRequest
from App.Contracts.Enums import TargetProperty
from App.Enums import PDXMetadata
from App.GUI.Widgets.PopupModels import form_is_read_only, split_loc_file
from ParadoxParser.ParadoxNodes import (
    GenericBlock,
    GenericComment,
    GenericKeyValue,
    GenericLegacyLocKey,
    GenericLocKey,
    GenericNode,
)
from ParadoxParser.queries import find_keyvalue

UNSORTED_COMMENT = "#### unsorted keys ####"


class BaseLocaliseForm(QDialog):
    def __init__(self, app_controller: AppController, node: GenericNode, name: str) -> None:
        super().__init__()
        self.setWindowTitle(name)
        self.app_controller = app_controller
        self.source = self.app_controller.file_system.open_file.directory.source
        self.localisation_directory = self.source.directories[Path("localisation/english")]
        self.localisation_meta = self.app_controller.registry.get_metadata(PDXMetadata.LocKey)
        self.localisation_fields = list()
        self.node = node
        self.save_file = None
        self.read_only = False

        self.setLayout(QFormLayout())
        self.form = self.layout()

    def _loc_key_widget(self, node: GenericLocKey | GenericLegacyLocKey, exists: bool) -> QTextEdit:
        label = QLabel(node.key)
        text_edit = QTextEdit()
        text_edit.setProperty("node", node)
        text_edit.setProperty("exists", exists)
        text_edit.setPlainText(node.value)
        self._handle_localisation_field(text_edit)
        label.setBuddy(text_edit)
        text_edit.textChanged.connect(lambda: self._resize_localisation_field(text_edit))
        self.form.addRow(label, text_edit)
        return text_edit

    def _lower_form_body(self) -> None:
        self.save_to_file_label = QLabel("Localisation File:")
        self.file_dropdown = QComboBox()

        self.file_dropdown.setMaxVisibleItems(10)
        self.file_dropdown.setSizeAdjustPolicy(QComboBox.AdjustToContents)
        self.file_dropdown.view().setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        # A really silly hack, to force the popup to obey the above
        self.file_dropdown.setStyleSheet("QComboBox {combobox-popup: 0;}")

        for index, _file in enumerate(self.localisation_directory.files.values()):
            self.file_dropdown.addItem(_file.file.filename, _file)
            if _file.file is self.save_file:
                self.file_dropdown.setCurrentIndex(index)
                self.file_dropdown.setEnabled(False)
        if not self.save_file:
            self.save_file = self.file_dropdown.currentData()

        self.save_to_file_label.setBuddy(self.file_dropdown)
        self.file_dropdown.currentIndexChanged.connect(self._change_save_file)
        self.form.addRow(self.save_to_file_label, self.file_dropdown)

        self.submit_button = QPushButton("Continue")
        self.form.addRow(self.submit_button)
        self.submit_button.clicked.connect(self._submit)

    def _change_save_file(self, index: int) -> None:
        self.save_file = self.file_dropdown.currentData()

    def _get_localisation_node(self, key: str) -> tuple[GenericLocKey | GenericLegacyLocKey, bool]:
        if key in self.localisation_meta.keys():
            loc_node = self.localisation_meta[key]["l_english"]["node"]
            file = self.localisation_meta[key]["l_english"]["file"]
            if file.read_only:
                self.read_only = True
            exists = True
            if file:
                if self.save_file and self.save_file is not file:
                    split_loc_file(self.app_controller.main)
                    return
                self.save_file = file
        else:
            loc_node = GenericLocKey(key, "")
            exists = False
        return loc_node, exists

    def _handle_localisation_field(self, text_edit: QTextEdit) -> None:
        text = self._decode_pdx_string(text_edit.toPlainText())
        if text != text_edit.toPlainText():
            text_edit.blockSignals(True)
            text_edit.setPlainText(text)
            text_edit.blockSignals(False)

        self._resize_localisation_field(text_edit)

    def _resize_localisation_field(self, text_edit: QTextEdit) -> None:
        doc_height = text_edit.document().size().height()
        new_height = max(30, int(doc_height + 1))
        new_height = min(new_height, 250)

        text_edit.setFixedHeight(new_height)

        self.adjustSize()

    def showEvent(self, event: QShowEvent) -> None:
        super().showEvent(event)

        for field in self.localisation_fields:
            self._resize_localisation_field(field)

    def _decode_pdx_string(self, value: str) -> str:
        return value.replace("\\n", "\n").replace('\\"', '"').replace("\\\\", "\\")

    def _encode_pdx_string(self, value: str) -> str:
        return value.replace("\\", "\\\\").replace('"', '\\"').replace("\n", "\\n")

    def _save_file_unsorted_comment(self) -> tuple[GenericComment, bool]:
        unsorted_comment = next(
            (
                node
                for node in self.save_file
                if isinstance(node, GenericComment) and node.value == UNSORTED_COMMENT
            ),
            None,
        )
        if unsorted_comment:
            return unsorted_comment, True
        return GenericComment(UNSORTED_COMMENT), False

    def _lock_form(self) -> None:
        form_is_read_only(self.app_controller.main)
        for localisation in self.localisation_fields:
            localisation.setEnabled(False)
        self.file_dropdown.addItem(self.save_file.file.filename, self.save_file)
        self.file_dropdown.setCurrentIndex(self.file_dropdown.count() - 1)
        self.file_dropdown.setEnabled(False)
        self.submit_button.setEnabled(False)

    def _submit(self) -> None:
        missing_generated = []
        for localisation in self.localisation_fields:
            node = localisation.property("node")
            exists = localisation.property("exists")

            if exists:
                self.app_controller.request_node_mutation.emit(
                    NodeMutationRequest(
                        file=self.save_file,
                        node=node,
                        target=TargetProperty.VALUE,
                        value=self._encode_pdx_string(localisation.toPlainText()),
                    )
                )
            else:
                missing_generated.append(localisation)

        if missing_generated:
            comment, exists = self._get_unsorted_comment()
            if not exists:
                self.app_controller.request_node_mutation.emit(
                    BlockMutationRequest.add(
                        file=self.save_file,
                        parent=self.save_file,
                        index=len(self.save_file.nodes) + 1,
                        payload=comment,
                    )
                )
            for localisation in missing_generated:
                self.app_controller.request_block_mutation.emit(
                    BlockMutationRequest.add(
                        file=self.save_file,
                        parent=self.save_file,
                        index=len(self.save_file.nodes) + 1,
                        payload=localisation.property("node"),
                    )
                )
        self.app_controller.request_registry_cache_rebuild.emit()
        self.accept()


class LocaliseNodeForm(BaseLocaliseForm):
    def __init__(self, app_controller: AppController, node: GenericKeyValue) -> None:
        super().__init__(app_controller, node, "Localise Key")
        loc_node, exists = self._get_localisation_node(node.value.value)
        self.localisation_fields.append(self._loc_key_widget(loc_node, exists))
        self._lower_form_body()
        if self.read_only:
            self._lock_form()
        self.exec_()


class LocaliseEventForm(BaseLocaliseForm):
    def __init__(self, app_controller: AppController, node: GenericBlock) -> None:
        super().__init__(app_controller, node, "Localise Event")
        localisation_nodes = [
            *self._get_localisation_nodes("title", "text"),
            *self._get_localisation_nodes("desc", "text"),
            *self._get_localisation_nodes("option", "name"),
        ]
        for node in localisation_nodes:
            loc_node, exists = self._get_localisation_node(node.value.value)
            text_edit = self._loc_key_widget(loc_node, exists)
            self.localisation_fields.append(text_edit)

        self._lower_form_body()
        for field in self.localisation_fields:
            self._resize_localisation_field(field)
        if self.read_only:
            self._lock_form()
        self.exec_()

    def _get_localisation_nodes(self, node_key: str, loc_key: str) -> list[GenericKeyValue]:
        loc_nodes = list()
        loc_entries = [
            node
            for node in self.node.nodes
            if isinstance(node, (GenericBlock, GenericKeyValue)) and node.key == node_key
        ]
        for entry in loc_entries:
            if isinstance(entry, GenericBlock):
                text_node = find_keyvalue(entry, loc_key)
                if text_node:
                    loc_nodes.append(text_node)
            else:
                loc_nodes.append(entry)
        return loc_nodes


class LocaliseFocusForm(BaseLocaliseForm):
    def __init__(self, app_controller: AppController, node: GenericBlock) -> None:
        super().__init__(app_controller, node, "Localise National Focus")
        self.localisation_fields = list()
        focus_id_node = find_keyvalue(node, "id")
        if not focus_id_node:
            return  # error
        id_key = focus_id_node.value.value
        id_loc_node, id_exists = self._get_localisation_node(id_key)
        id_text_edit = self._loc_key_widget(id_loc_node, id_exists)
        self.localisation_fields.append(id_text_edit)

        desc_key = f"{id_key}_desc"
        desc_loc_node, desc_exists = self._get_localisation_node(desc_key)
        desc_text_exit = self._loc_key_widget(desc_loc_node, desc_exists)
        self.localisation_fields.append(desc_text_exit)

        self._lower_form_body()
        for field in self.localisation_fields:
            self._resize_localisation_field(field)
        if self.read_only:
            self._lock_form()
        self.exec_()
