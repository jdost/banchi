class FullVlanException(Exception):
    def __init__(self, *msg):
        self.message = msg[0].format(*msg[1:]) if len(msg) > 1 else msg[0]

    def __str__(self):
        return self.message


class MissingValuesException(Exception):
    pass
