Coming soon...

Note: test cases that use namespace std and the bind() function don't compile with c++11 because std::bind() is different to ::bind()

# Juliet Test Suite for C/C++

build Juliet test suite for unix systems - individual test case binaries, cross platform with CMake

This is the Juliet Test Suite for C/C++ 1.3 from https://samate.nist.gov/SARD/testsuite.php
with an added CMake build system to allow it to compile for CHERI.

## Running tests on CheriBSD

To run the tests on CHERI you should use [cheribuild](https://github.com/CTSRD-CHERI/cheribuild):
`cheribuild.py juliet-c-cheri --build-and-test` will build and run the tests (assuming you have built the SDK and a CheriBSD image first). 
