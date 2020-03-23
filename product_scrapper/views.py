from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
import requests
from bs4 import BeautifulSoup
import json
from django.template.loader import render_to_string
import sys
import json
import threading 
# import MySQLdb
import pymysql
from datetime import datetime

# Create your views here.
def connection():
    conn = pymysql.connect(host="mustafa-db.cyptmcja8bd2.us-east-2.rds.amazonaws.com",
                           user = "mustafa",
                           passwd = "mustafas1",
                           db = "scrapper_products")
    c = conn.cursor()
    return c, conn

def index(request):
    return render(request,"index.html")



def check_for_save_description(url):
	c,conn = connection()
	query = "select * from product_describe where url='"+url+"' limit 1"
	c.execute(query)
	main = {}
	for i in c.fetchall():
		main = {
			'product_description':i[2],
			'feature_bullets':i[3],
			'id':i[0]
		}
	return main

def save_description(url,productsDesciption,feature_bullets):
	c,conn = connection()
	productsDesciption = pymysql.escape_string(productsDesciption)
	feature_bullets = pymysql.escape_string(feature_bullets)
	query = 'insert into product_describe (URL,product_description,feature_bullets) values("'+url+'","'+productsDesciption+'","'+feature_bullets+'")'
	print(c.execute(query))
	conn.commit()
def getDescription(request):
	URL = request.GET['q_url']
	main = check_for_save_description(URL)
	if main == {}:
		headers = {
		  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
		  'accept-encoding': 'gzip, deflate, br',
		  'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,te;q=0.7',
		  'cache-control': 'no-cache',
		  'downlink': '10',
		  'ect': '4g',
		  'pragma': 'no-cache',
		  'referer': 'https://www.amazon.in/',
		  'rtt': '150',
		  'sec-fetch-dest': 'document',
		  'sec-fetch-mode': 'navigate',
		  'sec-fetch-site': 'same-origin',
		  'sec-fetch-user': '?1',
		  'upgrade-insecure-requests': '1',
		  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
		}
		r = requests.get(URL,headers=headers) 
		soup = BeautifulSoup(r.content)
		productsDesciption = soup.find("div",attrs={"id":"productDescription"})
		feature = soup.find("div",attrs={"id":"featurebullets_feature_div"})
		imageContainer = soup.findAll("li",attrs={"class":"a-spacing-small item imageThumbnail a-declarative"})
		context = {
			'product_description':str(productsDesciption),
			'feature_bullets':str(feature)
		}
		save_description_thread = threading.Thread(target=save_description,args=(URL,str(productsDesciption),str(feature)))
		save_description_thread.start()
		return JsonResponse(context,safe=False)
	else:
		return JsonResponse(main,safe=False)

def autosuggestion(request):
	query = request.GET['query']
	URL = "https://www.snapdeal.com/app/get/json/autoSuggestions?sr=true&num=20&ss="+query
	json_data = requests.get(URL).json()
	keyword_list = []
	for keyword in json_data['responseAutosuggestions']:
		keyword_list.append({"title":keyword['keyword']})
	for keyword in json_data['unstructured']:
		keyword_list.append({"title":keyword['keyword']})
	keyword_list = (keyword_list)
	context = {
		"results": keyword_list
		,
		"total":len(keyword_list)
	}
	return JsonResponse(context,safe=False)




def save_products(mainDict,vender_type,keyword):
	c,conn = connection()
	for i in mainDict:
		try:
			if(vender_type == "flipkart"):
				i['image'] = ""
			i['title'] = i['title'].replace("'","").replace('"',"")
			query = 'insert into products (url,image,vender_type,keyword,title,price,rating_count,rating,mrp,discount,created_at) values ("'+i['url']+'","'+i['image']+'","'+vender_type+'","'+keyword+'","'+i['title']+'","'+str(i['price'])+'","'+str(i['rating_count'])+'","'+str(i['rating'])+'","'+str(i['mrp'])+'","'+str(i['discount'])+'","'+str(datetime.now())+'");';
			print(c.execute(query))
		except Exception as e:
			print(str(e))
	conn.commit()

def check_for_saved(vender_type,keyword):
	c,conn = connection()
	query = "select * from products where vender_type='"+vender_type+"' and keyword='"+keyword+"';"
	# print(query)
	c.execute(query)
	mainDict = []
	for i in c.fetchall():
		mainDict.append({
			"id":i[0],
			"url":i[1],
			"image":i[2],
			"title":i[3],
			"price":i[6],
			"rating":i[7],
			"rating_count":i[8],
			"mrp":i[9],
			"discount":i[10],
			"created_at":i[11]
			})
	return mainDict

def update_5_days(item,vender_type,keyword):
	c,conn = connection()
	time_compare = int(str(datetime.now() - item['created_at'])[0])
	if(time_compare >= 5):
		query = "delete from products where vender_type='"+vender_type+"' and keyword='"+keyword+"'";
		c.execute(query)
		conn.commit()
	else:
		return None

def scrape(request,type):
	keyword = request.GET['keyword']
	mainDict = check_for_saved(type,keyword);
	if(len(mainDict)  == 0):
		mainDict = []
		if(type == "flipkart"):
			mainDict = getFlipkart(keyword)
		elif(type == "snapdeal"):
			mainDict = getSnapDeal(keyword)
		elif(type == "tatacliq"):
			mainDict = getTataCliq(keyword)
		elif(type == "amazon"):
			mainDict = getAmazon(keyword)
		t = threading.Thread(target=save_products,args=(mainDict,type,keyword))
		t.start()
	context = {
		'query':keyword,
		'type':type,
		'results':mainDict,
		'results_total':len(mainDict)
	}
	try:
		update_product = threading.Thread(target=update_5_days,args=(mainDict[0],type,keyword))
		update_product.start()
	except:
		pass
	return JsonResponse(context,safe=False)
	return render(request,"index.html",{'mainDict':mainDict})


def rating_width_to_rating(width):
    if(width<=20):
        return 1
    elif(width<=30):
        return 1.5
    elif(width<=40):
        return 2
    elif(width<=50):
        return 2.5
    elif(width<=60):
        return 3
    elif(width<=70):
        return 3.5
    elif(width<=80):
        return 4
    elif(width<=90):
        return 4.5
    elif(width<=100):
        return 5




def getAmazon(keyword):
	URL = "https://www.amazon.in/s?i=aps&k="+keyword
	headers = {
	  'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
	  'accept-encoding': 'gzip, deflate, br',
	  'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8,te;q=0.7',
	  'cache-control': 'no-cache',
	  'downlink': '10',
	  'ect': '4g',
	  'pragma': 'no-cache',
	  'referer': 'https://www.amazon.in/',
	  'rtt': '150',
	  'sec-fetch-dest': 'document',
	  'sec-fetch-mode': 'navigate',
	  'sec-fetch-site': 'same-origin',
	  'sec-fetch-user': '?1',
	  'upgrade-insecure-requests': '1',
	  'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/80.0.3987.132 Safari/537.36'
	}
	r = requests.get(URL,headers=headers) 
	soup = BeautifulSoup(r.content)
	main_container = soup.findAll("div",attrs={"class":"s-result-item"})
	mainPack = []
	for i in main_container:
	    try:
	        title = (i.find("span",attrs={"class","a-size-medium a-color-base a-text-normal"}).text)
	    except:
	    	try:
	        	title = (i.find("span",attrs={"class","a-size-base-plus a-color-base a-text-normal"}).text)
	    	except:
	    		continue
	    try:
	        sale_price = int(i.find("span",attrs={"class":"a-price-whole"}).text.replace(",",""))
	    except:
	        sale_price = 0
	    try:
	        mrp = int(i.find("span",attrs={"class":"a-price a-text-price"}).span.text.replace("\u20B9","").replace(",",""))
	    except:
	    	continue
	    try:
	        rating = float(i.find("span",attrs={"class":"a-icon-alt"}).text.split(" ")[0])
	    except:
	        rating = 0
	    try:
	        rating_count = int(i.find("div",attrs={"class":"a-row a-size-small"}).find("span",attrs={"class":"a-size-base"}).text.replace(",",""))
	    except:
	        rating_count = 0
	    link = "https://www.amazon.in"+i.find("a",attrs={"class":"a-link-normal a-text-normal"})['href']
	    if link.find("picassoRedirect") != -1:
	    	link = "https://www.amazon.in"+link.split("url=")[1].replace("%2F","/")
	    try:
	    	image = i.find("img",attrs={"class":"s-image"})['src']
	    except:
	    	print("error")
	    """
	    pack = {
	        'url':link,
	        'title':title,
	        'image':img_src,
	        'price':sale_price,
	        'rating_count':rating_count,
	        'rating':rating,
	        'mrp':mrp,
	        'discount':discount
	    }
	    """
	    
	    mainPack.append({
	    		'url':link,
	    		'image':image,
	    		'title':title,
	    		'price':sale_price,
	    		'rating_count':rating_count,
	    		'rating':rating,
	    		'mrp':mrp,
	    		'discount':int(mrp)-int(sale_price),
	    	})
	return mainPack
    
    
def getTataCliq(keyword):
	query = keyword
	URL = "https://www.tatacliq.com/marketplacewebservices/v2/mpl/products/searchProducts/?searchText="+query+"%3Arelevance%3AinStockFlag%3Atrue&isKeywordRedirect=false&isKeywordRedirectEnabled=true&channel=WEB&isTextSearch=false&isFilter=false&page=0&isPwa=true&pageSize=40&typeID=all"
	r = requests.get(URL) 
	results = r.json()['searchresult']
	mainPack = []
	for i in results:
	    link = "https://www.tatacliq.com"+i['webURL']
	    title = i['productname']
	    try:
	        rating = i['averageRating']
	    except:
	        rating=0
	    rating_count = i['ratingCount']
	    mrp = i['price']['mrpPrice']['doubleValue']
	    sale_price = i['price']['sellingPrice']['doubleValue']
	    discount = mrp-sale_price
	    image = "http:"+i['imageURL']
	    mainPack.append({
	        'url':link,
	        'title':title,
	        'rating':rating,
	        'price':round(sale_price),
	        'mrp':round(mrp),
	        'discount':round(discount),
	        'image':image,
	        'rating_count':rating_count
	    })
	return mainPack
def getSnapDeal(keyword):
	query = keyword
	URL = "https://www.snapdeal.com/search?keyword="+query+"&santizedKeyword=mobie&catId=175&categoryId=0&suggested=false&vertical=p&noOfResults=20&searchState=&clickSrc=go_header&lastKeyword=&prodCatId=&changeBackToAll=false&foundInAll=false&categoryIdSearched=&cityPageUrl=&categoryUrl=&url=&utmContent=&dealDetail=&sort=rlvncy"
	r = requests.get(URL) 
	soup = BeautifulSoup(r.content)
	container_divs = soup.findAll("div",attrs={"class":"col-xs-6 favDp product-tuple-listing js-tuple"})
	mainPack = []
	for i in container_divs:
	    try:
	        img_src = i.find("img",attrs={"class":"product-image"})['src']
	    except:
	        img_src = i.find("img",attrs={"class":"lazy-load"})['data-src']
	    link = i.find("a")['href']
	    title = i.find("p",attrs={"class":"product-title"}).text
	    sale_price = i.find("span",attrs={"class":"lfloat product-price"})['data-price']
	    try:
	        rating_width = int(float(i.find("div",attrs={"class":"filled-stars"})['style'].strip("width: %")))
	        rating = int(rating_width_to_rating(rating_width))
	        rating_count = int(i.find("p",attrs={"class":"product-rating-count"}).text.strip("()"))
	    except:
	        rating = 0
	        rating_count = 0
	    mrp = int(i.find("span",attrs={"class":"lfloat product-desc-price strike"}).text.strip("Rs.").replace(",",""))
	    discount = int(mrp)-int(sale_price)
	    pack = {
	        'url':link,
	        'title':title,
	        'image':img_src,
	        'price':sale_price,
	        'rating_count':rating_count,
	        'rating':rating,
	        'mrp':mrp,
	        'discount':discount
	    }
	    mainPack.append(pack)
	return mainPack
def getFlipkart(keyword):
	query = keyword
	page = 0;
	URL = "https://www.flipkart.com/search?q="+query+"&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page="+str(page)
	r = requests.get(URL) 
	soup = BeautifulSoup(r.content)
	containers = soup.findAll("div",attrs={"class":"_3O0U0u"})
	subcontainers = []
	for i in containers:
	    for j in i.findAll("div",attrs={"style":"width:100%"}):
	        subcontainers.append(j)
	    for j in i.findAll("div",attrs={"style":"width:25%"}):
	        subcontainers.append(j)
	mainDict = []
	for item in subcontainers:
	    try:
	        title = item.find("div",attrs={"class":"_3wU53n"}).text
	    except:
	    	try:
	    		title = item.find("a",attrs={"a","_2mylT6"}).text
	    	except:
	        	try:
	        		title = item.find("a",attrs={"a","_2cLu-l"})['title']
	        	except:
	        		continue
	    sale_price = int(item.find("div",attrs={"class":"_1vC4OE"}).text.replace("\u20B9","").replace(",",""))
	    try:
	        mrp = int(item.find("div",attrs={"class":"_3auQ3N"}).text.replace("\u20B9","").replace(",",""))
	    except:
	        mrp = 0
	    try:
	        rating = float(item.find("div",attrs={"class":"hGSR34"}).text)
	    except:
	        rating = 0
	    try:
	        rating_count = int(item.find("span",attrs={"class":"_38sUEc"}).span.span.text.split("Ratings")[0].replace(",",""))
	    except:
	        rating_count = 0
	    try:
	        image = i.find("img",attrs={"class":"s-image"})['src']
	    except:
	        image = ""
	    try:
        	link = item.find("a",attrs={"class":"_31qSD5"})['href']
	    except:
	    	try:
	    		link = item.find("a",attrs={"class":"_3dqZjq"})['href']
	    	except:
	            link = item.find("a",attrs={"class":"_2cLu-l"})['href']
	    link = "https://www.flipkart.com"+link
	    mainDict.append({
	    	'url':link,
	        'title':title,
	        'price':sale_price,
	        'mrp':mrp,
	        'rating':rating,
	        'rating_count':rating_count,
	        'discount':mrp-sale_price
	    })

	return mainDict;
	# query =  keyword;
	# page = 0;
	# URL = "https://www.flipkart.com/search?q="+query+"&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page="+str(page)
	# r = requests.get(URL) 
	# soup = BeautifulSoup(r.content, features="xml") 
	# script = soup.find("script",attrs={"id":"is_script"}).text
	# script = script[29:]
	# script = script[:-3]
	# script = script+"}"	
	# script = json.loads(script)
	# main = []
	# for i in script["pageDataV4"]["page"]["data"]:
	#   for j in script["pageDataV4"]["page"]["data"][i]:
	#     for k in j:
	#       if k == "widget":
	#         for n in j['widget']['data']:
	#           if n == "products":
	#             for l in (j['widget']['data']['products']):
	#                 main.append(l['productInfo'])
	# mainDict = []
	# for i in main:
	#     try:
	#         productId = i['action']['params']['productId']
	#     except:
	#         productId = ""
	#     url = "www.flipkart.com"+i['action']['url']
	#     category = i['value']['analyticsData']['category']
	#     superCategory = i['value']['analyticsData']['superCategory']
	#     try:
	#         keySpecs = (i['value']['keySpecs'])
	#     except:
	#         keySpecs = ""
	#     image = (i['value']['media']['images'][0]['url']).replace('{@width}','300').replace("{@height}","300").replace("{@quality}","100")
	#     discount = i['value']['pricing']['discountAmount']
	#     price = i['value']['pricing']['finalPrice']['value']
	#     rating = (i['value']['rating']['average'])
	#     titles = i['value']['titles']['title']
	#     pack = {
	#         'productId':productId,
	#         'url':url,
	#         'category':category,
	#         'superCategory':superCategory,
	#         'keySpecs':keySpecs,
	#         'image':image,
	#         'discount':discount,
	#         'price':price,
	#         'rating':rating,
	#         'title':titles
	#     }
	#     mainDict.append(pack)
	# return mainDict;
