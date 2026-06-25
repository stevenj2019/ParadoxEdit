from gui.util import get_main_window
from gui.dialogues.file_dialogue import select_mod_file
from gui.dialogues.warning_messages import could_not_load_mod_critical
from gui.menus.top_bar.sub_windows.settings import SettingsWindow

from ModClasses import ParadoxMod
from gui.menus import ActionGroup, Action

def build_topbar_actions(toolbar):
    """
    Returns structured actions for the toolbar.
    """

    def open_mod():
        config = get_main_window().config
        mod_path = select_mod_file(config=config)

        try:
            mod = ParadoxMod(mod_path)
        except Exception as e:
            could_not_load_mod_critical(e)
            return

        toolbar.mod_loaded_signal.emit(mod)

    def open_settings():
        settings = SettingsWindow(
            "PDXEdit Settings",
            get_main_window().config
        )
        settings.exec_()

    return [
        ActionGroup("File", [
            Action("Open Mod", open_mod, True), 
            Action("Save Open", toolbar.save_open_signal.emit, False),
            Action("Save All Changed", toolbar.save_all_changed_signal.emit, False),
            Action("Save All", toolbar.save_all_signal.emit, False)
        ]),
        Action("Settings", open_settings, True)
    ]