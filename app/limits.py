from slowapi import Limiter
from slowapi.util import get_remote_address

# Single shared limiter for the whole app
limiter = Limiter(key_func=get_remote_address)
