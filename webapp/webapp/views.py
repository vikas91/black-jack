from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from django.views import View
from django.utils.decorators import method_decorator
from webapp.forms import ProfileForm, UserForm

class Register(View):
    def get(self, request):
        form = UserCreationForm()
        return render(request, 'registration/register.html', {'form': form})
    
    def post(self, request):
        form = UserCreationForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            raw_password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=raw_password)
            login(request, user)
            return redirect('/')
        
        return render(request, 'registration/register.html', {'form': form})

@method_decorator(login_required, name='dispatch')        
class Profile(View):
    def get(self, request):
        user_form = UserForm(instance=request.user)
        profile_form = ProfileForm(instance=request.user.profile)
        return render(request, 'profile.html', {
            'user_form': user_form,
            'profile_form': profile_form
        })
    
    def post(self, request):
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
        
        return render(request, 'profile.html', {
            'user_form': user_form,
            'profile_form': profile_form
        })

@login_required
def index(request):
    return render(request, 'index.html')