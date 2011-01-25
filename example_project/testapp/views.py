# Create your views here.
import datetime
import django_cal
from django_cal.views import Events

class Testevents(Events):
    def items(self):
        return ["Whattaday!", "meow"]

    def cal_name(self):
        return "a pretty calendar."

    def cal_desc(self):
        return "Lorem ipsum tralalala."

    def item_summary(self):
        return "That was suchaday!"

    def item_start(self):
        return datetime.date(year=2011, month=1, day=24)

    def item_end(self):
        return datetime.date(year=2011, month=1, day=26)
