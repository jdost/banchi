from . import models
from . import app, db
from . import errors
from .decorators import datatype, write_operation
from flask import request
import httplib

BASE_PATH = '/host/'


@app.endpoint(BASE_PATH)
@datatype
def hosts():
    ''' hosts - GET /host
    Returns an array of all the hosts
    '''
    return [host.__simple__() for host in models.Host.query.all()]


@app.get(BASE_PATH + "<host_name>/")
@datatype
def host_info(host_name=None):
    ''' host_info - GET /host/<host_name>
    Returns a more detailed set of information for the host specified by the
    `host_name` parameter, or BAD_REQUEST if no host exists with that name.
    '''
    if host_name:
        return models.Host.query.filter(
            models.Host.name == host_name).first().__full__()
    else:
        return httplib.BAD_REQUEST


@app.post(BASE_PATH)
@datatype
@write_operation
def create_host():
    ''' create_host - POST /host
        POST: name=<host_name>
              vlan=[<vlan_id>]
    Creates a host with the specified name and allocates IP addresses on each
    of the specified vlans and returns the simple listing for the host.  If
    an IP cannot be allocated due to limits, a PRECONDITION_FAILED will be
    returned, if a vlan does not exist, a BAD_REQUEST will be returned.
    '''
    name = request.form['name']
    vlans = request.form.getlist('vlan')

    if models.Host.query.filter(models.Host.name == name).count():
        return httplib.CONFLICT

    host = models.Host(name=name)
    db.session.add(host)

    for vlan_id in vlans:
        try:
            vlan = models.Vlan.query.filter(
                models.Vlan.number == int(vlan_id)).first()
            if not vlan:
                return httplib.BAD_REQUEST
            ip = models.Ip(number=vlan.get_next(), vlan=vlan, host=host)
            db.session.add(ip)
        except errors.FullVlanException:
            db.session.rollback()
            return httplib.PRECONDITION_FAILED

    return host.__simple__(), httplib.CREATED


@app.route(BASE_PATH + "<host_name>/", methods=["DELETE"])
@datatype
@write_operation
def delete_host(host_name=None):
    ''' delete_host - DELETE /host/<host_name>
    Attempts to find the host specified, if it exists, it and all of its IPs
    will be deleted and an ACCEPTED will be returned, if it doesn't exist, a
    NOT_FOUND will be returned.
    '''
    host = models.Host.query.filter(models.Host.name == host_name).first()
    if not host:
        return httplib.NOT_FOUND

    db.session.delete(host)
    return httplib.ACCEPTED
