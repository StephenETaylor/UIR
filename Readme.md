The files in this repository are expected to be used in my spring 2026
lectures in Pavel Kral's UIR course at ZCU.

The slides for the first lecture, on 4 March 2026, were mostly
from the CS188 course at the University of California, Berkeley.
They came from lectures on "Adversarial Search" (that is, game-playing)
and "Local Search" (that is, solving puzzles.)
I don't provide them here, but a web search will help you find lectures from
past semesters.

>n-queens.py contains python code to interface with graphics.py and
             compute/display solutions to the n-queens puzzle
             using:  
    manual manipulation of the queens  
    back-tracking [ that is, a depth-first search ]  
    hill-climbing  
    beam search  
    genetic programming   

>graphics.py     is a program written by John Zelle, of which you can probably 
            find several more copies on the web,  for example:

    https://gist.github.com/aslilac/38a4192e3dcd28ea08e19cd90e16ccf6

Not to mention better
            documentation for using it, for example,

https://www.rose-hulman.edu/class/csse/resources/Python/zellegraphics.pdf

The slides for the 29 April 2026 lecture are in two pdf files:

Language Models.pdf
Karpathy_s_medium_size_LSTM_language_model_.pdf

The code used in some of the Language model slides is:  
        >neighbors.py   which prints out nearby words in word-embedding vector space
   >cb-lc.py       character n-gram model demo.  It prompts you for a language
                   and an 'n' for the n-gram.  It expects that you will have
                   provided a file english.train, česky.train, (or whatever
                   you said for a language name).train, to use as a corpus.
                   I'm not providing any here.  I downloaded a few from
                   https://www.gutenberg.org.  If you do that, you should 
                   probably edit out the project Guttenberg information at the
                   beginning and end of the file, because it will mess
                   up your character counts otherwise.  
    >word_ngram.py  word n-gram model demo.  It looks for its corpus in
                   ./language_samples/(whatever you call the language).txt.
                   Again, www.gutenberg.org is probably a good source.
                   Deleting the Gutenberg license, etc. is probably less 
                   important here, but still matters -- why would you want all
                   those English bigrams in your Japanese model?  

