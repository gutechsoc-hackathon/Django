from django.conf.urls import patterns, include, url
from django.conf import settings

urlpatterns = patterns('',
        
)

# Service MEDIA from here if in DEBUG mode.
if settings.DEBUG:
    urlpatterns += patterns(
        'django.views.static',
        (r'media/(?P<path>.*)', 'serve', {'document_root': settings.MEDIA_ROOT}))
    
