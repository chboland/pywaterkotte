from pywaterkotte import Ecotouch, EcotouchTags

from time import sleep


wp = Ecotouch("192.168.2.22")

wp.login()

tags = [
    EcotouchTags.FIRMWARE_VERSION,
    EcotouchTags.BUILD,
    EcotouchTags.HARDWARE_REVISION,
    EcotouchTags.BIOS,
    EcotouchTags.BIOS_DATE,
]

while True:
    result = wp.read_values(tags)
    for k, v in result.items():
        unit = k.unit if k.unit is not None else ""
        print(f"\t{k.tags}:\t{v} {unit}")
    sleep(3)
