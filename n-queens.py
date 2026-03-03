""" a scheme for displaying and fooling with n-queens
"""
import graphics as gr
import numpy
import random
import time

SOLVER = "Manual"
#SOLVER = 'Backtracking'
#SOLVER = "HillClimbing"
#SOLVER = 'BeamSearch'
#SOLVER = 'GeneticProgramming'



n = 4   # how big a problem?  how many queens?
unit = 200  #PIXELS per chessboard square side
hunit = int(unit/2)
qunit = int(unit/4)
xmargin = 20
ymargin = 25
base = 25
downs = []
ups = []
col = []
Red = gr.color_rgb(255,0,0)
Black = gr.color_rgb(0,0,0)
White = gr.color_rgb(255,255,255)

queens = None
Win = None
mq = 0

def main():

    # n-Queens solver

    global queens, Win, mq
    Win = gr.GraphWin(f'{n} by {n} board', unit*n+2*xmargin, unit*n+2*ymargin)

    for i in range(n):  #ups
        ups.append(  gr.Text( gr.Point(0,i*unit),'^'))
        ups[i].draw(Win)

        col.append([])
        for j in range(n):
            x,y = get_bottom_left(i,j)
            col[i].append(  gr.Rectangle(gr.Point(x, y), gr.Point(x+unit,y+unit)))
            if (i+j)&1 == 0:
                col[i][j].setFill("red") #(Red)
            else:
                col[i][j].setFill("black")#(Black)
            col[i][j].draw(Win)


    queens = []
    for i in range(n):
        queens.append(queen())
        moveQueen(i,n-1)
        queens[i].draw(Win)


    while SOLVER == 'Manual':
        mark_conflicts()
        p = Win.getMouse()
        x,y = p.getX(), p.getY()
        c = int((x-xmargin) // unit)
        r = int((y-ymargin) // unit)
        print (f'got mouse click {x},{y}, means col{c} row {r}')
        moveQueen(c,r)

    while SOLVER == 'Backtracking':
        start = [0]*n

        for q,r in enumerate(start):
            moveQueen(q,r)

        mq = QueenMoves
        if not backtrack(start, 0):
            print('Failure.  total moves', QueenMoves -mq)
            mess = gr.Text(gr.Point(0,0),
                           f'FAILURE after {QueenMoves - mq} moves')
            mess.draw(Win)
        else:
            print(f'Success! QueenRows: {start}, moves to solution {QueenMoves - mq}')
            mess = gr.Text(gr.Point(0,0), f'SUCCESS used {QueenMoves-mq} moves')
            mess.draw(Win)
        time.sleep(20)
        Win.close()
        exit()

    while SOLVER == 'HillClimbing':
        start,bestConf = rand_init(0,n)

        for c,r in enumerate(start):
            moveQueen(c, r)
        time.sleep(10)

        mq = QueenMoves
        while True:
            if bestConf == 0:
                print(f'Success! hillclimbing steps: {QueenMoves-mq}')
                print(f'final pattern {start}')
                break

            # take a step, either the best one, or a random one.
            start, bestConf = step(start, bestConf, True)
       
        time.sleep(20) # pause to allow success to be viewed

    while SOLVER=='BeamSearch' or SOLVER == 'GeneticProgramming':              
        beamsize = 8
        beam = []
        for i in range(beamsize):
            beam.append(rand_init(0,n))
        
        beam.sort(key = lambda x:x[1]) #sort by number of conflicts
        count = sticks = 0



        flag = None

        while True:               #for h in range(3):
            if beam[0][1] == 0: #already have a solution?
                retval = beam[0][0]
                flag = 0
                break
            count += 1
            for i in range(beamsize):
                s,c  = step(beam[i][0], beam[i][1], 
                            display = False, stuckStop = True)
                if c is None: # this instance stuck
                    sticks += 1
                    if SOLVER == 'BeamSearch':
                        if i != 0: # this was not best so far
                            s,c = beam[0] # so copy the best 
                        else: # was best, but stuck. 
                            # make a random move
                            s[random.randint(0,n-1)] = random.randint(0,n-1)
                            c = cca(s)
                    elif SOLVER == 'GeneticProgramming':
                        # combine two best attempts:
                        bk = random.randint(1, n-2)
                        s = beam[0][0][:bk] + beam[1][0][bk:]
                        c = cca(s)

                # not stuck.
                elif c == 0:  #done?
                    flag = i
                    retval = s
                    break
                beam[i] = (s,c)
            if flag is not None:
                break
            beam.sort(key = lambda x:x[1]) #sort by number of conflicts

            #    change least successful quarter for variant on best
            #    for b in range(int(beamsize/4)):
            #        s,c  = beam[b]
            #        s[random.randint[0,n]] = random.randint[0,n]
            #        c = cca(s)
            #        beam[-b] = (s,c)

        if flag is not None:
            print('found a solution', retval, 'steps =',count, 'stuck:', sticks)
            for c,r  in enumerate(retval):
                moveQueen(c,r)
            time.sleep(20)
            

    # these two seem inaccessible
    Win.close()
    exit()





def rand_init(z,n):
    # return a random configuration of queens, and the total conflicts
    retval = [z]*n
    for c in range(n):
        r = random.randint(0,n-1)
        retval[c] = r
    return retval, cca(retval)

def step(start, bestConf, display=True, stuckStop=False):
    """
    make a single step in the iteration,
    either a step towards the goal, or a random step if no good step
    available.
    if display is set, display the new position.
    return the new position of all the queens and the current # of conflicts
    """

    global mq

    bestMove = None
    # consider all n**2-n moves, and find best
    for i in range(n):
        for j in range(n):
            if start[i] == j: continue
            test = list(start)  # copy start list
            test[i] = j
            tcon = cca(test)
            if tcon < bestConf or (tcon == bestConf and random.random()) > 0.5:
                bestMove = (i,j)
                bestConf = tcon
    # if we have a good move, take it
    if bestMove is not None:
        start[bestMove[0]] = bestMove[1]
        if display:
            moveQueen(bestMove[0],bestMove[1])
            print(f'Making move in column {bestMove[0]} to {bestMove[1]}')
            print(f'Conflicts now {bestConf}')
            time.sleep(1)
    else:
        if stuckStop:
            return start, None

        print(f'Failed to find a better move, situation {start}')
        print(f'Total of {QueenMoves - mq} moves, conflicts: {cca(start)}')
        c = random.randint(0,n-1)
        r = random.randint(0,n-1)
        start[c] = r
        bestConf = cca(start)
        if display:
            print (f'Making random move in col {c} to {r}')
            print(f'conflicts now {bestConf}')
            moveQueen(c,r)
            time.sleep(1)
    return start, bestConf

sbeam = None  #some allocate-once storage for nstep
ibeam = None
rbeam = None
rconflicts = None
sconflicts = None
tconflicts = None
F = None
G = None
def nstep(beam, conflicts, fixfunc)
    """
    [The code below is strictly illustrative.  It is not debugged.]
    This is an numpy using version of step.
    beam is an M x n array of queen positions
    conflicts is a parallel M-long column vector of conflicts for beam positions
    fixfunc(beam, conflicts, i) is a function which generates new positions
     for positions which are stuck at a local minimum.  It might be slow,
     but when n is large it seldom gets called, at least in  n-queens.
    
    The caller should set up the beam and conflicts arrays,
    and after each step check to see if conflicts[0] == 0, that is,
    we have a solution.
    """
    global sbeam, ibeam, cbeam, rbeam, rconflicts, sconflicts, tconflicts, F, G
    assert(n<255) # otherwise ibeam, sconflicts needs another int type
    if ibeam is None:
        ibeam = np.ndarray(beam.shape[0], dtype = np.uint8)

    if sconflicts is None:
        rconflicts = np.zeros(shape(conflicts), dtype = np.uint8) 
        sconflicts = np.zeros(shape(conflicts), dtype = np.uint8) 
        tconflicts = np.zeros(shape(conflicts), dtype = np.uint8) 
        F = np.zeros(shape(conflicts), dtype = np.int64) # subscripts
    else: 
        rconflicts = 0
        sconflicts = 0
        tconflicts = 255 # larger than possible conflicts.

    for i in range(n):
        for k in range(n): # loop through all rows, to discover diffs 
            if k == i: continue
            F = beam[,i] == beam[,k]
            Ibeam[F] += 1
            dif = r-k
            F = beam[,i]+dif == beam[,k]
            Ibeam[F] += 1
            F = beam[,i]-dif == beam[,k]
            Ibeam[F] += 1
        for j in range(n):  #i,j is the proposed change
            unchanged_i = 0
            changedto_j = 0
            for k in range(n): # loop through all rows, to discover diffs 
                if k == i: continue
                F = beam[,k] == j
                sconflicts[F] += 1
                dif = r-k
                F = beam[,k]+dif == j
                sconflicts[F] += 1
                F = beam[,k]-dif == j
                sconflicts[F] += 1
                
            # compute the conflict caused by this beam[i,:] = j change
            sconflicts = sconflict - Ibeam + conflicts
            
            F = tcontflicts > sconflicts
            tconflicts[F] = sconflicts[F]
            cbeam[F] = i
            rbeam[F] = j

    # compute next step
    F = conflicts > tconflicts
    for i in range(n):
        G = cbeam[F] == i
        beam[F][G,i] = rbeam[F][G]
        conflicts[F][G] = tconflicts[F][G]
    
    # now check for stuck states
    F = tconflict == 255
    for i,f in enumerate(F):
        fixfunc(beam, conflicts, i)
             
    # now sort
    F = np.argsort(beam)
    beam = beam[F]
    conflicts = conflicts[F]


def fixfunc(beam, conflicts, i):
    """
    the fixfunc, assuming it ever gets written, would fix up a specific 
    state at index i in the beam, and correspondingly in the conflicts.
    it doesn't need to use numpy to do that.
    And since I didn't pass tconflicts, it doesn't have an easy way to figure
    out for itself which other states might need to be fixed up.

    but when it is called, beam and conflicts are sorted by number of conflicts,
    so beam[0] has the least conflicts, and that number is in conflicts[0]

    depending on what is desired, fixfunc could implement combining
    two fairly good search-states [i.e. genetic programming]; it could
    duplicate a some existing state (but I didn't add the code to nstep
    which would allow two existing, identical states in the beam to 
    possibly diverge, so that is a less exciting possibility) or
    it could just make a random change, either to beam[i] or a copy of 
    a low-conflict state like beam[0]

    it could conceivably check the beam, to avoid introducing duplicates.

    In any case, it should compute the conflicts for the new state,
    and store them in conflicts[i].


    """

    raise Exception('no code here yet')          

                
                
    
        




def cca(start):
    # count all conflicts
    retval = 0
    n = len(start)
    for i in range(n):
        retval += cc(i,start)
    return retval

def ccbq(start):
    # count conflicts by queen
    # returns a count of conflicts for queens in each column of start)
    retval = []
    n = len(start)
    for i in range(n):
        retval.append(cc(i,start))
    return retval

def cc(i, start):
    # count conflicts for queen # i in start
    ir = start[i]
    retval = 0
    # if we only count conflicts up to i, we get half as many, not 2*all
    for c,r in enumerate(start[:i]):
        #if i == c:
        #    continue
        d = abs(i-c)
        if r == ir: 
            retval += 1
        elif r-d == ir:
            retval += 1
        elif r+d == ir:
            retval += 1
    return retval            


sleepPerChoice = 0.1
def backtrack(start, activeCol):
    # solve n-queens with backtracking.
    # start is a vector of current rows for n queens,
    # and we will return 
    #    either true, with start holding a successful pattern queen rows, 
    #    or failure.
    #  To do so, we iterate through the activeCol;
    #  when we get a configuration in which the activeCol is compatible
    #  with earlier colums, we either make a recursive call, passing the 
    #  configuration, and incrementing the active column, or, if we have
    #  reached column n already, returning success. 

    # also, the search updates the screen as it goes, with a little sleep
    # between choices to slow down the action..
    # parameter start is a list of row positions, for each of n queens
    # initialized to all zeros
    # parameter activeCol is the active Column to make choices for in this 
    # (recursive) call.

    # when the function begins, all the columns up to activeCol are okay,
    # that is, do not interfere with each other.  The only column that will
    # change during the call (except for recursive calls beyond this one)
    # is activeCol.  We'll start with row 0, and see if all that is 
    # to the left in the start is compatible,
    # that is, untouchable by a queen move from row 0, activeCol.
    # if zero doesn't work, we try successive values, up to n-1.
    # if we find a suitable value, 
    # (that is, one where no other queens share a row or diagonal)
    # then, depending on the value of 
    # activeCol, we are either finished setting all n values,
    # or we can make a recursive call, hoping that the activeCol + 1 values
    # we have so far set can be effectively used in the final solution.
    # if the recursive call fails, we continue search for another possible
    # value for the activeColumn.   If the recursive call succeeds,
    # we return the modified start list and a success indication.

    n = len(start)
    if activeCol >= n:
        #we're all done
        return True              # of course, since start is a list, and
                                 # since we have been updating it, there
                                 # is no real need to return it.
    # although we could quietly believe the value in start[activeCol],
    # doing so would require that we reset it on failing calls, so instead
    # doing that, we try all values from 0 to n-1.  But before we do that, we'll
    # put all the non-working rows into a set.
    badRows = set()
    for c,r in enumerate (start):
        if c >= activeCol:
            break   # consider only those rows below activeCol
        badRows.add(r)
        diff = activeCol - c
        badRows.add(r-diff)
        badRows.add(r+diff)
    for trial in range(n):
        if trial in badRows:
            continue
        #OK, can recurseL:
        start[activeCol] = trial
        moveQueen(activeCol,trial)
        time.sleep(sleepPerChoice)
        if backtrack(start,activeCol+1):
            return True
        else:
            continue
    return False  #couldn't make it work

def mark_conflicts():

    for i in range(n):
        queens[i].setOutline('yellow')
    print('deb: in mark_conflicts')

    conflicts = 0
    for i in range(n):
        qi = queens[i]
        rowi = int((qi.points[0].clone().getY()-ymargin)/unit)

        for j in range(i+1,n):
            conflict = False
            qj = queens[j]
            rowj = int((qj.points[0].clone().getY()-ymargin)/unit)
            if rowi == rowj:
                conflict = True
                print('deb', i, 'and', j, 'conflict: row',i)
            elif rowj-rowi == j-i:
                conflict = True
                print('deb', i, 'and', j, 'conflict: falling diag',i,j)
            elif rowi-rowj == j-i:
                conflict = True
                print('deb', i, 'and', j, 'conflict: rising diag', i,j)
            if not conflict:
                continue
            qi.setOutline("blue")
            qj.setOutline("blue")
            conflicts += 1
    if conflicts == 0:
            print('Success!')
            # show the supposed success
            for i in range(n):
                p = queens[i].points[0].clone()
                y = p.getY()
                rowi = int(y/unit)
                print(i,y,rowi,sep=',',end=' ')
            print()

            message = gr.Text( gr.Point(0,ymargin), 'Success!')
            message.draw(Win)
            time.sleep(20)
            Win.close()
            exit(0)
         
        

QueenMoves = 0  # I thought this could be a useful statistic
def moveQueen(column,row):
    """
    the queens only move up and down in their own column (in this n-queens 
    solution scheme)
    So the column argument tells both which queen to move, and which column
    she will move in.
    """
    global QueenMoves
    QueenMoves += 1

    midPoint = queens[column].points[0]
    x,y = midPoint.x, midPoint.y # where is she now?
    new_x,new_y = get_bottom_left(column,row)
    queens[column].move(new_x-x+hunit, new_y-y+hunit)
    #queens[column].draw(Win)

    if x > xmargin:
        # redraw old square
        ocol = int((x-xmargin)//unit)
        orow = int((y-ymargin)//unit)
        #col[ocol][orow].draw(Win)   #Maybe not necessary?
                                     # not.  doing so gives error




def get_bottom_left(column,row):
    # return coord of bottom {top?] row of column
    x = xmargin+unit*column
    y = ymargin + unit*row
    return x,y

def queen():
    # work out the queen figure in terms of unit...
    top = qunit
    mid = hunit
    bot = hunit + qunit
    l0 = int(unit/20)
    ts = int((unit - 2*l0)/3)
    ms = int(ts/2)

    
    retval =  gr.Polygon([gr.Point(mid,mid), gr.Point(mid+ms,top), 
                          gr.Point(mid+ts,mid), gr.Point(mid+3*ms,top), 
                          gr.Point(mid+ts,bot), gr.Point(mid-ts,bot),
                          gr.Point(l0,top), gr.Point(l0+ms,mid), 
                          gr.Point(l0+ts,top), gr.Point(mid,mid)])
    retval.setFill("yellow")
    return retval

if __name__ == '__main__': main()
