# Copyright (C) 2020 FireEye, Inc. All Rights Reserved.
# Licensed under the Apache License, Version 2.0 (the "License");
#  you may not use this file except in compliance with the License.
# You may obtain a copy of the License at: [package root]/LICENSE.txt
# Unless required by applicable law or agreed to in writing, software distributed under the License
#  is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and limitations under the License.

import sys
import builtins

from capa.features.insn import API

MIN_STACKSTRING_LEN = 8


def xor_static(data, i):
    if sys.version_info >= (3, 0):
        return bytes(c ^ i for c in data)
    else:
        return "".join(chr(ord(c) ^ i) for c in data)


def is_aw_function(function_name):
    """
    is the given function name an A/W function?
    these are variants of functions that, on Windows, accept either a narrow or wide string.
    """
    if len(function_name) < 2:
        return False

    # last character should be 'A' or 'W'
    if function_name[-1] not in ("A", "W"):
        return False

    # second to last character should be lowercase letter
    return "a" <= function_name[-2] <= "z" or "0" <= function_name[-2] <= "9"


def generate_api_features(apiname, va):
    """
    for a given function name and address, generate API names.
    we over-generate features to make matching easier.
    these include:
      - kernel32.CreateFileA
      - kernel32.CreateFile
      - CreateFileA
      - CreateFile
    """
    # (kernel32.CreateFileA, 0x401000)
    yield API(apiname), va

    if is_aw_function(apiname):
        # (kernel32.CreateFile, 0x401000)
        yield API(apiname[:-1]), va

    if "." in apiname:
        modname, impname = apiname.split(".")
        # strip modname to support importname-only matching
        # (CreateFileA, 0x401000)
        yield API(impname), va

        if is_aw_function(impname):
            # (CreateFile, 0x401000)
            yield API(impname[:-1]), va


def all_zeros(bytez):
    return all(b == 0 for b in builtins.bytes(bytez))
