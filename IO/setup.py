from IPython.core.release import long_description
from setuptools import setup

setup(
    name='knox_source_data_io',
    packages=['knox_source_data_io'],
    description='Package for important and exporting JSON files generated based on hte source data for the Knox project',
    long_description=long_description,
    long_description_content_type="text/markdown",
    version='0.0.1',
    url='https://repos.libdom.net/knox_source_data_io',
    author='Niels F. S. Vistisen, Thomas G. Lorentzen',
    author_email='nvisti18@student.aau.dk, tglo18@student.aau.dk',
    keywords=['Knox', 'I/O', 'JSON'],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3.0",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.8',
)
