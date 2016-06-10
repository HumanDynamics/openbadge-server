from django import template
from datetime import datetime
from pytz import timezone


TIME_FORMAT = "%Y-%m-%d %H:%M:%S+00:00"

register = template.Library()

#can now use function in django templates
@register.filter
def utc_to_eastern(time):
    try:
        if isinstance(time, str):
            time = datetime.strptime(time, TIME_FORMAT)
            return time.replace(tzinfo=timezone('US/Eastern'))
        else:
            return time.astimezone(timezone('US/Eastern'))
    except:
        return "Invalid time"

@register.filter
def length(obj):
    return len(obj)

@register.filter
def total_duration(meetings):
    return sum([(meeting.end_time - meeting.start_time).total_seconds()/3600 for meeting in meetings])
