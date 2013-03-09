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

conn = MySQLdb.connect(host = 'db67.pmtpa.wmnet', db = 'jmorgan', read_default_file = '~/.my.cnf' )

cursor = conn.cursor()

#updates the Teahouse page list
cursor.execute('''
insert ignore into th_pages (page_id, page_namespace, page_title, page_touched) select page_id, page_namespace, page_title, page_touched from enwiki.page where page_namespace in (4,5) and page_title like "Teahouse/%";
''')
conn.commit()
	
cursor.close()
conn.close()
	

