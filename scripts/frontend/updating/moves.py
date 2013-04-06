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
		
class Params:
	"""assigns values to edit variables, based on what kind of move it is
	mv_to is whether this is a deactivate or a reactivate. 
	0 = deactivate (move to breakroom), 1 = reactivate (move to host_landing). 
	mv_add is whether this edit action is adding content to a page (True)
	OR effectively removing it (False) by only adding back 	what was NOT moved.
	"""
	
	def __init__(self):
			self.api_url = u'http://en.wikipedia.org/w/api.php?action=parse&page=Wikipedia%%3A%s&prop=sections&format=xml'
			self.index_url = u'http://en.wikipedia.org/w/index.php?title=Wikipedia%%3A%s&action=raw&section=%s'
			self.ns = u'Wikipedia:'
			self.frpg = ('Teahouse/Host_landing', 'Teahouse/Host_breakroom')
			self.topg = ('Teahouse/Host_breakroom', 'Teahouse/Host_landing')
			self.frpg_tem = ('=Hosts=\n{{TOC hidden}}\n\n<br/>\n</noinclude>\n%s', '= Hosts on Sabbatical =\n{{TOC left}}\n</div>\n<br/>\n%s')
			self.topg_tem = '%s\n'
			self.frpg_cmt = (u'HostBot is automatically moving profiles for currently inactive hosts to [[WP:Teahouse/Host_breakroom]]', u'HostBot is automatically moving profiles of recently active hosts to [[WP:Teahouse/Host_landing]]')
			self.topg_cmt = (u'HostBot is automatically moving profiles for currently inactive hosts from [[WP:Teahouse/Host_landing]]', u'HostBot is automatically moving profiles of recently active hosts from [[WP:Teahouse/Host_breakroom]]')
			self.mv_queries = ('SELECT user_name FROM th_up_hosts WHERE num_edits_2wk = 0 AND in_breakroom = 0 AND has_profile = 1 AND join_date IS NOT NULL','SELECT user_name FROM th_up_hosts WHERE num_edits_2wk > 0 AND in_breakroom = 1 AND has_profile = 1 AND join_date IS NOT NULL')
			self.nomv_log = ('No moves to breakroom today','No moves to host landing today')
			self.mv_log = ('Moved profiles for %s to host breakroom at ','Moved profiles for %s to host landing at ')
			self.db_up = (1, 0)	










