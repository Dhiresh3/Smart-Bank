import pandas as pd 
data1=pd.DataFrame({'id':[1,2,3,4],'name':['Skiller','RAj','Ritika','Vishal']},index=['one','two', 'three','four'])
data2=pd.DataFrame({'s_id':[1,2,3,5,9],'marks':[98,92,99,86,88]},index=['one','two','three', 'five','nine'])

print("Joined DataFrame is as follow:")
print(data1.join(data2))
print("Merged DataFrame is as follow:")
print(pd.merge(data1,data2,left_index=True,right_index=True))
print("Concatenation:")
print(pd.concat([data1,data2],axis=1))
