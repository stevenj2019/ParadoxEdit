from .mod_panel import connect_mod_panel_events
from .contents_panel import connect_content_panel_events

def connect_main_events(main_window):
    connect_mod_panel_events(main_window)
    connect_content_panel_events(main_window)