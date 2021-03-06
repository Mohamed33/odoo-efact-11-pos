import jwt
import time


def generate_token(api_key, api_secret, time_valid=10):
    headers = {
        "iss": api_key
    }
    payload = {
        "exp": int(time.time()) + time_valid,
    }
    token = jwt.encode(payload, api_secret, 'HS256', headers)
    return token
