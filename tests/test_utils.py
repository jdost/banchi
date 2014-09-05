import unittest
from banchi import utils


class UtilsTest(unittest.TestCase):
    ''' UtilsTest
    Test various utility functions written for the application.
    '''

    def test_ip_conversion(self):
        ''' confirms that the ip conversion functions handle various forms.
        The functions convert ip strings into integers, which is useful for
        the CIDR masking along with SQL storage.  Then converts them back into
        the common string.
        '''
        ips = [
            "127.0.0.1",
            "255.255.255.255",
            "8.8.8.8",
            "0.0.0.0",
            "10.11.12.13"
        ]

        for ip in ips:
            i = utils.ip2int(ip)
            self.assertEqual(ip, utils.int2ip(i))

    def test_cidr_mask(self):
        ''' check the CIDR mask creation
        The function to generate CIDR bitmasks is used to handle IP discovery
        constrained by a CIDR range mask, allowing for integer based discovery
        with the common definition format.
        '''
        cidrs = [
            ("255.255.255.255/24", "1111 1111 1111 1111 1111 1111 0000 0000"),
            ("10.11.12.13/29", "0000 1010 0000 1011 0000 1100 0000 1000")
        ]

        cidrs = map(lambda (x, y): (x, filter(lambda x: x in "10", y)), cidrs)
        for (cidr, b) in cidrs:
            self.assertEqual(int(b, 2), utils.cidr2mask(cidr))

    def test_ip_check(self):
        ''' confirms the ip check works for various IPs
        '''
        ip_tests = [
            "127.0.0.1",
            "0.0.0.0",
            "255.255.255.255",
        ]

        for test in ip_tests:
            self.assertTrue(utils.isip(test))

        bad_tests = [
            "not an ip",
            "AA.BB.CC.DD",
            "127.O.O.1",
        ]

        for test in bad_tests:
            self.assertFalse(utils.isip(test))
