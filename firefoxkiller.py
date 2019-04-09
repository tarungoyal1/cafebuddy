import os
import time

while 1:
	os.system('./idwriter.sh')
	with open('wasteids.txt', mode='r') as f:
		ids = str(f.read()).split()
		os.system('kill '+ ids[5])


	# with open('wasteids.txt', mode='r') as f:
	# 	text = str(f.read()).split()
	# 	os.system('kill '+ text[0])
		# timeOfFirstId = text[text.index('ELAPSED')+1]

		# print('firstProcess = ' + text[0])

		# print(timeOfFirstId)
		# # if int(timeOfFirstId)>1000:
		# # 	firstProcess = int(text[0])
		# # 	os.system('kill '+ firstProcess)
	time.sleep(30)