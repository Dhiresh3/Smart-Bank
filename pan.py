
# a1 = [10,20,30,40,50]
# t = pd.Series(a1)
# print(t)
# print(type(t))

# c = {'a':4,'d':6,'o':1}
# p  = pd.Series(c)
# print(p)

# f = {'Countries': ['India','Japan','Russia','Srilanka'],'States':['Maharashtra','Tokyo','Moscow','Colombo'],'Dishes':['Vada Pav','Sushi','Borscht','Kottu Roti']}
# T = pd.DataFrame(f)

# print(T.dtypes)
# print(T.shape)
import numpy as np
import pandas as pd

np.random.seed(12)
b1 = np.random.randint(35, 51, (2, 3)) 
print(b1)

s = ['Raj', 'Ravi', 'Ram']
sub = ['Maths', 'Physics', 'Chemistry']

marks = pd.DataFrame(b1, index=s[:2], columns=sub)  
#print(marks)
#print(marks['Maths'])
# print(marks.describe())
# print(marks.info())
# print(marks.sum())#
marks['Total'] = marks.sum(axis=1)  
marks['Percentage'] = round((marks['Total'] / 200) * 100, 2)

print(marks[['Total', 'Percentage']])
marks = marks.drop(columns = ['Total', 'Percentage'])  
print(marks)