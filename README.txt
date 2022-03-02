Team Memebers:
Xiaoyue Chen - xc2551
Jakob Deutsch - jgd2150





------------------------------------------------
Installs & VM Setup: (Steps 1-3 should already have been done. If so, skip them.)
1. sudo apt-get update
2. sudo apt install python3-pip
3. sudo pip3 install --upgrade google-api-python-client
4. pip3 install numpy

------------------------------------------------
How To Execute the Program:
Under the program's root directory, run:
python3 proj1.py <EngineID> <APIkey> <query>

------------------------------------------------
Files Submitted:
pproj1.tar.gz which contains: proj1.py
Transcript.txt
README.txt

------------------------------------------------
Project Summary:
Overview:
    The program gets top ten results returned from Google search engine and then displays them to the users. The user then gives their
    feedback regarding these documents. The 'title' and 'snippet' attributes of the documents which have been labeled as relevant according to 
    the users are then used to build an inverted index for all the relevant words/documents. Next the program uses the information from inverted
    index to calculate the tf_idf values for every one of those words. Next we use the Ide dec-hi algorithm to update the query, which is essentially
    a variation of the Rocchio method with the difference being in the fact that we only incorporate the first non-relevant document into the calculation 
    as opposed to Rocchio which incorporates and subtracts all of the non-relevant tf_idf vectors. Then pick the term with highest tf-idf which does not 
    already appear in the previous search query to add into the new query. We then order the new query words from highest tf_idf value to lowest. Finally, 
    we execute the new query and repeat the process.

Implementation:
    Build the inverted index:
    1. Extract the documents that are relevant based on the feedback from the user.
    2. Use the stop words list to eliminate the words in the inverted index that are not wanted.
    3. Store the inverted index as dictionary: terms are the key and an array of document links are the values.
    4. Calculate the tf-idf based on inverted index.

    Query expansion:
    1. Using Ide dec-hi (reference 1.) to update the query vector. We used this algorithm because it is more efficient than the regular
       Rocchio algorithm because it only takes into account the first non-relevant document as opposed to Rocchio which takes into account all of them.
    2. Pick the term with the highest weight in the resulting vector (after the application of Ide dec-hi algorithm) to add to the query.
    3. Reorder the terms in the new query in descending order according to their weights in the resulting vector.

    Stemming:
    While we believe implementing stemming into our approach would have yielded more accurate/relevant tf_id scores for the words that we were 
    evaluating, we decided against implementing it after one attempt at it. We tried to use the Porter Stemmer, but the rults were inaccurate (at
    using the library we found) and the stemmer ended up stemming words into the wrong form. For example, Louis became Loui. Fo that reason we decided
    against using it, but in the future we understand a well functioning stemmer can be a valuable addition to the algorithm.

Application Flow & Functions Explained:
    main():
        This is the entry point of the application. Here the application takes the user's query along with their credentials
        and makes a query to google's API. Then the user is shown the results 1 by 1 and asked to indicate the relevance of each
        result. The user is then presented with the statistics of the results and their relevance along with the query and API 
        information. If the user's desired precision has been reached the program exits, otherwise the program calls getNewQuery() 
        passing in the results and the indicator of each document's relevance (along with a few other parameters) to generate a new 
        query and retrieve the results of that query to present to the user again. This cycle occurs until the user's desired 
        precision has been reached or if the new query returns 0 results.

    getNewData():
        This function initiates the process of getting results from a new query that has yet to be constructed. The function calls 
        getNewQuery() which performs all the necessary calculations and analysis to provide a reconstructed query. The function 
        provides the original query, api_key and engine_id so that the subsequent methods can eventually make another request to 
        the API with a newly constructed query and return its results.

    getNewQuery():
        This function accepts as inputs the original query as well as all the results of the prior query and their relevance array 
        (along with the previous relevant documents). The function the constructs an inverted index structure for both the relevant
        documents and the first non-relevant document. Then it uses the return values of the calls to makeInvertedIndex() to compute
        the tf_idf values for both the all the relevant and all the non-relevant documents. The function then calls getAdditionalTerms(),
        to retrieve a new query based on the results of its calculations.

    makeInvertedIndex():
        This function creates dictionary of all non stop-words as keys and arrays of documents that they appear in as values. The function 
        also creates dictionary of term frequencies with each document by calling getFrequencies function, providing the words and the query
        (so that even if a query term was a stop word it would be including in the frquencies dictionary).

    computeTf_idf():
        This function calculates the tf-idf weights based on the inverted index and frequencies of words returned by makeInvertedIndex(). It
        goes through the process of calculating the tf (term frequency) dictionary of values for every word that appears in any document provided.
        Then it calculated a dfs dictionary (containing the df values of each word). Next it calculates an idfs dictionary (containing the idf 
        values of each word). Finally, the results of the of the previous operations are used to calculate tf_idf, which is a dictionary with 
        document 'link' attributes as the keys and a dictionary of tf_idf values for each word in the corresponding document as the values.

    getSplitWords():
        This function receives an string of words as a parameter (in our case, a concatenation of words included in a document's 'title' 
        and 'snippet' field). The function then replaces all punctuation with a ' ' and then splits the resulting string into an array of
        words by using string.split() function to split on whitespace. The result of this split is returned to the caller.

    getFrequencies():
        This function produces a dictionary of words as keys and frequencies of each word in the particular words list (representing the words
        of a given document) as values. The function also takes into account stop words, retrieved from getStopWords(), and does not include 
        them in the resulting dictionary unless they are in the query.

    getStopWords():
        This function produces a list of words given a url to a webpage with a single word on each line. In our case, the function retrieved the 
        stop words that were provided to us by the Professor Gravano through a link to a webpage (http://www.cs.columbia.edu/~gravano/cs6111/proj1-stop.txt).

    getAdditionalTerms():
        Vectorizing & Adding:
            This function creates vectors for every document from the tf_idf values created in computeTf_idf(), one list of vectors for relevant results and 
            another for non-relevant results. Then, the function does array addition of all the relevent vectors to create a added_relevant_vectors vector.
            Next, it goes a similar process but subtracts the non-relevant vectors from the added_relevant_vectors vector which results in a vector that we
            refer to as the resulting_vector. The function continues by computinf the tf_idf value of the query by calling compute_query_tf_idf() and then
            creates a query_vector from the results. Then, the query_vector is also added to the resulting_vector to compute a finalized resulting_vector.
        
        Word Choice & Ordering:
            Once we have the final resulting_vector we use it to determine which (single) word we should add to the prior query to create the new query. The
            function goes through the resulting_vector and returns the word that corresponds to the highest value in the resulting_vector which does not already
            exist in the query. That word is then added to the list of query_words. The query_words are then ordered in descending order based on their values
            in the resulting_vector. Lastly, the newly formed query is returned to the caller. 

    compute_query_tf_idf():
        This function returns a dictionary of tf_idf values for the words that exist in the query. The steps taken in the function are almost identical to the steps
        taken in the regular computeTf_idf() function as seen above, except it is modified to handle taking in a query as opposed to a list of documents.

------------------------------------------------
NOTES:
1. Handling of Non-HTML Documents: We decided to ignore non-HTML files and calculate precision based on the number of HTML documents received.
2. Packages Used: Numpy - Used for counting non-zeros within an array. We tried to use it for vector calculations, but for some reason it did 
   not work so we opted to perform those calculations iteratively with loops.

------------------------------------------------
Reference:
1. https://digitalscholarship.unlv.edu/cgi/viewcontent.cgi?article=2124&context=thesesdissertations


