import ecotouch
from ecotouch_tags import ecotouch_tag


wp = ecotouch.Ecotouch('192.168.2.11')

wp.login()
wp.read_tag(ecotouch_tag.TEMPERATURE_OUTSIDE)
wp.read_tag(ecotouch_tag.TEMPERATURE_OUTSIDE_1H)
wp.read_tag(ecotouch_tag.TEMPERATURE_OUTSIDE_24H)
