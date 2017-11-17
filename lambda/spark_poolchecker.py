'''
Function to receive webhooks from Spark bot and run pools check
'''

import json
import urllib2
import re
import socket
import os
import sys


PROXY_LIST = { 
    'test': [1,2,9243,1736]
}


def _url(path):
    return 'https://api.ciscospark.com/v1/' + path


#correct syntax of authentication token:
def fix_at(at):
    at_prefix = 'Bearer '
    if not re.match(at_prefix, at):
        return 'Bearer ' + at
    else:
        return at


def findroomidbyname(at, roomName):
    room_dict = get_rooms(fix_at(at))
    for room in room_dict['items']:
        #print (room['title'])
        if room['title'] == roomName:
            return room['id']


def post_message(at, roomId, message, toPersonId='', toPersonEmail=''):
    payload = {'text': message, 'markdown': message}
    if roomId:
        payload['roomId'] = roomId
    if toPersonId:
        payload['toPersonId'] = toPersonId
    if toPersonEmail:
        payload['toPersonEmail'] = toPersonEmail
    data = json.dumps(payload)
    req = urllib2.Request(_url('messages'), data)
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', fix_at(at))
    try:
        response = urllib2.urlopen(req)
        response_dict = json.loads(response.read())
        return responce_dict
    except Exception as e:
        if hasattr(e, 'reason'):
            return 'We failed to reach a server. Reason: ', e.reason
        elif hasattr(e, 'code'):
            return 'The server couldn\'t fulfill the request. Error code: ', e.code


def get_msg_details(at, msgId):
    req = urllib2.Request(_url('messages/'+msgId))
    req.add_header('Content-Type', 'application/json')
    req.add_header('Authorization', fix_at(at))
    try:
        response = urllib2.urlopen(req)
        response_dict = json.loads(response.read())
        return response_dict
    except Exception as e:
        if hasattr(e, 'reason'):
            print 'We failed to reach a server. Reason: ', e.reason
            return False
        elif hasattr(e, 'code'):
            print 'The server couldn\'t fulfill the request. Error code: ', e.code
            return False


def ping_pools(prxlist, dc, roomId):
    port = 8080
    if dc not in list(prxlist):
        err_msg = "%s is not in list" % dc
        post_message(ACCESS_TOKEN, roomId, err_msg)
        #print err_msg
        return err_msg
    else:
        proxy_list = prxlist[dc]
        print "length = %s" % len(proxy_list)
        for proxynum in proxy_list:
            proxy = "access" + str(proxynum) + ".cws.example.com"
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.settimeout(0.5)
            try:
                s_result = s.connect_ex((proxy, port))
                print s_result
                if s_result == 0:
                    messg_ok = "* {0} is OK".format(proxy)
                    post_message(ACCESS_TOKEN, roomId, messg_ok)
                elif s_result == 11:
                    messg_bad = "* {0} is NOT OK - connection timeout".format(proxy)
                    post_message(ACCESS_TOKEN, roomId, messg_bad)
                else:
                    messg_fail = "* {0} is NOT OK - socket error code {1}".format(proxy, s_result)
                    post_message(ACCESS_TOKEN, roomId, messg_fail)
            except Exception as e:
                err_msg = "* {0} - [ERROR] TCP connection error: '{1}'".format(proxy, e)
                post_message(ACCESS_TOKEN, roomId, err_msg)
            s.close()
        print "Check completed"
        return "Check completed"


def lambda_handler(event, context):
    sender = event['data']['personEmail']
    msgId = event['data']['id']
    roomId = event['data']['roomId']
    print event
    if sender != "poolcheck@sparkbot.io":
        try:
            if get_msg_details(ACCESS_TOKEN, msgId) == False:
                raise Exception('Could not get message details')
            else:
                site = get_msg_details(ACCESS_TOKEN, msgId)['text'].split()
                if len(site) == 1:
                    site = site[0].lower()
                else:
                    site = site[1].lower()
                init_msg = "**Running test for {0}**".format(site.upper())
                post_message(ACCESS_TOKEN, roomId, init_msg)
                ping_pools(PROXY_LIST, site, roomId)
                post_message(ACCESS_TOKEN, roomId, '**Test finished.**')
                return "Message has been sent"
        except Exception as e:
            print e
            return 'Request failed'
    else:
        print "It's my own message, ignore"
        return "Request ignored"
