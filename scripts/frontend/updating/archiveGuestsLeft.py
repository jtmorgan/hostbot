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

import urllib2
import wikitools
import settings
from BeautifulSoup import BeautifulStoneSoup as bss


# the archive page, in this case Teahouse/Guest_book
report_title = settings.rootpage + '/Guest_book'

# the page you want to archive
remove_title_left = settings.rootpage + '/Guests/Left_column' 


report_template = '''%s
'''

remove_template = '''= Recent guests =
{{TOC left}}
</div>
<br/>
</noinclude>
%s
'''

wiki = wikitools.Wiki(settings.apiurl)
wiki.login(settings.username, settings.password)

# get the number of new profiles on the Guest_left page

securl = u'http://en.wikipedia.org/w/api.php?action=parse&page=Wikipedia%3ATeahouse%2FGuests%2FLeft_column&prop=sections&format=xml'

usock = urllib2.urlopen(securl)
sections = usock.read()
usock.close()
soup = bss(sections, selfClosingTags = ['s'])
seccount = soup.findAll('s')

if len(seccount) < 11:
	pass
else:
	# if there are more than 10 intros, get the text of the intros being archived
	i = len(seccount) #just changed this to be the seccount number, and changed the while loop to count down
	j = i - 10
	output = []
	returns = []
	
	while i > 1:
		texturl1 = u'http://en.wikipedia.org/w/index.php?title=Wikipedia%%3ATeahouse%%2FGuests%%2FLeft_column&action=raw&section=%d' % i
		usock = urllib2.urlopen(texturl1)
		sections1 = usock.read()
		usock.close()
		sections1 = unicode(sections1, 'utf8')
		sections1 = sections1.strip()
		sec1_template = u'''%s
		
		''' % sections1
		if i > j:	#to keep 10 intros on the page, we add these back (rather than archiving them)
			returns.insert(0,sec1_template)	#to maintain the original ordering
		else:		#put the oldest intros in the archive list		
			output.append(sec1_template)
		i -= 1
	
	texturl2 = u'http://en.wikipedia.org/w/index.php?title=Wikipedia%3ATeahouse%2FGuest_book&action=raw&section=2'
	usock = urllib2.urlopen(texturl2)
	sections2 = usock.read()
	usock.close()
	sections2 = unicode(sections2, 'utf8')
	sections2 = sections2.strip()
	sec2_template = u'''%s
	
	''' % sections2
	output.append(sec2_template)
	
	#adding the archived profiles to Teahouse/Host_lounge/sandbox	
	report = wikitools.Page(wiki, report_title)
	report_text = report_template % '\n'.join(output)
	report_text = report_text.replace("<noinclude>", "")
	report_text = report_text.replace("</noinclude>", "")
	report_text = report_text.encode('utf-8')
	report.edit(report_text, section=2, summary="HostBot is automatically archiving recent intros from [[WP:Teahouse/Guests/Left_column]]", bot=1)
	
	#removing the intros that were archived	
	remove = wikitools.Page(wiki, remove_title_left)
	remove_text = remove_template % '\n'.join(returns)
	remove_text = remove_text.encode('utf-8')
	remove.edit(remove_text, section=1, summary="HostBot is automatically archiving recent intros to [[WP:Teahouse/Guest_book]]", bot=1)