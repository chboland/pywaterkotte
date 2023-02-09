"""
library for communicating with waterkote ecotouch heatpumps
"""
import re
from dataclasses import dataclass
from datetime import datetime, timedelta, date
import struct
from typing import Any, Callable, Collection, Dict, List, Tuple

import requests

import types

MAX_NO_TAGS = 75
REQUEST_TIMEOUT = 3000


class InvalidResponseException(Exception):
    """the heatpump sent an unexpected response"""


class InvalidValueException(Exception):
    """thrown if value to be written is not suitable for a tag"""


class AuthenticationException(Exception):
    """thrown if login failed"""


class ConnectionException(Exception):
    """thrown if connection with heatpump not possible"""


@dataclass
class TagData:
    """collects all information required to read/write values"""

    def __hash__(self) -> int:
        return hash(tuple(self.tags))

    def _parse_value_default(self, vals: List[str]) -> Any:
        """
        default method that reads a value based on
        * a single tag if type D
        * one or more tags if type I or A
        """
        first_tag = self.tags[0]
        first_val = vals[0]

        # float case
        if first_tag.startswith("A"):
            if len(self.tags) == 1:
                return float(first_val) / 10.0
            ivals = [int(str_val) & 0xFFFF for str_val in vals]
            hex_string = f"{ivals[0]:04x}{ivals[1]:04x}"
            return struct.unpack("!f", bytes.fromhex(hex_string))[0]

        # integer case
        if first_tag.startswith("I"):
            if self.bit is not None:
                return (int(first_val) & (1 << self.bit)) > 0
            return int("".join(vals))

        # boolean case
        if first_tag.startswith("D"):
            if first_val == "1":
                return True
            if first_val == "0":
                return False
            raise InvalidValueException(
                f"{first_val} is not a valid value for {first_tag}"
            )
        raise Exception("Invalid tag type")

    def _write_value_default(self, value):
        et_values = {}
        assert len(self.tags) == 1
        ecotouch_tag = self.tags[0]
        assert ecotouch_tag[0] in ["A", "I", "D"]

        if ecotouch_tag[0] == "I":
            assert isinstance(value, int)
            et_values[ecotouch_tag] = str(value)
        elif ecotouch_tag[0] == "D":
            assert isinstance(value, bool)
            et_values[ecotouch_tag] = "1" if value else "0"
        elif ecotouch_tag[0] == "A":
            assert isinstance(value, float)
            et_values[ecotouch_tag] = str(int(value * 10))
        return et_values

    def _parse_time(self, str_vals: List[str]) -> datetime:
        vals = list(map(int, str_vals))
        vals[0] = vals[0] + 2000
        next_day = False
        if vals[3] == 24:
            vals[3] = 0
            next_day = True

        dt_val = datetime(*vals)
        return dt_val + timedelta(days=1) if next_day else dt_val

    def _write_time(self, value):
        et_values = {}
        assert isinstance(value, datetime)
        vals = [
            str(val)
            for val in [
                value.year % 100,
                value.month,
                value.day,
                value.hour,
                value.minute,
                value.second,
            ]
        ]
        for i, val in enumerate(self.tags):
            et_values[val] = vals[i]
        return et_values

    def _parse_firmware(self, str_vals: List[str]) -> str:
        str_val = str_vals[0]
        return f"{str_val[:-4]:0>2}.{str_val[-4:-2]}.{str_val[-2:]}"

    def _parse_bios(self, str_vals: List[str]) -> str:
        str_val = str_vals[0]
        return f"{str_val[:-2]}.{str_val[-2:]}"

    def _parse_bios_date(self, str_vals: List[str]):
        int_date = self._parse_value_default(str_vals)
        bios_day = int(int_date / 1000)
        bios_month = int((int_date % 1000) / 10)
        bios_year = int_date % 10

        if bios_month > 80:
            bios_month -= 80
            bios_year += 40
        elif bios_month > 60:
            bios_month -= 60
            bios_year += 30
        elif bios_month > 40:
            bios_month -= 40
            bios_year += 20
        elif bios_month > 20:
            bios_month -= 20
            bios_year += 10

        return date(bios_year + 2000, bios_month, bios_day)

    tags: Collection[str]
    unit: str = None
    writeable: bool = False
    read_function: Callable[[Any, Dict[Any, str], int], Any] = _parse_value_default
    write_function: Callable[[Any, Any], Dict[str, str]] = _write_value_default
    bit: int = None

    def parse_value(self, str_vals: List[str]) -> Any:
        return self.read_function(self, str_vals)

    def write_value(self, val) -> Dict[str, str]:
        return self.write_function(self, val)


class EcotouchTags(TagData):
    """enumeration and configuration of all configured ecotouch tags"""

    OUTSIDE_TEMPERATURE = TagData(["A1"], "°C")
    OUTSIDE_TEMPERATURE_1H = TagData(["A2"], "°C")
    OUTSIDE_TEMPERATURE_24H = TagData(["A3"], "°C")
    HOLIDAY_ENABLED = TagData(["D420"], writeable=True)
    HOLIDAY_START_TIME = TagData(
        ["I1254", "I1253", "I1252", "I1250", "I1251"],
        writeable=True,
        read_function=TagData._parse_time,
        write_function=TagData._write_time,
    )
    HOLIDAY_END_TIME = TagData(
        ["I1259", "I1258", "I1257", "I1255", "I1256"],
        writeable=True,
        read_function=TagData._parse_time,
        write_function=TagData._write_time,
    )
    SOURCE_IN_TEMPERATURE = TagData(["A4"], "°C")
    SOURCE_OUT_TEMPERATURE = TagData(["A5"], "°C")
    EVAPORATION_TEMPERATURE = TagData(["A6"], "°C")
    SUCTION_LINE_TEMPERATURE = TagData(["A7"], "°C")
    EVAPORATION_PRESSURE = TagData(["A8"], "bar")
    RETURN_TEMPERATURE = TagData(["A11"], "°C")
    FLOW_TEMPERATURE = TagData(["A12"], "°C")
    CONDENSATION_TEMPERATURE = TagData(["A13"], "°C")
    BUFFER_TANK_TEMPERATURE = TagData(["A16"], "°C")
    ROOM_TEMPERATURE = TagData(["A17"], "°C")
    ROOM_TEMPERATURE_1H = TagData(["A18"], "°C")
    HOT_WATER_TEMPERATURE = TagData(["A19"], "°C")
    HOT_WATER_TEMPERATURE_SETPOINT = TagData(["A37"], "°C", writeable=True)
    HEATING_TEMPERATURE = TagData(["A30"], "°C")
    HEATING_TEMPERATURE_SETPOINT = TagData(["A31"], "°C")
    ADAPT_HEATING = TagData(["I263"], writeable=True)
    STATE_SOURCEPUMP = TagData(["I51"], bit=0)
    STATE_HEATINGPUMP = TagData(["I51"], bit=1)
    STATE_COMPRESSOR = TagData(["I51"], bit=3)
    STATE_EXTERNAL_HEATER = TagData(["I51"], bit=5)
    HEATPUMP_TYPE = TagData(["I105"])
    SERIAL_NUMBER = TagData(["I114", "I115"])
    COMPRESSOR_ELECTRIC_CONSUMPTION_YEAR = TagData(["A444", "A445"], "kWh")
    SOURCEPUMP_ELECTRIC_CONSUMPTION_YEAR = TagData(["A446", "A447"], "kWh")
    ELECTRICAL_HEATER_ELECTRIC_CONSUMPTION_YEAR = TagData(["A448", "A449"], "kWh")
    HEATING_ENERGY_PRODUCED_YEAR = TagData(["A452", "A453"], "kWh")
    HOT_WATER_ENERGY_PRODUCED_YEAR = TagData(["A454", "A455"], "kWh")
    ELECTRICAL_POWER = TagData(["A25"], "kW")
    THERMAL_POWER = TagData(["A26"], "kW")
    COOLING_POWER = TagData(["A27"], "kW")
    FIRMWARE_VERSION = TagData(["I1"], read_function=TagData._parse_firmware)
    BUILD = TagData(["I2"])
    HARDWARE_REVISION = TagData(["I1718"])
    BIOS = TagData(["I3"], read_function=TagData._parse_bios)
    BIOS_DATE = TagData(["I4"], read_function=TagData._parse_bios_date)


class Ecotouch:
    """Class to control Waterkotte Ecotouch heatpumps."""

    auth_cookies = None

    def __init__(self, host):
        self.hostname = host
        self.language_dictionary = None

    def init_translations(self) -> Dict[str, Tuple[str, str, str]]:
        """initializes value-names: key: (de, en, fr)"""
        try:
            response = requests.get(
                f"http://{self.hostname}/easycon/js/dictionary.js",
                timeout=REQUEST_TIMEOUT,
            )
            if not response.ok:
                raise ConnectionException(
                    f"heatpump returned {response.status_code} {response.reason}"
                )
            TRANSLATION_REGEX = r'[^"]*'

            def replace_unicode(match: re.Match[str]) -> str:
                char_bytes = ord(match.group(1)).to_bytes(2, "little") + int(
                    match.group(2), 16
                ).to_bytes(2, "little")
                return char_bytes.decode("utf-16")

            def replace_x_code(match: re.Match[str]) -> str:
                in_str = match.group(1)
                char_bytes = int(in_str, 16).to_bytes(2, "little")
                replacement = char_bytes.decode("utf-16")
                return replacement

            text = re.sub(r"\\x([0-9a-fA-F]{2})", replace_x_code, response.text)
            text = re.sub(r"(\w)\\u(\d{4})", replace_unicode, text)

            translations: Dict[str, tuple] = {}
            matches = re.findall(
                rf'lng(?P<id>[\w\d]+)=\["(?P<de_text>{TRANSLATION_REGEX})","(?P<en_text>{TRANSLATION_REGEX})","(?P<fr_text>{TRANSLATION_REGEX})"]',
                text,
            )
            for match in matches:
                translations[match[0]] = (
                    match[1],
                    match[2],
                    match[3],
                )
            matches = re.findall(
                rf'lng(?P<id>[\w\d]+)=\["(?P<de_text>{TRANSLATION_REGEX})","(?P<en_text>{TRANSLATION_REGEX})"]',
                text,
            )
            for match in matches:
                translations[match[0]] = (
                    match[1],
                    match[2],
                    None,
                )

            matches = re.findall(
                rf'lng(?P<id>[\w\d]+)="(?P<de_text>{TRANSLATION_REGEX})"', text
            )
            for match in matches:
                translations[match[0]] = (
                    match[1],
                    match[1],
                    match[1],
                )

            matches = re.findall(r"lng(?P<id>[\w\d]+)=lng(?P<other_id>[\w\d]+)", text)
            for match in matches:
                if match[1] in translations.keys():
                    translations[match[0]] = translations[match[1]]
            return translations

        except (ConnectionError, OSError) as conn_eror:
            raise ConnectionException("could not connect to heatpump") from conn_eror

    def get_tag_description(self, tag: TagData, language_no=0) -> str:
        """returns the description of a tag
        0=DE
        1=EN
        2=FR"""
        if self.language_dictionary is None:
            self.language_dictionary = self.init_translations()
        key = tag.tags[0]
        if tag.bit is not None:
            key += f"_{tag.bit}"
        res = self.language_dictionary.get(key, (None, None, None))[language_no]
        if res == "":
            return None
        return res

    def _get_status_response(self, response):
        """extracts state from response"""
        match = re.search(r"^#([A-Z_]+)", response.text, re.MULTILINE)
        if match is None:
            raise InvalidResponseException("invalid response. could not read state")
        return match.group(1)

    hp_type_csv = None  # remember parsed csv data

    def decode_heatpump_series(self, heatpump_type: int) -> str:
        """Translates the heatpump type (number) to a human readable series string"""
        if self.hp_type_csv is None:
            result = requests.get(
                f"http://{self.hostname}/easycon/hpType.csv", timeout=REQUEST_TIMEOUT
            )
            if not result.ok:
                raise ConnectionException(
                    f"heatpump returned {result.status_code} {result.reason}"
                )

            lines = result.text.splitlines()
            hp_type_csv = [line.split(";") for line in lines]
        return hp_type_csv[heatpump_type][2]

    def login(self, username="waterkotte", password="waterkotte"):
        """performs a login. Has to be called before any other method."""
        args = {"username": username, "password": password}
        try:
            result = requests.get(
                f"http://{self.hostname}/cgi/login",
                params=args,
                timeout=REQUEST_TIMEOUT,
            )
            if not result.ok:
                raise ConnectionException("invalid result from server")
            if self._get_status_response(result) != "S_OK":
                raise AuthenticationException(
                    f"login error: {self._get_status_response(result)}"
                )
            self.auth_cookies = result.cookies
        except (ConnectionError, OSError) as conn_eror:
            raise ConnectionException("could not connect to heatpump") from conn_eror

    def read_value(self, tag: TagData):
        """reads a single value from heatpump"""
        res = self.read_values([tag])
        if tag in res:
            return res[tag]
        return None

    def write_values(self, kv_pairs: Dict[TagData, Any]):
        """writes values to heatpump"""
        to_write: Dict[str, str] = {}
        for tag, value in kv_pairs.items():
            if not tag.writeable:
                raise InvalidValueException("tried to write to an readonly field")
            to_write.update(tag.write_value(value))

        self._write_tags(to_write)

    def write_value(self, tag, value):
        """writes single value to heatpump"""
        self.write_values({tag: value})

    def read_values(self, tags: List[TagData]) -> Dict[TagData, Any]:
        """reads multiple values from heatpump"""
        e_tags = []
        for etag in tags:
            for wtag in etag.tags:
                e_tags.append(wtag)
        e_values = self._read_tags(e_tags)

        result = {}
        for tag in tags:
            str_vals = [e_values[e_tag] for e_tag in tag.tags]
            result[tag] = tag.parse_value(str_vals)
        return result

    def _read_tags(self, tags: List[TagData], results=None) -> Dict[TagData, str]:
        """reads a list of ecotouch tags"""
        if results is None:
            results = {}

        if len(tags) == 0:
            return results

        if len(tags) > MAX_NO_TAGS:
            results = self._read_tags(tags[MAX_NO_TAGS:], results)
        tags = tags[:MAX_NO_TAGS]

        args = {}
        args["n"] = len(tags)
        for i, tag in enumerate(tags):
            args[f"t{i+1}"] = tag
        result = requests.get(
            f"http://{self.hostname}/cgi/readTags",
            params=args,
            cookies=self.auth_cookies,
            timeout=REQUEST_TIMEOUT,
        )
        for tag in tags:
            match = re.search(
                rf"#{tag}\t(?P<status>[A-Z_]+)\n\d+\t(?P<value>\-?\d+)",
                result.text,
                re.MULTILINE,
            )
            if match is None:
                raise Exception("tag not found in response")
            val_str = match.group("value")
            results[tag] = val_str
        return results

    def _write_tags(self, to_write: Dict[str, str]):
        """writes <value> into the tag <tag>"""
        args = {"n": 1, "returnValue": "true"}
        for i, (tag, value) in enumerate(to_write.items()):
            args[f"t{i}"] = tag
            args[f"v{i}"] = value

        response = requests.get(
            f"http://{self.hostname}/cgi/writeTags",
            params=args,
            cookies=self.auth_cookies,
            timeout=REQUEST_TIMEOUT,
        )
