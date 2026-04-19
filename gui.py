import tkinter as tk
from tkinter import messagebox

def on_submit():
    name = name_entry.get()
    branch = branch_entry.get()
    subject = subject_entry.get()

    message = f"Hello {name}! You have selected branch {branch}.\nYour Favourite subject is {subject}."

    messagebox.showinfo("Registration Successful!",message)

root = tk.Tk()
root.title("College Admission Form Registration")
root.geometry("400x200")

tk.Label(root,text = "Name:",font = "Stencil").grid(row=0,column=0,pady=10,padx=10,sticky = "w")
name_entry = tk.Entry(root)
name_entry.grid(row=0,column=1,pady=10,padx=10)

tk.Label(root,text = "Branch:",font = "Stencil").grid(row=1,column=0,pady=10,padx=10,sticky = "w")
branch_entry = tk.Entry(root)
branch_entry.grid(row=1,column=1,pady=10,padx=10) 

tk.Label(root,text = "Subject:",font = "Stencil").grid(row=2,column=0,pady=10,padx=10,sticky = "w")
subject_entry = tk.Entry(root)
subject_entry.grid(row=2,column=1,pady=10,padx=10)

submit_button = tk.Button(root,text="Submit",command=on_submit,font="gabriola",bg="Cyan",fg="Black")
submit_button.grid(row=3,column=0,columnspan=2,pady=20)

root.mainloop()