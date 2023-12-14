"""Exceptions for AQMAN101 from RadonFTLabs"""


class PubAirError(Exception):
    """Generic Aqman Exception"""

    pass


class APIConnectionError(PubAirError):
    """Aqman connection Exception"""

    pass
