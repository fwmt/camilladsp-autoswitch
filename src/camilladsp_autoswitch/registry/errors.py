class ProfileRegistryError(Exception):
    """Base error for profile registry."""


class InvalidYamlError(ProfileRegistryError):
    """Raised when a YAML file is invalid."""


class ProfileAlreadyExistsError(ProfileRegistryError):
    """Raised when attempting to overwrite a profile without force."""


class ProfileNotFoundError(ProfileRegistryError):
    """Raised when a requested profile does not exist."""
