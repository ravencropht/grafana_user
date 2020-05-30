# Copyright: (c) 2020, Konstantin Galushko <galushko.kp@gmail.com>
# GNU General Public License v3.0+ (see COPYING or https://www.gnu.org/licenses/gpl-3.0.txt)

ANSIBLE_METADATA = {
    'metadata_version': '1.0',
    'status': ['release'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: grafana_user

short_description: Module for managing grafana users

version_added: "2.4"

description:
    - "Module for managing grafana users"

options:
    user_login:
        description:
            - User login
        required: true
    user_name:
        description:
            - User name
        required: false
    user_email:
        description:
            - User email
        required: false
    state:
        description:
            - State of user. Can be present or absent. Default present.
        required: false
    user_password:
        description:
            - User password.
        required: true
    grafana_user:
        description:
            - Grafana admin user for auth.
        required: true
    grafana_password:
        description:
            - Grafana admin password for auth.
        required: true
    grafana_url:
        description:
            - Grafana url.
        required: true
    verify_ssl:
        description:
            - Verify ssl. Should be yes or no. Use "no" if Grafana uses self-signed cert. Default yes.
        required: false

author:
    - Konstantin Galushko
'''

EXAMPLES = '''
# Add user
- grafana_user:
    user_login: test1
    user_name: Test User
    state: present
    user_password: t3stpassw0rd
    user_email: "test_user@example.com"
    grafana_user: admin
    grafana_password: adminPassw0rd
    grafana_url: 'https://grafana.example.com'
  delegate_to: localhost

# Remove user
- grafana_user:
    user_login: test1
    state: absent
    user_password: t3stpassw0rd
    grafana_user: admin
    grafana_password: adminPassw0rd
    grafana_url: 'https://grafana.example.com'
  delegate_to: localhost

'''

from ansible.module_utils.basic import AnsibleModule
import requests
import json


def main():
# Nest arguments
    module_args = dict(
        user_login=dict(type='str', required=True),
        user_name=dict(type='str', required=False, default=''),
        state=dict(type='str', required=False, default='present', choices=['present', 'absent']),
        user_password=dict(type='str', required=True, no_log=True),
        user_email=dict(type='str', required=False, default='no_email'),
        grafana_user=dict(type='str', required=True),
        grafana_password=dict(type='str', required=True, no_log=True),
        grafana_url=dict(type='str', required=True),
        verify_ssl=dict(type='bool', required=False, default=True)
    )
# Attach args to module
    module = AnsibleModule(
                     argument_spec=module_args,
                     supports_check_mode=True
    )

    user_login = module.params['user_login']
    user_name = module.params['user_name']
    state = module.params['state']
    user_password = module.params['user_password']
    user_email = module.params['user_email']
    grafana_user = module.params['grafana_user']
    grafana_password = module.params['grafana_password']
    grafana_url= module.params['grafana_url']
    verify_ssl_value = module.params['verify_ssl']

    playbook_user_data = {'login': user_login, 'name': user_name, 'email': user_email}

# Set initial result and headers
    result = {}
    headers = {'Content-Type': 'application/json'}

# Check is user present in Grafana
    try:
        r = requests.get(
            f'{grafana_url}/api/users/lookup?loginOrEmail={user_login}',
            auth=(grafana_user, grafana_password),
            verify=verify_ssl_value
        )
        grafana_user_data = json.loads(r.text)
    except OSError as e:
        module.fail_json(msg='Wrong Grafana url')

    if grafana_user_data.get('message') == 'User not found':
        user_present = False
    elif grafana_user_data.get('id'):
        user_present = True
        user_id = grafana_user_data.get('id')
    elif grafana_user_data.get('message') == 'Invalid username or password':
        module.fail_json(msg=(grafana_user_data.get('message')))

# Delete user
    if module.params['state'] == 'absent' and user_present:
        try:
            r = requests.delete(
                f'{grafana_url}/api/admin/users/{user_id}',
                auth=(grafana_user, grafana_password),
                verify=verify_ssl_value
            )
            result['changed'] = True
        except:
            module.fail_json(msg=r.text)

# Create user
    if module.params['state'] == 'present' and not user_present:
        try:
            data = {"name":user_name,"email":user_email,"login":user_login,"password":user_password}
            r = requests.post(f'{grafana_url}/api/admin/users',
                  headers=headers, json=data, auth=(grafana_user, grafana_password),
                  verify=verify_ssl_value
            )
            result['changed'] = True
        except:
            module.fail_json(msg=r.text)

# Check user password and user data (name, email, etc.)
    if module.params['state'] == 'present' and user_present:
        try:
            r = requests.get(
                f'{grafana_url}/api/org',
                auth=(user_login, user_password),
                verify=verify_ssl_value
            )
            data = json.loads(r.text)
            if data.get('message') == 'Invalid username or password':
                data = {"password":user_password}
                r = requests.put(f'{grafana_url}/api/admin/users/{user_id}/password',
                    headers=headers, json=data, auth=(grafana_user, grafana_password),
                    verify=verify_ssl_value
                )
                result['changed'] = True
        except:
            module.fail_json(msg=r.text)

        for data_value in playbook_user_data:
            if playbook_user_data[data_value] != grafana_user_data[data_value]:
                try:
                    r = requests.put(
                          f'{grafana_url}/api/users/{user_id}',
                          headers=headers, json=playbook_user_data,
                          auth=(grafana_user, grafana_password),
                          verify=verify_ssl_value
                    )
                except:
                    module.fail_json(msg=r.text)
                else:
                    result['changed'] = True
                    break


    module.exit_json(**result)


if __name__ == '__main__':
    main()
