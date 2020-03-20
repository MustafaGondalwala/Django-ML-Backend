from django.shortcuts import render
from django.http import HttpResponse,JsonResponse
import requests
from bs4 import BeautifulSoup
import json
from django.template.loader import render_to_string
import sys
import json
import pymongo
from bson import json_util, ObjectId

myclient = pymongo.MongoClient("mongodb://Mustafa32:mustafas1@ds263018.mlab.com:63018/cloudinaryimageapp?retryWrites=false")
mydb = myclient["cloudinaryimageapp"]


# Create your views here.
def index(request):
	return HttpResponse(""" 
		<h1>
			Api Page, Visitor not allowed
		</h1>
		""")

def autosuggestion(request):
	query = request.GET['query']
	products = mydb['products']

	URL = "https://www.snapdeal.com/app/get/json/autoSuggestions?sr=true&num=20&ss="+query
	json_data = requests.get(URL).json()
	keyword_list = []
	for keyword in json_data['responseAutosuggestions']:
		keyword_list.append(keyword['keyword'])
	for keyword in json_data['unstructured']:
		keyword_list.append(keyword['keyword'])
	keyword_list = (keyword_list)
	for i in mainDict:
		print(i)

	context = {
		"results": 
			list(set(keyword_list))
		,
		"total":len(keyword_list)
	}
	return JsonResponse(context,safe=False)


def scrape(request,type):
	keyword = request.GET['keyword']
	products = mydb['products']
	products_count = products.find({'type':type,'keyword':keyword})
	if(products_count.count() > 0 ):
		mainDict = json.loads(json_util.dumps(list(products_count)))


	if(type == "flipkart"):
		mainDict = getFlipkart(keyword)
	elif(type == "snapdeal"):
		mainDict = getSnapDeal(keyword)
	elif(type == "tatacliq"):
		mainDict = getTataCliq(keyword)
	elif(type == "amazon"):
		mainDict = getAmazon(keyword)
	for i in mainDict:
		i['keyword'] = keyword
		i['type'] = type
		products.insert(i)

	mainDict = json.loads(json_util.dumps(mainDict))
	context = {
		'query':keyword,
		'type':type,
		'results':mainDict,
		'results_total':len(mainDict)
	}
	return JsonResponse(context,safe=False)
	return render(request,"index.html",{'mainDict':mainDict})






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
	        sale_price = i.find("span",attrs={"class":"a-price-whole"}).text.replace(",","")
	    except:
	        sale_price = 0
	    try:
	        mrp = i.find("span",attrs={"class":"a-price a-text-price"}).span.text.replace("\u20B9","").replace(",","")
	    except:
	        mrp = 0
	    try:
	        rating = i.find("span",attrs={"class":"a-icon-alt"}).text.split(" ")[0]
	    except:
	        rating = None
	    try:
	        rating_count = i.find("div",attrs={"class":"a-row a-size-small"}).find("span",attrs={"class":"a-size-base"}).text.replace(",","")
	    except:
	        rating_count = 0
	    link = "www.amazon.in"+i.find("a",attrs={"class":"a-link-normal a-text-normal"})['href']
	    try:
	        image = i.find("img",attrs={"class":"s-image"})['src']
	    except:
	        image = None
	    try:
	    	mainPack.append({
	    		'url':link,
	    		'image':image,
	    		'title':title,
	    		'price':(sale_price),
	    		'rating_count':(rating_count),
	    		'rating':(rating),
	    		'mrp':(mrp),
	    		'discount':int(mrp)-int(sale_price)
	    	})
	    except:
	    	pass
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
	        rating=None
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
	    print(sale_price)
	    try:
	        rating_width = int(float(i.find("div",attrs={"class":"filled-stars"})['style'].strip("width: %")))
	        rating = rating_width_to_rating(rating_width)
	        rating_count = i.find("p",attrs={"class":"product-rating-count"}).text.strip("()")
	    except:
	        rating = None
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
	query =  keyword;
	page = 0;
	URL = "https://www.flipkart.com/search?q="+query+"&otracker=search&otracker1=search&marketplace=FLIPKART&as-show=on&as=off&page="+str(page)
	r = requests.get(URL) 
	soup = BeautifulSoup(r.content, features="xml") 
	script = soup.find("script",attrs={"id":"is_script"}).text
	script = script[29:]
	script = script[:-3]
	script = script+"}"	
	script = json.loads(script)
	main = []
	for i in script["pageDataV4"]["page"]["data"]:
	  for j in script["pageDataV4"]["page"]["data"][i]:
	    for k in j:
	      if k == "widget":
	        for n in j['widget']['data']:
	          if n == "products":
	            for l in (j['widget']['data']['products']):
	                main.append(l['productInfo'])
	mainDict = []
	for i in main:
	    try:
	        productId = i['action']['params']['productId']
	    except:
	        productId = ""
	    url = "www.flipkart.com"+i['action']['url']
	    category = i['value']['analyticsData']['category']
	    superCategory = i['value']['analyticsData']['superCategory']
	    try:
	        keySpecs = (i['value']['keySpecs'])
	    except:
	        keySpecs = ""
	    image = (i['value']['media']['images'][0]['url']).replace('{@width}','300').replace("{@height}","300").replace("{@quality}","100")
	    discount = i['value']['pricing']['discountAmount']
	    price = i['value']['pricing']['finalPrice']['value']
	    rating = (i['value']['rating']['average'])
	    titles = i['value']['titles']['title']
	    pack = {
	        'productId':productId,
	        'url':url,
	        'category':category,
	        'superCategory':superCategory,
	        'keySpecs':keySpecs,
	        'image':image,
	        'discount':discount,
	        'price':price,
	        'rating':rating,
	        'title':titles
	    }
	    mainDict.append(pack)
	return mainDict



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
