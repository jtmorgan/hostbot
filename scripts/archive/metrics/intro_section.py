#! /usr/bin/python2.7

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
import hostbot_settings

wiki = wikitools.Wiki(hostbot_settings.apiurl)
wiki.login(hostbot_settings.username, hostbot_settings.password)
conn = MySQLdb.connect(host = hostbot_settings.host, db = hostbot_settings.dbname, read_default_file = hostbot_settings.defaultcnf, use_unicode=1, charset="utf8")
cursor = conn.cursor()

##OUTPUT COMPONENTS##
#the namespace where the metrics will go
page_namespace = u'Wikipedia:'

#the page where the metrics will go
page_title = 'Teahouse/Host_lounge/Metrics'

#section template
section = u'''
<noinclude>[[Category:Wikipedia Teahouse]]</noinclude><div style="width:100%%; margin-top: -1em; font-family:arial; sans-serif; padding-bottom: 4em; background-color:#f4f3f0;">
<div style="height:40px;"></div>

<div style="margin: 1em 5em;">
[[File:Wikimedia_data.jpg|right|175px]]
<span style="color: #333; line-height: 100%%; font-weight: normal; margin-top: 20px; font-style: normal; mso-bidi-font-style: italic;"><font size="8.0pt">Teahouse<span style="color:#3fb6ff">:monthly metrics</span></font></span>
<div class="tagline" style="margin: 10px auto 20px 35px;">
<span style="color: #333; line-height: 100%%; font-weight: normal; font-style: normal; mso-bidi-font-style: italic"><font size="4.0pt">%s/1/%s through %s/%s/%s</font></span>
</div>

{| class="infobox" style="width: 175px;"
| colspan="2" | \'\'\'Want more data?\'\'\' The metrics report from the pilot period is available [[meta:Research:Teahouse/Metrics|in the Pilot Metrics Report]], and cumulative metrics through the end of [[meta:Research:Teahouse/Phase_2_report|Phase 2]] are available [[meta:Research:Teahouse/Phase_2_report/Metrics|Phase 2 Metrics Report]]. Previous incremental metrics are available [[meta:Research:Teahouse/Metrics/Archive|here]].
|}

<div style="width:80%%">
\'\'\'Activity metrics from the last month are presented below.\'\'\' For comparison, metrics for the month before are also listed. Numbers that have improved over the previous month are in <span style="background: LightGreen; font-weight:bold;">green</span>, declines in activity (and increases in response time) are highlighted in <span style="background: Tomato; font-weight:bold;">red</span>.

:\'\'This report is automatically generated on the first of every month by [[User:HostBot|HostBot]]. To check on the status of automated invites, go to [[Wikipedia:Teahouse/Hosts/Database_reports|the invitee reports page]]. If you have questions, chat up [[User:Jtmorgan|Jtmorgan]].\'\'
</div>
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



#posts as a new section to the metrics page
def postSection(month_data, section):
# 	print section % (str(month_data[0]),str(month_data[1]),str(month_data[0]),str(month_data[2]),str(month_data[1]))
	page = wikitools.Page(wiki, page_namespace + page_title)
	page_text = section % (str(month_data[0]),str(month_data[1]),str(month_data[0]),str(month_data[2]),str(month_data[1]))
# 	page_text = page_text.encode('utf-8')
	page.edit(page_text, summary="HostBot is adding the monthly automated metrics intro section for %s/%s" % (str(month_data[0]),str(month_data[1])), bot=1)


## MAIN ##
month_data = getMonthData(1, cursor) #get current month
postSection(month_data, section) #post it to the metrics page in a new section

cursor.close()
conn.close()