import pywaterkotte
from time import sleep

wp = pywaterkotte.Ecotouch('waterkotte.lan')

wp.login()

tags = [t for t in pywaterkotte.EcotouchTag]

while True:
    result = wp.read_values(tags)
    for k,v in result.items():
        print("\t%s:\t%s" % (k,v))
    print('\n'*3)
    sleep(3)
