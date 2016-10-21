"""
Program for text-summarization using TextRank algorithm
Dependencies:
    networkx
    nltk
    numpy
"""

import io,os,nltk,itertools
import networkx as nx
from operator import itemgetter

def filter_tags(tagged, tags=['NN', 'JJ', 'NNP']):
    return [item for item in tagged if item[1] in tags]

def normalize(tagged):
    return [(item[0].replace('.', ''), item[1]) for item in tagged]

def unique_everseen(iterable, key=None):
    """List unique elements, preserving order. Remember all elements ever seen."""
    seen = set()
    seen_add = seen.add
    if key is None:
        for element in itertools.ifilterfalse(seen.__contains__, iterable):
            seen_add(element)
            yield element
    else:
        for element in iterable:
            k = key(element)
            if k not in seen:
                seen_add(k)
                yield element

def levDis(firstString, secondString):
    """Function to find the Levenshtein distance between two words/sentences""" 
    if len(firstString) > len(secondString):
        firstString, secondString = secondString, firstString
    distances = range(len(firstString) + 1)
    for index2, char2 in enumerate(secondString):
        newDistances = [index2 + 1]
        for index1, char1 in enumerate(firstString):
            if char1 == char2:
                newDistances.append(distances[index1])
            else:
                newDistances.append(1 + min((distances[index1], distances[index1+1], newDistances[-1])))
        distances = newDistances
    return distances[-1]

def buildGraph(nodes):
    """nodes - list of hashables that represents the nodes of the graph"""
    gr = nx.Graph() #initialize an undirected graph
    gr.add_nodes_from(nodes)
    nodePairs = list(itertools.combinations(nodes, 2))

    #add edges to the graph (weighted by Levenshtein distance)
    for pair in nodePairs:
        firstString = pair[0]
        secondString = pair[1]
        levDistance = levDis(firstString, secondString)
        gr.add_edge(firstString, secondString, weight=levDistance)

    return gr

def extractKeyphrases(text):
    #tokenize the text using nltk
    wordTokens = nltk.word_tokenize(text)

    #assign POS tags to the words in the text
    tagged = nltk.pos_tag(wordTokens)
    textlist = [x[0] for x in tagged]
    
    tagged = filter_tags(tagged)
    tagged = normalize(tagged)

    unique_word_set = unique_everseen([x[0] for x in tagged])
    word_set_list = list(unique_word_set)

   #this will be used to determine adjacent words in order to construct keyphrases with two words

    graph = buildGraph(word_set_list)

    page_rank = nx.pagerank(graph, weight='weight')

    #most important words in ascending order of importance
    keyphrases = sorted(page_rank, key=page_rank.get, reverse=True)

    aThird = len(word_set_list) / 3
    keyphrases = keyphrases[0:aThird+1]
    # take the combined keywords together as given in the paper
    modifiedKeyphrases = set([])
    dealtWith = set([]) #keeps track of individual keywords that have been joined to form a keyphrase
    i = 0
    j = 1
    while j < len(textlist):
        firstWord = textlist[i]
        secondWord = textlist[j]
        if firstWord in keyphrases and secondWord in keyphrases:
            keyphrase = firstWord + ' ' + secondWord
            modifiedKeyphrases.add(keyphrase)
            dealtWith.add(firstWord)
            dealtWith.add(secondWord)
        else:
            if firstWord in keyphrases and firstWord not in dealtWith: 
                modifiedKeyphrases.add(firstWord)

            #if this is the last word in the text, and it is a keyword,
            #it definitely has no chance of being a keyphrase at this point    
            if j == len(textlist)-1 and secondWord in keyphrases and secondWord not in dealtWith:
                modifiedKeyphrases.add(secondWord)
        
        i = i + 1
        j = j + 1
        
    return modifiedKeyphrases

def extractSentences(text):
    sent_detector = nltk.data.load('tokenizers/punkt/english.pickle')
    sentenceTokens = sent_detector.tokenize(text.strip())
    graph = buildGraph(sentenceTokens)

    page_rank = nx.pagerank(graph, weight='weight')

    #most important sentences in ascending order of importance
    sentences = sorted(page_rank, key=page_rank.get, reverse=True)

    #return a 100 word summary
    summary = ' '.join(sentences)
    summaryWords = summary.split()
    summaryWords = summaryWords[0:101]
    summary = ' '.join(summaryWords)

    return summary



# txt = "She may look like easy pickings for an Early Cretaceous predator, but this iguanodon isnt going down without a fight.\
# As a pair of bloodthirsty Utahraptors rush in for the kill, this 16-foot (9-meter) foliage destroyer simply whips out her stiletto thumb spikes as if to say, Bring it, you Salt Lake sons of guns. Ive got one for each of ya\
# The first attacker springs through the air, talons eager for blood. And so iguanodon obliges it. Much like human martial artists more than 100 million years later, she dodges and administers a brutal thumb strike to her opponents throat, puncturing the delicate flesh and splattering the dirt with blood.\
# But the other Utahraptor has already pounced as well. She feels its talons sink into her back, severing veins and seeking organs like water-thirsty roots. She tries to shake the predator free, but it holds fast. The talons sink deeper with a flash of red-hot pain. Finally, she feels its teeth bite into the side of her neck which lets her know exactly where her enemys head is.\
# She drives both thumbs back into the attackers eye sockets, gouging forth blood and jelly, sending the thing tumbling back to the earth in a tangle of claws, feathers and blind rage.\
# Or at least thats how things might have gone. It's easy to construct such cinematic dino melees, especially when confronted with a spike-thumbed dino like those of the Iguanodon genus. But no matter how much we want those thumbs to be certified murder weapons, we still dont know exactly what they were for."



# k = extractKeyphrases(txt)
# print k
# s = extractSentences(txt)
# print "\n"
# print s

# def writeFiles(summary, keyphrases, fileName):
#     "outputs the keyphrases and summaries to appropriate files"
#     print "Generating output to " + 'keywords/' + fileName
#     keyphraseFile = io.open('keywords/' + fileName, 'w')
#     for keyphrase in keyphrases:
#         keyphraseFile.write(keyphrase + '\n')
#     keyphraseFile.close()

#     print "Generating output to " + 'summaries/' + fileName
#     summaryFile = io.open('summaries/' + fileName, 'w')
#     summaryFile.write(summary)
#     summaryFile.close()

#     print "-"


# #retrieve each of the articles
# articles = os.listdir("articles")
# for article in articles:
#     print 'Reading articles/' + article
#     articleFile = io.open('articles/' + article, 'r')
#     text = articleFile.read()
#     keyphrases = extractKeyphrases(text)
#     summary = extractSentences(text)
#     writeFiles(summary, keyphrases, article)