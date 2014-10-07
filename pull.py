#!/usr/bin/env python

import json
import urllib
from subprocess import call
from urllib2 import urlopen
import os
import math
import urllib2, base64
import keyring
import getopt
import sys

user=None
dest=None
token=None
use_keychain=False

def usage():
    print "%s args " % (sys.argv[0])
    print "where args are"
    print "-u  --user=<username>"
    print "-t --token=<github api token>"
    print "-d --dest=<destination for extracting the gists>"
    print "-u --use-keychain use the system keychain to obtain the token"

try:
    opts, args = getopt.getopt(sys.argv[1:], "u:t:d:kh", ["user=","token=","dest=","use-keychain","help"])
except getopt.error, msg:
    print "err %s %s" % (getopt.error, msg)
    usage()
    sys.exit(2)
    # process options
for o, a in opts:
    if o in ("-u", "--user"):
        user=a
    if o in ("-t", "--token"):
        token=a
    if o in ("-d", "--dest"):
        dest=a
    if o in ("-k", "--use-keychain"):
        use_keychain=True
    if o in ("-h", "--help"):
        usage()
        sys.exit(0)

#print "%s %s %s %s" % (user, token, dest, use_keychain) 

if use_keychain:
    kr=keyring.get_keyring()
    token=kr.get_password('github.gist','token')
    if token == None:
        print "please create an OSX keyring item - 'token' in the 'github.gist' keychain - You can use keychain access to do so"
        exit(1)

if token == None or user == None:
    print "either supply token (--token) on command line and provide user (--user), or choose --use-keychain and provide username"

if dest == None:
    print "dest (--dest) not specified"
    exit(1)

if not os.path.isdir(dest):
    print "target %s is not a directory" % dest
    exit(1)

request = urllib2.Request( 'https://api.github.com/users/' + user )
base64string = base64.encodestring('%s:x-oauth-basic' % (token)).replace('\n', '')
request.add_header("Authorization", "Basic %s" % base64string)   
userurl = urllib2.urlopen(request)

perpage=30.0

my_gists = json.load(userurl)

gistcount = int(my_gists['public_gists']) + int(my_gists['private_gists'] )
print "Found gists : " + str(gistcount)
pages = int(math.ceil(float(gistcount)/perpage))
print "Found pages : " + str(pages)

for page in range(pages):
    pageNumber = str(page + 1)
    print "Processing page number " + pageNumber
    #pageUrl = 'https://api.github.com/users/' + USER  + '/gists?page=' + pageNumber + '&per_page=' + str(int(perpage))
    pageUrl = 'https://api.github.com/users/' + user + '/gists?page=' + pageNumber + '&per_page=' + str(int(perpage))
    
    
    request = urllib2.Request( pageUrl  )
    base64string = base64.encodestring('%s:x-oauth-basic' % (token)).replace('\n', '')
    request.add_header("Authorization", "Basic %s" % base64string)   
    u = urlopen (request)

    gists = json.load(u)
    startd = os.getcwd()
    for gist in gists:
        try:
            gistd = gist['id']
            gistUrl = 'git@gist.github.com:/' + gistd + '.git' 
            targetdir=dest + gistd 

            print "gist %s trying to get %s into %s" % ( gistd, gistUrl, targetdir )
            if os.path.isdir(targetdir):
                os.chdir(targetdir)
                call(['git', 'pull'])
                os.chdir(startd)
            else:
                os.chdir(dest)
                call(['git', 'clone', gistUrl])
                os.chdir(startd)
        except Exception as e:
                print gist
                print e
                os.chdir(startd)
