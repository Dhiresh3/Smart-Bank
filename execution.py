try:
    x = int(input("Enter first Number: "))
    y = int(input("Enter second Number: "))
    result = x/y

except ZeroDivisionError:
    print("Error: Division by zero is not allowed. ")
except ValueError:
    print("Error invalid input. Please enter numeric value ")
except Exception as e:
    print("An unexpected error occurred : ",e)
else: 
    print("Result: ",result)
finally:
    print("Execution completed. ")
       