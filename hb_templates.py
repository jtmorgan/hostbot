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

class Template:
	"""templates of profiles for wiki pages"""
	def __init__(self):
		self.profile_templates = {
		'featured_hosts' : u"""
{{{{Wikipedia:Teahouse/Host_featured
| username = {username}
| image = {image}
}}}}""",
		'featured_guests_left' : u"""
{{{{Wikipedia:Teahouse/Guest
| username = {username}
| image = {image}
| quote = {quote}
}}}}""",
		'featured_guests_right' : u"""
{{{{Wikipedia:Teahouse/Guest
| username = {username}
| image = {image}
| quote = {quote}
}}}}""",
	'intro' : u"""=Hosts=\n{{{{TOC hidden}}}}\n<br/>\n</noinclude>
{profiles}""",
	'th invite templates' : u"{{{{subst:Wikipedia:Teahouse/HostBot_Invitation|message={message:s}|personal=I hope to see you there! {{{{noping|{inviter:s}}}}} ([[w:en:WP:Teahouse/Hosts|I\'m a Teahouse host]])|signature=~~~~}}}}",
	'coop invite templates' : u"{{{{subst:Co-op_invite|personal={{{{noping|{inviter:s}}}}} ([[Wikipedia:Co-op/{inviter:s}|I\'m a Co-op mentor]])|signature=~~~~}}}}",
	'twa invite templates' : u"""{{{{subst:Wikipedia:TWA/Invite|personal=I hope to see you there! {{{{noping|{inviter:s}}}}}|signature=~~~~}}}}""",
	
}
	def getTemplate(self, member):
		tmplt = self.profile_templates[member]
		return tmplt

