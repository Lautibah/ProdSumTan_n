
def storeValues(n, ProdTan, filename, checkinginteger = False):

	#save found values into txt file

	#check if file already exists
	if os.path.isfile(filename) and checkinginteger == False:
		#store data
		with open(filename, 'a', newline='') as file:
			writer = csv.writer(file, delimiter=' ')
			writer.writerow([n, ProdTan])
	elif ProdTan == 'create' and checkinginteger == True or checkinginteger == False: # does not exist, create file with headers
		with open(filename, 'w', newline='') as file:
			writer = csv.writer(file, delimiter=' ')
			writer.writerow(['n', 'ProdTan'])
			writer.writerow([n, '-']) #this row will be updated to the last checked integer
	else:
		# Read all data from the txt file.
		bottle_list = []
		
		with open(filename, 'rt') as file:
			bottles = csv.reader(file)
			bottle_list.extend(bottles)
		
		line_to_override = {1:[n, '-']}
		
		with open(filename, 'w', newline='') as file:
			writer = csv.writer(file,delimiter=' ')
			for line, row in enumerate(bottle_list):
				data = line_to_override.get(line, row)
				writer.writerow(data)

def PlaceValues(num):
	# split number into its extended form, tens, hundreds, thousands... (place values)
	c = 1
	place_values = []
	while num != 0:
		z = num % 10
		place_values.append(z*c)
		num = num // 10
		c = c*10
	return place_values
	
def ArrayTans():
	#obtain the tan for the expanded numbers up to 10^50
	import math 
	power = 0
	number = 1
	#array of arrays where we store the Tan value for each extended number
	Tan_Numbers = []
	while power < 50:
		record = []
		while number < 10:
			record.append(math.tan(number*10**power))
			number += 1
		Tan_Numbers.append(record)
		power += 1
		number = 1
	return Tan_Numbers

def ProdTan(n):
	# being n a positive integer, its expanded form has the form of Sum_{k=0..K} (b(k)*10^k)
	# find n for which |(Product_{k=0..K} tan(b(k)*10^k))/(Sum_{k=0..K} tan(b(k)*10^k))| >= n
    
	import numpy as np #pip install numpy
	import math
	
	#check if file where to store data exists
	storeValues(n, '-', filename, True)
	
	#load individual Tan values for the next checking, a way to speed up things
	EachNumberTan = ArrayTans()
	
	SumStage = []
	SubstractStage = []
	index = -1
	#obtain max and min for each different stage. 
	for each in EachNumberTan:
		SumStage.append(index < 0 and np.max(each) or np.max(each) + SumStage[index])
		SubstractStage.append(index < 0 and np.min(each) or np.min(each) + SubstractStage[index])
		index += 1

	
	#iterate for laaarge numbers
	IteratorIndex = 0
	while n <= 10**49:
		#split number into an array of place values, invert the array and calculate the sum of Tan(each element)
		place_values = PlaceValues(n)[::-1]
		tan_values = np.tan(place_values)
		totalTanProd = np.prod(tan_values)
		totalTanSum = np.sum(tan_values)
		totalProdDivSum = totalTanProd/totalTanSum
		if abs(totalProdDivSum) >= n:
			storeValues(n, totalProdDivSum, filename)
		
		#check if it is worth to keep iterating. Is there any possible sum in the present order of magnitude that can compensates the sum to reach values near 0?
		WorkingSumStage = SumStage[:-len(SumStage) + len(place_values)][::-1]
		WorkingSubstractStage = SubstractStage[:-len(SubstractStage) + len(place_values)][::-1]
		ActualSumiterator = 0
		ActualNumber = 0 #this number will help us to follow the order of magnitude which is evaluated
		if(len(place_values) > 2):
			for i in range(len(place_values)-1):	
				ActualNumber += place_values[i]				
				ActualSumiterator += np.tan(place_values[i])

				#check if there is any possible combination for this order of magnitude.
				#The best possible combination with opposite sign values should overcome the actualSumInterator 
				if(ActualSumiterator < 0 and ActualSumiterator + WorkingSumStage[i+1] < -0.1 or ActualSumiterator > 0 and ActualSumiterator + WorkingSubstractStage[i+1] > 0.1 or place_values[i] == 0):
					#lets let n jump to the following order of magnitude
					ActualNumber += 10**(len(place_values)-i-1)
					n = ActualNumber - 1	#jump to the next order of magnitude and substract 1 so when while finishes adds this substracted 1
					break
		
		#storing the actual value after 10^7 tries
		IteratorIndex += 1
		if IteratorIndex > 10**7:
			IteratorIndex = 0
			storeValues(n, '-', filename, True)
			
		#lets add 1
		n += 1
		
	return 'DONE'
	
#calling

import os.path
import csv

filename = os.path.splitext(os.path.basename(__file__))[0]+'.txt' #the filename is the script's name

#if file exists something was tried, get last value which was tried, use it as starting point
if os.path.isfile(filename):
	bottle_list = []
		
	with open(filename, 'rt') as file:
		bottles = csv.reader(file)
		bottle_list.extend(bottles)
	ProdTan(int(bottle_list[1][0].replace(' -', '').replace('"', '')))
else: #start with 1
	storeValues(1, 'create', filename, True)
	ProdTan(1)