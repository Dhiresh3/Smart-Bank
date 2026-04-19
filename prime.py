# def prime(n):
#     if n<=1:
#         return False
#     for i in range(2,int(n/2)+1): 
#         if n % i  == 0:
#          return False
#         return True

# n = int(input("Enter the number: "))
# if prime(n):
#    print(n, "is prime no. ")
# else:
#    print(n,"is not prime no. ")



def add(n1,n2):
    return n1 +n2
def sub(n1,n2):
    return n1-n2
def mul(n1,n2):
    return n1 * n2
def div(n1,n2):
    return n1 / n2
def mod(n1,n2):
    return n1 % n2

n1 = int(input("Enter a number: "))
n2 = int(input("Enter the number: "))
print("Enter your choice:\n 1 add\n 2 sub \n 3 mul\n 4 div\n 5 mod\n")
h = int(input(" "))
if h == 1:
    print(add(n1,n2))
elif h == 2:
    print(sub(n1,n2))
elif h == 3:
    print(mul(n1,n2))
elif h == 4:
    print(div(n1,n2))
elif h == 5:
    print(mod(n1,n2))
else: 
    print("Invalid!")

     