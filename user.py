import ad
from tokens import Token

class User(object):
    def __init__(self, email:str, accessToken:Token, refreshToken:Token, activeAds:list[ad]):
        self.email:str = email
        self.accessToken:Token = accessToken
        self.refreshToken:Token = refreshToken
        self.activeAds:list[ad] = activeAds

