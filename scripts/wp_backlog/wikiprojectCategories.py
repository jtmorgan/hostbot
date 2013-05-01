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

import MySQLdb
import wikitools
import settings
import catlist_tmplt

wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)
conn = MySQLdb.connect(host = 'db67.pmtpa.wmnet', db = 'jmorgan', read_default_file = '~/.my.cnf', use_unicode=1, charset="utf8" )
cursor = conn.cursor()


##GLOBAL VARIABLES##
wp_list_page = 'Wikipedia:Teahouse/Suggestions/Lists'
wp_cat_page = 'Wikipedia:Teahouse/Suggestions/Category_check'

##FUNCTIONS##

#gets projects that are candidates
def getProjects(cursor):
	wp_list = []
	cursor.execute('''select wikiproject, page_id from th_up_wikiprojects where non_bot_edits > 30 order by rand() limit 20''')
	rows = cursor.fetchall()
	for row in rows:
		proj = row[0]
		id = row[1]
		wp_list.append((proj, id))

	return wp_list

def matchProjCats(projects, cursor):
	output_lst = []
	for proj in projects:
		cursor.execute('''SELECT cat_title FROM th_wikiproject_categories WHERE proj_page = %d AND cat_pages > 50 AND cat_parent IS NOT NULL AND (cat_title LIKE "%%need%%" OR cat_title LIKE "%%importan%%" OR cat_title LIKE "%%Class%%") ORDER BY RAND() LIMIT 1''' % (proj[1],))
		row = cursor.fetchone()
		if row:
			pair = (proj[0].encode('utf8'), "Category:" + row[0].encode('utf8'))
			output_lst.append(pair)
	return output_lst

def pubLists(proj_cats, int):
	#sets output variables per list
	if int == 0:
		formatted_output = '|'.join([item[0] + '=' + item[1] for item in proj_cats])
		print formatted_output
		report_text = catlist_tmplt.cat_template % formatted_output
		print report_text
		title = wp_cat_page
		print title
	elif int == 1:
		formatted_output = '\n|'.join(['{0}\n|-'.format(item[0]) for item in proj_cats])
		report_text = catlist_tmplt.lst_template % formatted_output
		print report_text
		title = wp_list_page
		print title
	summ = "*TEST* updating list of [[WP:Teahouse/Suggestions|suggested WikiProjects]]"
	section=int
	print summ
	print section
	report = wikitools.Page(wiki, title)
	report.edit(report_text, section=int, summary=summ, bot=1)

##MAIN###
projects = getProjects(cursor)
# for proj in projects:
# 	updateEditCounts(proj, cursor)
proj_cats = matchProjCats(projects, cursor)



# proj_cats = generateList(cursor)
pubLists(proj_cats, 0) #publishes the project list to wiki
pubLists(proj_cats, 1) #publishes the cat lookup list to wiki


#updates the recent edit counts for the project
# def updateEditCounts(proj, cursor):
# 	cursor.execute('''UPDATE th_up_wikiprojects as wp, (select count(rc_id) as edits from enwiki.recentchanges where rc_title like "%s%%" and rc_user NOT IN (SELECT ug_user FROM enwiki.user_groups WHERE ug_group = 'bot')) AS tmp SET wp.non_bot_edits = tmp.edits, wp.updated = 1 WHERE wp.wikiproject = "%s"''' % (proj, proj))

# def generateList(cursor):
# 	pcat = []
# 	cursor.execute('''SELECT DISTINCT wikiproject, cat_title FROM th_wikiproject_categories as c, th_up_wikiprojects AS w WHERE c.proj_page = w.page_id AND c.cat_title LIKE "%_articles" AND c.cat_pages > 100 AND w.non_bot_edits > 30 GROUP BY page_id ORDER BY RAND() LIMIT 20''')
# 	rows = cursor.fetchall()
# 	for row in rows:
# 		p = row[0]
# 		cat = row[1]
# 		pcat.append( (p,cat) )
# 	print pcat
# 	return pcat
# def pubLists(list, int):
# 	output = []
# 	#sets output variables per list
# 	if int == 0:
# 		template = wp_cat_template
# 		title = wp_cat_page
# 		head = "<noinclude>[[Category:Wikipedia_Teahouse]]''This page is updated weekly by [[User:HostBot|HostBot]]. Please contact [[User:Jtmorgan|Jtmorgan]] if you want to change anything.''</noinclude>"
# 		table_row = u'''|%s=Category:%s'''
# 		summ = "*TEST* updating article category lookup list for [[WP:Teahouse/Suggestions/Lists|suggested WikiProjects]]"
# 		output.append("<includeonly>{{{{{|safesubst:}}}#switch:{{{1|}}}")
# 		for l in list:
# 			line = table_row % (l[0], l[1])
# 			output.append(line)
# 		output.append("|#default = no_match}}</includeonly>")
# 	elif int == 1:
# 		template = wp_list_template
# 		title = wp_list_page
# 		head = "</noinclude>"
# # 		output.append(head)
# 		table_row = u'''\n|%s
# |-'''
# 		summ = "*TEST* updating list of [[WP:Teahouse/Suggestions|suggested WikiProjects]]"
# 		for l in list:
# 			line = table_row % (l[0])
# 			output.append(line)
# 	report = wikitools.Page(wiki, title)
# 	report_text = template % (head, ''.join(output))
# 	report_text = report_text.encode('utf-8')
# 	print report_text
# 	print title


# cursor.execute('''
# INSERT INTO th_wp_categories_test
# SELECT SUBSTRING_INDEX(page_title, '/', 1) AS project,
#          SUM((
#          SELECT COUNT(*)
#          FROM enwiki.revision
#          WHERE page_id = rev_page
#          AND DATEDIFF(NOW(), rev_timestamp) <= 1
#          AND rev_user NOT IN
#           (SELECT ug_user
#           FROM enwiki.user_groups
#           WHERE ug_group = 'bot')
#        )) AS no_bots_count,
#        (SELECT page_is_redirect
#        FROM enwiki.page
#        WHERE page_namespace = 4
#        AND page_title = project) AS redirect
# FROM enwiki.page
# WHERE page_title LIKE 'WikiProject\_%'
# AND page_namespace BETWEEN 4 AND 5
# AND page_is_redirect = 0
# GROUP BY project
# ORDER BY no_bots_count DESC;
# ''')
#
# i = 1
# output = []
# for row in cursor.fetchall():
#     page_title = '[[Wikipedia:%s]]' % unicode(row[0], 'utf-8').replace('_', ' ')
#     no_bot_edits = row[1]
#     is_redirect = row[2]
#     if is_redirect:
#         page_title = "''" + page_title + "''"
#     table_row = u'''| %d
# | %s
# | %d
# | %d
# |-''' % (i, page_title, no_bots_edits)
#     output.append(table_row)
#     i += 1




cursor.close()
conn.close()
