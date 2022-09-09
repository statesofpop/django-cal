import datetime

import dateutil.rrule as rrule

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
        rruleset = rrule.rruleset()
        rruleset.rrule(rrule.YEARLY, count=10, dtstart=self.item_start(item))
        return rruleset

    def item_categories(self, item):
        return ["Family", "Birthdays"]
