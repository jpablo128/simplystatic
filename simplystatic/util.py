# -*- coding: utf-8 -*-
#!/usr/bin/python

'''Provide some text utilities.

This small module is just used to contain simple text utilities that 
might be used to cleanup text strings or to generate random text.

Most utilities are just functions.

Functions included:

    - sanitize_name: 


Classes included:

- Chomsky: This is and adaptatiion of the Chomsky utility by Raymond
           Hettinger. Generates random text.

'''

import textwrap, random
from itertools import chain, islice, izip
import string
import uuid
import datetime
import subprocess


def make_slug(rawname):
    sname = rawname
    sname =  sname.replace('á', 'a').replace('é', 'e').replace('í', 'i').replace('ó', 'o').replace('ú', 'u')
    sname =  sname.replace('Á', 'A').replace('É', 'E').replace('Í','I').replace('Ó','O').replace('Ú','U')
    #remove other non-ascii chars if there are any
    sname = ''.join([i if ord(i) < 128 else ' ' for i in sname])
    ic = string.punctuation.replace("_", "")  # ic = invalid chars, we remove the underscore
    #remove all punctuation symbols
    for ps in ic: 
        if ps in sname:
            sname = sname.replace(ps,"")
    sname = ('_'.join(sname.split())).lower()

    return unicode(sname,"UTF-8")

def random_title(withuuid=True):
    c = Chomsky()
    s = c.generate(1)
    sa = s.split()
    random.shuffle(sa)
    sa = sa[0:4]
    if withuuid:
        sa.append(uuid.uuid1().hex[0:9])
    r = ' '.join(sa)
    return r

# def date_generator(sty = random.randint(2008,datetime.datetime.now().year-1) ):
#     '''Generator that provides incremental dates.'''
#     d = datetime.date(sty,1,1)
#     while True:
#         #d = d + datetime.timedelta(days=random.randint(1,6))
#         d = d + datetime.timedelta(2)
#         yield d

def random_date():
    '''Return a valid random date.'''
    d = datetime.datetime.now().date()
    d = d - datetime.timedelta(random.randint(20,2001))
    return d

def random_text(paragraphs=4):
    c = Chomsky()
    s = c.generate(paragraphs)
    return s

def random_paragraphs(p=4):
    lines = []
    for h in range(1,random.randint(1,p)):
        lines.append(random_text(random.randint(2,7)))
    txt = '\n\n'.join(lines)
    return txt

def random_md_page():
    '''Generate random markdown page content..

    If the parameters are zero, instead of a fixed number of elements 
    it uses a random number.

    '''
    # headers #, ##
    # blockquote >
    # lists *
    # codeblock (indent 4 spaces)
    # hrule, 3 or more - in a line
    # emphasis: word surrounded by one * or _
    lines = []
    lines.append("\n# " + random_title(False) + "\n") # add title
    lines.append("\n" + random_text(1) + "\n") #and 1 paragraphs
    for h in range(1,random.randint(2,5)):
        lines.append("\n## " + random_title(False) + "\n") # add header
        lines.append("\n" + random_paragraphs(random.randint(1,5)) + "\n") #and some paragraphs
        for sh in range(1,random.randint(1,4)):
            lines.append("\n### " + random_title(False) +"\n") # add subheader
            lines.append("\n" + random_paragraphs(random.randint(4,13)) + "\n") #and some paragraphs
    txt = "\n".join(lines)
    return txt






class Chomsky():
    '''CHOMSKY is an aid to writing linguistic papers in the style
        of the great master.  It is based on selected phrases taken
        from actual books and articles written by Noam Chomsky.
        Upon request, it assembles the phrases in the elegant
        stylistic patterns that Chomsky is noted for.
        To generate n sentences of linguistic wisdom, type
            (CHOMSKY n)  -- for example
            (CHOMSKY 5) generates half a screen of linguistic truth.

    '''

    leadins = """To characterize a linguistic level L,
        On the other hand,
        This suggests that
        It appears that
        Furthermore,
        We will bring evidence in favor of the following thesis:
        To provide a constituent structure for T(Z,K),
        From C1, it follows that
        For any transformation which is sufficiently diversified in application to be of any interest,
        Analogously,
        Clearly,
        Note that
        Of course,
        Suppose, for instance, that
        Thus
        With this clarification,
        Conversely,
        We have already seen that
        By combining adjunctions and certain deformations,
        I suggested that these results would follow from the assumption that
        If the position of the trace in (99c) were only relatively inaccessible to movement,
        However, this assumption is not correct, since
        Comparing these examples with their parasitic gap counterparts in (96) and (97), we see that
        In the discussion of resumptive pronouns following (81),
        So far,
        Nevertheless,
        For one thing,
        Summarizing, then, we assume that
        A consequence of the approach just outlined is that
        Presumably,
        On our assumptions,
        It may be, then, that
        It must be emphasized, once again, that
        Let us continue to suppose that
        Notice, incidentally, that """
    # List of LEADINs to buy time.

    subjects = """ the notion of level of grammaticalness
        a case of semigrammaticalness of a different sort
        most of the methodological work in modern linguistics
        a subset of English sentences interesting on quite independent grounds
        the natural general principle that will subsume this case
        an important property of these three types of EC
        any associated supporting element
        the appearance of parasitic gaps in domains relatively inaccessible to ordinary extraction
        the speaker-hearer's linguistic intuition
        the descriptive power of the base component
        the earlier discussion of deviance
        this analysis of a formative as a pair of sets of features
        this selectionally introduced contextual feature
        a descriptively adequate grammar
        the fundamental error of regarding functional notions as categorial
        relational information
        the systematic use of complex symbols
        the theory of syntactic features developed earlier"""
    # List of SUBJECTs chosen for maximum professorial macho.

    verbs = """can be defined in such a way as to impose
        delimits
        suffices to account for
        cannot be arbitrary in
        is not subject to
        does not readily tolerate
        raises serious doubts about
        is not quite equivalent to
        does not affect the structure of
        may remedy and, at the same time, eliminate
        is not to be considered in determining
        is to be regarded as
        is unspecified with respect to
        is, apparently, determined by
        is necessary to impose an interpretation on
        appears to correlate rather closely with
        is rather different from"""
    #List of VERBs chosen for autorecursive obfuscation.

    objects = """ problems of phonemic and morphological analysis.
        a corpus of utterance tokens upon which conformity has been defined by the paired utterance test.
        the traditional practice of grammarians.
        the levels of acceptability from fairly high (e.g. (99a)) to virtual gibberish (e.g. (98d)).
        a stipulation to place the constructions into these various categories.
        a descriptive fact.
        a parasitic gap construction.
        the extended c-command discussed in connection with (34).
        the ultimate standard that determines the accuracy of any proposed grammar.
        the system of base rules exclusive of the lexicon.
        irrelevant intervening contexts in selectional rules.
        nondistinctness in the sense of distinctive feature theory.
        a general convention regarding the forms of the grammar.
        an abstract underlying order.
        an important distinction in language use.
        the requirement that branching is not tolerated within the dominance scope of a complex symbol.
        the strong generative capacity of the theory."""
    # List of OBJECTs selected for profound sententiousness.


    def generate(self,times=1, line_length=72):
        parts = []
        for part in (Chomsky.leadins, Chomsky.subjects, Chomsky.verbs, Chomsky.objects):
            phraselist = map(str.strip, part.splitlines())
            random.shuffle(phraselist)
            parts.append(phraselist)
        output = chain(*islice(izip(*parts), 0, times))

        return textwrap.fill(' '.join(output), line_length)
