File Taxonomy
*************

The different components are

* Generic functionality

  * gen_base_import.py  ``# imports module for python or upython``
  * gen_bitarray.py     ``# bit aligned buffer management``
  * gen_rulemanager.py  ``# stores and retrieves contexts``
  * gen_utils.py        ``# ?``

* COMPRESSION/DECOMPRESSION prefix

  * compr_core.py       ``# core compression/decompression functions``
  * compr_bitmap.py     ``# ?``
  * compr_parser.py     ``# ?``

* FRAGMENTATION/REASSEMBLY prefix

  * frag_all.py         ``# imports all frag code``
  * frag_bitmap.py      ``# ?``
  * frag_msg.py         ``# manages frag header``
  * frag_rcs_crc32.py   ``# RCS computation/check``
  * frag_recv.py        ``# reassembles fragments``
  * frag_send.py        ``# sends fragments``
  * frag_tile.py        ``# manages tiles``

* NETWORK interface/sim

  * net_sim_core.py     ``# ?``
  * net_sim_layer2.py   ``# simulates an L2``
  * net_sim_loss.py     ``# simulates packet loss on L2``
  * net_sim_record.py   ``# ?``
  * net_sim_sched.py    ``# schedules transmission in simulated network ?``

* APPLICATION

  * packet_picker.py    ``# read a pcap file to get packet``

* ORCHESTRATION

  * protocol.py         ``# start rule manager, C/D and F/R``

* RUNNERS

  * test_compress.py    ``# run a SCHC compression example``
  * test_frag_new.py    ``# run a SCHC fragmentation example``

* TEST (under the **tests** directory)

  * test_bitarray.py    ``# tests the BitBuffer functionalities``
  * test_bitarray2.py   ``# more tests of the BitBuffer functionalities``
  * test_bitmap.py      ``# tests the generation of a BitMap out of the list of tiles received``
  * test_newschc.py
  * test_ruleman.py
  * test_simsched.py

* UNKNOWN STATUS
