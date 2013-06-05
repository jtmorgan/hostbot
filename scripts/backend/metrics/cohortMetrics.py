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
import query

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
		query_lib = query.Queries()
		queries = query_lib.badgeQueries(self.group_type)
		usr_data = []
		dbquery = queries['experimental'] #stopped here
		print dbquery
		self.cursor.execute(dbquery) #gets the experimental sample
		rows = cursor.fetchall()
		for row in rows:
			usr_data.append(['experimental',row[0], row[1]])
		dbquery = queries['control']
		print dbquery
		self.cursor.execute(dbquery) #gets the control sample
		rows = cursor.fetchall()
		for row in rows:
			usr_data.append(['control',row[0], row[1]])
			print row[1]
		usr_activity = self.getActivity(usr_data, queries)

	def getActivity(self, usr_data, queries):
		"""
		find out what they've been up to on-wiki
		"""
		for usr in usr_data:
			dbquery = queries['activity'] % (usr[1], '%Y%m%d%H%i%s')
			self.cursor.execute(dbquery)
			row = cursor.fetchone()
			usr.append(row[0])
		print usr_data
		self.csvExport(usr_data)

	def csvExport(self, usr_data):
		"""prints it all to csv"""
		f = open(sys.argv[2], 'wt') #you tell it what to name the files at the command line
		writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
		writer.writerow( ('condition', 'user id', 'sample date', 'subsequent activity') )
		for usr in usr_data:
			writer.writerow( (usr[0], usr[1], usr[2], usr[3]) )
		f.close()


##MAIN###
group_info = sys.argv[1] #you specify the group name at the command line
print group_info
users = Data(group_info, cursor)
user_data = users.getUserData()

cursor.close()
conn.close()