import random

target = random.randint(1,100)

while True:
     choice = input("Guess the choice or Quit(Q): ")
     if(choice == "Q"):
      break

     choice = int(choice)
     if(choice == target):
       print("Success! Great Choice!")
       break
     elif(choice > target):
            print("Too big,Guess smaller one")
     else:
            print("Too small,Guess bigger one")
    
    
    
print("~~~Game Over~~~")    