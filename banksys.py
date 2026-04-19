import tkinter as tk
from tkinter import messagebox
import json
import os
import pyttsx3

DATA_FILE = "accounts.json"

# 🎙️ Voice Setup
engine = pyttsx3.init()

def speak(text):
    engine.say(text)
    engine.runAndWait()

# 🧠 Load/Save Functions
def load_accounts():
    if not os.path.exists(DATA_FILE):
        return []
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_accounts(accounts):
    with open(DATA_FILE, "w") as f:
        json.dump(accounts, f, indent=2)

# 🔐 Find Account
def find_account(acc_no, password):
    accounts = load_accounts()
    for acc in accounts:
        if acc["acc_no"] == acc_no and acc["pass"] == password:
            return acc
    return None

# 🎨 GUI Setup
root = tk.Tk()
root.title("🏦 Python Bank System")
root.geometry("500x400")
root.configure(bg="#f0f8ff")

speak("Welcome to Python Bank!")

status = tk.StringVar()
status.set("Welcome to Python Bank!")

def update_status(msg, color="black"):
    status.set(msg)
    status_label.config(fg=color)

status_label = tk.Label(root, textvariable=status, font=("Arial", 14), bg="#f0f8ff")
status_label.pack(pady=10)

# 📋 Account Creation
def create_account():
    speak("Opening account window")
    def submit():
        name = name_entry.get()
        acc_no = acc_entry.get()
        password = pass_entry.get()
        if not (name and acc_no and password):
            update_status("All fields required!", "red")
            return
        accounts = load_accounts()
        if any(acc["acc_no"] == acc_no for acc in accounts):
            update_status("Account already exists!", "red")
            return
        accounts.append({
            "name": name,
            "acc_no": acc_no,
            "pass": password,
            "balance": 0.0
        })
        save_accounts(accounts)
        update_status("Account created successfully!", "green")
        win.destroy()

    win = tk.Toplevel(root)
    win.title("Open Account")
    win.geometry("400x300")
    tk.Label(win, text="Name").pack()
    name_entry = tk.Entry(win)
    name_entry.pack()
    tk.Label(win, text="Account No").pack()
    acc_entry = tk.Entry(win)
    acc_entry.pack()
    tk.Label(win, text="Password").pack()
    pass_entry = tk.Entry(win, show="*")
    pass_entry.pack()
    tk.Button(win, text="Create", command=submit).pack(pady=10)

# 💰 Deposit
def deposit():
    speak("Deposit window opened")
    def submit():
        acc_no = acc_entry.get()
        password = pass_entry.get()
        try:
            amount = float(amount_entry.get())
        except ValueError:
            update_status("Invalid amount!", "red")
            return
        accounts = load_accounts()
        found = False
        for acc in accounts:
            if acc["acc_no"] == acc_no and acc["pass"] == password:
                acc["balance"] += amount
                found = True
                break
        if found:
            save_accounts(accounts)
            update_status("Deposit successful!", "green")
        else:
            update_status("Account not found!", "red")
        win.destroy()

    win = tk.Toplevel(root)
    win.title("Deposit")
    win.geometry("400x300")
    tk.Label(win, text="Account No").pack()
    acc_entry = tk.Entry(win)
    acc_entry.pack()
    tk.Label(win, text="Password").pack()
    pass_entry = tk.Entry(win, show="*")
    pass_entry.pack()
    tk.Label(win, text="Amount").pack()
    amount_entry = tk.Entry(win)
    amount_entry.pack()
    tk.Button(win, text="Deposit", command=submit).pack(pady=10)

# 💸 Withdraw
def withdraw():
    speak("Withdraw window opened")
    def submit():
        acc_no = acc_entry.get()
        password = pass_entry.get()
        try:
            amount = float(amount_entry.get())
        except ValueError:
            update_status("Invalid amount!", "red")
            return
        accounts = load_accounts()
        found = False
        for acc in accounts:
            if acc["acc_no"] == acc_no and acc["pass"] == password:
                if amount > acc["balance"]:
                    update_status("Insufficient balance!", "red")
                else:
                    acc["balance"] -= amount
                    save_accounts(accounts)
                    update_status("Withdrawal successful!", "green")
                found = True
                break
        if not found:
            update_status("Account not found!", "red")
        win.destroy()

    win = tk.Toplevel(root)
    win.title("Withdraw")
    win.geometry("400x300")
    tk.Label(win, text="Account No").pack()
    acc_entry = tk.Entry(win)
    acc_entry.pack()
    tk.Label(win, text="Password").pack()
    pass_entry = tk.Entry(win, show="*")
    pass_entry.pack()
    tk.Label(win, text="Amount").pack()
    amount_entry = tk.Entry(win)
    amount_entry.pack()
    tk.Button(win, text="Withdraw", command=submit).pack(pady=10)

def check_balance():
    speak("Checking balance")
    def submit():
        acc_no = acc_entry.get()
        password = pass_entry.get()
        acc = find_account(acc_no, password)
        if acc:
            update_status(f"Balance: ₹{acc['balance']:.2f}", "blue")
        else:
            update_status("Account not found!", "red")
        win.destroy()

    win = tk.Toplevel(root)
    win.title("Check Balance")
    win.geometry("400x300")
    tk.Label(win, text="Account No").pack()
    acc_entry = tk.Entry(win)
    acc_entry.pack()
    tk.Label(win, text="Password").pack()
    pass_entry = tk.Entry(win, show="*")
    pass_entry.pack()
    tk.Button(win, text="Check", command=submit).pack(pady=10)

def close_account():
    speak("Closing account")
    def submit():
        acc_no = acc_entry.get()
        password = pass_entry.get()
        accounts = load_accounts()
        new_accounts = [acc for acc in accounts if not (acc["acc_no"] == acc_no and acc["pass"] == password)]
        if len(new_accounts) < len(accounts):
            save_accounts(new_accounts)
            update_status("Account closed successfully.", "green")
        else:
            update_status("Account not found!", "red")
        win.destroy()

    win = tk.Toplevel(root)
    win.title("Close Account")
    win.geometry("400x300")
    tk.Label(win, text="Account No").pack()
    acc_entry = tk.Entry(win)
    acc_entry.pack()
    tk.Label(win, text="Password").pack()
    pass_entry = tk.Entry(win, show="*")
    pass_entry.pack()
    tk.Button(win, text="Close", command=submit).pack(pady=10)

def exit_app():
    speak("Thank you for banking with us")
    root.quit()

for label, command in [
    ("Open Account", create_account),
    ("Deposit", deposit),
    ("Withdraw", withdraw),
    ("Check Balance", check_balance),
    ("Close Account", close_account),
    ("Exit", exit_app)
]:
    tk.Button(root, text=label, font=("Arial", 12), width=20, command=command).pack(pady=5)

root.mainloop()