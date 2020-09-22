import secrets
import string
import requests
import json

from app.config_const import *
from .models import User, Statistiche

def get_random_password(): 
    alphabet = string.ascii_letters + string.digits
    password = ''.join(secrets.choice(alphabet) for i in range(10)) # for a 10-character password
    print(password)
    return(password)

#Funzione GET per tutte le challenge
def get_challenges():
    url = ""+URL_CTFD+":"+PORT_CTFD+"/api/v1/challenges"

    payload = {}

    #print ('\n\nToken '+AUTH_TOKEN)

    headers = {
    'Authorization': 'Token '+AUTH_TOKEN,
    'Content-Type': 'application/json'
    }  

    response = requests.request("GET", url, headers=headers)
    result = json.loads(response.text)

    return result

def check_challenges(name_challenge, category_challenge):

    result=get_challenges()
    #print("\n\nECCOO_>\n\n"+json.dumps(result))
    if result['success'] == True:
        for challenge in result['data']: 
            #print("Questo è l'indice" + i)
            if challenge['name'] == name_challenge and challenge['category'] == category_challenge:
                return challenge["id"]
    return False

#Funzione per prendere l'id delle flag nelle challenge
def get_idFlag(challenge_id):
    url = ""+URL_CTFD+":"+PORT_CTFD+"/api/v1/challenges/"+str(challenge_id)+"/flags"

    headers = {
        'Authorization': 'Token '+AUTH_TOKEN,
        'Content-Type': 'application/json'
    }  

    payload = {}

    response = requests.request("GET", url, headers=headers, data = payload)
    result = json.loads(response.text)
    if result['success'] == True:
        for flag in result['data']:
           flag_id = flag['id']          
           return flag_id
    else: 
        return False

def patch_challenge(challenge_id, patch_nameCh, patch_value, patch_categoryCh):
    
    url = ""+URL_CTFD+":"+PORT_CTFD+"/api/v1/challenges/"+str(challenge_id)+""
    

    payload = {

        "name": patch_nameCh,
        "value": patch_value,
        "category": patch_categoryCh,
    }

    headers = {
        'Authorization': 'Token '+AUTH_TOKEN,
        'Content-Type': 'application/json'
    }  

    response = requests.request("PATCH", url, headers=headers, data = json.dumps(payload))
    #print(response.text.encode('utf8'))
    result = json.loads(response.text)
    if result['success'] == True:
        return True
    else: 
        return False

def patch_flag(flag_patched, name_challenge, category_challenge):
    
    challenge_id=check_challenges(name_challenge,category_challenge)
    if challenge_id == False:
        return "challenge non trovata"

    flag_id = get_idFlag(challenge_id)
    if str(flag_id) == "None":
        return "flag non trovata"

    url = ""+URL_CTFD+":"+PORT_CTFD+"/api/v1/flags/"+str(flag_id)

    payload = {
        
        "challenge_id": challenge_id,
        "type": "static",
        "content": flag_patched,
    }
 
    headers = {
        'Authorization': 'Token '+AUTH_TOKEN,
        'Content-Type': 'application/json'
    }  
 
    response = requests.request("PATCH", url, headers=headers, data = json.dumps(payload))
    result = json.loads(response.text)
    print(response.text.encode('utf8'))
    if result['success'] == True:
        return True
    else:
        return False



#Funzione GET per tutte le flag associate alle challenge
def get_allFlag():
    url = ""+URL_CTFD+":"+PORT_CTFD+"/api/v1/flags"

    headers = {
    'Authorization': 'Token '+AUTH_TOKEN,
    'Content-Type': 'application/json'
    }  

    payload = {}

    response = requests.request("GET", url, headers=headers, data = payload)
    result = json.loads(response.text)

    return result

#Funzione per verificare se la flag già esiste
def check_flag(challenge_id, flag_content):
    
    result=get_allFlag()
    if result['success'] == True:
        for challenge in result['data']: 
            #print("Questo è l'indice" + i)
            if challenge['challenge_id'] == challenge_id and challenge['content'] == flag_content:
                return True
    return False

def add_flag(challenge_id, flag_content):
    url = ""+URL_CTFD+":"+PORT_CTFD+"/api/v1/flags"

    payload = {
        "challenge_id": challenge_id,
        "type": "static",  #Tipo di flag
        "content": flag_content, #Questa è la flag da aggiungere
    }

    headers = {
    'Authorization': 'Token '+AUTH_TOKEN,
    'Content-Type': 'application/json'
    }  

    if check_flag(challenge_id, flag_content) == False:
        #print("check flag è false")
        response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
        result = json.loads(response.text)
        if result['success'] == True:
            return True
        else:
            return False
    else: 
        #print("check flag è true")
        return False

def add_challenge(name_challenge, value_challenge, category_challenge, flag):

    url = ""+URL_CTFD+":"+PORT_CTFD+"/api/v1/challenges"
    
    payload = {
        "name": name_challenge, #Aggiungere il nome della challenge
        "description": "Inserisci qui la flag", #Aggiungere la descrizione della challenge
        "value": value_challenge, #Aggiungere il valore della challenge 
        "category": category_challenge, #Aggiungere la categoria
        "type": "standard",
        "state": "Visible", 
    }

    headers = {
    'Authorization': 'Token '+AUTH_TOKEN,
    'Content-Type': 'application/json'
    }  
    
    if check_challenges(name_challenge, category_challenge) == False:
        response = requests.request("POST", url, headers=headers, data = json.dumps(payload))
        #print(response.text.encode('utf8'))
        result = json.loads(response.text)
        #print(result['success'])
        if result['success'] == True:
        #Salvare l'id della challenge
            challenge_id = result['data']['id']
            return add_flag(challenge_id, flag) 
    else: 
        #print("\n\nChallenge già esistente")
        return False
        #print("Challenge già esistente")

def check_userCTFd_exists(user_id): # per vedere se nel DB già c'è un id assegnato
    me = User.objects.get(pk=user_id)

    try:
        id_ctfd = int(me.id_ctfd)
        if id_ctfd >= 0:
            return True
        else:
            return False
    except ValueError:
        return False

#Funzione per la classifica di tutti gli utenti
def get_scoreboard():

    payload = {}

    headers = {
    'Authorization': 'Token '+AUTH_TOKEN,
    'Content-Type': 'application/json'
    } 

    url = ""+URL_CTFD+":"+PORT_CTFD+"/api/v1/scoreboard"

    response = requests.request("GET", url, headers=headers, data = payload)
    #print(response.text.encode('utf8'))
    result = json.loads(response.text)
    return result

#prende lo score totale dell'utente
def get_UserScore(user_id):
    result=get_scoreboard()
    score_user = 0
    if result['success'] == True:
        for user in result['data']:
            if str(user['account_id']) == str(user_id):
                score_user += int(user['score'])
    return score_user

def insert_user(user_id):

    from app.notification_manage import insert_notification

    me = User.objects.get(pk=user_id)

    url = ""+URL_CTFD+":"+PORT_CTFD+"/api/v1/users"
    
    pwd_random = get_random_password()

    headers = {
        'Authorization': 'Token '+AUTH_TOKEN,
        'Content-Type': 'application/json'
    } 

    payload = {
        "name": me.username, #Aggiungere l'username della dashboard
        "password": pwd_random,
        "email": me.email, 
        "verified": True,
    } 
    
    #print("Inizio richiesta")
    response = requests.request("POST", url, headers=headers, data=json.dumps(payload))
    #print("RESPONSO DELLA RICHIESTA PER INSERIMENTO UTENTE"+response.text.encode('utf8'))

    #Primo if per controllare se la richiesta è stata eseguita 
    result = json.loads(response.text)
    #print(result['success'])
    if result['success'] == True:
        #Salvare l'id dell'utente
        user_id_ctfd = result['data']['id']
        me.id_ctfd = user_id_ctfd
        me.pwd_ctfd = pwd_random
        me.save()
        print("Utente inserito correttamente su CTFd")
        insert_notification("Il tuo profilo è stato aggiunto anche su CTFd", "page-user.html", user_id)
        return True

    else:
        print("ERRORE NELL'INSERIMENTO")
        return False



def get_solves(userCTFd_id):

    payload = {}
    headers = {
    'Authorization': 'Token '+AUTH_TOKEN,
    'Content-Type': 'application/json'
    }

    url = ""+URL_CTFD+":"+PORT_CTFD+"/api/v1/users"+str(userCTFd_id)+"/solves"

    response = requests.request("GET", url, headers=headers, data = payload)
    result = json.loads(response.text)
    if result['success'] == True:
        return result['data']
    else:
        return False

#Funzione GET per il numero di flag risolte da un'utente
def get_userSolves(user_id):

    payload = {}
    headers = {
    'Authorization': 'Token '+AUTH_TOKEN,
    'Content-Type': 'application/json'
    }

    url = ""+URL_CTFD+":8000/api/v1/users/"+str(user_id)+"/solves"

    response = requests.request("GET", url, headers=headers, data = payload)
    #print(response.text.encode('utf8'))
    result = json.loads(response.text)
    
    correct=0
    
    if result['success'] == True:
        for challenge_id in result['data']:
            correct+=1    
    return correct

def aggiorna_stats(id_utente_dash):
    #prendere l'id utente di ctfd
    #aggiornare le flag tramite get_solves
    #aggiornare lo score tramite get_UserScore

    #aromenti studiati e laboratori avviati vengono aggiornati dalle altre pagine

    me = User.objects.get(pk=id_utente_dash)

    if int(me.id_ctfd) >= 0: #se è associato già l'id di CTFd
        my_stats = Statistiche.objects.get(user_id=me)
        my_stats.flag_trovate = get_userSolves(me.id_ctfd)
        my_stats.punteggio = get_UserScore(me.id_ctfd)

        my_stats.save()
    

    pass