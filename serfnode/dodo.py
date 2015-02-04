import os
import subprocess


DOIT_CONFIG = {'default_tasks': ['build']}


def target_image_exists(img):
    """Check if 'img' exists in local registry"""

    def f():
        try:
            subprocess.check_output(
                'docker inspect {} 1>/dev/null 2>&1'.format(img),
                shell=True)
            return True
        except subprocess.CalledProcessError:
            return False
    return f


def remote_image_exists(img):
    """Check if 'img' exists in remote registry"""

    def f():
        try:
            subprocess.check_output(
                'docker pull {} 1>/dev/null 2>&1'.format(img),
                shell=True)
            return True
        except subprocess.CalledProcessError:
            return False
    return f


def task_build():
    """Build serfnode image"""

    def all_files():
        for d, _, fs in os.walk('.'):
            for f in fs:
                if not f.startswith('.'):
                    yield os.path.join(d, f)

    return {
        'actions': ['docker build -t serfnode .',
                    'docker inspect -f "{{ .Id }}" serfnode > .build'],
        'targets': ['.build'],
        'file_dep': list(all_files()),
        'uptodate': [target_image_exists('serfnode')],
        'clean': True,
        'verbosity': 2
    }


def task_push():
    """Push image to docker hub"""

    return {
        'actions': ['docker tag -f serfnode adama/serfnode',
                    'docker push adama/serfnode',
                    'docker inspect -f "{{ .Id }}" serfnode > .push'],
        'targets': ['.push'],
        'file_dep': ['.build'],
        'task_dep': ['build'],
        'uptodate': [remote_image_exists('adama/serfnode')],
        'verbosity': 2
    }