import numpy as np

a = np.arange(10).astype(int)

r1 = np.array([0,0,0,1,1,1,2,2,2])
r2 = np.array([0,0,0,1,1,1,2,2,2])
r3 = np.array([0,0,0,1,1,1,2,2,2])
r4 = np.array([3,3,3,4,4,4,5,5,5])
r5 = np.array([3,3,3,4,4,4,5,5,5])
r6 = np.array([3,3,3,4,4,4,5,5,5])
r7 = np.array([6,6,6,7,7,7,8,8,8])
r8 = np.array([6,6,6,7,7,7,8,8,8])
r9 = np.array([6,6,6,7,7,7,8,8,8])
blockmap =  np.stack([r1,r2,r3,r4,r5,r6,r7,r8,r9])

rowp = [0,0,0,3,3,3,6,6,6]
colp = [0,3,6,0,3,6,0,3,6]
idmap = np.arange(9).reshape((3,3))

def getblock(board,block_idx):
  '''
  Gets a block of a sudoku grid
  
    `+-+-+-+`
    `|0|1|2|`
    `+-+-+-+`
    `|3|4|5|`
    `+-+-+-+`
    `|6|7|8|`
    `+-+-+-+`
  
  '''  
  ridx = rowp[block_idx]
  cidx = colp[block_idx]
  return board[ridx:ridx+3,cidx:cidx+3]

def getrow(b,idx):
  '''
  returns row `idx` of the board
  '''
  return b[idx,:]
  
def getcol(b,idx):
  '''
  returns col `idx` of the board
  '''
  return b[:,idx].T

def get_empty_squares(block):
  '''
  returns the positions of the empty squares of the block
  '''
  return np.stack(np.where(block==0),axis=1)

def get_filled_squares(block):
  '''
  returns the positions of the filled squares of the block
  '''
  return np.stack(np.where(block!=0),axis=1)

def get_possible_at_position(board,block,r,c):
  '''
  returns the possible values at board[r,c] checking across row, col, block
  '''
  rowcol = np.concatenate([a,block.reshape(9),getrow(board,r),getcol(board,c)])
  rcbins = np.bincount(rowcol)-2
  valid_values_for_square = a[1:][rcbins[1:]<0]
  return valid_values_for_square.astype(int)

def cart2idx(cart):
  '''
  converts a cartesian block coordinate to an integer
  '''
  return int(cart[0] * 9 + cart[1])

def idx2cart(idx):
  '''
  converts an integer block coordinate to cartesian
  '''
  return np.array([idx//9, idx%9]).astype(int)

def convert_to_unique(row_posns,col_posns, block_posns):
  '''
  Given a list of cartesian coordinates, returns the unique elements
  '''
  rp = [cart2idx(row_posns[j]) for j in range(len(row_posns))]
  cp = [cart2idx(col_posns[j]) for j in range(len(col_posns))]
  bp = [cart2idx(block_posns[j]) for j in range(len(block_posns))]
  up = np.nonzero(np.bincount(np.concatenate([rp,cp,bp]).astype(int)))[0]
  return np.array([idx2cart(up[i]) for i in range(up.shape[0])])

def get_tainted_squares(board,r,c):
  '''
  Returns all tainted square positions assuming that specific board[r,c] is modified
  '''
  # gets modified squares
  i = blockmap[r,c]
  row_add = rowp[i]
  col_add = colp[i]
  block_posns = get_empty_squares(getblock(board,i))  
  block_posns[:,0]+=row_add
  block_posns[:,1]+=col_add
  # block = getblock(b,i)
  row = getrow(board,r)
  col = getcol(board,c)
  row_posns = get_empty_squares(row).squeeze(-1)
  col_posns = get_empty_squares(col).squeeze(-1)
  r = np.repeat(r,row_posns.shape[0])
  c = np.repeat(c,col_posns.shape[0])
  row_posns = np.stack([r,row_posns],axis=1)
  col_posns = np.stack([col_posns,c],axis=1)
  rowcol_posns = convert_to_unique(row_posns,col_posns,block_posns)
  return rowcol_posns

def get_rowcol_possible(b,rowcol_posns):
  # gets possible values given a list of squares
  rowcol_possible = [get_possible_at_position(b,getblock(b,blockmap[rowcol_posns[j,0],rowcol_posns[j,1]]) ,rowcol_posns[j,0],rowcol_posns[j,1]) for j in range(rowcol_posns.shape[0])]
  return rowcol_possible

def pad_out(block_run,maxlen):
  '''
  Matrix things for padding
  '''
  #pc = np.array(posn_counter)
  for j in range(81):
    i = idx2cart(j)
    block_run[i[0]][i[1]] = np.concatenate([block_run[i[0]][i[1]].astype(int),np.zeros((maxlen - block_run[i[0]][i[1]].shape[0])).astype(int)-1])
    int_mask = np.ones((maxlen))
    int_mask[np.nonzero(block_run[i[0]][i[1]] + 1)] = False  
  return np.array(block_run)

def set_map(board,blocks_to_update):
  """Given a list of blocks to update, returns parameters about the board
  """
  constraints = [[] for _ in range(9)]
  posn_counter = [[] for _ in range(9)]
  for j in range(len(constraints)):
    for i in range(9):
      constraints[j].append(np.empty(1))
      posn_counter[j].append(0)
  for i in blocks_to_update:
    row_add = rowp[i]
    col_add = colp[i]
    block = getblock(board,i)
    es = get_empty_squares(block)
    es[:,0] += row_add
    es[:,1] += col_add
    for j in es:
      r,c = j[0], j[1]
      constraints[r][c] = get_possible_at_position(board,block,r,c)
      posn_counter[r][c] = len(constraints[r][c])
  posn_counter = np.array(posn_counter)
  maxlen = np.max(posn_counter)
  return constraints,posn_counter,maxlen

def create_mask(posns, pos_lens, maxlen):
  block_run = np.array([np.zeros((maxlen)).astype(bool) for _ in range(len(posns))])
  for j,i in enumerate(posns):
    block_run[j][0:pos_lens[i[0],i[1]]] = True
  return np.array(block_run)

def update_mask(current_masks, constraints, intermediate_constraints, intermediate_posns):
  for j,i in enumerate(intermediate_posns):
    r,c = i[0],i[1]
    current_masks[j] = current_masks[j] * np.isin(constraints[r,c], np.intersect1d(constraints[r,c],intermediate_constraints[j]))
  return current_masks

def get_trivial(masks, empty_squares):
  return empty_squares[np.sum(masks1,axis=1)==1,:]
def assign_trivial(b,masks,possibilities,posn_counters):  
  es = get_empty_squares(b)
  index_trivial = posn_counters[es[:,0],es[:,1]] == 1
  trivial = posn_counters == 1
  while index_trivial.shape[0]:
    # print(np.nonzero(trivial))
    b[trivial] = possibilities[trivial,0]
    masks[np.nonzero(index_trivial),0] = False