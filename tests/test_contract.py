import unittest
from sismic import io
from sismic.interpreter import Interpreter
from sismic.model import Event, Transition, StateChart, StateMixin
from sismic.exceptions import PreconditionError, PostconditionError, InvariantError


class ElevatorContractTests(unittest.TestCase):
    def setUp(self):
        self.sc = io.import_from_yaml(open('docs/examples/elevator.yaml'))
        self.interpreter = Interpreter(self.sc)

    def test_no_error(self):
        self.interpreter.queue(Event('floorSelected', floor=4))
        self.interpreter.execute()
        self.assertFalse(self.interpreter.final)

    def test_state_precondition(self):
        self.sc.state_for('movingUp').preconditions.append('False')
        self.interpreter.queue(Event('floorSelected', floor=4))
        with self.assertRaises(PreconditionError) as cm:
            self.interpreter.execute()
        self.assertTrue(isinstance(cm.exception.obj, StateMixin))

    def test_state_postcondition(self):
        self.sc.state_for('movingUp').postconditions.append('False')
        self.interpreter.queue(Event('floorSelected', floor=4))
        with self.assertRaises(PostconditionError) as cm:
            self.interpreter.execute()
        self.assertTrue(isinstance(cm.exception.obj, StateMixin))

    def test_state_invariant(self):
        self.sc.state_for('movingUp').invariants.append('False')
        self.interpreter.queue(Event('floorSelected', floor=4))
        with self.assertRaises(InvariantError) as cm:
            self.interpreter.execute()
        self.assertTrue(isinstance(cm.exception.obj, StateMixin))

    def test_transition_precondition(self):
        self.sc.state_for('floorSelecting').transitions[0].preconditions.append('False')
        self.interpreter.queue(Event('floorSelected', floor=4))
        with self.assertRaises(PreconditionError) as cm:
            self.interpreter.execute()
        self.assertTrue(isinstance(cm.exception.obj, Transition))

    def test_transition_postcondition(self):
        self.sc.state_for('floorSelecting').transitions[0].postconditions.append('False')
        self.interpreter.queue(Event('floorSelected', floor=4))
        with self.assertRaises(PostconditionError) as cm:
            self.interpreter.execute()
        self.assertTrue(isinstance(cm.exception.obj, Transition))

    def test_statechart_precondition(self):
        self.sc.preconditions.append('False')
        with self.assertRaises(PreconditionError) as cm:
            self.interpreter = Interpreter(self.sc)
        self.assertTrue(isinstance(cm.exception.obj, StateChart))

    def test_statechart_postcondition(self):
        sc = io.import_from_yaml(open('tests/yaml/simple.yaml'))
        sc.postconditions.append('False')
        interpreter = Interpreter(sc)
        interpreter.queue(Event('goto s2')).queue(Event('goto final'))
        with self.assertRaises(PostconditionError) as cm:
            interpreter.execute()
        self.assertTrue(isinstance(cm.exception.obj, StateChart))

    def test_statechart_invariant(self):
        self.sc.invariants.append('False')
        self.interpreter.queue(Event('floorSelected', floor=4))
        with self.assertRaises(InvariantError) as cm:
            self.interpreter.execute()
        self.assertTrue(isinstance(cm.exception.obj, StateChart))

    def test_do_not_raise(self):
        self.sc.invariants.append('False')
        interpreter = Interpreter(self.sc, ignore_contract=True)
        interpreter.queue(Event('floorSelected', floor=4))
        interpreter.execute()