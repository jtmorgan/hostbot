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
import hostbot_settings
import sys
import csv
from queries import Queries as q

conn = MySQLdb.connect(host = hostbot_settings.host, db = hostbot_settings.dbname, read_default_file = '~/.my.cnf', use_unicode=1, charset="utf8" )
cursor = conn.cursor()

###CLASSES###
class Data:
	"""some data about a group of users"""

	def __init__(self, group_info, cursor):
		"""
		set the variables we're going to use to generate our dataset
		"""
		self.cursor = cursor
		self.group_type = group_info

	def getUserData(self):
		"""
		generate a list of our userdata
		"""
		query_lib = q()
		queries = query_lib.badgeQueries(self.group_type)
		usr_data = []
		query = self.queries['welcome']['experimental'] #stopped here
		print query
		self.cursor.execute(query) #gets the experimental sample
		rows = cursor.fetchall()
		for row in rows:
			usr_data.append(['experimental',row[0], row[1]] for row in rows)
		query = self.queries['control']
		print query
		self.cursor.execute(query) #gets the control sample
		rows = cursor.fetchall()
		for row in rows:
			usr_data.append(['control',row[0], row[1]] for row in rows)
		usr_activity = getActivity(usr_data)

	def getActivity(self, usr_data):
		"""
		find out what they've been up to on-wiki
		"""
		query = self.queries['activity']
		for usr in usr_data:
			self.cursor.execute(query % (usr, '%Y%m%d%H%i%s'))
			row = cursor.fetchone()
			usr.append(row[0])
		print usr_data
		csvExport(usr_data)

	def csvExport(usr_data):
		"""prints it all to csv"""
		f = open(sys.argv[2], 'wt') #you tell it what to name the files at the command line
		writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
		writer.writerow( ('condition', 'user id', 'sample date', 'subsequent activity') )
		for usr in usr_data:
			writer.writerow(x for x in usr)
		f.close()


##MAIN###
group_info = sys.argv[1] #you specify the group name at the command line
print group_info
users = Data(group_info, cursor)
user_data = users.getUserData()

cursor.close()
conn.close()