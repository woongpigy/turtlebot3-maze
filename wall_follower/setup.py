import os
from glob import glob

from setuptools import setup

package_name = 'wall_follower'

setup(
    name=package_name,
    version='0.1.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages', ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
        (os.path.join('share', package_name, 'launch'), glob('launch/*.launch.py')),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='TA',
    maintainer_email='noreply@example.com',
    description='터틀봇3 오른쪽 벽 따라가기',
    license='Apache-2.0',
    entry_points={
        'console_scripts': [
            'wall_follower = wall_follower.wall_follower:main',
        ],
    },
)
