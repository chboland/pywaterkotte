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

# default method that reads a value based on a single tag
def _parse_value_default(self, vals, bitnum=None):
    assert len(self._tags) == 1
    ecotouch_tag = self._tags[0]
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
    assert len(self._tags) == 1
    ecotouch_tag = self._tags[0]
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

def _parse_time(self, e_vals):
    vals = [int(e_vals[tag]) for tag in self._tags]
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
    for i in range(len(tag._tags)):
        et_values[tag._tags[i]] = vals[i]

class EcotouchTag(Enum):
    def __init__(self, ecotouch_tags, unit : str =None, writeable : bool = False, read_function=None, write_function=None, bit : int =None):
        self._tags = ecotouch_tags
        self.unit = unit
        self._writeable = writeable
        self.bitnum = bit

        if read_function is None:
            self._fn_read = lambda t : _parse_value_default(self, t, bit)
        else:
            self._fn_read = lambda t : read_function(self, t)
        if write_function is None:
            self._fn_write = lambda v, ev : _write_value_default(self, v, ev)
        else:
            self._fn_write = lambda v, ev : write_function(self, v, ev)

    TEMPERATURE_OUTSIDE =           (['A1'], '°C')
    HOLIDAY_ENABLED =               (['D420'], None, True)
    HOLIDAY_START_TIME =            (['I1254', 'I1253', 'I1252', 'I1250', 'I1251'], None, True, _parse_time, _write_time)
    HOLIDAY_END_TIME =              (['I1259', 'I1258', 'I1257', 'I1255', 'I1256'], None, True, _parse_time, _write_time)
    TEMPERATURE_OUTSIDE_1H =        (['A2'], '°C')
    TEMPERATURE_OUTSIDE_24H =       (['A3'], '°C')
    TEMPERATURE_SOURCE_IN =         (['A4'], '°C')
    TEMPERATURE_SOURCE_OUT =        (['A5'], '°C')
    TEMPERATURE_WATER =             (['A19'], '°C')
    TEMPERATURE_WATER_SETPOINT =    (['A37'], '°C', True)
    ADAPT_HEATING =                 (['I263'], None, True)
    STATE_SOURCEPUMP =              (['I51'], None, False, None, None, 0)
    STATE_HEATINGPUMP =             (['I51'], None, False, None, None, 1)
    STATE_COMPRESSOR =              (['I51'], None, False, None, None, 3)
    STATE_EXTERNAL_HEATER =         (['I51'], None, False, None, None, 5)

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

    def read_value(self, tag):
        res = self.read_values([tag])
        if tag in res:
            return res[tag]
        return None

    def write_values(self, kv_pairs):
        to_write = {}
        for k, v in kv_pairs:
            if not k._writeable:
                raise InvalidValueException('tried to write to an readonly field')
            k._fn_write(v, to_write)

        for k,v in to_write.items():
            self._write_tag(k,v)

    def write_value(self, tag, value):
        self.write_values([(tag, value)])


    def read_values(self, tags):
        #create flat list of ecotouch tags to be read
        e_tags = list(set([etag for tag in tags for etag in tag._tags]))
        e_values = self._read_tags(e_tags)

        result = {}
        for tag in tags:
            result[tag] = tag._fn_read(e_values)
        return result

    #
    # reads a list of ecotouch tags
    #
    def _read_tags(self, tags, results={}):

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
    def _write_tag(self, tag, value):
        args={'n': 1, 'returnValue': 'true', 't1': tag, 'v1' : value}
        r = requests.get('http://%s/cgi/writeTags' % self.hostname, params=args, cookies=self.auth_cookies)
        val_str = re.search(r'(?:^\d+\t)(\-?\d+)', r.text, re.MULTILINE).group(1)
        return val_str

