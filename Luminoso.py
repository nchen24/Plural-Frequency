# Author: Nick Chen
import sys
import os
import operator
import inflect  # See README
from collections import defaultdict

CORPUS_FOLDER  = "./brown_corpus/"
OUTPUT_FILE    = "./output.txt"
THRESHHOLD     = 5
FOREIGN_TAG    = "fw"
NOUN_TAG       = "nn"
PLURAL_TAG     = "s"
p              = inflect.engine()


def toSingular(word):
    """ Purpose: Convert word to its singular form.
        Parameters:
            word: The word to convert.
        Return: Singular form of word.
        Notes: Due to a bug(?) in inflect.singular_noun breaks on certain cases
               (notably 'two-by-fours'), so a very rough-and-dirty method to
               avoid that and similar cases is to simply return the word minus
               the last letter (given that most plurals are simply formed by
               adding an s).  Presumably these cases occur infrequently enough
               that they don't actually exceed THRESHHOLD.

    """
    try:
        return p.singular_noun(word)
    except:
        return word[:-1]


def parseInput():
    """ Purpose: Parse the input to two dictionaries: one for plurals and one
                 for singular nouns, where the value is how many times that
                 word has been seen.
        Parameters: None.
        Return: The dictionaries for plurals, singulars; in that order.
        Notes: defaultdict sets the default value for a dictionary.  This
               allows just using += 1 when a word is seen, rather than checking
               if the word exists, if it doesn't, setting it to 1, and if it
               does, incrementing it by 1.

               TODO: sys.stderr.write will fail in python 3, change to:
                     print(msg, file=sys.stderr)

    """
    plurals   = {}; plurals   = defaultdict(lambda: 0, plurals)
    singulars = {}; singulars = defaultdict(lambda: 0, singulars)
    for file in os.listdir(CORPUS_FOLDER):
        try:
            with open(CORPUS_FOLDER + file, 'r') as fr:
                for line in fr:
                    for wordAndTag in line.split(None):
                        splitWord = wordAndTag.split('/')
                        if len(splitWord) != 1:  # Ignore non-words
                            word = splitWord[0]
                            tag  = splitWord[1]
                            if tag == "vvs":
                                print word, tag
                                raw_input()
                            if not FOREIGN_TAG in tag:
                                if NOUN_TAG + PLURAL_TAG in tag:
                                    plurals[word.lower()] += 1
                                elif NOUN_TAG in tag:
                                    singulars[word.lower()] += 1
        except IOError:
            sys.stderr.write("Warning: Could not open file %s\n"
                             % (CORPUS_FOLDER + file))
    return plurals, singulars


def calcPercentPlurality(plurals, singulars):
    """ Purpose: Given two dictionaries of plurals and singulars, calculate how
                 often that word is plural.
        Parameters:
            plurals:   A dictionary where k = a plural, v = how many times that
                       word has occurred
            singulars: A dictionary where k = a singular, v = how many times
                       that word has occurred
        Return: A dictionary where k = a plural word v = a percentage of how
                often that word is plural
        Notes: numSingle can be safely called even if that word was never seen
               in singular form because the default values of the dicts have
               been set to zero

    """
    rateOfPlurality = {}
    for k, v in plurals.iteritems():  # Create iterable object from plurals
        numPlural = v
        numSingle = singulars[toSingular(k)]
        if numPlural > numSingle:
            rateOfPlurality[k] = 100.0 * numPlural / (numPlural + numSingle)
    printPercentPlurality(rateOfPlurality, plurals)


def printPercentPlurality(rateOfPlurality, plurals):
    """
        Purpose: Print out the dictionary.
        Parameters:
            rateOfPlurality: A dictionary where k = a plural v = how often that
                             word occurs as a plural (in %)
            plurals:         A dictionary where k = a plural, v = how many
                             times that word has occurred
        Return: Nothing.
        Notes: None.

    """
    with open(OUTPUT_FILE, "w+") as fw:
        # Create iterable object from a dict, reverse sorted by value, not key
        for k, v in sorted(rateOfPlurality.iteritems(),
                           key=operator.itemgetter(1), reverse=True):
            if plurals[k] > THRESHHOLD:
                fw.write(k + " %f%%\n" % v)  # %% is used to escape %


def main():
    """
        Purpose: Deal with command line arguments, then call the functions that
                 do the bulk of the work.
        Parameters:
            sys.argv[1]: Optional argument for a path to a corpus.  Will use
            './brown_corpus/' if no other argument is given.
        Return: Zero on success.
        Notes: None.
    """
    if len(sys.argv) > 1:
        if sys.argv[1] == "-h" or sys.argv[1] == "-help":
            print "Usage: %s ([CORPUS_FOLDER] [OUTPUT_FILE])" % sys.argv[0]
            exit(1)
        global CORPUS_FOLDER
        CORPUS_FOLDER = sys.argv[1]
        if CORPUS_FOLDER[:-1] != os.sep:
            CORPUS_FOLDER += os.sep
        global OUTPUT_FILE
        OUTPUT_FILE = sys.argv[2]

    # * unpacks the argument from a tuple to two arguments
    calcPercentPlurality(*parseInput())
    return 0


if __name__ == "__main__":
    main()
