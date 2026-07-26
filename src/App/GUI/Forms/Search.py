import re
from PyQt5.QtWidgets import QDialog, QFormLayout, QPushButton, QTreeWidget, QTreeWidgetItem

from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser import ParadoxLocParser as PDXLocFile
from ParadoxParser.ParadoxNodes import GenericBlock, GenericComparator, GenericKeyValue, GenericNode

from App.Loading.Models import FileReference
from App.GUI.Widgets.CustomWidgets import CheckableComboBox, SearchLineEdit
from App.Contracts import SearchResult
from App.GUI.Enums import QtStorage

class SearchForm(QDialog):
    def __init__(self, app_controller):
        super().__init__()
        self.app_controller = app_controller
        self.load_order = self.app_controller.file_system.load_order

        self.case_sensitive = False
        self.regex_search = False
        self.search_results = list()

        self.setWindowTitle("Search")
        self.resize(200, 100)
        self.setLayout(QFormLayout())
        self.form = self.layout()

        self.source_selector_widget = CheckableComboBox()
        for source in self.load_order.sources:
            self.source_selector_widget.addItem(source.source_name, source)
        self.form.addRow("", self.source_selector_widget)

        self.search_control_widget = SearchLineEdit()
        self.search_control_widget.caseChanged.connect(self._set_case_sensitivity)
        self.search_control_widget.regexChanged.connect(self._set_regex)
        self.form.addRow("🔍︎", self.search_control_widget)

        self.search_button = QPushButton("Search 🔍︎")
        self.search_button.clicked.connect(self._get_search_results)
        self.form.addRow(self.search_button)

        self.results_tree = QTreeWidget()
        self.results_tree.setColumnCount(1)
        self.results_tree.setHeaderLabel("Result(s)")
        self.results_tree.setVisible(False)
        self.results_tree.setMaximumHeight(400)
        self.results_tree.itemDoubleClicked.connect(self._result_double_clicked)
        self.results_tree.setExpandsOnDoubleClick(False)
        self.form.addRow(self.results_tree)

    def _set_case_sensitivity(self, case_sensitive:bool):
        self.case_sensitive = case_sensitive

    def _set_regex(self, regex:bool):
        self.regex_search = regex

    def _get_search_results(self):
        selected_sources = self.source_selector_widget.currentData()
        search_text = self.search_control_widget.text().strip()

        def matches(value, node_value):
            value = str(value)
            node_value = str(node_value)

            if self.regex_search:
                flags = 0 
                if not self.case_sensitive:
                    flags |= re.IGNORECASE
                try:
                    return re.search(value, node, flags) is not None
                except re.error:
                    return False
                
            if not self.case_sensitive:
                value = value.lower()
                node_value = node_value.lower()
            return value in node_value

        def recurse(result, node):
            if isinstance(node, GenericBlock):
                if matches(search_text, node.key):
                    result.results.append(node)
                for child in node.nodes:
                    recurse(result, child)
            else:
                if matches(search_text, node._to_string_literal().strip()):
                    result.results.append(node)

        self.search_results = list()
        for source in selected_sources:
            for file in source.root.iter_files():
                if isinstance(file.file, (PDXScriptFile, PDXLocFile)):
                    result = SearchResult(file, [])
                    for node in file.file.nodes:
                        recurse(result, node)
                    if result.results:
                        self.search_results.append(result)
        self._build_results_tree()

    def _build_results_tree(self):
        self.results_tree.clear()
        for result in self.search_results:
            file_item = QTreeWidgetItem([f"{result.file.file.filename} - {len(result.results)} instance(s)"])
            file_item.setToolTip(0, str(result.file.file.filepath))
            file_item.setData(0, QtStorage.FILE, result.file)
            self.results_tree.addTopLevelItem(file_item)
            for instance in result.results:
                if isinstance(instance, GenericBlock):
                    text = f"{instance.key} = {{"
                else:
                    text = instance._to_string_literal().strip()
                # match instance:
                #     case GenericBlock():
                #         text = f"{instance.key} = {{"
                #     case GenericKeyValue():
                #         text = f"{instance.key} = {instance.value.value}"
                #     case GenericComparator():
                #         text = f"{instance.left} {instance.operator} {instance.right}"
                #     case GenericNode():
                #         text = f"{instance.value}"

                item = QTreeWidgetItem([text])
                item.setData(0, QtStorage.FILE, result.file)
                item.setData(0, QtStorage.NODE, instance)
                file_item.addChild(item)
        self.results_tree.setVisible(True)
        self.results_tree.resizeColumnToContents(0)
        self.adjustSize()

    def _result_double_clicked(self, item, column):
        file = item.data(0, QtStorage.FILE)
        self.app_controller.main.load_file(file)
        node = item.data(0, QtStorage.NODE)
        if node:
            self.app_controller.main.contents_panel.script_view.jump_to_node(node)