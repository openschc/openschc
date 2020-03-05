#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PYTHONPATH must be set to openschc/src
from contextlib import redirect_stdout
from pathlib import Path
import glob
import importlib
import os
import shutil

# Parameters
golden_samples_folder = "golden_samples"
input_test_folder = "packets_rules"

# Delete previous directory, in case tests are removed
shutil.rmtree(golden_samples_folder, ignore_errors=True)
os.mkdir(golden_samples_folder)


class DummyStdout:
    """Used to disable write to stdout
    """

    def write(self, _):
        pass


for file_name in glob.glob(f"./{input_test_folder}/[0-9][0-9]-*.py"):
    file_name_stem = Path(file_name).stem
    # Disable output to loaded test prints
    with redirect_stdout(DummyStdout()):
        # Import each test and generate golden sample
        test = __import__(f"{input_test_folder}.{file_name_stem}")
        with open(f"{golden_samples_folder}/{file_name_stem}.txt", "w") as f:
            getattr(test, file_name_stem).result.save_to_file(f)
