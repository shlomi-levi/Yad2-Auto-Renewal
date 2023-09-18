from enum import Enum

class TokenTypes(Enum):
    ACCESS  = 1
    REFRESH = 2

class Token(object):
    def __init__(self, token_type:TokenTypes, tokenID:str, expirationUnix:int):
        self.type:TokenTypes = token_type
        self.tokenID:str = tokenID
        self.expirationUnix:int = expirationUnix



