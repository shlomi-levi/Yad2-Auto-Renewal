import tkinter as tk
import applicationLogic
from tkinter import ttk, messagebox
from User import User

root = tk.Tk()

def addUser():
    # Get the cursor's position
    x, y = root.winfo_pointerxy()

    # Create a modal popup for entering email and password
    popup = tk.Toplevel(root)
    popup.title("Add User")
    popup.grab_set()  # Make the popup modal

    # Set the popup's position relative to the cursor
    popup.geometry(f"+{x}+{y}")

    # Create and configure labels and entry fields for email and password with larger fonts
    email_label = tk.Label(popup, text="Email:", font=("Arial", 14))
    email_label.pack()
    email_entry = tk.Entry(popup, font=("Arial", 14))
    email_entry.pack()

    password_label = tk.Label(popup, text="Password:", font=("Arial", 14))
    password_label.pack()
    password_entry = tk.Entry(popup, show="*", font=("Arial", 14))  # Use "*" to hide password characters
    password_entry.pack()

    def save_user():
        email = email_entry.get()
        password = password_entry.get()

        errText = ""

        if email and password:
            if applicationLogic.emailExists(email):
                errText += "A user with this email address already exists!"

            elif not applicationLogic.addUser(email, password):
                errText += "Can't connect to Yad2 server. email/password might be incorrect."
                x, y = root.winfo_pointerxy()

                error_popup = tk.Toplevel(popup)
                error_popup.geometry(f"+{x}+{y}")

                error_popup.geometry("300x100")
                error_popup.title("Error")
                error_popup.geometry("300x100")
                error_label = tk.Label(error_popup, text=errText, font=("Arial", 14))
                error_label.pack(pady=10)
                error_popup.transient(popup)  # Make the error popup dependent on the "Add User" popup

            else:
                popup.destroy()
                refreshGUI()

        else:
            tk.messagebox.showerror("Error", "Both email and password are required.")

    save_button = tk.Button(popup, text="Save", command=save_user, font=("Arial", 14))
    save_button.pack(pady=10)  # Add space between the password field and the button

    # Increase the size of the popup window
    popup.geometry("400x200")

    popup.transient(root)  # Make the popup dependent on the main window

def toggleActivation(status, button_var):
    # Implement the logic to toggle user activation status here
    # Update the text of the button_var based on the updated user status
    button_var.set("Deactivate" if status else "Activate")

def activateOrDeactivateUser(u:User, bv):
    userActive = applicationLogic.isUserThreadActive(u)

    if userActive:
        applicationLogic.deactivateUser(u)

    else:
        applicationLogic.activateUser(u)

    newStatus = not userActive

    toggleActivation(newStatus, bv)

def refreshGUI():
    global root

    root.withdraw()
    root = tk.Tk()
    initGUI()

def removeUser(u:User) -> None:
    applicationLogic.removeUser(u)
    refreshGUI()


def initGUI():
    root.title("Yad2 Auto Renewal")

    # Set the initial window size
    root.geometry("420x300")

    # Create and configure the label with the text "Yad2 Auto Bump"
    label = tk.Label(root, text="Yad2 Auto Bump", font=("Arial", 20), fg="red")
    label.grid(row=0, column=0, columnspan=3, padx=10, pady=20, sticky="n")

    # Create and configure the buttons using ttk for a different style
    button_font = ("Arial", 14)  # Adjust font size as needed

    style = ttk.Style()
    style.configure("TButton", font=button_font)

    usersList = applicationLogic.getUsersList()

    # Create labels, activate buttons, and delete buttons in a loop
    row = 0
    for user in usersList:
        row += 1
        label = tk.Label(root, text=user.email, font=("Arial", 14))
        label.grid(row=row, column=0, padx=10, pady=5, sticky="w")

        userActive = applicationLogic.isUserThreadActive(user)

        button_text = "Deactivate" if userActive else "Activate"
        button_var = tk.StringVar(value=button_text)

        activateOrDeactivate_button = tk.Button(root, textvariable=button_var, font=("Arial", 12), command=lambda u=user, bv=button_var: activateOrDeactivateUser(user, bv))
        activateOrDeactivate_button.grid(row=row, column=1, padx=(0, 5), pady=5, sticky="e")

        delete_button = tk.Button(root, text="Delete", font=("Arial", 12), command=lambda u=user:removeUser(u))
        delete_button.grid(row=row, column=2, padx=(5, 10), pady=5, sticky="e")

    # "Add User" button
    add_user_button = tk.Button(root, text="Add User", command=addUser, font=("Arial", 12))
    add_user_button.grid(row=row + 1, column=0, columnspan=3, padx=10, pady=10, sticky="n")

    # Configure column weights to center-align the label and the button
    root.grid_columnconfigure(0, weight=1)
    root.grid_columnconfigure(1, weight=1)
    root.grid_columnconfigure(2, weight=1)

    # Start the Tkinter main loop
    root.mainloop()

# Initialize application logic
applicationLogic.init()

initGUI()
# Create the main window
