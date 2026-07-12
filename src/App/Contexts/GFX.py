import os

from ParadoxParser import ParadoxScriptParser as PDXFile
from ParadoxParser.ParadoxNodes import GenericBlock

from App.Contracts import BlockMutationRequest
from App.Contexts.Base import ParadoxContext, ParadoxFileContext, ParadoxNodeContext
from App.GUI.Actions import Action
from App.PDXFactory.Blocks.Sprites import GFX_icon, GFX_shine_icon

class GFXContext(ParadoxContext):
    @staticmethod
    def get_file_context():
        return GFXFileContext
    
    @staticmethod
    def get_block_context(node):
        if isinstance(node, GenericBlock):
            if node.key.lower() == "spritetypes":
                return GFXSpriteTypesContext
        return GFXRootContext
    
    @staticmethod
    def get_node_context(node):
        return
    
class GFXFileContext(ParadoxFileContext):
    @staticmethod
    def get_actions(app_controller, file):
        from App.GUI.Forms.AddGFX import AddNewGFXForm
        return [
            *ParadoxFileContext.get_actions(app_controller, file),
            Action("Bulk-Upload Sprites",
                   lambda:AddNewGFXForm(app_controller, file),
                   isinstance(file, PDXFile))
        ]

class GFXRootContext(ParadoxFileContext):
    @staticmethod
    def get_actions(app_controller, block_context):
        return [
            *ParadoxNodeContext.get_actions(app_controller, block_context)
        ]
    
class GFXSpriteTypesContext(ParadoxFileContext):
    def get_actions(app_controller, block_context):
        return [
            *ParadoxNodeContext.get_actions(app_controller, block_context),
            Action("Add Static Sprite",
                   lambda:app_controller.request_block_mutation.emit(
                       BlockMutationRequest.add(block_context.parent, block_context.parent_index, GFX_icon)
                   ), True
            ),
            Action("Add Focus _shine Sprite",
                   lambda:app_controller.request_block_mutation.emit(
                       BlockMutationRequest.add(block_context.parent, block_context.parent_index, GFX_shine_icon)
                   ), True
            )
        ]