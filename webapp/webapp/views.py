import json
import traceback
import random

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


def getCardDetails(inputCardValue):
    cardSuitMap = {
        0 : "Club",
        1 : "Diamond",
        2 : "Heart",
        3 : "Spade"
    }
    
    cardValueMap = {1: ("A", 1), 2: ("2", 2), 3: ("3", 3), 4: ("4", 4), 5: ("5", 5), 6: ("6", 6), 7: ("7",7),
                 8: ("8", 8), 9: ("9", 9), 10: ("10", 10), 11: ("J", 10), 12: ("Q", 10), 0: ("K", 10)}
    
    cardString = cardSuitMap[inputCardValue//13] + ' ' +  cardValueMap[inputCardValue%13][0]
    cardValue = cardValueMap[inputCardValue%13][1]
    return cardString, cardValue     
 
    
def dealCards(playerCount):
    cardArray = [i for i in range(1,53)]
    random.shuffle(cardArray)
    playerArray = [['', 0] for x in range(playerCount)]
    
    for i in range(2):
        for j in range(playerCount):
            inputCardValue = cardArray.pop() 
            cardString, cardValue = getCardDetails(inputCardValue)
            if not playerArray[j][0]:
                playerArray[j][0] = cardString
                playerArray[j][1] = cardValue
            else:
                playerArray[j][0] = playerArray[j][0] + ',' +  cardString
                playerArray[j][1] = playerArray[j][1] + cardValue   
    return playerArray, cardArray     
        

def getMaxPlayerCount(player):
    playerCards = player.player_cards
    playerCount = player.player_count
    playerCardList = playerCards.split(",")
    playerFVList = [x.split()[1] for x in playerCardList]
    
    for playerFV in playerFVList:
        if playerFV == 'A':
            playerCount = playerCount+10 if(playerCount+10)<=21 else playerCount
    
    player.player_max_count = playerCount
    player.save()
    
    return player
        
        
@method_decorator(login_required, name='dispatch')
class RoundStart(View):
    @transaction.atomic
    def post(self, request, table_id):
        bet_value = json.loads(request.POST.get("bet_value"))
        current_table = Table.objects.filter(id=table_id)
        if(current_table.count()==0):
            error_message = "Unable to start round on table. Table doesn't exists!!"
            return redirect(reverse('index') + '?error=' + error_message)
        else:
            try:
                current_table = current_table[0]
                table_players = TablePlayer.objects.filter(table_id=current_table)
                playerArray, cardArray = dealCards(table_players.count()+1)
                current_table.table_status=1
                current_table.save()
                round_obj = Round.objects.create(table=current_table, 
                                                 player_count=current_table.player_count,
                                                 dealer_cards=playerArray[-1][0],
                                                 remaining_cards=",".join([str(i) for i in cardArray]),
                                                 dealer_count=playerArray[-1][1],
                                                 round_status =1)
                
                order = 1
                round_players = []
                for table_player in table_players:
                    player_status = 1 if order==1 else 0
                    if (table_player.user_id.profile.wallet_value - float(bet_value.get(table_player.user_id.username, 0))>=0):
                        round_player = RoundPlayer.objects.create(round=round_obj, 
                                                                  player=table_player.user_id, 
                                                                  player_order=order,
                                                                  player_status=player_status, 
                                                                  player_cards=playerArray[order-1][0],
                                                                  player_count= playerArray[order-1][1],
                                                                  player_bet=float(bet_value.get(table_player.user_id.username, 0)))
                        
                        round_player = getMaxPlayerCount(round_player)
                        
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


@method_decorator(login_required, name='dispatch')
class PlayerDeal(View):
    @transaction.atomic
    def post(self, request, table_id, player_order):
        current_table = Table.objects.filter(id=table_id)
        if(current_table.count()==0):
            error_message = "Unable to start deal on table. Table doesn't exists!!"
            return redirect(reverse('index') + '?error=' + error_message)
        else:
            try:
                current_table = current_table[0]
                round = Round.objects.filter(table=current_table, round_status=1)
                if(round.count()==0):
                    error_message = "Unable to start player deal on table. No active plays on the table!!"
                    return redirect(reverse('index') + '?error=' + error_message)
                else:
                    round = round[0]
                    remainingCardsList = []
                    for x in round.remaining_cards.split(","):
                        if x: 
                            remainingCardsList.append(int(x))
                    newCard = remainingCardsList.pop()
                    
                    cardString, cardValue = getCardDetails(newCard)
                    round_player = RoundPlayer.objects.filter(round=round, player_order=player_order)
                    if(round_player.count()==0):
                        error_message = "Unable to update player deal on table. No active plays on the round table!!"
                        return redirect(reverse('index') + '?error=' + error_message)
                    else:
                        round_player = round_player[0]
                        round_player.player_cards = round_player.player_cards + ',' + cardString
                        round_player.player_count = round_player.player_count + cardValue
                        if(round_player.player_count>21):
                            round_player.player_status=2
                             
                        round_player = getMaxPlayerCount(round_player)
                        
                        remaining_cards=",".join([str(i) for i in remainingCardsList])
                        round.remaining_cards = remaining_cards
                        round.save()
                        
                        round_players = RoundPlayer.objects.filter(round=round)
                        updated_round_html = render_to_string('round_players.html', {"round_players": round_players, "active_round": round})
                
                response_data = {"status": "Success", "http_status_code": 200, "round_html": updated_round_html} 
            except Exception:
                traceback.print_exc()
                response_data = {"status": "Failure", "http_status_code": 500} 
            
            return HttpResponse(json.dumps(response_data), status=response_data["http_status_code"])


@method_decorator(login_required, name='dispatch')
class PlayerStay(View):
    @transaction.atomic
    def post(self, request, table_id, player_order):
        player_order = int(player_order)
        current_table = Table.objects.filter(id=table_id)
        if(current_table.count()==0):
            error_message = "Unable to stop dealing on table. Table doesn't exists!!"
            return redirect(reverse('index') + '?error=' + error_message)
        else:
            try:
                current_table = current_table[0]
                round = Round.objects.filter(table=current_table, round_status=1)
                if(round.count()==0):
                    error_message = "Unable to stop player deal on table. No active plays on the table!!"
                    return redirect(reverse('index') + '?error=' + error_message)
                else:
                    round = round[0]
                    round_player = RoundPlayer.objects.filter(round=round, player_order=player_order)
                    if(round_player.count()==0):
                        error_message = "Unable to stop player deal on table. No active plays on the round table!!"
                        return redirect(reverse('index') + '?error=' + error_message)
                    else:
                        round_player= round_player[0]
                        round_player.player_status = 0
                        round_player.save()
                        
                        if(player_order<round.player_count):
                            player_order = player_order+1
                            round_players = RoundPlayer.objects.filter(round=round, player_order=player_order).update(player_status=1)
                        else:
                            # Stop Round Status
                            round.round_status = 1
                            round.save()
                        
                        round_players = RoundPlayer.objects.filter(round=round)
                        updated_round_html = render_to_string('round_players.html', {"round_players": round_players, "active_round": round})
                response_data = {"status": "Success", "http_status_code": 200, "round_html": updated_round_html} 
            except Exception:
                traceback.print_exc()
                response_data = {"status": "Failure", "http_status_code": 500} 
            
            return HttpResponse(json.dumps(response_data), status=response_data["http_status_code"])
