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
import pages

wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)
conn = MySQLdb.connect(host = 'db67.pmtpa.wmnet', db = 'jmorgan', read_default_file = '~/.my.cnf', use_unicode=1, charset="utf8" )
cursor = conn.cursor()



##FUNCTIONS##

#gets projects that are candidates
def getProjects(cursor):
	"""
	retrieves the list of WikiProjects we want to find subcategories for
	"""
	wp_list = []
	cursor.execute('''select cat_title, proj_page from th_wikiproject_categories WHERE cat_subcats > 0 AND cat_pageid IS NOT NULL AND cat_parent IS NULL AND proj_featured = 1''')
	rows = cursor.fetchall()
	for row in rows:
		cat = row[0]
		proj = row[1]
		wp_list.append((cat, proj))

	return wp_list


def get_category_pages(cat_title, catquery):
	"""
	Retrieve all the articles in a category and its first-level subcategories.
	"""
	memcat_lst = [] #build out a list of pages in a given category
	memcats = catquery.getPages('subcat', "Category:"+ cat_title[0])
	for memcat in memcats:
# 		memcat = memcat[9:]
		memcat_lst.append((cat_title[0], cat_title[1], memcat['pageid'], memcat['title'][9:].encode("utf8")))
		subcats = catquery.getPages('subcat', memcat['title'].encode("utf8"))
		if len(subcats) > 0:
			for subcat in subcats:
				memcat_lst.append((cat_title[0], cat_title[1], subcat['pageid'], subcat['title'][9:].encode("utf8")))

# 		page_cnt = len(mempages)
	return memcat_lst

def update_table(new_cats, cursor):
	for item in new_cats:
		for cat in item:
			cursor.execute('''INSERT INTO th_wikiproject_categories (cat_parent, proj_page, cat_pageid, cat_title) VALUES ("%s", %d, %d, "%s") ON DUPLICATE KEY UPDATE cat_parent=VALUES(cat_parent), proj_page=VALUES(proj_page)''' % (cat[0], cat[1], cat[2], cat[3]))
			conn.commit()




##MAIN##
catquery = pages.CategoryCheck()
wp_list = getProjects(cursor)
new_cats = []
for wp in wp_list:
	memcat_lst = get_category_pages(wp, catquery)
	print memcat_lst
	new_cats.append(memcat_lst)
update_table(new_cats, cursor)
cursor.close()
conn.close()
