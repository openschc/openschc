.. OpenSCHC documentation master file, created by
   sphinx-quickstart on Sat Mar 23 20:39:26 2019.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive

Welcome to OpenSCHC's documentation!
************************************

What is OpenSCHC ?
==================

OpenSCHC
--------

OpenSCHC is a OpenSource Implementation of `SCHC (Static Context Header Compression) <https://datatracker.ietf.org/doc/draft-ietf-lpwan-ipv6-static-context-hc/>`_ currently being standardized by the `LPWAN Working Group <https://tools.ietf.org/wg/lpwan/>`_ at the IETF. Oversimplifying, this is essentially IP protocl headers compression and fragmentation so that they can be transported by low datarate, long range IoT networks.

The long term goal is to have a stable, open-source, reference Python3 codebase for the SCHC protocol.

OpenSCHC is developed to be compatible with micropython, on the device side.

OpenSCHC is licensed under the `MIT License <https://github.com/openschc/openschc/blob/master/LICENSE>`_ .

Understanding the architecture
------------------------------

A global architecture of openSCHC implementation is shown below:

.. image:: _static/openSCHC_arch.png
   :alt: OpenSCHC Architecture

The **Rule Manager** stores a set of Rules and provides methods to install or retreive Rules.

Rules are composed of two elements:

* A **RuleID** which identifies the Rule by its number, and
* A **content** which contains an array of fields. For details, refer to the `SCHC protocol <https://datatracker.ietf.org/doc/draft-ietf-lpwan-ipv6-static-context-hc/?include_text=1>`_

The **App 1 ... App n** are the applications that invoke the **SCHC Orchestrator** to run the necessary SCHC operations, which are briefly defined below:

**Compression** is used on the sender side to compress the header of a packet provided by the App, using a specific rule (identified by its RuleID).
**Decompression**: on the receiver side, upon receiving a compressed packet, the Decompresser is invoked to rebuild the original packet, using the Rule identified by the RuleID carried in the compressed packet.

**Fragmentation** is invoked on the sender side with a RuleID to generate a set of fragments out of a packet (compressed or uncompressed).
**Reassembly** is used on the receiver side to reconstruct the packet out of the set of fragments.

Fragmentation modes and the associated parameters are described in the `SCHC protocol <https://datatracker.ietf.org/doc/draft-ietf-lpwan-ipv6-static-context-hc/?include_text=1>`_ .

**Network Connector** interfaces to a physical model to a real LPWAN network such as LoRa or Sigfox,
or to a link simulator.

Using OpenSCHC
==============

Want to give it a try? See :doc:`General/Installation_guide` in order to set up OpenSCHC on your computer and :doc:`General/User_guide` to start running it.

Contributing
============

Want to help ? See our :doc:`General/Contributing_Guidelines` for more details on the future work on the OpenSCHC project.

Our current activity
====================

Direct link to the Etherpad for on-line information exchange at the IETF Hackathons : `https://etherpad.tools.ietf.org/p/openschc <https://etherpad.tools.ietf.org/p/openschc>`_

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`

Table of contents
-----------------

.. include:: toc.rst

