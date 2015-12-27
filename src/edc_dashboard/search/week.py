from datetime import date, timedelta


class Week(object):

    def boundaries(self, year, week):
        """http://bytes.com/topic/python/answers/499819-getting-start-end-dates-given-week-number"""
        startOfYear = date(year, 1, 1)
        now = startOfYear + timedelta(weeks=week)
        sun = now - timedelta(days=now.isoweekday() % 7)
        sat = sun + timedelta(days=6)

        return sun, sat
