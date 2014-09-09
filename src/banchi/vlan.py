from . import models
from . import app, db
from .utils import cidr2mask
from .decorators import datatype, write_operation
from flask import request
import httplib

BASE_PATH = '/vlan/'


@app.endpoint(BASE_PATH)
@datatype
def vlans():
    ''' vlans - GET /vlan
    Returns an array of all the vlans
    '''
    return [vlan.__simple__() for vlan in models.Vlan.query.all()]


@app.get(BASE_PATH + "<int:vlan_id>/")
@app.get(BASE_PATH + "<vlan_name>/")
@datatype
def vlan_info(vlan_id=None, vlan_name=None):
    ''' vlan_info - GET /vlan/<vlan id>
        vlan_info - GET /vlan/<vlan_name>
        GET:
    Returns a detailed listing of the specified vlan
    '''
    if vlan_id:
        return models.Vlan.query.filter_by(number=vlan_id).first().__full__()
    elif vlan_name:
        return models.Vlan.query.filter_by(name=vlan_name).first().__full__()
    else:
        return httplib.BAD_REQUEST


@app.post(BASE_PATH)
@datatype
@write_operation
def create_vlan():
    number = int(request.form['number'], 10)
    name = request.form['name']
    mask = request.form['mask']

    if models.Vlan.query.filter_by(number=number).count() or \
            models.Vlan.query.filter_by(name=name).count():
        return httplib.CONFLICT

    vlan = models.Vlan(
        name=name, number=number, cidr=cidr2mask(mask),
        length=mask.split("/")[1]
    )

    db.session.add(vlan)
    return vlan.__simple__(), httplib.CREATED
