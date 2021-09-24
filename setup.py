from setuptools import find_packages, setup

setup(
    name='flask-rest-framework',
    version='0.0.2',
    license='MIT',
    description='',
    author='waro163',
    author_email='waro163@163.com',
    url='https://github.com/waro163/flask-restframework',
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type = 'text/markdown',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    python_requires = '>=3.5',
    install_requires=[
        'flask>=2.0.0',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Flask',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'License :: OSI Approved :: MIT License',
        'Topic :: Internet :: WWW/HTTP',
    ]
)