"""
Unit tests for various types of solvers for cardiac cell models.
"""

__author__ = "Marie E. Rognes (meg@simula.no), 2013 and Simon W. Funke (simon@simula.no), 2014"
__all__ = ["TestCardiacODESolverAdjoint"]

import pytest
from testutils import assert_true, assert_greater, slow, \
        adjoint, cell_model, parametrize

from beatadjoint.dolfinimport import UnitIntervalMesh, info_green
from beatadjoint import CardiacODESolver, \
        replay_dolfin, InitialConditionParameter, \
        Constant, Expression, Function, Functional, \
        project, inner, assemble, dx, dt, FINISH_TIME, \
        parameters, compute_gradient_tlm, compute_gradient, \
        taylor_test
from beatadjoint.cellmodels import *

supported_schemes = ["ForwardEuler",
                     "BackwardEuler",
                     "CrankNicolson",
                     "RK4",
                     "ESDIRK3",
                     "ESDIRK4",
                     ]

fails_with_RK4 = (Tentusscher_2004_mcell,
                  Tentusscher_2004_mcell_disc,
                  Tentusscher_2004_mcell_cont,
                  Tentusscher_panfilov_2006_M_cell,
                  )

seed_collection_adm = {Tentusscher_2004_mcell:1e-5,
                   Tentusscher_2004_mcell_disc:1e-5,
                   Tentusscher_2004_mcell_cont:1e-5,
                   Tentusscher_panfilov_2006_M_cell:1e-5,
                   Grandi_pasqualini_bers_2010:1e-7,
                   }

seed_collection_tlm = seed_collection_adm.copy()
seed_collection_tlm[Grandi_pasqualini_bers_2010] = 1e-6

fails_with_forward_euler = (Grandi_pasqualini_bers_2010,
                            )

class TestCardiacODESolverAdjoint(object):

    def setup_dolfin_parameters(self):
        ''' Set optimisation parameters for these tests '''

        parameters["form_compiler"]["cpp_optimize"] = True
        flags = "-O3 -ffast-math -march=native"
        parameters["form_compiler"]["cpp_optimize_flags"] = flags

    def _setup_solver(self, model, Scheme, mesh):

        # Initialize time and stimulus (note t=time construction!)
        time = Constant(0.0)
        stim = {0: Expression("(time >= stim_start) && (time < stim_start + stim_duration)"
                              " ? stim_amplitude : 0.0 ", time=time, stim_amplitude=52.0,
                              stim_start=0.0, stim_duration=1.0, name="stim")}

        # Initialize solver
        params = CardiacODESolver.default_parameters()
        params["scheme"] = Scheme
        solver = CardiacODESolver(mesh, time, model.num_states(),
                                  model.F, model.I, I_s=stim, params=params)

        return solver

    def _run(self, solver, ics):
        # Assign initial conditions

        solver._pi_solver.scheme().t().assign(0)
        (vs_, vs) = solver.solution_fields()
        vs_.assign(ics)

        # Solve for a couple of steps
        dt = 0.01
        T = 4*dt
        dt = [(0.0, dt), (dt*3,dt/2)]
        solver._pi_solver.parameters.reset_stage_solutions = True
        solver._pi_solver.parameters.newton_solver.reset_each_step = True
        solver._pi_solver.parameters.newton_solver.relative_tolerance = 1.0e-10
        solver._pi_solver.parameters.newton_solver.recompute_jacobian_for_linear_problems = True
        solutions = solver.solve((0.0, T), dt)
        for ((t0, t1), vs) in solutions:
            pass

    def tlm_adj_setup(self, cell_model, Scheme):
        mesh = UnitIntervalMesh(3)
        Model = cell_model.__class__

        # Initiate solver, with model and Scheme
        params = Model.default_parameters()
        model = Model(params=params)

        solver = self._setup_solver(model, Scheme, mesh)
        ics = Function(project(model.initial_conditions(), solver.VS), name="ics")

        info_green("Running forward %s with %s (setup)" % (model, Scheme))
        self._run(solver, ics)

        # Define functional
        (vs_, vs) = solver.solution_fields()
        form = lambda w: inner(w, w)*dx
        J = Functional(form(vs)*dt[FINISH_TIME])

        # Compute value of functional with current ics
        Jics = assemble(form(vs))

        # Set-up runner
        def Jhat(ics):
            self._run(solver, ics)
            (vs_, vs) = solver.solution_fields()
            return assemble(form(vs))

        # Stop annotating
        parameters["adjoint"]["stop_annotating"] = True

        m = InitialConditionParameter(vs)
        return J, Jhat, m, Jics

    @adjoint
    @slow
    @parametrize(("Scheme"), supported_schemes)
    def test_replay(self, cell_model, Scheme):
        mesh = UnitIntervalMesh(3)
        Model = cell_model.__class__

        if isinstance(cell_model, fails_with_RK4) and Scheme == "RK4":
            pytest.xfail("RK4 is unstable for some models with this timestep (0.01)")

        # Initiate solver, with model and Scheme
        params = Model.default_parameters()
        model = Model(params=params)

        solver = self._setup_solver(model, Scheme, mesh)
        ics = project(model.initial_conditions(), solver.VS)

        info_green("Running forward %s with %s (replay)" % (model, Scheme))
        self._run(solver, ics)

        print solver.solution_fields()[0].vector().array()

        info_green("Replaying")
        success = replay_dolfin(tol=0, stop=True)
        assert_true(success)

    @adjoint
    @slow
    @parametrize(("Scheme"), supported_schemes)
    def test_tlm(self, cell_model, Scheme):
        "Test that we can compute the gradient for some given functional"

        if Scheme == "ForwardEuler":
            pytest.xfail("RK4 is unstable for some models with this timestep (0.01)")
            
        if isinstance(cell_model, fails_with_RK4) and Scheme == "RK4":
            pytest.xfail("RK4 is unstable for some models with this timestep (0.01)")

        J, Jhat, m, Jics = self.tlm_adj_setup(cell_model, Scheme)

        # Seed for taylor test
        seed = seed_collection_tlm.get(cell_model.__class__)

        # Check TLM correctness
        info_green("Computing gradient")
        dJdics = compute_gradient_tlm(J, m, forget=False)
        assert (dJdics is not None), "Gradient is None (#fail)."
        conv_rate_tlm = taylor_test(Jhat, m, Jics, dJdics, seed=seed)

        assert_greater(conv_rate_tlm, 1.9)

    @adjoint
    @slow
    @parametrize(("Scheme"), supported_schemes)
    def test_adjoint(self, cell_model, Scheme):
        """ Test that the gradient computed with the adjoint model is correct. """

        if isinstance(cell_model, fails_with_RK4) and Scheme == "RK4":
            pytest.xfail("RK4 is unstable for some models with this timestep (0.01)")

        if isinstance(cell_model, fails_with_forward_euler) and Scheme == "ForwardEuler":
            pytest.xfail("ForwardEuler is unstable for some models with this timestep (0.01)")

        J, Jhat, m, Jics = self.tlm_adj_setup(cell_model, Scheme)

        # Seed for taylor test
        seed = seed_collection_adm.get(cell_model.__class__)

        # Compute gradient with respect to vs.
        info_green("Computing gradient")
        dJdics = compute_gradient(J, m, forget=False)
        assert (dJdics is not None), "Gradient is None (#fail)."
        conv_rate = taylor_test(Jhat, m, Jics, dJdics, seed=seed)

        # Check that minimal rate is greater than some given number
        assert_greater(conv_rate, 1.9)
