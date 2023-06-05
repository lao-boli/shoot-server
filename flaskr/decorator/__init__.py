import logging
from .auth import *
__all__ = ['requires_roles']
def log_decorator(cls):
    logger = logging.getLogger(cls.__module__ + '.' + cls.__name__)
    handler = logging.StreamHandler()
    handler.setFormatter(logging.Formatter('%(name)s - %(levelname)s - %(message)s'))
    # logger.addHandler(handler)
    logger.setLevel(logging.INFO)
    cls.logger = logger
    return cls
