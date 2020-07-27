from django.conf import settings
from django.contrib.auth.hashers import check_password
from app.models import User

class Custom_Auth_Backend:

    def authenticate(self, request, username=None, password=None):

        try:
            utente = User.objects.get(username=username)

            username_valid = (utente.username == username)
            pwd_valid = check_password(password, utente.password)

            if username_valid and pwd_valid:
                return utente
            else:
                return None

        except User.DoesNotExist:
            return None
        
        return None

    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None