.. cbcbeat documentation master file, created by
   sphinx-quickstart on Fri Sep 12 10:27:56 2014.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

=================================================================================
cbcbeat: an adjoint-enabled framework for computational cardiac electrophysiology
=================================================================================

cbcbeat is a Python-based lightweight solver collection for solving
computational cardiac electrophysiology problems. cbcbeat provides
solvers for single cardiac cell models, the monodomain and bidomain
equations and coupled systems of such. All cbcbeat solvers are
adjoint-enabled thus allowing for efficient solution of both forward
and inverse cardiac electrophysiology problems.

cbcbeat is based on the finite element functionality provided by the
FEniCS Project software, the automated derivation and computation of
adjoints offered by the dolfin-adjoint software and cardiac cell
models from the CellML repository.

cbcbeat originates from the `Center for Biomedical Computing
<http://cbc.simula.no>`__, a Norwegian Centre of Excellence, hosted by
`Simula Research Laboratory <http://www.simula.no>`__, Oslo, Norway.

Installation and dependencies:
==============================

The cbcbeat source code is hosted on Bitbucket:

  https://bitbucket.org/meg/cbcbeat

The cbcbeat solvers are based on the `FEniCS Project
<http://www.fenicsproject.org>`__ finite element library and its
extension `dolfin-adjoint <http://www.dolfin-adjoint.org>`__.

See the separate file INSTALL in the root directory of the cbcbeat
source for a complete list of dependencies and installation
instructions.

Main authors:
=============

See the separate file AUTHORS in the root directory of the cbcbeat
source for the list of authors and contributors.

License:
========

cbcbeat is free software: you can redistribute it and/or modify
it under the terms of the GNU Lesser General Public License as
published by the Free Software Foundation, either version 3 of the
License, or (at your option) any later version.

cbcbeat is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
FITNESS FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public
License for more details.

You should have received a copy of the GNU Lesser General Public
License along with cbcbeat. If not, see
<http://www.gnu.org/licenses/>.

Testing and verification:
=========================

The cbcbeat test suite is based on `pytest <http://pytest.org>`__ and
available in the test/ directory of the cbcbeat source. See the
INSTALL file in the root directory of the cbcbeat source for how to
run the tests.

cbcbeat uses Bitbucket Pipelines for automated and continuous testing,
see the current test status of cbcbeat here:
 
  https://bitbucket.org/meg/cbcbeat/addon/pipelines/home

Contributions:
==============

Contributions to cbcbeat are very welcome. If you are interested in
improving or extending the software please `contact us
<https://bitbucket.org/meg/cbcbeat>`__ via the issues or pull requests
on Bitbucket. Similarly, please `report
<https://bitbucket.org/meg/cbcbeat/issues>`__ issues via Bitbucket.

Documentation:
==============

Examples and demos:
-------------------

A collection of examples on how to use cbcbeat is available in the
demo/ directory of the cbcbeat source. We also recommend looking at
the test suite for examples of how to use the cbcbeat solvers.

API documentation:
------------------

.. toctree::
   :maxdepth: 2
   :numbered:              
              
   cbcbeat

Indices and tables
==================

* :ref:`genindex`
* :ref:`modindex`
* :ref:`search`
