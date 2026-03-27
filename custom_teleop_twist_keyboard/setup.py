from setuptools import setup

package_name = 'teleop_twist_keyboard_custom'

setup(
    name=package_name,
    version='0.0.0',
    packages=[package_name],
    data_files=[
        ('share/ament_index/resource_index/packages',
            ['resource/' + package_name]),
        ('share/' + package_name, ['package.xml']),
    ],
    install_requires=['setuptools'],
    zip_safe=True,
    maintainer='Shaikh Aakif',
    maintainer_email='shaikhaakif278@gmail.com',
    description='Custom teleop_twist_keyboard with actuator keys',
    license='BSD',
    tests_require=['pytest'],
    entry_points={
        'console_scripts': [
            'teleop_twist_keyboard = teleop_twist_keyboard_custom.teleop_twist_keyboard:main',
        ],
    },
)
