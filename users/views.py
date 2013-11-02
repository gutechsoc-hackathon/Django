from users.models import User
from users.forms import RegisterForm
from django.shortcuts import render, HttpResponseRedirect
from django.utils import timezone

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
            return HttpResponseRedirect('/')
        else:
            return render(request, 'users/register.html', {'form':form, 'valid':False})        
    
