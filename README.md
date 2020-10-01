# SW517e20

## Unit testing
The unit tests for the project are structured according to unittest documentation found [here](https://docs.python.org/3/library/unittest.html).

The tests for a given file/class is grouped in a file named '_test\_{name\_of\_file/class}.py_'. Each of the test files have specialized _setUp_ and _tearDown_ methods, which might be empty if no set up/tear down is needed.

	def setUp(self):
        	# Set up of the test, will be run before each test
		self.object = Object('content')

	...

	def tearDown(self):
		# Tear down of the test, will be run after each test
		self.object.dispose()

_setUp_ is executed before every test and _tearDown_ is executed after each test. _setUp_ is used to avoid duplicate set up code for the tests in the file, as they often use similar or identical prerequisite data. _tearDown_ is used to dispose of any objects or structures that otherwise could use up memory.

It is also possible to set up test suites as well, allowing us to set the execution order for the tests and add conditions for what test to be executed.
