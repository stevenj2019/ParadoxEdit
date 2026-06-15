from ModClasses.ParadoxCategory import GenericCategory
from ModClasses.ParadoxCategoryItem import GenericCategoryItem
from gui.warning_messages import bulk_operation_warning

def iter_files(target):
    if isinstance(target, GenericCategoryItem):
        yield target
    elif isinstance(target, GenericCategory):
        for item in target.files.values():
            yield item
    else:
        raise TypeError(f"Cannot iterate from {type(target).__name__}")
    
def apply_to_target(action, parent, target):
    if bulk_operation_warning(parent):
        for file in iter_files(target):
            file.has_been_modified = True
            action(file.obj)
            parent.right_panel.load_block(file.obj)
            
