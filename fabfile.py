from fabricio import docker, tasks
from fabric import api

host = '195.201.27.44'
user = 'metric'
domain = 'metr.ddns.net'


@api.hosts(f'root@{host}')
@api.task
def install_docker():
    api.run('apt-get remove docker docker-engine docker.io')
    api.run('apt-get update')
    api.run(
        'apt-get install '
        'apt-transport-https '
        'ca-certificates '
        'curl '
        'software-properties-common '
    )
    api.run('curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo apt-key add -')
    api.run('apt-key fingerprint 0EBFCD88')
    api.run(
        'add-apt-repository '
        '"deb [arch=amd64] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" '
    )
    api.run('apt-get update')
    api.run('apt-get install docker-ce')


@api.hosts(f'root@{host}')
@api.task
def user_add():
    api.run(f'useradd -u 1010 -d /home/{user} -s /bin/bash -p wrongpassword {user}')
    api.run(f'usermod -aG docker {user}')


@api.hosts(f'root@{host}')
@api.task
def install_certificates():
    api.run('apt-get install software-properties-common')
    api.run('add-apt-repository ppa:certbot/certbot')
    api.run('apt-get update')
    api.run('apt-get install python-certbot-nginx')
    api.run(f'certbot --nginx -d {domain}')


metric_web = tasks.DockerTasks(
    service=docker.Container(
        name='metric_web',
        image='python:alpine',
        options={
            'publish': '8181:8181',
        },
    ),
    hosts=[f'{user}@{host}']
)
