from PyQt5.Qt import QMenu
from PyQt5.QtGui import QCursor
from traverse import apply_to_target
from gui.warning_messages import toggle_safe_mode_warning
from gui.util import get_safe_mode_opposed_text
from ParadoxParser import ParadoxScriptParser as PDXScript
def global_options(parent, menu):
    menu.addSection("Editor")
    menu.addAction(f"{get_safe_mode_opposed_text(parent)} Safe Mode", lambda:toggle_safe_mode_warning(parent))
    
def build_context_menu(parent, selected):
    menu = QMenu(parent)
    global_options(parent, menu)
    if not isinstance(selected, PDXScript):
        sections = selected.context_sections()
        for section_name, actions in sections.items():
            menu.addSection(section_name)
            for action in actions:
                menu.addAction(
                    action.text,
                    lambda checked=False, a=action:
                    apply_to_target(a.callback, parent, selected)
                )
    else:
        
    menu.exec_(QCursor.pos())