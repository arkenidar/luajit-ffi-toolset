#!/usr/bin/env bash

# gcc
gcc -E includes_input.h | grep -v "^#" | grep -v "^_Static_assert" > includes_output.h

# python && luajit
python produce_for_ffi.py > produced_for_ffi.h && luajit produced_test1.lua
