from django import template
from datetime import datetime

register = template.Library()

@register.filter
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_timespent(dict, key):
    return "%d seconds" % (get_item(dict,key)/1000.0)

@register.filter
def get_sessions(application):
	return application.session_set.all()