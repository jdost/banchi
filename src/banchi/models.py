from .utils import int2ip
from . import errors
from . import db
from flask import url_for


class Ip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    number = db.Column(db.Integer)
    vlan_id = db.Column(db.Integer, db.ForeignKey('vlan.id'))
    host_id = db.Column(db.Integer, db.ForeignKey('host.id'))

    __mapper_args__ = {
        "confirm_deleted_rows": False
    }

    def __tuple__(self):
        name = "{}_{}_ip".format(self.host.name, self.vlan.name)
        return (name, str(self))

    def __str__(self):
        return int2ip(self.number)


class Vlan(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    cidr = db.Column(db.Integer)
    number = db.Column(db.Integer, unique=True)
    length = db.Column(db.Integer)
    ips = db.relationship("Ip", backref='vlan', cascade="delete")

    def get_next(self):
        mask = ~ self.cidr
        allocated = set(map(lambda ip: ip.number & mask, self.ips))
        for i in range(0, 1 << (32 - self.length)):
            if i not in allocated:
                return i | self.cidr

        raise errors.FullVlanException(
            "{} addresses allocated on {}/{}".format(len(self.ips),
                                                     int2ip(self.cidr),
                                                     self.length))

    def __str__(self):
        return str(self.number)

    def __simple__(self):
        return {
            "name": self.name,
            "number": self.number,
            "range": "{}/{}".format(int2ip(self.cidr), self.length),
            "url": url_for("vlan_info", vlan_name=self.name),
        }

    def __full__(self):
        return {
            "name": self.name,
            "number": self.number,
            "range": "{}/{}".format(int2ip(self.cidr), self.length),
            "hosts": [host.name for host in self.hosts],
        }


class Host(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False, unique=True)
    ips = db.relationship("Ip", backref='host', cascade="delete")
    vlans = db.relationship("Vlan", secondary="ip", backref="hosts")

    def __simple__(self):
        return {
            "name": self.name,
            "vlans": [vlan.number for vlan in self.vlans],
            "url": url_for("host_info", host_name=self.name),
        }

    def __full__(self):
        return {
            "name": self.name,
            "ips": dict(map(lambda ip: (str(ip.vlan), str(ip)), self.ips)),
        }
