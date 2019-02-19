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
        print(r.text)
        val_str = re.search(r'(?:^\d+\t)(\-?\d+)', r.text, re.MULTILINE).group(1)
        if tag.no_decimal_places > 0:
            val_str = val_str[:-tag.no_decimal_places] + '.' + val_str[-tag.no_decimal_places:]
        val = tag.val_type(val_str)
        return val

    def write_tag(self, tag, value):
        args={'n': 1, 't1': tag.tag, 'v1' : value}
        r = requests.get('http://%s/cgi/writeTags' % self.hostname, params=args, cookies=self.auth_cookies)
        print(r.text)
        val_str = re.search(r'(?:^\d+\t)(\-?\d+)', r.text, re.MULTILINE).group(1)
        if tag.no_decimal_places > 0:
            val_str = val_str[:-tag.no_decimal_places] + '.' + val_str[-tag.no_decimal_places:]
        val = tag.val_type(val_str)
        return val


