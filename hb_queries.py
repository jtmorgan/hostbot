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
'five edit newbies' : {
    'string' : u"""insert ignore into th_up_invitees_experiment_2
	(user_id, user_name, user_registration, user_editcount, sample_date, sample_type)
	SELECT user_id, user_name, user_registration, user_editcount, NOW(), 3
	FROM enwiki_p.user
	WHERE user_registration > DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 2 DAY),'%Y%m%d%H%i%s')
	AND user_editcount BETWEEN 5 AND 9
	AND user_id NOT IN (SELECT ug_user FROM enwiki_p.user_groups WHERE ug_group = 'bot')
	AND user_name not in (SELECT REPLACE(log_title,"_"," ") from enwiki_p.logging
		where log_type = "block" and log_action = "block"
		and log_timestamp >  DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 2 DAY),'%Y%m%d%H%i%s'))""",
		        },
'teahouse experiment newbies' : {
    'string' : u"""insert ignore into th_up_invitees_experiment_2
	(user_id, user_name, user_registration, user_editcount, sample_date, sample_type)
	SELECT user_id, user_name, user_registration, user_editcount, NOW(), 4
	FROM enwiki_p.user
	WHERE user_registration > DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 2 DAY),'%Y%m%d%H%i%s')
	AND user_editcount >=5
	AND user_id NOT IN (SELECT ug_user FROM enwiki_p.user_groups WHERE ug_group = 'bot')
	AND user_name not in (SELECT REPLACE(log_title,"_"," ") from enwiki_p.logging
		where log_type = "block" and log_action = "block"
		and log_timestamp >  DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 2 DAY),'%Y%m%d%H%i%s'))""",
		        },
'teahouse test' : { #when using the test db th_invite_test
    'string' : u"""insert ignore into th_invite_test
	(user_id, user_name, user_registration, user_editcount, sample_date, sample_type)
	SELECT user_id, user_name, user_registration, user_editcount, NOW(), 4
	FROM enwiki_p.user
	WHERE user_registration > DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 2 DAY),'%Y%m%d%H%i%s')
	AND user_editcount >=5
	AND user_id NOT IN (SELECT ug_user FROM enwiki_p.user_groups WHERE ug_group = 'bot')
	AND user_name not in (SELECT REPLACE(log_title,"_"," ") from enwiki_p.logging
		where log_type = "block" and log_action = "block"
		and log_timestamp >  DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 2 DAY),'%Y%m%d%H%i%s'))""",
		        },			        		        
'ten edit newbies' : {
    'string' : u"""insert ignore into th_up_invitees_experiment_2
	(user_id, user_name, user_registration, user_editcount, sample_date, sample_type)
	SELECT user_id, user_name, user_registration, user_editcount, NOW(), 1
	FROM enwiki_p.user
	WHERE user_registration > DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 2 DAY),'%Y%m%d%H%i%s')
	AND user_editcount >= 10
	AND user_id NOT IN (SELECT ug_user FROM enwiki_p.user_groups WHERE ug_group = 'bot')
	AND user_name not in (SELECT REPLACE(log_title,"_"," ") from enwiki_p.logging
		where log_type = "block" and log_action = "block"
		and log_timestamp >  DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 2 DAY),'%Y%m%d%H%i%s'))""",
		        },		        
'autoconfirmed newbies' : {
    'string' : u"""insert ignore into th_up_invitees_experiment_2
	(user_id, user_name, user_registration, user_editcount, sample_date, sample_type)
	SELECT user_id, user_name, user_registration, user_editcount, NOW(), 2 from enwiki_p.user where user_editcount >= 10 and user_registration between DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 5 DAY),'%Y%m%d%H%i%s') and DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 4 DAY),'%Y%m%d%H%i%s') AND user_name not in (SELECT REPLACE(log_title,"_"," ") from enwiki_p.logging where log_type = "block" and log_action = "block" and log_timestamp >  DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 5 DAY),'%Y%m%d%H%i%s'))""",
		        },
'th invitees' : {
	'string' : u"""SELECT user_name, user_id, user_talkpage
		FROM th_up_invitees_experiment_2
		WHERE date(sample_date) = date(NOW())
		AND sample_type = 4
		AND invite_status IS NULL
		AND (ut_is_redirect = 0 OR ut_is_redirect IS NULL)""",
				},
'th experiment invitees' : {
	'string' : u"""SELECT user_name, user_id, user_talkpage
		FROM th_up_invitees_experiment_2
		WHERE date(sample_date) = date(NOW())
		AND sample_type = 4
		AND invite_status IS NULL
		AND (ut_is_redirect = 0 OR ut_is_redirect IS NULL)""",
				},
'th test invitees' : { #when using the test db th_invite_test
	'string' : u"""SELECT user_name, user_id, user_talkpage
		FROM th_invite_test
		WHERE date(sample_date) = date(NOW())
		AND sample_type = 4
		AND invite_status IS NULL
		AND (ut_is_redirect = 0 OR ut_is_redirect IS NULL)""",
				},								
'twa invitees' : {
	'string' : u"""SELECT user_name, user_id, user_talkpage
		FROM th_up_invitees_experiment_2
		WHERE date(sample_date) = date(NOW())
		AND sample_type = 4
		AND invite_status IS NULL
		AND (ut_is_redirect = 0 OR ut_is_redirect IS NULL)""",
				},
'testwiki invitees' : {#only use when hostbot_settings url is set to testwiki
	'string' : u"""select user_name, user_id, NULL from testwiki_p.user u join testwiki_p.page p on u.user_name = p.page_title where u.user_name like "Jmtest%" and p.page_namespace = 2""",
				},								
'update th invite status' : { 
	'string' : u"""update th_up_invitees_experiment_2 set sample_group = '%s', invite_status = %d,  hostbot_skipped = %d where user_id = %d""",
				},
'update test invite status' : { #when using the test db th_invite_test
	'string' : u"""update th_invite_test set sample_group = '%s', invite_status = %d,  hostbot_skipped = %d where user_id = %d""",
				},				
'th add talkpage' : {
	'string' : u"""UPDATE th_up_invitees_experiment_2 as i, enwiki_p.page as p
		SET i.user_talkpage = p.page_id, i.ut_is_redirect = p.page_is_redirect
		WHERE date(i.sample_date) = date(NOW())
		AND p.page_namespace = 3
		AND REPLACE(i.user_name, " ", "_") = p.page_title
		AND i.user_talkpage IS NULL""",
				},
'th add talkpage test' : { #when using the test db th_invite_test
	'string' : u"""UPDATE th_invite_test as i, enwiki_p.page as p
		SET i.user_talkpage = p.page_id, i.ut_is_redirect = p.page_is_redirect
		WHERE date(i.sample_date) = date(NOW())
		AND p.page_namespace = 3
		AND REPLACE(i.user_name, " ", "_") = p.page_title
		AND i.user_talkpage IS NULL""",
				},		
}

	def getQuery(self, query_type, query_vars = False):
		if query_type in self.mysql_queries:
			query = self.mysql_queries[query_type]['string'].encode("utf8")
			if query_vars:
				query = query % tuple(query_vars) #should accept a list containing any number of vars

			else:
				pass
			return query
		else:
			print "something went wrong with query of type " + query_type