"""Contains exceptions for the gen"""


class GuestTokenError(Exception):
    """Raised when a client fails to grab guest token"""


class FlowInitError(Exception):
    """Raised when there is an error while initiating the signup flow"""


class EmailFlowError(Exception):
    """Raised when there is an error while filling the email flow"""


class PhoneFlowError(Exception):
    """Raised when there is an error while filling the phone flow"""


class PasswordFlowError(Exception):
    """Raised when there is an error while filling the password flow"""


class AvatarFlowError(Exception):
    """Raised when there is an error while setting an avatar"""


class BioFlowError(Exception):
    """Raised when there is an error while setting a bio"""


class UsernameFlowError(Exception):
    """Raised when there is an error while setting a username"""


class PemissionFlowError(Exception):
    """Raised when there is an error while setting permissions"""


class LanguageFlowError(Exception):
    """Raised when there is an error while setting a language"""


class NotificationsFlowError(Exception):
    """Raised when there is an error while setting notifications settings"""
