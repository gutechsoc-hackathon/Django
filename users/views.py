from users.models import User
from users.forms import RegisterForm
from django.shortcuts import render, HttpResponseRedirect
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate

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
        return render(request, 'users/register.html')
    else:
        return HttpResponseRedirect('/user/associate/')
    
