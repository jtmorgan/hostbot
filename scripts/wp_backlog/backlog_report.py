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

import pages
import csv
import datetime
import sys
import shelve

##FUNCTIONS##
def get_category_pages(cat_title, cat_ns, catquery):
	"""
	Retrieve all the articles in a category and its first-level subcategories.
	"""
	print cat_title
	page_lst = [] #build out a list of pages
	cat_lst = [cat_title] #build out a list of subcategories
	mempages = catquery.getPages('page', cat_title, cat_ns)
	for item in mempages:
		page_lst.append((cat_title, item['title'].encode("utf8")))
	memcats = catquery.getPages('subcat', cat_title, cat_ns)
	for item in memcats:
		cat_lst.append(item['title'].encode("utf8"))
		mems = catquery.getPages('page', item['title'].encode("utf8"), cat_ns)
		for pg in mems:
			seen = False
			for spg in page_lst:
				if pg == spg[1]:
					seen = True
					print pg
			if not seen:
				page_lst.append((item['title'], pg['title'].encode("utf8")))
# 	print cat_lst
# 	print page_lst
# 	page_lst = list(set(page_lst))
	return page_lst

def update_shelf(page_lst):
	db = shelve.open('/home/jmorgan/hostbot/data/wp_backlog/db/th_cats.db')
	for key in db:
		for page in page_lst:
			if key not in page[1]:
				print key
# 	for page in page_lst:
# 		if page[1] not in db:
# 			print page
# 		db[page[1]] = [page[0], str(datetime.date.today())]
	print len(db)
	db.close()

def write_to_file(cat_title, page_lst):
	"""
	Write the category and page list to a csv file. May contain duplicates if a page is
	multiply categorized.
	"""

	csv_file = "/home/jmorgan/hostbot/data/wp_backlog/csv/" + cat_title + str(datetime.date.today()) + '.csv'
	print csv_file
	f = open(csv_file, 'wt')
	writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
	writer.writerow( ('category','page') )
	i = 1

	for page in page_lst:
		writer.writerow( (i, page[0], page[1].encode('utf-8')) )
		i += 1

##MAIN##
catquery = pages.CategoryCheck()
page_lst = get_category_pages("Category:" + sys.argv[1].encode("utf8"), sys.argv[2], catquery)
# write_to_file(sys.argv[1], page_lst)
update_shelf(page_lst)



