#! /usr/bin/env python

# Copyright 2012 Jtmorgan
 
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
 
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
 
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.

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
section = ''';Total hosts who have participated as of \'\'%s:\'\'<span style="color:#3fb6ff"> %s</span>

{| class=\"wikitable\"
|-
! month
! hosts who participated
! new hosts who joined
! hosts who stopped participating
|-
%s
|}
'''

##FUNCTIONS##
#gets the numeric month and year, and num days in month
def getMonthData(interval, cursor):
	cursor.execute('''select month(date_sub(now(), Interval %d month)), year(date_sub(now(), Interval %d month))''' % (interval, interval))
	row = cursor.fetchone()	
	month = int(row[0])
	year = int(row[1])
	cursor.execute('''select distinct day(last_day(post_date)) from th_up_questions where month(post_date) = %d and year(post_date) = %d''' % (month, year))
	row = cursor.fetchone()		
	days = int(row[0])	
	
	return (month, year, days)
	
#get all the host data for a given month	
def getMonthlyMetrics(month, month_data, cursor):
	metrics = []
	month_year = '| Last month (%s/%s)' % (str(month_data[0]), str(month_data[1]))
	mo_count = getMonthCounts(month_data, cursor)
	new_users = getNewUsers(month_data, cursor)
# 	edits_per_day = getEditsPerDay(month_data, cursor)
	inactive_users = getInactiveUsers(month_data, cursor)
# 	avg_day = round(float(mo_count) / month_data[2],2)
# 	avg_week = avg_day * 7
	metrics.extend([month_year, mo_count, new_users, inactive_users])
	
	return metrics	
	
	
#get counts of hosts participating this month
def getMonthCounts(month_data, cursor):
	cursor.execute('''SELECT COUNT(user_id)
						FROM th_up_hosts
							WHERE
								MONTH(latest_edit) = %d
					''' % (month_data[0]))
	row = cursor.fetchone()
	count = int(row[0])	
	
	return count												


#gets number of new hosts who joined
def getNewUsers(month_data, cursor):
	cursor.execute('''SELECT count(user_id) 
						FROM th_up_hosts
							WHERE MONTH(join_date) = %d 
							AND colleague = 0
					''' % month_data[0])	
	row = cursor.fetchone()
	new = row[0]
	
	return new	
	
	
#gets the number of hosts who have become inactive since last month
def getInactiveUsers(month_data, cursor):
	cursor.execute('''SELECT count(user_id)
						FROM th_up_hosts
							WHERE MONTH(latest_edit) = %d
							AND colleague = 0
					''' % (month_data[0] - 1)) #this doesn't account for the December/January switchover	
	row = cursor.fetchone()
	inactive = row[0]
	
	return inactive	


#compare this month's numbers with last month's, color code the results
def formatTableData(metrics):
	i = 1
	while i < len(metrics):
		metrics[i] = '| %s' % str(metrics[i])
		i+=1
	
	row = '\n'.join(metrics)
	
	return row

	
#posts as a new section to the metrics page		
def postSection(datetime, count, metrics):	
	page = wikitools.Page(wiki, page_namespace + page_title)
	page_text = section % (datetime, count, metrics)
# 	page_text = page_text.encode('utf-8')
	page.edit(page_text, section="new", sectiontitle = "Hosts", summary="HostBot is updating monthly metrics on host participation", bot=1)	

			
## MAIN ##
cursor.execute("SELECT date(NOW()), COUNT(user_id) FROM th_up_hosts WHERE colleague = 0") #get total hosts participating for all time
row = cursor.fetchone()	
cur_datetime = str(row[0])
tot_count = str(row[1])
month_data = getMonthData(1, cursor) #get current month
monthly_metrics = getMonthlyMetrics(1, month_data, cursor)
formatted_metrics = formatTableData(monthly_metrics)
postSection(cur_datetime, tot_count, formatted_metrics) #post it to the metrics page in a new section

cursor.close()
conn.close()