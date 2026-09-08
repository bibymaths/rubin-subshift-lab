"""Simulate elementary CA Rule 110 on a periodic binary word."""

from rubin_subshifts.cellular_automata import CellularAutomaton, simulate
from rubin_subshifts.symbolic import Alphabet, PeriodicConfiguration, Word

alphabet = Alphabet((0, 1))
initial = PeriodicConfiguration(Word(alphabet, (0, 0, 0, 1, 0, 0, 0, 0)))
for state in simulate(CellularAutomaton.elementary(110), initial, 16):
    print("".join(map(str, state.word.symbols)))
