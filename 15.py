import re
phone = input("Enter Your Phone Number: ")
email = input("Enter Your Email ID: ")

if re.match(r'^[0-9]\d{9}$',phone):
    print("Valid phone number")
else: 
    print("Invalid phone number(Must start with 0-9 and be 10 digits)")

if re.match(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$',email):
    print("Valid Email ID")
else:
    print("Invalid Email ID")