import urllib2 as u2
from datetime import datetime
import operator
import json
import wikitools
import MySQLdb
import settings

wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)
conn = MySQLdb.connect(host = 'db67.pmtpa.wmnet', db = 'jmorgan', read_default_file = '~/.my.cnf' )
cursor = conn.cursor()

##OUTPUT COMPONENTS##
#the namespace where the metrics will go
page_namespace = u'Wikipedia:'

#the page where the metrics will go
page_title = 'Teahouse/Host_lounge/Metrics'

#section template
section_template = '''Total page views for [[WP:Teahouse|the Teahouse main page]] (not including sub-pages) last month.

{| class=\"wikitable\"
|-
! month
! total pageviews
! pageviews per day
|-
%s
|-
%s
|}
'''

pageview_url = 'http://stats.grok.se/json/en/%s%s/Wikipedia:Teahouse'

# months = []

#this is a manually curated list. Need to add the same dates for 2013, or this script will break. 
null_dates = ["2012-02-29","2012-02-30","2012-02-31","2012-04-31","2012-06-31","2012-09-31","2012-11-31","2013-02-29","2013-02-30","2013-02-31","2013-04-31","2013-06-31","2013-09-31","2013-11-31"]

##FUNCTIONS##
#gets the numeric month and year, and num days in month
def getMonthData(interval, cursor):
	cursor.execute('''select month(date_sub(now(), Interval %s month)), year(date_sub(now(), Interval %s month))''', (interval, interval))
	row = cursor.fetchone()	
	month = str(row[0])
	year = str(row[1])
	if len(month) == 1:
		month = '0' + month
	print (month, year)
	return (month, year)

#gets list of pageviews by day for month
def getMonthlyPvList(month_data, pageview_url):
	pv_list = []
	sock = u2.urlopen(pageview_url % (month_data[1], month_data[0]))
	views = sock.read()
	pv_data = json.loads(views)
	pv = pv_data['daily_views']
	for key, value in pv.iteritems():
		temp = (key,value)  
		if temp[0] not in null_dates:
			pv_list.append(temp)	            
# 	pv_list = sorted(pv_list, key=get_date, reverse = False)
	
	return pv_list
	        
	        
# def get_date(record):
#     return datetime.strptime(record[0],"%Y-%m-%d")

#computes total and average pageviews per month
def getMonthlyPvMetrics(interval, pv_list, month_data):
	alldata = []
	if interval == 1:
		month_year = '| Last month (%s/%s)' % (str(month_data[0]), str(month_data[1]))
	else:
		month_year = '| Two months ago (%s/%s)' % (str(month_data[0]), str(month_data[1]))	
	pv_mo_count = sum([pv[1] for pv in pv_list])
	pv_avg_day = round(float(pv_mo_count) / len(pv_list),2)
	alldata.extend([month_year, str(pv_mo_count), str(pv_avg_day)])

	return alldata


def compareMonths(cur, prev):
	i = 1
	while i < len(cur):
		if cur[i] > prev[i]:
			cur[i] = '| style=\"background: LightGreen\" | %s' % str(cur[i])
		elif cur[i] < prev[i]:
			cur[i] = '| style=\"background: Tomato\" | %s' % str(cur[i])
		else:
			cur[i] = '| %s' % str(cur[i])
		prev[i] = '| %s' % str(prev[i])		
		i+=1
	
	prev_row = '\n'.join(prev)
	cur_row = '\n'.join(cur)
	
	return (prev_row, cur_row)
	
	
def postSection(bothmonth_data):	
	page = wikitools.Page(wiki, page_namespace + page_title)
	page_text = section_template % (bothmonth_data[1], bothmonth_data[0])
# 	page_text = page_text.encode('utf-8')
	page.edit(page_text, section="new", sectiontitle = "Page views", summary="HostBot is updating monthly metrics on page views", bot=1)	
	
	
##MAIN##	
month_data = getMonthData(1, cursor) #get current month
pv_list = getMonthlyPvList(month_data, pageview_url)
curmonth_data = getMonthlyPvMetrics(1, pv_list, month_data)
month_data = getMonthData(2, cursor) #get previous month
pv_list = getMonthlyPvList(month_data, pageview_url)
prevmonth_data = getMonthlyPvMetrics(2, pv_list, month_data)
bothmonth_data = compareMonths(curmonth_data, prevmonth_data) #compare the two months
# postSection(bothmonth_data) #post it to the metrics page in a new section

    
    
