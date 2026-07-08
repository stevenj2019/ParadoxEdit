import os

from ParadoxParser import ParadoxScriptParser as PDXFile
from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue

from App.Services import AppLogger
from App.Contracts import BlockMutationRequest
from App.Modules.Base import GenericCategory, ParadoxContext, ParadoxFileContext, ParadoxNodeContext
from App.GUI.Actions import Action
from App.GUI.Forms.AddGFX import AddNewGFXForm
from App.PDXFactory.Blocks.Sprites import GFX_icon, GFX_shine_icon

###        ###
#  CATEGORY  #
###        ###
class GFXCategory(GenericCategory):
    def __init__(self, mod_path:os.PathLike):
        super().__init__(mod_path, ["interface/"], GFXContext, ".gfx")

    def _build_metadata(self):
        self.metadata = dict()
        for file in self.files.values():
            try:
                block = next(block for block in file.nodes
                            if isinstance(block, GenericBlock)
                            and block.key.lower() == "spritetypes")
            except StopIteration:
                print(file.filename, "has no spritetypes block")
                AppLogger.error(f"{file.filename} malformed, cannot find SpriteTypes block")
                pass
            for node in block.nodes:
                if isinstance(node, GenericBlock) and node.key.lower() == "spritetype":
                    name = next((kvnode.value.value for kvnode in node.nodes
                                if isinstance(kvnode, GenericKeyValue)
                                and kvnode.key.lower() == "name"), "")
                    texture = next((kvnode.value.value for kvnode in node.nodes
                                    if isinstance(kvnode, GenericKeyValue)
                                    and kvnode.key.lower() == "texturefile"), "")
                    if name and texture:
                        self.metadata[name] = texture
                    else:
                        AppLogger.error(f"{file.filename} in {node.key} block, missing name:{name} or texturefile:{texture}")
        print()

    def _get_metadata(self, key):
        try:
            return self.metadata[key]
        except KeyError:
            return None
###        ###
#  CONTEXTS  #
###        ###
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