from ParadoxParser.ParadoxNodes import GenericComment
def comment_node(value=None):
    value = value if value else "##COMMENT HERE##"
    return GenericComment(value)