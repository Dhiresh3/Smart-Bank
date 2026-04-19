# import numpy as np

# array1 = np.array([1,2,3])
# array2 = np.array([[5,6,7],[8,9,10],[11,20,30]])
# array3 = np.array([[[8,9,10],[11,12,14]],[[15,16,17],[21,22,23]]])

# print("Array1:\t ")
# print(array1)
# print("Array2:\t ")
# print(array2)
# print("Array3:\t ")
# print(array3)

# reshaped_1 = array1.reshape((3,1))
# print("Reshaped 1D to 3x1: ",reshaped_1)
# reshaped_2 = array2.reshape((3,3))
# print("Reshaped 2D to 2x3: ",reshaped_2)

# slice1 = array1[0:2]
# print("\nSliced 1D array: ",slice1)
# slice2 = array2[:,1]
# print("\nSliced 1D array: ",slice2)
# slice3 = array3[:,1,:]
# print("\nSliced 1D array: ",slice3)

# index1 = array1[1]
# print("\nIndexing 1D array: ",index1)
# index2 = array1[0]
# print("\nIndexing 1D array: ",index2)
# index3 = array1[1]
# print("\nIndexing 1D array: ",index3)

import numpy as np

array1 = np.array([[1,2,3],[4,5,6],[7,8,9]])
array2 = np.array([[9,8,7],[6,5,4],[3,2,1]])

print(array2 + array1)
print(array2 - array1)
print(array2 * array1)
print(array2 / array1)

vector1 = np.array([1,2,3])
vector2 = np.array([7,8,9])
dot_product = np.dot(vector1 , vector2)
print(dot_product)