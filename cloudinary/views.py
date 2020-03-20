from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,JsonResponse
import bcrypt
import json
import pymongo
import datetime
import threading 
import jwt
import re
from bson import ObjectId,json_util

import shutil
from imageai.Detection import ObjectDetection
import os
import warnings
warnings.filterwarnings("ignore")






myclient = pymongo.MongoClient("mongodb://Mustafa32:mustafas1@ds263018.mlab.com:63018/cloudinaryimageapp?retryWrites=false")
mydb = myclient["cloudinaryimageapp"]


def index(request):
	return HttpResponse(""" 
		<h1>
			Api Page, Visitor not allowed
		</h1>
		""")


@csrf_exempt
def login(request):
	email = json.loads(request.body)['credentials']['email']
	password = json.loads(request.body)['credentials']['password']
	users = mydb['users']
	users_check = users.find({'email':email}).limit(1)
	if(users_check.count()==0):
		resp = Response(json.dumps({"errors": {"global":"Invalid Username/Password"}}), mimetype='application/json')
		resp.status_code = 400
		return resp
	else:
		if(bcrypt.checkpw(password.encode('utf8'),users_check[0]['password'].encode('utf8'))):
			payload = {
				'email':email,
				'username':users_check[0]['username'],
				'id':str(users_check[0]['_id'])
			}
			user = {
				'email':email,
				'username':users_check[0]['username'],
	            'id':str(users_check[0]['_id']),
				'token':str(jwt.encode(payload,'SECRET_KEY',algorithm='HS256')),
			}
			return JsonResponse({'user':user})
		else:
			return JsonResponse(status=400,data={"errors": {"global":"Invalid Username/Password"}})

@csrf_exempt
def search(request):
	searchValue = json.loads(request.body)['searchValue']
	files = mydb['files']
	rgx = re.compile('.*'+searchValue+'.*', re.IGNORECASE)
	files = list(files.find({'name':rgx}))
	filesm = []
	for i in files:
		i['_id'] = str(i['_id'])
		filesm.append(i)
	return JsonResponse({'files':filesm,'length':len(files)},safe=False)

@csrf_exempt
def deleteImage(request):
	fileid = json.loads(request.body)['fileId']
	files = mydb['files']
	files.delete_one({'_id':ObjectId(fileid)})
	filesm = []
	for i in files.find():
		i['_id'] = str(i['_id'])
		filesm.append(i)
	return JsonResponse({'files':filesm},safe=False)

@csrf_exempt
def file(request):
	files = mydb['files']
	userId = json.loads(request.body)['userId']
	allFiles = list(files.find({"_id":ObjectId(userId)}).sort('created_at',pymongo.DESCENDING))
	filesm = []
	for i in files.find():
		i['_id'] = str(i['_id'])
		filesm.append(i)
	return JsonResponse({'files':filesm})



from urllib.parse import urlparse
import urllib.request


def object_detection(userId,path):
	temp = urlparse(path)
	filename = "./cloudinary/"+os.path.basename(temp.path)
	temp_filename = "./cloudinary/temp_"+os.path.basename(temp.path)
	urllib.request.urlretrieve(path, filename)	
	urllib.request.urlretrieve(path, temp_filename)

	execution_path = os.getcwd()
	detector = ObjectDetection()
	detector.setModelTypeAsRetinaNet()
	detector.setModelPath(os.path.join(execution_path,"./cloudinary/resnet50_coco_best_v2.0.1.h5"))
	detector.loadModel()
	detections = detector.detectObjectsFromImage(input_image=filename, output_image_path=temp_filename)
	imageRecog = ""
	for eachObject in detections:
		imageRecog = imageRecog + eachObject['name'] + ","
	os.remove(temp_filename)
	os.remove(filename)	
	mycol = mydb["files"]
	myquery = { "_id": ObjectId(userId) }
	newvalues = { "$set": { "imageRecog": imageRecog[:-1]}}
	mycol.update_one(myquery,newvalues)

@csrf_exempt
def sendImageDetails(request):
	fileDetails = json.loads(request.body)['fileDetails']
	S3File = json.loads(request.body)['S3File']
	size = fileDetails['size']
	lastModified = fileDetails['lastModified']
	name = fileDetails['name']
	type = fileDetails['type']
	directoryFile = S3File['directoryFile']
	path = S3File['path']
	userId = json.loads(request.body)['userId']
	imageRecog = "We will Load it Soon."
	files = mydb['files']
	fileInsertObject = files.insert_one({'imageRecog':imageRecog,'size':size,'lastModified':lastModified,'name':name,'type':type,'directoryFile':directoryFile,'path':path,'userId':userId,'created_at':datetime.datetime.now()})
	allFiles = list(files.find().sort('created_at',pymongo.DESCENDING))
	filesm = []
	for i in files.find():
		i['_id'] = str(i['_id'])
		filesm.append(i)
	threading.Thread(target=object_detection,args=(fileInsertObject.inserted_id,path,)).start()
	return JsonResponse({'files':filesm},safe=True)

@csrf_exempt
def register(request):
	email = json.loads(request.body)['user']['email']
	username = json.loads(request.body)['user']['username']
	password = json.loads(request.body)['user']['password']
	users = mydb['users']
	salt = bcrypt.gensalt(12)
	hashed = bcrypt.hashpw(str(password).encode('utf-8'),salt).decode('utf-8')
	mydict = {"email":email,"username":username,"createdAt":datetime.datetime.now(),'password':str(hashed)}
	x = users.insert_one(mydict)
	_id = x.inserted_id
	payload = {
		'email':email,
		'username':username,
		'id':str(_id)
	}
	user = {
			'email':email,
            'username':username,
            'id':str(_id),
			'token':str(jwt.encode(payload,'SECRET_KEY',algorithm='HS256')),
    }
	return JsonResponse({'user': user},safe=False);