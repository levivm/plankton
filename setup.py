from setuptools import setup, find_packages


setup(
    name='plankton',
    version='0.1',
    author='Levi Velazquez',
    author_email='levi.velazquez@bairesdev.com',
    description='Tag AWS resources',
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        'Click',
        'boto3',
        'assumptions>=2.0.8',
        'PyYAML',
    ],
    entry_points='''
        [console_scripts]
        plankton=plankton.cli:cli
    '''
)
