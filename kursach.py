#	Курсач
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
		self.route = []	#технологический маршрут
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
			#if co.endTime == time and co.comp.engaged == True:
			if co.endTime <= time + 0.005 and co.endTime >= time - 0.005 and co.comp.engaged == True:
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

#Алгоритм формирования диаграммы Ганта:
def gant(rule):
	global Q, C
	time = 0
	while any(comp for comp in C if comp.operation < len(comp.route)) and time < 2000:
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
			#print("	gvm = " + str(gvm.number))
			if gvm.engaged == False:		#Если станок завершил обработку
				#print("	gvm not engaged")
				for comp in C:
					#print("		comp = " + str(comp.number))
					if comp.engaged == False and comp.operation < len(comp.route):
						#print("		comp not engaged")
						if comp.route[comp.operation] == gvm.number:	#Если следущая операция на этой gvm, то занести в портфель
							if any(pf.time == time for pf in gvm.Portf) == False:
								gvm.Portf.append(Portfolio(time))
							gvm.Portf[len(gvm.Portf) - 1].Components_list.append(comp)
							#Для перебора вариантов
							#break
							##########
							#print("		Занесено в порфель")
					
				#Здесь нужно выбрать деталь из портфеля согласно правилу 1
				if (rule == 1):
					#if (any(pf.time == time for pf in gvm.Portf)):
					if (any(pf.time >= time - 0.005 and pf.time <= time + 0.005 for pf in gvm.Portf)):
						chosenComp = min((comp for comp in gvm.Portf[len(gvm.Portf) - 1].Components_list), \
							key = lambda x: x.time[x.operation])
						#print("	chosen = " + str(chosenComp.number))
						gvm.Portf[len(gvm.Portf) - 1].Components_list.remove(chosenComp)	#Удалить деталь из порфеля
						gvm.WorkList.append(CompOperation(chosenComp, time))				#добавить в обработку
						chosenComp.operation += 1
						gvm.Comp = chosenComp
						gvm.engaged = True
						chosenComp.engaged = True
						
				#Здесь нужно выбрать деталь из портфеля согласно правилу 2
				if (rule == 2):
					#if (any(pf.time == time for pf in gvm.Portf)):
					if (any(pf.time >= time - 0.005 and pf.time <= time + 0.005 for pf in gvm.Portf)):
						#######debug
						print("	##########debug")
						for comp in gvm.Portf[len(gvm.Portf) - 1].Components_list:
							print("	comp = " + str(comp.number), end = " ")
							print("sum = " + str(sum(comp.time[i] \
								for i in range(len(comp.time)) if i > comp.operation)))
						print("	##########debug")
						#######debug
						chosenComp = max((comp for comp in gvm.Portf[len(gvm.Portf) - 1].Components_list), \
							key = lambda x: sum(x.time[i] \
							for i in range(len(x.time)) if i > x.operation))
						print("	chosen = " + str(chosenComp.number))
						gvm.Portf[len(gvm.Portf) - 1].Components_list.remove(chosenComp)	#Удалить деталь из порфеля
						gvm.WorkList.append(CompOperation(chosenComp, time))				#добавить в обработку
						chosenComp.operation += 1
						gvm.Comp = chosenComp
						gvm.engaged = True
						chosenComp.engaged = True
						
				#Здесь нужно выбрать деталь из портфеля согласно правилу 4
				if (rule == 4):
					#if (any(pf.time == time for pf in gvm.Portf)):
					if (any(pf.time >= time - 0.005 and pf.time <= time + 0.005 for pf in gvm.Portf)):
						#######debug
						print("	##########debug")
						for comp in gvm.Portf[len(gvm.Portf) - 1].Components_list:
							print("	comp = " + str(comp.number), end = " ")
							print("sum = " + str(sum(comp.time[i] \
								for i in range(len(comp.time)) if i > comp.operation)))
						print("	##########debug")
						#######debug
						chosenComp = min((comp for comp in gvm.Portf[len(gvm.Portf) - 1].Components_list), \
							key = lambda x: sum(x.time[i] \
							for i in range(len(x.time)) if i > x.operation))
						print("	chosen = " + str(chosenComp.number))
						gvm.Portf[len(gvm.Portf) - 1].Components_list.remove(chosenComp)	#Удалить деталь из порфеля
						gvm.WorkList.append(CompOperation(chosenComp, time))				#добавить в обработку
						chosenComp.operation += 1
						gvm.Comp = chosenComp
						gvm.engaged = True
						chosenComp.engaged = True
						
				#Здесь нужно выбрать деталь из портфеля согласно правилу 5
				if (rule == 5):
					#if (any(pf.time == time for pf in gvm.Portf)):
					if (any(pf.time >= time - 0.005 and pf.time <= time + 0.005 for pf in gvm.Portf)):
						chosenComp = max((comp for comp in gvm.Portf[len(gvm.Portf) - 1].Components_list), \
							key = lambda x: x.time[x.operation])
						#print("	chosen = " + str(chosenComp.number))
						gvm.Portf[len(gvm.Portf) - 1].Components_list.remove(chosenComp)	#Удалить деталь из порфеля
						gvm.WorkList.append(CompOperation(chosenComp, time))				#добавить в обработку
						chosenComp.operation += 1
						gvm.Comp = chosenComp
						gvm.engaged = True
						chosenComp.engaged = True
				
				#Здесь нужно выбрать деталь из портфеля согласно правилу 6
				if (rule == 6):
					#if (any(pf.time == time for pf in gvm.Portf)):
					if (any(pf.time >= time - 0.005 and pf.time <= time + 0.005 for pf in gvm.Portf)):
						chosenComp = gvm.Portf[len(gvm.Portf) - 1].Components_list[0]
						#print("	chosen = " + str(chosenComp.number))
						gvm.Portf[len(gvm.Portf) - 1].Components_list.remove(chosenComp)	#Удалить деталь из порфеля
						gvm.WorkList.append(CompOperation(chosenComp, time))				#добавить в обработку
						chosenComp.operation += 1
						gvm.Comp = chosenComp
						gvm.engaged = True
						chosenComp.engaged = True
						
				#Здесь нужно выбрать деталь из портфеля согласно правилу 6
				if (rule == 7):
					#if (any(pf.time == time for pf in gvm.Portf)):
					if (any(pf.time >= time - 0.005 and pf.time <= time + 0.005 for pf in gvm.Portf)):
						chosenComp = gvm.Portf[len(gvm.Portf) - 1].Components_list[ \
							len(gvm.Portf[len(gvm.Portf) - 1].Components_list) - 1]
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
				#if (any(pf.time == time for pf in gvm.Portf)):	#Если есть портфель на данное время
				if (any(pf.time >= time - 0.005 and pf.time <= time + 0.005 for pf in gvm.Portf)):
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
							#print("	chosenGvm = " + str(chosenGvm.number))
							chosenComp = next(comp for comp in cl \
								if comp.route[comp.operation + 1] == chosenGvm.number)
						#print("	chosen = " + str(chosenComp.number))
						gvm.Portf[len(gvm.Portf) - 1].Components_list.remove(chosenComp)	#Удалить деталь из порфеля
						gvm.WorkList.append(CompOperation(chosenComp, time))				#добавить в обработку
						chosenComp.operation += 1
						gvm.Comp = chosenComp
						gvm.engaged = True
						chosenComp.engaged = True
		
		time += 0.01



#Нарисовать диаграмму:
def diagrammOut():
	mainColors = np.array([
		(1, 0, 0, 1), 
		(1, 0.5, 0, 1), 
		(1, 1, 0, 1), 
		(0.5, 1, 0, 1),
		(0, 1, 0, 1),
		(0, 1, 0.5, 1),
		(0, 1, 1, 1),
		(0, 0.5, 1, 1),
		(0, 0, 1, 1),
		(0.5, 0, 1, 1),
		(1, 0, 1, 1),
		(1, 0, 0.5),
		(0.5, 0.5, 0.5),
		(0, 0, 0, 1)
		])
	colr = []
	patches = []
	for i in range(len(C)):
		colr.append(mainColors[i])
		patches.append(mpatches.Patch(color = colr[i], label='Деталь ' + str(C[i].number)))
	fig, ax = pl.subplots()
	ax.xaxis.set_major_locator(ticker.MultipleLocator(50))
	for gvm in Q:
		colors = [colr[i] for co in gvm.WorkList for i in range(len(C)) if co.comp.number == i + 1]
		verticals = [[(co.startTime, 0), (co.startTime, gvm.number + 0.5)] for co in gvm.WorkList] + \
			[[(co.endTime, 0), (co.endTime, gvm.number + 0.5)] for co in gvm.WorkList]
		vc = col.LineCollection(verticals, linestyle = '--', color = 'red', linewidths = 0.5)
		lines = [[(co.startTime ,gvm.number), (co.endTime ,gvm.number)] for co in gvm.WorkList]
		lc = col.LineCollection(lines, colors = colors, linewidths = 15)
		ax.add_collection(lc)
		ax.autoscale()
		#ax.add_collection(vc)
	plt.legend(handles=patches)
	plt.ylim([0, 6])
	plt.xlim([0, 1100])
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


##############################kursach#####################################	
#Детали:
C = [
	Component(1, [41.26, 33.01, 33.01, 61.89, 33.01]),
	Component(2, [61.89, 41.26, 33.01, 37.14]),
	Component(3, [61.89, 24.76, 66.02, 33.01, 33.01]),
	Component(4, [28.88, 49.52, 66.02, 33.01, 33.01]),
	Component(5, [24.76, 41.26, 33.01, 33.01, 24.76]),
	Component(6, [24.76, 41.26, 33.01, 66.02]),
	Component(7, [41.26, 33.01, 37.14]),
	Component(8, [41.26, 66.02, 61.89]),
	Component(9, [33.01, 61.89, 28.88, 24.76, 4.13]),
	Component(10, [78.39, 33.01, 61.89, 28.88, 24.76]),
	Component(11, [103.15, 33.01, 61.89, 24.76]),
	Component(12, [61.89, 66.02, 61.89, 28.88]),
	Component(13, [61.89, 33.01, 61.89, 24.76, 4.13]),
	Component(14, [41.26, 33.01, 61.89])
	]
	
C[0].route = [1, 3, 2, 3, 2]
C[1].route = [3, 1, 3, 2]
C[2].route = [3, 4, 1, 3, 2]
C[3].route = [3, 4, 1, 3, 2]
C[4].route = [4, 1, 3, 2, 4]
C[5].route = [4, 1, 3, 2]
C[6].route = [1, 3, 2]
C[7].route = [1, 3, 2]
C[8].route = [3, 2, 3, 4, 2]
C[9].route = [1, 3, 2, 3, 4]
C[10].route = [1, 3, 2, 4]
C[11].route = [1, 3, 2, 3]
C[12].route = [1, 3, 2, 4, 2]
C[13].route = [1, 3, 2]

#Станки:
Q = [
	GVM(1),
	GVM(2),
	GVM(3),
	GVM(4)
	]
	
gant(7)
print("Загальний час обробки всіх деталей: " + str(c1_1()))
printPortfolio()
printWorkList()
diagrammOut()
##############################kursach#####################################

