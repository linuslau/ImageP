from setuptools import setup, find_packages

setup(
    name='ImageP',
    version='0.1',
    packages=find_packages(include=['ImageP', 'ImageP.*']),
    include_package_data=True,
    install_requires=[
        'PyQt5',
    ],
    entry_points={
        'console_scripts': [
            'ImageP = ImageP.main:main',
        ],
    },
    package_data={
        'ImageP': ['menu/**/*'],
    },
)
