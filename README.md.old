# SCHC Implementation (for micropython and Python3).

This document's objective is to help one use the OpenSCHC implementation of the SCHC protocol.

ToDo - See branches [here](https://github.com/openschc/openschc/network).

##  openschc
OpenSCHC (Static Context Header Compression) is an open source implementation of the
[SCHC protocol](https://datatracker.ietf.org/doc/draft-ietf-lpwan-ipv6-static-context-hc/?include_text=1)

It is licensed under the [MIT License](https://github.com/openschc/openschc/blob/master/LICENSE).

Further documentation about OpenSCHC is available
[here](https://github.com/openschc/openschc/wiki).

## Understanding the architecture
A global architecture of openSCHC implementation is shown below:

<img style="float: right;" src="images/openSHCH_arch.png">

The *Rule Manager* stores a set of Rules and provides methods to install or retreive Rules.

Rules are composed of two elements:
* A *RuleID* which identifies the Rule by its number, and
* A *content* which contains an array of fields. For details, refer to the [SCHC protocol](https://datatracker.ietf.org/doc/draft-ietf-lpwan-ipv6-static-context-hc/?include_text=1)

The *App 1 ... App n* are the applications that invoke the *SCHC Orchestrator* to run the necessary SCHC operations, which are briefly
defined below:

*Compression* is used on the sender side to compress the header of a packet provided by the App,
using a specific rule (identified by its RuleID).
*Decompression*: on the receiver side, upon receiving a compressed packet,
the Decompresser is invoked to rebuild the original packet, using the Rule identified by the RuleID carried in the compressed packet.

*Fragmentation* is invoked on the sender side with a RuleID to generate a set of fragments out of a packet (compressed or uncompressed).
*Reassembly* is used on the receiver side to reconstruct the packet out of the set of fragments.

Fragmentation modes and the associated parameters are described in the [SCHC
protocol](https://datatracker.ietf.org/doc/draft-ietf-lpwan-ipv6-static-context-hc/?include_text=1).

*Network Connector* interfaces to a physical model to a real LPWAN network such as LoRa or Sigfox,
or to a link simulator.

## Setting up the environment using Python3
Step 1 : Make sure you have a Python3 version installed. Check
your python version with the following command and update the python version, if
necessary
```sh
   python --version
```
Step 2: Clone the [OpenSCHC repository](https://github.com/openschc/openschc).

Step 3: For testing a simple example using SCHC under different scenarios, see [here](https://github.com/openschc/openschc/blob/master/src/README.md).

## Setting up the environment using micropython
Micropython is Python3 for microcontrollers, but it also runs on Windows/Linux/Unix
machine. Ues this to test your code on a computer before trying on an embedded device.

Step 1: install micropython. Some pointers are indicated
below. For more details, please refer to the relevant documentation.

* Micropython GitHub project: ```https://github.com/micropython/micropython```

* For Linux distribs, specific instructions for the Unix port of micropython can be found at (it should be noted that this has not been tested on all
Linux distribs):
    ```https://github.com/micropython/micropython#the-unix-version```

* On OSX
  * either recompile from the GitHub project, see ```https://github.com/micropython/micropython/wiki/Micro-Python-on-Mac-OSX```
  * or install with Brew: ```brew install micropython```
  * Note: on OS X, if you get an error message about missing libffi, try the fix described in
 ```https://stackoverflow.com/questions/22875270/error-installing-bcrypt-with-pip-on-os-x-cant-find-ffi-h-libffi-is-installed/25854749#25854749```

Step 2: download the needed micropython modules.
Modules to be installed in order to run SCHC are:
  * argparse.py : ```./micropython -m upip install micropython-argparse```
  * copy.py : ```./micropython -m upip install micropython-copy```
  * types.py : ```./micropython -m upip install micropython-types```

Libs are located under ```~/.micropython/lib```

Step 3: Test the SCHC C/D and F/R

The following command line will simulate a simple ICMPv6 echo request/response using the SCHC protocol between
the SCHC device and the gateway. The input JSON files are part of the SCHC
orchestrator configuration (as you can see in the architecture figure above), and
the loss parameters configure the link simulator to simulate packet drops on the radio link.

As you can see from the results of the below command, the 1st and the 2nd SCHC
fragments are lost. Therefore, when the sender transmits the last fragment that includes
the MIC, the receiver MIC check fails.
Consequently, the sender retransmits the 1st and 2nd fragments and when the receiver
receives all the fragments with the MIC, the transmission is successful.

```  
./micropython $youropenschcdirectory/src/test_newschc.py --context
example/context-100.json --rule-comp example/comp-rule-100.json --rule-fragin
example/frag-rule-101.json --rule-fragout example/frag-rule-102.json --data-file
test/icmpv6.dmp --loss-mode list --loss-param 1,2
```




## File classification

Refer to the [File Classification](docs/File_Classification.md) for an overview
of the source code repository.



See the [Wiki](https://github.com/openschc/openschc/wiki) for documentation.

See branches [here](https://github.com/openschc/openschc/network).
