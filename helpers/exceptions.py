class RentError(Exception):
    """Raised when there is an error renting an email"""


class GetCodeError(Exception):
    """Raised when there is an error getting a code"""


class TaskCreateError(Exception):
    """Raised when a task fails to create"""


class SolvingError(Exception):
    """Raised when a captcha fails to solve"""


class JsInstrumentationError(Exception):
    """Raised when getting js instrumentation fails"""
