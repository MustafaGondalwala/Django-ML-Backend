from django.shortcuts import render
from django.http import HttpResponse,JsonResponse

from .scrape import harvard_scrape as h_scrape
from .scrape import techcrunch_scrape as t_scrape
from .scrape import topheadline_scrape as top_scrape
from .scrape import startup_scrape as s_scrape
import pymysql

def index(request):
	return HttpResponse(""" 
		<h1>
			Api Page, Visitor not allowed
		</h1>
		""")


def connection():
    conn = pymysql.connect(host="mustafa-db.cyptmcja8bd2.us-east-2.rds.amazonaws.com",
                           user = "mustafa",
                           passwd = "mustafas1",
                           db = "quicknews")
    c = conn.cursor()
    return c, conn


def scrapeAll(request):
	scrape(request,type="harvard")
	scrape(request,type="techcrunch")
	scrape(request,type="startup")
	scrape(request,type="top10")
	return JsonResponse({"Done":"All"})
def scrape(request,type="all"):
	try:
		c,conn = connection()
	except:
		return JsonResponse({"error":True,"message":"Error Occured"})
	if(type=="harvard"):
		store = h_scrape.getCurrentHarvard()
	elif(type=="techcrunch"):
		store = t_scrape.getCurrentTechcrush()
	elif(type=="startup"):
		store = s_scrape.getCurrentStartup()
	elif(type=="top10"):
		store = top_scrape.getCurrentTopHeadline()
	else:
		return "Sorry Not Found";
	for i in store:
		try:
			c.execute("INSERT INTO `quicknews`.`coreapi_news` (`type`, `title`, `link`, `image_link`, `created_date`) VALUES ('"+type+"', '"+(i[0])+"', '"+i[1]+"', '"+i[2]+"', '"+str(current_time.now())+"')")
		except:
			pass
	conn.commit()
	return JsonResponse(store,safe=False);



# @app.route('/get/<type>')
def get(request,type,justNews=False):
	try:
		c, conn = connection()
	except Exception as e:
		return str(e)
	l = ['harvard','startup','techcrunch','top10']
	if(type not in l):
		return jsonify([]);
	c.execute("select * from quicknews.coreapi_news where type='"+type+"' order by created_date DESC LIMIT 10;")
	records = c.fetchall()
	news = []
	for i in records:
		item = {
					'title':i[2],
					'url':i[3],
					'urlToImage':i[4],
					'created_date':i[5]
				}
		news.append(item)
	if(justNews==True):
		return news;
	context = {
		'items': news,
		'length': len(news),
		'type':type
	}	
	return JsonResponse(context,safe=False)



# @app.route('/get')
def getAll(request):
	news = []
	news.extend(get(request,type="harvard",justNews=True))
	news.extend(get(request,type="startup",justNews=True))
	news.extend(get(request,type="techcrunch",justNews=True))
	context = {
		'items': news,
		'length': len(news),
		'type':"all"
	}	
	return JsonResponse(context,safe=False)
	
