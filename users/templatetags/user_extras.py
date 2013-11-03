from django import template
from datetime import datetime
import datetime as dt

register = template.Library()

@register.filter
def get_dev_name(notification):
	print notification
	return notification.device.device_name

@register.filter
def get_app_name(notification):
	return notification.session.dev_app.appname

@register.filter
def get_item(dictionary, key):
	print dictionary, key
	return dictionary.get(key)
	
@register.filter
def get_notification_timespent(notification):
	return convert_duration(notification.session.time_spent)

@register.filter
def get_timespent(dict, key):
    return "%d seconds" % (get_item(dict,key)/1000.0)

@register.filter
def get_timestamp(dict, key):
    return datetime.fromtimestamp(get_item(dict,key)/1000.0)
 
@register.filter
def convert_date(ms):
    return datetime.fromtimestamp(ms/1000.0)

@register.filter
def convert_duration(ms):
	s=ms/1000
	m,s=divmod(s,60)
	h,m=divmod(m,60)
	d,h=divmod(h,24)
	return '%d hours %d minutes %d seconds' % (h, m, s)

@register.filter
def get_time_today(dict):
	sessions = get_item(dict, 'sessions')


@register.filter
def get_sessions(application):
	return application.session_set.all()

