import json
import docker
import datetime
import urllib
from app.setup_docker_client import get_docker_client
from app.setup_docker_client import LOCAL_TUNNEL

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

        # Nome del container Docker per il Laboratorio
        name_lab = "labid_" + str(labo.pk) + "_userid_" + str(request.session["user_pk"])

        # Nome per il certificato client dell VPN
        name_client_ovpn = "userid_" + str(request.session["user_pk"])

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
            #print("\n\n -->" + json.dumps(net_custom.attrs))
            
            #print("\n\n -->" + net_custom.attrs["IPAM"]["Config"][0]["Subnet"][:-3])

            #Scorre tutti i container connessi alla network utente
            for container in net_custom.attrs["Containers"]:
                container_final = client.containers.get(container)
                if container_final.attrs['Name'] == "/"+name_VPN: #se uno di questi è proprio il container VPN
                    found_vpn_connection = True

            #se il serverVPN non è connesso alla rete custom, connettilo
            if found_vpn_connection == False:
                client_low.connect_container_to_network(container=name_VPN, net_id=network_name_user)
            
            # - CHECK 4 -
            # Controlliamo se nel container vpn esiste già la configurazione per l'utente attuale
            # La configurazione consiste nell'avere nel containerVPN, nella cartella etc/openvpn/ccd (path indicato quando si crea la configurazione del containerVPN)
            # un file che rispecchi il nome di un client
            # ed all'interno del file ci sia la stringa
            # push "route 172.24.0.0 255.255.0.0"
            # dove 172.24.0.0 è l'ip della subnet custom creata per l'utente e 255.255.0.0 la sua netmask
            # dopodichè bisogna dare il comando seguente:
            # iptables -t nat -A POSTROUTING -o $INTERFACE_USERID_1 -j MASQUERADE
            # per dire al containerVPN di agire da NAT per quell'interfaccia
            # $INTERFACE_USERID_1 è una variabile d'ambiente in cui setta l'interfaccia fisica del containerVPN su cui è connesso alla rete custom

            cont_vpn = client.containers.get(name_VPN)
            stdout = cont_vpn.exec_run(cmd="cd etc/openvpn/ccd && [ -f logss ] && echo \"File found!\"")

            #net_custom.attrs["IPAM"]["Config"][0]["Subnet"][:-3] è l'ip della subnet
            #net_custom.attrs["IPAM"]["Config"][0]["Subnet"] è la network interface (ovvero l'ip con /16 alla fine)

            if stdout.output != "File found!":
                netmask_from_ip_interface = str(IPv4Interface(net_custom.attrs["IPAM"]["Config"][0]["Subnet"]).netmask)
                str1 = "sh -c \'echo \\'push \"route "
                str2 = "\" \\' > /etc/openvpn/ccd/"
                command = str1 + net_custom.attrs["IPAM"]["Config"][0]["Subnet"][:-3] +" "+netmask_from_ip_interface + str2 + name_client_ovpn + "\'"
                print("\n\n" + command)
                stdout = cont_vpn.exec_run(cmd=command)
                print("\n\n1--->> "+ str(stdout.output))
                print("\n\n11--->> "+ str(stdout.exit_code))
                print(command)

                # se il primo comando è andato bene
                if stdout.exit_code == 0:

                    # setta una variabile d'ambiente in cui inserisce l'interfaccia fisica del containerVPN che è connessa alla network custom
                    # 172.24.0.2 = ip del serverVPN nella rete custom = cont_vpn.attrs["NetworkSettings"]["Networks"][network_name_user]["IPAddress"]
                    # export INTERFACE_USERID_1=$(ifconfig | sed -n '/addr:172.24.0.2/{g;H;p};H;x' | awk '{print $1}')

                    name_variable_env = "INTERFACE_USERID_" + str(request.session["user_pk"])
                    ip_serverVPN_in_rete_custom = str(cont_vpn.attrs["NetworkSettings"]["Networks"][network_name_user]["IPAddress"])
                    command = "export "+name_variable_env+"=$(ifconfig | sed -n '/addr:"+ip_serverVPN_in_rete_custom+"/{g;H;p};H;x' | awk '{print $1}')"
                    stdout = cont_vpn.exec_run(cmd=command)

                    print("\n\n2--->> "+ str(stdout.output))
                    print("\n\n22--->> "+ str(stdout.exit_code))

                    # se il secondo comando è andato bene
                    if stdout.exit_code == 0:
                        # iptables -t nat -A POSTROUTING -o $INTERFACE_USERID_1 -j MASQUERADE

                        command = "iptables -t nat -A POSTROUTING -o $"+name_variable_env+" -j MASQUERADE"
                        stdout = cont_vpn.exec_run(cmd=command)
                        print("\n\n3--->> "+ str(stdout.output))
                        print("\n\n33--->> "+ str(stdout.exit_code))

                        # se l'ultimo comando è andato male
                        if stdout.exit_code != 0:
                            pass #return
                    else:
                        pass #return
                else:
                    pass #return

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
    