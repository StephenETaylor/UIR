'''
A program to save word n-grams to a file
implements train(), and generate()
'''
import nltk
import numpy as np
import os.path as op
import pickle
import random
import sys


left_stuff  = {'"', chr(8220), '\'', '(', '[', '{', '<', '\ufeff', '$', '-'}
right_stuff = {'"', chr(8221), '\'',  ')', ']', '}', '>', ',', ';', ':', '.', '?', '!', '-'}

#tiny UI:  allow ngram_size as command line argument
ngram_size = 3
if len(sys.argv) > 1:
    try:
        ngram_size = int(sys.arv[1])
    except:
        pass



def main():
    lang_list = ['English']
    for lang in lang_list:
        train(lang, ngram_size)
        print(generate(lang, ngram_size, 'It', '.'))

def train(lang, num):

    wc = dict()
    wd = dict()
    total_words = 0
    next_word_number = 0
    word_list = []

    # a semi-dry run first to count tokens
    # and set up the token numbers
    with open(lang+'.corpus.tmp', 'wb') as fob:
        with open(op.join('language-samples',lang+'.txt')) as fi:
            for lin in fi:
                t= lin.strip()+' ' #add a trailing space, to break e.g. it\nwas 
                while t != '':
                    tlen = len(t)
                    if tlen == 1:
                        token = t
                        t = t[1:]
                    elif t[0] in left_stuff:
                        token = t[0]
                        t = t[1:]
                    elif t[0] not in right_stuff:
                        if t[0] == ' ':
                            token = ''
                            while len(t) !=0 and t[0] == ' ':
                                token += ' ' 
                                t = t[1:]
                        else:
                            token = ''
                            while (len(t) != 0 
                                    and t[0] not in right_stuff
                                    and t[0] != ' '):
                                token += t[0]
                                t = t[1:]
                        #breakflag = False
                        #for j in range(1,len(t)):
                        #    if t[j]  in right_stuff:
                        #        token = t[:j]
                        #        t = t[j:]
                        #        breakflag = True
                        #        break
                        #if not breakflag:
                        #    token = t
                        #    t = ''
                    else: # t now all right_stuff
                        token = t[0]
                        t = t[1:]
                        
                    if token == '\ufeff' : continue
                    # this also would be a spot to drop numbers, dates, etc.
                    # but in this version I don't

                    #print ('p:',token)
                    if token not in wd:
                        wd[token] = next_word_number
                        next_word_number += 1
                        word_list.append(token)
                        if len(word_list) != next_word_number: 
                            raise Exception('freakout!')
                    wc[token] = 1 + wc.get(token,0)
                    total_words += 1

                    if num != 1:
                        #write corpus to binary file for next loop
                        fob.write(np.int32(wd[token]))

    # now sort the wordlist, so that word numbers will correspond to 
    # alphabetical order for n-grams
    pairs = [(w,wc[w]/total_words) for w in word_list]
    pairs.sort()
    xlate = dict()
    wordlist = []
    wd_ = dict()
    for i,(w,p) in enumerate(pairs):
        xlate[wd[w]]=i
        wd_[w] = i
        wc[w] = p
        wordlist.append(w)

    if num == 1:
        with open(lang+'.w1','wb') as fob:
            pickle.dump(wordlist, wc, wd_)
        return


    recent = ['']*num
    currec = 0
    ngrams = dict()
    ngramoffset = 0
    ngramlist = []
    ngramc = dict()
    with open(lang+'.corpus.tmp','rb') as fib:
        def wgen():  #define generator to return 32-bit ints from corpus
            while True:
                buff = np.frombuffer(fib.read(4096), dtype= np.int32)
                if buff.size == 0: return
                for w in buff:
                    yield xlate[w]

        for wno in wgen():
                token = wordlist[wno]
                currec = (currec + 1)% num
                recent[currec] = wno #token

                tuplis = [None]*num
                badtuple = False
                for i in range (num):
                    x = recent[(currec + num - i)%num]
                    if x == '':
                        badtuple = True
                        break
                    tuplis[num-i-1] = x
                if badtuple:
                    continue
                ngram = tuple(tuplis)
                ngramc[ngram] = 1 + ngramc.get(ngram, 0)

    if len(wordlist) < 2**16 and max(ngramc.values())< 2**16:
        wdtype = np.uint16
        wbc = 2
    else:
        wdtype = np.uint32
        wbc = 4

    shp = (len(ngramc),num+1)
    ng = np.ndarray(shape=shp, dtype = wdtype)
    for i,(ngram,ct) in enumerate(sorted(ngramc.items())):
        for j in range(num):
            x = ngram[j]
            ng[i,j] = x
        #ng[i,:num] = ngramlist[i,:num]
        ng[i,num] = ct
            


    with open(lang+'.w'+str(num),'wb') as fob:
        pickle.dump(wordlist, fob)
        x = ng.shape[0]
        y = ng.shape[1]
        fob.write(np.uint64(x).tobytes())
        fob.write(np.uint64(y).tobytes())
        fob.write(np.uint64(wbc).tobytes())
        ng.tofile(fob)
                

def generate(lang, num, start, fin):
    """
    #with open(lang+'.w1', 'rb') as fib:
    #    (wordlist, wc, wd) = pickle.load(fib)

    #if len(wd) < 2**16 and max(wc.values())< 2**16:
        wdtype = np.uint16
    #else:
    #    wdtype = np.uint32
    """
    with open(lang+'.w'+str(num),'rb') as fib:
        #(ngramlist,ngramc,ngrams) = pickle.load(fib)
        #npgr = np.array(ngramlist)
        #sl = np.argsort(npgr)
        wordlist = pickle.load(fib)
        wd = {w:i for i,w in enumerate(wordlist)}
        buf = fib.read(24)
        xy = np.frombuffer(buf, dtype= np.uint64)
        tc = int(xy[0]*xy[1]*xy[2])
        if xy[2] == 2: 
            wdtype = np.uint16
        else:
            wdtype = np.uint32
        ngramlist = np.frombuffer(fib.read(tc),dtype = wdtype)
        ngramlist = ngramlist.reshape((xy[0],xy[1]))

    # Startup, starting with one word, until we have num
    start_n = wd[start]
    start_list = [ start_n]
    end_n = wd[fin]
    retval = ''
    previous_token = None
    while True:
        new_token = wordlist[start_list[-1]]
        #if (previous_token is not None 
        #        and previous_token not in left_stuff
        #        and new_token not in right_stuff):
        #    retval += ' '
        retval += new_token
        if start_list[-1] == end_n: break
        previous_token = new_token
        
        
        # find the two ends of the start_list in ngramlist
        while True: # loop until we have a non-zero range, discarding context
            for k in range(num-1):
                if k == 0:
                    i = np.searchsorted(ngramlist[:,k], start_list[k],
                            side = 'left')
                    j = np.searchsorted(ngramlist[:,k], start_list[k],
                            side = 'right')
                elif k>=len(start_list): # only for first few tokens
                    break
                else:
                    while ngramlist[i,k] < start_list[k]:
                        i += 1
                    while ngramlist[j-1,k] > start_list[k]:
                        j -= 1
            if j-i > 0: break
            # wasn't any.  Usually this might happen while growing start_list;
            # otherwise the existence of a,b,c in the corpus suggests that
            # there must have been a,b,c,x (unless a,b,c are at corpus end)
            oops =  start_list.pop(0) # shorten context
            if len(start_list) == 0:
                start_list.append((oops+1%len(wd))) # try a random next word

        tot = sum(ngramlist[i:j,num])
        idx = np.argsort(ngramlist[i:j,num]) # want these reversed:
        idx += i # change these values into ngramlist indices
        #print('mean', ngramlist[idx,num].mean(), 'count:',len(idx))
        flip = tot* random.random()  # a number (0,tot)

        choice = None
        for c in range(1, 1+len(idx)): # start at top of : range(0,j-i+1):
            freq = ngramlist[idx[-c], num]
            if flip < freq:
                choice = idx[-c]
                #print('choice',c,choice, end='')
                break
            flip -= freq
        if choice is None:
            choice = idx[-1]  # that is, want largest value, was :[0]
        nexttoken = ngramlist[choice,len(start_list)] # take token after match
        #print(' token ', wordlist[ nexttoken])
        start_list.append(nexttoken)
        if len(start_list) > num-1:
            del start_list[0]

    return retval




def main2():
    import os.path
    for i in range(30):
        ng = 2+i//5
        print (ng,'- grams')
        if not os.path.exists('English'+'.w'+str(ng)):
            train('English',ng)

        print(generate('English',ng, 'It', '.'))



if __name__ == '__main__':  main2()


