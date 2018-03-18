#! /usr/bin/env python

from datetime import datetime
import hb_config
# import MySQLdb
import pymysql.cursors
import pymysql.converters as conv
# import pymysql.constants as const
from pymysql.constants import FIELD_TYPE
import hb_output_settings as output_settings
import hb_queries
import hb_templates as templates
import requests
from requests_oauthlib import OAuth1

#TODO: add in logging again, more try statements
#hb_config to config
#get DB class out of profiles.py, rename

def connect_to_db(hostname, dbname, defaultfile):

    conn = pymysql.connect(
            host = hostname,
            db = dbname,
            read_default_file = defaultfile,
            use_unicode = 1,
            charset="utf8",
                )

    return conn

def select_query(conn, qstring, convert_bytestrings = False):
    cursor = conn.cursor()
    cursor.execute(qstring)
    if convert_bytestrings:
        result = convert_bytes_in_results_tuple(cursor.fetchall())
    else:
        result = list(cursor.fetchall())
    return result

def commit_query(conn, qstring):
    cursor = conn.cursor()
    cursor.execute(qstring)
    conn.commit()

def insert_multiple_rows_query(conn, qstring, list_of_rows):
    cursor = conn.cursor()
    for row in rows:
        x = tuple(row)
#         qstring.format(*x)
        cursor.execute(qstring.format(*x))

#     cursor.executemany(qstring, list_of_tuples)
    conn.commit()

def convert_bytes_in_results_tuple(results_tuple):
    """
    Convert the varbinaries to unicode strings, and return a list of lists.
    """
    return [[x.decode() if type(x) == bytes else x for x in row] for row in results_tuple]

if __name__ == "__main__":
    conn1 = connect_to_db('tools.db.svc.eqiad.wmflabs', 's51322__hostbot','/home/jmorgan/replica.my.cnf')

## VALIDATED - SELECT FROM THE TEAHOUSE INVITE DATABASE
#     query1 = "select * from th_up_invitees_current where sample_date = '2017-09-14 20:00:40' and sample_group = 'invalid' and user_editcount > 48;"
#     rows = select_query(conn1, query1, convert_bytestrings = True)
#     print(rows)

## VALIDATED - COMMIT TO THE TEAHOUSE INVITE DATABASE FROM ANOTHER DATABASE ON THE SAME HOST
#     query2 = "insert ignore into th_invite_test select * from th_up_invitees_current where sample_date = '2017-09-14 20:00:40' and sample_group = 'invalid' and user_editcount > 48;"
#     commit_query(conn1, query2)

## VALIDATED - CONNECT TO A DIFFERENT HOST
#     conn2 = connect_to_db('enwiki.labsdb', 'enwiki_p','/home/jmorgan/replica.my.cnf')
#     query3 = """SELECT user_id, user_name, user_registration, user_editcount, NOW(), 4
#     FROM enwiki_p.user
#     WHERE user_registration > DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 2 DAY),'%Y%m%d%H%i%s')
#     AND user_editcount >=5 limit 2"""
#
#     rows = select_query(conn2, query3)
#     print(rows)

## VALIDATED - SELECT FROM ENWIKI AND COMMIT TO HOSTBOT INVITE TABLE
    conn2 = connect_to_db('enwiki.labsdb', 'enwiki_p','/home/jmorgan/replica.my.cnf')
    query3 = """SELECT user_id, user_name, user_registration, user_editcount, NOW(), 4
    FROM enwiki_p.user
    WHERE user_registration > DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 2 DAY),'%Y%m%d%H%i%s')
    AND user_editcount >=5 limit 2"""

    rows = select_query(conn2, query3, convert_bytestrings = True)
    for row in rows:
        row[4] = '{:%Y-%m-%d %H:%M:%S}'.format(row[4])

    print(rows)

    query4 = "INSERT ignore INTO th_invite_test(user_id, user_name, user_registration, user_editcount, sample_date, sample_type) VALUES({}, '{}', '{}', {}, '{}', {})"

    insert_multiple_rows_query(conn1, query4, rows)





#     def insertInvitees(self, query_key):
#         """
#         Insert today's potential invitees into the database
#         """
#         query = self.queries.getQuery(query_key)
#         self.cursor.execute(query)
#         self.conn.commit()
#
#     def updateTalkPages(self, query_key):
#         """
#         Updates the database with user talkpage ids (if they have one)
#         """
#         query = self.queries.getQuery(query_key)
#         self.cursor.execute(query)
#         self.conn.commit()
#
#     def selectSample(self, query_key, sub_sample=False):
#         """
#         Returns a list of usernames and ids of candidates for invitation
#         """
#         sample_query = self.queries.getQuery(query_key)
#         self.cursor.execute(sample_query)
#         rows = self.cursor.fetchall()
#         sample_set = [[row[0],row[1], row[2]] for row in rows]
#         if sub_sample:
#             sample_set = sample_set[:5]
#         return sample_set
#
#     def updateOneRow(self, query_key, qvars):
#         """
#         Updates the database: was the user invited, or skipped?
#         """
# #         try:
#         query = self.queries.getQuery(query_key, qvars)
#         self.cursor.execute(query)
#         self.conn.commit()
# #         except:
# #             print "something went wrong with this one"