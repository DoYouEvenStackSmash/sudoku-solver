from helpers import *
from collections import deque
blocks_to_check = deque([0,1,2,3,4,5,6,7,8])
r1 = np.array([3,0,5,4,0,2,0,6,0])
r2 = np.array([4,9,0,7,6,0,1,0,8])
r3 = np.array([6,0,0,1,0,3,2,4,5])
r4 = np.array([0,0,3,9,0,0,5,8,0])
r5 = np.array([9,6,0,0,5,8,7,0,3])
r6 = np.array([0,8,1,3,0,0,0,9,2])
r7 = np.array([0,5,0,6,0,1,4,0,0])
r8 = np.array([2,0,0,5,4,9,0,7,0])
r9 = np.array([1,4,9,0,0,7,3,0,6])
b = np.stack([r1,r2,r3,r4,r5,r6,r7,r8,r9])

# get board parameters
constraints,constraint_lens,maxlen = set_map(b,blocks_to_check)
empty_square_posns = get_empty_squares(b)

# demonstrate values at test square
test_square = empty_square_posns[0]
r,c = test_square.tolist()
print(get_possible_at_position(b,getblock(b,blockmap[r,c]),r,c))

# get modified squares assuming some modification
modified_squares = get_tainted_squares(b,r,c)
print(modified_squares)