class Platform():
    def __init__(self, name, views):
        self.name = name
        self.views = views


class Element():
    def __init__(self, name, type):
        self.name = name
        self.type = type
        self.is_extra = False
        self.params = {}
