from ParadoxParser import ParadoxLocParser as PDXFile
from ParadoxParser.ParadoxNodes import GenericBlock, GenericString, GenericKeyValue, GenericComment
from PyQt5.QtWidgets import QMainWindow

immediate_log_string = "\"[GetDateText]: [ROOT.id] has received the event {}\""
options_log_string =  "\"[GetDateText]: [ROOT.id] has chosen the option {}\""

def event_log_injection(parent: QMainWindow, file:PDXFile):
    file.file_saved = False
    parent.been_modified = True

    event_nodes = [node for node in file.nodes if isinstance(node, GenericBlock)]
    for event_block in event_nodes:
        immediate_log = False
        event_id_value = next(
            child.value.value
            for child in event_block
            if isinstance(child, GenericKeyValue) and child.key == "id"
        )
        log_string = immediate_log_string.format(event_id_value)

        immediate_block = next((child for child in event_block.children if child.key == "immediate"), None)
        if not immediate_block:
            immediate_block = GenericBlock("immediate")
            insert_index = next(i for i, c in enumerate(event_block.children) if c.key == "option"), len(event_block.children)
            event_block.children.insert(insert_index, immediate_block)

        immediate_block_logs = [child for child in immediate_block.children if child.key == "log"]
        for log in immediate_block_logs:
            if log.value.value == log_string:
                immediate_log = True
                break

        if not immediate_log:
            immediate_block.children.insert(0, GenericKeyValue("log", GenericString(log_string)))

        option_blocks = filter(lambda c: c.key == "option", event_block.children) #gets option = { } from the event
        for option_block in option_blocks:                                        #iters them
            option_log = False                                                    #sets false flag
            # for node in option_block.children:                                    #iters through the keyvalues dont think this is needed
            option_keys = [child.key for child in option_block.children if getattr(child, "key", None)] #gets list of event keys
            option_id_index = option_keys.index("name")                       #gets index of name
            option_id = option_block.children[option_id_index].value.value
            log_string = options_log_string.format(option_id)

            for c_node in option_block.children:
                if isinstance(c_node, GenericKeyValue):
                    if c_node.key == "log" and c_node.value.value == log_string:
                        option_log = True

            if not option_log:
                option_block.children.insert(option_id_index + 1, GenericKeyValue("log", GenericString(log_string)))