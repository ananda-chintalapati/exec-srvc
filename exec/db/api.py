from db.sqlalchemy import api as IMPL

_BACKEND_MAPPING = {'sqlalchemy': 'mgmt.db.sqlalchemy.api'}

def get_service_list():
    return IMPL.get_service_list()

def get_service_status(service_name):
    return IMPL.get_service_status(service_name)

def get_dependent_service_list(service_name):
    return IMPL.get_dependent_service_list(service_name)

def update_service_status(service_name):
    return IMPL.update_service_status(service_name)

def update_dependent_service_list(service_name, **kw):
    return IMPL.update_dependent_service_list(service_name, **kw)

def create_service(service_name, **kw):
    return IMPL.create_service(service_name, **kw)

def create_request(**req):
    return IMPL.create_request(**req)

def update_request(**req):
    return IMPL.update_request(**req)

def get_request(request_id):
    return IMPL.get_request(request_id)

def get_all_requests():
    return IMPL.get_all_requests()
