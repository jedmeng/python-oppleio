from setuptools import setup, find_packages


setup(
    name='pyoppleio',
    version='1.0.6',
    keywords=['opple', 'iot'],
    description='Python library for interfacing with opple mobile control light',
    long_description=open('README.md', 'rt').read(),
    long_description_content_type='text/markdown',
    author='jedmeng',
    author_email='jedm@jedm.cn',
    url='https://github.com/jedmeng/python-oppleio',
    license='MIT',
    install_requires=[
        'crc16==0.1.1'
    ],
    packages=find_packages(),
    platforms='any',
    python_requires='>=3.5',
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'oppleio=pyoppleio.__main__:main',
        ]
    },
)
