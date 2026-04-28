import math

with open('stepsSticks.t') as fi:
    sum_steps = sum_sticks = 0
    steps2 = sticks2 = 0
    count = 0
    for lin in fi:
        line = lin.strip().split()
        steps = int(line[0])
        sticks = int(line[1])
        sum_steps += steps
        sum_sticks += sticks
        steps2 += steps*steps
        sticks2 += sticks*sticks
        count += 1
    mean_steps = sum_steps/count
    mean_sticks = sum_sticks/count
    var_steps = steps2 /count - mean_steps* mean_steps
    var_sticks = sticks2 /count - mean_sticks* mean_sticks
    stddev_sticks = math.sqrt(var_sticks)
    stddev_steps = math.sqrt(var_steps)

    print ( f'mean steps: {mean_steps} mean_sticks {mean_sticks}')
    print ( f'var steps:  {var_steps}  var_sticks:  {var_sticks}')
    print ( f'stddev steps:  {stddev_steps}  stddev_sticks:  {stddev_sticks}')
    print ( f'ratio, sticks/steps: {sum_sticks / sum_steps}')


