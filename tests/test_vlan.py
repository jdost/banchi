from base import TestBase
import json
import httplib


class VlanTest(TestBase):
    ''' VlanTest
    Tests the various routes and business logic related to viewing and
    managing the vlans.
    '''

    def get_vlans(self):
        ''' ::get_vlans
        Helper method to request the list of vlans.
        '''
        response = self.client.get(self.url_vlans,
                                   headers=self.json_header)
        self.assertHasStatus(response, httplib.OK)
        return json.loads(response.data)

    def test_create_vlan(self):
        ''' create a vlan
        Create a vlan and ensure it shows up in subsequent queries.
        '''
        vlan = self.create_vlan(number=35)
        self.assertEqual(vlan['number'], 35)

        vlans = self.get_vlans()
        self.assertEqual(len(vlans), 1)
        self.assertEqual(vlans[0]['number'], 35)

    def test_conflict(self):
        ''' creating a conflicting vlan results in an error
        Creates another vlan with the same name ornumber, returns the
        appropriate error code.
        '''
        vlan_data = {
            'number': 42,
            'name': "foo",
            'mask': "10.11.12.0/24",
        }
        self.create_vlan(number=vlan_data["number"])
        response = self.client.post(self.url_vlans,
                                    data=vlan_data, headers=self.json_header)
        self.assertHasStatus(response, httplib.CONFLICT)

        response = self.client.post(self.url_vlans,
                                    data=vlan_data, headers=self.json_header)
        self.assertHasStatus(response, httplib.CONFLICT)

    def test_full_vlan(self):
        ''' creating host with a full vlan results in an error
        Creates a vlan with a low range and fills it, then attempts to create
        a host with the full vlan and makes sure it results in an error and the
        host is not created.
        '''
        vlan = self.create_vlan(mask="10.10.10.126/31")
        for i in range(2):
            self.create_host(name="host{}".format(i), vlans=[vlan["number"]])

        host_data = {'name': 'fullhost', 'vlan': [vlan["number"]]}
        response = self.client.post(self.url_hosts, data=host_data,
                                    headers=self.json_header)
        self.assertHasStatus(response, httplib.PRECONDITION_FAILED)

        hosts = self.get_hosts()
        self.assertEqual(len(hosts), 2)

    def test_delete_vlan(self):
        ''' deleting a vlan removes the vlan and associated ips
        Creates a vlan and an associated host, then removes the vlan, the host
        should no longer have ips for the vlan.
        '''
        vlan = self.create_vlan()
        host = self.create_host(vlans=[vlan["number"]])
        self.assertEqual(len(host["vlans"]), 1)

        response = self.client.delete(vlan["url"])
        self.assertHasStatus(response, httplib.ACCEPTED)
        self.assertEqual(len(self.get_vlans()), 0)

        response = self.client.get(host["url"])
        self.assertHasStatus(response, httplib.OK)
        host = json.loads(response.data)
        self.assertEqual(len(host['ips']), 0)
