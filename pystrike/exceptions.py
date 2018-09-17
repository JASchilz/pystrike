"""
Exceptions for the pystrike module.
"""


class ConnectionException(Exception):
    """
    Raised when the client is unable to communicate with the indicated
    host.

    This exception could indicate that the client is unable to contact
    the indicated host, or it could indicate that the client was unable
    to send an HTTP request to the indicated host, or that the client
    was unable to receive an HTTP response from the indicated host.
    """

    pass


class ClientRequestException(Exception):
    """
    Raised when the server returns a 4xx response.

    The library code shall include the content of the error message
    from Strike, if available.
    """

    pass


class ServerErrorException(Exception):
    """
    Raised when the server returns a 5xx response.

    The library code shall include the content of the error message
    from Strike, if available.
    """

    pass


class UnexpectedResponseException(Exception):
    """
    Raised when the server returns a response that the library does not
    understand.
    """

    pass


class ChargeNotFoundException(ClientRequestException):
    """
    Raised when the server returns a 404 response.
    """

    pass
