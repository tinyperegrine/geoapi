class ResourceNotFoundError(Exception):
    """An API resource is not found in the database
    """
    pass


class ResourceMissingDataError(Exception):
    """An API resource does not have required data
    """
    pass
