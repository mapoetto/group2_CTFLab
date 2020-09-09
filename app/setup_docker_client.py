import docker
import subprocess
import time

from app.config_const import *

#SETUP sul SERVER DOCKER:
# rimuovi il docker pid: sudo rm /var/run/docker.pid
# stoppa il servizio docker: sudo systemctl stop docker
# starta il demone docker sulla tua porta: sudo dockerd -H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock
#sudo rm /var/run/docker.pid && sudo systemctl stop docker && sudo dockerd -H tcp://0.0.0.0:2375 -H unix:///var/run/docker.sock



#client = docker.DockerClient(base_url='tcp://127.0.0.1:7000')
ports_dict = {'80/tcp': 123}
#docker run -d -p 123:80 giussorama/repo:latest
#lab_started = client.containers.run("giussorama/repo:latest", detach=True, name="lab1", auto_remove=True, ports=ports_dict)
#print(lab_started)

# ssh -i "challange.pem" ubuntu@ec2-52-3-245-151.compute-1.amazonaws.com -Nf -L  7000:127.0.0.1:2375
# -Nf = in background e senza interattività



def get_docker_client(url_server_docker, low=False):

    #Comando per controllare se la porta in questione è usata
    cmd_check_tunnel = "nc -z localhost "+LOCAL_PORT+" || echo \"no tunnel open\""

    #Provo a prendere il client 
    try:

        result = subprocess.check_output(cmd_check_tunnel, shell=True)

        #print("\n\n\nResult of tunnel-> "+ str(result) + " \n\n\n")

        if "no tunnel open" in str(result): #vuol dire che ha stampato "no tunnel open"
            #print("non c'è il tunnel")
            #print("\n\nIl Tunnel non c'è")
            raise Exception("Il Tunnel non c'è")
        else:
            #print("\n\nil tunnell c'è ->"+str(result))
            pass

        if low == False:
            client = docker.DockerClient(base_url=url_server_docker)
        else:
            client = docker.APIClient(base_url=url_server_docker)
    except Exception as e:

        print("\n\n\n Excepted ("+str(e.args)+")\n\n\n")

        #Impossibile trovare l'API Docker su questo indirizzo
        #Facciamo il set up del tunnel ssh

        #Comando: ssh -i "challange.pem" ubuntu@ec2-52-3-245-151.compute-1.amazonaws.com -Nf -L  7000:127.0.0.1:2375
        cmd = "ssh -i \""+FULL_PATH_SSH_KEY+"\" "+USER_SERVER+"@"+DNS_NAME_SERVER+" -Nf -L  "+LOCAL_PORT+":127.0.0.1:"+REMOTE_PORT
        
        result = subprocess.check_output(cmd, shell=True)

        time.sleep(1) # Aspettiamo 1 secondo per fare in modo che il tunnel SSH sia attivo

        #Riproviamo a prendere il client
        try:

            result = subprocess.check_output(result = subprocess.check_output(cmd_check_tunnel, shell=True), shell=True)
            
            if len(str(result)) > 5: #vuol dire che ha stampato "no tunnel open"
                #print("non c'è il tunnel")
                print("\n\nImpossibile stabilire il tunnel ssh, non è possibile comunicare con la macchina docker")
                raise Exception("Impossibile stabilire il tunnel ssh, non è possibile comunicare con la macchina docker")
            else:
                print("\n\nil tunnell c'è")
                pass

            if low == False:
                client = docker.DockerClient(base_url=url_server_docker)
            else:
                client = docker.APIClient(base_url=url_server_docker)
        except:
            raise Exception('Errore', 'Impossibile creare il client con l\'url specificato') 

    return client
