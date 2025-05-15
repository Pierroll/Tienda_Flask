from setuptools import setup, find_packages

setup(
    name="tienda_flask",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'flask',
        'flask-sqlalchemy',
        'flask-login',
        'flask-wtf',
        'flask-mail',
        'email-validator',
        'pillow',
        'selenium',
        'webdriver-manager',
        'pytest',
    ],
)
