# from pywaterkotte.ecotouch import (
#     Ecotouch,
#     EcotouchTag,
#     InvalidResponseException,
#     StatusException,
# )
import asyncio


# from pywaterkotte.detect import (
#     ECOTOUCH,
#     EASYCON,
#     waterkotte_detect,
# )  # , EASYCON, ECOTOUCH
from easycon import Easycon, EcotouchTag  # pylint: disable=import-error

# from pywaterkotte.ecotouch import EcotouchTag

# import responses
# import pytest
# from datetime import datetime

HOSTNAME = "localhost:8000"
USERNAME = "waterkotte"
PASSWORD = "waterkotte"
EASYCON = "EASYCON"

loop = asyncio.get_event_loop()
# res = loop.run_until_complete(waterkotte_detect(HOSTNAME, USERNAME, PASSWORD))

# print(res)
res = EASYCON
if res == EASYCON:
    wp = Easycon(HOSTNAME)
    tags = [
        EcotouchTag.ENABLE_COOLING,
        EcotouchTag.ENABLE_HEATING,
        EcotouchTag.ENABLE_PV,
        EcotouchTag.ENABLE_WARMWATER,
        EcotouchTag.STATE_WATER,
        EcotouchTag.STATE_COOLING,
        EcotouchTag.STATE_SOURCEPUMP,
        EcotouchTag.STATUS_HEATING,
        EcotouchTag.STATUS_WATER,
        EcotouchTag.STATUS_COOLING,
    ]
    # print(tags)
    # tag = EcotouchTag.STATUS_COOLING
    # result = wp.read_value(tag)
    # print(result)
    # while True:

    # result = asyncio.run(wp.read_values(tags))
    # for k, v in result.items():
    #     print("\t%s:\t%s %s Status: %s" % (k, v["value"], k.unit, v["status"]))

    result = asyncio.run(wp.write_values([(EcotouchTag.ENABLE_COOLING, "off")]))
    # Collection[Tuple[EcotouchTag, Any]]
    print(result)
