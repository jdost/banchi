from flask.ext.testing import TestCase
from banchi import app, db
import httplib
import json

app.config['TESTING'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = "sqlite:///:memory:"
app.debug = True

db.init_app(app)


class TestBase(TestCase):
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'

    json_header = [("Accept", "application/json")]

    def create_app(self):
        return app

    def setUp(self):
        db.create_all()
        self.session = db.session

        self.client = self.app.test_client()
        response = self.client.get("/", headers=self.json_header)
        endpoints = json.loads(response.data)
        for (name, v) in endpoints.items():
            setattr(self, "url_" + name, v['url'])

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def assertHasStatus(self, response, status, msg=None):
        ''' TestBase::assertHasStatus
        wrapper for tests to check if a response returns the correct HTTP
        status code
        params:
            response: <Response Object> returned from a test_client request
            status: <Int> for the expected status code or a <List> of the
                accepted status codes
            msg: <String> message to give to the assert call (default message
                is generated)
        '''
        if isinstance(status, list):
            if not msg:
                msg = "Response returned {} (expeded one of: {})".format(
                    response.status_code, str(status))
                self.assertIn(response.status_code, status, msg)
        else:
            if not msg:
                msg = "Response returned {} (expected: {})".format(
                    response.status_code, status)
            self.assertEqual(response.status_code, status, msg)

    def create_vlan(self, number=20, name="test", mask="100.110.120.0/24"):
        ''' ::create_vlan
        Helper method to request the creation of a new vlan.
        '''
        vlan = {
            'number': number,
            'name': name,
            'mask': mask,
        }
        response = self.client.post(self.url_vlans, data=vlan,
                                    headers=self.json_header)
        self.assertHasStatus(response, httplib.CREATED)
        return json.loads(response.data)

    def create_host(self, name="test", vlans=[]):
        ''' ::create_host
        Helper method to request the creation of a new host attached to
        specified vlans (none by default).
        '''
        host = {
            'name': name,
            'vlan': vlans
        }
        response = self.client.post(self.url_hosts, data=host,
                                    headers=self.json_header)
        self.assertHasStatus(response, httplib.CREATED)
        return json.loads(response.data)

    def get_hosts(self):
        ''' ::get_hosts
        Helper method to request the list of hosts.
        '''
        response = self.client.get(self.url_hosts, headers=self.json_header)
        self.assertHasStatus(response, httplib.OK)
        return json.loads(response.data)
