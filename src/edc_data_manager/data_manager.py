from .handlers import DoNothingHandler, QueryRuleHandler
from .site_data_manager import site_data_manager

site_data_manager._register(DoNothingHandler)
site_data_manager._register(QueryRuleHandler)
