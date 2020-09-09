from app.models import CTFd_configs

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
FULL_PATH_SSH_KEY = "/home/mapoetto/Scrivania/PW/django/django/challange.pem"
USER_SERVER = "ubuntu"
DNS_NAME_SERVER = "ec2-3-85-164-96.compute-1.amazonaws.com"
LOCAL_PORT = "7000"
REMOTE_PORT = "2375"

LOCAL_TUNNEL = "tcp://127.0.0.1:"+LOCAL_PORT+""