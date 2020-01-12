
## Simulator

A simulator and a set of classes are available for OpenSCHC.
They are in the files `src/net_sim_*`, and `src/net_sim_builder.py` provides a nicer upper-level API  to use them.

An short simple example is provided how to use it:
 * The code for the simulation (one device, one gateway) `test_simul.py`, 
 * A script that sets the proper `PYTHONPATH` (to add `../src`) and run `test_simul_py` is `run_test_simul.sh`

 How to run it: `./run_test_simul.sh`


## Automated Simulation Tool

### Introduction

The program `simtool` provides a way to run, and compare the output of simulations, and the intended workflow is as
follows:
  1) With a stable version of openschc, run and record all scenarios with `./simtool run-all --prefix ref`
  2) ... do modifications of openschc (like refactoring) ...
  3) Check if the output is identical (or what are the differences) with `./simtool recheck-all` (which assumes 
  default prefix `ref` for reference output)


### Reference

The program `simtool` provides a way to run, and compare the output of simulations

* `./simtool list`:

  List the available scenario names
  
* `./simtool run <scenario name> [--prefix <prefix>]`

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
 