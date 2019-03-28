File Classification
*******************
=
Each of the different components is

* RULE_MANAGERS

  * rulemanager.py      ``# store and retrieve contexts``

* COMMON TO C/D & F/R

  * bitarray.py         ``# bit aligned buffer management``

* COMPRESSION/DECOMPRESSION prefix

  * schccomp.py         ``# basic compression/decompression fct``

* FRAGMENTATION/REASSEMBLY prefix

  * mic_crc32.py        ``# MIC computation/check``
  * schcmsg.py          ``# manage frag header``
  * schcrecv.py         ``# reassemble fragments``
  * schcsend.py         ``# send fragments``
  * schctile.py         ``# manage tiles``

* SYSTEM

  * base_import.py      ``# import module for python or upython``

* LPWAN Interface prefix
* SIMULATION            ``# Code for simulation only``

  * simlayer2.py        ``# emulate a L2``
  * simsched.py         ``# schedule transmission in simulated network ?``
  * simul.py            ``# eumulate L2 ?``
  * cond_true.py        ``# used to emulate transmission errors``

* APPLICATION

  * packet_picker.py    ``# read a pcap file to get packet``
  * schcgw.py           ``# interface with LPWAN``

* ORCHESTRATION

  * schc.py             ``# start rule manager, cC/D and F/R``

* TEST

  * test_bitarray.py
  * test_bitarray2.py
  * test_bitmap.py
  * test_compress.py
  * test_frag.py
  * test_newschc.py
  * test_oschc.py
  * test_ruleman.py
  * test_simsched.py

* UNKNOWN STATUS

  * comp_bitmap.py       ``# this is test implementation for bitmap compression``
