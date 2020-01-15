
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

  1) First select a builtin simulation name from:
     * `./simtool list` 
  2) Display the parameters of that simulation with `./simtool show <sim-name>` (see below "Scenario Specification" 
  for the parameters and their names)
     * example:`./simtool show ackerror`
  3) Run the builtin simulation as `./simtool run <sim-name>` 
     * example: `simtool run ackerror`
  4) **Try out** the same simulation but changing one (or several parameters) by using one or several
   options  `--<parameter-name> <parameter-value>`
     * example: `./simtool run ackerror --frag-ruleid 2`
     * or: `./simtool run ackerror --loss-packet 15` 
  5) From the directory names displayed when you did `./simtool run ...`, do a comparison between
    the output of the two runs with `./simtool diff <dir1> <dir2>` or `./simtool kdiff <dir1> <dir2>`,
     * example: `./simtool diff test-ackerror test-ackerror-rid2` 
     * ... or `./simtool kdiff test-ackerror test-ackerror-rid2`
     * ... or `./simtool kdiff test-ackerror test-ackerror-lp15`     
 
#### Workflow for looking for differences

The workflow for refactoring or looking at the changes for the whole set of builtin simulations
 is follows:
  1) With a stable version of openschc, run and record all scenarios with `./simtool run-all --prefix ref`
    (or use the equivalent shortcut `./simtool reref`)
  2) ... do modifications of openschc (like refactoring) ...
  3) Check if the output is identical with `./simtool recheck-all` (which assumes 
  default prefix `ref` for reference output), or alternately display the differences with any
  recorded file with: `./simtool rediff` or `./simtool rekdiff`

### Workflow for an individual simulation

If you want to set the parameters by yourself (described in next section "Scenario specification"), 
you can use the command line with many options or:
  1) You can create a json scenario specification file `<scenario-name>.json`, with content 
    as follows (and example is in the file [sample-scen.json](sample-scen.json) ):
     * `{ "option1": value1, "option2": value2, ... }` 
  2) You can run the example with:
     * `./simtool run <scenario-name>.json [<options>...]` 
     * example: `./simtool run sample-scen.json`
  3) The output should be in recorded files in `test-<scenario-name>`

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

  
  * `loss-interval <i>` : every `<i>` packet is lost (starting from `<i>-1`) 
  * `loss-packet <i>`: packet with index `<i>` is lost
  * `loss-rate <p>`: lost rate in percentage, e.g. `<p>` % 
  * `seed`: random seed (for `loss-rate` case)
  
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
 
 * TODO: commands `diff`, `kdiff`, `show`, explain options for changing parameters

