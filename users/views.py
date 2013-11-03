from users.models import User, Device, Application, Session
from users.forms import RegisterForm
from django.shortcuts import render, HttpResponseRedirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
import json, urllib2
from datetime import datetime, timedelta
from api import API_KEY


def register(request):
    if request.method == 'GET':
        form = RegisterForm()
        return render(request, 'users/register.html', {'form':form, 'valid':True})
    elif request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            user = User(email=data['email'],
                        first_name=data['first_name'],
                        last_name=data['last_name'],
                        is_staff=False, is_active=True, is_superuser=False,
                        last_login=timezone.now(), date_joined=timezone.now())
            user.set_password(data['password'])
            user.save()

            user.backend='django.contrib.auth.backends.ModelBackend' 
            login(request, user)
            return HttpResponseRedirect('/user/associate/')
        else:
            return render(request, 'users/register.html', {'form':form, 'valid':False})

@login_required
def associate(request):
    return render(request, 'users/associate.html')

@login_required
def associate_callback(request):
    if 'user_id' in request.GET:
        print request.GET
        user = request.user
        print user
        user.app_tracker_id = request.GET['user_id']
        user.save()
        retrieve_devices(user)
        return HttpResponseRedirect('/user/home')
    else:
        return HttpResponseRedirect('/user/associate/')

def retrieve_devices(user):
    url = 'https://tethys.dcs.gla.ac.uk/AppTracker/api/v2/devices?key=%s&user_id=%s' % (API_KEY, user.app_tracker_id)
    devices = json.load(urllib2.urlopen(url))
    user_devices = user.device_set.all()
    
    print "Devices:"
    for device in devices:
        print device['device'],
        if not user_devices.filter(device_id=device['device']):
            device = Device(owner=user, device_id=device['device'], 
                            device_name='Change me!', user='Who uses me?', 
                            device_type='NA')
            device.save()
         
            print "added to user"
        else: 
            print "Device already exists"
   
@login_required            
def home(request):
    return render(request, 'users/home.html')

@login_required
def devices(request):
    devices = request.user.device_set.all()
    retrieve_device_usageDB(devices[0])
    return render(request, 'devices/devices.html', {'devices':devices})

@login_required
def device_by_id(request):
    if 'id' not in request.GET:
        print "no device id"
        return HttpResponseRedirect('/user/devices')
    device = request.user.device_set.filter(device_id=request.GET['id'])
    if len(device) == 0:
        print "Couldn't find device"
        return HttpResponseRedirect('/user/devices')

    applications = device[0].application_set.all()

    print applications
    return render(request, 'devices/device.html', {'device_name':device[0].device_name,
                                                   'applications':applications})

def retrieve_device_usage(device):
    #IMEI:353918057929438 2013-11-22+02:00
    t_now = datetime.now()
    end = t_now.strftime("%Y-%m-%d+%H:%M")
    print "Last check:", device.last_checked
    print "Time now:",  end
    print device.applications
    for app in device.applications.keys():
        print "this device already has", len(device.applications[app]['sessions']), app, "sessions"
    if device.last_checked == end:

      print "No time elapsed since last check"
      return
    device.last_checked = end
    start =  (t_now - timedelta(minutes=60)).strftime("%Y-%m-%d+%H:%M")
    print "Checking usage for time:", start, "until", end
    url = 'https://tethys.dcs.gla.ac.uk/AppTracker/api/v2/log?key=%s&device=%s&from=%s&to=%s' % (API_KEY, device.device_id, 
                                                                                                 start, end)
    print url
    sessions = json.load(urllib2.urlopen(url))
    #print sessions
    print "There are :", len(sessions), "new sessions"
    for app in device.applications.keys():
        print "this device already has", len(device.applications[app]['sessions']), app, "sessions"

    for session in sessions:
        if session["app"] not in device.applications:
            device.applications[session['app']] = {'total': session['timespent'], 
                                                   'sessions':[{'startTime':session['timestamp'],
                                                               'timeSpent':session['timespent'],
                                                               }],
                                                    }
            print "Added something new"
        else:
            device.applications[session['app']]['total'] += session['timespent']
            device.applications[session['app']]['sessions'] += [{'startTime':session['timestamp'],
                                                               'timeSpent':session['timespent'],
                                                               }]
            print "added something old"
    device.save()

# applications = {'facebook':{'total':23232323232, 'sessions':[ {'startTime':23232322323,'length':223232}, {'startTime':23232322323,'length':223232}],
#                 'snapchat':{'total':23232323232, 'sessions':[ {'startTime':23232322323,'length':223232}, {'startTime':23232322323,'length':223232}],
#                 }


def retrieve_device_usageDB(device):
    #IMEI:353918057929438 2013-11-22+02:00
    t_now = datetime.now()
    end = t_now.strftime("%Y-%m-%d+%H:%M")
    print "Last check:", device.last_checked
    print "Time now:",  end
    deviceApps = device.application_set.all()
    for app in deviceApps:
        print "this device already has", app.session_set.all(), app.appname, "sessions"

    if device.last_checked == end:

      print "No time elapsed since last check"
      return
    device.last_checked = end
    start =  (t_now - timedelta(minutes=5)).strftime("%Y-%m-%d+%H:%M")
    print "Checking usage for time:", start, "until", end
    url = 'https://tethys.dcs.gla.ac.uk/AppTracker/api/v2/log?key=%s&device=%s&from=%s&to=%s' % (API_KEY, device.device_id, 
                                                                                                 start, end)
    print url
    sessions = json.load(urllib2.urlopen(url))
    #print sessions
    print "There are :", len(sessions), "new sessions"

    for session in sessions:
        print session['app']
        print deviceApps
        app = deviceApps.filter(appname=session["app"])
        print app
        if len(app) == 0:
            app = Application(device=device, appname=session['app'], total_time=session['timespent'])
            app.save()
            sesh = Session(dev_app=app, time_spent=session['timespent'], time_stamp=session['timestamp'])
            print app.appname
            print "Added something new"
        else:
            app = app[0]
            sesh = Session(dev_app=app, time_spent=session['timespent'], time_stamp=session['timestamp'])
            app.total_time += session['timespent']
            app.save()
            print "added something old"
        
        sesh.save()
    device.save()
