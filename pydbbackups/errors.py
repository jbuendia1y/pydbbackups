class MethodNotImplemented(Exception):
    """ Raised when a one method not implemented is called """

    def __init__(self, name: str = None) -> None:
        message = ""
        if not name:
            message += "Method"
        else:
            message += f"{name} method"

        super().__init__(f"{message} not implemented")


class CommandNotFound(Exception):
    """ Raised when python not found a command """

    def __init__(self, name: str) -> None:
        super().__init__(f'{name} command was not found')
