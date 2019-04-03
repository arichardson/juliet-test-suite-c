project(juliet-c)



# TODO: build good testcases, check they don't crash with CHERI;
set(GOOD_FLAGS -DOMITBAD -DINCLUDE_MAIN)
# TODO: build the testcase with the flaw and check that they crash:
set(BAD_FLAGS -DOMITGOOD -DINCLUDE_MAIN)

# TODO: handle other cases, but for now only look at CWEs relevant to CHERI



# TODO: testcases/CWE469_Use_of_Pointer_Subtraction_to_Determine_Size ?
