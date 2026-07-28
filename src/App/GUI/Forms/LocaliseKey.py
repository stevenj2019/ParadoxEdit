from pathlib import Path
from PyQt5.QtWidgets import QDialog, QFormLayout, QLabel, QTextEdit, QComboBox, QPushButton
from PyQt5.QtCore import QTimer

from ParadoxParser.ParadoxNodes import GenericLocKey, GenericBlock, GenericComment

from App.Enums import PDXMetadata
from App.Contracts import NodeMutationRequest, BlockMutationRequest
from App.Contracts.Enums import TargetProperty

class BaseLocaliseForm(QDialog):
    def __init__(self, app_controller, name):
        super().__init__()
        self.setWindowTitle(name)
        self.app_controller = app_controller
        self.source = self.app_controller.file_system.open_file.directory.source
        self.localisation_directory = self.source.directories[Path("localisation/english")]
        self.localisation_meta = self.app_controller.registry.get_metadata(PDXMetadata.LocKey)

        self.save_file = None

        self.setLayout(QFormLayout())
        self.form = self.layout()

    def _loc_key_widget(self, node):
        label = QLabel(node.key)
        text_edit = QTextEdit()
        text_edit.setProperty("node", node)
        text_edit.setPlainText(node.value)
        self._handle_localisation_field(text_edit)
        label.setBuddy(text_edit)
        text_edit.textChanged.connect(lambda: self._resize_localisation_field(text_edit))
        self.form.addRow(label, text_edit)
        return text_edit
    
    def _lower_form_body(self):
        self.save_to_file_label = QLabel("Localisation File:")
        self.file_dropdown = QComboBox()
        for index, _file in enumerate(self.localisation_directory.files.values()):
            self.file_dropdown.addItem(_file.file.filename)
            if _file is self.save_file:
                self.file_dropdown.setCurrentIndex(index)
                self.file_dropdown.setEnabled(False)
                self.save_file = self.localisation_directory.files[self.file_dropdown.itemText(index)]
        if not self.save_file:
            text = self.file_dropdown.currentText()
            self.save_file = self.localisation_directory.files[text]

        self.save_to_file_label.setBuddy(self.file_dropdown)
        self.file_dropdown.currentIndexChanged.connect(self._change_save_file)
        self.form.addRow(self.save_to_file_label, self.file_dropdown)    
        
        self.submit_button = QPushButton("Continue")
        self.form.addRow(self.submit_button)
        self.submit_button.clicked.connect(self._submit)
    
    def _change_save_file(self, index):
        file = self.file_dropdown.itemText(index)
        self.save_file = self.localisation_directory.files[file]
    
    def _handle_localisation_field(self, text_edit):
        # text = text_edit.toPlainText()
        # text = text.replace("\\n", "\n")
        text = self._decode_pdx_string(text_edit.toPlainText())
        if text != text_edit.toPlainText():
            text_edit.blockSignals(True)
            text_edit.setPlainText(text)
            text_edit.blockSignals(False)

        self._resize_localisation_field(text_edit)
    
    def _resize_localisation_field(self, text_edit):
        doc_height = text_edit.document().size().height()
        new_height = max(30, int(doc_height+1))
        new_height = min(new_height, 250)

        text_edit.setFixedHeight(new_height)

        self.adjustSize()

    def showEvent(self, event):
        super().showEvent(event)

        for field in self.localisation_fields:
            self._resize_localisation_field(field)

    def _decode_pdx_string(self, value):
        return (
            value
            .replace('\\n', '\n')
            .replace('\\"', '"')
            .replace('\\\\', '\\')
        )

    def _encode_pdx_string(self, value):
        return (
            value
            .replace("\\", "\\\\")
            .replace('"', '\\"')
            .replace("\n", "\\n")
        )

class LocaliseNodeForm(BaseLocaliseForm):
    def __init__(self, app_controller, node):
        super().__init__(app_controller, "Localise Key")
        key = node.value.value
        if key in self.localisation_meta.keys():
            node_selected = self.localisation_meta[key]["l_english"]["node"]
            self.save_file = self.localisation_meta[key]["l_english"]["file"]
        else:
            node_selected = GenericLocKey(key, "")
            self.save_file = None
        self.loc_text = self._loc_key_widget(node_selected)
        self.localisation_fields.append(self.loc_text)
        self._lower_form_body()
        self.exec_()

    def _submit(self):
        self._handle_localisation_field(self.loc_text)
        # new_value = self.loc_text.toPlainText().replace("\n", "\\n")
        new_value = self._encode_pdx_string(self.loc_text.toPlainText())
        self.app_controller.request_node_mutation.emit(
            NodeMutationRequest(file=self.save_file, node=self.node_selected, target=TargetProperty.VALUE, value=new_value)
        )

class LocaliseEventForm(BaseLocaliseForm):
    def __init__(self, app_controller, node):
        super().__init__(app_controller, "Localise Event")
        self.localisation_fields = list()
        self.node = node
        localisation_nodes = [
            *self._get_localisation_nodes("title", "text"),
            *self._get_localisation_nodes("desc", "text"),
            *self._get_localisation_nodes("option", "name"),
        ]

        multiple_file_error = False
        for node in localisation_nodes:
            if node.value.value in self.localisation_meta.keys():
                loc_node = self.localisation_meta[node.value.value]["l_english"]["node"]
                file = self.localisation_meta[node.value.value]["l_english"]["file"]
                if self.save_file and self.save_file is not file:
                    multiple_file_error = True
                else:
                    self.save_file = file
            else:
                loc_node = GenericLocKey(node.value.value, "")

            text_edit = self._loc_key_widget(loc_node)
            # QTimer.singleShot(0, lambda: self._resize_localisation_field(text_edit))
            self.localisation_fields.append(text_edit)

            if multiple_file_error:
                pass #dialog
        
        self._lower_form_body()
        for field in self.localisation_fields:
            self._resize_localisation_field(field)
        self.exec_()

    def _get_localisation_nodes(self, node_key:str, loc_key:str):
        loc_nodes = list()
        loc_entries = [node for node in self.node.nodes if not isinstance(node, GenericComment) and node.key == node_key]
        for entry in loc_entries:
            if isinstance(entry, GenericBlock):
                text_node = next((node for node in entry.nodes if not isinstance(node, GenericComment) and node.key == loc_key), None)
                if text_node:
                    loc_nodes.append(text_node)
            else:
                loc_nodes.append(entry)
        return loc_nodes
    
    def _submit(self):
        for localisation in self.localisation_fields:
            self._handle_localisation_field(localisation)
            node = localisation.property("node")
            new_value = localisation.toPlainText().replace("\n", "\\n")
            self.app_controller.request_node_mutation.emit(
                NodeMutationRequest(file=self.save_file, node=node, target=TargetProperty.VALUE, value=new_value)
            )