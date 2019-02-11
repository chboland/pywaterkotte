import ecotouch
from time import sleep
from ecotouch_tags import ecotouch_tag


wp = ecotouch.Ecotouch('192.168.2.11')

wp.login()

while True:
    for tag in ecotouch_tag:
        print('%s: %s' % (tag.identifier, str(wp.read_tag(tag))))
    print('\n\n\n')
    sleep(3)
