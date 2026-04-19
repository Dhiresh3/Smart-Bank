#Make a report on plastic usage in the world and using graphics with images in python
import matplotlib.pyplot as plt

plastic_usage = [300, 320, 340, 360, 380] 
years = [2015, 2016, 2017, 2018, 2019]

plt.plot(years, plastic_usage)
plt.xlabel('Year')
plt.ylabel('Plastic Usage (million tons)')
plt.title('Plastic Usage in the World')
plt.grid(True)
plt.show()

single_use_plastics = 40  
recyclable_plastics = 30  
non_recyclable_plastics = 30  


labels = ['Single Use Plastics', 'Recyclable Plastics', 'Non-Recyclable Plastics']
sizes = [single_use_plastics, recyclable_plastics, non_recyclable_plastics]
plt.pie(sizes, labels=labels, autopct='%1.1f%%')
plt.title('Types of Plastics')
plt.show()


plastic_waste_management_costs = [2.2, 2.5, 2.8, 3.1, 3.4]  
years = [2015, 2016, 2017, 2018, 2019]

plt.bar(years, plastic_waste_management_costs)
plt.xlabel('Year')
plt.ylabel('Plastic Waste Management Costs (trillion USD)')
plt.title('Plastic Waste Management Costs')
plt.grid(True)
plt.show()

from PIL import Image
img = Image.open('plastic_waste.jpg')
img.show()