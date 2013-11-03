from users.models import User, Device, Application, Session, Notification
from users.forms import RegisterForm
from django.shortcuts import render, HttpResponseRedirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
import json, urllib2
from datetime import datetime, timedelta
from api import API_KEY
from notification_sender import sendmail

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
    return render(request, 'users/associate.html', {'api_key':API_KEY})

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
                            device_name=device['device'], user='Someone', 
                            device_type='NA')
            device.save()
            retrieve_device_usageDB(device, True)
            print "added to user"
        else: 
            print "Device already exists"
   
@login_required            
def home(request):
    devices = request.user.device_set.all()
    notification_list = []
    for device in devices:
        n = get_notifications(device)
        for notification in n:
            added = False
            if len(notification_list) == 0:
                notification_list = [notification]
            for x in range(len(notification_list)):
                if notification.time_stamp > notification_list[x].time_stamp:
                    notification_list = notification_list[:x] + [notification] + notification_list[x:]  
                    added = True
                    break
            if not added:
                notification_list += [notification]
    return render(request, 'users/home.html', {'notifications':notification_list})

@login_required
def devices(request):
    devices = request.user.device_set.all()
    notification_list= []

    for device in devices:
        retrieve_device_usageDB(device, False)
        n = get_notifications(device)
        for notification in n:
            added = False
            if len(notification_list) == 0:
                print "first item"
                notification_list = [notification]
            for x in range(len(notification_list)):
                if notification.time_stamp > notification_list[x]:
                    print "added"
                    notification_list = notification_list[:x] + [notification] + notification_list[x:]  
                    added = True
                    break
            if not added:
                print "blab"
                notification_list += [notification]

    print "notifications: ", notification_list
    return render(request, 'devices/devices.html', {'devices':devices, 
                                                    'notifications':notification_list})

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
    appSessions = {}
    for app in applications:
        appSessions[app.appname] = {}
        appSessions[app.appname]['sessions'] = app.session_set.all()
        appSessions[app.appname]['total_time'] = app.total_time

    notification_list = []
    n = get_notifications(device[0])
    for notification in n:
        added = False
        if len(notification_list) == 0:
            print "first item"
            notification_list = [notification]
        for x in range(len(notification_list)):
            if notification.time_stamp > notification_list[x]:
                print "added"
                notification_list = notification_list[:x] + [notification] + notification_list[x:]  
                added = True
                break
        if not added:
            print "blab"
            notification_list += [notification]

    print appSessions
    return render(request, 'devices/device.html', {'device':device[0], 
                                                   'appSessions':appSessions, 
                                                   'notifications':notification_list})

def retrieve_device_usageDB(device, massive):
    #IMEI:353918057929438 2013-11-22+02:00
    t_now = datetime.now()
    end = t_now.strftime("%Y-%m-%d+%H:%M")
    print "Last check:", device.last_checked
    print "Time now:",  end
    deviceApps = device.application_set.all()
    for app in deviceApps:
        print "this device already has", app.session_set.all(), app.appname, "sessions"
    print "===================== notifications"
    get_notifications(device)
    if device.last_checked == end:
      print "No time elapsed since last check"
      return

    device.last_checked = end
    if massive:
        start =  (t_now - timedelta(days=30)).strftime("%Y-%m-%d+%H:%M")
    else:
        start =  (t_now - timedelta(minutes=5)).strftime("%Y-%m-%d+%H:%M")

    print "Checking usage for time:", start, "until", end
    url = 'https://tethys.dcs.gla.ac.uk/AppTracker/api/v2/log?key=%s&device=%s&from=%s&to=%s' % (API_KEY, device.device_id, 
                                                                                                 start, end)
    print url
    sessions = json.load(urllib2.urlopen(url))
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
        else:
            app = app[0]
            sesh = Session(dev_app=app, time_spent=session['timespent'], time_stamp=session['timestamp'])
            app.total_time += session['timespent']
            app.save()
            
        sesh.save()
        if not massive and ((sesh.time_spent / 1000) > 1):
            print "added a notification"
            notification = Notification(device=device,session=sesh, time_stamp=sesh.time_stamp)
            notification.save()
            sendmail("Appage", "You have a new notification", device.owner.email)
    device.save()
    
@login_required 
def profile(request):
    return render(request, 'users/profile.html', {'user': request.user })

def get_notifications(device):
    return device.notification_set.all()

@login_required
def change_device_name(request):
    if request.method == 'POST':
        device = request.user.device_set.filter(device_id=request.POST['id'])[0]
        device.device_name = request.POST['name']
        device.user = request.POST['username']
        device.save()
    return HttpResponseRedirect(('/user/device?id=%s' % device.device_id))

