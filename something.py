# make a code to convert cm into meter and inchesusing graphics in python

# import tkinter as tk

# class ConversionApp:
#     def __init__(self, root):
#         self.root = root
#         self.root.title("Conversion App")

#         # Create entry field for centimeters
#         self.cm_label = tk.Label(self.root, text="Centimeters:")
#         self.cm_label.grid(row=0, column=0)
#         self.cm_entry = tk.Entry(self.root)
#         self.cm_entry.grid(row=0, column=1)

#         # Create button to convert
#         self.convert_button = tk.Button(self.root, text="Convert", command=self.convert)
#         self.convert_button.grid(row=1, column=0, columnspan=2)

#         # Create labels to display results
#         self.m_label = tk.Label(self.root, text="Meters:")
#         self.m_label.grid(row=2, column=0)
#         self.m_result = tk.Label(self.root, text="")
#         self.m_result.grid(row=2, column=1)

#         self.inches_label = tk.Label(self.root, text="Inches:")
#         self.inches_label.grid(row=3, column=0)
#         self.inches_result = tk.Label(self.root, text="")
#         self.inches_result.grid(row=3, column=1)

#     def convert(self):
#         try:
#             cm = float(self.cm_entry.get())
#             meters = cm / 100
#             inches = cm / 2.54
#             self.m_result.config(text=str(meters))
#             self.inches_result.config(text=str(inches))
#         except ValueError:
#             self.m_result.config(text="Invalid input")
#             self.inches_result.config(text="Invalid input")

# if __name__ == "__main__":
#     root = tk.Tk()
#     app = ConversionApp(root)
#     root.mainloop()

#Make a code to convert celcius into fahrenheit and kelvin using graphics

import tkinter as tk

class ConversionApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Conversion App")

        # Create entry field for Celsius
        self.celsius_label = tk.Label(self.root, text="Celsius:")
        self.celsius_label.grid(row=0, column=0)
        self.celsius_entry = tk.Entry(self.root)
        self.celsius_entry.grid(row=0, column=1)

        # Create button to convert
        self.convert_button = tk.Button(self.root, text="Convert", command=self.convert)
        self.convert_button.grid(row=1, column=0, columnspan=2)

        # Create labels to display results
        self.fahrenheit_label = tk.Label(self.root, text="Fahrenheit:")
        self.fahrenheit_label.grid(row=2, column=0)
        self.fahrenheit_result = tk.Label(self.root, text="")
        self.fahrenheit_result.grid(row=2, column=1)

        self.kelvin_label = tk.Label(self.root, text="Kelvin:")
        self.kelvin_label.grid(row=3, column=0)
        self.kelvin_result = tk.Label(self.root, text="")
        self.kelvin_result.grid(row=3, column=1)

        self.error_label = tk.Label(self.root, text="")
        self.error_label.grid(row=4, column=0, columnspan=2)

    def convert(self):
        try:
            celsius = float(self.celsius_entry.get())
            fahrenheit = (celsius * 9/5) + 32
            kelvin = celsius + 273.15
            self.fahrenheit_result.config(text=str(fahrenheit))
            self.kelvin_result.config(text=str(kelvin))
            self.error_label.config(text="")
        except ValueError:
            self.fahrenheit_result.config(text="")
            self.kelvin_result.config(text="")
            self.error_label.config(text="Invalid input. Please enter a numeric value.")

if __name__ == "__main__":
    root = tk.Tk()
    app = ConversionApp(root)
    root.mainloop()