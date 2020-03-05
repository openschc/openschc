#!/usr/bin/env python
# -*- coding: utf-8 -*-
# PYTHONPATH must be set to openschc/src
from contextlib import redirect_stdout
from pathlib import Path
import argparse
import glob
import importlib
import os

# Parameters
golden_samples_folder = "golden_samples"

# Create CLI interface
parser = argparse.ArgumentParser(
    description="Compare a set of tests with the golden sampes"
)
parser.add_argument(
    "dut_folder", help="Folder containing data to compare with golden samples"
)
args = parser.parse_args()


def generate_positionnal_changes_indicator(string1, string2):
    """ Generate a string showing the differences between two strings
    """
    changes = ""
    if len(string1) < len(string2):
        string_iteration = string1
        string_to_compare = string2
    else:
        string_iteration = string2
        string_to_compare = string1
    for i in range(len(string_iteration)):
        if string_iteration[i] == string_to_compare[i]:
            changes += " "
        else:
            changes += "^"
    return changes


# Iterate on all golden samples
for file_name in sorted(glob.glob(f"./{golden_samples_folder}/[0-9][0-9]-*.txt")):
    file_name_stem = Path(file_name).stem
    status = True
    print(f"{file_name_stem}...", end="")

    # Open files
    try:
        with open(file_name, "r") as f_golden_sample, open(
            f"{args.dut_folder}/{file_name_stem}.txt", "r"
        ) as f_dut:
            for golden_sample_line in f_golden_sample.readlines():
                dut_line = f_dut.readline()
                if golden_sample_line != dut_line:
                    status = False
                    changes = generate_positionnal_changes_indicator(
                        golden_sample_line, dut_line
                    )
                    print("\033[91mERROR\033[0m:")
                    print(f" - Golden sample:\t{golden_sample_line[:-1]}")
                    print(f" - DUT:\t\t\t{dut_line[:-1]}")
                    print(f"\t\t\t{changes}\n")
                    break
            if status:
                print(f"\033[92mOK\033[0m\n")
    except FileNotFoundError:
        print("\033[91mERROR\033[0m: DUT file does not exists\n")
