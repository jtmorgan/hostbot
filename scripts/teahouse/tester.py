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
import requests
from requests_oauthlib import OAuth1


if __name__ == "__main__":
    #dev
# Set up your auth -- do this once
    auth1 = OAuth1(unicode("b5d87cbe96174f9435689a666110159c"),
        client_secret=unicode(hostbot_settings.client_secret),
        resource_owner_key=unicode("ca1b222d687be9ac33cfb49676f5bfd2"),
        resource_owner_secret=unicode(hostbot_settings.resource_owner_secret))

    # Do this once for every edit (Not part of OAuth)
    response = requests.get(
        hostbot_settings.oauth_api_url,
        params={
            'action': "query",
            'meta': "tokens",
            'type': "csrf",
            'format': "json"
        },
        headers={'User-Agent': hostbot_settings.oauth_user_agent},
        auth=auth1  # This is the new thing
    )
    doc = response.json() #why name this variable doc? 
    print doc
    response = requests.post(
        "https://en.wikipedia.org/w/api.php",
        data={
            'action': "edit",
            'title': "User:Jtmorgan/sandbox",
            'section': "new",
            'summary': "Hello World",
            'text': "Hello everyone!",
            'token': doc['query']['tokens']['csrftoken'],
            'format': "json"
        },
        headers={'User-Agent': hostbot_settings.oauth_user_agent},
        auth=auth1  # This is the new thing
    )
    response.json()