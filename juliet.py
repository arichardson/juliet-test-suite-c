#!/usr/bin/env python3


import os, re, argparse, shutil, subprocess


def juliet_print(string):
    print("========== " + string + " ==========")


def clean(path):
    try:
        os.remove(path + "/CMakeLists.txt")
        os.remove(path + "/CMakeCache.txt")
        os.remove(path + "/cmake_install.cmake")
        os.remove(path + "/Makefile")
        shutil.rmtree(path + "/CMakeFiles")
    except OSError:
        pass


def generate(path, keep_going):
    shutil.copy("CMakeLists.txt", path)
    retcode = subprocess.Popen(["cmake", "."], cwd=path).wait()
    if retcode != 0 and not keep_going:
        juliet_print("error generating " + path + " - stopping")
        exit()


def make(path, keep_going):
    if keep_going:
        subprocess.Popen(["make", "-j16", "-k"], cwd=path).wait()
    else:
        retcode = subprocess.Popen(["make", "-j16"], cwd=path).wait()
        if retcode != 0:
            juliet_print("error making " + path + " - stopping")
            exit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="build and run Juliet test cases for targeted CWEs")
    parser.add_argument("CWEs", metavar="N", type=int, nargs="*", help="a CWE number to target")
    parser.add_argument("-c", "--clean", action="store_true", help="clean all CMake and make files for the targeted CWEs")
    parser.add_argument("-g", "--generate", action="store_true", help="use CMake to generate Makefiles for the targeted CWEs")
    parser.add_argument("-m", "--make", action="store_true", help="use make to build test cases for the targeted CWES")
    parser.add_argument("-r", "--run", action="store_true", help="run tests for the targeted CWEs")
    parser.add_argument("-a", "--all", action="store_true", help="target all CWEs")
    parser.add_argument("-k", "--keep-going", action="store_true", help="keep going in case of build failures")
    args = parser.parse_args()
    args.CWEs = set(args.CWEs)

    testcases = "testcases"
    if not os.path.exists(testcases):
        juliet_print("no testcases directory")
        exit()

    if args.generate and not os.path.exists("CMakeLists.txt"):
        juliet_print("no CMakeLists.txt")
        exit()

    for subdir in os.listdir(testcases):
        match = re.search("^CWE(\d+)", subdir)
        if match != None and (int(match.group(1)) in args.CWEs or args.all):
            path = testcases + "/" + subdir
            if args.clean:
                juliet_print("cleaning " + path)
                clean(path)
            if args.generate:
                juliet_print("generating " + path)
                generate(path, args.keep_going)
            if args.make:
                juliet_print("making " + path)
                make(path, args.keep_going)
            if args.run:
                juliet_print("running " + path)
                pass # TODO
