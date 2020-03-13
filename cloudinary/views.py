from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,JsonResponse
import bcrypt
import json
import pymongo
import datetime
import jwt
import re
from bson import ObjectId,json_util
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
	print(users_check[0])
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
			# resp = Response(json.dumps({"errors": {"global":"Invalid Username/Password"}}), mimetype='application/json')
			# resp.status_code = 400
			# return resp




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
	# email = json.loads(request.body)['userId']

	files = mydb['files']
	allFiles = list(files.find().sort('created_at',pymongo.DESCENDING))
	filesm = []
	for i in files.find():
		i['_id'] = str(i['_id'])
		filesm.append(i)
	return JsonResponse({'files':filesm})

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
	# detector.setModelPath(os.path.join(execution_path,"resnet50_coco_best_v2.0.1.h5"))
	# detector.loadModel()
	# resp = requests.get(path, stream=True)
	# local_file = open('local_image.png', 'wb')
	# resp.raw.decode_content = True
	# shutil.copyfileobj(resp.raw, local_file)
	# local_file.close()
	# detections = detector.detectObjectsFromImage(input_image=os.path.join(execution_path , "local_image.png"), output_image_path=os.path.join(execution_path , ",mainImage.png"))
	# imageRecog = ""
	# for eachObject in detections:
	# 	imageRecog = imageRecog + eachObject['name'] + ","
	imageRecog = ""
	files = mydb['files']
	files.insert_one({'imageRecog':imageRecog,'size':size,'lastModified':lastModified,'name':name,'type':type,'directoryFile':directoryFile,'path':path,'userId':userId,'created_at':datetime.datetime.now()})
	allFiles = list(files.find().sort('created_at',pymongo.DESCENDING))
	filesm = []
	for i in files.find():
		i['_id'] = str(i['_id'])
		filesm.append(i)
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