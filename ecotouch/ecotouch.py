import requests
import re

class Ecotouch:
    auth_cookies = None

    def __init__(self, host):
        self.hostname = host

    def get_status_response(self, r):
        return re.search(r'^(#[A-Z]+)', r.text, re.MULTILINE).group(1)

    def login(self, username="waterkotte", password="waterkotte"):
        args={'username': username, 'password':password}
        r = requests.get('http://%s/cgi/login' % self.hostname, params=args)
        print("login: " + repr(r.text))
        if self.get_status_response(r) != "#OK":
            raise "Fehler beim Login: Status:%s" % self.get_status_response(r) 
        self.auth_cookies = r.cookies


    def read_tag(self, tag):
        args={'n': 1, 't1': tag.tag}
        r = requests.get('http://%s/cgi/readTags' % self.hostname, params=args, cookies=self.auth_cookies)
        print("%s: %s" % (tag.identifier, repr(r.text)))
        val = re.search(r'(?:^\d+\t)(\d+)', r.text, re.MULTILINE).group(1)
        print("%s: %s" % (tag.identifier, val))
        return val


