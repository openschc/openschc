# Interoperability test tools


## Summary
This folder helps with interroperability testing:

* `generate_golden_samples.py` to create reference test vector using OpenSCHC
* `compare_to_golden_samples.py` to compare a DUT with golden samples
* `packet_rules` is the folder containing the parameters (packets and rules) to generate test vectors
* `golden_samples` is the fodler containing the references test vectors

Remember to setup PYTHONPATH per https://github.com/openschc/openschc/tree/master/examples

## Usage - `generate_golden_samples.py`
Call `python generate_golden_samples.py`, no parameters. Results are generated in directory `golden_samples`.

## Usage - `compare_to_golden_samples.py`
Call `python compare_to_golden_samples.py dut_folder_path`

Example:
```
./compare_to_golden_samples.py dut
01-NO_COMPRESSION_ALIGNED...OK

02-NO_COMPRESSION_NOT_ALIGNED...OK

03-IPv6-UDP-full-compression...ERROR: DUT file does not exists

04-IPv6-UDP-all-CDA...ERROR:
 - Golden sample:       e67c641d2c84140c0414/80
 - DUT:                 e67c641dAc84140c0414/80
                                ^                     
```

## File format
1. Data are represented as hexadecimal encoded string.
2. If padding is required `0` bits are added to the right.
3. The size in bits is then appened after a slash, encoded as integer and expressed as ascii.
4. There should be a new line character (`\n`) at the end of each line.

Example:
 Binary data `00100101 01101` (13 bits) should be represented as `2568/13\n`
