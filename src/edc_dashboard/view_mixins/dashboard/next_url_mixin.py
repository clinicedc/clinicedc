from .base import Base

from ...next_url_mixin import NextUrlMixin as NextUrlMixinBase


class NextUrlMixin(Base, NextUrlMixinBase):

    next_url_name = 'dashboard_url'
