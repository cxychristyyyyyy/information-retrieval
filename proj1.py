import sys
import requests
import numpy as np
import urllib
from urllib import request
import string
import math
import string
import re
from googleapiclient.discovery import build

def main():
    
    # Gather variables from command line
    API_KEY = sys.argv[1]
    ENGINE_ID = sys.argv[2]
    PRECISION = float(sys.argv[3])
    QUERY = " ".join(sys.argv[4:])

    # Query for results using user inputted query
    service = build("customsearch", "v1", developerKey=API_KEY)
    results = service.cse().list(
      q=QUERY,
      cx=ENGINE_ID,
    ).execute()

    results = results["items"]

    # Allocate array for collecting relevence of each result
    relevant = []
    relevantResults = []

    print("Parameters:")
    print(f'Client Key: {API_KEY}')
    print(f'Engine Key: {ENGINE_ID}')
    print(f'Query: {QUERY}')
    print(f'Precision: {PRECISION}')
    print(f'Google Search Results:')
    print()

    # Exit if results returned are less than 10 on first iteration
    if len(results) < 10:
        print("Returned less than 10 results. Exiting now.")
        exit()
    else:
        results = results[0:10]

    #to check if the file is html file
    isHTML = []

    #Number of html
    Nhtml = 10

    # Display each page result and as if it is relvevent
    while np.count_nonzero(relevant)/Nhtml < PRECISION:

        results = results[0:min(10, len(results))]

        # Reset relevanct array
        relevant = []

        #Reset isHTML array
        isHTML = []

        # Display results and determine relevance
        for page in range(len(results)):

            #store the feedback
            print(f'Result {page+1}:')
            print("[")
            print(" " + results[page]["link"])
            print(" " + results[page]["title"])
            print(" " + results[page]["snippet"])
            print("]")
            rel = input("Relevant (Y/N)? ")
            relevant.append(1 if rel == 'Y' else 0)
            print()

            #check if it's a html file
            try:
                res = requests.head(results[page]["link"])
                contentType = res.headers["Content-Type"].split(";")[0]
            except:
                contentType = ""
            isHTML.append(1 if contentType == "text/html" else 0)

        # Get the html number
        Nhtml = np.count_nonzero(isHTML)

        #If no html file returned, exit this program
        if Nhtml==0:
            exit()

        print("==================")
        print("FEEDBACK SUMMARY")
        print("Query: " + QUERY)

        #calculate the precision of html file
        count = 0
        for i in range(len(relevant)):
            if relevant[i] == 1 and isHTML[i] == 1:
                count += 1

        precision = count / np.count_nonzero(isHTML)

        print("Precision: " + str(precision))
        if precision < PRECISION:
            print(f'Still below the desired precision of {PRECISION}')
            print()
            if precision == 0:
                exit()
        else:
            print(f'Desired precision reached, done.')
            exit()

        # Get relebvant HTML results
        relevant_results = [results[x] for x in range(len(results)) if relevant[x] == 1 and isHTML[x] == 1]

        # Make the relevant array only contains the html file information
        relevant = [relevant[x] if (relevant[x] == 1 and isHTML[x] == 1) else 0 for x in range(len(results))]

        # Query new results from google API
        relevant_results, results, QUERY = getNewData(QUERY, API_KEY, ENGINE_ID, results[0:10], relevant, relevant_results, isHTML)

def getNewData(query, api_key, engine_id, results, relevant, relevant_results, isHTML):
    
    # Get new query
    relevant_results, newQuery = getNewQuery(query, results, relevant, relevant_results, isHTML)

    # Query for new results with updated query
    service = build("customsearch", "v1", developerKey=api_key)
    results = service.cse().list(
      q=newQuery,
      cx=engine_id,
    ).execute()

    results = results["items"][0:10]

    return relevant_results, results, newQuery

def getNewQuery(query, results, relevant, relevant_results, isHTML):
    
    # DEAL WITH RELEVANT DOCUMENTS
    # Select only relevant results
    rel = [results[x] for x in range(len(results)) if relevant[x] == 1]
    relevant_results = rel + relevant_results

    # Get inverted index (allWords) and frequencies per document
    allWords, frequencies = makeInvertedIndex(relevant_results, query)

    
    # Compute tf_idf for every term
    tf_idf_relevant = computeTf_idf(relevant_results, allWords, frequencies)

    # DEAL WITH NON_RELEVANT DOCUMENTS
    # Select nonrelevant results
    all_non_relevant_results = [results[x] for x in range(len(results)) if relevant[x] == 0 and isHTML[x]==1]
    
    # Get first non-relevant result for Ide dec-hi algorithm 
    first_non_relevant_result = [all_non_relevant_results[0]]

    # Get inverted index (allWords) and frequencies per document
    allWords_non_relevant, frequencies_non_relevant = makeInvertedIndex(first_non_relevant_result, query) # all_non_relevant_results

    # Compute tf_idf for every term
    tf_idf_first_non_relevant = computeTf_idf(all_non_relevant_results, allWords_non_relevant, frequencies_non_relevant)

    # Pick new term to add to the query using de dec-hi
    # Come up with new query based on results and relevance markings
    newQuery = getAdditionalTerms(query, allWords, tf_idf_relevant, tf_idf_first_non_relevant)

    # Return the newly formed query
    return relevant_results, newQuery

def getSplitWords(words):
    
    # Split words string and remove special characters
    if words is not None:
        words.replace(string.punctuation, ' ')
        punctuation_string = string.punctuation
        for i in punctuation_string:
            words = words.replace(i, ' ')
        words = words.split()

    return words

def getFrequencies(words, query): 
    
    # Get stopwords from professor's file and join with our own stop words
    professorsStopWords = getStopWords('http://www.cs.columbia.edu/~gravano/cs6111/proj1-stop.txt')
    ourStopWords = []
    stopWords = professorsStopWords + ourStopWords
    words = [word.lower() for word in words]    

    # Generate frequency dictionary of words in each file
    word_freq = {}

    # If the link returned page words then make a dictionary of their frequencies
    if words is None:
        return None
    else:
        for word in words:
            # Make word lowercase           
            if word in stopWords and word not in query.split(" "):
                continue
            elif word not in word_freq:
                word_freq[word] = 1
            else:
                word_freq[word] = word_freq[word] + 1

    return word_freq

def getStopWords(link):

    # API call to get all words from file
    res = urllib.request.urlopen(link)

    # Create list of all stop words
    stopWords = []
    for line in res:
        word = line.decode("utf-8")
        stopWords.append(str(word).replace('\n', ''))

    return stopWords

def makeInvertedIndex(relevantResults, query):
    
    allWords = {}
    frequencies = {}

    # Create dictionary of all non stop-words as keys and arrays of documents that they appear in as values.
    # Create dictionary of term frequencies within each document.
    for i in range(0,len(relevantResults)):

        # Take words from both the title and snippet of the relevant documents
        words = relevantResults[i]['title'] + " " + relevantResults[i]['snippet']
        stopWords = getStopWords('http://www.cs.columbia.edu/~gravano/cs6111/proj1-stop.txt')
        stopWords.append("·")
        stopWords.append('•')
        words = getSplitWords(words)

        # Make words all lowercase
        words = [word.lower() for word in words]

        for word in words:
            # Only include non stop-words or words that are in the query in the inverted index
            if word not in stopWords or word in query.split(" "):
                if word not in allWords.keys():
                    allWords[word] = [relevantResults[i]['link']]
                else:
                    if relevantResults[i]['link'] not in allWords[word]:
                        allWords[word].append(relevantResults[i]['link'])

        frequencies[relevantResults[i]['link']] = getFrequencies(words, query)

    return allWords, frequencies

def computeTf_idf(relevantResults, allWords, frequencies):
    
    # Number of relevent documents
    N = len(relevantResults)

    # Compute term frequencies per document
    tf = {}
    for word in allWords.keys():
        wordFreq = {}
        for doc in allWords[word]:
            wordFreq[doc] = frequencies[doc][word]
        tf[word] = wordFreq

    # Compute df for each term
    dfs = {}
    for word in allWords.keys():
        dfs[word] = len(allWords[word])

    # Compute idf for each term
    idfs = {}
    for word in allWords.keys():
        idfs[word] = math.log10(N/dfs[word])

    # Compute tf_idf
    tf_idf = {}
    for doc in relevantResults:
        tf_idf_word = {}
        for word in allWords.keys():
            if doc['link'] in tf[word].keys():
                tf_idf_word[word] = idfs[word] * (1 + math.log10(tf[word][doc['link']]))
        tf_idf[doc['link']] = tf_idf_word

    return tf_idf

def getAdditionalTerms(query, allWords, relevant_tf_idf, non_relevant_tf_idf):
    
    # Vectorize documents using tf_idf values
    doc_vectors = []
    for key in relevant_tf_idf.keys():
        doc_vector = []
        for word in allWords.keys():
            if word in relevant_tf_idf[key].keys():
                doc_vector.append(relevant_tf_idf[key][word])
            else:
                doc_vector.append(0)
        doc_vectors.append(doc_vector)

    non_relevant_doc_vector = []
    for key in non_relevant_tf_idf.keys():
        doc_vector = []
        for word in allWords.keys():
            if word in non_relevant_tf_idf[key].keys():
                doc_vector.append(non_relevant_tf_idf[key][word])
            else:
                doc_vector.append(0)
        non_relevant_doc_vector.append(doc_vector)

    # Add vectors
    added_relevant_vectors = [0 for i in range(len(allWords.keys()))]
    for vector in doc_vectors:
        for i in range(len(allWords.keys())):
            added_relevant_vectors[i] = added_relevant_vectors[i] + vector[i]

    # Subtract non-relevant vector
    resulting_vector = [0 for i in range(len(allWords.keys()))]
    for vector in non_relevant_doc_vector:
        for i in range(len(allWords.keys())):
            resulting_vector[i] = added_relevant_vectors[i] - vector[i]

    # Get tf_idf for query
    query_tf_idf = compute_query_tf_idf(query, allWords, relevant_tf_idf)

    query_vector = []
    for word in allWords.keys():
        if word in query_tf_idf.keys():
            query_vector.append(query_tf_idf[word])
        else:
            query_vector.append(0)

    # Add query_vector to resulting_vector
    for i in range(len(resulting_vector)):
        resulting_vector[i] = resulting_vector[i] + query_vector[i]

    # Get top new word to add to query
    query_words = query.split(" ")
    words = [""]
    word1 = 0
    words_list = list(allWords.keys())
    for n in range(len(resulting_vector)):
        if resulting_vector[n] > word1:
            if words_list[n] not in query_words:
                words[0] = words_list[n]
                word1 = resulting_vector[n]

    query_words.append(words[0])

    # Fucntion to rank words by tf_idf value
    def get_tf_idf(word):
        i = words_list.index(word)
        return resulting_vector[i]
    
    # Rank words in the query by tf_idf value
    query_words.sort(key=get_tf_idf)

    # Combine query_words array to generate the new query string
    newQuery = f"{' '.join(query_words)}"

    return newQuery

def compute_query_tf_idf(query, allWords, relevant_tf_idf):
    
    # Number of documents
    N = len(relevant_tf_idf.keys())
    words = query.split()
    
    # Set frequencies to 1
    tf = {}
    for word in allWords.keys():
        if word in words:
            tf[word] = 1
    
    # Calculate idf
    dfs = {}
    for word in words:
        dfs[word] = len(allWords[word])

    # Compute idf for each term
    idfs = {}
    for word in allWords.keys():
        if word in words:
            idfs[word] = math.log10(N/dfs[word])
        else:
            idfs[word] = 0

    # Compute tf_idf
    tf_idf = {}
    for word in allWords.keys():
        if word in words:
            tf_idf[word] = idfs[word] * (1 + math.log10(tf[word]))
        else:
            tf_idf[word] = 0

    return tf_idf

if __name__ == "__main__":
    main()