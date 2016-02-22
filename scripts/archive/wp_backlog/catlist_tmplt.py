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

lst_template = '''
== Article categories ==
</noinclude>
{| cellpadding="5"
|%s
|}'''


cat_template = "<noinclude>[[Category:Wikipedia_Teahouse]]''This page is updated weekly by [[User:HostBot|HostBot]]. Please contact [[User:Jtmorgan|Jtmorgan]] if you want to change anything.''</noinclude> <includeonly>{{{{{|safesubst:}}}#switch:{{{1|}}}|%s|#default = no_match}}</includeonly>"