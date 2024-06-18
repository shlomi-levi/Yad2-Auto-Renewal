import logic
from user import User

OPERATION_ACTIVATE = 1
OPERATION_DEACTIVATE = 0

def viewUsers():
    users:list[User] = logic.getUsersList()

    numofUsers = len(users)

    if not numofUsers:
        print("There are currently no users in the bot")
        return

    print(f"There are currently {numofUsers} in the bot:")

    for user in users:
        activeStatus = logic.isUserThreadActive(user)
        activeString = "Active" if activeStatus else "Not active"
        print(f"{user.email} ({activeString})")

def activateUser(email:str):
    userObj:User = logic.getUserObject(email)

    if not userObj:
        print("Error: unknown user")
        return

    activateOrDeactivateUser(userObj, OPERATION_ACTIVATE)

def deactivateUser(email:str):
    userObj: User = logic.getUserObject(email)

    if not userObj:
        print("Error: unknown user")
        return

    activateOrDeactivateUser(userObj, OPERATION_DEACTIVATE)

def removeUser(email:str):
    userObj: User = logic.getUserObject(email)

    if not userObj:
        print("Error: unknown user")
        return

    logic.removeUser(userObj)

def removeAll():
    users:list[User] = logic.getUsersList()

    for user in users:
        logic.removeUser(user)

def activateAll():
    users: list[User] = logic.getUsersList()

    for user in users:
        userActive = logic.isUserThreadActive(user)

        if userActive:
            continue

        activateUser(user.email)

def deactivateAll():
    users: list[User] = logic.getUsersList()

    for user in users:
        userActive = logic.isUserThreadActive(user)

        if not userActive:
            continue

        deactivateUser(user.email)

def getInput():
    inp = input()

    # Command Name -> (Number of arguments [including command name], Handling function)
    commandMap:dict[str, tuple[int, callable]] = {
        "help": (1, showHelp),
        "users": (1, viewUsers),
        "quit": (1, quit),
        "activate": (2, activateUser),
        "deactivate": (2, deactivateUser),
        "add": (3, addHandler),
        "remove": (2, removeUser),
        "removeall": (1, removeAll),
        "activateall": (1, activateAll),
        "deactivateall": (1, deactivateAll)
    }

    parsedLine = inp.split()

    command, numOfArguments = parsedLine[0], len(parsedLine)

    if command not in commandMap:
        print("Error: invalid command")
        return

    requestedCommNumOfArgs, handlingFunc = commandMap[command]

    if numOfArguments != requestedCommNumOfArgs:
        print("Error: invalid number of arguments")
        return

    if numOfArguments == 1:
        handlingFunc()

    elif numOfArguments == 2:
        handlingFunc(parsedLine[1])

    elif numOfArguments == 3:
        handlingFunc(parsedLine[1], parsedLine[2])

def showHelp():
    print("""Welcome to the Yad 2 Auto Bump program!\n
    Here are the available commands:\n
    - 'help': Displays a list of available commands.\n
    - 'add <email> <password>': Adds a user to the bot.\n
    - 'users': Shows a list of users currently in the bot.\n
    - 'activate <email>': Initiates the bot for a specific user (multiple users can run simultaneously).\n
    - 'activateall': Activates the bot for all the users in the system\n
    - 'deactivate <email>': Deactivates the bot for the specified user\n
    - 'deactivateall': Deactivates the bot for all the users in the system \n
    - 'remove <email>': Removes the user from the bot\n
    - 'removeall': Removes all the users from the bot\n
    - 'quit': Terminates the program (alternatively, you can close the command-line window)
    """)

def main():
    showHelp()
    logic.init()

    while True:
        getInput()

def addHandler(email:str, password:str):
    if not email or not password:
        print("Error: invalid input. Current usage is 'add <email> <password>'")
        return

    if logic.emailExists(email):
        print("Error: a user with this email address already exists")
        return

    status = logic.addUser(email, password)

    if not status:
        print("Error: cannot authorize on Yad2 server - email/password might be incorrect, or Yad2's server is currently down")

    print("User added successfully.")

def activateOrDeactivateUser(u:User, operation):
    userActive = logic.isUserThreadActive(u)

    if userActive and operation == OPERATION_ACTIVATE:
        print("Error: trying to activate the bot for a user that is already activated")
        return

    if not userActive and operation == OPERATION_DEACTIVATE:
        print("Error: trying to deactivate the bot for a user that is not currently activated")
        return

    if userActive:
        logic.deactivateUser(u)

    else:
        logic.activateUser(u)

if __name__ == '__main__':
    main()
