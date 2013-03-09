#! /usr/bin/env python

# Copyright 2012 Jtmorgan
 
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

import BeautifulSoup as bs
from BeautifulSoup import BeautifulStoneSoup
import urllib2
import wikitools
import re
import MySQLdb
import settings


report_title = settings.rootpage + '/Questions-recent/%i'
 
report_template = '''%s

<!-- Fill in the "section" parameter with the question title from the Q&A page -->
{{Wikipedia:Teahouse/Questions-answer|section=%s}}
'''
wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)
conn = MySQLdb.connect(host = 'db67.pmtpa.wmnet', db = 'jmorgan', read_default_file = '~/.my.cnf' )
cursor = conn.cursor()

cursor.execute('''
select rev_id from enwiki.revision 
	where rev_page = 34745517 
	and rev_comment like "New question:%" and rev_timestamp > DATE_FORMAT(DATE_SUB(NOW(),INTERVAL 2 DAY),'%Y%m%d%H%i%s') order by rand() limit 5;
	''')

page = 1
	
row = cursor.fetchone()
while 1:
	if not row:
		break
	rev_id = row[0]
	url = u'http://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles=Wikipedia%%3ATeahouse%%2FQuestions&rvprop=content&rvstartid=%d&rvendid=%d&rvlimit=1&rvsection=1&format=xml' % (rev_id, rev_id) # write the url here
	usock = urllib2.urlopen(url)
	data = usock.read()
	usock.close()
	data = unicode(data, 'utf8')
	soup = bs.BeautifulSoup(data)
	q = soup.find('rev')
	qraw = q.renderContents()
	qtitle = re.match("\=\=(.*?)\=\=", qraw)
	qlink = qtitle.group(1)
	qclean = re.sub("\=\=(.*?)\=\=", "", qraw)
	qstone = BeautifulStoneSoup(qclean, convertEntities=BeautifulStoneSoup.XML_ENTITIES)
	report = wikitools.Page(wiki, report_title % page)
	report_text = report_template % (qstone, qlink)
#	report_text = report_text.encode('utf-8')
	report.edit(report_text, section=0, summary="Automatic recent question update by [[User:HostBot|HostBot]]", bot=1)
	page+=1
	if page > 5:
		break
	row = cursor.fetchone()                

cursor.close()
conn.close()