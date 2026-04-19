# import matplotlib.pyplot as plt

# a1 = [1,2,3,4,5]
# a2 = [12,13,14,15,16]
# y = plt.bar(a1,a2)
# print(y)
# plt.xlabel('X-axis')
# plt.ylabel('Y-axis')
# plt.title('Bar Plot')
# #plt.grid(True)
# plt.show()

# import matplotlib.pyplot as plt
# import numpy as np

# data = np.random.randn(1000)

# plt.hist(data, bins=30, color='skyblue', edgecolor='black')

# plt.xlabel('Values')
# plt.ylabel('Frequency')
# plt.title('Histogram Example')
# plt.show()

# import matplotlib.pyplot as plt
# import numpy as np

# d = np.random.randn(2000)
# plt.hist(d,bins = 25, color = 'cyan', edgecolor = 'Black')
# plt.title("Histogram")
# plt.xlabel("Values")
# plt.ylabel("Frequency")
# plt.show()
# import matplotlib.pyplot as plt
# import numpy as np

# t_d = ('Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday')
# a = [10,20,30,40,50,60,70]

# p = plt.plot(t_d,a,color = 'orange',label = "Points")
# print(p)
# plt.figure(figsize = (10,5))
# plt.title("Line")
# plt.xlabel("Days")
# plt.ylabel("Numbers")
# plt.legend(loc = "Bottom Right")
# plt.show()

import matplotlib.pyplot as plt
import numpy as np

t_d = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
a = [10, 20, 30, 40, 50, 60, 70]
b = [1, 2, 3, 4, 5, 6, 7]

#plt.figure(figsize=(10, 5))
# plt.plot(t_d, a, color='cyan', label='Sets', linestyle="dotted",marker = "*")
# plt.plot(t_d, b, color='orange', label="Points",marker = "o")
exp = [0,0,0.7,0,0,0,0]
plt.pie(a,labels = a,explode =exp,shadow = 'true',autopct = "%0.1f%%")
#plt.xlabel("Days", fontsize=16)
plt.ylabel("Numbers", fontsize=16)
plt.title("Pie")
plt.legend(loc="upper left")
#plt.grid(linestyle = "dashed")
plt.xticks(rotation = 15)
#plt.yticks(np.arange(0,80,10),rotation = 15)
plt.show()



