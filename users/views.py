from users.models import User, Device
from users.forms import RegisterForm
from django.shortcuts import render, HttpResponseRedirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
import json, urllib2
API_KEY = "avi661w6tdox8ip"

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
            device = Device(user=user, device_id=device['device'], device_name="Change me!")
            device.save()
            print "added to user"
        else: 
            print "Device already exists"
    
@login_required            
def home(request):
    return render(request, 'users/home.html')
