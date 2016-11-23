import requests
import subprocess
import paramiko
import json
import jinja2
import util

from heatclient.client import Client
from heatclient import exc as heat_exc


class JenkinsManager(object):

    def __init__(self, host, port, user, passwd, api_token, objc):
        self._host = host
        self._port = port
        self._user = user
        self._passwd = passwd
        self._api = api_token
        self._objc = objc

    def _build_endpoint(self):
        uri = 'http://' + self._user + ':' + self._passwd + '@' + self._host + ':' + str(self._port)
        print "jenkins uri %s " % uri
        return uri

    def _get_auth_string(self):
        return ' --user user.name:' + self._user + ':' + self._api

    def verify_jenkins_status(self):
        url = self._build_endpoint()
        url += '/api/json'
        data = {}
        response = requests.get(url, data=data)
        if response.ok:
            return True
        else:
            return False

    def _is_job_created(self, job_name):
        url = self._build_endpoint()
        url = url + '/job/' + job_name# + ' ' + self._get_auth_string()
        data = {}
        response = requests.get(url, data=data)
        if response.ok:
            return True
        else:
            return False

    def _build_config_payload(self):
        payload = None
        if isinstance(self._objc, RallyManager):
            payload = self._objc.build_rally_jenkins_payload()
        cntx = {'rally_script': payload}
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader("../templates/")
        ).get_template("rally_full_config.xml").render(cntx)

    def _get_job_params(self):
        if isinstance(self._objc, RallyManager):
            return self._build_parameter_job(self._objc.get_cloud_info())

    def create_job(self, component, action):
        url = self._build_endpoint()
        job_name = util.get_component_action(component, action)
        headers = {'Content-Type': 'application/xml'}
        data = self._build_config_payload()
        if not self._is_job_created(job_name):
            url += '/createItem?name=' + job_name
            print 'here'
            print data
            response = requests.post(url, data=data, headers=headers)
            print response.text
            if not response.ok:
                raise Exception("Jenkins job creation failed)")
        return job_name

    def _get_empty_job_config(self):
        return """<?xml version='1.0' encoding='utf-8'?>
        <project><builders/><publishers/><buildWrappers/></project>"""

    def trigger_job(self, component, action, args):
        job_name = self.create_job(component, action)
        #data = self._build_config_payload()
        print "Inside trigger job"
        params = self._build_rally_parameter_job(args.get('tool_data'))
        print "Job param data %s " % params
        url = self._build_endpoint() + '/job/' + job_name + '/buildWithParameters' + '?' + params# + self._get_auth_string()
        print url
        response = requests.post(url)
        print response

    def get_job_status(self, job_id):
        pass

    def _build_rally_parameter_job(self, args):
        cloud_info = args.get('cloud_data')
        cmd = ''
        cmd += 'OS_AUTH_URL=' + cloud_info.get('auth_url')
        cmd += '&OS_USERNAME=' + cloud_info.get('cloud_user')
        cmd += '&OS_PASSWORD=' + cloud_info.get('cloud_pass')
        cmd += '&OS_PROJECT_NAME=' + cloud_info.get('project_name')
        cmd += '&OS_TEST_NAME=' + cloud_info.get('test_name')
        cmd += '&OS_RELEASE=' + cloud_info.get('release')
        cmd += '&OS_TEST_TARGET=' + args.get('test_target')
        cmd += '&OS_TEST_TARGET_VALUE=' + args.get('test_target_value')
        cmd += '&INFLUX_URL=' + args.get('influx_url')
        cmd += '&INFLUX_DB=' + args.get('influx_db')
        return cmd


class RallyManager(object):

    REQ_KEY = ['auth_url', 'user', 'passwd']

    def __init__(self, host, user, passwd, cloud_req):
        self._host = host
        self._user = user
        self._passwd = passwd
        self._cloud_req = cloud_req

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
            opts += '--set'
        elif 'testsuite' == filter:
            opts += '--regex'
        if opts is not None:
            opts += ' ' + param
        return opts

    def build_rally_cmd(self, action, filter_text=None, param=None, deployment_id=None):
        if action == 'create':
            return 'rally deployment create --fromenv --name=rally-auto'
        elif action == 'deploy_check':
            return 'rally deployment check'
        elif action == 'install':
            return 'rally verify install --deployment %s' % deployment_id
        elif action == 'verify':
            cmd = 'rally verify start'
            if deployment_id is not None:
                cmd += ' --deployment %s' % deployment_id
            if filter_text is not None:
                cmd += self._parse_rally_options(filter_text, param)
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
        ssh.connect(self._host, username=self._user, password=self._passwd)
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
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader("../templates")
        ).get_template("rally_full.sh").render(self._build_rally_script_context())

    def _build_rally_script_context(self):
        cntx = {
       #     'project': self._cloud_req.get('project_name') or 'admin',
       #     'user': self._user or 'admin',
       #     'passwd': self._passwd or 'admin',
       #     'auth_url': self._cloud_req.get('auth_url') or 'http://localhost:5000/v3',
       #     'rally_cmd': self.build_rally_cmd(action='verify')
        }
        return cntx

    def get_rally_execution_status(self, execution_id):
        pass

    def get_cloud_info(self):
        return self._cloud_req

class OpenStackServiceManager(object):

    def __init__(self, auth_url, user, passwd, tenant):
        self._auth_url = auth_url
        self._user = user
        self._passwd = passwd
        self._tenant = tenant

    def _get_keystone_resp(self):
        data = self._build_keystone_payload()
        headers = {'Content-Type': 'application/json'}
        url = self._auth_url + '/tokens'
        resp = requests.post(url, data=json.dumps(data), headers=headers)
        print 'keystone resp %r ' % resp
        print 'keyst resp data %r ' % resp.content
        if resp.ok:
            return resp
        return None

    def get_auth_token_service_url(self, ser_req, region='RegionOne'):
        resp = json.loads(self._get_keystone_resp().content)
        print 'Keystone respone %r ' % resp
        token = url = tenant_id = None
        if resp is not None:
            token = resp['access']['token']['id']
            tenant_id = resp['access']['token']['tenant']['id']
            for service in resp['access']['serviceCatalog']:
                if service['name'] == ser_req:
                    print 'endpoints %r ' % service['endpoints']
                    for url_list in service['endpoints']:
                        print url_list
                        if url_list['region'] == region:
                            url = url_list['publicURL']
                            break
        print 'url %r, token %r, tenant_id %r' % (url, token, tenant_id)
        return token, url, tenant_id

    def _build_keystone_payload(self):
        data = {"auth": {
                    "tenantName": self._tenant,
                    "passwordCredentials": {
                        "username": self._user,
                        "password": self._passwd
                    }
            }
        }
        print 'keystone req data %r ' % data
        return data


class HeatDeployManager(object):

    def __init__(self, hot_url, auth_token, tenant_id):
        self._hot_url = hot_url
        self._auth_token = auth_token
        self._tenant_id = tenant_id
        self._heat_client = Client('1', endpoint=self._hot_url, token=self._auth_token)

    def create_stack(self, master=1, slave=3, deploy_is_master=True):
        pass

    def create_default_stack(self, args, stack_id=None):
        template = self._get_default_hot_template(args)
        print 'Template %r \n' % template
        try:
            response = self._heat_client.stacks.create(stack_name=args['name'], template=template)
            stack = response['stack']
        except Exception:
            print 'Inside except block'
            response = self._heat_client.stacks.update(stack_id, template=template)
            print 'Update response %r ' % response
            return stack_id
        print 'Heat response %r ' % stack
        return stack

    def _get_default_hot_template(self, args):
        with open("../templates/requirements.yml", "r") as myfile:
            data = myfile.read()
        cntx = {
            'key_name': args['key_name'],
            'image_id': args['image_id'],
            'public_net_id': args['public_net_id'],
            'private_net_id': args['private_net_id'],
            'private_subnet_id': args['private_subnet_id'],
            'instance_type': args['instance_type'],
            'galaxy_requirements': data
        }
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader("../templates")
        ).get_template("hot-cluster.yml").render(cntx)

    def _build_deploy_node_template(self):
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader("../templates")
        ).get_template("hot-deploy.yml").render({
            'init_script': self._build_init_script()
        })

    def _build_init_script(self):
        data = None
        with open("requirements.yml", "r") as myfile:
            data = myfile.readlines()
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader("../templates")
        ).get_template("init.sh").render({
            'ansible_requirements': data
        })

    def _get_requirement_file(self):
        return jinja2.Environment(
            loader=jinja2.FileSystemLoader("../templates")
        ).get_template("requirements.yml").render()
