from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue

from App.Contracts import BlockMutationRequest
from App.Contexts.Base import (ParadoxContext, ParadoxFileContext, ParadoxNodeContext,
                              LocalisationFieldContext, GFXFieldContext, dummy)
from App.GUI.Actions import Action
from App.PDXFactory.Blocks.Events import (add_namespace_keyval, country_event_block, news_event_block, 
                                          immediate_block, option_block)
from App.GUI.Actions import Action

class FocusTreeContext(ParadoxContext):
    @staticmethod
    def get_file_context():
        return FocusFileContext
    
    @staticmethod
    def get_block_context(node):
        return FocusRootContext
    
    @staticmethod
    def get_node_context(parent_node, node):
        if isinstance(node, GenericKeyValue):
            if parent_node.key != "focus_tree" and node.key == "id":
                return LocalisationFieldContext
            elif node.key == "icon":
                return GFXFieldContext
        return ParadoxNodeContext
            
class FocusFileContext(ParadoxFileContext):
    @staticmethod
    def get_actions(app_controller, file):
        return [
            *ParadoxFileContext.get_actions(app_controller, file)
        ]

class FocusRootContext(ParadoxFileContext):
    @staticmethod
    def get_actions(app_controller, block_context):
        return [
            *ParadoxNodeContext.get_actions(app_controller, block_context)
        ]
