from pywaterkotte import Ecotouch, EcotouchTags
from time import sleep


wp = Ecotouch("192.168.2.22")

wp.login()

tags = [
    EcotouchTags.COMPRESSOR_ELECTRIC_CONSUMPTION_YEAR,
    EcotouchTags.COMPRESSOR_ELECTRICAL_POWER,
]

while True:
    result = wp.read_values(tags)
    for k, v in result.items():
        print(f"\t{k.tags}:\t{v} {k.unit}")
    sleep(3)
