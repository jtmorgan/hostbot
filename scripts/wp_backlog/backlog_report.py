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
from datetime import date
import sys

##FUNCTIONS##
def get_category_pages(cat_title, catquery):
	"""
	Retrieve all the articles in a category and its first-level subcategories.
	"""
	print cat_title
	page_lst = [] #build out a list of pages
	cat_lst = [cat_title] #build out a list of subcategories
	mempages = catquery.getPages('page', cat_title)
	for item in mempages:
		page_lst.append((cat_title, item['title']))
	memcats = catquery.getPages('subcat', cat_title)
	for item in memcats:
		cat_lst.append(item['title'])
		mems = catquery.getPages('page', item['title'])
		for pg in mems:
			page_lst.append((item['title'], pg['title']))
# 	print cat_lst
# 	print page_lst
	return page_lst

def write_to_file(cat_title, page_lst):
	"""
	Write the category and page list to a csv file. May contain duplicates if a page is
	multiply categorized.
	"""
	
	file_name = "/home/jmorgan/hostbot/data/wp_backlog/" + cat_title + str(date.today()) + '.csv'
	print file_name
	f = open(file_name, 'wt')
	writer = csv.writer(f, quoting=csv.QUOTE_NONNUMERIC)
	writer.writerow( ('category','page') )	
	i = 1
	
	for page in page_lst:
		writer.writerow( (i, page[0], page[1].encode('utf-8')) )
		i += 1

##MAIN##
catquery = pages.CategoryCheck()
page_lst = get_category_pages("Category:" + sys.argv[1])
write_to_file(sys.argv[1], page_lst)




