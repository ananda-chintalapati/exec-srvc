import requests
import subprocess
import sys

class JenkinsExecutor(object):

    def __init__(self, host, port, user, passwd):
        self._host = host
        self._port = port
        self._user = user
        self._passwd = passwd

    def _build_endpoint(self):
        uri = 'http://' + self._user + ':' + self_passwd + '@' + self._host + ':' + self._port
        return uri + '/api/json'

    def verifyJenkinsStatus(self):
        url = _build_endpoint()
        data = {}
        response = requests.get(url, data=data)
        if response.ok:
            return True
        else:
            return False

    def createJob(self):
        pass

    def triggerJob(self):
        pass

    def getJobStatus(self, job_id):
        pass

class RallyExecutor(object):

    REQ_KEY = [ 'auth_url', 'user', 'passwd']

    def __init__(self, jenkins, host, user, passwd):
        self._jenkins = jenkins
        self._host = host
        self._user = user
        self._passwd = passwd

    def _validate_request(self, **kwargs):
        validate = True
        if request is not None:
            for key, value in kwargs.iteritems():
                if key not in REQ_KEY:
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

    def _parse_rally_options(self, filter, param):
        opts = "--"

        if 'project' == filter:
            opts = opts + 'set'
        else if 'testsuite' == filter:
            opts = opts + 'regex'

        opts = opts + ' ' + param
        return opts

    def _build_rally_cmd(self, action, filter, param, deployment_id):
        if action == 'create':
            return 'rally deployment create --fromenv --name=rally-auto'
        elif action == 'deploy_check':
            return 'rally deployment check'
        elif action == 'install':
            return 'rally verify install --deployment %s' % deployment_id
        elif action == 'verify':
            cmd = 'rally verify start --deployment %s' % deployment_id
            cmd = cmd + _parse_rally_options(filter, param)
            return cmd
        elif action == 'uninstall'
            return 'rally verify uninstall --deployment %s' % deployment_id
        elif action == 'results'
            return 'rally verify results --json --deployment %s' % deployment_id
        elif action == 'destroy'
            return 'rally deployment destroy --deployment %s ' % deployment_id

    def trigger_rally(self):
        pass

    def _validate_iput_request(self):
        pass

    def get_rally_executions(self):
        pass

    def get_rally_executionStatus(self, execution_id):
        pass


