import boto3

from .utils import get_config

from assumptions import (
    assume,
    boto3_credentials
)


class AWSTagger:

    config = None
    accounts_data = None

    def __init__(self, config=None):
        self.config = get_config() \
            if not self.config else self.config

        self.accounts_data = self.config.get('accounts').items() \
            if not self.accounts_data else self.accounts_data

    @staticmethod
    def connect_by_account_and_region(account, region):

        session = boto3.session.Session(
            region_name=region,
            **boto3_credentials(
                **assume(
                    "cloud-formation",
                    account_name=account
                )
            )
        )

        return session

    def tag_resource(self, resource):
        accounts_data = self.accounts_data

        for account, regions in accounts_data:

            if not regions:
                regions = self.config.get('default').get('regions')

            for region in regions:
                session = self.connect_by_account_and_region(
                    account,
                    region
                )
                getattr(
                    self,
                    'tag_{}_using_session'.format(resource),
                    None
                )(session)

    @staticmethod
    def filter_tags(tags):

        filtered_tags = [
            tag for tag in tags if tag.get('Key') in [
                'Environment',
                'Project'
            ]
        ]

        return filtered_tags


class AWSTaggerNetworkInterfaces(AWSTagger):

    def set_tags(self):
        self.tag_resource('network_interfaces')

    def tag_network_interfaces_using_session(self, session):

        ec2_resource = session.resource('ec2')

        network_interfaces = ec2_resource.network_interfaces.all()

        for network in network_interfaces:

            subnet = network.subnet
            tags = subnet.tags

            filtered_tags = self.filter_tags(tags)

            network.create_tags(
                Tags=filtered_tags
            )

            print("Tagged Network Interface {} with tags {}".format(
                network.id,
                filtered_tags
            ))


class AWSTaggerVolumes(AWSTagger):

    def set_tags(self):
        self.tag_resource('volumes')

    def tag_volumes_using_session(self, session):

        ec2_resource = session.resource('ec2')

        volumes = ec2_resource.volumes.all()

        for volume in volumes:

            instance_id = volume.attachments[0].get('InstanceId')

            instance_tags = self._get_instance_tags_by_id_from_session(
                session,
                instance_id
            )

            volume.create_tags(
                Tags=instance_tags
            )

            print("Tagged EBS {} with tags {}".format(
                volume.id,
                instance_tags
            ))

    @classmethod
    def _get_instance_tags_by_id_from_session(cls, session, instance_id):

        ec2_resource = session.resource('ec2')

        instance = ec2_resource.Instance(instance_id)

        instance_tags = instance.tags

        return cls.filter_tags(instance_tags)

# tagger = AWSTaggerNetworkInterface()
# tagger.set_tags()

# tagger = AWSTaggerVolumes()
# tagger.set_tags()

