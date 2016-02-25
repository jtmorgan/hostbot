#! /usr/bin/env python

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

from datetime import datetime, timedelta
import dateutil.parser
import hb_output_settings
import requests
import sys
import requests.packages.urllib3
requests.packages.urllib3.disable_warnings()


class Eligible:

    def __init__(self):
        self.api_url = "https://en.wikipedia.org/w/api.php/"
        self.settings = hb_output_settings.Params()
        self.output_params = self.settings.getParams("th_invites")
             
    def getLatestEditDate(self, user_name):
        """
        Get the date of the user's most recent edit
        See: https://www.mediawiki.org/wiki/API:Usercontribs
        Example: https://en.wikipedia.org/w/api.php/?ucprop=timestamp&ucuser=Jtmorgan&list=usercontribs&action=query&ucshow=top&uclimit=1&ucdir=older  
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
        edit_timestamp = api_data["query"]["usercontribs"][0]["timestamp"]
        latest_edit_date = dateutil.parser.parse(edit_timestamp, ignoretz=True).date()
        return latest_edit_date

    def getBlockStatus(self, user_name):
        """
        Find out whether the user is currently blocked from editing
        See: https://www.mediawiki.org/wiki/API:Users
        Example: https://en.wikipedia.org/w/api.php?action=query&list=users&ususers=Willy_on_Wheels~enwiki&usprop=blockinfo 
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
        if "blockid" in api_data["query"]["users"][0].keys():
            blocked = True
        else:
            pass    
        # print blocked
        return blocked
    
    def meetsEditDateThreshold(self, latest_edit_date, threshold):
        meets_threshold = False
        cur_date = datetime.utcnow().date()
        threshold_date = cur_date - timedelta(days=threshold)
        if latest_edit_date >= threshold_date:
            meets_threshold = True
        else:
            pass
        return meets_threshold        
                            
    def determineInviterEligibility(self, inviter, threshold):
        """
        Takes a username and a date.
        """
        is_eligible = False
        is_blocked = self.getBlockStatus(inviter)
        latest_edit_date = self.getLatestEditDate(inviter)
        is_active = self.meetsEditDateThreshold(latest_edit_date, threshold)
        if is_active and not is_blocked:
            is_eligible = True
        else:
            pass
        return is_eligible        

    def determineInviteeEligibility(self, invitee):
        """
        Takes a tuple of user_name, user_id, userpage_id.
        """
        is_eligible = False
        has_skip_template = False        
        is_blocked = self.getBlockStatus(invitee[1])
        if invitee[2] is not None:
            has_skip_template = self.checkTalkPage(self.output_params["output namespace"] + invitee[0], invitee[2], self.output_params["skip templates"])
#             print invitee[0] + str(has_skip_template)
        if not has_skip_template and not is_blocked:
            is_eligible = True
        else:
            pass
        return is_eligible

    def checkTalkPage(self, page_path, page_id, skip_templates): 
        """
        Takes a dictionary of key words.
        If those words appear in the user talkpage,
        skip the user (don't send an invite).
        """
        skip = False
        tp_text = self.getPageText(page_path, page_id)
        for t in skip_templates:
            if t in tp_text:
                skip = True
        return skip
                     
    def getPageText(self, page_path, page_id, section=False): #create a generic class?
        """
        Gets the raw text of a page or page section.
        Sample: http://meta.wikimedia.org/w/api.php?action=query&prop=revisions&titles=Grants:IdeaLab/Introductions&rvprop=content&rvsection=21&format=jsonfm
        """
        api_params={
            'action': 'query',
            'prop': 'revisions',
            'titles': page_path,
            'rvprop' : 'content',
            'format': "json"            
        }        
        if section:
            api_params['rvsection'] = section
        else:
            pass
        try:
            response = requests.get(self.api_url, params=api_params)                   
            doc = response.json()
            text = doc['query']['pages'][str(page_id)]['revisions'][0]['*'] #note page_id as str
        except:#if there's an error, text is an empty string. Keeps the system working.
            text = ""
        return text        
         
if __name__ == "__main__":
    """
    Run this script directly if you want to test it.
    Pass in the date threshold fron the command line.
    """
    param = hb_output_settings.Params()
    params = param.getParams(sys.argv[1]) #what type of invites
    sub_date = int(sys.argv[2]) #numeric threshold (days ago)
    e = Eligible()
    potential_inviters = params['inviters'] 
    eligible_inviters = [x for x in potential_inviters if e.determineInviterEligibility(x, sub_date)]
    print potential_inviters
    print eligible_inviters        
    




