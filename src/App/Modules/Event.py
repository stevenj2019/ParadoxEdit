import os 

from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue

from App.Contracts import BlockMutationRequest
from App.Modules.Base import (GenericCategory, ParadoxContext, 
                              ParadoxFileContext, ParadoxNodeContext,
                              LocalisationContext, GFXContext)
from App.GUI.Actions import Action
from App.PDXFactory.Blocks.Events import (add_namespace_keyval, country_event_block, news_event_block, 
                                          immediate_block, option_block)
from App.GUI.Actions import Action

#TODO: need to update front-end to use this
###        ###
#  CATEGORY  #
###        ###
class EventCategory(GenericCategory):
    def __init__(self, mod_path:os.PathLike):
        super().__init__(mod_path, ["events/"], EventContext)

###        ###
#  CONTEXTS  #
###        ###
class EventContext(ParadoxContext):
    @staticmethod
    def get_file_context():
        return EventFileContext
    
    @staticmethod
    def get_block_context(node):
        if isinstance(node, GenericBlock):
            if node.key in ["news_event", "country_event"]:
                return EventBlockContext
            elif node.key in ["option", "immediate"]:
                return EventOptionContext
        return EventRootContext
    
    @staticmethod
    def get_node_context(node):
        if isinstance(node, GenericKeyValue):
            if node.key in ("name", "title", "desc", "name"):
                return LocalisationContext
            elif node.key == "picture":
                return GFXContext
            
class EventFileContext(ParadoxFileContext):
    @staticmethod
    def get_actions(app_controller, file):
        return [
            *ParadoxFileContext.get_actions(app_controller, file)
            # Action("Inject Event Logs", dummy(), False),
            
        ]

class EventRootContext(ParadoxFileContext):
    @staticmethod
    def get_actions(app_controller, block_context):
        return [
            *ParadoxNodeContext.get_actions(app_controller, block_context),
            Action("Add Namespace", 
                   lambda:app_controller.request_block_mutation.emit(
                       BlockMutationRequest.add(block_context.parent, block_context.parent_index, add_namespace_keyval)
                   ), 
                   True
            ),
            Action("Add Country Event",
                   lambda:app_controller.request_block_mutation.emit(
                       BlockMutationRequest.add(block_context.parent, block_context.parent_index, country_event_block)
                   ),
                   True
            ),
            Action("Add News Event",
                   lambda:app_controller.request_block_mutation.emit(
                       BlockMutationRequest.add(block_context.parent, block_context.parent_index, news_event_block)
                   ),
                   True
            )
        ]
class EventBlockContext:
    @staticmethod
    def get_actions(app_controller, block_context):
        return [
            *ParadoxNodeContext.get_actions(app_controller, block_context),
            Action("Add Immediate Block",
                   lambda:app_controller.request_block_mutation.emit(
                       BlockMutationRequest.add(block_context.parent, block_context.parent_index, immediate_block)
                   ),
                   True
            ),
            Action("Add Option Block",
                   lambda:app_controller.request_block_mutation.emit(
                       BlockMutationRequest.add(block_context.parent, block_context.parent_index, option_block)
                   ),
                   True
            )
        ]
    
class EventOptionContext:
    @staticmethod
    def get_actions(app_controller, block_context):
        return [
            *ParadoxNodeContext.get_actions(app_controller, block_context),
            # *TriggerBlockActions.get_actions(context), 
            # *EventBlockContext.get_actions(context),
        ]
