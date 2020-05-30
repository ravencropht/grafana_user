## Synopsis
Manage grafana users.

## Install
The easiest way to install module is to put it in **library/** folder near your playbook.
Like this:
```buildoutcfg
playbook.yml
library/
  |_ grafana_user.py
```

## Parameters

- **user_login** (*required*) - User login.
- **user_password** (*required*) - User password.
- **user_name** - User name.
- **user_email** - User email. Default: *no_email*
- **state** - State of plugin. Choices: present/absent. Default: *present*.
- **grafana_user** (*required*) - Grafana admin login.
- **grafana_password** (*required*) - Grafana admin password.
- **grafana_url** (*required*) - Grafana url.
- **verify_ssl** - Verify ssl. Should be yes or no. Use "no" if Grafana uses self-signed cert. Default: *yes*.

## Example

```buildoutcfg
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
```
