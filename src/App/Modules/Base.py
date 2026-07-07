from __future__ import annotations
import os
from pathlib import Path

from ParadoxParser import ParadoxScriptParser as PDXScriptFile

from App.Contracts import BulkMutationRequest, BlockMutationRequest
from App.GUI.Actions import Action
from App.Scripts.Generic import clear_comments, clear_whitespace

class GenericCategory:
    def __init__(self, base:os.PathLike, paths:list[os.PathLike], context:ParadoxContext, file_type:str=None):
        self.file_type = file_type
        self.files:dict[str, PDXScriptFile] = {}
        self.context = context
        for path in paths:
            self._read_directory(os.path.join(base, path))
    
    def _read_file(self, file):
        self._parse_file(file)
        
    def _read_directory(self, path):
        for root, dirs, files in os.walk(path):
            for name in dirs:
                self._read_directory(Path(os.path.join(root, name)))
            for name in files:
                if ((not self.file_type or name.endswith(self.file_type)) 
                     and not name.endswith(".bak")):
                    self._parse_files(Path(os.path.join(root, name)))

    def _parse_files(self, path:os.PathLike):
        self.files[path.name] = PDXScriptFile(path)

class ParadoxContext:
    @staticmethod
    def get_file_context():
        return ParadoxFileContext
    
    @staticmethod
    def get_block_context(node):
        return ParadoxBlockContext

    @staticmethod
    def get_node_context(node):
        return ParadoxNodeContext
            
class ParadoxFileContext:
    @staticmethod
    def get_actions(app_controller, file):
        return [
            Action("Remove Comments", 
                   lambda:app_controller.request_bulk_mutation.emit(
                       BulkMutationRequest(target=file, action=clear_comments)
                   ),
                   True
            ),
            Action("Remove Whitespace", 
                   lambda:app_controller.request_bulk_mutation.emit(
                       BulkMutationRequest(target=file, action=clear_whitespace)
                   ),
                   True
            )
        ]

class ParadoxBlockContext:
    @staticmethod
    def get_actions(app_controller, block_context):
        return
    
class ParadoxNodeContext:
    @staticmethod
    def get_actions(app_controller, block_context):
        return [
            Action("Add Comment", 
                   lambda:app_controller.request_block_mutation.emit(
                       BlockMutationRequest.add(block_context.parent, block_context.parent_index, comment_node)
                   ), 
                   True
            )
        ]

class LocalisationContext:
    @staticmethod
    def get_actions():
        return []
    
class GFXContext:
    @staticmethod
    def get_actions():
        return []