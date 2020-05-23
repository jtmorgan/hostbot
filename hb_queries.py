#! /usr/bin/env python

class Query:
    """queries for database tracking tables"""

    def __init__(self):
        self.mysql_queries = {
'select th sample' : {#should sub-sample in code for test, not in a separate query
    'string' : """SELECT u.user_id, u.user_name, u.user_registration, u.user_editcount, NOW(), 4
    FROM enwiki_p.user AS u WHERE (u.user_editcount >= 5 AND u.user_editcount < 100) AND u.user_id IN
(SELECT a.actor_user AS uid FROM enwiki_p.recentchanges AS r JOIN enwiki_p.actor AS a ON r.rc_actor = a.actor_id WHERE r.rc_log_type = "newusers"
AND r.rc_log_action != "autocreate"
AND r.rc_timestamp > DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 2 DAY),'%Y%m%d%H%i%s') AND r.rc_title NOT IN (SELECT log_title FROM enwiki_p.logging
        WHERE log_type = "block" AND log_action = "block"
        AND log_timestamp > DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 2 DAY),'%Y%m%d%H%i%s'))) LIMIT 300""",
                },
'select sample test' : {#only select 20 of the possible invitees
    'string' : """SELECT u.user_id, u.user_name, u.user_registration, u.user_editcount, NOW(), 4
    FROM enwiki_p.user AS u WHERE (u.user_editcount >= 5 AND u.user_editcount < 100) AND u.user_id IN
(SELECT a.actor_user AS uid FROM enwiki_p.recentchanges AS r JOIN enwiki_p.actor AS a ON r.rc_actor = a.actor_id WHERE r.rc_log_type = "newusers"
AND r.rc_log_action != "autocreate"
AND r.rc_timestamp > DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 2 DAY),'%Y%m%d%H%i%s') AND r.rc_title NOT IN (SELECT log_title FROM enwiki_p.logging
        WHERE log_type = "block" AND log_action = "block"
        AND log_timestamp > DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 2 DAY),'%Y%m%d%H%i%s'))) LIMIT 20""",
                },
'insert th sample' : {'string' : """INSERT IGNORE INTO th_up_invitees_current(user_id, user_name, user_registration, user_editcount, sample_date, sample_type) VALUES({}, "{}", "{}", {}, "{}", {})"""
                },
'insert sample test' : {'string' : """INSERT IGNORE INTO th_invite_test(user_id, user_name, user_registration, user_editcount, sample_date, sample_type) VALUES({}, "{}", "{}", {}, "{}", {})"""
                },
'select th candidates' : {
    'string' : """SELECT user_name, user_id, user_talkpage
        FROM th_up_invitees_current
        WHERE date(sample_date) = date(NOW())
        AND sample_type = 4
        AND invite_status IS NULL
        AND (ut_is_redirect = 0 OR ut_is_redirect IS NULL)""",
                },
'select candidates test' : {
    'string' : """SELECT user_name, user_id, user_talkpage
        FROM th_invite_test
        WHERE date(sample_date) = date(NOW())
        AND sample_type = 4
        AND invite_status IS NULL
        AND (ut_is_redirect = 0 OR ut_is_redirect IS NULL)""",
                },
'find th talkpage' : {#not necessary to duplicate
    'string' : """SELECT p.page_id, p.page_is_redirect, p.page_title
 FROM enwiki_p.page AS p
 WHERE p.page_namespace = 3
 AND p.page_title IN ({})""",
                },
'find talkpage test' : {
    'string' : """SELECT p.page_id, p.page_is_redirect, p.page_title
 FROM enwiki_p.page AS p
 WHERE p.page_namespace = 3
 AND p.page_title IN ({})""",
                },
'add th talkpage' : {#should pull this from the API, because of replag
    'string' : """UPDATE th_up_invitees_current SET user_talkpage = {}, ut_is_redirect = {}
WHERE REPLACE(user_name," ","_") = "{}" AND user_talkpage IS NULL""",
                },
'add talkpage test' : {
    'string' : """UPDATE th_invite_test SET user_talkpage = {}, ut_is_redirect = {}
WHERE REPLACE(user_name," ","_") = "{}" AND user_talkpage IS NULL""",
                },
'update th invite status' : {
    'string' : """update th_up_invitees_current SET sample_group = "{}", invite_status = {},  hostbot_skipped = {} where user_id = {}""",
                },
'update invite status test' : { #when using the test db th_invite_test
    'string' : """update th_invite_test SET sample_group = "{}", invite_status = {},  hostbot_skipped = {} where user_id = {}""",
                },
}

    def getQuery(self, query_type, query_vars = False):
        if query_type in self.mysql_queries:
#           query = self.mysql_queries[query_type]['string'].encode("utf8")
            query = self.mysql_queries[query_type]['string']
            if query_vars:
#               query = query % tuple(query_vars) #should accept a list containing any number of vars
                query = query.format(**query_vars)

            else:
                pass
            return query
        else:
            print("something went wrong with query of type " + query_type)