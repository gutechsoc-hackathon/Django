from django.conf.urls import patterns, include, url

from users import views

urlpatterns = patterns('',
                       url(r'^register/$', views.register, name='register'),
                       url(r'^login/$', 'django.contrib.auth.views.login', {'template_name':'users/login.html', 'extra_context':{'next':'/'}}, name='login'),
                       url(r'^logout/$', 'django.contrib.auth.views.logout', {'next_page':'/'}, name='logout'),
                       url(r'^associate/$', views.associate, name='associate'),
                       url(r'^associate-response/$', views.associate_callback, name='associate-response'),
                       url(r'^home/$', views.home, name='home'),
url(r'^devs/$', views.retrieve_devices, name='retrieve_devices'),
)
