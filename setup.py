from setuptools import setup,find_packages

with open('requirements.txt') as f:
    requirements = f.read().splitlines()

setup(
        name='ecommerce-recommendation-system',
        version='0.1',
        author='the-lotuseater',
        packages=find_packages(),
        install_requires=requirements
)


