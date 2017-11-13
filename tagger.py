import boto3

from utils import get_config

from assumptions import (
    assume,
    boto3_credentials
)


def tag_accounts_ebs():

    config = get_config()

    accounts_data = config.get('accounts').items()

    for account, regions in accounts_data:

        if not regions:
            regions = config.get('default').get('regions')

        for region in regions:
            tag_account_ebs_volumes(
                account,
                region
            )


def tag_account_ebs_volumes(account, region):

    region = 'us-east-1'
    session = connect_by_account_and_region(
        account,
        region
    )

    tag_ebs_resource_from_session(session)


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


def tag_ebs_resource_from_session(session):

    ec2_resource = session.resource('ec2')

    volumes = ec2_resource.volumes.all()

    for volume in volumes:

        instance_id = volume.attachments[0].get('InstanceId')

        instance_tags = get_instance_tags_by_id_from_session(
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


def get_instance_tags_by_id_from_session(session, instance_id):

    ec2_resource = session.resource('ec2')

    instance = ec2_resource.Instance(instance_id)

    instance_tags = instance.tags

    filtered_tags = [
        tag for tag in instance_tags if tag.get('Key') in [
            'Environment',
            'Project'
        ]
    ]

    return filtered_tags

tag_accounts_ebs()
