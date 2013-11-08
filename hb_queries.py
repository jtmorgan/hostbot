#! /usr/bin/python2.7

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

class Query:
	"""queries for database tracking tables"""

	def __init__(self):
		self.mysql_queries = {
'twa sample' : {
	'string' : u"""INSERT IGNORE INTO twa_up_invitees (user_id, user_name, user_registration, edit_count, sample_group, dump_unixtime, invite_status) VALUES (%d, "%s", "%s", %d, "%s", %f, 0)""",
				},
			}	

	def getQuery(self, query_type, query_vars):
		try:
			query_data = self.mysql_queries[query_type]
			query = query_data['string'] % query_vars
			return query
		except:
			print "something went wrong in the query module"	

