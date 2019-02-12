""" Generic Testing Utilities. """

import docker
import os
import sys
from flask_migrate import upgrade
from outcomes_api import app, ConfigurationFactory


class DatabaseContainerFixture(object):
    def __init__(self):
        self.docker_client = docker.from_env()
        self.config = ConfigurationFactory.get_config('TEST')
        self.container = None
        self.test_environment = [
            'POSTGRES_USER={}'.format(self.config.POSTGRES_USER),
            'POSTGRES_PASSWORD={}'.format(self.config.POSTGRES_PASSWORD),
            'POSTGRES_DB={}'.format(self.config.POSTGRES_DATABASE)
        ]
        self.test_ports = {'5432/tcp': self.config.POSTGRES_PORT}

    def setup_database(self):
        # pull the postgresql image from repo if it doesn't exist
        try:
            self.docker_client.images.pull(self.config.get_postgresql_image())
        except Exception:
            print('Failed to pull image {} from repository.'.format(
                self.config.get_postgresql_image()))

        # launch the testing container
        self.container = self.docker_client.containers.run(
            self.config.get_postgresql_image(),
            detach=True,
            auto_remove=True,
            name=self.config.CONTAINER_NAME,
            environment=self.test_environment,
            ports=self.test_ports)

    def populate_database(self):
        app.config.from_object(self.config)
        print(os.path.dirname(sys.modules['__main__'].__file__))
        with app.app_context():
            upgrade(
                directory='/Users/gmundy/Work/program-outcomes-api/outcomes_api/db/migrations')

    def teardown_database(self):
        self.container.stop()