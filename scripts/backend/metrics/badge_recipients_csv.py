#! /usr/bin/env python

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

# this script prints out the results of the badge table in CSV form
import MySQLdb
import csv
import sys

conn = MySQLdb.connect(host = 'db67.pmtpa.wmnet', db = 'jmorgan', read_default_file = '~/.my.cnf', use_unicode=1, charset="utf8" )
cursor = conn.cursor()


# gets the hosts who are nn the breakroom, and newly active from the database table
f = open(sys.argv[1], 'wt')
writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
writer.writerow( ('User_page','User_page_namespace', 'Date_awarded', 'Badge', 'Badge_page') )	
cursor.execute('''
	SELECT
	bap_title, bap_ns, ba_date, b_name, bpage_title FROM th_ba_temp as a JOIN th_badges as b ON a.b_id = b.b_id;
	''')
	
rows = cursor.fetchall()
for row in rows:
	page_title = row[0]
	page_ns = row[1]
	date = row[2]
	badge = row[3]
	bpage = row[4]
	writer.writerow( (page_title, page_ns, date, badge, bpage) )

f.close()
cursor.close()
conn.close()