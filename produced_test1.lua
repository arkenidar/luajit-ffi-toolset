local function lines_with_number(input_string)
  local line_number = 1
  for line in input_string:gmatch("([^\r\n]*)[\r\n]?") do
    print(line_number, line)
    line_number = line_number + 1
  end
end

local ffi = require("ffi")

local file_path = "produced_for_ffi.h"

local function process_segment(text_segment)
  io.write("[[\n")
  lines_with_number(text_segment)
  io.write("]]\n\n")
  ffi.cdef(text_segment)
end

local buffer = ""
local lines_iterator = io.lines(file_path)
for line in lines_iterator do
  buffer = buffer .. line .. "\n"

  if string.find(line, "@$*/", 1, true) ~= nil then
    process_segment(buffer)
    buffer = ""
  end
end

if buffer ~= "" then
  process_segment(buffer)
end

print("-----------------------------")
print("successful completion of cdef")
print("-----------------------------")
