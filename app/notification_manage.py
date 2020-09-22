import json
import urllib
from app.models import Notifica, Notifica_vista
from app.models import User
from django.db.models import Q

def decode_input(inputs):

    RETURNED = {}
   
    for key,value in inputs.items():
        RETURNED[key] = urllib.parse.unquote(value)

    return RETURNED

def insert_notification(insert_testo, insert_link, insert_utente):
    insert = Notifica(testo=insert_testo, link=insert_link, destinatario=insert_utente)
    insert.save()

def manage(request):
    if request.is_ajax():

        POST_VALUES = decode_input(json.loads(request.POST.get('data')))

        if POST_VALUES["action"] == "get_notifications":

            notifiche = dict()
            num_notifiche = 0

            try:
                notifiche_per_me = Notifica.objects.filter(destinatario=request.session["user_pk"])

                for notifica in notifiche_per_me:
                    try:
                        vista = Notifica_vista.objects.get(notifica_id=notifica.pk) #se ci sta vuol dire che è già stata vista, e non dobbiamo metterla
                        if vista.stato == "vista":
                            #print("Questa notifica già l'ho vista1")
                            pass
                        else:
                            #print("Questa notifica NON l'ho vista1")
                            raise Notifica_vista.DoesNotExist

                    except Notifica_vista.DoesNotExist: #se non è nella tabella delle notifiche viste, vuol dire che non è stata vista
                        notifiche["x_utente_"+str(notifica.pk)] = dict()
                        notifiche["x_utente_"+str(notifica.pk)]["testo"] = notifica.testo
                        notifiche["x_utente_"+str(notifica.pk)]["link"] = notifica.link
                        if POST_VALUES["click"] == "si":
                            Notifica.objects.filter(pk=notifica.pk).delete()
                        num_notifiche= num_notifiche + 1
                        #print("NOTIFICA DA VEDERE1")

            except Notifica.DoesNotExist: #non ci sono notifiche fatte personalmente per me
                print("non ci sono notifiche fatte personalmente per me1")
                pass

            try:
                notifiche_per_tutti = Notifica.objects.filter(destinatario="tutti")
                for notifica in notifiche_per_tutti:
                    try:
                        vista = Notifica_vista.objects.get(Q(notifica_id=notifica.pk) & Q(user_id=request.session["user_pk"])) #se ci sta vuol dire che è già stata vista, e non dobbiamo metterla
                        
                        if vista.stato == "vista":
                            #print("Questa notifica già l'ho vista2")
                            pass
                        else:
                            #print("Questa notifica NON l'ho vista2")
                            raise Notifica_vista.DoesNotExist
                    except Notifica_vista.DoesNotExist: #se non è nella tabella delle notifiche viste, vuol dire che non è stata vista
                        notifiche["x_tutti_"+str(notifica.pk)] = dict()
                        notifiche["x_tutti_"+str(notifica.pk)]["testo"] = notifica.testo
                        notifiche["x_tutti_"+str(notifica.pk)]["link"] = notifica.link
                        if POST_VALUES["click"] == "si":
                            insert = Notifica_vista(stato="vista", user_id=User.objects.get(pk=request.session["user_pk"]), notifica_id=Notifica.objects.get(pk=notifica.pk))
                            insert.save()
                        num_notifiche= num_notifiche + 1
                        #print("NOTIFICA DA VEDERE2")
            except Notifica.DoesNotExist: #non esiste ancora alcuna notifica per tutti
                #print("non esiste ancora alcuna notifica per tutti2")
                pass

        response_list = {
            "notifiche": json.dumps(notifiche),
            "num_notifiche": num_notifiche
        }
        message = json.dumps(response_list)
            


    else:
        message = "Not Ajax"

    return message

