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
        self.api_url = hb_config.api_url_get
        self.output_params = params

    def get_latest_edit_date(self, user_name):
        """
        Takes a user name. Returns the date of that user's latest edit, in datetime format.
        See: https://www.mediawiki.org/wiki/API:Usercontribs
        Example: https://en.wikipedia.org/w/api.php?ucprop=timestamp&ucuser=Jtmorgan&list=usercontribs&action=query&ucdir=older
        """

        api_params = {
            "action" : "query",
            "list" : "usercontribs",
            "ucuser" : user_name,
            "uclimit" : 1,
            "ucdir" : "older",
            "ucprop": "timestamp",
            "format": "json",
            }

        api_req = requests.get(self.api_url, params=api_params)
#         print(api_req.url)
        api_data = api_req.json()
        edit_timestamp = api_data["query"]["usercontribs"][0]["timestamp"]
        latest_edit_date = dateutil.parser.parse(edit_timestamp, ignoretz=True).date()

        return latest_edit_date


    def get_block_status(self, user_name, blocked = False):
        """
        Takes a user name. Returns whether the user is currently blocked from editing, as a boolean value.
        See: https://www.mediawiki.org/wiki/API:Users
        Example: https://en.wikipedia.org/w/api.php?action=query&list=users&ususers=Willy_on_Wheels~enwiki&usprop=blockinfo
        """
        api_params = {
            "action" : "query",
            "list" : "users",
            "ususers" : user_name,
            "usprop" : "blockinfo",
            "format": "json",
            }
        api_req = requests.get(self.api_url, params=api_params)
        # print(api_req.url)

        api_data = api_req.json()
        if "blockid" in api_data["query"]["users"][0].keys():#check this
            blocked = True
 #            print("The user " + user_name + " is blocked.") #to check whether my block check is working
        else:
            pass

        return blocked


    def meets_edit_date_threshold(self, latest_edit_date, threshold, meets_threshold = False):
        """
        Takes a datetime of someone's latest edit and a numeric threshold.
        Returns a boolean of whether that datetime falls within a given number of days from the current date.
        """
        cur_date = datetime.utcnow().date()
        threshold_date = cur_date - timedelta(days=threshold)

        if latest_edit_date >= threshold_date:
            meets_threshold = True
        else:
            pass

        return meets_threshold


    def determine_user_eligibility(self, user, elig_type, is_eligible = False):
        """
        Takes a username and numeric threshold.
        Returns a boolean of whether that user is eligible to be listed as a Teahouse inviter.
        """

        is_blocked = self.get_block_status(user)
#         if is_blocked: #for checking whether the block check is working
#             print(user + " is blocked")

        if elig_type == 'inviter':
            latest_edit_date = self.get_latest_edit_date(user)
            is_active = self.meets_edit_date_threshold(latest_edit_date, self.output_params['inviter edit threshold'])#check
            if is_active and not is_blocked:
                is_eligible = True

        elif elig_type == 'invitee':
            has_skip_template = self.check_talkpage_text(self.output_params["output namespace"] + user, self.output_params["skip templates"])
            if not has_skip_template and not is_blocked:
                is_eligible = True

        else:
            print("unrecognized user type: " + elig_type)

        return is_eligible


    def check_talkpage_text(self, page_path, skip_templates, skip=False):
        """
        Takes a dictionary of key words, and a talkpage and namespace string
        If those words appear in the user talkpage text, skip the user (e.g. don't send an invite).
        """
#         skip = False
        tp_text = self.get_page_text(page_path)
        if tp_text is not None:
            for t in skip_templates:
                if t in tp_text:
                    skip = True
#                     print("This talkpage contains skip templates: " + page_path) #verifying the talkpage check is working
        return skip


    def get_page_text(self, page_path, section=False, text=None):

        """
        Takes a page and namespace and optionally a section number
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

        response = requests.get(self.api_url, params=api_params)
        doc = response.json()
        if "-1" in doc['query']['pages'].keys():
            pass #no talkpage found
        else:
            for v in doc['query']['pages'].values():
#                 print(v)
                text = v['revisions'][0]['*']

        return text

    def get_page_id(self, page_path, page_id=None): #should merge with get_page_text

        """
        Takes a page and namespace
        Gets the id of the page.
        Sample: https://en.wikipedia.org/w/api.php?action=query&prop=revisions&titles=User_talk:Abcd%20dbca&rvprop=ids&format=jsonfm
        """
        api_params={
            'action': 'query',
            'prop': 'revisions',
            'titles': page_path,
            'rvprop' : 'content',
            'format': "json"
        }

        response = requests.get(self.api_url, params=api_params)
        doc = response.json()
        if "-1" in doc['query']['pages'].keys():
            pass #no talkpage found
        else:
            for v in doc['query']['pages'].values():
#                 print(v)
                page_id = v['pageid']

        return page_id


if __name__ == "__main__":
    """
    Run this script directly if you want to test it.
    Pass in the username from the command line.
    """
    test_user = sys.argv[1]
    e = Eligible(hb_output_settings.Params().getParams('test_invites'))
    latest_edit = e.get_latest_edit_date(test_user)

    print("is blocked: " + str(e.get_block_status(test_user)))

    print(str(datetime.strftime(latest_edit, "%Y-%m-%d")))

    print("meets edit date threshold: " + str(e.meets_edit_date_threshold(latest_edit, e.output_params['inviter edit threshold'])))

    talkpage = e.get_page_text(e.output_params['output namespace'] + test_user)
    if talkpage is not None:
        has_talkpage = True
    else:
        has_talkpage = False
    print("has talkpage: " + str(has_talkpage))

    print("found skip templates: " + str(e.check_talkpage_text(e.output_params['output namespace'] + test_user, e.output_params['skip templates'])))
    print("is eligible inviter: " + str(e.determine_user_eligibility(test_user, 'inviter')))
    print("is eligible invitee: " + str(e.determine_user_eligibility(test_user, 'invitee')))