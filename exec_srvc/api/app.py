import json
import os
import jinja2

from flask import Flask, jsonify, request, render_template
from service import JenkinsManager as Jenkins
from service import RallyManager as Rally

app = Flask(__name__)
app.jinja_loader = jinja2.FileSystemLoader('../templates')

CLOUD_REQ_DATA = ["auth_url", "username", "password", "project_name"]
JENKINS_REQ_DATA = ["host", "port", "user", "passwd", "tool"]
TOOL_REQ_DATA = ["host_ip", "rally_user", "rally_pass", "cloud_data"]

def get_file(dir, filename):  # pragma: no cover
    try:
        src = os.path.join(dir, filename)
        return open(src).read()
    except IOError as exc:
        return str(exc)

@app.route('/')
def hello():
    return "Welcome to OpenStack test package"


@app.route('/os_test')
def welcome():
    file = get_file('../templates','index.html')
    return render_template('index.html')

def _build_trigger_job(req_data):
    jenkins = _build_jenkins(req_data)
    print 'Is Jenkins running? %r ' % jenkins.verify_jenkins_status()
    if not jenkins.verify_jenkins_status():
        response = jsonify("Jenkins not found")
        response.status_code = 404
        raise response
    job_name = jenkins.create_job(req_data.get('tool'), req_data.get('action'))
    print '%s created' % job_name
    jenkins.trigger_job(req_data.get('tool'), req_data.get('action'), req_data)
    return job_name


@app.route('/jenkins/trigger', methods=['POST'])
def trigger_jenkins():
    print 'Form data %r ' % request.data
    req_data = request.data
    job_name = _build_trigger_job(req_data)
    return job_name


@app.route('/jenkins/ui/trigger', methods=['GET','POST'])
def trigger_jenkins_from_html():
    form_data = json.dumps(request.form)
    data = json.loads(form_data)
    print "UI Form data %r " % data
    req_data = {}
    req_data['host'] = data['host']
    req_data['port'] = data['port']
    req_data['user'] = data['user']
    req_data['passwd'] = data['passwd']
    req_data['auth_token'] = data['auth_token']
    req_data['tool'] = data['tool']
    req_data['action'] = data['action']

    req_data['tool_data'] = {}
    req_data['tool_data']['host_ip'] = data['host_ip']
    req_data['tool_data']['rally_user'] = data['rally_user']
    req_data['tool_data']['rally_pass'] = data['rally_pass']
    req_data['tool_data']['test_target'] = data['test_target']
    req_data['tool_data']['influx_url'] = data['influx_url']
    req_data['tool_data']['test_target_value'] = data['test_target_value']
    req_data['tool_data']['influx_db'] = data['influx_db']

    req_data['tool_data']['cloud_data'] = {}
    req_data['tool_data']['cloud_data']['auth_url'] = data['auth_url']
    req_data['tool_data']['cloud_data']['cloud_user'] = data['cloud_user']
    req_data['tool_data']['cloud_data']['cloud_pass'] = data['cloud_pass']
    req_data['tool_data']['cloud_data']['project_name'] = data['project_name']
    req_data['tool_data']['cloud_data']['test_name'] = data['test_name']
    req_data['tool_data']['cloud_data']['release'] = data['release']

    print 'Request data %r ' % req_data
    job_name = _build_trigger_job(req_data)
    msg = "<html> <h3>Job %s created and triggered successfully <br/>" % job_name
    msg += "\n Test execution is in progress <br/>"
    msg += "\n Results will be available at <a>http://192.168.20.137:3000/dashboard/db/new-dashboard</a></html>"
    return msg

def _build_jenkins(data):
    jenkins_url = data.get('host')
    jenkins_port = data.get('port')
    jenkins_user = data.get('user')
    jenkins_pass = data.get('passwd')
    jenkins_auth_token = data.get('auth_token')
    tool = data.get('tool')
    _validate_request(data, JENKINS_REQ_DATA)
    objc = None
    if 'rally' == tool.lower():
        objc = build_rally(data.get('tool_data'))
    return Jenkins(jenkins_url, jenkins_port, jenkins_user, jenkins_pass, jenkins_auth_token, objc)


def build_rally(request_json):
    rally_host = request_json.get('host_ip')
    rally_user = request_json.get('rally_user')
    rally_pass = request_json.get('rally_pass')
    cloud_json = request_json.get('cloud_data')
    _validate_request(request_json, TOOL_REQ_DATA)
    rally = Rally(rally_host, rally_user, rally_pass, cloud_json)
    return rally


def _validate_request(cloud_json, req_data):
    keys = list(cloud_json.keys())
    for key in req_data:
        if key not in keys:
            raise Exception("Incomplete request. Missing %s " % key)
    return True


if __name__ == '__main__':
    app.run()
