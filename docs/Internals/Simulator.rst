Simulator
*********

Introduction
============

OpenSCHC includes a way to run simple simulations:
to use it, one sets up, one creates nodes,

An example of simulation is in `examples/simulator`.



Configuration
=============

The configuration is in a dictionary with the following fields

*  There have been 4 different versions of logging :

  * "log" (boolean): the initial logging system (with clock). Not used much lately.
  * "enable-print" (boolean): the print statements that have been added to do debugging.
  * "enable-trace" (boolean): the trace displays only the packet exchanged between nodes.
  * the record system to record the state of nodes at each event.

When used, the record system uses the following entries in the dictionary:
  * "record.enable" (boolean): should loging
  * "record.directory" (string): the name of the directory where all state/logs will be stored
  * "record.format" (string): the format with which the information is stored ("pprint" or "json")
  * "record.quiet" (string): disable all output from screen (including trace)

Testing
=======

An example of simulation in `examples/simulator` can be run through the script `run_simul.sh`.
