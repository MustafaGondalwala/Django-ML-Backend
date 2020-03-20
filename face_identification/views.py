from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse,JsonResponse
import json
import face_recognition
import io,base64
import pymongo
import bcrypt
import numpy as np
import jwt

# myclient = pymongo.MongoClient("mongodb://mustafa:mustafas1@ds263656.mlab.com:63656/face-identification?retryWrites=false")
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
	base64string = json.loads(request.body)['camera_image']
	password = json.loads(request.body)['password']
	username = json.loads(request.body)['username']
	base64string = base64string.replace("data:image/png;base64,","")
	image = face_recognition.load_image_file(io.BytesIO(base64.b64decode(base64string)))
	login_user_face = face_recognition.face_encodings(image)[0]
	user = mydb['face_login_users']
	check_user_exists = user.find_one({"username":username})
	if(check_user_exists == None ):
		return JsonResponse({"error":"Cannot Found Username/Password"})
	if(not(bcrypt.checkpw(password.encode('utf8'),check_user_exists['passwordHash'].encode('utf8')))):
		return JsonResponse({"error":"Cannot Found Username/Password"})
		
	know_face_encoding = [np.fromiter(check_user_exists['user_image_numpy'],dtype=np.float)]
	match = face_recognition.compare_faces(know_face_encoding,login_user_face)[0]
	if(match == False):
		return JsonResponse({"error":"Cannot Detect the Face in Our System. Try Again"})
	payload = {
		'username':username,
		'id':str(check_user_exists['_id'])
	}
	user = {
		'username':username,
		'id':str(check_user_exists['_id']),
		'token':str(jwt.encode(payload,'SECRET_KEY',algorithm='HS256'))
	}
	return JsonResponse({"success":{'user':user,'message':"Login Success"}})

@csrf_exempt
def checkForFace(request):
	base64string = json.loads(request.body)['dataUri']
	base64string = base64string.replace("data:image/png;base64,","")
	image = face_recognition.load_image_file(io.BytesIO(base64.b64decode(base64string)))
	check_total_face = face_recognition.face_encodings(image)
	context = {
		'total_faces':len(check_total_face)
	}
	return JsonResponse(context)

@csrf_exempt
def add_new_face(request):
	base64string = json.loads(request.body)['camera_image']
	password = json.loads(request.body)['password']
	username = json.loads(request.body)['username']
	base64string = base64string.replace("data:image/png;base64,","")
	image = face_recognition.load_image_file(io.BytesIO(base64.b64decode(base64string)))
	new_face = face_recognition.face_encodings(image)[0]
	user = mydb['face_login_users']
	
	if(user.find({"username":username}).count() != 0):
		return JsonResponse({"error":"User Already Exists. Try Another Username"})
	salt = bcrypt.gensalt(12)
	hashed = bcrypt.hashpw(str(password).encode('utf-8'),salt).decode('utf-8')
	mydict = {"username":username,"passwordHash":hashed,"user_image_numpy":new_face.tolist()}
	

	user.insert_one(mydict)
	return JsonResponse({"success":"New User Added, Redirecting to Login Page"})

