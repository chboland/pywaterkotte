import requests
from itertools import islice
import re

MAX_NO_TAGS = 20

class StatusException(Exception):
    pass

class InvalidResponseException(Exception):
    pass

#
# Class to control Waterkotte Ecotouch heatpumps.
#
class Ecotouch:
    auth_cookies = None

    def __init__(self, host):
        self.hostname = host

    # extracts statuscode from response
    def get_status_response(self, r):
        match = re.search(r'^#([A-Z_]+)', r.text, re.MULTILINE)
        if match is None:
            raise InvalidResponseException('Ungültige Antwort. Konnte Status nicht auslesen.')
        return match.group(1)

    # performs a login. Has to be called before any other method.
    def login(self, username="waterkotte", password="waterkotte"):
        args={'username': username, 'password':password}
        r = requests.get('http://%s/cgi/login' % self.hostname, params=args)
        if self.get_status_response(r) != "S_OK":
            raise StatusException("Fehler beim Login: Status:%s" % self.get_status_response(r)) 
        self.auth_cookies = r.cookies

    #
    # reads a list of tags
    #
    def read_tags(self, tags, results={}):

        if len(tags) > MAX_NO_TAGS:
            results = self.read_tags(tags[MAX_NO_TAGS:], results)
        tags = tags[:MAX_NO_TAGS]

        args = {}
        args['n'] = len(tags)
        for i in range(len(tags)):
            args['t%d' % (i+1)] = tags[i].tag
        r = requests.get('http://%s/cgi/readTags' % self.hostname, params=args, cookies=self.auth_cookies)
        for tag in tags:
            match = re.search(r'#%s\t(?P<status>[A-Z_]+)\n\d+\t(?P<value>\-?\d+)' % tag.tag, r.text, re.MULTILINE)
            val_str = match.group('value')
            val_status = match.group('status')
            if val_str is not None:
                if tag.no_decimal_places > 0:
                    val_str = val_str[:-tag.no_decimal_places] + '.' + val_str[-tag.no_decimal_places:]
                val = tag.val_type(val_str)
                results[tag] = val
            else:
                results[tag] = None


        return results


    #
    # reads a single tag
    #
    def read_tag(self, tag):
        return self.read_tags([tag])[tag]
    
    #
    # writes <value> into the tag <tag>
    #
    def write_tag(self, tag, value):
        args={'n': 1, 't1': tag.tag, 'v1' : value}
        r = requests.get('http://%s/cgi/writeTags' % self.hostname, params=args, cookies=self.auth_cookies)
        print(repr(r.text))
        val_str = re.search(r'(?:^\d+\t)(\-?\d+)', r.text, re.MULTILINE).group(1)
        if tag.no_decimal_places > 0:
            val_str = val_str[:-tag.no_decimal_places] + '.' + val_str[-tag.no_decimal_places:]
        val = tag.val_type(val_str)
        return val

    def slice_list(self, tags):
        it = iter(tags)
        for i in range(0, len(tags), MAX_NO_TAGS):
            yield [k for k in islice(it, MAX_NO_TAGS)]



