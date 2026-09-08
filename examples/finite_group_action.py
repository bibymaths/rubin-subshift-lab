"""Generate the finite cyclic shift image on period-four points."""

from rubin_subshifts.cellular_automata import CellularAutomaton
from rubin_subshifts.groups import generate_group, induced_permutation
from rubin_subshifts.symbolic import Alphabet
from rubin_subshifts.symbolic.configurations import enumerate_periodic_configurations

alphabet = Alphabet((0, 1))
domain = tuple(enumerate_periodic_configurations(alphabet, 4))
generator = induced_permutation(CellularAutomaton.left_shift(alphabet), domain)
group = generate_group((generator,))
print({"finite_image_order": group.order, "generator": generator.to_cycle_notation()})
