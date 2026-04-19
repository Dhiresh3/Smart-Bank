# import math

# def calculator():
#     print("Scientific Calculator")
#     print("1. Basic Operations")
#     print("2. Trigonometric Operations")
#     print("3. Exponential Operations")
#     print("4. Logarithmic Operations")
#     print("5. Root Operations")
#     print("6. Quit")

#     while True:
#         choice = input("Enter your choice (1-6): ")

#         if choice == "1":
#             print("Basic Operations")
#             print("1. Addition")
#             print("2. Subtraction")
#             print("3. Multiplication")
#             print("4. Division")

#             basic_choice = input("Enter your choice (1-4): ")

#             if basic_choice == "1":
#                 num1 = float(input("Enter first number: "))
#                 num2 = float(input("Enter second number: "))
#                 print("Result: ", num1 + num2)

#             elif basic_choice == "2":
#                 num1 = float(input("Enter first number: "))
#                 num2 = float(input("Enter second number: "))
#                 print("Result: ", num1 - num2)

#             elif basic_choice == "3":
#                 num1 = float(input("Enter first number: "))
#                 num2 = float(input("Enter second number: "))
#                 print("Result: ", num1 * num2)

#             elif basic_choice == "4":
#                 num1 = float(input("Enter first number: "))
#                 num2 = float(input("Enter second number: "))
#                 if num2 != 0:
#                     print("Result: ", num1 / num2)
#                 else:
#                     print("Error! Division by zero is not allowed.")

#             else:
#                 print("Invalid choice. Please try again.")

#         elif choice == "2":
#             print("Trigonometric Operations")
#             print("1. Sine")
#             print("2. Cosine")
#             print("3. Tangent")

#             trig_choice = input("Enter your choice (1-3): ")

#             if trig_choice == "1":
#                 num = float(input("Enter a number (in degrees): "))
#                 print("Result: ", math.sin(math.radians(num)))

#             elif trig_choice == "2":
#                 num = float(input("Enter a number (in degrees): "))
#                 print("Result: ", math.cos(math.radians(num)))

#             elif trig_choice == "3":
#                 num = float(input("Enter a number (in degrees): "))
#                 print("Result: ", math.tan(math.radians(num)))

#             else:
#                 print("Invalid choice. Please try again.")

#         elif choice == "3":
#             print("Exponential Operations")
#             print("1. Exponentiation")
#             print("2. Natural Exponential")

#             exp_choice = input("Enter your choice (1-2): ")

#             if exp_choice == "1":
#                 num1 = float(input("Enter base number: "))
#                 num2 = float(input("Enter exponent: "))
#                 print("Result: ", num1 ** num2)

#             elif exp_choice == "2":
#                 num = float(input("Enter a number: "))
#                 print("Result: ", math.exp(num))

#             else:
#                 print("Invalid choice. Please try again.")

#         elif choice == "4":
#             print("Logarithmic Operations")
#             print("1. Natural Logarithm")
#             print("2. Base-10 Logarithm")

#             log_choice = input("Enter your choice (1-2): ")

#             if log_choice == "1":
#                 num = float(input("Enter a number: "))
#                 if num > 0:
#                     print("Result: ", math.log(num))
#                 else:
#                     print("Error! Logarithm is not defined for non-positive numbers.")

#             elif log_choice == "2":
#                 num = float(input("Enter a number: "))
#                 if num > 0:
#                     print("Result: ", math.log10(num))
#                 else:
#                     print("Error! Logarithm is not defined for non-positive numbers.")

#             else:
#                 print("Invalid choice. Please try again.")

#         elif choice == "5":
#             print("Root Operations")
#             print("1. Square Root")
#             print("2. Cube Root")

#             root_choice = input("Enter your choice (1-2): ")

#             if root_choice == "1":
#                 num = float(input("Enter a number: "))
#                 if num >= 0:
#                     print("Result: ", math.sqrt(num))
#                 else:
#                     print("Error! Square root is not defined for negative numbers.")

#             elif root_choice == "2":
#                 num = float(input("Enter a number: "))
#                 print("Result: ", round(num ** (1/3), 3))

#             else:
#                 print("Invalid choice. Please try again.")

#         elif choice == "6":
#             print("Goodbye!")
#             break

#         else:
#             print("Invalid choice. Please try again.")

# calculator()


import math
import tkinter as tk
from tkinter import messagebox

class Calculator:
    def __init__(self, root):
        self.root = root
        self.root.title("Scientific Calculator")
        self.entry = tk.Entry(self.root, width=35, borderwidth=5)
        self.entry.grid(row=0, column=0, columnspan=4)

        self.create_buttons()

    def create_buttons(self):
        buttons = [
            '7', '8', '9', '/',
            '4', '5', '6', '*',
            '1', '2', '3', '-',
            '0', '.', '=', '+'
        ]

        row_val = 1
        col_val = 0

        for button in buttons:
            tk.Button(self.root, text=button, width=5, command=lambda button=button: self.click_button(button)).grid(row=row_val, column=col_val)
            col_val += 1
            if col_val > 3:
                col_val = 0
                row_val += 1

        tk.Button(self.root, text="C", width=21, command=self.clear_entry).grid(row=row_val, column=0, columnspan=4)

        row_val += 1

        tk.Button(self.root, text="sin", width=5, command=self.sin).grid(row=row_val, column=0)
        tk.Button(self.root, text="cos", width=5, command=self.cos).grid(row=row_val, column=1)
        tk.Button(self.root, text="tan", width=5, command=self.tan).grid(row=row_val, column=2)
        tk.Button(self.root, text="log", width=5, command=self.log).grid(row=row_val, column=3)

        row_val += 1

        tk.Button(self.root, text="sqrt", width=5, command=self.sqrt).grid(row=row_val, column=0)
        tk.Button(self.root, text="exp", width=5, command=self.exp).grid(row=row_val, column=1)
        tk.Button(self.root, text="pi", width=5, command=self.pi).grid(row=row_val, column=2)
        tk.Button(self.root, text="e", width=5, command=self.e).grid(row=row_val, column=3)

    def click_button(self, button):
        if button == '=':
            try:
                result = eval(self.entry.get())
                self.entry.delete(0, tk.END)
                self.entry.insert(tk.END, str(result))
            except Exception as e:
                messagebox.showerror("Error", str(e))
        else:
            self.entry.insert(tk.END, button)

    def clear_entry(self):
        self.entry.delete(0, tk.END)

    def sin(self):
        try:
            result = math.sin(math.radians(float(self.entry.get())))
            self.entry.delete(0, tk.END)
            self.entry.insert(tk.END, str(result))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def cos(self):
        try:
            result = math.cos(math.radians(float(self.entry.get())))
            self.entry.delete(0, tk.END)
            self.entry.insert(tk.END, str(result))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def tan(self):
        try:
            result = math.tan(math.radians(float(self.entry.get())))
            self.entry.delete(0, tk.END)
            self.entry.insert(tk.END, str(result))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def log(self):
        try:
            result = math.log10(float(self.entry.get()))
            self.entry.delete(0, tk.END)
            self.entry.insert(tk.END, str(result))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def sqrt(self):
        try:
            result = math.sqrt(float(self.entry.get()))
            self.entry.delete(0, tk.END)
            self.entry.insert(tk.END, str(result))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def exp(self):
        try:
            result = math.exp(float(self.entry.get()))
            self.entry.delete(0, tk.END)
            self.entry.insert(tk.END, str(result))
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def pi(self):
        self.entry.insert(tk.END, str(math.pi))

    def e(self):
        self.entry.insert(tk.END, str(math.e))

if __name__ == "__main__":
    root = tk.Tk()
    calc = Calculator(root)
    root.mainloop()