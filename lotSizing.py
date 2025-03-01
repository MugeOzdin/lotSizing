import csv
import operator
import matplotlib.pyplot as plt
import numpy as np


#settings 
perishement = 24
sup_file_path = "sup_data6.csv"
dem_file_path = "dem_data6.csv"
weekly_holding_cost_constant = 0.005


# class definition start
class demand:

	def __init__(self, raw_material_no, week, amount):
	    
	    self.raw_material_no = raw_material_no
	    self.week = week
	    self.amount = amount

class supplier:

	def __init__(self, supplier_no, joint_cost, lead_time):
	    
	    self.supplier_no = supplier_no
	    self.joint_cost = joint_cost
	    self.lead_time = lead_time


class supplier_raw_material: 

	'''
    Each supplier has a price list: Pricebook
	In this list, each element shows the price of a product: Pricebookentry
	We named the pricebookentry as supplier_raw_material here.
	'''

	def __init__(self, supplier_no, raw_material_no, unit_price, fixed_cost):
	    
	    self.supplier_no = supplier_no
	    self.raw_material_no = raw_material_no
	    self.unit_price = unit_price
	    self.fixed_cost = fixed_cost


class purchase_order:

	'''
    The purchase order will have at least one order line within this order. 
	We keep these order line(s) in the purchase_order_items list.
	'''

	def __init__(self, supplier_no, week, lead_time, joint_cost, order_week):
	    
		self.supplier_no = supplier_no
		self.week = week	    
		self.lead_time = lead_time
		self.joint_cost = joint_cost
		self.purchase_order_items = []
		self.fixed_cost = 0
		self.holding_cost = 0
		self.total_variable_cost = 0

	def print(self):

		print('supplier no:', self.supplier_no)
		print('week:', self.week)
		print('lead time:', self.lead_time)
		print('joint cost:', self.joint_cost)
		
		print('holding cost:', self.holding_cost)
		print('fixed cost:', self.fixed_cost)
		print('total variable cost:', self.total_variable_cost)

		print('Batch total:', self.holding_cost + self.fixed_cost + self.total_variable_cost)

		print(len(self.purchase_order_items), 'item(s) batched')


	def calculate(self):

		for POItem in self.purchase_order_items:
			
			self.holding_cost = self.holding_cost + (POItem.max_order_week - self.week) * POItem.weekly_holding_cost

			self.fixed_cost = self.fixed_cost + POItem.fixed_cost

			self.total_variable_cost = self.total_variable_cost + POItem.unit_price * POItem.amount


class purchase_order_item:

	'''
    Each order contains information such as the order date, the company/person to whom the order was placed, the person/company who placed the order, and the total price.
	In addition, a list of which products or services are subject to order is displayed.
	This class was created to keep the information of the elements of this list. 
	This class includes information such as product information, quantity and price.   
	'''

	def __init__(self, raw_material_no, amount, unit_price, fixed_cost, max_order_week, supplier_no):
	    
	    self.raw_material_no = raw_material_no
	    self.amount = amount
	    self.unit_price = unit_price
	    self.fixed_cost = fixed_cost
	    self.max_order_week = max_order_week
	    self.supplier_no = supplier_no
	    self.weekly_holding_cost = self.amount * weekly_holding_cost_constant #fixed holding cost is 0.25
	    self.in_po = False

	def print(self):

		print('\tmaterial no:', self.raw_material_no)
		print('\tamount:', self.amount)
		print('\tunit price:', self.unit_price)
		print('\tfixed cost:', self.fixed_cost)
		print('\tmax week to order:', self.max_order_week)
		print('\tsupplier no:', self.supplier_no)
		print('\tweekly holding cost:', self.weekly_holding_cost)

# class definition end


# global variables
demands = []
suppliers = []
supplier_raw_materials = []
srm_supplier_dict = {} # We keep supplier_raw_material as the key and supplier as the value.
supplierno_supplier_dict = {} # We keep supplier_no as the key and supplier as the value.
cheapest_suitable_srm = None
POList = [] # order list
POItemList = [] # list of order lines
Inventory_Status = [] # It contains the status of inventory stock status on a weekly basis.


for i in range(0,number_of_weeks):

	Inventory_Status.append(0) # every distinctive week of inventory starts with 0 amount of items

'''
Inventory is a structure similar to stock status. It is assumed that the products arriving on demand in the same week are sent to the customer before they are in stock. 
With this structure, we see how much space they would take up if they were in stock.
'''
Momentary = [] 

for i in range(0,number_of_weeks):

	Momentary.append(0) # every distinctive week of inventory starts with 0 amount of items

#importing demand data
with open(dem_file_path) as csv_file:
	csv_reader = csv.reader(csv_file, delimiter=',')

	first_line = True

	for row in csv_reader:
	    
		if first_line == True:

			first_line = False

			continue

		for t in range(1,number_of_weeks+1):

			#print(len(row))
			#print(t)
			if float(row[t]) == 0:

				continue

			d = demand(row[0], t, float(row[t]))

			demands.append(d)

			#print(d.raw_material_no, d.week, d.amount) // checking if we created demands correctly

'''
#checkpoint for demand list in order to get we store demands correctly
for a in demands:


	print(a.raw_material_no, a.week, .amount)
'''


supplier1 = supplier('1', 150, 5)
supplier2 = supplier('2', 100, 3)
supplier3 = supplier('3', 50, 1)

suppliers.append(supplier1)
suppliers.append(supplier2)
suppliers.append(supplier3)

#importing supplier material data
with open(sup_file_path) as csv_file:

	csv_reader = csv.reader(csv_file, delimiter=',')

	first_line = True

	for row in csv_reader:
	    
		if first_line == True:

			first_line = False

			continue

		srm = supplier_raw_material(row[0], row[1], float(row[2]), float(row[3]))

		#print(row[0], row[1], row[2], row[3])

		supplier_raw_materials.append(srm)



'''
#checkpoint for supplier_raw_materials list in order to get we store supplier_raw_materials correctly
for a in supplier_raw_materials:

	print(a.supplier_no, a.raw_material_no, a.unit_price, a.fixed_cost)
'''


'''
filling our global dictionaries which contains supplier raw materials as keys and suppliers as values
this dicts helps us finding the data easily, beside this, the dicts have no meaning
'''
for srm in supplier_raw_materials: 

	for sup in suppliers:

		supplierno_supplier_dict[sup.supplier_no] = sup

		if sup.supplier_no == srm.supplier_no:

			srm_supplier_dict[srm] = sup

			break



# for each demand, finding the cheapest suitable supplier raw material and we create purchase order items using them
for d in demands:

	# create purchase order & purchase order item
	cheapest_suitable_srm = None

	# loop for finding the cheapest srm
	for srm in supplier_raw_materials:

		if srm.raw_material_no == d.raw_material_no:

			if cheapest_suitable_srm == None:

				cheapest_suitable_srm = srm

			elif ((cheapest_suitable_srm.unit_price * d.amount) + cheapest_suitable_srm.fixed_cost) > ((srm.unit_price * d.amount) + srm.fixed_cost):

				cheapest_suitable_srm = srm


	

	max_order_week = d.week - srm_supplier_dict[cheapest_suitable_srm].lead_time
	
	PO_Item = purchase_order_item(cheapest_suitable_srm.raw_material_no, d.amount, cheapest_suitable_srm.unit_price, cheapest_suitable_srm.fixed_cost, max_order_week, cheapest_suitable_srm.supplier_no)

	POItemList.append(PO_Item)
	#PO.purchase_order_items.append(PO_Item)
	
	#POList.append(PO)

PO_Items_Grouped_By_Supplier = dict()
PO_Items_Grouped_By_Supplier["1"] = dict()
PO_Items_Grouped_By_Supplier["2"] = dict()
PO_Items_Grouped_By_Supplier["3"] = dict()


#grouping purchase order items based on suppliers
for POItem in sorted(POItemList, key=operator.attrgetter('max_order_week')): # iterating elemnts in the list sorted by max_order_week in ascending order


	if PO_Items_Grouped_By_Supplier[POItem.supplier_no].get(POItem.max_order_week) == None:

		PO_Items_Grouped_By_Supplier[POItem.supplier_no][POItem.max_order_week] = []


	PO_Items_Grouped_By_Supplier[POItem.supplier_no][POItem.max_order_week].append(POItem)



#creating purchase orders and putting appropriate purchase order items into them.
print('changes are below\n')
for supplier_no in PO_Items_Grouped_By_Supplier: # for each supplier
	
	for week in PO_Items_Grouped_By_Supplier[supplier_no]: # for each week

		PO = purchase_order(supplier_no, week, supplierno_supplier_dict[supplier_no].lead_time, supplierno_supplier_dict[supplier_no].joint_cost, week) # create PO for each week

		for POItem in PO_Items_Grouped_By_Supplier[supplier_no][week]:

			if POItem.in_po == True: 

				continue

			PO.purchase_order_items.append(POItem)

			POItem.in_po = True

		for next_week in PO_Items_Grouped_By_Supplier[supplier_no]: # calculate total holding costs of next weeks

			if week >= next_week : 

				continue 

			#print('week:', week, ' next_week:', next_week)
			diff = next_week - week

			if diff >= perishement: # it will be perished if greater than or equal to 24

				continue

			item_moved = True

			while item_moved:

				item_moved = False
				
				item_counter = 0
				total_item_count = 0

				for POItem in PO_Items_Grouped_By_Supplier[supplier_no][next_week]: 

					if POItem.in_po != True: 

						total_item_count = total_item_count + 1

				for POItem in PO_Items_Grouped_By_Supplier[supplier_no][next_week]: 

					if POItem.in_po == True: 

								continue

					holding_cost = POItem.weekly_holding_cost * diff

					fixed_cost_profit = 0
					for itemInPO in PO.purchase_order_items:

						if itemInPO.raw_material_no == POItem.raw_material_no:

							fixed_cost_profit = POItem.fixed_cost

					#print('week:', next_week)
					#print('holding_cost:', holding_cost)
					
					if item_counter == total_item_count - 1:


						if holding_cost - fixed_cost_profit < supplierno_supplier_dict[supplier_no].joint_cost: # put feasible next weeks' purchase order items to current week's purchase order

								inventory_flag = False
								for t in range(week, POItem.max_order_week):

									if Inventory_Status[t + PO.lead_time - 1]  + POItem.amount > 3500 * 1000:

										# inventory is full, cannot be purchased this week
										inventory_flag = True

										break
										

								
								if 	inventory_flag == True: 

									continue

								else:

									for t in range(week, POItem.max_order_week):

										Inventory_Status[t + PO.lead_time - 1] =  Inventory_Status[t + PO.lead_time - 1]  + POItem.amount

										
									

								if fixed_cost_profit > 0:

									POItem.fixed_cost = 0

								PO.purchase_order_items.append(POItem)

								print('from', next_week, ' to', week)
								POItem.print()

								POItem.in_po = True

								item_moved = True

								item_counter = item_counter + 1

					else:

						if fixed_cost_profit - holding_cost > 0: # put feasible next weeks' purchase order items to current week's purchase order

								inventory_flag = False
								for t in range(week, POItem.max_order_week):

									if Inventory_Status[t + PO.lead_time - 1]  + POItem.amount > 3500 * 1000:

										# inventory is full, cannot be purchased this week

										inventory_flag = True

										break
										

								
								if 	inventory_flag == True: 

									continue

								else:

									for t in range(week, POItem.max_order_week):

										print('t:', t)
										Inventory_Status[t + PO.lead_time - 1] =  Inventory_Status[t + PO.lead_time - 1]  + POItem.amount


									
								if fixed_cost_profit > 0:

									POItem.fixed_cost = 0

								PO.purchase_order_items.append(POItem)

								print('from', next_week, ' to', week)
								POItem.print()

								POItem.in_po = True

								item_moved = True

								item_counter = item_counter + 1



		POList.append(PO)




#printing created purchase orders and items to screen
print('\n###############################################################################################')
print('\n###############################################################################################')
print('\n###############################################################################################\n')
print('POItems grouped by PO below\n')




print('Supplier No', '\t', 'Week' , '\t', 'Item Count')

total_fixed_cost = 0
total_holding_cost = 0
total_unit_variable_cost = 0
total_joint_cost = 0
total_cost = 0

for PO in POList:

	PO.calculate()

	if len(PO.purchase_order_items) <= 0: 

		continue


	total_fixed_cost = total_fixed_cost + PO.fixed_cost
	total_holding_cost = total_holding_cost + PO.holding_cost
	total_unit_variable_cost = total_unit_variable_cost + PO.total_variable_cost
	total_joint_cost = total_joint_cost + PO.joint_cost


	print('\n>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>>\n')

	PO.print()
	print('')

	for POItem in PO.purchase_order_items:

		POItem.print()
		print('')

		if POItem.max_order_week == PO.week:

			Momentary[PO.week + PO.lead_time - 1] =  Momentary[PO.week + PO.lead_time - 1]  + POItem.amount

total_cost = total_cost + total_fixed_cost + total_holding_cost + total_unit_variable_cost + total_joint_cost


print('total fixed cost:', total_fixed_cost, 'EUR')
print('total holding cost:', total_holding_cost, 'EUR')
print('total unit variable cost:', total_unit_variable_cost, 'EUR')
print('total joint cost:', total_joint_cost, 'EUR')
print('grand total cost:', total_cost, 'EUR')



y_pos = np.arange(len(Inventory_Status))
height = Inventory_Status
plt.bar(y_pos, Momentary, color = 'y', align='center')
plt.bar(y_pos, height, color = 'g', align='center')


# If we have long labels, we cannot see it properly
x_pos = []
for i in range(1,number_of_weeks+1):

	x_pos.append(i)

plt.xticks(y_pos, x_pos, rotation=90)

# Thus we have to give more margin:
plt.subplots_adjust(bottom=0.4)

# It's the same concept if you need more space for your titles
plt.title("Weekly inventory status")
plt.subplots_adjust(top=0.7)

plt.show()

