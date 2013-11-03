from django.conf.urls import patterns, include, url

from users import views

urlpatterns = patterns('',
                       url(r'^register/$', views.register, name='register'),
                       url(r'^login/$', 'django.contrib.auth.views.login', {'template_name':'users/login.html', 'extra_context':{'next':'/'}}, name='login'),
                       url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page':'/'}, name='logout'),
                       url(r'^associate/$', views.associate, name='associate'),
                       url(r'^associate-response/$', views.associate_callback, name='associate-response'),
                       url(r'^home/$', views.home, name='home'),
                       url(r'^devices/$', views.devices, name='devices'),
                       url(r'^device/$', views.device_by_id, name='devices_by_id'),
                       url(r'^profile/$', views.profile, name='profile'),
)
