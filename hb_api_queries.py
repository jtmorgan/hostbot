#! /usr/bin/env python2.7

# Copyright 2015 Jtmorgan

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

import requests

class Query:

	def __init__(self):
        self.api_url = "http://en.wikipedia.org/w/api.php/"
        
        
    def getLatestEditDate(user_name):
        """
        Get the date of the user's most recent edit
        See: https://www.mediawiki.org/wiki/API:Usercontribs  
        """
        
        parameters = {
            "action" : "query",
            "list" : "usercontribs",
            "ucuser" : user_name,
            "uclimit" : 1,
            "ucdir" : "older",
            "ucshow": "top",
            "ucprop": "timestamp",
            "format": "json",
            }


        api_req = requests.get(self.api_url, params=parameters)
        # print api_req.url

        api_data = api_req.json()
        # print api_data
        edit_timestamp = api_data["query"]["usercontribs"][0]["timestamp"]
        # print edit_timestamp
        return edit_timestamp
        return api_data
 
     def getBlockStatus(user_name):
        """
        Find out whether the user is currently blocked from editing
        See: https://www.mediawiki.org/wiki/API:Usercontribs 
        https://en.wikipedia.org/w/api.php?action=query&list=users&ususers=Lightbreather&usprop=blockinfo 
        """
        parameters = {
            "action" : "query",
            "list" : "users",
            "ususers" : user_name,
            "usprop" : "blockinfo",
            "format": "json",
            }  
        blocked = False
        api_req = requests.get(self.api_url, params=parameters)
        # print api_req.url

        api_data = api_req.json()
        # print api_data
        if api_data["query"]["users"][0]["blockinfo"]:
            blocked = True
        else:
            pass    
        # print blocked
        return blocked
                  
 #https://github.com/jtmorgan/grantsbot/blob/ec5497770b5fa284058aab9715af6be3c7c193c6/profiles.py#L267
 #https://github.com/makoshark/harrypotter-wikipedia-cdsw/blob/master/build_hpwp_dataset.py
 #https://en.wikipedia.org/w/api.php/?ucprop=timestamp&ucuser=Jtmorgan&list=usercontribs&action=query&ucshow=top&uclimit=1&ucdir=older
 #https://www.mediawiki.org/wiki/API:Users
 
#     ts = getLatestEditDate("Jtmorgan")
    blocked = getBlockStatus("Lightbreather")
    print blocked




