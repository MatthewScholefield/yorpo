from setuptools import setup

setup(
    name='yorpo',
    version='0.1.0',
    description='Tool to merge C/C++ source files',
    url='https://github.com/matthewscholefield/yorpo',
    author='Matthew D. Scholefield',
    author_email='matthew331199@gmail.com',
    classifiers=[
        'Development Status :: 3 - Alpha',

        'Intended Audience :: Developers',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='yorpo',
    py_modules=['yorpo'],
    install_requires=[],
    entry_points={
        'console_scripts': [
            'yorpo=yorpo:main'
        ],
    }
)
