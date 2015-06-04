Preparing your app to use search
================================

There are three base search classes. Each needs to be configured in the local 
study-specific EDC app (e.g *mpepu*, *maikaelelo*, *cancer*, ...) so that the
class knows which models to use for search. The best models to use for search are 
the consent models or models with a foreign key to :class:`RegisteredSubject`.

Word
----

In **mpepu**, the :class:`SearchByWord` is subclasses locally as follows
and saved under :mod:`mpepu.classes` in the file :file:`search_by_word.py`::

    from bhp_search.classes import BaseSearchByWord
    from mpepu_maternal.models import MaternalConsent
    from mpepu_infant.models import InfantBirth
    
    
    class SearchByWord(BaseSearchByWord):
        
        def __init__(self, request, **kwargs):
            
            super(SearchByWord, self).__init__(request, **kwargs)
            self.search_model.update({ 
                  'maternalconsent': MaternalConsent, 
                  'infantbirth': InfantBirth})
                  
As you see, the search models are :class:`MaternalConsent`  and :class:`InfantBirth`.

Date
----                


In **mpepu**, the :class:`SearchByDate` is subclasses locally as follows
and saved under :mod:`mpepu.classes` in the file :file:`search_by_date.py`:: 

    from bhp_search.classes import BaseSearchByDate
    from mpepu_maternal.models import MaternalConsent
    from mpepu_infant.models import InfantBirth
    
    
    class SearchByDate(BaseSearchByDate):
        
        def __init__(self, request, **kwargs):
            
            super(SearchByDate, self).__init__(request, **kwargs)
            self.search_model.update({ 
                  'maternalconsent': MaternalConsent, 
                  'infantbirth': InfantBirth})
                  
Week
----                

In **mpepu**, the :class:`SearchByWeek` is subclasses locally as follows
and saved under :mod:`mpepu.classes` in the file :file:`search_by_week.py`:: 

    from bhp_search.classes import BaseSearchByWeek
    from mpepu_maternal.models import MaternalConsent
    from mpepu_infant.models import InfantBirth
    
    
    class SearchByWeek(BaseSearchByWeek):
        
        def __init__(self, request, **kwargs):
            
            super(SearchByDate, self).__init__(request, **kwargs)
            self.search_model.update({ 
                  'maternalconsent': MaternalConsent, 
                  'infantbirth': InfantBirth})    
                  
                                