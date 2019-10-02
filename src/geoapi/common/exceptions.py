"""Custom Exceptions
"""

class ResourceNotFoundError(Exception):
    """An API resource is not found in the database
    """


class ResourceMissingDataError(Exception):
    """An API resource does not have required data
    """
