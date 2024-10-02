class InvalidInterfaceError(Exception):
    pass


class EmptyInterfaceError(InvalidInterfaceError):
    pass


class NotAFileError(Exception):
    pass


class MissingFileError(Exception):
    pass


class InvalidInputOutputsError(Exception):
    pass


class InvalidCLIError(Exception):
    pass


class FunctionNotFoundError(Exception):
    pass


class ExistingRegisteredFunctionError(Exception):
    pass
