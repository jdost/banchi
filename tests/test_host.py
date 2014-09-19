from base import TestBase
import json
import httplib


class HostTest(TestBase):
    ''' HostTest
    Tests the various routes and business logic related to creating and
    managing hosts.
    '''

    def get_host(self, host):
        ''' ::get_host
        Helper method to retrieve a full set of host information.
        '''
        response = self.client.get(host["url"], headers=self.json_header)
        self.assertHasStatus(response, httplib.OK)
        return json.loads(response.data)

    def query_ip(self, ip):
        ''' ::query_ip
        Helper method to query the IP name for a given IP
        '''
        response = self.client.get(self.url_find, query_string={"ip": ip},
                                   headers=self.json_header)
        return response.data, response.status_code

    def query_host(self, host):
        ''' ::query_host
        Helper method to query for the host(s) with a given hostname
        '''
        response = self.client.get(self.url_find, headers=self.json_header,
                                   query_string={"hostname": host})
        return json.loads(response.data), response.status_code

    def test_create_host(self):
        ''' a created host shows up on subsequent requests
        Creating a host and then requesting a list of hosts has the recently
        created host in the list.
        '''
        host = self.create_host()
        hosts = self.get_hosts()
        self.assertEqual(len(hosts), 1)
        self.assertEqual(hosts[0], host)

    def test_host_with_vlans(self):
        ''' a created host with vlans gets IPs assigned
        Creating a host with a list of vlans should populate an IP for each of
        the vlans.
        '''
        for i in range(4):
            self.create_vlan(number=i, name="vlan{}".format(i))

        response = self.client.get(self.url_vlans, headers=self.json_header)
        self.assertHasStatus(response, httplib.OK)
        vlans = json.loads(response.data)
        self.assertEqual(len(vlans), 4)

        host = self.create_host(vlans=[vlan["number"] for vlan in vlans])
        self.assertEqual(len(host["vlans"]), 4)

        host = self.get_host(host)
        self.assertEqual(len(host["ips"]), 4)
        self.assertTrue(all(host["ips"].values()))

    def test_conflict(self):
        ''' creating a host with an already used named results in an error
        Creating a host with a name that is already in use results in a
        CONFLICT error.
        '''
        host_data = {"name": "conflict_test", "vlan": []}
        self.create_host(name=host_data["name"])
        response = self.client.post(self.url_hosts, data=host_data,
                                    headers=self.json_header)
        self.assertHasStatus(response, httplib.CONFLICT)

    def test_find(self):
        ''' querying with an ip returns proper strings
        Creating a host and then using the find path with existing and non IPs
        results in expected values.
        '''
        vlan = self.create_vlan(name="vlan15", number=15)
        host = self.create_host(name="test", vlans=[vlan["number"]])

        host_full = self.get_host(host)
        v, _ = self.query_ip(host_full["ips"].values()[0])
        self.assertEqual(v, "test_vlan15_ip")

        _, r = self.query_ip("256.256.256.256")
        self.assertEqual(r, httplib.NOT_FOUND)

        _, r = self.query_ip("notanip")
        self.assertEqual(r, httplib.BAD_REQUEST)

    def test_find_multiple(self):
        ''' querying with a hostname that returns multiple hosts
        Creating multiple hosts with similar names and querying for the common
        part of the name returns all of the hosts.
        '''
        for i in range(4):
            self.create_host(name="test" + str(i))

        hosts, _ = self.query_host("test")
        self.assertEqual(len(hosts), 4)

    def test_delete(self):
        ''' deleting a host cleans up the host and ips
        Creates a host with associated IPs, then removes the host.  The IPs
        should be removed (and available).
        '''
        self.create_vlan(number=7, name="vlan7")
        host = self.create_host(vlans=[7])

        self.assertEqual(len(self.get_hosts()), 1)
        response = self.client.delete(host["url"])
        self.assertHasStatus(response, httplib.ACCEPTED)

        self.assertEqual(len(self.get_hosts()), 0)
