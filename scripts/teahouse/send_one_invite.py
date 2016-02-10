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

import hb_api_queries
import hb_output_settings
import hb_profiles
import requests
from requests_oauthlib import OAuth1
import sys


def runSample(page_path, page_id):
    output = hb_profiles.Profiles(params['output namespace'] + page_path, id = page_id, settings = params)
    invited = False
    skip = talkpageCheck(output)
    print "skipped? " + skip
    message = random.choice(params['messages'])
    if not skip:
        inviteGuests(output, message[1], "Jtmorgan")
        invited = True
    print "invited? " + invited

def talkpageCheck(output):
    """checks talk pages"""
    skip = False
    talkpage_text = output.getPageText()
    for template in params['skip templates']:
        if template in talkpage_text:
            skip = True
    return skip
    
def inviteGuests(output, message_text, inviter):
    """
    Invites todays newcomers.
    """
    invite = output.formatProfile({'inviter' : inviter, 'message' : message_text})
    edit_summ = page_path + params["edit summary"]
    try:
        output.publishProfile(invite, params['output namespace'] + page_path, edit_summ, edit_sec = "new")
    except:
        print "something went wrong trying to invite " + page_path

if __name__ == "__main__":
    param = hb_output_settings.Params()
    params = param.getParams("th_invites")
    page_path = sys.argv[0]
    page_id = sys.argv[1]
    api_queries = hb_api_queries.Query()
    text = api_queries.getPageText(page_path, page_id)
    print text
#     runSample(page_path, page_id)
