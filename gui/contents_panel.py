# gui/contents_panel.py
from PyQt5.QtWidgets import QWidget, QLabel, QVBoxLayout, QTreeWidget, QTreeWidgetItem
from ModClasses.ParadoxMod import ParadoxMod
from ModClasses.ParadoxCategoryItem import GenericCategoryItem
from ParadoxParser import ParadoxScriptParser
from ParadoxParser.ParadoxNodes import GenericBlock

#test this at some point, GPT made it 
class ContentsPanel(QWidget):
    def __init__(self, parent:ParadoxMod=None):
        super().__init__()

        layout = QVBoxLayout()
        self.setLayout(layout)

        # Two-column tree: Column 0 = key, Column 1 = value
        self.tree = QTreeWidget()
        self.tree.setColumnCount(2)
        self.tree.setHeaderLabels(["Key", "Value"])
        layout.addWidget(self.tree)

        # Hold reference to the currently loaded block
        self.current_block = None

    def load_block(self, block):
        """
        Load a GenericBlock into the tree for display.
        """
        self.current_block = block
        self.tree.clear()
        #descriptor
        if isinstance(block, ParadoxScriptParser):
            self._add_nodes(self.tree.invisibleRootItem(), block.nodes)
        #categoryitem
        elif isinstance(block, GenericCategoryItem):
            self._add_nodes(self.tree.invisibleRootItem(), block.obj.nodes)
        #?????
        elif isinstance(block, GenericBlock):
            self._add_nodes(self.tree.invisibleRootItem(), block.children)
        #????
        elif isinstance(block, dict):
            self._add_nodes(self.tree.invisibleRootItem(), block)

    def _add_nodes(self, parent_item, nodes):
        """
        Recursive helper to add nodes to the QTreeWidget.
        """
        for node in nodes:
            # Skip comments for display
            if node.__class__.__name__ == "GenericComment":
                # continue
                value_str = self._value_to_str(node.value)
                item = QTreeWidgetItem(["Comment", value_str])
                parent_item.addChild(item)
            # KeyValue
            elif node.__class__.__name__ == "GenericKeyValue":
                value_str = self._value_to_str(node.value)
                item = QTreeWidgetItem([str(node.key), value_str])
                parent_item.addChild(item)

                # If the value itself is a block or list, recurse
                if hasattr(node.value, "children"):
                    self._add_nodes(item, node.value.children)

            # Block/List
            elif isinstance(node, GenericBlock) or isinstance(node, dict):
            # elif hasattr(node, "children") or hasattr(node, "keys"):
                # Use key as the label in column 0, blank in column 1
                item = QTreeWidgetItem([str(node.key), ""])
                parent_item.addChild(item)
                if isinstance(node, GenericBlock):
                    self._add_nodes(item, node.children)
                elif isinstance(node, dict):
                    self._add_nodes(item, node.values())
            # Atomic value without KeyValue
            else:
                value_str = self._value_to_str(node)
                item = QTreeWidgetItem(["", value_str])
                parent_item.addChild(item)

    def _value_to_str(self, node):
        """
        Convert a value node to string for display.
        """
        cls_name = node.__class__.__name__
        match cls_name:
            case "GenericString"|"GenericToken"|"GenericComment":
                return node.value
            case "GenericInt"|"GenericFloat":
                return str(node.value)
            case "GenericBool":
                return "yes" if node.value else "no"
            case "GenericKeyValue":
                return self._value_to_str(node.value)
            case _:
                return (str(getattr(node, "value", node)))
        # if cls_name == "GenericString":
        #     return node.value
        # elif cls_name == "GenericToken":
        #     return node.value
        # elif cls_name == "GenericInt":
        #     return str(node.value)
        # elif cls_name == "GenericFloat":
        #     return str(node.value)
        # elif cls_name == "GenericBool":
        #     return "yes" if node.value else "no"
        # elif cls_name == "GenericKeyValue":
        #     return self._value_to_str(node.value)
        # else:
        #     # fallback
        #     return str(getattr(node, "value", node))