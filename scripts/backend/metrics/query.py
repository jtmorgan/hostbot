#! /usr/bin/env python2.7

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

class Queries:

	def __init__(self):
		"""database queries"""
		self.queries = { 'welcome' :
							{ 'experimental' : 'SELECT user_id, DATE_FORMAT(DATE(ba_date), "%m-%d-%Y") as sample_date FROM th_up_badges_awarded WHERE user_id != 0 AND b_id = 1 AND bap_ns = 3 AND ba_date > "2013-01-31" AND not_badge = 0 AND user_id IN (SELECT rev_user FROM th_up_profiles WHERE DATE(post_date) > "2013-01-31")',
							 'control' : 'SELECT DISTINCT rev_user, DATE_FORMAT(DATE(post_date), "%m-%d-%Y") as sample_date FROM th_up_profiles AS p, (SELECT user_id, ba_date FROM th_up_badges_awarded WHERE user_id != 0 AND b_id = 1 AND bap_ns = 3 AND ba_date >= "2013-01-24" AND not_badge = 0 AND user_id IN (SELECT rev_user FROM th_up_profiles WHERE DATE(post_date) >= "2013-01-24")) AS tmp WHERE p.rev_user != tmp.user_id AND p.rev_user != 0 AND DATE(p.post_date) >= "2013-01-24" ORDER BY RAND() LIMIT 228',
							'activity' : 'SELECT count(rev_id) AS cum_revs FROM enwiki.revision WHERE rev_user = %s AND DATE(DATE_FORMAT(rev_timestamp,"%s")) > "2013-01-24" AND rev_page NOT IN (SELECT page_id FROM th_pages)'
							},
						'qna' : 
							{ 'experimental' : 'SELECT distinct user_id, ba_date FROM th_up_badges_awarded WHERE user_id != 0 AND b_id IN (2,3) AND bap_ns = 3 AND ba_date >= "2013-01-24" AND not_badge = 0 AND user_id IN (SELECT rev_user FROM th_up_answers WHERE DATE(q_date) >= "2013-01-24" AND rev_user != 0 UNION ALL SELECT rev_user FROM th_up_questions WHERE DATE(post_date) >= "2013-01-24" AND rev_user != 0)',
							'control': '(SELECT DISTINCT a.rev_user, DATE(a.q_date) AS pdate FROM th_up_answers AS a, (SELECT rev_user FROM th_up_answers WHERE DATE(q_date) >= "2013-01-24" AND rev_user != 0) AS tmp1 WHERE a.rev_user != tmp1.rev_user AND a.rev_user != 0 AND DATE(a.q_date) >= "2013-01-24" ORDER BY RAND() LIMIT 27) UNION ALL (SELECT DISTINCT q.rev_user, DATE(q.post_date) AS pdate FROM th_up_questions AS q, (SELECT rev_user FROM th_up_questions WHERE DATE(post_date) >= "2013-01-24" AND rev_user != 0) AS tmp2 WHERE q.rev_user != tmp2.rev_user AND q.rev_user != 0 AND DATE(q.post_date) >= "2013-01-24" ORDER BY RAND() LIMIT 62)',
							'activity' : 'SELECT count(rev_id) AS cum_revs FROM enwiki.revision WHERE rev_user = %s AND DATE(DATE_FORMAT(rev_timestamp,"%s")) > "2013-01-24" AND rev_page = 34745517' 
							}	
						}
							
	def badgeQueries(self, group_name):
		if group_name in self.queries:
			return self.queries[group_name]

