# SW517e20
This project is part of the Knox pipeline. It resides in the first layer and is centered around processing the data set of newspaper articles.

The project is divided into five packages:
- **Crawling** (to traverse the folder structure of the data set)
- **Segmentation** (based on the _alto.xml_ files from the data set)
- **Pre-processing** (of the images [_not used_])
- **OCR** (for extract the text from the image files)
- **Parsing of NITF Files** (to convert .nitf files to the desired output)

In addition to these packages, the repository _Knox/source-data-io_ containing functionality related to the output of the system has been developed. This repository can be found [here](https://git.its.aau.dk/Knox/source-data-io).

One of the future features that could enhance the output of the system is post-processing. This should be added as a sixth package when developed.

## Installation
To install the project, the following dependencies must also be installed:

```
// Install latest python (replace version)
sudo apt install build-essential libssl-dev
sudo apt install python3.9 python3.9-dev python3.9-distutils python3.9-venv

// Install pip
python3.9 -m pip install pip

// Generate virtual environment
cd /project/folder
python3.9 -m venv venv

// Activate virtual environment
cd /project/folder
source venv/bin/activate
pip3.9 install wheel
```

After this, the final step of installation is to install the packages in the _requirements.txt_ file by running:

```
pip install -r requirements.txt
```

>:warning: The virtual environment can be disabled by running the command: ``deactivate``

## Usage
Each package contains a _\_\_main\_\_.py_ file that can be execute. Each package can be executed individually by running the associate _\_\_main\_\_.py_ file, possibly with parameters.

### Crawling
The crawling module should only be used within other modules, which is the reason behind its empty _\_\_main\_\_.py_ file.

### Segmentation
The segmentation module is executed with two parameters.
- _path_ : the relative path to the folder containing the _.jp2_ file and associated _.alto.xml_ file
- _filename_ : name of the _.jp2_ to be segmented

This outputs a _.png_ file with the input file and an overlay of paragraph and header boxes.

### OCR
The OCR module is executed with four parameters:
- _path_ : the relative path to the file on which OCR should be performed
- _output\_dest_ : the relative path at which the output should be saved
- _tesseract_path_ : the relative path to Tesseract (this is only necessary if the installation of tesseract is not performed in a way that allows the system to find it by it self)
- _language_ : the language that should be used for the OCR (a full list can be found at [https://github.com/tesseract-ocr/langdata](https://github.com/tesseract-ocr/langdata))

This outputs a _.json_ file following the I/O modules schema and contains the extracted text.

### Parsing of NITF Files
The OCR module is executed with two parameters:
- _input_file_ : the relative path to the _.xml_ file that should parsed (must be in NITF format)
- _output\_dest_ : the relative path at which the output should be saved

This outputs a _.json_ file following the I/O modules schema and contains the parsed publication.

## Support
The development team behind this project will change once a year and for this reason support will be limited. However, if you have any questions or stumble upon something that has not clearly been described, please contact one of the developers at: <nvisti18@student.aau.dk>

However, make sure to have researched the issue before reaching out and to document the issue of question elaborately.

## Contributing
A general walkthrough of how the codebase is structure and what standards are followed can be seen below. Please ensure that you follow these conventions when contributing to the project.

### Naming conventions
The naming of different components follow the Python naming conventions, which can be seen in full [here](https://www.python.org/dev/peps/pep-0008/) or boiled down [here](https://visualgit.readthedocs.io/en/latest/pages/naming_convention.html).

### Unit testing
The unit tests for the project are structured according to the _pytest_ documentation found [here](https://docs.pytest.org/en/stable/contents.html#toc).

#### Setup
To set up _pytest_ in you virtual environment, you should add _pytest==6.1.1_ to the _requirements.txt_ for the module, if not already present, and then set the testing framework to _pytest_. In PyCharm, this is done under _settings > Tools > Python Integrated Tools_.

The folder structure of the tests is _{module\_folder} > tests > {test\_ClassToBeTested}_.

#### Defining tests

A test is defined as seen below:

	def test_{method_name}_{what_should_happen_given_input}:
		assert method(param)

To speed up the process of creating tests, some IDE's can generate the tests for an entire class or a specific method.

The tests for a given file/class is grouped in a file named '_test\_{name\_of\_file/class}.py_'. The class within the file should follow _Test{TestedClass}_. Each of the test files can have specialized _setUp_ and _tearDown_ methods as seen below:

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

The _setup\_method_ method is used to avoid duplicate set up code for the tests in the file, as they often use similar or identical prerequisite data, such as initialized objects. The _teardown\_method_ is used to dispose of any objects or structures that otherwise could be left behind as garbage.

#### Mocking
For some of the unit tests, mocking is used. We have utilized the [unittest.mock library](https://docs.python.org/3/library/unittest.mock.html).

#### Test suite
It is also possible to set up test suites as well, allowing us to set the execution order for the tests and add conditions for what test to be executed.

### Virtual environment
The virtual environment should just be set up for each module, as it should never be necessary to duplicate in other modules with other dependencies. However, the requirements for the virtual environment should be exported to the _requirements.txt_ file and this file should then be loaded when ever the given module is being set up.

To generate a new virtual environment, run ``python -m venv venv``.

Be sure to set the virtual environment as you python interpreter. If you are working in PyCharm, then you have to add a new interpreter under ``File > Settings > Project > Python Interpreter`` and point the path to the generated virtual environment.

> :warning: Remember to activate your virtual environment by running `source venv/bin/activate`.

#### Handling requirements.txt
The _requirements.txt_ file can be generated by running the command:

    pip freeze -l > requirements.txt

It can then be loaded into the current project by running the command:

    pip install -r requirements.txt

If _conda_ is used, it is necessary to install _pip_ in the virtual environment to use these commands. This is, from our research during the project, the easiest way to handle requirements in _conda_.

> :warning: _pip_ might be switched out for _pip3_ on your system

#### Generate packages
If additional packages are desired to improve the structure of additions to the project, the following links were used when the current packages were created:

[https://packaging.python.org/tutorials/packaging-projects/](https://packaging.python.org/tutorials/packaging-projects/)
[https://packaging.python.org/guides/hosting-your-own-index/](https://packaging.python.org/guides/hosting-your-own-index/)

### .jp2 to .tiff conversion (Linux)
The data set consists of .jp2 files, but Tesseract requires .tiff files for training. This means that the conversion of these files is necessary for certain situations. For Linux users, the package _ffmpeg_ can be downloaded with the command:

```
sudo apt install ffmpeg
```

The conversion can after this be performed with the command:

```
ffmpeg -i input.jp2 output.tiff

```

## Authors and achknowledgement
The development teams who have been part of the development can be seen below:
- SW517e20 (Fall 2020)
	- Alex Immerkær Kristensen
	- Ida Thoft Christiansen
	- Jakob Kjeldbjerg Lund
	- Lau Ernebjerg Josefsen
	- Lena Said
	- Niels Vistisen
	- Thomas Gjedsted Lorentzen

Special thanks to all supervisors, who have contributed their expertice to the development of the project:
- Theis Erik Jendal

## Status of project
The project is not done and is currently a work in progress.

The functionality still missing from the system includes:
- Post-processing
- Enhanced extraction of text written in a Gothic font
- Segmentation and text extraction across multiple pages
