#	Задача Джонсона о 2 станках
#	Вариант с 3 станками
#	Автор: Зволикевич А.В. ІК-51

import numpy as np
import matplotlib.pyplot as plt
import pylab as pl
from matplotlib import collections as col
import matplotlib.ticker as ticker
import matplotlib.patches as mpatches

class Component():
	#класс Деталь
	def __init__(self, number, time_arr):
		self.number = number
		self.time = time_arr	#time[i] -- время обработки на і-той операции
		self.route = [1, 2, 3]	#технологический маршрут
		self.operation = 0		#Поточная операция
		self.engaged = False	#Обрабатываеться ли деталь на данный момент
		
	def reset(self):
		self.operation = 0
		self.engaged = False
		
class Portfolio():
	def __init__(self, time):
		self.time = time
		self.Components_list = []
	def Append_Component(self, comp):
		self.Components_list.append(comp)
	def getJobWorth(self):
		jw = 0
		for comp in self.Components_list:
			jw += comp.time[comp.operation]
		return jw
		
class CompOperation():
	#класс объеденяет операцию, время начала и конца обработки
	def __init__(self, c, sT):
		self.comp = c
		self.startTime = sT
		self.endTime = sT + c.time[c.operation]
		
class GVM():
	def __init__(self, number):
		self.number = number
		self.engaged = False				#Выполняет ли станок работу на данный момент
		self.Comp = Component(0, [0, 0, 0])	#Деталь над которой проводиться обработка
		self.Portf = []						#Портфель работ
		self.WorkList = []					#Очередь обработок(массив CompOperation)
	
	def refresh(self, time):
		if (any(self.WorkList)):
			co = self.WorkList[len(self.WorkList) - 1]
			#print("refreshing: gvm = " + str(self.number) + " t_e = " + str(co.endTime) + \
			#	" comp = " + str(co.comp.number) + ", comp engaged = " + str(co.comp.engaged))
			if co.endTime == time and co.comp.engaged == True:
				co.comp.engaged = False
				self.engaged = False
	
	def reset(self):
		self.engaged = False				
		self.Comp = Component(0, [0, 0, 0])	
		self.Portf = []						
		self.WorkList = []
	

#T[j][i] -- время обработки j-той детали на і-той операции(гвм)
	
#########################debug##########################################
def printPortfolio():
	print("Portfolio:")
	for gvm in Q:
		print("gvm = " + str(gvm.number), end = ':')
		for p in gvm.Portf:
			print("t" + str(p.time), end = ':')
			for comp in p.Components_list:
				print(comp.number, end = " ")
			print(" ", end = '')
		print('')
		
def printWorkList():
	print("WorkList:")
	for gvm in Q:
		print("gvm = " + str(gvm.number))
		for w in gvm.WorkList:
			print("	comp = " + str(w.comp.number), end = ' ')
			print("t_start = " + str(w.startTime), end = ' ')
			print("t_end = " + str(w.endTime))
		print('')
#########################debug##########################################

##############################test#####################################
"""#Детали:
C = [
	Component(1, [2, 3, 3]),
	Component(2, [5, 2, 4]),
	Component(3, [3, 4, 3]),
	Component(4, [4, 1, 5]),
	]
#Станки:
Q = [
	GVM(1),
	GVM(2),
	GVM(3)
	]"""
##############################test#####################################


#Алгоритм формирования диаграммы Ганта:
def gant(rule):
	global Q, C
	time = 0
	while any(comp for comp in C if comp.operation < len(comp.route)):
		print("time = " + str(time))
		for gvm in Q:
			gvm.refresh(time)
		#ранжировка:
		Q1 = [q for q in Q if any(q.WorkList) and (not q.engaged)]
		Q1.sort(key = lambda gvm: gvm.WorkList[len(gvm.WorkList) - 1].endTime)
		Q2 = [q for q in Q if any(q.WorkList) == False or q.engaged]
		Q = Q2 + Q1
		######
		for gvm in Q:
			print("	gvm = " + str(gvm.number))
			if gvm.engaged == False:		#Если станок завершил обработку
				print("	gvm not engaged")
				for comp in C:
					print("		comp = " + str(comp.number))
					if comp.engaged == False and comp.operation < len(comp.route):
						print("		comp not engaged")
						if comp.route[comp.operation] == gvm.number:	#Если следущая операция на этой gvm, то занести в портфель
							if any(pf.time == time for pf in gvm.Portf) == False:
								gvm.Portf.append(Portfolio(time))
							gvm.Portf[len(gvm.Portf) - 1].Components_list.append(comp)
							#Для перебора вариантов
							#break
							##########
							print("		Занесено в порфель")
					
				#Здесь нужно выбрать деталь из портфеля согласно правилу 1
				if (rule == 1):
					if (any(pf.time == time for pf in gvm.Portf)):
						chosenComp = min((comp for comp in gvm.Portf[len(gvm.Portf) - 1].Components_list), \
							key = lambda x: x.time[x.operation])
						#print("	chosen = " + str(chosenComp.number))
						gvm.Portf[len(gvm.Portf) - 1].Components_list.remove(chosenComp)	#Удалить деталь из порфеля
						gvm.WorkList.append(CompOperation(chosenComp, time))				#добавить в обработку
						chosenComp.operation += 1
						gvm.Comp = chosenComp
						gvm.engaged = True
						chosenComp.engaged = True
		
		#Здесь нужно выбрать деталь из портфеля согласно правилу 3
		if rule == 3:
			for gvm in Q:
				if (any(pf.time == time for pf in gvm.Portf)):	#Если есть портфель на данное время
					if any(gvm.Portf[len(gvm.Portf) - 1].Components_list):	#Если есть детали в портфеле
						cl = gvm.Portf[len(gvm.Portf) - 1].Components_list
						nextGvm = []
						for comp in cl:
							if comp.operation < len(comp.route) - 1:
								nextGvm.append(next(g for g in Q \
									if comp.route[comp.operation + 1] == g.number)) #Заполнить список следуущих ГВМ
						#Разделить следующие ГВМ на свободные и занятые
						nextGvmIdle = []	
						nextGvmNotIdle = []
						chosenGvm = 0
						for g in nextGvm:
							if (any(pf.time == time for pf in g.Portf)):
								nextGvmNotIdle.append(g)
							else:
								nextGvmIdle.append(g)
						if (any(comp for comp in cl if comp.operation == len(comp.route) - 1)):	#Если есть деталь у которой данная
							chosenComp = next(comp for comp in cl if comp.operation == len(comp.route) - 1)	#операция последняя, то выбираем её
						else:
							if (any(nextGvmIdle)):	#Если есть свободная то выберем её
								chosenGvm = nextGvmIdle[0]
							else:	#Иначе -- ищем по трудоёмкости портфеля
								chosenGvm = min((g for g in nextGvmNotIdle), \
									key = lambda x: x.Portf[len(x.Portf) - 1].getJobWorth())
							print("	chosenGvm = " + str(chosenGvm.number))
							chosenComp = next(comp for comp in cl \
								if comp.route[comp.operation + 1] == chosenGvm.number)
						print("	chosen = " + str(chosenComp.number))
						gvm.Portf[len(gvm.Portf) - 1].Components_list.remove(chosenComp)	#Удалить деталь из порфеля
						gvm.WorkList.append(CompOperation(chosenComp, time))				#добавить в обработку
						chosenComp.operation += 1
						gvm.Comp = chosenComp
						gvm.engaged = True
						chosenComp.engaged = True
		
		time += 1



#Нарисовать диаграмму:
def diagrammOut():
	mainColors = np.array([(1, 0, 0, 1), (0, 1, 0, 1), (0, 0, 1, 1), (1, 1, 0, 1)])
	patches = []
	for i in range(len(C)):
		if (i + 1) % 4 == 0:
			colr = mainColors[3]
		elif (i + 1) % 3 == 0:
			colr = mainColors[2]
		elif (i + 1) % 2 == 0:
			colr = mainColors[1]
		elif (i + 1) % 1 == 0:
			colr = mainColors[0]
		patches.append(mpatches.Patch(color = colr, label='Деталь ' + str(C[i].number)))
		"""red_patch = mpatches.Patch(color='red', label='Деталь ' + str(C[0].number))
		green_patch = mpatches.Patch(color='green', label='Деталь ' + str(C[1].number))
		blue_patch = mpatches.Patch(color='blue', label='Деталь ' + str(C[2].number))
		yeallow_patch = mpatches.Patch(color=(1, 1, 0, 1), label='Деталь ' + str(C[3].number))"""
	fig, ax = pl.subplots()
	ax.xaxis.set_major_locator(ticker.MultipleLocator(1))
	for gvm in Q:
		colors = [mainColors[i] for co in gvm.WorkList for i in range(4) if co.comp.number == i + 1]
		verticals = [[(co.startTime, 0), (co.startTime, gvm.number + 0.5)] for co in gvm.WorkList] + \
			[[(co.endTime, 0), (co.endTime, gvm.number + 0.5)] for co in gvm.WorkList]
		vc = col.LineCollection(verticals, linestyle = '--', color = 'red', linewidths = 0.5)
		lines = [[(co.startTime ,gvm.number), (co.endTime ,gvm.number)] for co in gvm.WorkList]
		lc = col.LineCollection(lines, colors = colors, linewidths = 6)
		ax.add_collection(lc)
		ax.autoscale()
		ax.add_collection(vc)
	#plt.legend(handles=[red_patch, green_patch, blue_patch, yeallow_patch])
	plt.legend(handles=patches)
	plt.ylim([0, 6])
	plt.show()
		
	

#################criterion 1.1:+
def c1_1():
	#print("Критерий 1.1:" + str(max(co.endTime for gvm in Q
		#for co in gvm.WorkList)))
	#print(str(max(co.endTime for gvm in Q
		#for co in gvm.WorkList)))
	return(max(co.endTime for gvm in Q
		for co in gvm.WorkList))
	
#################criterion 2.1:+
def c2_1():
	K = []
	for gvm in Q:
		Tr = sum(co.endTime - co.startTime for co in gvm.WorkList)
		#print("Tr = " + str(Tr))

		WL = gvm.WorkList
		Tp = []
		Tp.append(WL[0].startTime)
		for i in range(len(WL) - 1):
			Tp.append(WL[i + 1].startTime - WL[i].endTime)
		Tp = sum(Tp)
		#print("Tp = " + str(Tp))
		K.append(Tr/(Tr + Tp))
		#print("K = " + str(Tr/(Tr + Tp)))
	#print("Критерий 2.1:" + str(min(K)))
	#print(str(min(K)))
	return(min(K))

##################criterion 2.3:+
def c2_3():
	Tp = []
	for gvm in Q:
		WL = gvm.WorkList
		Tpk = []
		Tpk.append(WL[0].startTime)
		for i in range(len(WL) - 1):
			Tpk.append(WL[i + 1].startTime - WL[i].endTime)
		Tpk = sum(Tpk)
		Tp.append(Tpk)

	#print("Критерий 2.3:" + str(max(Tp)))
	#print(str(max(Tp)))
	return(max(Tp))

##################criterion 2.6:+
def c2_6():
	Tp = []
	for gvm in Q:
		WL = gvm.WorkList
		Tpk = []
		Tpk.append(WL[0].startTime)
		for i in range(len(WL) - 1):
			Tpk.append(WL[i + 1].startTime - WL[i].endTime)
		Tpk = sum(Tpk)
		Tp.append(Tpk/len(gvm.WorkList))

	#print("Критерий 2.6:" + str(max(Tp)))
	#print(str(max(Tp)))
	return(max(Tp))

##################criterion 3.1:+
def c3_1():
	T = []
	for comp in C:
		for j in range(1, len(comp.route)):
			gvm1 = next(gvm for gvm in Q if gvm.number == comp.route[j - 1])
			t1 = next(co for co in gvm1.WorkList if co.comp == comp).endTime
			gvm2 = next(gvm for gvm in Q if gvm.number == comp.route[j])
			t2 = next(co for co in gvm2.WorkList if co.comp == comp).startTime
			T.append((t2 - t1))

	#print("Критерий 3.1:" + str(max(T)))
	#print(str(max(T)))
	return(max(T))
		
##################criterion 3.4: +
def c3_4():
	TM = []
	for comp in C:
		for j in range(1, len(comp.route)):
			gvm1 = next(gvm for gvm in Q if gvm.number == comp.route[j - 1])
			t1 = next(co for co in gvm1.WorkList if co.comp == comp).endTime
			gvm2 = next(gvm for gvm in Q if gvm.number == comp.route[j])
			t2 = next(co for co in gvm2.WorkList if co.comp == comp).startTime
			TM.append((t2 - t1)/len(comp.route))

	#print("Критерий 3.4:" + str(max(TM)))
	#print(str(max(TM)))
	return(max(TM))
		
##################criterion 3.6:+
def c3_6():
	TM = []
	for comp in C:
		for j in range(1, len(comp.route)):
			gvm1 = next(gvm for gvm in Q if gvm.number == comp.route[j - 1])
			t1 = next(co for co in gvm1.WorkList if co.comp == comp).endTime
			gvm2 = next(gvm for gvm in Q if gvm.number == comp.route[j])
			t2 = next(co for co in gvm2.WorkList if co.comp == comp).startTime
			TM.append((t2 - t1)/len(comp.route))

	#print("Критерий 3.6:" + str(sum(TM)))
	#print(str(sum(TM)))
	return(sum(TM))


##############################test#####################################	
#Детали:
C = [
	Component(1, [2, 3, 3]),
	Component(2, [5, 2, 4]),
	Component(3, [3, 4, 3]),
	Component(4, [4, 1, 5]),
	]
	
C[0].route = [1, 3, 2]
C[1].route = [3, 1, 2]
C[2].route = [2, 3, 1]
C[3].route = [1, 2, 3]

#Станки:
Q = [
	GVM(1),
	GVM(2),
	GVM(3)
	]
	
gant(3)
diagrammOut()
##############################test#####################################
"""
############################lab4###########################
n = int(input("Введіть кількість обладнання: "))
m = int(input("Введіть кількість деталей: "))
T = [[0 for j in range(n)] for i in range(m)]
print("Введіть матрицю тривалостей обробки:")
for j in range(n):
	for i in range(m):
		T[i][j] = int(input("T[" + str(i + 1) + "]["  +str(j + 1) + "] = "))

#Детали
C = []	
for i in range(m):
	Tj = []
	for j in range(n):
		Tj.append(T[i][j])
	C.append(Component(i + 1, Tj))

#ГВМ
Q = [GVM(j + 1) for j in range(n)]

for comp in C:
	comp.route = [j + 1 for j in range(len(Q))]

gant()


print("Кількість обладнання: " + str(n))
print("Кількість деталей: " + str(m))
print("Загальний час обробки всіх деталей: " + str(c1_1()))
print("Критерій 1.1: " + str(c1_1()))
print("Критерій 2.1: " + str(c2_1()))
print("Критерій 2.3: " + str(c2_3()))
print("Критерій 2.6: " + str(c2_6()))
print("Критерій 3.1: " + str(c3_1()))
print("Критерій 3.4: " + str(c3_4()))
print("Критерій 3.6: " + str(c3_6()))

P = [[0 for i in range(m)] for j in range(n)]
for j in range(n):
	for i in range(m):
		for co in Q[j].WorkList:
			if co.comp.number == i + 1:
				P[j][i] = co.startTime
				break

print("Матриця P:")				
for j in range(n):
	print(P[j])
	
diagrammOut()

############################lab3###########################
"""
