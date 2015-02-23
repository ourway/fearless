from fabric.api import run, env, hosts

#env.hosts = ['fearless@192.168.20.159', 'fearless@192.168.20.151']

@hosts('fearless@192.168.20.159')
def taskA():
    run('ls')

@hosts('fearless@192.168.20.151')
def taskB():
    run('whoami')
