from PyQt5.QtWidgets import QDialog, QFormLayout, QLabel, QLineEdit, QTextEdit, QComboBox, QPushButton

from ParadoxParser.ParadoxNodes import GenericLocKey

from App.Contracts import NodeMutationRequest, BlockMutationRequest

class LocaliseForm(QDialog):
    def __init__(self, app_controller, key:str=None):
        super().__init__()
        self.app_controller = app_controller
        self.category = app_controller.file_system.mod.categories["LocalisationCategory"]

        loc_dict = self.category.metadata
        if key and key in loc_dict.keys():
            self.save_file = loc_dict[key]["file"]
            self.node_selected = loc_dict[key]["node"]
        else:
            self.file_selected = None
            self.node_selected = None

        self.setWindowTitle("Localise Key")
        self.resize(550, 150)
        self.setLayout(QFormLayout())
        self.form = self.layout()

        self.key_input_label = QLabel("Localisation key:")
        self.key_input_text = QLineEdit()
        if key is not None:
            self.key_input_text.setText(key)
            self.key_input_text.setReadOnly(True)
        self.key_input_label.setBuddy(self.key_input_text)
        self.form.addRow(self.key_input_label, self.key_input_text)

        self.localisation_label = QLabel("localisation Value:")
        self.localisation_text = QTextEdit()
        if self.node_selected is not None:
            self.localisation_text.setPlainText(self.node_selected.value)
            self._handle_localisation_field()
        self.localisation_label.setBuddy(self.localisation_text)
        self.localisation_text.textChanged.connect(self._resize_localisation_field)
        self.form.addRow(self.localisation_label, self.localisation_text)

        self.save_to_file_label = QLabel("Localisation File:")
        self.file_dropdown = QComboBox()
        for index, _file in enumerate(self.category.files.values()):
            self.file_dropdown.addItem(_file.filename)
            if _file is self.file_selected:
                self.file_dropdown.setCurrentIndex(index)
                self.file_dropdown.setEnabled(False)
        if not self.save_file:
            text = self.file_dropdown.currentText()
            self.save_file = self.category.files[text]

        self.save_to_file_label.setBuddy(self.file_dropdown)
        self.file_dropdown.currentIndexChanged.connect(self._change_save_file)
        self.form.addRow(self.save_to_file_label, self.file_dropdown)

        self.submit_button = QPushButton("Continue")
        self.form.addRow(self.submit_button)
        self.submit_button.clicked.connect(self._submit)
        self.exec_()

    def _change_save_file(self, index):
        file = self.file_dropdown.itemText(index)
        self.save_file = self.category.files[file]
    
    def _handle_localisation_field(self):
        text = self.localisation_text.toPlainText()
        text = text.replace("\\n", "\n")

        if text != self.localisation_text.toPlainText():
            self.localisation_text.blockSignals(True)
            self.localisation_text.setPlainText(text)
            self.localisation_text.blockSignals(False)

        self._resize_localisation_field()
    
    def _resize_localisation_field(self):
        doc_height = self.localisation_text.document().size().height()
        new_height = max(30, int(doc_height+1))
        new_height = min(new_height, 250)

        self.localisation_text.setFixedHeight(new_height)

    #TODO: this needs more validation
    def _submit(self):
        self._handle_localisation_field()
        key = self.key_input_text.text()
        new_value = self.localisation_text.text().replace("\n", "\\n")
        if self.node_selected is not None:
            self.app_controller.request_node_mutation.emit(
                NodeMutationRequest(file=self.save_file, node=self.node_selected, node_value=self.node_selected, value=new_value)
            )
        else:
            node = GenericLocKey(key, new_value)
            self.app_controller.request_block_mutation.emit(
                BlockMutationRequest.add(self.save_file, len(self.save_file.nodes)+1, node, self.save_file)
            )
