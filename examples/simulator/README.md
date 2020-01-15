
## Simulator

A simulator and a set of classes are available for OpenSCHC.
They are in the files `src/net_sim_*`, and `src/net_sim_builder.py` provides a nicer upper-level API  to use them.

An short simple example is provided how to use it:
 * The code for the simulation (one device, one gateway) `test_simul.py`, 
 * A script that sets the proper `PYTHONPATH` (to add `../src`) and run `test_simul_py` is `run_test_simul.sh`

 How to run it: `./run_test_simul.sh`


## Automated Simulation Tool

### Introduction

The program `simtool` provides a way to run, and compare the output of simulations, 
 
#### Workflow for trying out parameters
 
The workflow or trying out simulation parameters is as follows:

  1) First select a builtin simulation name from `./simtool list` 
  2) Display the parameters of that simulation with `./simtool show <sim-name>` (e.g. `./simtool ackerror`)
  3) Run the builtin simulation as `./simtool run <sim-name>` (e.g. `simtool run ackerror`)
  4) **Try out** the same simulation but changing one (or several parameters) by using one or several
   options  `--<parameter-name> <parameter-value>`, e.g.
    `./simtool run ackerror --fcn-size 5` 
  5) From the directory names displayed when you did './simtool run ...', do a comparison between
    the output of the two runs with `./simtool diff <dir1> <dir2>` or `./simtool kdiff <dir1> <dir2>`,
    e.g. `./simtool diff test-ackerror test-ackerror-fs5` or `./simtool kdiff test-ackerror test-ackerror-fs5`
 
#### Workflow for looking for differences

The workflow for refactoring or looking at the changes for one set of simulation is follows:
  1) With a stable version of openschc, run and record all scenarios with `./simtool run-all --prefix ref`
    (or use the equivalent shortcut `./simtool reref`)
  2) ... do modifications of openschc (like refactoring) ...
  3) Check if the output is identical with `./simtool recheck-all` (which assumes 
  default prefix `ref` for reference output), or alternately display the differences with any
  recorded file with: `./simtool rediff` or `./simtool rekdiff`

### Scenario specification

Scenario specification format:

  * `packet-size`: size of the packet to send in bytes, `0` means a default predefined COAP packet is used
  

  * `compr-ruleid`
  * `compr-ruleid-size` 


  * `frag-mode`: `"ack-on-error"` or `"no-ack"`
  * `frag-ruleid`
  * `frag-ruleid-size`
  * `dtag-size`
  * `w-size`
  * `fcn-size`
  * `tile-size`

  
  * `loss-interval`
  * `loss-packet`
  * `loss-rate`
  * `seed`
  
### Reference

The program `simtool` provides a way to run, and compare the output of simulations

* `./simtool list`:

  List the available predefined scenario names
  
* `./simtool run <scenario name> [<options>] [--prefix <prefix>]`

  Run a the scenario `<scenario name>` and output the result (logs) in the directory name corresponding 
 to the scenario (prefixed by `"<prefix>-"` if specified on the command line)
 
 * `./simtool run-all [--prefix <prefix>]`
   
   Run all the available scenario (prefixed by `"<prefix>-"` if specified on the command line options)
  
  * `./simtool compare-all [--prefix <prefix>]`
 
   Compare the output of each existing scenario in its default output directory to the one prefixed
   by `<prefix>-` (or by default by `ref-`)
  
  * `./simtool recheck-all [--prefix <prefix>]`

   Re-run each existing scenario, and theyn compare the output of each scenario in its default output 
   directory to the one prefixed by `<prefix>-` (or by default by `ref-`)
 
 * Alternate commands for `recheck-all` are `rediff` or resp. `rekdiff`, which perform the same actions, 
   except that the programs `diff -u` or resp. `kdiff3` are used to display the differences.
 
 
 ## Configuration