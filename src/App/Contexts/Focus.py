from ParadoxParser.ParadoxNodes import GenericKeyValue

from App.Contexts.Base import (ParadoxContext, ParadoxFileContext, ParadoxBlockContext,
                               ParadoxNodeContext, LocalisationFieldContext, GFXFieldContext)
from App.PDXFactory.Blocks.Events import (add_namespace_keyval, country_event_block, news_event_block, 
                                          immediate_block, option_block)

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
            if parent_node.key == "focus" and node.key == "id":
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

class FocusRootContext(ParadoxBlockContext):
    @staticmethod
    def get_actions(app_controller, block_context):
        return [
            *ParadoxNodeContext.get_actions(app_controller, block_context)
        ]
