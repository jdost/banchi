import json
import datetime
import time
from functools import wraps
from flask import request, make_response, session, render_template, Flask, \
    url_for
from werkzeug import BaseResponse
import httplib


def intersect(a, b):
    ''' intersect
    Returns a boolean if an item in <list> a is also in <list> b
    '''
    return reduce(lambda x, y: x or y, [i in a for i in b])


def html_base():
    ''' html_base
    Generates a general base set of information for the HTML page rendering.
    '''
    return {
        "logged_id": 'id' in session
    }


class BanchiFlask(Flask):
    ''' BanchiFlask:
    This is just an expansion on the Flask app class to add fancier decorators
    to the app
    '''
    def __init__(self, *args, **kwargs):
        self.endpoints = {}  # This is the storage property for the endpoints

        self.__dict__.update({
            method: self.__shorthand(methods=[method.upper()])
            for method in ["get", "post", "put"]})

        return Flask.__init__(self, *args, **kwargs)

    def endpoint(self, *args, **kwargs):
        ''' endpoint:
        Stores an alias for a specific endpoint of the application, this is
        used for the dynamic discovery of the application.
        '''
        def decorator(f):
            self.endpoints[f.__name__] = {
                'url': args[0]
            }
            return self.route(*args, **kwargs)(f)
        return decorator

    def __shorthand(self, **defaults):
        ''' decorator helper method:
        Helps the create shorthand decorators for making the method setting
        simpler.  Just used to override the kwargs of a route to some
        established set.
        '''

        def new_route(*args, **kwargs):
            kwargs.update(defaults)
            return lambda f: self.route(*args, **kwargs)(f)
        return new_route


class JSONEncoder(json.JSONEncoder):
    ''' JSONEncoder
    An extended json.JSONEncoder, used to customize the encoding of the data
    packets (dicts or lists) into JSON, just catches various types and beyond
    the basic types and handles their JSON representation (examples are things
    like python's datetime).
    '''
    DATE_FORMATS = {
        'iso': lambda date: date.isoformat(),
        'epoch': lambda date: time.mktime(date.timetuple())
    }

    def date_format(self, obj):
        if 'date_format' not in session:
            return str(obj)
        if session['date_format'] not in self.DATE_FORMATS:
            return obj.strftime(session['date_format'])
        return self.DATE_FORMATS[session['date_format']](obj)

    def default(self, obj):
        if isinstance(obj, datetime.datetime):  # datetime used for dates
            return self.date_format(obj)
        return json.JSONEncoder.default(self, obj)


JSON_KWARGS = {
    "cls": JSONEncoder,
    "separators": (',', ':')
}


def datatype(template=None):
    ''' datatype decorator:
    This decorator function is used to handle formatting and packaging a
    response coming out of a handler.  It will handle different scenarios and
    produce the proper format of output.  If the output of the route is a
    dictionary, it is assumed to be a data packet and will be formatted based
    on the HTTP Accept header, if it is a number, it is treated like a HTTP
    status code.

    argument(optional) template file to render html requests with

    ex:
        @datatype('some_function.html')
        @app.route('/some/path')
        def some_function():  # this will be converted into a proper response
            return { "foo": "bar" }
    '''
    mimetypes = {
        "application/json": lambda d: json.dumps(d, **JSON_KWARGS)
    }
    if type(template) is str:
        mimetypes["text/html"] = lambda d: \
            render_template(template, **dict(d.items() + html_base().items()))
    default = 'application/json'

    def decorator(func):
        @wraps(func)
        def decorated_function(*args, **kwargs):
            request.is_html = request.accept_mimetypes.accept_html
            data = func(*args, **kwargs)
            status_code = httplib.OK
            if type(data) is tuple:  # if multiple, break apart
                status_code = data[1]
                data = data[0]

            if type(data) is int:  # if int, treat it like a status code
                response = make_response("", data)
            elif type(data) is dict or type(data) is list:
                # if it is a dict or list, treat like data packet
                callback = request.args.get('callback', False)
                if callback:  # if has a callback parameter, treat like JSONP
                    data = str(callback) + "(" + \
                        mimetypes['application/json'](data) + ");"
                    response = make_response(data, status_code)
                    response.mimetype = 'application/javascript'
                else:  # Non-JSONP treatment
                    best = request.accept_mimetypes. \
                        best_match(mimetypes.keys())
                    data = mimetypes[best](data) if best \
                        else mimetypes[default](data)
                    response = make_response(data, status_code)
                    response.mimetype = best if best else default
            elif isinstance(data, BaseResponse):  # if it is a Response, use it
                response = data
            else:  # otherwise, treat it like raw data
                response = make_response(data, status_code)

            return response
        return decorated_function

    if hasattr(template, '__call__'):  # if no template was given
        return decorator(template)
    else:
        return decorator


def paginate(func):
    ''' paginate decorator:
    This decorator function is used to handle the pagination of long lists of
    models.  It pulls the page count and page size from either the request
    arguments or the session and passes them into the view function.  It then
    adds the 'Link' header to the response.

    Assumes the wrapped function takes kwargs of 'page' and 'per_page' to
    handle the limiting and offsetting of the query.
    '''
    @wraps(func)
    def decorated_function(*args, **kwargs):
        page = int(request.args.get('page', 0))
        per_page = request.args.get('per_page', session.get('page_size', 25))

        kwargs['page'] = page
        kwargs['per_page'] = int(per_page)

        links = []
        vargs = request.view_args.copy()
        if 'per_page' in request.args:
            vargs['per_page'] = per_page

        if page > 0:
            vargs['page'] = page - 1
            links.append(
                "<" + url_for(request.endpoint, **vargs) + ">; rel=\"prev\"")

        vargs['page'] = page + 1
        links.append(
            "<" + url_for(request.endpoint, **vargs) + ">; rel=\"next\"")

        response = func(*args, **kwargs)
        response.headers.add('Link', ", ".join(links))

        return response

    return decorated_function


def write_operation(func):
    ''' write operation decorator:
    Designates a route that is considered a write operation, handles committing
    the operations performed during the requests.
    '''
    from . import db

    @wraps(func)
    def decorated_function(*args, **kwargs):
        response = func(*args, **kwargs)
        db.session.commit()
        return response

    return decorated_function
