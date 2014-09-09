from . import models
from . import app
from .utils import ip2int, isip
from .decorators import datatype
from flask import request
import httplib


@app.endpoint("/query/")
@datatype
def find():
    ''' find - GET /query
        GET: ip=<ip_string>
             host=<hostname>
    Tries to retrieve the value associated with the string provided, including
    IP addresses and their names or ip names and their addresses. If there is
    nothing for the result a NOT_FOUND is returned, if the value is malformed
    (such as a non IP for the IP string) a BAD_REQUEST is returned.
    '''
    ip = request.args.get('ip')
    if ip:
        return find_ip(ip)
    host = request.args.get('hostname')
    if host:
        return find_host(host)


def find_ip(ip):
    if not isip(ip):
        return httplib.BAD_REQUEST
    ip = models.Ip.query.filter_by(number=ip2int(ip)).first()
    return ip.__tuple__()[0] if ip else httplib.NOT_FOUND


def find_host(hostname):
    if not len(hostname):
        return httplib.BAD_REQUEST
    host = models.Host.query.filter_by(name=hostname).first()
    return host.__full__() if host else httplib.NOT_FOUND
