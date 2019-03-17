import json
import traceback

from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.db import transaction
from django.http import HttpResponse
from django.shortcuts import render, redirect, reverse
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.views import View

from webapp.forms import ProfileForm, UserForm
from webapp.models import Table, TablePlayer, Round, RoundPlayer


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
            active_round = Round.objects.filter(table=current_table, round_status=1)
            if active_round.count()!=0:
                active_round = active_round[0]
                round_players = RoundPlayer.objects.filter(round=active_round).order_by('player_order')
            else:
                active_round = None
                round_players = None
            return render(request, 'table.html', {'table': current_table, 
                                                  'table_players': table_players,
                                                  'active_round': active_round,
                                                  'round_players': round_players,
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
        
@method_decorator(login_required, name='dispatch')
class RoundStart(View):
    @transaction.atomic
    def post(self, request, table_id):
        bet_value = json.loads(request.POST.get("bet_value"))
        current_table = Table.objects.filter(id=table_id)
        if(current_table.count()==0):
            error_message = "Unable to start table. Table doesn't exists!!"
            return redirect(reverse('index') + '?error=' + error_message)
        else:
            try:
                current_table = current_table[0]
                current_table.table_status=1
                current_table.save()
                table_players = TablePlayer.objects.filter(table_id=current_table)
                round_obj = Round.objects.create(table=current_table, player_count=current_table.player_count, round_status =1)
                order = 1
                round_players = []
                for table_player in table_players:
                    if (table_player.user_id.profile.wallet_value - float(bet_value.get(table_player.user_id.username, 0))>=0):
                        round_player = RoundPlayer.objects.create(round=round_obj, player=table_player.user_id, player_order=order, player_bet=float(bet_value.get(table_player.user_id.username, 0)))
                        round_players.append(round_player)
                        table_player.user_id.profile.wallet_value = table_player.user_id.profile.wallet_value - float(bet_value.get(table_player.user_id.username, 0)) 
                        table_player.user_id.save()
                        table_player.player_type=1
                        table_player.save()
                        order = order + 1
                
                updated_player_html = render_to_string('current_players.html', {"table_players": table_players, "table": current_table})
                updated_round_html = render_to_string('round_players.html', {"round_players": round_players, "active_round": round_obj})
                response_data = {"status": "Success", 
                                 "player_html": updated_player_html, 
                                 "round_html": updated_round_html,
                                 "http_status_code": 200}
            except Exception:
                traceback.print_exc() 
                response_data = {"status": "Failure", "http_status_code": 500}    
                
            return HttpResponse(json.dumps(response_data), status=response_data["http_status_code"])
