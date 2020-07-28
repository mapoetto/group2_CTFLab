import json
import docker
import datetime
import urllib

from .models import Lab

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

def manage(request):
    # is_ajax è una funzione già fatta da Django che controlla la presenza dell'header HTTP_X_REQUESTED_WITH nella richiesta HTTP
    if request.is_ajax():

        # L'SDK python per docker ha una versione standard, ed una versione "low" che permette di interagire con docker a più basso livello
        client = docker.from_env()
        client_low = docker.APIClient(base_url='unix://var/run/docker.sock')

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

        # Nome del container Docker per il Laboratorio
        name_lab = "labid_" + str(labo.pk) + "_userid_" + str(request.session["user_pk"])

        # Nome Immagine del DockerHub
        image_lab = labo.docker_name

        # Nome della network custom associata all'utente
        network_name_user = "network_userid_"+str(request.session["user_pk"])

        # Nome del container VPN  NB: il container deve essere già in esecuzione e preconfigurato
        name_VPN = "serverVPN" 

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

            # - CHECK 1 -
            # Proviamo a fare un get del containerVPN, perchè nel caso fallisca, viene eseguito l'except che stoppa tutto
            # Non ha senso startare un laboratorio se non c'è il container VPN
            client.containers.get(container_id=name_VPN)

            # - CHECK 2 -
            # Proviamo a fare un get della network Custom dell'utente, nel caso già abbia startato un'altro lab
            try:
                client.networks.get(network_id=network_name_user)
            except docker.errors.NotFound:
                #Nel caso non ci sia (poichè può essere stata eliminata dopo un tot di inutilizzo), la creiamo
                #print("la rete custom dell'utente ancora non esiste, quindi la creiamo")
                client.networks.create(name=network_name_user, driver="bridge")

            # - CHECK 3 -
            # Controlliamo se il server vpn è già connesso alla rete custom dell'utente
            net_custom = client.networks.get(network_id=network_name_user) #prende i container collegati alla network 
            found_vpn_connection = False

            #Scorre tutti i container connessi alla network utente
            for container in net_custom.attrs["Containers"]:
                container_final = client.containers.get(container)
                if container_final.attrs['Name'] == "/"+name_VPN: #se uno di questi è proprio il container VPN
                    found_vpn_connection = True

            #se il serverVPN non è connesso alla rete custom, connettilo
            if found_vpn_connection == False:
                client_low.connect_container_to_network(container=name_VPN, net_id=network_name_user)

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

                    msg_response = "Laboratorio Startato !! <br /> IP Lab: " + lab_ip
                    response_list = {
                        "response_action": "stop_container",
                        "msg_response" : msg_response,
                        "start_time": x.strftime("%m/%d/%Y, %H:%M:%S")
                    }
                    
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
                        print("Errore nel cancellare la sessione")

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

    client = docker.from_env()

    try:
        net_custom = client.networks.get(network_id=network_name)
    except docker.errors.NotFound:
        return False

    for container in net_custom.attrs["Containers"]:
        if net_custom.attrs["Containers"][str(container)]['Name'] == container_name:
            return net_custom.attrs["Containers"][str(container)]['IPv4Address']

    

def prune_networks():

    client = docker.from_env()

    try:
        client.networks.prune()
    except docker.errors.APIError:
        print("\n \n ---- il server ha ritornato un errore mentre faceva i prune dei networks ---- \n \n")
    