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
'twa invites' : {
	'string' : u"""SELECT user_name, user_talkpage FROM twa_up_invitees WHERE dump_unixtime = (select max(dump_unixtime) from twa_up_invitees) AND invite_status = 0 AND block_status IS NULL AND skipped IS NULL AND sample_group = 'exp'""",
				},	
'twa blocked' : {
	'string' : u"""UPDATE twa_up_invitees AS t SET t.blocked = 1 WHERE REPLACE(t.user_name," ","_") IN (SELECT l.log_title FROM enwiki_p.logging AS l WHERE l.log_timestamp > DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 3 DAY),'%Y%m%d%H%i%s') AND l.log_type = "block" and l.log_action = "block")""",
				},
'twa talkpage' : {
	'string' : u"""UPDATE twa_up_invitees AS t, enwiki_p.page AS p SET t.user_talkpage = p.page_id WHERE p.page_namespace = 3 and p.page_is_redirect = 0 AND REPLACE(t.user_name," ","_") = p.page_title""",
				},						
'twa invited' : {
	'string' : u""" """,
				},		
'twa skipped' : {
	'string' : u""" """,														
			}	

	def getQuery(self, query_type, query_vars = False):
		try:
			query_data = self.mysql_queries[query_type]
			if query_vars:
				query = query_data['string'] % query_vars
			else:
				pass	
			return query
		except:
			print "something went wrong in the query module"	


