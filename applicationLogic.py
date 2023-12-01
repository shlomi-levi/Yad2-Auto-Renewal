import math
import json
import pickle
import requests
import threading
import time
import copy
import Yad2Constants

from ThreadInfo import ThreadInfo
from Token import Token, TokenTypes
from Ad import Ad
from User import User

dataFile = 'data.pickle'

usersList:list[User] = []
emailsList:set = set()
userToThread:dict[str, ThreadInfo] = {}
threadCounter:int = 1

# Convert the provided timestamp to a datetime object
def getUnixTime(timeString: str):
    import iso8601

    return int(math.ceil(iso8601.parse_date(timeString).timestamp()))

def getCurrentUnixTime():
    import time
    return int(math.floor(time.time()))

def getNewTokens(u: User) -> None:
    URL:str = Yad2Constants.TOKEN_REFRESH_ADDRESS
    session = requests.session()

    try:
        response = session.post(URL, cookies={Yad2Constants.REFRESH_TOKEN_STRING: u.refreshToken.tokenID})

        if response.status_code < 200 or response.status_code > 299:
            return

        accessToken: Token = None  # type: ignore
        refreshToken: Token = None  # type: ignore

        for cookie in session.cookies:
            if cookie.name == Yad2Constants.ACCESS_TOKEN_STRING:
                accessToken: Token = Token(TokenTypes.ACCESS, cookie.value, cookie.expires)

            elif cookie.name == Yad2Constants.REFRESH_TOKEN_STRING:
                refreshToken: Token = Token(TokenTypes.REFRESH, cookie.value, cookie.expires)

        if session:
            session.close()

        if accessToken is not None:
            u.accessToken = accessToken

        if refreshToken is not None:
            u.refreshToken = refreshToken

    except Exception:
        if session:
            session.close()

def verifyTokensValidity(user:User):
    currUnix = getCurrentUnixTime()

    if user.accessToken.expirationUnix < currUnix or user.refreshToken.expirationUnix < currUnix:
        getNewTokens(user)

# add verification that everything went smoothly
def bumpAd(ad:Ad, user:User) -> None:
    adID = ad.adID

    requestURL:str = f"{Yad2Constants.BUMP_AD_URL_PART_1}/{adID}/{Yad2Constants.BUMP_AD_URL_PART_2}"

    verifyTokensValidity(user)

    session = requests.Session()
    response = session.put(requestURL, cookies = { Yad2Constants.ACCESS_TOKEN_STRING: user.accessToken.tokenID, Yad2Constants.REFRESH_TOKEN_STRING: user.refreshToken.tokenID})

    for cookie in session.cookies:
        if cookie.name == Yad2Constants.ACCESS_TOKEN_STRING:
            user.accessToken = Token(TokenTypes.ACCESS, cookie.value, cookie.expires)

        elif cookie.name == Yad2Constants.REFRESH_TOKEN_STRING:
            user.refreshToken = Token(TokenTypes.REFRESH, cookie.value, cookie.expires)

    response = json.loads(response.text)

    nextPromotion = response.get(Yad2Constants.BUMP_AD_RESPONSE_ROOT, {}).get(Yad2Constants.BUMP_AD_RESPONSE_NEXT_PROMOTION_FIELD, {})

    ad.nextPromotionUnix = getUnixTime(nextPromotion)

    if session:
        session.close()

def threadFunction(user:User, threadID:int) -> None:
    while user.email in userToThread and userToThread[user.email].threadID == threadID:
        current_time_utc = getCurrentUnixTime()

        for i in range(len(user.activeAds)):
            if current_time_utc > user.activeAds[i].nextPromotionUnix:
                bumpAd(user.activeAds[i], user)

        user.activeAds.sort(key=lambda x: x.nextPromotionUnix)

        time.sleep( math.ceil(user.activeAds[0].nextPromotionUnix - current_time_utc))

def findIndex(email:str) -> int:
    for i in range(len(usersList)):
        if usersList[i].email == email:
            return i

    return -1

def getUserObject(email:str) -> User:
    index = findIndex(email)
    if index == -1:
        return None # type: ignore

    return usersList[index]

def activateUser(u:User) -> None:
    global threadCounter

    email = u.email
    index = findIndex(email)

    if len(usersList[index].activeAds) < 1 or index == -1:
        return

    if email in userToThread and userToThread[email].isActive:
            return

    thread = threading.Thread(target=threadFunction, daemon=True, args=(usersList[index],threadCounter))

    tinfo: ThreadInfo = ThreadInfo(threadCounter, True)

    threadCounter += 1

    userToThread[email] = tinfo

    thread.start()

def deactivateUser(u:User) -> None:
    email = u.email

    if email not in userToThread:
        return

    del userToThread[email]

def removeUser(u:User) -> None:
    email = u.email

    if email in userToThread:
        deactivateUser(u)

    if email in emailsList:
        emailsList.remove(email)

    index = findIndex(email)

    if index != -1:
        del usersList[index]

    saveData()

def emailExists(email:str) -> bool:
    if email in emailsList:
        return True

    else:
        return False

def isUserThreadActive(user:User) -> bool:
    if user.email in userToThread:
        if userToThread[user.email].isActive:
            return True

    return False

class LoginRequestOutput(object):
    def __init__(self, isSuccess:bool, accessToken:Token, refreshToken: Token):
        self.isSuccess:bool = isSuccess
        self.accessToken:Token = accessToken
        self.refreshToken:Token = refreshToken

def sendLoginRequest(username:str, pw:str) -> LoginRequestOutput:
    URL:str = Yad2Constants.LOGIN_URL
    session = requests.session()

    payload = { Yad2Constants.LOGIN_REQUEST_EMAIL_FIELD_STRING: username, Yad2Constants.LOGIN_REQUEST_PASSWORD_FIELD_STRING: pw}

    try:
        response = session.post(URL, json = payload)

        if response.status_code < 200 or response.status_code > 299:
            return LoginRequestOutPut(False, None, None) # type: ignore

        accessToken:Token = None # type: ignore
        refreshToken:Token = None # type: ignore

        for cookie in session.cookies:
            if cookie.name == Yad2Constants.ACCESS_TOKEN_STRING:
                accessToken:Token = Token(TokenTypes.ACCESS, cookie.value, cookie.expires)

            elif cookie.name == Yad2Constants.REFRESH_TOKEN_STRING:
                refreshToken:Token = Token(TokenTypes.REFRESH, cookie.value, cookie.expires)

        if session:
            session.close()

        return LoginRequestOutput(True, accessToken, refreshToken)

    except Exception:
        if session:
            session.close()

        return LoginRequestOutput(False, None, None)  # type: ignore

def getActiveAds(user:User) -> None:
    URL = Yad2Constants.ACTIVE_ADS_ADDRESS

    verifyTokensValidity(user)

    response = requests.get(URL, cookies = { Yad2Constants.ACCESS_TOKEN_STRING: user.accessToken.tokenID, Yad2Constants.REFRESH_TOKEN_STRING: user.refreshToken.tokenID})

    response = json.loads(response.text)

    items = response.get(Yad2Constants.ACTIVE_ADS_RESPONSE_ROOT, {}).get(Yad2Constants.ACTIVE_ADS_RESPONSE_CHILD, {})

    tempActiveAds = []

    for ad in items:
        nextPromotion = getUnixTime(ad[Yad2Constants.NEXT_AD_PROMOTION_STRING])
        tempActiveAds.append(Ad(ad[Yad2Constants.AD_ID_STRING], nextPromotion))

    user.activeAds = tempActiveAds

def addUser(email: str, password: str) -> bool:
    output = sendLoginRequest(email, password)

    if not output.isSuccess:
        return False

    u:User = User(email, output.accessToken, output.refreshToken, [])

    emailsList.add(email)

    getActiveAds(u)

    usersList.append(u)

    saveData()

    return True

def loadData() -> None:
    import os
    file_path = f'./{dataFile}'

    if not os.path.exists(file_path):
        return

    global usersList

    with open(dataFile, 'rb') as handle:
        usersList = pickle.load(handle)

def saveData() -> None:
    myList:list[User] = copy.deepcopy(usersList)
    for user in myList:
        user.activeAds = []

    with open(dataFile, 'wb') as handle:
        pickle.dump(myList, handle, protocol=pickle.HIGHEST_PROTOCOL)

def init():
    loadData()

    for user in usersList:
        getActiveAds(user)

def getUsersList() -> list[User]:
    return usersList
