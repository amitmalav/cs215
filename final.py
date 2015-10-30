import csv
from math import *

f_w=open("final_ouput.txt","w")
f_c=open("countries_id_map.txt","r")
f_c_o=open("countries_id_map_orig.txt","r")
f_t=open("target-relations.tsv","r")
f_k=open("selected_indicators","r")
f_s=open("sentences.tsv","r")
f_f=open("kb-facts-train_SI.tsv","r")


country_map=dict()
country_map_from_code=dict()
country_facts=dict()
keyword_list=dict()
targets_list=[]
"""--------------------------------------------------------------------------------------------------------
Classes
--------------------------------------------------------------------------------------------------------"""
#Class Country
class Country:
	def __init__(self,c_id) :
		self.lists=[[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[],[]]
	#	self.name=name
		self.id=c_id

	def __str__(self):
		return self.name

#Class Keyword
class Keyword:
	def __init__(self,name):
		self.name=name
		self.lists=[]

	def __str__(self):
		return self.name

"""--------------------------------------------------------------------------------------------------------
End of Classes
--------------------------------------------------------------------------------------------------------"""

"""--------------------------------------------------------------------------------------------------------
Functions
--------------------------------------------------------------------------------------------------------"""

#Function - convert string to float
def isfloat(value):
  try:
    float(value)
    return True
  except ValueError:
    return False

#Function - Giving initial confidence to sentences 
def initial_confidence(n,N):
	if N==0:
		return 0
	if N-n >0:
		d=(N-n)/N
	else: 
		d=(n-N)/N	
	return 0.65*(2.7**(-1*20*d*d))

#Function - Giving the final confidence to the sentences depending on the matchings found in the sentences and target
def matching(sentence_string,keyword_parameter,init):
	count=0
	for keywords in keyword_list[keyword_parameter].lists:
		if keywords in sentence_string:
			count=count+1
	final_confidence=1-(1-init)*(2**(-1*count))
	if count==0:
		final_confidence=final_confidence/2
	return round(final_confidence,2)		

array_of_unknown_country=[]
def function(sentence_id,sentence_string,sentence_numbers_array,sentence_countries_array):
	count=0
	f=0
	for country in sentence_countries_array:
		for number in sentence_numbers_array:
			if not isfloat(number):
				#print(sentence_id,sentence_string,number) 
				continue
			number=float(number)
			if number<0:
				number=-1*number
			if number==0:
				continue			
			if number >1:
				digit = ceil(log10(number))
			elif number <=1 and number >= -1:
				digit = 0
			else :
				digit = ceil(log10(-1*number))	 
			#print(country,"d") 	
			#if country=="Israeli":
			#	continue	
			#if country not in country_map.keys():
			#	if country not in array_of_unknown_country:
			#		array_of_unknown_country.append(country)
			#		print(country)
				#continue 
			targets={k:[0,0] for k in targets_list}
			final_list = country_facts[country_map[country]].lists[digit] + country_facts[country_map[country]].lists[digit+1] + country_facts[country_map[country]].lists[digit-1]
			for tuples in final_list:
				if ((tuples[0]-number)/number) <= 0.3 and ((tuples[0]-number)/number) >= -0.3:
					init=initial_confidence(tuples[0],number)
					final_confidence=matching(sentence_string,tuples[1],init)
					if targets[tuples[1]][0]<final_confidence:
						targets[tuples[1]][0]=final_confidence
						targets[tuples[1]][1]=tuples[0]
					#string=sentence_id+"\t"+country+"\t"+tuples[1]+"\t"+str(final_confidence)+"\t"+str(number)+"\t"+str(tuples[0])+"\n"
					#f_w.write(string)
					count=1

			for targ,confi in targets.items():
				if confi[0]>=0.30:
					string=sentence_id+"\t"+country_map_from_code[country_map[country]]+"\t"+targ+"\t"+str(number)+"\t"+str(confi[1])+"\t"+str(confi[0])+"\n"
					f_w.write(string)
					f=2
				#	break
		#	break
	#	break			

						
	if count==0 or f==0:
		string=sentence_id+"\t"+"matching to no country"+"\n"
		f_w.write(string)


"""--------------------------------------------------------------------------------------------------------
End of Functions
--------------------------------------------------------------------------------------------------------"""

"""--------------------------------------------------------------------------------------------------------
Reading the data and initialising objects
--------------------------------------------------------------------------------------------------------"""

#cc=[]
#Reading the country_id_map.txt and relating countries with country code
reader_c = csv.reader(f_c,dialect="excel-tab")
for row in reader_c:
	try:
		country_map[row[1]]=row[0]
	except:
		print(row[1],row[0])
	if row[0] not in country_facts:
		country_facts[row[0]]=Country(row[0])
		#print(row[0])
	#else:
	#	cc.append(row[0])	
	#print(row[0])	
	#print("\n")
#print("yes")
f_c.close()	

#for i in cc:
#	print(i)


#Reading the country_id_map.txt and relating countries with country code
reader_c = csv.reader(f_c_o,dialect="excel-tab")
for row in reader_c:
	try:
		country_map_from_code[row[0]]=row[1]
	except:
		print(row[1],row[0])
	#if row[0] not in country_facts:
	#	country_facts[row[0]]=Country(row[0])
		#print(row[0])
	#else:
	#	cc.append(row[0])	
	#print(row[0])	
	#print("\n")
#print("yes")
f_c.close()	


#Reading the kb-facts-train.tsv (facts) and adding the facts in the countries
reader_f = csv.reader(f_f,dialect="excel-tab")
for row in reader_f:
	#pr.num=float(row[1])
	#pr.Rel=row[2]
	tup=(float(row[1]),row[2])
	#print(pr.num)
	if float(row[1])>1:
		if tup not in country_facts[row[0]].lists[ceil(log10(float(row[1])))]:
			country_facts[row[0]].lists[ceil(log10(float(row[1])))].append(tup)
	elif -1<=float(row[1]) and float(row[1])<=1:
		if tup not in country_facts[row[0]].lists[0]:
			if float(row[1]) < 0:
				tup=(-1*float(row[1]),row[2])				
			country_facts[row[0]].lists[0].append(tup)
	else:
		if tup not in country_facts[row[0]].lists[ceil(log10(-1*float(row[1])))]:		
			if float(row[1]) < 0:
				tup=(-1*float(row[1]),row[2])				
			country_facts[row[0]].lists[ceil(log10(-1*float(row[1])))].append(tup)

"""
for name,country in country_facts.items():
	print(name)
	i=0
	for list1 in country.lists:
		print("\t",i)
		for tup in list1:
			print("\t","\t",tup[0],"\t",tup[1])
		i=i+1
	print("\n")"""
f_f.close()		
		
			
reader_t=csv.reader(f_t,dialect="excel-tab")
for row1 in reader_t:
	keyword_list[row1[0]]=Keyword(row1[0])
	targets_list.append(row1[0])
	#print(keyword_list[row1[0]])

reader_k=csv.reader(f_k,dialect="excel-tab")
for row in reader_k:

	target=""
	for target,sent in keyword_list.items():
		if target in row:
			break
	for col in row:
		if col != target:
			keyword_list[target].lists.append(col)
	#print(target)
	#print("\t",keyword_list[target].lists)		
			














reader_s=csv.reader(f_s,dialect="excel-tab")
for row in reader_s:
	sid=row[0]
	ss=row[1]
	sn=row[2]
	sc=row[3]

	snu=sn.replace(" ","")
	scu=sc.replace(" ","")
	sna=snu.split(",")
	sca=scu.split(",")
	snau=[]
	scau=[]

	for country in sca:
		if country not in scau:
			scau.append(country)

	for num in sna:
		if num not in snau:
			snau.append(num)
	#print(sid,"\t",ss,"\t",sn,"\t",sc)
	#print(sna)
	#print(sca)
	#print(scau)
	#print("\n")
	function(sid,ss,snau,scau)
f_s.close()	

#for ,country in country_map.items():
#	print(country)