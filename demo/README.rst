I'm a new user, where do I start?
=================================

If you are interested in just using cbcbeat for forward
electrophysiology simulations, start by looking at

  monodomain/demo_monodomain.py

If you are interested in using cbcbeat for computing functional
sensitivities, continue by looking at

  monodomain/demo_monodomain_adjoint.py

If you would like to tune the performance of the solvers, in
particular to customize the linear algebra solvers, look at

  solver-efficiency/*

Conventions for adding new demos
================================

* Please prefix all new demos filenames with demo_
