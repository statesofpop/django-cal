import six

import vobject
from django.db.models import ObjectDoesNotExist
from django.http import HttpResponse, Http404
from django.conf import settings

from django.contrib.syndication.views import add_domain
from django.contrib.sites.shortcuts import get_current_site


# Mapping of iCalendar event attributes to prettier names.
EVENT_ITEMS = (
    ("uid", "item_uid"),
    ("dtstart", "item_start"),
    ("dtend", "item_end"),
    ("duration", "item_duration"),
    ("summary", "item_summary"),
    ("description", "item_description"),
    ("location", "item_location"),
    ("url", "item_url"),
    ("comment", "item_comment"),
    ("last-modified", "item_last_modified"),
    ("created", "item_created"),
    ("categories", "item_categories"),
    ("rruleset", "item_rruleset"),
)


class Events(object):
    def __call__(self, request, *args, **kwargs):
        """Makes Events callable for easy use in your urls.py"""
        try:
            obj = self.get_object(request, *args, **kwargs)
        except ObjectDoesNotExist:
            raise Http404("Events object does not exist.")
        ical = self.get_ical(obj, request)
        response = HttpResponse(
            ical.serialize(),
            content_type="text/calendar;charset={}".format(settings.DEFAULT_CHARSET),
        )
        filename = self.__get_dynamic_attr("filename", obj)
        # following added for IE, see
        # http://blog.thescoop.org/archives/2007/07/31/django-ical-and-vobject/
        response["Filename"] = filename
        response["Content-Disposition"] = "attachment; filename={}".format(filename)
        return response

    def __get_dynamic_attr(self, attname, obj, default=None):
        """Returns first defined occurence of the following:
            self.$attname(obj)
            self.$attname()
            self.$attname
            default
        Taken from django.contrib.syndication.views.Feed
        """
        try:
            attr = getattr(self, attname)
        except AttributeError:
            return default
        if callable(attr):
            # Check co_argcount rather than try/excepting the function and
            # catching the TypeError, because something inside the function
            # may raise the TypeError. This technique is more accurate.
            try:
                code = six.get_function_code(attr)
            except AttributeError:
                code = six.get_function_code(attr.__call__)
            if code.co_argcount == 2:  # one argument is 'self'
                return attr(obj)
            else:
                return attr()
        return attr

    def get_ical(self, obj, request):
        """Returns a populated iCalendar instance."""
        cal = vobject.iCalendar()
        cal.add("method").value = "PUBLISH"  # IE/Outlook needs this
        items = self.__get_dynamic_attr("items", obj)
        cal_name = self.__get_dynamic_attr("cal_name", obj)
        cal_desc = self.__get_dynamic_attr("cal_desc", obj)
        # Add calendar name and description if set
        if cal_name:
            cal.add("x-wr-calname").value = cal_name
        if cal_desc:
            cal.add("x-wr-caldesc").value = cal_desc

        current_site = get_current_site(request)

        for item in items:
            event = cal.add("vevent")
            for vkey, key in EVENT_ITEMS:
                value = self.__get_dynamic_attr(key, item)
                if value:
                    if vkey == "rruleset":
                        event.rruleset = value
                    else:
                        if vkey == "url" and current_site:
                            value = add_domain(
                                current_site.domain,
                                value,
                                request.is_secure(),
                            )
                        event.add(vkey).value = value
        return cal

    # ONLY DEFAULT PARAMETERS FOLLOW #

    def get_object(self, request, *args, **kwargs):
        return None

    def item_summary(self, item):
        return item

    def item_url(self, item):
        return getattr(item, "get_absolute_url", lambda: None)()

    def filename(self, item):
        return "events.ics"
