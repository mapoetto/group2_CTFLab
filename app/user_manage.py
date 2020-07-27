from .models import User
from django.contrib.auth.hashers import check_password
import json

def manage(request):

    response_list = {
        "": ""
    }

    POST_VALUES = json.loads(request.POST.get('data'))

    if POST_VALUES["action"] == "update_infos":
        
        me = User.objects.get(pk=request.session["user_pk"])
        if len(POST_VALUES["professione"]) >=3 and len(POST_VALUES["nome"]) >=3 and len(POST_VALUES["cognome"]) >=3:
            me.professione = POST_VALUES["professione"]
            me.nome = POST_VALUES["nome"]
            me.cognome = POST_VALUES["cognome"]
            me.save()

            response_list = {
                "msg_response" : "Informazioni Aggiornate Correttamente!",
            }
        else:
            response_list = {
                "error": "Riempire correttamente i campi"
            }
        
        message = json.dumps(response_list)

    elif POST_VALUES["action"] == "update_pwd":
        me = User.objects.get(pk=request.session["user_pk"])
        if len(POST_VALUES["pwd_attuale"]) >=3 and len(POST_VALUES["new_pwd"]) >=3 and len(POST_VALUES["r_new_pwd"]) >=3:
            if POST_VALUES["new_pwd"] == POST_VALUES["r_new_pwd"]:
                if(check_password(POST_VALUES["pwd_attuale"], me.password)):
                    me.set_password(POST_VALUES["new_pwd"])
                    me.save()
                    response_list = {
                        "logout": "si",
                        "msg_response" : "Password Aggiornata Correttamente! (E' necessario effettuare nuovamente il login!)",
                    }
                else:
                    response_list = {
                        "error": "Password Errata"
                    }
            else:
                response_list = {
                    "error": "La nuova password non corrisponde"
                }
        else:
            response_list = {
                "error": "Inserire una password maggiore o uguale di 3 caratteri"
            }
    else:
        #should not be here
        response_list = {
            "error": "Unknown action"
        }
    
    message = json.dumps(response_list)

    return message
