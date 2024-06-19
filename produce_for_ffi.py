#!/usr/bin/env python3

# usage: python3 produce-for-ffi.py

# This script is used to split a C file into a set of C files that are FFI compatible.


# find tokens in string
def token_list_in_string(string, tokens):
    for token in tokens:
        if token in string:
            return True
    return False


# remove bit field
import re


def bit_field_remove_change_line(line):
    if token_list_in_string(line, ["[", "]", "{", "}"]):
        return line
    return re.sub(r"[ ]*:[ ]*[^;'\"]+", "", line)


# example lines for testing and debugging
example_lines = """
typedef enum{
    SDL_FALSE = 0,
    SDL_TRUE = 1
} SDL_bool;

void example_function1(){
    if(1){
        do_something();
    }
}

"""  # lines end of string

# debugging mode
debug_mode = False

# enable only for debugging
if debug_mode:
    print("===", "example_lines:", example_lines)  # debugging inspection

# split example lines
example_lines = example_lines.split("\n")

# debugging skip, enable usually
if not debug_mode:
    file_lines = open("includes_output.h").readlines()  # debugging skip, enable usually

# choose lines to parse
lines = example_lines
lines = file_lines  # debugging skips this, enable normally

# initializations
is_inside_function = False
is_inside_aggregate = False
inside_aggregate_level = 0
nesting_level = 0
some_aggregate_pending_to_close = False


# comment out end of function or aggregate
def comment_out_end_of(type, nesting_level):
    nesting_level_zero = nesting_level == 0
    special_character = nesting_level_zero and "@" or ""
    return ' /*$ end_of("' + type + '") ' + special_character + "$*/ "


# debugging inspection
print_inside_function = debug_mode  # debugging inspection

# main loop
for line in lines:

    # sanity checks
    assert nesting_level >= 0  # nesting level should be non-negative
    assert inside_aggregate_level >= 0  # inside aggregate level should be non-negative

    # remove trailing newline character
    line = line.rstrip("\r\n")  # remove trailing newline character

    # remove bit field
    line = bit_field_remove_change_line(line)

    # remove trailing whitespace
    line_before_strip = line
    line = line.lstrip()

    # line out before strip has trailing whitespace
    line_out = line_before_strip

    # skip empty lines and comments
    if line == "":
        continue
    if line.startswith("#"):
        continue

    # print inside function when not hidden
    if not print_inside_function and is_inside_function:
        line_out = None  # "hides" lines inside function

    # open close line difference
    def open_close_line(line):
        return line.count("{") - line.count("}")

    # nesting level
    nesting_level_before_open_close_line = nesting_level
    nesting_level += open_close_line(line)

    # inside aggregate (struct, enum, union)
    some_aggregate = token_list_in_string(line, ["struct", "enum", "union"])

    if not is_inside_function and (
        some_aggregate or (is_inside_aggregate and open_close_line(line) > 0)
    ):
        inside_aggregate_level += open_close_line(line)
        is_inside_aggregate = True

    # outside aggregate (end of aggregate: struct, enum, union)
    elif (
        is_inside_aggregate
        and inside_aggregate_level >= 0
        and open_close_line(line) <= 0
    ):
        inside_aggregate_level += open_close_line(line)
        if inside_aggregate_level == 0:
            some_aggregate_pending_to_close = True
    if some_aggregate_pending_to_close and (";" in line):
        is_inside_aggregate = False
        line_out += comment_out_end_of("aggregate", nesting_level)
        some_aggregate_pending_to_close = False

    # inside function
    if (
        inside_aggregate_level == 0
        and open_close_line(line) > 0
        and is_inside_function == False
        and nesting_level_before_open_close_line == 0
    ):
        is_inside_function = True

        if not print_inside_function:
            line_out = line[:-1]  # removes trailing "{" character (pre-condition)
        if line_out.strip() == "":
            line_out = None  # dont print empty line

    # outside function (end of function)
    elif (
        open_close_line(line) < 0 and is_inside_function == True and nesting_level == 0
    ):
        is_inside_function = False
        line_out = ";"  # no function "body"
        line_out += comment_out_end_of("function", nesting_level)

    # print if not None
    if line_out != None:
        # rewrite case
        line_out = line_out.replace("_Float16 _Complex", "_Complex")
        # print line with comment
        print(
            line_out,
            " // nesting_level :",
            nesting_level,
            "inside_function :",
            is_inside_function,
            "inside_aggregate_level :",
            inside_aggregate_level,
        )

    # debugging inspection
    if debug_mode:
        print(
            "===",
            "nesting_level:",
            nesting_level,
            "is_inside_function:",
            is_inside_function,
            "is_inside_aggregate:",
            is_inside_aggregate,
        )

# termination checks

# asserts for sanity checks
assert nesting_level >= 0  # nesting level should be non-negative
assert inside_aggregate_level >= 0  # inside aggregate level should be non-negative
assert (
    inside_aggregate_level == 0 and is_inside_aggregate == False
)  # inside aggregate should be False

# sanity checks for termination
if is_inside_function:
    print(
        "// WARNING: inside_function. not closed properly. nesting_level :",
        nesting_level,
    )
if inside_aggregate_level > 0 or is_inside_aggregate:
    print(
        "// WARNING: inside_aggregate. not closed properly. nesting_level :",
        nesting_level,
    )
if nesting_level > 0:
    print("// WARNING: nesting_level not zero. nesting_level :", nesting_level)

# successful termination
if (
    not is_inside_function
    and not is_inside_aggregate
    and inside_aggregate_level == 0
    and nesting_level == 0
):
    print("\n // SUCCESS: termination checks passed.")
