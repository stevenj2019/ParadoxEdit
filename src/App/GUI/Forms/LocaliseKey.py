from PyQt5.QtWidgets import QDialog, QFormLayout, QLabel, QLineEdit, QTextEdit, QComboBox, QPushButton

from ParadoxParser.ParadoxNodes import GenericBlock, GenericLocKey

# from App.Contexts.Loc import LocDirectoryContext
from App.Contracts import NodeMutationRequest, BlockMutationRequest

CATEGORY = "LocDirectoryContext"
class BaseLocaliseForm(QDialog):
    def __init__(self, app_controller, name):
        super().__init__()
        self.setWindowTitle(name)
        self.app_controller = app_controller
        self.category = app_controller.registry.get_category(CATEGORY)
        self.category_meta = app_controller.registry.get_category_metadata(CATEGORY)
        
        self.setLayout(QFormLayout())
        self.form = self.layout()

    def _loc_key_widget(self, key, value=None):
        label = QLabel(key)
        text_edit = QTextEdit()
        if value is not None:
            text_edit.setPlainText(value)
        self._handle_localisation_field(text_edit)
        label.setBuddy(text_edit)
        text_edit.textChanged.connect(lambda: self._resize_localisation_field(text_edit))
        self.form.addRow(label, text_edit)
        return text_edit
    
    def _lower_form_body(self):
        self.save_to_file_label = QLabel("Localisation File:")
        self.file_dropdown = QComboBox()
        for index, _file in enumerate(self.category.files.values()):
            self.file_dropdown.addItem(_file.filename)
            if _file is self.save_file:
                self.file_dropdown.setCurrentIndex(index)
                self.file_dropdown.setEnabled(False)
                self.save_file = self.category.files[self.file_dropdown.itemText(index)]
        if not self.save_file:
            text = self.file_dropdown.currentText()
            self.save_file = self.category.files[text]

        self.save_to_file_label.setBuddy(self.file_dropdown)
        self.file_dropdown.currentIndexChanged.connect(self._change_save_file)
        self.form.addRow(self.save_to_file_label, self.file_dropdown)    
        
        self.submit_button = QPushButton("Continue")
        self.form.addRow(self.submit_button)
        self.submit_button.clicked.connect(self._submit)
    
    def _change_save_file(self, index):
        file = self.file_dropdown.itemText(index)
        self.save_file = self.category.files[file]
    
    def _handle_localisation_field(self, text_edit):
        text = text_edit.toPlainText()
        text = text.replace("\\n", "\n")

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

class LocaliseNodeForm(BaseLocaliseForm):
    def __init__(self, app_controller, key:str=None):
        super().__init__(app_controller, "Localise Key")
        self.loc_key = key
        if key in self.category_meta.keys():
            self.node_selected = self.category_meta[key]["node"]
            text = self.node_selected.value
            self.save_file = self.category_meta[key]["file"]
        else:
            self.node_selected = None
            text = None
            self.save_file = None
        self.loc_text = self._loc_key_widget(key, text)
        self._lower_form_body()
        self.exec_()

    #Generalise
    def _submit(self):
        self._handle_localisation_field(self.loc_text)
        new_value = self.loc_text.toPlainText().replace("\n", "\\n")
        if self.node_selected is not None:
            self.app_controller.request_node_mutation.emit(
                NodeMutationRequest(file=self.save_file, node=self.node_selected, node_value=self.node_selected, value=new_value)
            )
        else:
            node = GenericLocKey(self.loc_key, new_value)
            self.app_controller.request_block_mutation.emit(
                BlockMutationRequest.add(self.save_file, len(self.save_file.nodes)+1, node, self.save_file)
            )
# class LocaliseEventForm(BaseLocaliseForm):
#     def __init__(self, app_controller, block:GenericBlock):
#         super().__init__(app_controller, "Localise Event")