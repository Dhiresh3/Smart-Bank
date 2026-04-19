# Dict = {}
# print("Empty Dictionary: ",Dict)

# Dict = {1:'Ironman', 2:'Batman', 3:'Hulk'}
# print("\nDictionary with the use of Integer Keys: ",Dict)

# Dict = {'Name': 'Ram', 1: [10, 20, 30, 40]}
# print("\nDictionary with the use of Mixed Keys: ",Dict)

# Dict = dict({1: 'Alan walker', 2: 'the Fade', 3:'The popular song'})
# print("\nDictionary with the use of dict(): ",Dict)

# Dict = dict([(1, 'Sam'), (2, 'the captain')])
# print("\nDictionary with each item as a pair: ",Dict)

# my_dict = {'name': 'Christina', 'age': 35, 'city': 'London'}
# dict_copy = my_dict.copy()
# print("\nCopied Dictionary:", dict_copy)


# dict = {'Name': 'Sara', 'Age': 19, 'Class': 'SE' , 'Roll no': 170 }
# print ("dict[Name]: ", dict['Name'])
# print ("dict[Roll no]: ", dict['Roll no'])


# dict = {'Name': 'Sara', 'Age': 19, 'Class': 'SE','Roll no': 170}
# print("\nAfter updating:")
# dict['Roll no'] = 171; 
# dict['College'] = "RGIT"; 
# print( "dict['Roll no']: ", dict['Roll no'])
# print ("dict['College']: ", dict['College'])

my_dict = {'name': 'Natasha', 'age': 29, 'city': 'New York'}
print("\nKeys:", my_dict.keys())
print("\nValues:", my_dict.values())
print("Items:", my_dict.items())

dict1 = {'a': 1, 'b': 2}
dict2 = {'b': 3, 'c': 4}
dict1.update(dict2)  
print("\nMerged Dictionary:\n", dict1)

merged_dict = dict1 | dict2
print("\nMerged Dictionary (Python 3.9+):", merged_dict)

my_dict = {'name': 'Natasha', 'age': 29, 'city': 'New York'}

city = my_dict.pop('city') 
print("\nAfter Popping city:\n ", my_dict)

my_dict.clear()  
print("\nAfter Clearing:", my_dict)

