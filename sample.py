""" Usage sample for lib """
from pywaterkotte import Ecotouch, EcotouchTag
from time import sleep
import asyncio

wp = Ecotouch("waterkotte.local")

asyncio.run(wp.login())

# tags = [t for t in EcotouchTag]
tags = [EcotouchTag.ENABLE_COOLING, EcotouchTag.ENABLE_HEATING, EcotouchTag.ENABLE_PV, EcotouchTag.ENABLE_WARMWATER , EcotouchTag.STATE_WATER, EcotouchTag.STATE_COOLING, EcotouchTag.STATE_SOURCEPUMP, EcotouchTag.STATUS_HEATING, EcotouchTag.STATUS_WATER, EcotouchTag.STATUS_COOLING]
# print(tags)
# tag = EcotouchTag.STATUS_COOLING
# result = wp.read_value(tag)
# print(result)
# while True:

result = asyncio.run(wp.read_values(tags))
for k, v in result.items():
    print("\t%s:\t%s %s Status: %s" % (k, v['value'], k.unit, v['status']))
# print("\n" * 3)
#    sleep(3)
