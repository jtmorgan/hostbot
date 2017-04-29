#! /usr/bin/env python

class Template:
	"""invite templates"""
	def __init__(self):
		self.profile_templates = {
	'th invite templates' : u"{{{{subst:Wikipedia:Teahouse/HostBot_Invitation|personal=The Teahouse is a friendly space where new editors can ask questions about contributing to Wikipedia and get help from experienced editors like {{{{noping|{inviter:s}}}}} ([[User_talk:{inviter:s}|talk]]). |bot={{{{noping|HostBot}}}}|timestamp=~~~~~}}}}",
	'test invite templates' : u"{{{{subst:User:HostBot/Invitation|personal=The Teahouse is a friendly space where new editors can ask questions about contributing to Wikipedia and get help from experienced editors like {{{{noping|{inviter:s}}}}} ([[User_talk:{inviter:s}|talk]]). |bot={{{{noping|HostBot}}}}|timestamp=~~~~~}}}}", #only use when hostbot_settings urls set to testwiki
    'tm invite template' : "{{{{subst:User:HostBot/Training_modules_invitation|signed=~~~~}}}}", #update when testing is over
}
	def getTemplate(self, member):
		tmplt = self.profile_templates[member]
		return tmplt

