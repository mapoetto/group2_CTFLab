
import docker
import subprocess
import random
import json
from app.models import User

from app.config_const import *
from app.setup_docker_client import get_docker_client

#       WORKFLOW
#
# 1) Controlla se esiste già la rete custom dell'utente (se non esiste, creala)
# 2) Controlla se esiste già il container serverVPN dell'utente (se non esiste, crealo) (di seguito i comandi per crearlo)
#
#PROBLEMA-SUDO NETSTAT RICHIEDE LA PASSWORD AL PRIMO AVVIO
#ANCHE IL TUNNEL SSH RICHIEDE LA CONFERMA LA PRIMA VOLTA

def get_porta(user_id):

    #RANGE DI PORTE GENERALMENTE NON UTILIZZATE 
    MIN_RANGE = 34444
    MAX_RANGE = 36962

    user_id= int(user_id)

    me = User.objects.get(pk=user_id)

    if len(str(me.porta_vpn)) == 0: #non c'è alcuna porta

        random_port = random.randint(MIN_RANGE, MAX_RANGE)

        cmd_check_port = "sudo netstat -nlp | grep :"+str(random_port)
        try:
            result = subprocess.check_output(cmd_check_port, shell=True)

            while (len(result)!=0):
                random_port = random.randint(MIN_RANGE, MAX_RANGE)
                cmd_check_port = "sudo netstat -nlp | grep :"+str(random_port)
                try:
                    result = subprocess.check_output(cmd_check_port, shell=True)
                except:
                    break #se netstat fa exit 1 vuol dire che la porta non è occupata
        except:
            pass #se netstat fa exit 1 vuol dire che la porta non è occupata



        me.porta_vpn = str(random_port)
        me.save()

        return random_port
    else:
        return me.porta_vpn


def create_server_vpn(user_id):

    user_id = str(user_id)

    # L'SDK python per docker ha una versione standard, ed una versione "low" che permette di interagire con docker a più basso livello
    client = get_docker_client(LOCAL_TUNNEL)
    client_low = get_docker_client(LOCAL_TUNNEL, True)

    #url sul quale sarà attivo il server VPN
    url_attuale = DNS_NAME_SERVER

    #export ID_UTENTE_ID=Utente1
    nome_certificato_utente = "Utente_" + user_id

    #export PORTA_CLIENT_ID=1001
    #RANGE PORTE NON USATE 34444 - 36962
    porta_client_utente = get_porta(user_id)  #PORTA_CLIENT_ID deve essere in un certo range

    #

    #export OVPN_DATA_ID="ovpn-data-$ID_UTENTE"
    nome_volume_utente = "ovpn-data-" + user_id

    # Nome della network custom associata all'utente
    network_name_user = "network_userid_"+user_id

    # Nome del container VPN
    name_VPN = "serverVPN_user_" + user_id
    print("ora inizio a creare")
    # Proviamo a fare un get della network Custom dell'utente, nel caso esista già
    try:
        client.networks.get(network_id=network_name_user)
    except docker.errors.NotFound:
        #Nel caso non ci sia (poichè può essere stata eliminata dopo un tot di inutilizzo), la creiamo
        #print("la rete custom dell'utente ancora non esiste, quindi la creiamo")
        client.networks.create(name=network_name_user, driver="bridge")

    #docker volume create --name $OVPN_DATA_ID
    client.volumes.create(name=nome_volume_utente)


    #primo comando
    #docker run -v $OVPN_DATA_ID:/etc/openvpn --log-driver=none --rm kylemanna/openvpn ovpn_genconfig -u udp://vpn.projectwork2.cyberhackademy.it:$PORTA_CLIENT_ID
    
    #secondo comando
    #docker run -v $OVPN_DATA_ID:/etc/openvpn --log-driver=none --rm -e EASYRSA_BATCH=1 kylemanna/openvpn ovpn_initpki nopass

    #terzo comando
    #docker run -v $OVPN_DATA_ID:/etc/openvpn -d -p $PORTA_CLIENT_ID:1194/udp --cap-add=NET_ADMIN kylemanna/openvpn

    #quarto comando
    #docker run -v $OVPN_DATA_ID:/etc/openvpn --log-driver=none --rm kylemanna/openvpn easyrsa build-client-full $ID_UTENTE_ID nopass

    #quinto comando
    #docker run -v $OVPN_DATA_ID:/etc/openvpn --log-driver=none --rm kylemanna/openvpn ovpn_getclient $ID_UTENTE_ID > $ID_UTENTE_ID.ovpn

    #immagine del serverVPN
    immagine_server = "kylemanna/openvpn"
    
    volumes= ['/host_location']

    volume_bindings = {
        nome_volume_utente: {
            'bind': '/etc/openvpn',
            'mode': 'rw',
        },
    }

    envs = ["EASYRSA_BATCH=1"]

    porte = {'1194/udp': porta_client_utente} #will expose port 1194/udp inside the container as port porta_client_utente on the host.

    print("\n- Inizio il primo comando - ")
    try:
        cmd1 = "ovpn_genconfig -u udp://"+url_attuale+":"+str(porta_client_utente)

        cmd_setup_1  = client.containers.run(immagine_server, 
                                             volumes=volume_bindings,
                                             command=cmd1,
                                             cap_add=["net_admin"],
                                             network=network_name_user)
    except docker.errors.APIError as e1:
        print ("Errore al primo comando ("+ str(e1.args) +")---- \n \n")
        return False

    print ("completato")

    print("\n- Inizio il secondo comando - ")
    if True:
        try:
            cmd_setup_2  = client.containers.run(immagine_server,
                                                volumes=volume_bindings,
                                                command="ovpn_initpki nopass",
                                                environment=envs,
                                                cap_add=["net_admin"],
                                                auto_remove=True,
                                                network=network_name_user)
        except docker.errors.APIError as e2:
            print ("Errore al secondo comando ("+ str(e2.args) +")---- \n \n")
            return False
    print ("completato")

    print("\n- Inizio il terzo comando - ")
    try:
        cmd_setup_3  = client.containers.run(immagine_server,
                                            volumes=volume_bindings,
                                            ports=porte,
                                            cap_add=["net_admin"],
                                            detach=True,
                                            name=name_VPN,
                                            network=network_name_user)
    except docker.errors.APIError as e3:
        print ("Errore al terzo comando ("+ str(e3.args) +")---- \n \n")
        return False
    print ("completato")

    print("\n- Inizio il quarto comando - ")
    try:

        #se già esiste:
        #vedi se c'è la stringa = Request file already exists
        #rm /etc/openvpn/pki/reqs/"+nome_certificato_utente+".req
        #rm /etc/openvpn/pki/issued/"+nome_certificato_utente+".crt
        #rm /etc/openvpn/pki/private/"+nome_certificato_utente+".key

        cont_vpn = client.containers.get(name_VPN)
        stdout = cont_vpn.exec_run(cmd="easyrsa build-client-full "+nome_certificato_utente+" nopass")

        if "Request file already exists" in bytes(stdout.output).decode("utf-8"):

            cmd_delete_all = "rm /etc/openvpn/pki/reqs/"+nome_certificato_utente+".req && rm /etc/openvpn/pki/issued/"+nome_certificato_utente+".crt && rm /etc/openvpn/pki/private/"+nome_certificato_utente+".key"

            stdout = cont_vpn.exec_run(cmd=cmd_delete_all)
            
            stdout = cont_vpn.exec_run(cmd="easyrsa build-client-full "+nome_certificato_utente+" nopass")
            if "Generating a RSA private key" in bytes(stdout.output).decode("utf-8"):
                print("-- Certificato generato")
            else:
                raise docker.errors.APIError("Non ha generato nulla1")

        elif "Generating a RSA private key" in bytes(stdout.output).decode("utf-8"):
            print ("-- Certificato generato 2")
        
        stdout = cont_vpn.exec_run(cmd="sh -c 'ovpn_getclient "+nome_certificato_utente+" > client.ovpn'")
        stdout = cont_vpn.exec_run(cmd="sh -c 'cat client.ovpn'")
        if "BEGIN CERTIFICATE" in bytes(stdout.output).decode("utf-8"):
            print("-- File client.ovpn generato correttamente")
        else:
            raise docker.errors.APIError("Non ha generato nulla2"+bytes(stdout.output).decode("utf-8"))

        client.containers.prune()
        client.images.prune()
        client.networks.prune()
        client.volumes.prune()
        
        print("-- Prune completati")

    except docker.errors.APIError as e4:
        print ("Errore al quarto comando ("+ str(e4.args) +")---- \n \n")
        return False
        
    print ("completato")

    #se il serverVPN non è connesso alla rete custom, connettilo
    #client_low.connect_container_to_network(container=name_VPN, net_id=network_name_user)

    return True



def check_server_vpn(user_id):

    client = get_docker_client(LOCAL_TUNNEL)

    #print("deleted containers->"+json.dumps(client.containers.prune()))
    #print("\n\ndeleted images->"+json.dumps(client.images.prune(filters={"dangling":False})))
    #client.networks.prune()
    #client.volumes.prune()

    client = get_docker_client(LOCAL_TUNNEL)
    name_VPN = "serverVPN_user_" + str(user_id)
    try:
        print("CHECK - sto quiii")
        cont_vpn = client.containers.get(name_VPN)
        if cont_vpn.status == "running":
            pass
        else:
            return False
    except docker.errors.APIError as e:
        print ("serverVPN per l'utente (ID:"+str(user_id)+") inesistente, dettagli: ("+ str(e.args) +")---- \n \n")
        return False

    return True