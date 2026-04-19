#write code using function for prime number

def prime(n):
    i=2
    while i<n:  
        if n%i==0:
            return False
        i+=1
    return True 

n=int(input("Enter the number: "))
if prime(n):
    print(f"{n} is a prime number")
else:
    print(f"{n} is not a prime number") 