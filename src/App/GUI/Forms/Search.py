from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import AppController

import re

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import (
    QDialog,
    QFormLayout,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QStackedWidget,
    QToolButton,
    QTreeWidget,
    QTreeWidgetItem,
    QWidget,
)

from App.Contracts import SearchResult
from App.GUI.Enums import QtStorage
from App.GUI.Widgets.CustomWidgets import CheckableComboBox, SearchLineEdit
from ParadoxParser import ParadoxLocParser as PDXLocFile
from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser.ParadoxNodes import (
    GenericBlock,
    GenericNode,
)


class SearchForm(QDialog):
    def __init__(self, app_controller: AppController) -> None:
        super().__init__()
        self.app_controller = app_controller
        self.load_order = self.app_controller.file_system.load_order

        self.case_sensitive = False
        self.regex_search = False
        self.search_results = list()

        self.setWindowTitle("Search")
        self.resize(250, 100)
        self.setLayout(QFormLayout())
        self.form = self.layout()

        self.control_layout = QHBoxLayout()

        self.search_control_widget = SearchLineEdit()
        self.search_control_widget.caseChanged.connect(self._set_case_sensitivity)
        self.search_control_widget.regexChanged.connect(self._set_regex)
        self.control_layout.addWidget(self.search_control_widget)

        self.toggle_advanced_search = QToolButton()
        self.toggle_advanced_search.setToolTip("Show advanced options")
        self.toggle_advanced_search.setFixedWidth(24)
        self.toggle_advanced_search.setArrowType(Qt.DownArrow)
        self.toggle_advanced_search.clicked.connect(self.toggle_options)
        self.control_layout.addWidget(self.toggle_advanced_search)

        self.form.addRow("🔍︎", self.control_layout)

        self.advanced_control_container = QWidget()
        self.advanced_control_container.setVisible(False)
        self.advanced_control_container_layout = QFormLayout()
        self.advanced_control_container_layout.setContentsMargins(0, 0, 0, 0)

        self.advanced_control_container.setLayout(
            self.advanced_control_container_layout
        )

        self.source_selector_widget = CheckableComboBox()
        for source in self.load_order.sources:
            self.source_selector_widget.addItem(source.source_name, source)
        self.advanced_control_container_layout.addRow("📦", self.source_selector_widget)

        self.form.addRow(self.advanced_control_container)

        self.search_button = QPushButton("Search 🔍︎")
        self.search_button.clicked.connect(self._get_search_results)
        self.form.addRow(self.search_button)

        self.result = QStackedWidget()
        self.result.setVisible(False)

        self.results_tree = QTreeWidget()
        self.results_tree.setColumnCount(1)
        self.results_tree.setHeaderLabel("Result(s)")
        self.results_tree.setMaximumHeight(400)
        self.results_tree.itemDoubleClicked.connect(self._result_double_clicked)
        self.results_tree.setExpandsOnDoubleClick(False)
        self.result.addWidget(self.results_tree)

        self.no_results_label = QLabel("No Results Found")
        self.no_results_label.setAlignment(Qt.AlignCenter)
        self.no_results_label.setMaximumHeight(50)
        self.result.addWidget(self.no_results_label)

        self.form.addRow(self.result)

    def toggle_options(self) -> None:
        self.toggle_advanced_search.setArrowType(
            Qt.DownArrow if self.advanced_control_container.isVisible() else Qt.UpArrow
        )
        self.advanced_control_container.setVisible(
            not self.advanced_control_container.isVisible()
        )
        self.toggle_advanced_search.setToolTip(
            f"{'Hide' if self.advanced_control_container.isVisible() else 'Show'} advanced options"
        )
        self.adjustSize()

    def _set_case_sensitivity(self, case_sensitive: bool) -> None:
        self.case_sensitive = case_sensitive

    def _set_regex(self, regex: bool) -> None:
        self.regex_search = regex

    def _get_search_results(self) -> None:
        selected_sources = self.source_selector_widget.currentData()
        search_text = self.search_control_widget.text().strip()

        def matches(value: str, node_value: str) -> bool:
            # value = str(value)
            # node_value = str(node_value)

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

        def recurse(result: SearchResult, node: GenericNode) -> None:
            if isinstance(node, GenericBlock):
                if matches(search_text, node.key):
                    result.results.append(node)
                for child in node.nodes:
                    recurse(result, child)
            else:
                if matches(search_text, node._to_string_literal().strip()):
                    result.results.append(node)

        self.search_results = list()
        search_sources = (
            selected_sources if selected_sources else self.load_order.sources
        )
        for source in search_sources:
            for file in source.root.iter_files():
                if isinstance(file.file, (PDXScriptFile, PDXLocFile)):
                    result = SearchResult(file, [])
                    for node in file.file.nodes:
                        recurse(result, node)
                    if result.results:
                        self.search_results.append(result)
        self._build_results_tree()

    def _build_results_tree(self) -> None:
        self.results_tree.clear()
        if self.search_results:
            for result in self.search_results:
                file_item = QTreeWidgetItem(
                    [f"{result.file.file.filename} - {len(result.results)} instance(s)"]
                )
                file_item.setToolTip(0, str(result.file.file.filepath))
                file_item.setData(0, QtStorage.FILE, result.file)
                self.results_tree.addTopLevelItem(file_item)
                for instance in result.results:
                    if isinstance(instance, GenericBlock):
                        text = f"{instance.key} = {{"
                    else:
                        text = instance._to_string_literal().strip()

                    item = QTreeWidgetItem([text])
                    item.setData(0, QtStorage.FILE, result.file)
                    item.setData(0, QtStorage.NODE, instance)
                    file_item.addChild(item)
            self.results_tree.resizeColumnToContents(0)
            self.result.setCurrentWidget(self.results_tree)
        else:
            self.result.setCurrentWidget(self.no_results_label)
        self.result.setVisible(True)
        self.adjustSize()

    def _result_double_clicked(self, item: QTreeWidgetItem, column: int) -> None:
        file = item.data(0, QtStorage.FILE)
        self.app_controller.main.load_file(file)
        node = item.data(0, QtStorage.NODE)
        if node:
            self.app_controller.main.contents_panel.script_view.jump_to_node(node)
