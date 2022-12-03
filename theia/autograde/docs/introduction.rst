============
Introduction
============

.. image:: _static/logo512.png

To start off on configuring an autograde assignment, you will need to create the actual
autograde test code. There is quite a bit of machinery in place in the admin IDEs on anubis
to make this process more streamline and easy.

We encourage all TAs that are using Anubis for autograding to take a few minutes to read
this documentation to get familiar with the tools available. We guarantee you it will
save you time later.


::

    @register_build
    def build(build_result: BuildResult):
        stdout, retcode = exec_as_student('make xv6.img fs.img')

        build_result.stdout = stdout
        build_result.passed = retcode == 0

        if 'this is a bad thing' in stdout:
            raise Panic("This is a bad thing that just happened. "
                        "We need to stop this pipeline right here and now")


::

    @register_test('Long file test')
    @points_test(10)
    def test_1(test_result: TestResult):
        test_result.message = "Testing long lines\n"

        # Start xv6 and run command
        stdout_lines = xv6_run("echo 123", test_result)

        # Run echo 123 as student user and capture output lines
        expected_raw, _ = exec_as_student('echo 123')
        expected = expected_raw.strip().split('\n')

        # Attempt to detect crash
        if did_xv6_crash(stdout_lines, test_result):
            return

        # Test to see if the expected result was found
        verify_expected(stdout_lines, expected, test_result)