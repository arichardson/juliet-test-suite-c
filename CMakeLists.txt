cmake_minimum_required (VERSION 3.0)
project (juliet)

# prevent cmake from setting -O2 (for release, relwithdebinf, minsizerel, etc)
set(CMAKE_C_FLAGS_RELWITHDEBINFO "-g")
set(CMAKE_C_FLAGS_RELEASE "-g")
set(CMAKE_C_FLAGS_MINSIZEREL "-g")
add_compile_options(-O0)  # hopefully adding -O0 here should turn off test optimizations

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY ${CMAKE_BINARY_DIR}/bin)

set(SUPPORT_DIR ../../../testcasesupport/) #TODO this changes depending on whether test dir split
add_library(support SHARED ${SUPPORT_DIR}io.c ${SUPPORT_DIR}std_thread.c)

include_directories(${SUPPORT_DIR})
link_libraries(support pthread m)
add_definitions(-DINCLUDEMAIN)

# this test suite consists of five types of tests (see user's guide)
# - tests that can be built from a single source file
# - tests that are built from multiple source files (sub-file identifiers a,b,c,...)
# - class-based cpp tests that have good and bad files (sub-file identifiers _good1 and _bad)
# - virtual-based cpp tests that consist of a header and other source files (identifiers in guide)
# some tests are bad-only, but this does not require special consideration

# our strategy is to iterate through source files, determine the test name corresponding to the file,
# then build an executable with all files corresponding to that test

# collect all source files corresponding to windows tests, we don't want to build them
file(GLOB WINDOWS_FILES RELATIVE ${CMAKE_SOURCE_DIR} CWE*w32*.c* CWE*wchar_t*.c* CWE*w32*.h CWE*wchar_t*.h)

# collect all test sources and remove windows files
file(GLOB SOURCE_FILES RELATIVE ${CMAKE_SOURCE_DIR} CWE*.c CWE*.cpp)
list(REMOVE_ITEM SOURCE_FILES ${WINDOWS_FILES} "") # empty string in case windows files is empty

foreach(SOURCE_FILE ${SOURCE_FILES})
  # get the name of the test that this source file corresponds to (cf user's guide section 3.4.1)
  # regex: "CWE", CWE ID, "_", Shortened CWE entry name, "__", Functional Variant Name, "_",
  # Flow Variant, Sub-file Identifier, ".", extension
  string(REGEX MATCH "^CWE[0-9]+_.+__.+_[0-9][0-9]" EXECUTABLE_NAME ${SOURCE_FILE})
  # don't make multiple executables with sources from the same test
  if (NOT TARGET ${EXECUTABLE_NAME}-good)
    # collect all source files corresponding to this test
    file(GLOB EXECUTABLE_SOURCES RELATIVE ${CMAKE_SOURCE_DIR} ${EXECUTABLE_NAME}*)

    # add good executable
    add_executable(${EXECUTABLE_NAME}-good ${EXECUTABLE_SOURCES})
    set_target_properties(${EXECUTABLE_NAME}-good
      PROPERTIES
      RUNTIME_OUTPUT_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/good
      COMPILE_DEFINITIONS OMITBAD
    )

    # add bad executable
    add_executable(${EXECUTABLE_NAME}-bad ${EXECUTABLE_SOURCES})
    set_target_properties(${EXECUTABLE_NAME}-bad
      PROPERTIES
      RUNTIME_OUTPUT_DIRECTORY ${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/bad
      COMPILE_DEFINITIONS OMITGOOD
    )
  endif(NOT TARGET ${EXECUTABLE_NAME}-good)
endforeach(SOURCE_FILE ${SOURCE_FILES})

#TODO add test run support and other options

# copy the run makefile to the build directory every time it changes:
#add_custom_target(copy-test-makefile ALL DEPENDS ${CMAKE_CURRENT_BINARY_DIR}/Makefile.bsd-run)
#add_custom_command(OUTPUT ${CMAKE_CURRENT_BINARY_DIR}/Makefile.bsd-run
                   #COMMAND ${CMAKE_COMMAND} -E copy ${CMAKE_CURRENT_SOURCE_DIR}/Makefile.bsd-run
                                                    #${CMAKE_CURRENT_BINARY_DIR}/Makefile.bsd-run
                   #DEPENDS ${CMAKE_CURRENT_SOURCE_DIR}/Makefile.bsd-run
#)

#option(WITH_STACK_PROTECTOR "disable stack protector" OFF)
#option(WITH_FORTIFY_SOURCE "disable _FORTIFY_SOURCE" OFF)
#if (WITH_STACK_PROTECTOR)
	#message(STATUS "compiling WITH stack protector")
	#add_compile_options(-fstack-protector-all)
#else()
	#message(STATUS "compiling WITHOUT stack protector")
	#add_compile_options(-fno-stack-protector)
#endif()
#if (WITH_FORTIFY_SOURCE)
	#message(STATUS "compiling WITH _FORTIFY_SOURCE=2")
	#add_definitions(-D_FORTIFY_SOURCE=2)
#else()
	#add_definitions(-D_FORTIFY_SOURCE=0)
	#message(STATUS "compiling WITHOUT _FORTIFY_SOURCE")
#endif()


#if (NOT CMAKE_CROSSCOMPILING)
	#enable_testing()
#endif()

#  Could also add extern "C" int __lsan_is_turned_off() { return 1; }
# to disable LSAN (but for now just set ASAN_OPTIONS=detect_leaks=0 in the test script)
# add_library(disable-lsan OBJECT disable-leak-sanitizer.c)

#[[
foreach ( tcf ${test_cs} ${test_cs_heap})
	string ( REGEX REPLACE ".c$" "" tf ${tcf} )
	string ( REGEX REPLACE "^testcases(-heap)?/" "" to ${tf} )
	unset ( tf )
	add_executable ( ${to} ${tcf} )
	target_compile_options( ${to} PUBLIC "-pthread")
	target_link_libraries( ${to} "pthread")
	# target_link_libraries( ${to} disable-lsan)
	add_test(NAME test-${to} COMMAND ${CMAKE_CURRENT_SOURCE_DIR}/check_test.sh $<TARGET_FILE:${to}>)
	if (NOT ${to} MATCHES ".*-ok$")
		# message(STATUS "Expecting ${to} to fail")
		set_tests_properties(test-${to} PROPERTIES WILL_FAIL TRUE)
	endif()
endforeach ( tcf ${TESTC} )
]]
