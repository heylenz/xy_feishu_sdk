from setuptools import setup, find_packages

from xy_feishu_sdk import __version__

setup(
    name='xy_feishu_sdk',
    version=__version__,
    description='A tutorial for creating pip packages.',

    url='https://github.com/heylenz/feishu_sdk',
    author='hailin.yin',
    author_email='hailin.yin@outlook.com',

    packages=find_packages(),
    install_requires=["requests_toolbelt", "requests"],
    dependency_links =['https://github.com/heylenz/feishu-python-sdk/archive/refs/tags/0.1.5.zip'],

    classifiers=[
        'Intended Audience :: Developers',

        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
    ],
)
