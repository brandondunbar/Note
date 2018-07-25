class Note:
    def __init__(self, **kwargs):
        self.name = kwargs.get("name", "name")
        self.body = kwargs.get("body", "body")

    def __repr__(self): return self.name