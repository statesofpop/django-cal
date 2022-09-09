import datetime

from dateutil.rrule import YEARLY, rrule, rruleset
from django.test import RequestFactory

from django_cal.views import Events


class Testevents(Events):
    def items(self):
        return ["Whattaday!", "meow"]

    def cal_name(self):
        return "a pretty calendar."

    def cal_desc(self):
        return "Lorem ipsum tralalala."

    def item_summary(self, item):
        return "That was suchaday!"

    def item_start(self, item):
        return datetime.date(year=2011, month=1, day=24)

    def item_end(self, item):
        return datetime.date(year=2011, month=1, day=26)

    def item_rruleset(self, item):
        set = rruleset()
        set.rrule(rrule(freq=YEARLY, count=10, dtstart=self.item_start(item)))
        return set

    def item_categories(self, item):
        return ["Family", "Birthdays"]


def test_for_smoke():
    """
    Very basic test, just test that we get an ical file.
    """
    request = RequestFactory().get("/cal")
    response = Testevents()(request)
    assert response.status_code == 200
    assert b"VCALENDAR" in response.content
