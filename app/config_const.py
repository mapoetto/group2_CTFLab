from app.models import CTFd_configs
from app.models import SSHTunnel_configs

######################################################################
#                                                                    #
#                       APPLICATIVO MIDDLEWARE                       #
#                                                                    #
######################################################################

URL_CTFD = ""
PORT_CTFD = ""
AUTH_TOKEN = ""

if CTFd_configs.objects.exists():
    conf = CTFd_configs.objects.first()
    URL_CTFD = conf.url_API #"http://vpn.projectwork2.cyberhackademy.it"
    PORT_CTFD = str(conf.port_API) #"8000"
    AUTH_TOKEN = conf.token_API #"Token af08dd99ce903fe13b593e1053c5b1f331b4dbfe2669c8d1a538143238e17bbd"
else:
    print("Inserire la configurazione di CTFd")




######################################################################
#                                                                    #
#                       DOCKER API - SSH TUNNEL                      #
#                                                                    #
######################################################################
FULL_PATH_SSH_KEY = ""
USER_SERVER = ""
DNS_NAME_SERVER = ""
LOCAL_PORT = ""
REMOTE_PORT = ""


if SSHTunnel_configs.objects.exists():
    conf= SSHTunnel_configs.objects.first()
    FULL_PATH_SSH_KEY = conf.FULL_PATH_SSH_KEY
    USER_SERVER = conf.USER_SERVER
    DNS_NAME_SERVER = conf.DNS_NAME_SERVER
    LOCAL_PORT = conf.LOCAL_PORT
    REMOTE_PORT = conf.REMOTE_PORT   

    LOCAL_TUNNEL = "tcp://127.0.0.1:"+str(LOCAL_PORT)+""
else:
   print("Inserire la configurazione del Tunnel SSH")

