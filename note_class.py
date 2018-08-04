"""A file exclusively for the Note class"""


class Note:

    def __init__(self, name, body):
        self.name = name
        self.body = body

    def __repr__(self): return self.name
