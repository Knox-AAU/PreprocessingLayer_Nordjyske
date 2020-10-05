# SW517e20

## Unit testing
The unit tests for the project are structured according to the _pytest_ documentation found [here](https://docs.pytest.org/en/stable/contents.html#toc).

A test is defined as seen below:

	def test\_{method\_name}\_{expected\_answer}:
		assert method(par)

The tests for a given file/class is grouped in a file named '_test\_{name\_of\_file/class}.py_'. Each of the test files can have a _fixture_ that fucntions as the specialized _setUp_ and _tearDown_ methods in other frameworks. In _pytest_, such a method contains both _setUp_ and _tearDown_. An example can be seen below:

	@pytest.fixture(autouse=True)
	def transact(self, {_optional_parameters_}):
			# Code to be executed before each test
			...

			yield

			# Code to be executed after each test
			...

The ficture is used to avoid duplicate set up code for the tests in the file, as they often use similar or identical prerequisite data (set up part). Furthermore, it is used to dispose of any objects or structures that otherwise could use up memory (tear down part).

### (Mocking)

### (Test suite)
