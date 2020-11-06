from typing import Any, Callable, Collection, NamedTuple, Sequence, Tuple
import requests
import re
from enum import Enum
from datetime import datetime, timedelta

MAX_NO_TAGS = 20

class StatusException(Exception):
    pass

class InvalidResponseException(Exception):
    pass

class InvalidValueException(Exception):
    pass

class EcotouchTag:
    pass

# default method that reads a value based on a single tag
def _parse_value_default(self : EcotouchTag, vals, bitnum=None, *other_args):
    assert len(self.tags) == 1
    ecotouch_tag = self.tags[0]
    assert ecotouch_tag[0] in ['A', 'I', 'D']

    if ecotouch_tag not in vals:
        return None

    val = vals[ecotouch_tag]
    
    if ecotouch_tag[0] == 'A':
        return float(val) / 10.            
    if ecotouch_tag[0] == 'I':
        if bitnum is None:
            return int(val)
        else:
            return (int(val) & (1 << bitnum)) > 0

    if ecotouch_tag[0] == 'D':
        if val == "1":
            return True
        elif val == "0":
            return False
        else:
            raise InvalidValueException("%s is not a valid value for %s" % (val, ecotouch_tag))

def _write_value_default(self, value, et_values):
    assert len(self.tags) == 1
    ecotouch_tag = self.tags[0]
    assert ecotouch_tag[0] in ['A', 'I', 'D']

    if ecotouch_tag[0] == 'I':
        assert isinstance(value, int)
        et_values[ecotouch_tag] = str(value)
    elif ecotouch_tag[0] == 'D':
        assert isinstance(value, bool)
        et_values[ecotouch_tag] = '1' if value else '0'
    elif ecotouch_tag[0] == 'A':
        assert isinstance(value, float)
        et_values[ecotouch_tag] = str(int(value*10))

def _parse_time(self, e_vals, *other_args):
    vals = [int(e_vals[tag]) for tag in self.tags]
    vals[0] = vals[0] + 2000
    next_day = False
    if (vals[3] == 24):
        vals[3] = 0
        next_day = True

    dt = datetime(*vals)
    return dt + timedelta(days=1) if next_day else dt

def _write_time(tag, value, et_values):
    assert isinstance(value, datetime)
    vals = [str(val) for val in [value.year % 100, value.month, value.day, value.hour, value.minute, value.second]]
    for i in range(len(tag.tags)):
        et_values[tag.tags[i]] = vals[i]

class TagData(NamedTuple):
    tags : Collection[str]
    unit: str = None
    writeable: bool = False
    read_function : Callable = _parse_value_default
    write_function : Callable = _write_value_default
    bit : int = None

class EcotouchTag(TagData, Enum):
    TEMPERATURE_OUTSIDE =           TagData(['A1'], '°C')
    HOLIDAY_ENABLED =               TagData(['D420'], writeable=True)
    HOLIDAY_START_TIME =            TagData(['I1254', 'I1253', 'I1252', 'I1250', 'I1251'],  writeable=True, read_function=_parse_time, write_function=_write_time)
    HOLIDAY_END_TIME =              TagData(['I1259', 'I1258', 'I1257', 'I1255', 'I1256'],  writeable=True, read_function=_parse_time, write_function=_write_time)
    TEMPERATURE_OUTSIDE_1H =        TagData(['A2'], '°C')
    TEMPERATURE_OUTSIDE_24H =       TagData(['A3'], '°C')
    TEMPERATURE_SOURCE_IN =         TagData(['A4'], '°C')
    TEMPERATURE_SOURCE_OUT =        TagData(['A5'], '°C')
    TEMPERATURE_WATER =             TagData(['A19'], '°C')
    TEMPERATURE_WATER_SETPOINT =    TagData(['A37'], '°C', writeable=True)
    ADAPT_HEATING =                 TagData(['I263'], writeable=True)
    STATE_SOURCEPUMP =              TagData(['I51'], bit=0)
    STATE_HEATINGPUMP =             TagData(['I51'], bit=1)
    STATE_COMPRESSOR =              TagData(['I51'], bit=3)
    STATE_EXTERNAL_HEATER =         TagData(['I51'], bit=5)

    def __hash__(self) -> int:
        return hash(self.name)

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

    def read_value(self, tag : EcotouchTag):
        res = self.read_values([tag])
        if tag in res:
            return res[tag]
        return None

    def write_values(self, kv_pairs : Collection[Tuple[EcotouchTag, Any]]):
        to_write = {}
        for k, v in kv_pairs:
            if not k.writeable:
                raise InvalidValueException('tried to write to an readonly field')
            k.write_function(k, v, to_write)

        for k,v in to_write.items():
            self._write_tag(k,v)

    def write_value(self, tag, value):
        self.write_values([(tag, value)])


    def read_values(self, tags : Sequence[EcotouchTag]):
        #create flat list of ecotouch tags to be read
        e_tags = list(set([etag for tag in tags for etag in tag.tags]))
        e_values = self._read_tags(e_tags)

        result = {}
        for tag in tags:
            val = tag.read_function(tag, e_values, tag.bit)
            result[tag] = val
        return result

    #
    # reads a list of ecotouch tags
    #
    def _read_tags(self, tags : Sequence[EcotouchTag], results={}):

        if len(tags) > MAX_NO_TAGS:
            results = self.read_tags(tags[MAX_NO_TAGS:], results)
        tags = tags[:MAX_NO_TAGS]

        args = {}
        args['n'] = len(tags)
        for i in range(len(tags)):
            args['t%d' % (i+1)] = tags[i]
        r = requests.get('http://%s/cgi/readTags' % self.hostname, params=args, cookies=self.auth_cookies)
        for tag in tags:
            match = re.search(r'#%s\t(?P<status>[A-Z_]+)\n\d+\t(?P<value>\-?\d+)' % tag, r.text, re.MULTILINE)
            if match is None:
                raise Exception("tag not found in response")
            val_str = match.group('value')
            val_status = match.group('status')
            results[tag] = val_str
        return results
    
    #
    # writes <value> into the tag <tag>
    #
    def _write_tag(self, tag : EcotouchTag, value):
        args={'n': 1, 'returnValue': 'true', 't1': tag, 'v1' : value}
        r = requests.get('http://%s/cgi/writeTags' % self.hostname, params=args, cookies=self.auth_cookies)
        val_str = re.search(r'(?:^\d+\t)(\-?\d+)', r.text, re.MULTILINE).group(1)
        return val_str

