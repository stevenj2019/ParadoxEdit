from __future__ import annotations

from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from App import AppController
    from App.Loading.Models import FileReference

from App.Contexts import BlockContext
from App.Contexts.Base import (
    GFXFieldContext,
    LocalisationFieldContext,
    ParadoxBlockContext,
    ParadoxContext,
    ParadoxFileContext,
    ParadoxNodeContext,
)
from App.Contracts import BlockMutationRequest
from App.GUI.Actions import Action, ActionsResult
from App.PDXFactory.Blocks import Events
from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue, GenericNode

def dummy() -> None: return

class EventContext(ParadoxContext):
    @staticmethod
    def get_file_context() -> type[ParadoxFileContext]:
        return EventFileContext

    @staticmethod
    def get_block_context(node: GenericNode) -> type[ParadoxBlockContext]:
        if isinstance(node, GenericBlock):
            if node.key in ["news_event", "country_event"]:
                return EventBlockContext
            elif node.key in ["option", "immediate"]:
                return EventOptionContext
        return EventRootContext

    @staticmethod
    def get_node_context(parent_node: GenericBlock, node: GenericNode) -> type[ParadoxNodeContext]:
        if isinstance(node, GenericKeyValue):
            if node.key in ("name", "title", "desc", "text"):
                return LocalisationFieldContext
            elif node.key == "picture":
                return GFXFieldContext
        return ParadoxNodeContext


class EventFileContext(ParadoxFileContext):
    @staticmethod
    def get_actions(app_controller: AppController, file: FileReference) -> ActionsResult:
        return [
            *ParadoxFileContext.get_actions(app_controller, file),
            Action("Inject Event Logs", dummy, False),
        ]


class EventRootContext(ParadoxBlockContext):
    @staticmethod
    def get_actions(app_controller: AppController, block_context: BlockContext) -> ActionsResult:
        return [
            *ParadoxNodeContext.get_actions(app_controller, block_context),
            Action(
                "Add Namespace",
                lambda: app_controller.request_block_mutation.emit(
                    BlockMutationRequest.add(
                        block_context.parent,
                        block_context.parent_index,
                        Events.add_namespace_keyval,
                    )
                ),
                False,
            ),
            Action(
                "Add Country Event",
                lambda: app_controller.request_block_mutation.emit(
                    BlockMutationRequest.add(
                        block_context.parent, block_context.parent_index, Events.country_event_block
                    )
                ),
                False,
            ),
            Action(
                "Add News Event",
                lambda: app_controller.request_block_mutation.emit(
                    BlockMutationRequest.add(
                        block_context.parent, block_context.parent_index, Events.news_event_block
                    )
                ),
                False,
            ),
        ]


class EventBlockContext:
    @staticmethod
    def get_actions(app_controller: AppController, block_context: BlockContext) -> ActionsResult:
        from App.GUI.Forms.LocaliseKey import LocaliseEventForm

        return [
            *ParadoxNodeContext.get_actions(app_controller, block_context),
            Action(
                "Add Immediate Block",
                lambda: app_controller.request_block_mutation.emit(
                    BlockMutationRequest.add(
                        block_context.parent, block_context.parent_index, Events.immediate_block
                    )
                ),
                False,
            ),
            Action(
                "Add Option Block",
                lambda: app_controller.request_block_mutation.emit(
                    BlockMutationRequest.add(
                        block_context.parent, block_context.parent_index, Events.option_block
                    )
                ),
                False,
            ),
            Action(
                "Localise Event",
                lambda: LocaliseEventForm(app_controller, block_context.key_node),
                True,
            ),
        ]


class EventOptionContext:
    @staticmethod
    def get_actions(app_controller: AppController, block_context: BlockContext) -> ActionsResult:
        return [
            *ParadoxNodeContext.get_actions(app_controller, block_context),
            # *TriggerBlockActions.get_actions(context),
            # *EventBlockContext.get_actions(context),
        ]
