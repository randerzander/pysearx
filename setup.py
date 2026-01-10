from setuptools import setup, find_packages

setup(
    name='pysearx',
    version='0.1.0',
    description='A plain Python library for generic web search',
    author='pysearx contributors',
    packages=find_packages(),
    install_requires=[
        'requests>=2.25.0',
        'lxml>=4.6.0',
    ],
    python_requires='>=3.7',
)
