from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.shortcuts import render, redirect, reverse
from django.utils.decorators import method_decorator
from django.views import View

from webapp.forms import ProfileForm, UserForm
from webapp.models import Table, TablePlayer
import traceback


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
    
    @transaction.atomic
    def post(self, request):
        user_form = UserForm(request.POST, instance=request.user)
        profile_form = ProfileForm(request.POST, instance=request.user.profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('/')
            
        else:
            return render(request, 'profile.html', {
                'user_form': user_form,
                'profile_form': profile_form
            })

@method_decorator(login_required, name='dispatch') 
class Index(View):
    def get(self, request):
        error = request.GET.get("error")
        if(request.user.profile.wallet_value>=25):
            tables = Table.objects.filter(min_bet__lte=request.user.profile.wallet_value/5, player_count__lt=6)
        else:
            tables = None    
        return render(request, 'index.html', {'tables': tables, 'error': error})

@method_decorator(login_required, name='dispatch') 
class BJTable(View):
    def get(self, request, table_id):
        current_table = Table.objects.filter(id=table_id)
        if(current_table.count()==0):
            error_message = "Unable to join table. Table doesn't exists!!"
            return redirect(reverse('index') + '?error=' + error_message)
        else:
            current_table = current_table[0]
            if(TablePlayer.objects.filter(table_id=current_table, user_id=request.user).count()==0):
                return redirect('/table/'+ str(current_table.id) + '/join/')
            
            table_players = TablePlayer.objects.filter(table_id=current_table)
            return render(request, 'table.html', {'table': current_table, 
                                                  'table_players': table_players,
                                                  'error': None})
             
    
@method_decorator(login_required, name='dispatch')
class TableJoin(View):
    @transaction.atomic
    def get(self, request, table_id):
        current_table = Table.objects.filter(id=table_id)
        if(current_table.count()==0):
            error_message = "Unable to join table. Table doesn't exists!!"
            return redirect(reverse('index') + '?error=' + error_message)
        else:
            current_table = current_table[0]
            if(TablePlayer.objects.filter(table_id=current_table, user_id=request.user).count()!=0):
                return redirect('/table/'+ str(current_table.id) + '/')
            elif current_table.player_count>=6:
                error_message = "Unable to join table. Table is full!!"
                return redirect(reverse('index') + '?error=' + error_message)
            else:
                try:
                    obj = TablePlayer.objects.create(table_id=current_table, user_id=request.user)
                    current_table.player_count = current_table.player_count + 1
                    current_table.save()
                except Exception:
                    traceback.print_exc()
                    error_message = "Unable to join table. Error while joining table!!"
                    return redirect(reverse('index') + '?error=' + error_message)
                
            return redirect('/table/'+ str(current_table.id) + '/')

@method_decorator(login_required, name='dispatch')
class TableUnJoin(View):
    @transaction.atomic
    def get(self, request, table_id):
        current_table = Table.objects.filter(id=table_id)
        if(current_table.count()==0):
            error_message = "Unable to unjoin table. Table doesn't exists!!"
            return redirect(reverse('index') + '?error=' + error_message)
        else:
            current_table = current_table[0]
            obj = TablePlayer.objects.filter(table_id=current_table, user_id=request.user)
            if(obj.count()==0):
                error_message = "Invalid Request. User not on table!!"
            else:
                try:
                    obj.delete()
                    current_table.player_count = current_table.player_count - 1
                    current_table.save()
                    error_message = ''
                except Exception:
                    traceback.print_exc()
                    error_message = "Unable to unjoin table. Error while unjoining table!!"
                
            return redirect(reverse('index') + '?error=' + error_message)
