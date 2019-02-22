import ecotouch
from time import sleep
from ecotouch_tags import ecotouch_tag


wp = ecotouch.Ecotouch('192.168.2.11')

wp.login()

tags = [t for t in ecotouch_tag]

while True:
    result = wp.read_tags(tags)
    #    print('%s: %s' % (tag.identifier, str(wp.read_tags([tag]))))
    print('\n\n\n')
    sleep(3)
