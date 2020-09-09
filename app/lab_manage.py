import json
import docker
import datetime
import urllib
from app.setup_docker_client import get_docker_client
from app.config_const import *
from app.vpn_manage import check_server_vpn, create_server_vpn
from app.notification_manage import insert_notification
from .models import Lab

from ipaddress import IPv4Interface

#TO-DO 

# IMPLEMENTARE TIMER CHE STOPPA AUTOMATICAMENTE TUTTO DOPO UN DET.TEMPO
# SPAWNING DEL PROCESSO CHE CONTROLLA L'UTENZA
# push route indirizzo ip subnet e la mask  PATH di CONF profilizzata /etc/openVPN/ccd

# Funzione equivalente a decodeURIComponent di javascript
def decode_input(inputs):

    RETURNED = {}
   
    for key,value in inputs.items():
        RETURNED[key] = urllib.parse.unquote(value)

    return RETURNED

#cont_vpn = client.containers.get("serverVPN")
#stdout = cont_vpn.exec_run(cmd="ovpn_getclient user01")


def manage(request):
    # is_ajax è una funzione già fatta da Django che controlla la presenza dell'header HTTP_X_REQUESTED_WITH nella richiesta HTTP
    if request.is_ajax():

        # L'SDK python per docker ha una versione standard, ed una versione "low" che permette di interagire con docker a più basso livello
        client = get_docker_client(LOCAL_TUNNEL)
        client_low = get_docker_client(LOCAL_TUNNEL, True)

        #creo una data corretta che servirà successivamente (il sistema attuale è 2 ore indietro, quindi qui ne aggiungo 2)
        x = datetime.datetime.now() + datetime.timedelta(hours=2)

        message = ""

        #I messaggi inviati dal frontend vengono concatenati come una stringa JSON
        POST_VALUES = decode_input(json.loads(request.POST.get('data')))

        #prendo dal db il lab che ha come primary key POST_VALUES["lab"]
        try:
            labo = Lab.objects.get(pk=POST_VALUES["lab"])
        except: 
            response_list = {
                "error": "Impossibile trovare il laboratorio"
            }
            message = json.dumps(response_list)

            return message

        ######################################################################
        #                                                                    #
        #                   INIZIO CONFIGURAZIONI VARIABILI                  #
        #                                                                    #
        ######################################################################

        #Nome network custom
        network_name_user = "network_userid_" + str(request.session["user_pk"])

        # Nome del container Docker per il Laboratorio
        name_lab = "labid_" + str(labo.pk) + "_userid_" + str(request.session["user_pk"])

        # Nome Immagine del DockerHub
        image_lab = labo.docker_name

        # - START - Configurazioni per il comando docker.run 
        cap_lab = labo.cap_add

        if labo.detach == "True":
            detach_lab = True
        else:
            detach_lab = False

        if labo.auto_remove == "True":
            auto_rm_lab = True
        else:
            auto_rm_lab = False
        # - END -

        ######################################################################
        #                                                                    #
        #                   FINE CONFIGURAZIONI VARIABILI                    #
        #                                                                    #
        ######################################################################
        
        #Flag che serve più avanti per capire se il container in questione è già in esecuzione
        found = False

        #Fai il check se esiste già una network associata all 'utente
        #Se non esiste crea la network e fai l'attach al server VPN e restituisci il certificato all'utente
        #Poi fai l'attach del container su quella rete, e restituisci l'ip all'utente

        #client.networks.create(name, ARGS)
        #   NAME = nome_utente
        #   DRIVER = bridge
        #   INTERNAL = true ? (Restrict external access to the network.)

        response_list = {
            "": ""
        }
        
        try:
            ######################################################################
            #                                                                    #
            # FACCIAMO UNA SERIE DI CHECK PER VEDERE SE TUTTO L'ENVIROMENT E' OK #
            #                                                                    #
            ######################################################################

            
            if check_server_vpn(str(request.session["user_pk"]))==False:
                response_list = {
                    "error": "Attendere l'avvio del serverVPN"
                }
                message = json.dumps(response_list)

                return message


            ######################################################################
            #                                                                    #
            #                           END CHECKS                               #
            #                                                                    #
            ######################################################################

            # I comandi inviati dal frontend tramite AJAX 
            if POST_VALUES["action"] == "start_lab" or POST_VALUES["action"] == "stop_lab":

                for cont in client.containers.list():
                    contain = client.containers.get(cont.short_id)

                    #print (json.dumps(contain.attrs))

                    #message = message + " <br /> imgs: " + contain.attrs['Config']['Image'] + " name:" + contain.attrs['Name']

                    # E' stato trovato il container del Lab
                    if contain.attrs['Config']['Image'] == image_lab and contain.attrs['Name'] == "/"+name_lab:
                        found = True
                        break
                    else:
                        pass
                        #print(contain.attrs['Name'] + "!=" + name_lab)

                

            if POST_VALUES["action"] == "start_lab": 
                if(found == True):
                    msg_response = "Questo laboratorio è già in esecuzione <br />"
                    response_list = {
                        "response_action": "stop_container",
                        "msg_response" : msg_response,
                        "start_time": x.strftime("%m/%d/%Y, %H:%M:%S")
                    }
                     
                else:

                    ports_dict = {'80/tcp': 3000} #will expose port 2222 inside the container as port 3333 on the host.

                    # Avvia il container
                    lab_started = client.containers.run(image_lab, cap_add=[cap_lab], detach=detach_lab, name=name_lab, auto_remove=auto_rm_lab, network=network_name_user)
                    
                    # Prende l'ip del container startato
                    lab_ip = get_ip_by_container(name_lab,network_name_user)

                    msg_response = "Laboratorio Avviato !! <br /> IP Lab: " + lab_ip
                    response_list = {
                        "response_action": "stop_container",
                        "msg_response" : msg_response,
                        "start_time": x.strftime("%m/%d/%Y, %H:%M:%S")
                    }

                    insert_notification("Laboratorio "+labo.nome+" Avviato!", "#", request.session["user_pk"])

                    # Setta la sessione che serve al frontend
                    request.session[name_lab] = "running"
                    request.session[name_lab+"_start_time"] = x.strftime("%m/%d/%Y, %H:%M:%S")
                    request.session[name_lab+"_IP"] = lab_ip

            elif POST_VALUES["action"] == "stop_lab":
                if(found == True):

                    client.containers.get(name_lab).remove(force=True)

                    msg_response = "Laboratorio Stoppato !! <br />"
                    response_list = {
                        "msg_response" : msg_response,
                        "response_action": "start_container"
                    }
                    
                    insert_notification("Laboratorio "+labo.nome+" Stoppato!", "#", request.session["user_pk"])

                    #Togli il valore dalla sessione
                    try:
                        del request.session[name_lab]
                        del request.session[name_lab+"_start_time"]
                        del request.session[name_lab+"_IP"]
                    except:
                        print("Errore nel cancellare la sessione")

                    #CHECK se bisogna cancellare anche la rete 
                    prune_networks()

                else:
                    #fatal error

                    try:
                        del request.session[name_lab]
                        del request.session[name_lab+"_start_time"]
                        del request.session[name_lab+"_IP"]
                    except:
                        print("Errore nel cancellare la sessione" )
                        

                    msg_response = "FATAL ERROR - Laboratorio NON TROVATO !! <br />"
                    response_list = {
                        "msg_response" : msg_response
                    }
                    

        except docker.errors.NotFound as e : 
            print("\n \n ---- il server non è riuscito a trovare il container VPN 1 (Provvedere ad un lancio manuale)  ("+ str(e.args) +")---- \n \n")
            response_list = {
                "error": "error1"
            }
        except docker.errors.APIError as e:
            print("\n \n ---- Errore nell'api docker 2 ("+ str(e.args) +")---- \n \n")
            response_list = {
                "error": "error2"
            }
        
        message = json.dumps(response_list)


    else:
        message = "Not Ajax"
    return message


def get_ip_by_container(container_name, network_name):

    client = get_docker_client(LOCAL_TUNNEL)

    try:
        net_custom = client.networks.get(network_id=network_name)
    except docker.errors.NotFound:
        return False

    for container in net_custom.attrs["Containers"]:
        if net_custom.attrs["Containers"][str(container)]['Name'] == container_name:
            return net_custom.attrs["Containers"][str(container)]['IPv4Address']

    

def prune_networks():

    client = get_docker_client(LOCAL_TUNNEL)

    try:
        client.networks.prune()
    except docker.errors.APIError:
        print("\n \n ---- il server ha ritornato un errore mentre faceva i prune dei networks ---- \n \n")
    