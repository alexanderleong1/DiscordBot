class Equipment:
    def __init__(self):
        self.type = None

    def __str__(self):
        return self.type

class MainHand(Equipment):
    def __init__(self):
        super().__init__()
        self.type = "Main Hand"