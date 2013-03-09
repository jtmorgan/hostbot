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
questions_section = ''';Total questions asked as of \'\'%s:\'\'<span style="color:#3fb6ff"> %s</span>

{| class=\"wikitable\"
|-
! month
! questions
! questions per day
! questions per week
! average questions per guest
! average responses per question
! mean time to first response
|-
%s
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
	
#get all the question data for a given month	
def getMonthlyMetrics(month, month_data, cursor):
	alldata = []
	if month == 1:
		month_year = '| Last month (%s/%s)' % (str(month_data[0]), str(month_data[1]))
	else:
		month_year = '| Two months ago (%s/%s)' % (str(month_data[0]), str(month_data[1]))
	q_mo_count = getMonthCounts(month_data, cursor)
	q_avg_day = round(float(q_mo_count) / month_data[2],2)
	q_avg_week = q_avg_day * 7
	q_avg_restime = getAvgResponseTime(month_data, cursor)
	q_avg_guest = getAvgPerGuest(month_data, cursor)
	q_avg_ans = getAvgAnswers(month_data, cursor)
	alldata.extend([month_year, q_mo_count, q_avg_day, q_avg_week, q_avg_guest, q_avg_ans, q_avg_restime])
	
	return alldata	
	
	
#get counts of questions per month
def getMonthCounts(month_data, cursor):
	cursor.execute('''SELECT COUNT(rev_id)
						FROM th_up_questions
							WHERE
								MONTH(post_date) = %d
					''' % (month_data[0]))
	row = cursor.fetchone()
	count = int(row[0])	
	
	return count												


#gets the average num answers to questions
def getAvgAnswers(month_data, cursor):
	cursor.execute('''SELECT AVG(answers) 
						FROM th_up_questions 
							WHERE MONTH(post_date) = %d 
							AND answers > 0;
					''' % month_data[0])	
	row = cursor.fetchone()
	avg = float(round(row[0],2))
	
	return avg	
	
	
#gets the mean time to first response to question, in minutes
def getAvgResponseTime(month_data, cursor):
	cursor.execute('''SELECT AVG(diff) 
						FROM 
							(SELECT TIMESTAMPDIFF(MINUTE, post_date, first_answer_date) 
									AS diff 
										FROM th_up_questions 
											WHERE MONTH(post_date) = %d 
												AND answers > 0) AS tmp;
					''' % month_data[0])	
	row = cursor.fetchone()
	avg = float(round(row[0],2))
	
	return avg		

#get the average num questions per guest
def getAvgPerGuest(month_data, cursor):
	cursor.execute('''SELECT AVG(questions) 
						FROM (select count(rev_id) as questions 
							FROM th_up_questions 
								WHERE MONTH(post_date) = %d 
								GROUP BY rev_user_text) as tmp;
					''' % month_data[0])	
	row = cursor.fetchone()
	avg = float(round(row[0],2))
	
	return avg	

#compare this month's numbers with last month's, color code the results
def compareMonths(cur, prev):
	i = 1
	while i < len(cur):
		if i == len(cur) - 1: #lower response times are better
			if cur[i] < prev[i]:
				cur[i] = '| style=\"background: LightGreen\" | %s' % str(cur[i])
			elif cur[i] > prev[i]:
				cur[i] = '| style=\"background: Tomato\" | %s' % str(cur[i])
			else:
				cur[i] = '| %s' % str(cur[i])
		else:
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

	
#posts a section to the metrics page, one section at a time				
def postSection(cur_datetime, q_tot_count, bothmonth_data):	
# 	print questions_section % (cur_datetime, q_tot_count, bothmonth_data[0], bothmonth_data[1])
	page = wikitools.Page(wiki, page_namespace + page_title)
	page_text = questions_section % (cur_datetime, q_tot_count, bothmonth_data[1], bothmonth_data[0])
# 	page_text = page_text.encode('utf-8')
	page.edit(page_text, section="new", sectiontitle = "Questions", summary="HostBot is updating monthly metrics on questions", bot=1)	

			
## MAIN ##
cursor.execute("SELECT date(NOW()), COUNT(rev_id) FROM th_up_questions WHERE week > 8;") #get total questions for all time
row = cursor.fetchone()	
cur_datetime = str(row[0])
q_tot_count = str(row[1])
month_data = getMonthData(1, cursor) #get current month
curmonth_data = getMonthlyMetrics(1, month_data, cursor)
month_data = getMonthData(2, cursor) #get last month's data
prevmonth_data = getMonthlyMetrics(2, month_data, cursor)
bothmonth_data = compareMonths(curmonth_data, prevmonth_data) #compare the two months
postSection(cur_datetime, q_tot_count, bothmonth_data) #post it to the metrics page in a new section

cursor.close()
conn.close()