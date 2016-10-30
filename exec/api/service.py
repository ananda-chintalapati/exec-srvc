import datetime.datetime
import requests
import subprocess
import sys
import paramiko
import json
import jinja2
import flask

class JenkinsManager(object):

    def __init__(self, host, port, user, passwd, api_token):
        self._host = host
        self._port = port
        self._user = user
        self._passwd = passwd
        self._api = api_token


    def _build_endpoint(self):
        uri = 'http://' + self._user + ':' + self._passwd + '@' + self._host + ':' + self._port
        return uri

    def _get_auth_string(self):
        return '--user user.name:' + self._user + ':' + self._api

    def verifyJenkinsStatus(self):
        url = self._build_endpoint()
        url = url + '/api/json' + self._get_auth_string()
        data = {}
        response = requests.get(url, data=data)
        if response.ok:
            return True
        else:
            return False

    def createJob(self, component, request_data):
        pass

    def triggerJob(self):
        pass

    def getJobStatus(self, job_id):
        pass

class RallyManager(object):

    REQ_KEY = [ 'auth_url', 'user', 'passwd']

    def __init__(self, jenkins, host, user, passwd):
        self._jenkins = jenkins
        self._host = host
        self._user = user
        self._passwd = passwd

    def _validate_request(self, request):
        validate = True
        if request is not None:
            kwargs = request['request']
            for key, value in kwargs.iteritems():
                if key not in self.REQ_KEY:
                    validate = False
                    break
        else:
            validate = False
        return validate

    def verifyRallyStatus(self):
        command = "rally --version"
        ssh = subprocess.Popen(["ssh", "%s" % self._host, command],
                               shell=False,
                               stdout=subprocess.PIPE,
                               stderr=subprocess.PIPE)

    def _parse_rally_options(self, filter_text, param):
        opts = None

        if 'project' == filter_text:
            opts = opts + '--set'
        elif 'testsuite' == filter:
            opts = opts + '--regex'
        if opts is not None:
            opts = opts + ' ' + param
        return opts

    def build_rally_cmd(self, action, filter_text, param, deployment_id):
        if action == 'create':
            return 'rally deployment create --fromenv --name=rally-auto'
        elif action == 'deploy_check':
            return 'rally deployment check'
        elif action == 'install':
            return 'rally verify install --deployment %s' % deployment_id
        elif action == 'verify':
            cmd = 'rally verify start --deployment %s' % deployment_id
            cmd = cmd + self._parse_rally_options(filter, param)
            return cmd
        elif action == 'uninstall':
            return 'rally verify uninstall --deployment %s' % deployment_id
        elif action == 'results':
            return 'rally verify results --json'
        elif action == 'destroy':
            return 'rally deployment destroy --deployment %s ' % deployment_id

    def trigger_rally(self, action, filter_txt=None, param=None, deployment_id=None):
        rally_cmd = self.build_rally_cmd(action, filter_txt, param, deployment_id)
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        ssh.connect(self._host,username=self._user, password=self._passwd)
        stdin, out, err = ssh.exec_command(rally_cmd)
        return out.readlines(), err.readlines()

    def _validate_iput_request(self):
        pass

    def get_rally_executions(self):
        out, err = self.trigger_rally('results')
        results = json.loads(out)
        success = results['success']
        skipped = results['skipped']
        failures = results['failures']
        expected_failures = results['expected_failures']
        test_cases = results['test_cases']

    def build_rally_jenkins_payload(self):
        pass

    def get_rally_executionStatus(self, execution_id):
        pass


