from PyQt5.QtWidgets import QFileDialog, QMessageBox

def select_and_load_mod(parent=None):
    """
    Opens a file dialog for selecting a .mod file,
    loads it into a ParadoxMod instance, and returns it.
    """
    options = QFileDialog.Options()
    options |= QFileDialog.ReadOnly
    filepath, _ = QFileDialog.getOpenFileName(
        parent,
        "Select Paradox descriptor.mod file",
        "",
        "Paradox Mod Files (*.mod);;All Files (*)",
        options=options
    )

    if not filepath:
        QMessageBox.warning(parent, "No file selected", "You did not select a mod file.")
        return None

    try:
        from ModClasses.ParadoxMod import ParadoxMod
        mod = ParadoxMod(filepath)
        return mod
    except Exception as e:
        QMessageBox.critical(parent, "Failed to load mod", f"Error: {e}")
        return None