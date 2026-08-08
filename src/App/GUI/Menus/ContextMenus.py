from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import AppController
from PyQt5.QtCore import pyqtSignal
from PyQt5.QtWidgets import (
    QAction,
    QApplication,
    QLabel,
    QMenu,
    QTreeWidget,
    QTreeWidgetItem,
    QWidgetAction,
)

from App.Contexts import BlockContext, FileContext, NodeContext
from App.Contracts import BlockMutationRequest
from App.Contracts.Enums import ChangeState
from App.GUI.Actions import Action, ActionGroup, ActionsResult, ActionSubMenu
from App.GUI.Enums import ExpansionMode
from App.GUI.Forms.DLCConfig import ConfigureLoadedDLCForm
from App.GUI.Forms.LoadOrderForms import CopyFileForm, AddReplacePathForm
from App.Loading.Directories.Base import GenericDirectory
from App.Loading.ParadoxSource import ParadoxMod, ParadoxVanilla
from App.Loading.Models import FileReference
from ParadoxParser import ParadoxScriptParser as PDXScriptFile
from ParadoxParser.ParadoxNodes import GenericBlock


def dummy() -> None: return 

class GenericContextMenu(QMenu):
    def __init__(self, parent: QTreeWidgetItem, app_controller: AppController) -> None:
        super().__init__()
        self.parent: QTreeWidget = parent
        self.app_controller = app_controller
        self.menu_def: list = []
        self.parent_node = None
        self.parent_index = None

    def _build_menu(self) -> None:
        for item in self.menu_def:
            if isinstance(item, ActionGroup):
                self._build_subcategory(item)
            elif isinstance(item, ActionSubMenu):
                self._build_submenu(item)
            elif isinstance(item, Action):
                self._build_button(self, item)

    def _build_subcategory(self, group: ActionGroup) -> None:
        label = QLabel(group.text)
        label.setStyleSheet("""
            font-weight:bold;
            padding: 4px 12px;
        """)
        action = QWidgetAction(self)
        action.setDefaultWidget(label)
        self.addAction(action)
        self.addSeparator()
        for item in group.actions:
            if isinstance(item, Action):
                self._build_button(self, item)
            elif isinstance(item, ActionSubMenu):
                self._build_submenu(item)

    def _build_submenu(self, group: ActionSubMenu) -> None:
        _menu = QMenu(group.text, self)
        for item in group.actions:
            self._build_button(_menu, item)
        self.addMenu(_menu)

    def _build_button(self, menu: ActionGroup | ActionSubMenu, item: Action) -> None:
        action = QAction(item.text, menu)
        action.triggered.connect(item.callback)
        action.setEnabled(item.enabled)
        menu.addAction(action)


class GenericDirectoryMenu(GenericContextMenu):
    def __init__(self, parent: QTreeWidget, app_controller: AppController) -> None:
        super().__init__(parent, app_controller)
        self.menu_def: list = []

    def call(self, file_context: FileContext) -> None:
        self.clear()
        match file_context.target:
            case ParadoxVanilla():
                self.menu_def = self._build_vanilla_source_menu(file_context)
            case ParadoxMod():
                self.menu_def = self._build_mod_source_menu(file_context)
            case GenericDirectory():
                self.menu_def = self._build_directory_menu(file_context)
            case FileReference():
                self.menu_def = self._build_file_menu(file_context)
            case _:
                pass
        self._build_menu()

    def _build_vanilla_source_menu(self, file_context:FileContext) -> list[ActionGroup]:
        return [
            ActionGroup(
                "Source Options",
                [
                    Action(
                        "Configure Loaded DLC", 
                        lambda: ConfigureLoadedDLCForm(self.app_controller), 
                        True
                    )
                ]
            ),
            ActionGroup(
                "File Options",
                file_context.context.get_actions(self.app_controller, file_context.target)
            )
        ]

    def _build_mod_source_menu(self, file_context:FileContext) -> list[ActionGroup]:
        return [
            ActionGroup(
                "Source Options",
                [
                    Action(
                        "No Actions Available", 
                        dummy, 
                        False
                    )
                ]
            ),
            ActionGroup(
                "File Options",
                file_context.context.get_actions(self.app_controller, file_context.target)
            )
        ]
    
    def _build_directory_menu(self, file_context:FileContext)-> list[ActionGroup]:
        return [
            ActionGroup(
                "Directory Options",
                [
                    Action(
                        "Add to replace path",
                        lambda: AddReplacePathForm(self.app_controller, file_context),
                        True
                    )
                ]
            ),
            ActionGroup(
                "File Options",
                file_context.context.get_actions(self.app_controller, file_context.target)
            )
        ]

    def _build_file_menu(self, file_context:FileContext) -> list[ActionGroup]:
        return [
            ActionGroup(
                "File Options",
                [
                    Action(
                        "Copy File to Source",
                        lambda: CopyFileForm(self.app_controller, file_context),
                        True
                    ),
                    *file_context.context.get_actions(self.app_controller, file_context.target)
                ]
            )
        ]
    
    def _get_context_menu_options(self, file_context: FileContext) -> None:
        return file_context.context.get_actions(self.app_controller, file_context.target)


class ParadoxNodesContextMenu(GenericContextMenu):
    request_expansion = pyqtSignal(object)

    def __init__(self, parent: QTreeWidget, app_controller: AppController) -> None:
        super().__init__(parent, app_controller)
        self.menu_def: list = []

    def call(self, block_context: BlockContext, node_context: NodeContext) -> None:
        self.clear()
        self.menu_def = self._get_context_menu_options(block_context, node_context)
        self._build_menu()

    def _get_context_menu_options(
        self, block_context: BlockContext, node_context: NodeContext
    ) -> ActionsResult:
        return [
            ActionGroup(
                "Tree Options",
                [
                    Action(
                        "Expand All",
                        lambda: self.parent.set_expansion_rule(ExpansionMode.ALL),
                        True,
                    ),
                    Action(
                        "Collapse All",
                        lambda: self.parent.set_expansion_rule(ExpansionMode.DEPTH, depth_limit=1),
                        True,
                    ),
                    Action(
                        "Expand This",
                        lambda: self.parent.set_expansion_rule(
                            ExpansionMode.FROM_NODE, root_item=block_context.parent
                        ),
                        (
                            block_context.parent_index == 0
                            and isinstance(block_context.parent, GenericBlock)
                        ),
                    ),
                    Action(
                        "Copy",
                        lambda: QApplication.clipboard().setText(node_context.selected_node.value),
                        True,
                    ),
                ],
            ),
            ActionGroup(
                "Block Options",
                [
                    Action(
                        "Delete",
                        lambda: self.app_controller.request_block_mutation.emit(
                            BlockMutationRequest(
                                file=None,
                                parent=block_context.parent,
                                index=block_context.parent_index,
                                payload=None,
                                state=ChangeState.DELETED,
                            )
                        ),
                        (not isinstance(block_context.parent, PDXScriptFile)),
                    ),
                    # *block_context.parent_context.get_actions(self.app_controller,
                    #                                           block_context.parent)
                ],
            ),
            ActionGroup(
                "Node Options",
                [*node_context.node_context.get_actions(self.app_controller, node_context)],
            ),
        ]
