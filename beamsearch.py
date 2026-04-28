#!/usr/bin/env python
# Manual version of n-queen
import nqueens as nq


nq.SOLVER='BeamSearch'
nq.n = 8
nq.unit = 100
nq.hunit = int(nq.unit/2)
nq.qunit = int(nq.unit/4)

nq.main()
