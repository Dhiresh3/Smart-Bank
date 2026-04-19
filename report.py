#make report card of studentand assign grade according to markswith graphics 
# import tkinter as tk
# from tkinter import messagebox

# class ReportCard:
#     def __init__(self):
#         self.window = tk.Tk()
#         self.window.title("Report Card")

#         self.name_label = tk.Label(self.window, text="Student Name:")
#         self.name_label.grid(row=0, column=0)
#         self.name_entry = tk.Entry(self.window)
#         self.name_entry.grid(row=0, column=1)

#         self.maths_label = tk.Label(self.window, text="Maths Marks:")
#         self.maths_label.grid(row=1, column=0)
#         self.maths_entry = tk.Entry(self.window)
#         self.maths_entry.grid(row=1, column=1)

#         self.science_label = tk.Label(self.window, text="Science Marks:")
#         self.science_label.grid(row=2, column=0)
#         self.science_entry = tk.Entry(self.window)
#         self.science_entry.grid(row=2, column=1)

#         self.english_label = tk.Label(self.window, text="English Marks:")
#         self.english_label.grid(row=3, column=0)
#         self.english_entry = tk.Entry(self.window)
#         self.english_entry.grid(row=3, column=1)

#         self.compute_button = tk.Button(self.window, text="Compute Grade", command=self.compute_grade)
#         self.compute_button.grid(row=4, column=0, columnspan=2)

#         self.grade_label = tk.Label(self.window, text="Grade:")
#         self.grade_label.grid(row=5, column=0)
#         self.grade_display = tk.Label(self.window, text="")
#         self.grade_display.grid(row=5, column=1)

#     def compute_grade(self):
#         try:
#             maths_marks = float(self.maths_entry.get())
#             science_marks = float(self.science_entry.get())
#             english_marks = float(self.english_entry.get())

#             total_marks = maths_marks + science_marks + english_marks
#             average_marks = total_marks / 3

#             if average_marks >= 90:
#                 grade = "A"
#             elif average_marks >= 80:
#                 grade = "B"
#             elif average_marks >= 70:
#                 grade = "C"
#             elif average_marks >= 60:
#                 grade = "D"
#             else:
#                 grade = "F"

#             self.grade_display.config(text=grade)
#         except ValueError:
#             messagebox.showerror("Error", "Invalid input")

#     def run(self):
#         self.window.mainloop()

# if __name__ == "__main__":
#     report_card = ReportCard()
#     report_card.run()


import tkinter as tk
from tkinter import messagebox

class ReportCard:
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("Report Card")

        self.name_label = tk.Label(self.window, text="Student Name:")
        self.name_label.grid(row=0, column=0)
        self.name_entry = tk.Entry(self.window)
        self.name_entry.grid(row=0, column=1)

        self.maths_label = tk.Label(self.window, text="Maths Marks:")
        self.maths_label.grid(row=1, column=0)
        self.maths_entry = tk.Entry(self.window)
        self.maths_entry.grid(row=1, column=1)

        self.science_label = tk.Label(self.window, text="Science Marks:")
        self.science_label.grid(row=2, column=0)
        self.science_entry = tk.Entry(self.window)
        self.science_entry.grid(row=2, column=1)

        self.english_label = tk.Label(self.window, text="English Marks:")
        self.english_label.grid(row=3, column=0)
        self.english_entry = tk.Entry(self.window)
        self.english_entry.grid(row=3, column=1)

        self.compute_button = tk.Button(self.window, text="Compute CGPA", command=self.compute_cgpa)
        self.compute_button.grid(row=4, column=0, columnspan=2)

        self.cgpa_label = tk.Label(self.window, text="CGPA:")
        self.cgpa_label.grid(row=5, column=0)
        self.cgpa_display = tk.Label(self.window, text="")
        self.cgpa_display.grid(row=5, column=1)

    def compute_cgpa(self):
        try:
            maths_marks = float(self.maths_entry.get())
            science_marks = float(self.science_entry.get())
            english_marks = float(self.english_entry.get())

            maths_grade = self.get_grade(maths_marks)
            science_grade = self.get_grade(science_marks)
            english_grade = self.get_grade(english_marks)

            maths_cgpa = self.get_cgpa(maths_grade)
            science_cgpa = self.get_cgpa(science_grade)
            english_cgpa = self.get_cgpa(english_grade)

            total_cgpa = (maths_cgpa + science_cgpa + english_cgpa) / 3

            self.cgpa_display.config(text=str(total_cgpa))
        except ValueError:
            messagebox.showerror("Error", "Invalid input")

    def get_grade(self, marks):
        if marks >= 90:
            return "A"
        elif marks >= 80:
            return "B"
        elif marks >= 70:
            return "C"
        elif marks >= 60:
            return "D"
        else:
            return "F"

    def get_cgpa(self, grade):
        if grade == "A":
            return 4.0
        elif grade == "B":
            return 3.0
        elif grade == "C":
            return 2.0
        elif grade == "D":
            return 1.0
        else:
            return 0.0

    def run(self):
        self.window.mainloop()

if __name__ == "__main__":
    report_card = ReportCard()
    report_card.run()