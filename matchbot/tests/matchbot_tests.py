from nose.tools import *
import datetime

from matchbot import *


def setup():
    print('Setup!')


def teardown():
    print('Teardown!')


def test_basic():
    print('I RAN!')


def test_parse_timestamp():
    assert matchbot.parse_timestamp('0000-00-00T00:00:00Z') == None
    assert matchbot.parse_timestamp('2010-10-10T01:01:10Z') == datetime.datetime(2010, 10, 10, 01, 01, 10)


def test_get_profile_talkpage():
    pass


def test_match():
    pass


def test_build_greeting():
    pass


def test_get_revid():
    pass


def test_get_time_posted():
    pass
