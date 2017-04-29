#! /usr/bin/env python

class Query:
	"""queries for database tracking tables"""

	def __init__(self):
		self.mysql_queries = {
'teahouse experiment newbies' : {
    'string' : u"""insert ignore into th_up_invitees_current
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
'tm insert records' : {
    'string' : """insert ignore into tm_up_invitees
	(user_id, user_name, user_registration, user_editcount, sample_date, sample_type)
	SELECT user_id, user_name, user_registration, user_editcount, NOW(), 1
	FROM enwiki_p.user
	WHERE user_registration > DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 1 DAY),'%Y%m%d%H%i%s')
	AND user_editcount >=2
	AND user_id NOT IN (SELECT ug_user FROM enwiki_p.user_groups WHERE ug_group = 'bot')
	AND user_name not in (SELECT REPLACE(log_title,"_"," ") from enwiki_p.logging
		where log_type = "block" and log_action = "block"
		and log_timestamp >  DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 1 DAY),'%Y%m%d%H%i%s'))""",
		        },
'th experiment invitees' : {
	'string' : u"""SELECT user_name, user_id, user_talkpage
		FROM th_up_invitees_current
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
'tm select records' : { #need to make sure I'm not selecting skips
	'string' : u"""SELECT user_name, user_id, user_talkpage
		FROM tm_up_invitees
		WHERE date(sample_date) = date(NOW())
		AND sample_type = 1
		AND invite_status IS NULL
		AND (ut_is_redirect = 0 OR ut_is_redirect IS NULL)""",
				},
'update th invite status' : {
	'string' : u"""update th_up_invitees_current set sample_group = '%s', invite_status = %d,  hostbot_skipped = %d where user_id = %d""",
				},
'update test invite status' : { #when using the test db th_invite_test
	'string' : u"""update th_invite_test set sample_group = '%s', invite_status = %d,  hostbot_skipped = %d where user_id = %d""",
				},
'tm update invite status' : {
	'string' : """update tm_up_invitees set sample_group = '%s', invite_status = %d,  hostbot_skipped = %d where user_id = %d""",
				},
'th add talkpage' : {
	'string' : u"""UPDATE th_up_invitees_current as i, enwiki_p.page as p
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
'tm add talkpage' : {
	'string' : """UPDATE tm_up_invitees as i, enwiki_p.page as p
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