#! /usr/bin/python2.7

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

import hostbot_settings
import hb_output_settings as output_settings
import hb_profiles as profiles
import sys
import hb_templates as templates

###FUNCTIONS
def makeGallery():
	"""
	Makes featured profiles for Teahouse galleries.
	"""
	if params['subtype'] in ['host_intro',]:
		featured_list = getFeaturedProfiles()
	else:
		sys.exit("unrecognized featured content type " + params['subtype'])        
	prepOutput(featured_list)                                

def getFeaturedProfiles():
	"""
	Gets info about the top-billed profiles in a guide.
	"""
	featured_list = []
	profile_page = profiles.Profiles(params[params['subtype']]['input page path'],id = params[params['subtype']]['input page id'], settings = params)
	profile_list = profile_page.getPageSectionData(level = params[params['subtype']]['profile toclevel'])
	num_featured = params[params['subtype']]['number featured'] #redundancy with below
	profile_list = profile_list[:num_featured]
	for profile in profile_list:
# 		print profile
		text = profile_page.getPageText(profile['index'])
		profile = profile_page.scrapeInfobox(profile, text)
		if params['subtype'] == 'host_intro':
			if (profile['image'] and profile['title']):
				profile['username'] = profile['title']
				featured_list.append(profile)
			else:
				pass        
		else:
			pass
	return featured_list                
        
def prepOutput(featured_list):
	i = 1
	number_featured = params[params['subtype']]['number featured']
	featured_list = tools.addDefaults(featured_list)                       
	output = profiles.Profiles(params[params['subtype']]['output path'], settings = params) #stupid tocreate a new profile object here. and stupid to re-specify the path below
	for f in featured_list:
			if i <= number_featured:
					f['profile'] = output.formatProfile(f)
					f['profile'] = f['profile'] + '\n' + params['header template']
					edit_summ = params['edit summary'] % (params['subtype'] + " " + params['type'])
					output.publishProfile(f['profile'], params[params['subtype']]['output path'], edit_summ, sb_page = i)
					i += 1
			else:
					break        

###MAIN
param = output_settings.Params()
params = param.getParams(sys.argv[1])
params['type'] = sys.argv[1]
params['subtype'] = sys.argv[2]
tools = profiles.Toolkit()
makeGallery()    
