from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
from django.views.decorators.csrf import csrf_exempt
import json
import pymysql
import datetime
# Create your views here.
def connection():
    conn = pymysql.connect(host="mustafa-db.cyptmcja8bd2.us-east-2.rds.amazonaws.com",
                           user = "mustafa",
                           passwd = "mustafas1",
                           db = "p_timetracker")
    c = conn.cursor()
    return c, conn
c,conn = connection()


hour_to_id = [
					['5:00 - 6:00 am','5','0'],
    				['6:00 - 7:00 am','6','1'],
    				['7:00 - 8:00 am','7','2'],
    				['8:00 - 9:00 am','8','3'],
    				['9:00 - 10:00 am','9','4'],
    				['10:00 - 11:00 am','10','5'],
    				['11:00 - 12:00 pm','11','6'],
    				['12:00 - 1:00 pm','12','7'],
    				['1:00 - 2:00 pm','13','8'],
    				['2:00 - 3:00 pm','14','9'],
    				['3:00 - 4:00 pm','15','10'],
    				['4:00 - 5:00 pm','16','11'],
    				['5:00 - 6:00 pm','17','12'],
    				['6:00 - 7:00 pm','18','13'],
    				['7:00 - 8:00 pm','19','14'],
    				['8:00 - 9:00 pm','20','15'],
    				['9:00 - 10:00 pm','21','16'],
    				['10:00 - 11:00 pm','22','17'],
    				['11:00 - 12:00 pm','23','18'],
    				['12:00 - 1:00 am','0','19'],
    ]

@csrf_exempt
def autosuggestion(request):
	keyword = json.loads(request.body)['keyword']
	c,conn = connection()
	query = "select distinct title from time_descriptions where title like '%"+keyword+"%';"
	c.execute(query)
	main = []
	for i in c.fetchall():
		main.append({'title':i[0]})
	return JsonResponse({"data":main})

@csrf_exempt
def update_task(request):
	c,conn = connection()
	id = json.loads(request.body)['update_id']
	checked_status = json.loads(request.body)['checked_status']
	if(checked_status==True):
		checked_status = 1
	else:
		checked_status = 0
	query = "update tasks set status="+str(checked_status)+" where id="+str(id)
	total_entry = []
	if(c.execute(query) == 1):
		conn.commit()
		query = "select * from tasks where DATE(`created_at`) = CURDATE()";
		c.execute(query)
		records = c.fetchall()
		for i in records:
			item = {
				'id':i[0],
				'task_name':i[1],
				'status':i[2],
				'created_at':i[3].date()
			}
			total_entry.append(item)
	return JsonResponse({"data":total_entry,"message":"Task Updated."})

@csrf_exempt
def delete_task(request):
	c,conn = connection()
	delete_id = json.loads(request.body)['delete_id']
	query = "delete from tasks where id="+str(delete_id);
	total_entry = []
	if(c.execute(query) == 1):
		conn.commit()
		query = "select * from tasks where DATE(`created_at`) = CURDATE()";
		c.execute(query)
		records = c.fetchall()
		for i in records:
			item = {
				'id':i[0],
				'task_name':i[1],
				'status':i[2],
				'created_at':i[3].date()
			}
			total_entry.append(item)
	return JsonResponse({"data":total_entry,"message":"Task Removed."})		


def getAllDayDescriptionDate(request):
	c,conn = connection()
	query = "select DISTINCT DATE(created_at) as days from tasks ORDER BY created_at DESC"
	c.execute(query)
	records = c.fetchall()
	total_entry = []
	for i in records:
		total_entry.append([i[0].day,i[0].month])
	return JsonResponse({"data":total_entry})

def getAllTaskDate(request):
	c,conn = connection()
	query = "select DISTINCT DATE(created_at) as days from time_descriptions ORDER BY created_at DESC"
	c.execute(query)
	records = c.fetchall()
	total_entry = []
	for i in records:
		try:
			total_entry.append([i[0].day,i[0].month])
		except:
			pass
	return JsonResponse({"data":total_entry})

def get_tasks(request,day,month):
	c,conn = connection()
	date = datetime.datetime.strptime(day+"/"+month+"/"+'2020', "%d/%m/%Y").date()
	query = "select * from tasks where DATE(`created_at`) = '"+str(date)+"'";
	c.execute(query)
	records = c.fetchall()
	total_entry = []
	for i in records:
		item = {
				'id':i[0],
				'task_name':i[1],
				'status':i[2],
				'created_at':i[3].date()
		}
		total_entry.append(item)
	return JsonResponse({"data":total_entry})
@csrf_exempt
def add_task(request):
	c,conn = connection()
	task_name = json.loads(request.body)['task_name']
	current_timestamp = str(datetime.datetime.now())
	query = 'insert into tasks (task_name,status,created_at,updated_at) values ("'+task_name+'","0","'+current_timestamp+'","'+current_timestamp+'");';
	total_entry = []
	if(c.execute(query) == 1):
		conn.commit()
		c.execute("SELECT * FROM tasks WHERE DATE(`created_at`) = CURDATE()")
		records = c.fetchall()
		for i in records:
			item = {
				'id':i[0],
				'task_name':i[1],
				'status':i[2],
				'created_at':i[3].date()
			}
			total_entry.append(item)	

	return JsonResponse({'data':total_entry,"message":"Task Created."})

@csrf_exempt
def removeDescription(request):
	try:
		c,conn = connection()
	except Exception as e:
		return HttpResponse(str(e))
	hour_id = json.loads(request.body)['hour_id']
	delete_id = json.loads(request.body)['delete_id']
	query = "delete from time_descriptions where id="+str(delete_id);
	total_entry = []
	if(c.execute(query) == 1):
		conn.commit()
		c.execute("SELECT * FROM time_descriptions WHERE DATE(`created_at`) = CURDATE() AND hour_id='"+str(hour_id)+"'")
		records = c.fetchall()
		for i in records:
			item = {
				'id':i[0],
				'hour_id':i[1],
				'title':i[2],
				'task_time':(str(i[3])),
				'time_wasted':i[4],
				'created_at':i[7].date()
			}
			total_entry.append(item)
	return JsonResponse({"data":total_entry,"message":"Description Removed"})

def index(request):
	return HttpResponse("not allowed")

def getDescription(request,hour_id):
	try:
		c,conn = connection()
	except Exception as e:
		return HttpResponse(str(e))
	total_entry = []
	query = "SELECT * FROM time_descriptions WHERE DATE(`created_at`) ='"+str(datetime.date.today())+"'  AND hour_id='"+str(hour_id)+"'"
	print(query)
	c.execute(query)
	records = c.fetchall()
	for i in records:
		item = {
				'id':i[0],
				'hour_id':i[1],
				'title':i[2],
				'task_time':(str(i[3])),
				'time_wasted':i[4],
				'created_at':i[7].date()
		}
		total_entry.append(item)
	return JsonResponse({'data':total_entry})

def get_particular_date(request,day,month):
	try:
		c,conn = connection()
	except Exception as e:
		return HttpResponse(str(e))
	date = datetime.datetime.strptime(day+"/"+month+"/"+'2020', "%d/%m/%Y").date()
	query = "SELECT * FROM time_descriptions WHERE DATE(`created_at`) = '"+str(date)+"'";
	c.execute(query)
	records = c.fetchall()
	total_entry = []
	for i in records:
		item = {
			'id':i[0],
			'hour_id':i[1],
			'title':i[2],
			'task_time':(str(i[3])),
			'time_wasted':i[4],
			'created_at':i[7].date()
		}
		total_entry.append(item)

	return JsonResponse({'data':total_entry})

@csrf_exempt
def addDescription(request):
	main = json.loads(request.body)
	if(main['time_wasted'] == "on"):
		main['time_wasted'] = "1"
	else:
		main['time_wasted'] = "0"
	try:
		c,conn = connection()
	except Exception as e:
		return HttpResponse(str(e))

	task_time = datetime.datetime.strptime(main['currentTime'], '%H:%M')
	hour_id = main['hour_id']
	current_hour = datetime.datetime.now().hour

	new_hour = ""
	for i in hour_to_id:
		if(i[1] == str(current_hour)):
			new_hour = i[2]

	query = "insert into time_descriptions (hour_id,title,task_time,time_wasted,created_at,updated_at) values ("+new_hour+",'"+main['title']+"','"+str(task_time)+"',"+main['time_wasted']+",'"+str(datetime.datetime.now())+"','"+str(datetime.datetime.now())+"')"
	total_entry = []
	if(c.execute(query) == 1):
		conn.commit();
		c.execute("SELECT * FROM time_descriptions WHERE DATE(`created_at`) = CURDATE() AND hour_id='"+str(main['hour_id'])+"'")
		records = c.fetchall()
		for i in records:
			item = {
				'id':i[0],
				'hour_id':i[1],
				'title':i[2],
				'task_time':(str(i[3])),
				'time_wasted':i[4],
				'created_at':i[7].date()
			}
			total_entry.append(item)
	if(hour_id!=new_hour):
		message = "Task Added in Other Hour ID. <a href='/add-description/"+str(new_hour)+"'>Click Here</a>"
	else:
		message = "Task Created"
	return JsonResponse({"data":total_entry,"message":message})