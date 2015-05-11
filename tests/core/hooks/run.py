#!/usr/bin/env python2

import os
import sys
import commands
import atexit

TEST_NAME = "core hooks"

# those globales give infos on all tests / errored tests
ERRORS = 0
TESTS = 0

# common action message display
def print_action(msg):
    sys.stdout.write("\033[1;33m" + "[*] ")
    sys.stdout.write("\033[0;33m" + msg + "\033[0m\n")

# get git repository's root directory.
print_action("compiling BEURK for %r testing ..." % TEST_NAME)
ROOTDIR=commands.getoutput("git rev-parse --show-toplevel").strip()
assert os.path.isdir(ROOTDIR)

# compile BEURK for hooks testing
buildcmd = "BEURK_DEBUG_LEVEL=1 %s/build %s/beurk.conf"
assert os.system(buildcmd % (ROOTDIR, ROOTDIR)) == 0

# move to script directory
os.chdir(os.path.dirname(sys.argv[0]))

# test a given function hook given it's expected arguments
def test_hook(*args):
    global ERRORS
    global TESTS
    TESTS += 1

    testinfo = args[0]+"() " + " ".join([repr(x) for x in args[1:]])
    print("")
    print_action("Running test -> %s  ..." % testinfo)
    cmd = "gcc %s -o %s" % (args[0]+".c", args[0])
    print(cmd)
    ret = commands.getstatusoutput(cmd)
    if ret[0] == 0:
        cmd = "LD_PRELOAD=" + ROOTDIR + "/libselinux.so "
        cmd += "./" + " ".join([str(x) for x in args])
        cmd += " 2>&1"
        print(cmd)
        ret = commands.getstatusoutput(cmd)
        os.unlink(args[0])
    if "[BEURK_INFO]: " + args[0] in ret[1]:
        print("\033[32mOK!\033[0m")
        return True
    # elif ret[0] or "[BEURK_ERROR" in ret[1]:
    else:
        print("\033[31mFAIL!\033[0m")
        ERRORS += 1
        return False


###############################################################################
# open() @ libc
###############################################################################

test_hook("open", "test1", os.O_CREAT, 0o777)
os.unlink("test1")

test_hook("open", "test1", os.O_RDONLY)
test_hook("open")
test_hook("open", "test1", os.O_RDONLY)



###############################################################################
# FOOTER
###############################################################################
if ERRORS:
    msg = "\033[31m[-] Some %r tests failed (%d of %d)\033[0m"
    sys.exit(msg % (TEST_NAME, ERRORS, TESTS))
else:
    print("\033[32m[+] All %r tests passed ! (%d)\033[0m" % (TEST_NAME, TESTS))
    sys.exit(0)
