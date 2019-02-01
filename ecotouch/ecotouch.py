import requests
import re

class StatusException(Exception):
    pass

class Ecotouch:
    auth_cookies = None

    def __init__(self, host):
        self.hostname = host

    def get_status_response(self, r):
        return re.search(r'^#([A-Z_]+)', r.text, re.MULTILINE).group(1)

    def login(self, username="waterkotte", password="waterkotte"):
        args={'username': username, 'password':password}
        r = requests.get('http://%s/cgi/login' % self.hostname, params=args)
        if self.get_status_response(r) != "S_OK":
            raise StatusException("Fehler beim Login: Status:%s" % self.get_status_response(r)) 
        self.auth_cookies = r.cookies


    def read_tag(self, tag):
        args={'n': 1, 't1': tag.tag}
        r = requests.get('http://%s/cgi/readTags' % self.hostname, params=args, cookies=self.auth_cookies)
        val_str = re.search(r'(?:^\d+\t)(\d+)', r.text, re.MULTILINE).group(1)
        val = int(val_str) * tag.factor
        print("%s: %s [%s]" % (tag.identifier, tag.pattern % val, tag.unit))
        return val


