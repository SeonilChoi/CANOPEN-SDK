from setuptools import setup, find_packages

setup(
    name='canopen_sdk',
	version='0.0.1',
	description='CANOpen Software Development Kit.',
	author='Ho-sik Shin, Seon-il Choi',
	author_email='seonilchoi98@gmail.com',
	install_requires=[
	    'canopen==2.3.0',
        'python-can==4.5.0'
	],
	packages=find_packages(exclude=[]),
	keywords=['canopen'],
	python_requires='>=3.6',
	package_data={},
	zip_safe=False
)
