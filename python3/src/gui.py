#!../bin/python
import tkinter as tk
import robin_stocks.robinhood as r


def close_app():
    window.destroy()

def login():
    # Get values from entry fields
    username = usernameEntry.get()
    password = passwordEntry.get()
    mfa_code = mfaEntry.get()
    login = r.login(username, password, mfa_code=mfa_code)
    # Print or use the gathered values as needed
    print(login) 

if __name__ == "__main__":
    GREEN = "#11ce98"
    window = tk.Tk()
    window.title("Robinhood Login")
    window.minsize(400, 300)

    rootFrame = tk.Frame(window, bg=GREEN)
    rootFrame.pack(expand=True, fill="both")

    topBar = tk.Frame(rootFrame, bg="gray")
    topBar.pack(side="top", fill="x")

    close_button = tk.Button(topBar, text="Close", command=close_app)
    close_button.pack(side="right")

    loginFrame = tk.Frame(rootFrame, bg=GREEN)
    loginFrame.place(relx=0.5, rely=0.5, anchor="center")

    usernameLabel = tk.Label(loginFrame, text="Username:", bg=GREEN)
    usernameLabel.grid(row=0, column=0, padx=10, pady=5)
    usernameEntry = tk.Entry(loginFrame, width=30)
    usernameEntry.grid(row=0, column=1, padx=10, pady=5)

    passwordLable = tk.Label(loginFrame, text="Password:", bg=GREEN)
    passwordLable.grid(row=1, column=0, padx=10, pady=5)
    passwordEntry = tk.Entry(loginFrame, show="*", width=30)
    passwordEntry.grid(row=1, column=1, padx=10, pady=5)

    mfaLabel = tk.Label(loginFrame, text="MFA Code:", bg=GREEN)
    mfaLabel.grid(row=2, column=0, padx=10, pady=5)
    mfaEntry = tk.Entry(loginFrame, width=30)
    mfaEntry.grid(row=2, column=1, padx=10, pady=5)

    login_button = tk.Button(loginFrame, text="Log In", command=login)
    login_button.grid(row=3, column=0, columnspan=2, padx=10, pady=5)

    window.mainloop()
