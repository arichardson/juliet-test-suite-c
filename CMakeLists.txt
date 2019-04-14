# TODO invoke generated build files with option to continue in case of compiler
# error - some tests have errors, particularly use of bind() syscall
cmake_minimum_required(VERSION 3.6)

# grab CWE name from the directory we're in
get_filename_component(CWE_FOLDER "${CMAKE_SOURCE_DIR}" NAME)
string(REGEX MATCH "^CWE[0-9]+" CWE_NAME "${CWE_FOLDER}")

project("juliet-c-${CWE_NAME}")

# prevent cmake from setting -O2 (for release, relwithdebinf, minsizerel, etc)
set(CMAKE_C_FLAGS_RELWITHDEBINFO "-g")
set(CMAKE_C_FLAGS_RELEASE "-g")
set(CMAKE_C_FLAGS_MINSIZEREL "-g")
add_compile_options(-O0)  # hopefully adding -O0 here should turn off test optimizations

# if not using cheribuild, put binaries in a top-level /bin folder
set(CMAKE_BINARY_DIR ../../bin/)

set(CMAKE_RUNTIME_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/${CWE_NAME}")
set(CMAKE_LIBRARY_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/support")
set(CMAKE_ARCHIVE_OUTPUT_DIRECTORY "${CMAKE_BINARY_DIR}/support")
set(SUPPORT_DIR ../../testcasesupport/)
add_library(support SHARED "${SUPPORT_DIR}io.c" "${SUPPORT_DIR}std_thread.c")

# TODO identify add CWE-specific support files sec 5.2

include_directories("${SUPPORT_DIR}")
link_libraries(support pthread m)
add_definitions(-DINCLUDEMAIN)

# this test suite consists of many types of tests (see user's guide)
# - tests that can be built from a single source file
# - tests that are built from multiple source files (sub-file identifiers a,b,c,...) with a single main()
# - class-based cpp tests that have good and bad files (sub-file identifiers _good1 and _bad) each with a main()
# - virtual-based cpp tests that consist of a header and other source files (identifiers in guide) with a single main()
# some tests are bad-only, but this does not require special consideration

# collect all source files corresponding to windows tests, we don't want to build them
# glob recurse used to handle directories split up due to size (see user's guide)
file(GLOB_RECURSE WINDOWS_FILES CWE*w32*.c* CWE*wchar_t*.c* CWE*w32*.h CWE*wchar_t*.h)

# collect all test sources and remove windows files
file(GLOB_RECURSE SOURCE_FILES CWE*.c CWE*.cpp)
list(REMOVE_ITEM SOURCE_FILES ${WINDOWS_FILES} "") # empty string in case windows files is empty

foreach(SOURCE_FILE ${SOURCE_FILES})
  get_filename_component(SOURCE_NAME "${SOURCE_FILE}" NAME)
  get_filename_component(SOURCE_DIRECTORY "${SOURCE_FILE}" DIRECTORY)

  # get the name of the test that this source file corresponds to (cf user's guide section 3.4.1)
  # filename format: "CWE", CWE ID, "_", Shortened CWE entry name, "__", Functional Variant Name, "_",
  # Flow Variant, Sub-file Identifier, ".", extension
  string(REGEX MATCH "^CWE[0-9]+_.+__.+_[0-9][0-9]" EXECUTABLE_NAME "${SOURCE_NAME}")

  # don't make multiple executables for the same test
  if(NOT TARGET "${EXECUTABLE_NAME}-good")

    # if this is a class-based test, we need to build good and bad cases with
    # separate source files because each has a main
    list(FIND SOURCE_FILES "${SOURCE_DIRECTORY}/${EXECUTABLE_NAME}_good1.cpp" CLASS_TEST)
    if(NOT ${CLASS_TEST} EQUAL "-1")

      # add good executable
      add_executable("${EXECUTABLE_NAME}-good" "${SOURCE_DIRECTORY}/${EXECUTABLE_NAME}_good1.cpp")
      set_target_properties("${EXECUTABLE_NAME}-good"
        PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/good"
        COMPILE_DEFINITIONS OMITBAD
      )

      # add bad executable
      add_executable("${EXECUTABLE_NAME}-bad" "${SOURCE_DIRECTORY}/${EXECUTABLE_NAME}_bad.cpp")
      set_target_properties("${EXECUTABLE_NAME}-bad"
        PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/bad"
        COMPILE_DEFINITIONS OMITGOOD
      )

    # otherwise we can build both executables with all files corresponding to the
    # test
    else(NOT ${CLASS_TEST} EQUAL "-1")

      # collect all source files corresponding to this test - recursive glob here too expensive
      set(EXECUTABLE_SOURCES ${SOURCE_FILES})
      list(FILTER EXECUTABLE_SOURCES INCLUDE REGEX "^${SOURCE_DIRECTORY}/${EXECUTABLE_NAME}")

      # add good executable
      add_executable("${EXECUTABLE_NAME}-good" ${EXECUTABLE_SOURCES})
      set_target_properties("${EXECUTABLE_NAME}-good"
        PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/good"
        COMPILE_DEFINITIONS OMITBAD
      )

      # add bad executable
      add_executable("${EXECUTABLE_NAME}-bad" ${EXECUTABLE_SOURCES})
      set_target_properties("${EXECUTABLE_NAME}-bad"
        PROPERTIES
        RUNTIME_OUTPUT_DIRECTORY "${CMAKE_RUNTIME_OUTPUT_DIRECTORY}/bad"
        COMPILE_DEFINITIONS OMITGOOD
      )

    endif(NOT ${CLASS_TEST} EQUAL "-1")
  endif(NOT TARGET "${EXECUTABLE_NAME}-good")
endforeach(SOURCE_FILE ${SOURCE_FILES})
