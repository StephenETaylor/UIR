'''
this program illustrates identifying languages from a small text sample,
based on single character examples, two character examples, three ..., etc.
'''
import math
import random

def main():
    while True:
        lang = input('give me a language name: ').strip()
        number = int(input('how many characters per sample? ').strip())
        task = input('train or test or guess or generate: ').strip()
        
        lt = len(task)
        if task == 'train'[:lt]:
            train(lang, number)
            continue
        elif task == 'test'[:lt]:
            test(lang, number)
            continue
        elif task == 'generate'[:lt]:
            start = input('starting character: ')
            if start == 'newline':
                start = '\n'
            else: start = start[0]
            terminator = input('ending character: ')
            if terminator == 'newline':
                terminator = '\n'
            else: terminator = terminator[0]

            reps = int(input('number of reps: '))
            for _ in range(reps):
                print(generate(lang, number, 
                               terminator=terminator, 
                               previous=start))
        elif task == 'guess'[:lt]:
            guess(lang, number)
            continue

def get_dict(filepath, number):
    item_counts = dict()
    total_items = 0
    def count(x):
        nonlocal total_items
        total_items += 1
        item_counts[x] = 1 + item_counts.get(x,0)
    
    #try:
    for _ in range(1):
        with open(filepath) as fi:

            for lin in fi:
                len_lin = len(lin)
                pref = '\n'+lin[:number-1] # this creates '\n\n' for empty lines
                if len(pref) == number:
                    count(pref)
                    pass
                for i in range(len_lin-number+1) :
                    pref = lin[i:i+number]
                    if len(pref) == number:
                        count(pref)
                    else: 
                        pass
                # the following code ensured partial strings padded w/ '\n'
                #for i in range(len_lin-number,len_lin) :
                #    item = lin[i:] + '\n'*(len_lin-i) #arith was wrong here
                #    count(item)

        return item_counts, total_items            

    #except Exception as err:
    #    print(err)
    #    return None, None

def train(lang, number):
    item_counts, total_items = get_dict(lang+'.train', number)

    # write frequencies to file
    with open(lang+'.'+ str(number), 'w') as fi:
        for item in sorted(item_counts.keys()):
            val = item_counts[item]
            freq = val / total_items
            if freq < 0.5e-7: continue
            print(repr(item)+',%.7f'%freq, file=fi)

    return normalize(item_counts)

def get_model(file_handle):
    mod = dict()
    for lin in file_handle:
        line = eval(lin)      # handle '\n', '\t', etc., as well as vanilla 'x'
        mod[line[0]] = line[1]
    return normalize(mod)

def cosine(mod, dic):
    '''
    return the cosine betwwen the vector of the model, and the vector of the test-sample
    '''
    sumprod = 0
    msum = 0
    for k,vm in mod.items():
        #msum += vm*vm
        sumprod += vm*dic.get(k,0)
    #mnorm = math.sqrt(msum)
    return sumprod #/mnorm

def normalize(dic):
    norm2=0
    norm2 = sum((v*v for v in dic.values()))
    #    for v in dic.values():          norm2 += v*v
    norm = math.sqrt(norm2)
    for k,v in dic.items():
        dic[k] = v/norm
    return dic


def test(lang, number):
    model = get_lang_n(lang, number)
    tf = input('enter test filename: ')
    cos = test1(model, tf, number)

    print('plausibility:', cos)

def test1(model, tf, number):
    while True:
        try:
            test_items,test_counts = get_dict(tf , number)
            test_items = normalize(test_items)
            cos = cosine(model,test_items)
            return cos
        except Exception as err:
            print(err)
            return 0





def generate(lang,n,terminator='\n', previous=' '):
    '''
    using the probabilities given by the model, print a string of characters
    such that:
        the last character is the specified terminator -- ' ', '.', & '\n' 
                                                            each makes sense

        if previous = ''
        the first character is randomly chosen according to the distribution
        of individual character in the lang.1 (unigram probabilities) file.

        character k<n is similarly chosen from among the last characters
        of keys in the lang.k file which begin with the k-1 character prefix 
        of characters already chosen.

        and characters m where m>=n are randomly chosen as the last characters
        of keys in the lang.n file which begin with the n-1 characters most
        recently generated.
        
        if previous != ''  and len(previous) == j 
        the first character is randomly chosen according to the distribution
        of last characters of keys with prefix previous in the lang.(j+1)
        ((j+1)-gram probabilities) file.

        character k<n is similarly chosen from among the last characters
        of keys in the lang.(j+k) file which begin with previous followed by
        the k-1 character prefix of characters already chosen.

        and characters m where m>=n are randomly chosen as the last characters
        of keys in the lang.n file which begin with the n-1 characters most
        recently generated.

        In any case, a fallback is possible, either because there is no key in
        the database for the given prefix, or just to keep things exciting.
        Instead of the n character prefix, we can fall back to the n-1, n-2, 
        ..., 0 character prefix instead.
        
    '''
    retval = ''
    lp = len(previous)
    if lp == 0:
        sofar = ''
        i = 1
    else:
        sofar = previous
        i = 1 + lp
    
    while True:
        while True:  #choose trial_list for next character
            mod = get_lang_n(lang,i)
            lsf = len(sofar)
            if i == 1 and lp == 0:
                trial_list = list(((freq, item) for item, freq in mod.items()))
            else:
                trial_list = list(((freq, item) for item, freq in mod.items()
                                                        if sofar == item[:lsf]))
            if len(trial_list) == 0: # search was unsuccessful
                i -= 1               # try shorter prefix (in different model)
                sofar = sofar[1:]    
            else: break              # search was successful.

        # now have chosen trial_list.
        trial_list.sort(reverse=True)
        tsum = sum((t[0] for t in trial_list))
        rs = tsum * random.random()
        selector = 0

        ltl = len(trial_list)-1 
        while selector < ltl and trial_list[selector][0] <= rs:
            rs += - trial_list[selector][0]
            selector += 1
        choice = trial_list[selector][1][-1] # take last char here, instead
                                              # of allocating a new string
                                              # for each pair in trial_list
        sofar += choice
        retval += choice

        if choice == terminator: return retval

        if i >= n: 
            while i>=n:
                sofar = sofar[1:] # leave len(sofar) == n-1 for next iteration
                i -= 1
            i = n
        else:
            i += 1            # sofar has i chars. next use lang.(i+1) model 



            

model = dict()
def get_lang_n(lang, number):
    '''
    if we have previously stashed the indicated model in a table in dict model,
    then retrieve and return it.
    if not, and the file lang+'.%d'%number exists, retrieve and stash the file
    if not, train the model, stash it in the dict and the file, and return it.

    the dict model is indexed by language, and the values found are an ordered
    list of models or None, i.e, [german.1, None, german.3]
    '''
    
    global model

    model_list = model.get(lang, None)
    if model_list is None: model[lang] = model_list = [None]*number
    while len(model_list) < number:
        model_list.append(None)
    if model_list[number-1] is not None:
        return model_list[number-1]
    try:
        with open(lang + '.' + str(number)) as fi:
            retval = model_list[number-1] = get_model(fi)
        return retval
            
    except: # no file; so train
        retval = train(lang, number) # train stores result in file
        model_list[number-1] = retval
        return retval

def main1():
    '''
    A slide demo; should illustrate that larger segments are more recognizable,
    That languages can be distinguished.
    '''

    #for all languages
     #for all test files
      #print cosines for test in all languages
    langs = 'chinese czech English french german japanese'.split()
    #langs = 'English french'.split()
    tags = '.A. .B. .C.'.split()
    trange = [10,5,2]

    for lang in langs:
        for tag,tr in zip(tags,trange):
            for t in range(tr):
                fn = lang+tag+str(t)
                    # new page
                print()
                print(fn)
                for tl in langs:
                    print('%10s'%tl, end=' ')
                    for num in range(1,6):
                        mod = get_lang_n(tl,num)
                        print('%.5f'%test1(mod, fn+'.test', num), end = '  ')
                    print()

def main2():
    '''
    Prepare a few generated words, for various  n-gram models
    '''
    langs = 'English czech'.split()
    langs = 'English'.split()

    for lang in langs:
        print(lang)
        for i in range(1,13):
            print(i,'character model')
            print()

            print('preceded by " ", terminated with " "')
            for _ in range(50):
                print (generate(lang,i,terminator=' ',previous=' '), end=' ')
            print()
            print()

            print('preceded by "\n", terminated with " "')
            for _ in range(50):
                print (generate(lang,i,terminator=' ',previous='\n'), end=' ')
            print()
            print()

            print('preceded by "\n", terminated with "\n"')
            for _ in range(50):
                print (generate(lang,i,terminator='\n',previous='\n'), end='')
            print()
            print()


if __name__ == '__main__': main() #main2()
