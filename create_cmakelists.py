#!/usr/bin/env python3
#
# Running this script will update the batch and make files that compile the test cases
# for each CWE into a separate .exe or executable file.  This script also edits source code
# and header files needed for a successful compilation with these files.
#
#
import os, glob, shutil, time, sys

# add parent directory to search path so we can use py_common
sys.path.append("..")

import py_common

import update_main_cpp_and_testcases_h

def create_makefile(cwe, is_dir_split):
    contents = ""
    contents += "CC=/usr/bin/gcc\n"
    contents += "CPP=/usr/bin/g++\n"
    contents += "DEBUG=-g\n"
    contents += "CFLAGS=-c\n"
    contents += "LFLAGS=-lpthread -lm\n"
    contents += "LD=ld\n"
    contents += "INCLUDE_MAIN=-DINCLUDEMAIN\n"

    if is_dir_split:
        contents += "\nINCLUDES=-I ../../../testcasesupport\n"
    else:
        contents += "\nINCLUDES=-I ../../testcasesupport\n"

    contents += "\nMAIN=main_linux.cpp\n"
    contents += "MAIN_OBJECT=$(MAIN:.cpp=.o)\n"

    if is_dir_split:
        contents += "\nC_SUPPORT_PATH=../../../testcasesupport/\n"
    else:
        contents += "\nC_SUPPORT_PATH=../../testcasesupport/\n"

    contents += "C_SUPPORT_FILES=$(C_SUPPORT_PATH)io.c $(C_SUPPORT_PATH)std_thread.c\n"
    contents += "C_SUPPORT_OBJECTS=io.o std_thread.o\n"

    contents += "FILTER_OUT=$(wildcard CWE*w32*.c*) $(wildcard CWE*wchar_t*.c*)\n"

    contents += "\n# only grab the .c files without \"w32\" or \"wchar_t\" in the name\n"
    contents += "C_SOURCES=$(filter-out $(FILTER_OUT),$(wildcard CWE*.c))\n"
    contents += "C_OBJECTS=$(C_SOURCES:.c=.o)\n"

    contents += "\n# only grab the .cpp files without \"w32\" or \"wchar_t\" in the name\n"
    contents += "CPP_SOURCES=$(filter-out $(FILTER_OUT),$(wildcard CWE*.cpp))\n"
    contents += "CPP_OBJECTS=$(CPP_SOURCES:.cpp=.o)\n"

    contents += "\nSIMPLES=$(filter-out $(FILTER_OUT), $(wildcard CWE*0.c*) $(wildcard CWE*1.c*) $(wildcard CWE*2.c*) $(wildcard CWE*3.c*) $(wildcard CWE*4.c*)) \\\n"
    contents += "        $(filter-out $(FILTER_OUT), $(wildcard CWE*5.c*) $(wildcard CWE*6.c*) $(wildcard CWE*7.c*) $(wildcard CWE*8.c*) $(wildcard CWE*9.c*))\n"
    contents += "SIMPLES_C=$(filter-out $(CPP_SOURCES), $(SIMPLES))\n"
    contents += "SIMPLES_CPP=$(filter-out $(C_SOURCES), $(SIMPLES))\n\n"

    contents += "LETTEREDS=$(filter-out $(FILTER_OUT), $(wildcard CWE*a.c*))\n"
    contents += "LETTEREDS_C=$(subst a.,.,$(filter-out $(CPP_SOURCES), $(LETTEREDS)))\n"
    contents += "LETTEREDS_CPP=$(subst a.,.,$(filter-out $(C_SOURCES), $(LETTEREDS)))\n\n"

    contents += "GOOD1S=$(filter-out $(FILTER_OUT), $(wildcard CWE*_good1.cpp))\n"
    contents += "BADS=$(subst _good1.,_bad.,$(GOOD1S))\n\n"

    contents += "INDIVIDUALS_C=$(addsuffix .out, $(sort $(subst .c,,$(SIMPLES_C) $(LETTEREDS_C))))\n"
    contents += "INDIVIDUALS_CPP=$(addsuffix .out, $(sort $(subst .cpp,,$(SIMPLES_CPP) $(LETTEREDS_CPP) $(BADS) $(GOOD1S))))\n"

    contents += "\nOBJECTS=$(MAIN_OBJECT) $(C_OBJECTS) $(CPP_OBJECTS) $(C_SUPPORT_OBJECTS)\n"
    contents += "# TARGET is the only line in this file specific to the CWE\n"
    contents += "TARGET=" + cwe + "\n"

    contents += "\nall: $(TARGET)\n"

    contents += "\npartial.o: $(C_OBJECTS) $(CPP_OBJECTS)\n"
    contents += "	$(LD) -r $(C_OBJECTS) $(CPP_OBJECTS) -o $@\n"

    contents += "\nindividuals: $(INDIVIDUALS_C) $(INDIVIDUALS_CPP)\n\n"
    contents += "$(INDIVIDUALS_C): $(C_SUPPORT_OBJECTS)\n"
    contents += "	$(CC) $(INCLUDES) $(INCLUDE_MAIN) -o $@ $(wildcard $(subst .out,,$@)*.c) $(C_SUPPORT_OBJECTS) $(LFLAGS)\n\n"
    contents += "$(INDIVIDUALS_CPP): $(C_SUPPORT_OBJECTS)\n"
    contents += "	$(CPP) $(INCLUDES) $(INCLUDE_MAIN) -o $@ $(wildcard $(subst .out,,$@)*.cpp) $(C_SUPPORT_OBJECTS) $(LFLAGS)\n"

    contents += "\n$(TARGET) : $(OBJECTS)\n"
    contents += "	$(CPP) $(LFLAGS) $(OBJECTS) -o $(TARGET)\n"

    contents += "\n$(C_OBJECTS) : %.o:%.c \n"
    contents += "	$(CC) $(CFLAGS) $(INCLUDES) $^ -o $@\n"

    contents += "\n$(CPP_OBJECTS) : %.o:%.cpp\n"
    contents += "	$(CPP) $(CFLAGS) $(INCLUDES) $^ -o $@\n"

    contents += "\n$(C_SUPPORT_OBJECTS) : $(C_SUPPORT_FILES)\n"
    contents += "	$(CC) $(CFLAGS) $(INCLUDES) $(C_SUPPORT_PATH)$(@:.o=.c) -o $@\n"

    contents += "\n$(MAIN_OBJECT) : $(MAIN)\n"
    contents += "	$(CC) $(CFLAGS) $(INCLUDES) $(MAIN) -o $@\n"

    contents += "\nclean:\n"
    contents += "	rm -rf *.o *.out $(TARGET)\n"

    return contents


def check_if_c_files_exist(directory):
    files = py_common.find_files_in_dir(directory, "CWE.*\.c$")
    if len(files) > 0:
        return True

    return False


def check_if_cpp_files_exist(directory):
    files = py_common.find_files_in_dir(directory, "CWE.*\.cpp$")
    if len(files) > 0:
        return True

    return False

# may need /bigobj flag: http://msdn.microsoft.com/en-us/library/ms173499%28VS.90%29.aspx
# Only one of our C/C++ tools requires debug flags so the debug flags that are set are specific for this tool
debug_flags = '/I"..\\..\\testcasesupport" /Zi /Od /MTd /GS- /INCREMENTAL:NO /DEBUG /W3 /bigobj /EHsc /nologo' # if this line is modified, change the one below
split_debug_flags = '/I"..\\..\\..\\testcasesupport" /Zi /Od /MTd /GS- /INCREMENTAL:NO /DEBUG /W3 /bigobj /EHsc /nologo'
linker_flags = '/I"..\\..\\testcasesupport" /W3 /MT /GS /RTC1 /bigobj /EHsc /nologo' # if this line is modified, change the one below
split_linker_flags = '/I"..\\..\\..\\testcasesupport" /W3 /MT /GS /RTC1 /bigobj /EHsc /nologo'
compile_flags = linker_flags + " /c"
split_compile_flags = split_linker_flags + " /c"
debug_compile_flags = debug_flags + " /c"
split_debug_compile_flags = split_debug_flags + " /c"
if __name__ == "__main__":

    # check if ./testcases directory exists, if not, we are running
    # from wrong working directory
    if not os.path.exists("testcases"):
        py_common.print_with_timestamp("Wrong working directory; could not find testcases directory")
        exit()

    # default values which are used if no arguments are passed on command line
    cwe_regex = "CWE"
    # get the CWE directories in testcases folder
    cwe_dirs = py_common.find_directories_in_dir("testcases", cwe_regex)
    # only allow directories
    cwe_dirs = filter(lambda x: os.path.isdir(x), cwe_dirs)

    for dir in cwe_dirs:
        if 's01' in os.listdir(dir):
            is_dir_split = True
        else:
            is_dir_split = False

        if is_dir_split:
            # get the list of subdirectories
            cwe_sub_dirs = py_common.find_directories_in_dir(dir, "^s\d.*")

            for sub_dir in cwe_sub_dirs:
                # update main.cpp/testcases.h to call only this functional variant's testcases
                testcase_files = update_main_cpp_and_testcases_h.build_list_of_primary_c_cpp_testcase_files(sub_dir, None)

                # get the CWE number from the directory name (not the full path since that may also have the string CWE in it)
                this_cwe_dir = os.path.basename(dir)
                cwe_index = this_cwe_dir.index("CWE")
                unders_index = this_cwe_dir.index("_", cwe_index)
                cwe = this_cwe_dir[cwe_index:unders_index]
                sub_dir_number = os.path.basename(sub_dir)
                cwe = cwe + "_" + sub_dir_number

                # check if any .c files exist to compile
                c_files_exist = check_if_c_files_exist(sub_dir)
                cpp_files_exist = check_if_cpp_files_exist(sub_dir)

                linux_testcase_exists = False
                for file in testcase_files:
                    if ('w32' not in file) and ('wchar_t' not in file):
                        linux_testcase_exists = True
                        break

                # only generate main_linux.cpp and Makefile if there are Linux test cases for this CWE
                if linux_testcase_exists:
                    makefile_contents = create_makefile(cwe, is_dir_split)
                    makefile_fullpath = os.path.join(sub_dir, "Makefile")
                    py_common.write_file(makefile_fullpath, makefile_contents)
                else:
                    py_common.print_with_timestamp("No Makefile created for " + cwe + ". All of the test cases are Windows-specific.")
        else:
            # update main.cpp/testcases.h to call only this cwe's testcases
            testcase_files = update_main_cpp_and_testcases_h.build_list_of_primary_c_cpp_testcase_files(dir, None)

            # get the CWE number from the directory name (not the full path since that may also have the string CWE in it)
            thisdir = os.path.basename(dir)
            cwe_index = thisdir.index("CWE")
            unders_index = thisdir.index("_", cwe_index)
            cwe = thisdir[cwe_index:unders_index]

            # check if any .c files exist to compile
            c_files_exist = check_if_c_files_exist(dir)
            cpp_files_exist = check_if_cpp_files_exist(dir)

            linux_testcase_exists = False
            for file in testcase_files:
                if ('w32' not in file) and ('wchar_t' not in file):
                    linux_testcase_exists = True
                    break

            # only generate main_linux.cpp and Makefile if there are Linux test cases for this CWE
            if linux_testcase_exists:
                makefile_contents = create_makefile(cwe, is_dir_split)
                makefile_fullpath = os.path.join(dir, "Makefile")
                py_common.write_file(makefile_fullpath, makefile_contents)
            else:
                py_common.print_with_timestamp("No Makefile created for " + cwe + ". All of the test cases are Windows-specific.")
