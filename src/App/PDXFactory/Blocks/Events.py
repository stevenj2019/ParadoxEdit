from ParadoxParser.ParadoxNodes import GenericBlock, GenericKeyValue, GenericToken, GenericBool, GenericComment
###          ###
#  ROOT LEVEL  #
###          ###
def add_namespace_keyval(namespace_id=None):
    namespace_id = namespace_id if namespace_id else "namespace_here"
    return GenericKeyValue("add_namespace", GenericToken(namespace_id))

def country_event_block(event_id=None):
    event_id = event_id if event_id else None
    return GenericBlock("country_event",[
                            *event_essentials(event_id),
                            immediate_block(),
                            option_block(event_id)
                        ])

def news_event_block(event_id=None):
    event_id = event_id if event_id else None
    return GenericBlock("news_event",[
                            *event_essentials(event_id),
                            immediate_block(),
                            option_block(event_id)
                        ])

def event_essentials(event_id=None):
    event_id = event_id if event_id else "namespace_here.1"
    return [
        GenericKeyValue("id", GenericToken(event_id)),
        GenericKeyValue("title", GenericToken(f"{event_id}.t")),
        GenericKeyValue("description", GenericToken(f"{event_id}.d")),
        GenericKeyValue("picture", GenericToken(f"GFX_{event_id}_1")),
        GenericKeyValue("fire_only_once", GenericBool(False)),
        GenericKeyValue("is_triggered_only", GenericBool(False)),
    ]
###            ###
#  EVENT BLOCKS  #
###            ###
def immediate_block():
    return GenericBlock("immediate",[
        GenericComment("##YOUR CODE HERE")
    ])

def option_block(option_name=None):
    option_name = option_name if option_name else "option_name_here.a"
    return GenericBlock("option", [
        GenericKeyValue("name", GenericToken(option_name)),
        GenericComment("##YOUR CODE HERE")
    ])