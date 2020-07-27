import json
import docker
import datetime

def manage(request):
    if request.is_ajax():
        #TO-DO

        # - IMPLEMENTARE TIMER CHE STOPPA AUTOMATICAMENTE TUTTO DOPO UN DET.TEMPO
        # SPAWNING DEL PROCESSO CHE CONTROLLA L'UTENZA
        # push route indirizzo ip subnet e la mask  PATH di CONF profilizzata /etc/openVPN/ccd

        client = docker.from_env()
        client_low = docker.APIClient(base_url='unix://var/run/docker.sock')

        x = datetime.datetime.now() + datetime.timedelta(hours=2)

        message = ""

        POST_VALUES = json.loads(request.POST.get('data'))

        name_lab = "lab_01_user01"

        found = False

        #Fai il check se esiste già una network associata all 'utente
        #Se non esiste crea la network e fai l'attach al server VPN e restituisci il certificato all'utente
        #Attenzione a non mettere tutto nella rete bridge
        #Poi fai l'attach del container su quella rete, e restituisci l'ip all'utente

        #client.networks.create(name, ARGS)
        #   NAME = nome_utente
        #   DRIVER = bridge
        #   INTERNAL = true ? (Restrict external access to the network.)

        network_name_user = "network_user01" #nome della network associata all'utente

        name_VPN = "serverVPN" #nome del container

        response_list = {
            "": ""
        }
        
        try:
            client.containers.get(container_id=name_VPN)

            #CHECK - se esiste già la network dell'utente, nel caso già abbia startato un'altro lab
            try:
                client.networks.get(network_id=network_name_user)
            except docker.errors.NotFound:
                #print("la rete ancora non esiste, quindi la creiamo")
                client.networks.create(name=network_name_user, driver="bridge")

            #Check - se il server vpn è connesso alla rete custom dell'utente
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

            

            if POST_VALUES["action"] == "start_lab" or POST_VALUES["action"] == "stop_lab":

                for cont in client.containers.list():
                    contain = client.containers.get(cont.short_id)

                    #print (json.dumps(contain.attrs))

                    #message = message + " <br /> imgs: " + contain.attrs['Config']['Image'] + " name:" + contain.attrs['Name']
                    if contain.attrs['Config']['Image'] == "bkimminich/juice-shop" and contain.attrs['Name'] == "/"+name_lab:
                        found = True
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

                    ports_dict = {'3000/tcp': 3000} #will expose port 2222 inside the container as port 3333 on the host.
                    lab_started = client.containers.run("bkimminich/juice-shop", cap_add=["NET_ADMIN"], detach=True, ports =ports_dict, name=name_lab, auto_remove=True, network=network_name_user)
                    lab_ip = get_ip_by_container(name_lab,network_name_user)
                    net_custom = client.networks.get(network_id=network_name_user)
                    msg_response = "Laboratorio Startato !! <br /> IP Lab: " + lab_ip
                    response_list = {
                        "response_action": "stop_container",
                        "msg_response" : msg_response,
                        "start_time": x.strftime("%m/%d/%Y, %H:%M:%S")
                    }
                    
                    #setti la sessione
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
                    

        except docker.errors.NotFound: 
            print("\n \n ---- il server non è riuscito a trovare il container VPN 1 (Provvedere ad un lancio manuale)---- \n \n")
            response_list = {
                "error": "error1"
            }
        except docker.errors.APIError as e:
            print("\n \n ---- il server non è riuscito a trovare il container VPN 2 ("+ str(e.args) +")---- \n \n")
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
    