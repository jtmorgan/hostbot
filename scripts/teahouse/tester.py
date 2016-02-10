
import invite_config
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