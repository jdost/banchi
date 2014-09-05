import re

ip_regex = re.compile(r"^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$")


def ip2int(ip):
    if not isip(ip):
        return None
    octs = map(int, ip.split('.'))
    return reduce(lambda i, o: (i << 8) + o, octs)


def int2ip(i):
    return '.'.join(map(str, [
        i >> 24,
        (i >> 16) & 255,
        (i >> 8) & 255,
        i & 255
    ]))


def isip(i):
    return bool(ip_regex.match(i))


def cidr2mask(cidr):
    ip, mask_length = cidr.split("/")

    i = ip2int(ip)
    mask = (~ 0) << (32 - int(mask_length))

    return i & mask
