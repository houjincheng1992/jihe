from .base import *

# SECURITY WARNING: don't run with debug turned on in production!
DEBUG = True
ALLOWED_HOSTS=['.tiffcode.com']

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = '7&r0r@5s^fpt=l%3b9&68d$k)_#cty)9%&f$71qf2skg*sy%gt'


EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'


try:
    from .local import *
except ImportError:
    pass
