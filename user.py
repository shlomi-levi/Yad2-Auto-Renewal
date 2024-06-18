import Ad
from Token import Token

class User(object):
    def __init__(self, email:str, accessToken:Token, refreshToken:Token, activeAds:list[Ad]):
        self.email:str = email
        self.accessToken:Token = accessToken
        self.refreshToken:Token = refreshToken
        self.activeAds:list[Ad] = activeAds

