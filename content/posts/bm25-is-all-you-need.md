---
date: 2024-09-01
tags: [ai, technology]
readTime: 10 minutes
---

# BM25 is all you need

It’s never been easier to build a search engine.

When LLMs took off, vector embeddings followed. Now, new frameworks and tools are making it easy for developers to index and search over documents in just a few lines of code. As it turns out, there are benefits to molding language space into coherent semantic clusters. The result of which, for these two technologies, gave birth to the answer engine[^1].

Another reason reason adoption has been smooth is that for many cases, vector embeddings just work. When used to index a set of documents, they are remarkably good at returning the most relevant documents given an input query. Yet like many LLM applications, we can quickly fall for demo mirages: illusions that demos will be easy to scale into production, especially across the range of inputs for your users.

In practice, production is a lot harder than building a demo. This is especially true with the current wave of AI tech. This is a feature, not a bug. The nondeterminism in LLM models suggests that the range of inputs and outputs is hard to predict. Until you have enough data to derive this distribution from users, you won’t have a broad enough set of test cases to confirm your thing really works.

It's proabably good for someone building in AI to consider how “pretty-good-out-of-the-box” solutions can create these kinds of illusions.

## Vector search and it’s problems 

It’s incredible that vector embeddings work at all. And yet using them can feel almost like magic.

Yet, from a mathematical standpoint, they are relatively simple. Vector embeddings work by capturing the relationships between words based on their context, allowing models to understand how similar or different concepts are. Like language models, an embedding model is created from a large corpora of text. Generally, the main difference is that embedding models focus on learning representations of words based on context, while language models aim to generate or predict sequences of text.[^2]

When calculating embeddings, we train the model using the contexts in which a word appears. This process captures semantic relationships based on co-occurrence patterns across the corpus. This is like using math to derive context clues from surrounding words to understanding the meaning of the target word.

Modern approaches like Word2Vec or GloVe learn these embeddings through optimization techniques, iterating over many examples to capture nuanced meanings and relationships between words.

Imagine words and sentences as points in high-dimensional space. Similar concepts cluster together, so "Goku" and "super saiyan" would be neighbors, while "panda" would be in a different neighborhood entirely. This is what allows vector embedding based search engines to grasp the semantics of queries and return relevant documents, even without exact word matches.

Embedding models are powerful technologies, but they are not without their limitations. High computational costs, storage requirements, and retrieval latency can hinder performance, especially when scaling to large datasets or real-time applications. Additionally, vector search methods often rely on top-k retrieval, meaning they only return a fixed number of the most relevant documents, which can be a significant limitation.

For many use cases, especially demos, these limitations don’t reveal themselves. While in production settings, when dealing with high request volumes and a varying distribution of user needs, they can be a huge problem. Luckily, the trad NLP community has a solution.

## Lost baggage

New paradigms often bring in new players, and just as transformers revolutionized NLP, the rise of vector embeddings has shifted the landscape of search. These shifts can sometimes result in what looks like collective forgetting—where solutions of the previous era get lost among new entrants. Bag-of-words approaches to NLP seems like one of them. 

Bag-of-words is a pre-transformer approach to NLP, where text is reduced to a collection of individual words, ignoring order and context. This simplicity allows for fast computation and is useful for text classification or clustering tasks, where the presence or frequency of words can indicate certain patterns. It's like dumping all your words into a bag and counting how often each one appears, which can be used to create a sparse vector representing the text. However, bag-of-words ignores the relationships between words, such as syntax and semantics, and fails to capture context, making it less effective for tasks that require understanding the meaning or nuances of the text. Modern approaches, such as word embeddings and transformers, address these limitations by incorporating word context and meaning into the representations.

While fairly limited compared to transformers, we can still get fairly sophisticated by building on this approach. TF-IDF (Term Frequency-Inverse Document Frequency) is one example of how bag-of-words can get us to some pretty interesting NLP algorithms.

TF-IDF is an extension of the bag-of-words approach that not only counts word frequency but also weighs words by how unique they are across documents. It assigns more importance to words that appear frequently in a specific document but less frequently in the overall corpus. This helps highlight words that are more relevant to a given document, rather than common words like "the" or "and."[^3]

This approach turns out to be pretty useful because it helps identify the most important or distinguishing terms in a document, making it easier to retrieve relevant information. By balancing term frequency with how rare a word is across the corpus, TF-IDF improves search and retrieval tasks by emphasizing the words that truly matter in a specific context.

But most importantly, from TF-IDF we got BM25.

## Okapi

BM25 is a direct descendant of TF-IDF. It's full name is Okapi Best Matching 25 (for version 25), after the experimental retrival systemed developed by the Center for Interactive Systems Research in the Department of Information Science at City Univeristy, London.[^4] It addresses some of its shortcomings by introducing more flexibility and nuance in calculating document relevance. The process is refined by considering not just the frequency of terms but also the length of documents and the diminishing returns of term frequency, allowing for a more balanced scoring system.

An important feature of BM25 is its ability to assign a relevance score to each document, including scores of 0 or effectively no score at all. This allows for potentially high recall by not imposing arbitrary limits on the number of results retrieved. BM25 balances this potential for high recall with its nuanced scoring approach, which considers relevance factors like term frequency and document length. This makes it well-suited for large-scale search applications. Additionally, BM25 is computationally efficient, capable of processing substantial document collections with relatively modest hardware requirements compared to more complex algorithms.

Here's a simplified version of how it calculates the relevance score for a document:

$$
\text{score}(D,Q) = \sum \text{IDF}(q_i) \cdot \frac{f(q_i,D) \cdot (k_1 + 1)}{f(q_i,D) + k_1 \cdot (1 - b + b \cdot \frac{|D|}{\text{avgdl}})}
$$

Where:

- $D$ is the document
- $Q$ is the query
- $q_i$ is a term in the query
- $f(q_i,D)$ is the frequency of $q_i$ in $D$
- $|D|$ is the length of the document
- $\text{avgdl}$ is the average document length
- $k_1$ and $b$ are free parameters

What's happening:

- We calculate the inverse document frequency (IDF) of a term, which gives higher weight to rare terms.
- We multiply this by how often the term appears in the document (its frequency).
- Then we adjust this based on the document's length (so longer documents don’t unfairly dominate).
- Finally, we sum this for all the terms in the query to get the overall score.

Doing this for every document in your corpus allows you to rank them based on their relevance to the query by balancing term frequency, document length, and inverse document frequency in a more nuanced way than basic TF-IDF.[^5]

## Trade-offs

When you compare vector search and BM25 side-by-side, it's hard to say one is definitively better. They each have trade-offs:

1. BM25 is computationally efficient, but it doesn't understand the semantic meaning of words.
2. Vector search excels at capturing semantics, often performing better for complex document sets and queries where meaning is key.
3. BM25 can rank all documents without imposing a result limit, while vector search typically returns only the top-k results.

For example, in legal document search or e-commerce, where exact keyword matches often matter more than nuanced meaning, BM25 tends to outperform vector search because of its ability to retrieve all relevant documents. On the other hand, for tasks like customer support chatbots or recommendation systems, where understanding the intent behind a query is crucial, vector embeddings might offer superior results.

While BM25 doesn't capture semantic nuances like vector search does, for many applications, especially those dealing with domain-specific content or structured information, the lexical matching provided by BM25 is often sufficient and, in some cases, can even outperform semantic search.

BM25 shines in scenarios where precision and recall are paramount. For instance, in scientific or medical databases where exact terminology is crucial, BM25’s focus on term frequency and document length can deliver more precise results than vector search, which might misinterpret technical terms.

If you don’t believe me, just ask Perplexity CEO Aravind Srinivas, who recently shared his take on the Lex Friedman podcast[^6]: the biggest search competitor to Google is using BM25.

On a personal level, I used BM25 for searching my local notes database. It lets me quickly search a large set of notes and return everything related to my query at fast speeds, with quick reindexing. I can use this as a tool for local LLMs to help me write posts like these.

## But is it really all you need?

The title of this essay is a playful nod to the famous 'Attention is All You Need' paper, but the truth is BM25 isn’t always all you need—though it often comes close. Certainly it’s better to start with BM25 rather than jumping into more sophisticated patterns using vector embeddings. BM25 is a great baseline, so if your vector search can’t outperform it, you should default to using it until you can improve those results. This is much more cost effective and lower complexity to manage. There is no need to pay for a vector database or worry much about whether you have enough compute to run these algorithms at scale with concurrent users.

But even for Perplexity, BM25 is just a great way to improve their semantic search engine. Instead of just using one or the other, they use a hybrid system that gives them the best of both worlds: fast, instant results from BM25, plus a runtime re-ranker using vector embeddings for better semantic matching. 

## Final thoughts

In a world where we often reach for the newest, shiniest tool, BM25 reminds us of the value of tried-and-true methods. It's computationally efficient, capable of ranking entire document collections, and often surprisingly effective.

Does this mean BM25 is always the answer? Of course not. But it does mean that before you jump into complex vector search implementations, it's worth considering whether BM25 might solve your problem just as well, if not better. Often, it offers the best balance of simplicity, performance, and cost-effectiveness.

Ultimately, the right search solution depends on your specific use case. But don't overlook BM25 – sometimes, it really is all you need.

### Notes
[^1]: [What is an answer engine?](https://www.perplexity.ai/page/what-is-an-answer-engine-G7w5zRTmQw604cVDmaPHkw)
[^2]: [What is the difference between embeddings and transformers?](https://www.perplexity.ai/search/what-is-the-difference-between-Tr.H2evOS5qK.7MPKR3bxg)
[^3]: [TF-DF and it's shortcomings](https://www.perplexity.ai/search/what-is-tf-idf-and-what-are-it-GM13VNvWRgauuvvdDa_UcQ)
[^4]  [The OKAPI Information Retrieval System](https://smcse.city.ac.uk/doc/cisr/web/okapi/okapi.html)
[^5]: [What is BM25?](https://pub.aimind.so/understanding-the-bm25-ranking-algorithm-19f6d45c6ce)
[^6]: [Perplexity CEO on Lex Friedman Podcast](https://youtu.be/e-gwvmhyU7A?si=jcxhNX58t9V_Vl9A&t=6987)