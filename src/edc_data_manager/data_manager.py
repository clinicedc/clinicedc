from .handlers import QueryRuleHandler, DoNothingHandler
from .site_data_manager import site_data_manager

site_data_manager.register(DoNothingHandler)
site_data_manager.register(QueryRuleHandler)
