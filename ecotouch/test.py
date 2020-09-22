import ecotouch
from time import sleep

wp = ecotouch.Ecotouch('192.168.2.148')

wp.login()

tags = [t for t in ecotouch.EcotouchTag]

while True:
    result = wp.read_values(tags)
    for k,v in result.items():
        print("\t%s:\t%s" % (k,v))
    print('\n'*3)
    sleep(3)
