from base import TestBase
from banchi import models, errors


class TestModels(TestBase):
    cidr = 256

    def vlan(self, name="foo", number=1):
        ''' ::vlan
        Creates a simple Vlan model object, used to remove as much boilerplate
        from tests as possible.
        '''
        return models.Vlan(name=name, cidr=self.cidr, number=number, length=8)

    def test_vlan_ip_relationship(self):
        ''' vlans and ips can reference each other via relationship
        Creates a vlan and ip and checks that each can reference the other via
        the defined relationship.
        '''
        vlan = self.vlan()
        self.session.add(vlan)

        ip = models.Ip(number=123, vlan=vlan)
        self.session.add(ip)

        self.assertEqual(len(vlan.ips), 1)
        self.assertEqual(vlan.ips[0].vlan_id, vlan.id)

    def test_vlan_ip_collection(self):
        ''' vlans can retrieve their full set of allocated ips
        Creates a vlan and adds some ips, then checks that the model can
        retrieve the full collection of ips for that vlan.
        '''
        vlan = self.vlan(number=20)
        self.session.add(vlan)

        for i in range(7):
            ip = models.Ip(number=i, vlan=vlan)
            self.session.add(ip)

        self.assertEqual(len(vlan.ips), 7)

        ip = models.Ip(number=0)
        self.session.add(ip)

        self.assertEqual(len(vlan.ips), 7)

    def test_ip_allocation(self):
        ''' vlan can find available ips
        Creates a vlan and requests IP addresses from the vlan, checking
        that the returned value is as expected.
        '''
        vlan = self.vlan()
        self.session.add(vlan)

        self.assertEqual(self.cidr, vlan.get_next())

        for i in range(0, 5, 2):
            ip = models.Ip(number=(i & self.cidr), vlan=vlan)
            self.session.add(ip)

        self.assertEqual(self.cidr + 1, vlan.get_next())

    def test_full_vlan(self):
        ''' full vlan raises error when asking for new IP
        Creates a small vlan and fills up the IP range, then requests another
        address and receives an error.
        '''
        vlan = models.Vlan(name="small", cidr=256, number=1, length=30)
        self.session.add(vlan)

        for i in range(4):
            ip = models.Ip(number=i, vlan=vlan)
            self.session.add(ip)

        with self.assertRaises(errors.FullVlanException):
            vlan.get_next()

    def test_host_vlan_relationship(self):
        ''' vlans and hosts are related via ips
        A host with ips attached to reference the associated VLANs properly
        '''
        vlan = self.vlan()
        self.session.add(vlan)
        host = models.Host(name="test")
        self.session.add(host)

        ip = models.Ip(number=257, vlan=vlan, host=host)
        self.session.add(ip)

        vlan = self.session.query(models.Vlan).first()
        self.assertEqual(len(vlan.hosts), 1)
        self.assertEqual(vlan.hosts[0], host)
        self.assertEqual(len(host.vlans), 1)
        self.assertEqual(host.vlans[0], vlan)
