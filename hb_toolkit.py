#! /usr/bin/env python

from datetime import datetime, timedelta
import dateutil.parser
import hb_config
import hb_output_settings
import requests
import sys
#cmt out 9/15/2017 - not sure if this is needed
# import requests.packages.urllib3
# requests.packages.urllib3.disable_warnings()


class Eligible:

    def __init__(self, params):
        self.api_url = hb_config.api_url_get #different from OAuth api url, for testwiki
        self.output_params = params

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
        # print(api_req.url)

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
#             print(invitee[0] + " " + str(has_skip_template))
        if is_blocked:
            print(invitee[1])
            print(invitee[0])
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
    Note: may not be working!
    Run this script directly if you want to test it.
    Pass in the date threshold from the command line.
    """
    #testing eligibility for invite (not blocked)
    block_test_user = sys.argv[1]
    e = Eligible(hb_output_settings.Params().getParams('th_invites'))
    is_blocked = e.getBlockStatus(block_test_user)
    print(is_blocked)

# cmt out on 9/15/2017 to test block status
#     param = hb_output_settings.Params()
#     params = param.getParams(sys.argv[1]) #what type of invites
#     sub_date = int(sys.argv[2]) #numeric threshold (days ago)
#     e = Eligible()
#     potential_inviters = params['inviters']
#     eligible_inviters = [x for x in potential_inviters if e.determineInviterEligibility(x, sub_date)]
#     print potential_inviters
#     print eligible_inviters