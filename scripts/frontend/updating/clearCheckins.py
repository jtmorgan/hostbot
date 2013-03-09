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

import MySQLdb
import wikitools
import settings
from datetime import datetime
import logging

wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)

conn = MySQLdb.connect(host = 'db67.pmtpa.wmnet', db = 'jmorgan', read_default_file = '~/.my.cnf', use_unicode=1, charset="utf8" )
cursor = conn.cursor()

logging.basicConfig(filename='logs/checkins.log',level=logging.INFO)

 ##GLOBAL VARIABLES AND TEMPLATES
checkin_list = []
curtime = str(datetime.utcnow())
#the page where hosts check in
sub_domain = 'Teahouse/Host_checkin'  

page_namespace = u'Wikipedia:'

target_template = '''%s
'''
checkin_template = '''= Recent checkins as of {{CURRENTDAYNAME}}, {{CURRENTMONTHNAME}} {{CURRENTDAY}} ='''

#determines if there are any users to check in
def findCheckins(cursor):
	global checkin_list
	cursor.execute('''select rev_user_text from enwiki.revision where rev_page = 36967956 and rev_comment = "/* {{subst:REVISIONUSER}} */ new section" and rev_timestamp > DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 1 DAY),'%Y%m%d%H%i%s')
	''')	
	rows = cursor.fetchall()
	checkins = False
	if rows:
		checkins = True
		for row in rows:
			checkin = row[0]
			checkin_list.append(checkin)	
		logging.info('Checked in ' + ' '.join(checkin_list) + ' ' + curtime)
	else:
		logging.info('No checkins today ' + curtime)

	return checkins

# #clears checkin page
def clearCheckinList():
	page_path = page_namespace + sub_domain	
	page = wikitools.Page(wiki, page_path)
	page.edit(checkin_template, section=1, summary="HostBot is automatically clearing the list of recently [[WP:Teahouse/Host_checkin|checked in]] hosts. Profiles in [[WP:Teahouse/Host_breakroom]] will be move to [[WP:Teahouse/Host_landing]]", bot=1)

##Main##
checkins = findCheckins(cursor)
if checkins:
	clearCheckinList()

cursor.close()
conn.close()