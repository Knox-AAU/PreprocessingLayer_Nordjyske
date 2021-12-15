# Preprocessing Nordjyske

This project is part of the Knox pipeline. It resides in the first layer and is centered around
processing the data set of newspaper articles.

The project is divided into five packages:

- **Crawling** (to traverse the folder structure of the data set)
- **Segmentation** (based on the _alto.xml_ files from the data set)
- **Pre-processing** (of the images [_not used_])
- **OCR** (for extract the text from the image files)
- **Parsing of NITF Files** (to convert .nitf files to the desired output)

In addition to these packages, the following repositories are also used: <br />
https://github.com/Knox-AAU/PreprocessingLayer_Source_Data_IO <br />
https://github.com/Knox-AAU/PreprocessingLayer_MongoDB_API <br />
https://github.com/Knox-AAU/PreprocessingLayer_Alto_Segment_Lib <br />

Along with the shared UI-repository: <br />
https://github.com/Knox-AAU/UI_React

Development of new features, such as pre- or post-processing should be added as new packages to this project.

## Installation and documentation
Please refer to the [wiki](https://wiki.knox.cs.aau.dk/Preprocessing/NordjyskeMedier) for installation and usage guides.

## Support

The development team behind this project will change once a year and for this reason support will be
limited. However, if you have any questions or stumble upon something that has not clearly been
described, you can contact one of the developers below, according to what issues your are experiencing.

**HOWEVER**, please be sure you have researched the issue *extensively*, and documented the issues along with the question elaborately.

Questions about the MongoDB + API and file watcher, please contact <br />
<ahha19@student.aau.dk> <\t> (Fall 2021) <br />

Questions about using and training Tesseract, please contact: <br />
<kpede19@student.aau.dk> <\t> (Fall 2021) <br/>

Generel questions for the project as a whole (alongside with all modules), please contact: <br />
<nvisti18@student.aau.dk> <\t> (Fall 2020)

## Contributing

A general walkthrough of how the codebase is structure and what standards are followed can be seen
below. Please ensure that you follow these conventions when contributing to the project.

Please also red the [agreements](https://wiki.knox.cs.aau.dk/en/Agreements) on the wiki page.
We have used [pep8](https://www.python.org/dev/peps/pep-0008/) standard, along with [Black](https://pypi.org/project/black/) to refactor the code (this is also run as the cont. integration when pushing to the repository)

### Naming conventions

The naming of different components follow the Python naming conventions, which can be seen in
full [here](https://www.python.org/dev/peps/pep-0008/) or boiled
down [here](https://visualgit.readthedocs.io/en/latest/pages/naming_convention.html).

### Unit testing

The unit tests for the project are structured according to the _pytest_ documentation
found [here](https://docs.pytest.org/en/stable/contents.html#toc).

#### Defining tests

A test is defined as seen below:

	def test_{method_name}_{what_should_happen_given_input}:
		assert method(param)

To speed up the process of creating tests, some IDE's can generate the tests for an entire class or
a specific method.

The tests for a given file/class is grouped in a file named '_test\_{name\_of\_file/class}.py_'. The
class within the file should follow _Test{TestedClass}_. Each of the test files can have
specialized _setUp_ and _tearDown_ methods as seen below:

	def setup_method(self, method):
		""" setup any state tied to the execution of the given method in a
		class.  setup_method is invoked for every test method of a class.
		"""

	...

	{tests}

	...


	def teardown_method(self, method):
		""" teardown any state that was previously setup with a setup_method
		call.
		"""

The _setup\_method_ method is used to avoid duplicate set up code for the tests in the file, as they
often use similar or identical prerequisite data, such as initialized objects. The _
teardown\_method_ is used to dispose of any objects or structures that otherwise could be left
behind as garbage.

#### Mocking

For some of the unit tests, mocking is used. We have utilized
the [unittest.mock library](https://docs.python.org/3/library/unittest.mock.html).

#### Test suite

It is also possible to set up test suites as well, allowing us to set the execution order for the
tests and add conditions for what test to be executed.

#### Generate packages

If additional packages are desired to improve the structure of additions to the project, the
following links were used when the current packages were created:

[https://packaging.python.org/tutorials/packaging-projects/](https://packaging.python.org/tutorials/packaging-projects/)
[https://packaging.python.org/guides/hosting-your-own-index/](https://packaging.python.org/guides/hosting-your-own-index/)

### .jp2 to .tiff conversion (Linux)

The data set consists of .jp2 files, but Tesseract requires .tiff files for training. This means
that the conversion of these files is necessary for certain situations. For Linux users, the
package _ffmpeg_ can be downloaded with the command:

```
sudo apt install ffmpeg
```

The conversion can after this be performed with the command:

```
ffmpeg -i input.jp2 output.tiff

```

## Authors and achknowledgement
The development teams who have been part of the development can be seen below:

- Cs-21-sw-5-15 (Fall 2021)
    - Kristian Morsing Pedersen
    - Alex Farup Christensen
    - Cecilie Welling Fog
    - Jonas Noermark
    - Alexander Hansen

- SW517e20 (Fall 2020)
    - Alex Immerkær Kristensen
    - Ida Thoft Christiansen
    - Jakob Kjeldbjerg Lund
    - Lau Ernebjerg Josefsen
    - Lena Said
    - Niels Vistisen
    - Thomas Gjedsted Lorentzen

Special thanks to all supervisors, who have contributed their expertice to the development of the
project:

- Theis Erik Jendal

## Status of project
The project is not done and is currently a work in progress.

The functionality still missing from the system includes:

- Pre-processing
- Post-processing
- Enhanced extraction of text written in a Gothic font (improved in the fall of 2021)
- Segmentation and text extraction across multiple pages

## Known issues
None :-)
