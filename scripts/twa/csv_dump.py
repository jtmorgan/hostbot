#! /usr/bin/env python2.7

# Copyright 2013 Jtmorgan

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

import csv
from datetime import date
import hostbot_settings
import MySQLdb
import wikitools

###needs to be made agnostic, so can accept th or twa invitees
##FUNCTIONS##

def dumpCsv(cursor, curdate, f):
	"""
	Gets all the invited users up 'til now and dumps them into a csv file.
	"""
	writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
	writer.writerow( ('row id', 'output date', 'user id', 'user name', 'user registration date', 'article edits', 'sample group', 'unix dump timestamp', 'invited? y/n', 'blocked? y/n', 'skipped? y/n', 'user talkpage id') )
	cursor.execute("SELECT * from twa_up_invitees")		
	rows = cursor.fetchall()
	for row in rows:
		try:
			writer.writerow( (row[0], curdate, row[1], row[2], row[3], row[4], row[5], row[6], row[7], row[8], row[9], row[10]) )
		except ValueError:
			writer.writerow( ("error!") )

##MAIN##
wiki = wikitools.Wiki(hostbot_settings.apiurl)
wiki.login(hostbot_settings.username, hostbot_settings.password)
conn = MySQLdb.connect(host = hostbot_settings.host, db = hostbot_settings.dbname, read_default_file = hostbot_settings.defaultcnf, use_unicode=1, charset="utf8")
cursor = conn.cursor()
curdate = str(date.today())
output_path = '/data/project/hostbot/public_html/twa_invites.csv'
f = open(output_path, 'wt')
dumpCsv(cursor, curdate, f)
f.close()
cursor.close()
conn.close()
