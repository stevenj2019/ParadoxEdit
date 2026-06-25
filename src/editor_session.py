class InlineEditSession:
    def __init__(self):
        self.source = None
        self.editor = None

    def start(self, source, widget):
        self.cancel()  # replace old session
        self.source = source
        self.editor = widget

    def cancel(self):
        self.source = None
        self.editor = None

    def complete(self):
        self.source = None
        self.editor = None

    def active(self):
        return self.editor and self.source