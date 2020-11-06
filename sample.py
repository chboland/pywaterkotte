from pywaterkotte import Ecotouch, EcotouchTag
from time import sleep


wp = Ecotouch('waterkotte.lan')

wp.login()

tags = [t for t in EcotouchTag]

while True:
    result = wp.read_values(tags)
    for k,v in result.items():
        print("\t%s:\t%s" % (k,v))
    print('\n'*3)
    sleep(3)

