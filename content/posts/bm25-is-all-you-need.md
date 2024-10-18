---
date: 2024-09-01
image: /static/images/posts/bm25-is-all-you-need.png
readTime: 10 minutes
tags:
- ai
- technology
---



# BM25 is all you need

It’s never been easier to build a search engine.

Since the emergence of ChatGPT-era language models, vector embeddings have dominated the search discourse. The synergy of the these two technologies gave birth to the answer engine[^1], allowing scrappy startups like Perplexity AI to take on search grandmasters like Google.

Retrieval augmented generation (RAG) has since become one of the most popular use cases for LLMs. Now, new frameworks make it easy for developers to implement a semantic search engine in a few lines of code.

Like LLMs, much of the allure of vector embeddings comes from the fact that they often just work. After indexing a set of documents, semantic search is remarkably good at returning the most relevant documents for a query. Used together, LLMs produce better answers to questions because the retriever is able to inject the right documents into the LLM’s context window.

Yet like many LLM applications, mirages are everywhere — illusions that scaling to production won’t be hard because building a demo was easy.

As it turns out, this is a feature, not a bug. Non-determinism in LLMs suggests that the range of outputs is hard to predict. Until you have enough data to derive this distribution from users, you won’t have a broad enough set of test cases to confirm your solution really works in production. In this regard, vector embeddings aren't much different, coming with their own set of problems that often don't present themselves until scaling.

> <small>...</small>

> <small>*Epistemics: earlier this year, I worked on an [AI-driven search product](https://noometic.com) that helped users discover creative talent with natural language.*</small>

> <small>*We built a graph-based vector retrieval system that integrated with an LLM to help users run nuanced searches. The tech was fairly sophisticated, but we started running into problems as the size of our index grew. Not only did queries take too long to process, but we couldn’t reliably return more than 25 results per query. This meant that despite growing our database, users experienced slower query times and the same limitations on results.*</small> 

> <small>*Dealing with the limitations of vector search algorithms can be tricky. Our users wanted lots of results, fast. We considered solutions ranging from tuning to agentic procedures. But we were a small team. We needed a simple solution that we could get working quickly. That’s when I realized we might be overcomplicating a retrieval problem that had been solved long ago...*</small>

> <small>...</small>

## Vector search and it’s problems 

It’s incredible that vector embeddings work at all. And yet, using them can feel almost like magic. When I first started digging into the math behind them, I found a sort of elegance in their simplicity.

Vector embeddings work by capturing the relationships between words based on their context, allowing us to model similarities between concepts.

Like language models, an embedding model is trained on a large corpus of text. Generally, the main difference between them is that embedding models focus on learning representations of words based on context, while language models aim to generate or predict sequences of text.[^2]

When calculating embeddings, we train the model using the contexts in which a word appears. This process captures semantic relationships based on co-occurrence patterns across the corpus. This process is analogous to using context clues to figure out the meaning of a word.

Modern approaches like Word2Vec and GloVe learn these embeddings through optimization techniques, iterating over many examples to capture nuanced meanings and relationships between words.

You can imagine words and sentences as points in high-dimensional space. Similar concepts cluster together, so "Goku" and "super saiyan" would be neighbors, while "Dumbledore" and “wizard” would be in a different neighborhood entirely. The distance between them is what allows vector embedding-based search engines to grasp the semantics of queries and return relevant documents, even without exact word matches.

While powerful technologies, vector embedding models are not without their limitations. High computational costs, storage requirements, and retrieval latency can hinder performance, especially when scaling to large datasets or real-time applications.

Additionally, vector search methods often use approximation algorithms like K-nearest neighbor (KNN) which rely on top-k retrieval, meaning we specify the number of results to retrieve per query. In pre-built frameworks, top-k is often capped because anything greater starts to result in performance degradations.

For many use cases, especially demos, these limitations don’t reveal themselves. But in production settings, when dealing with high request volumes and a varying distribution of user inputs, they can become major sticking points. Luckily, there are solutions out there. Sometimes, finding them requires a bit of a history lesson.

## Lost baggage

New paradigms often bring in new players. Just as transformers revolutionized NLP, the rise of vector embeddings shifted the landscape of search. These shifts can sometimes result in what looks like collective forgetting—where solutions of the previous era get lost in the noise of the shiny new thing. Bag-of-words approaches to NLP seems like one of these.

However, bag-of-words ignores relationships between words and fails to capture context, making it less effective for tasks that require understanding the meaning or nuances of the text. Modern approaches, such as word embeddings and transformers, addressed these limitations at the cost of greater computation.

While fairly limited compared to transformers, we can still get sophisticated results by building on this approach. TF-IDF (Term Frequency-Inverse Document Frequency) is one example of how bag-of-words can lead to some pretty interesting NLP algorithms.

TF-IDF is an extension of the BoW approach that not only counts word frequency but also weighs words by how unique they are across documents. It assigns more importance to words that appear frequently in a specific document but less frequently in the overall corpus. This helps highlight words that are more distinctive to a given document, rather than common words like "the" or "and" which appear frequently across most documents.[^3]

This approach turns out to be pretty useful because it helps identify the most important or distinguishing terms in a document, making it easier to retrieve relevant information. By balancing term frequency with how rare a word is across the corpus, TF-IDF improves search and retrieval tasks by emphasizing the words that truly matter in a specific context.

TF-IDF alone, despite its computational efficiency, isn’t good enough to replace vector embeddings, but with a few tweaks, it’s can become a surprisingly powerful retriever.

## The Okapi BM25 algorithm

BM25, also known as Okapi BM25, is a ranking function used in information retrieval to estimate the relevance of documents to a given search query. It is part of the Okapi family of ranking functions and is rooted in the probabilistic retrieval framework developed in the 1970s and 1980s by researchers like Stephen E. Robertson and Karen Spärck Jones at the Center for Interactive Systems Research in the Department of Information Science at City University, London.[^4] [^5]

While BM25 shares similarities with TF-IDF—both consider term frequency and inverse document frequency—it originates from a different theoretical foundation. BM25 refines these concepts within a probabilistic model to calculate document relevance more effectively. The algorithm introduces flexibility and nuance by considering not just the frequency of terms but also the length of documents and adjusting for the diminishing returns of term frequency. This means that each additional occurrence of a term contributes less to the relevance score than the previous one, preventing term frequency from disproportionately influencing the ranking.

Here's a simplified version of how it calculates the relevance score for a document[^6]:

<p>$$
\text{score}(D,Q) = \sum \text{IDF}(q_i) \cdot \frac{f(q_i,D) \cdot (k_1 + 1)}{f(q_i,D) + k_1 \cdot (1 - b + b \cdot \frac{|D|}{\text{avgdl}})}
$$</p>

Where:

- **D** is the document
- **Q** is the query
- **qᵢ** is a term in the query
- **f(qᵢ, D)** is the frequency of **qᵢ** in **D**
- **|D|** is the length of the document
- **avgdl** is the average document length

Central to BM25 are two parameters, **k₁** and **b**, which allow for fine-tuning the algorithm to suit specific applications:

- **k₁** controls the saturation of term frequency; it dictates how quickly the impact of term frequency increases and then levels off, reflecting the diminishing returns of repetitive terms.
- **b** manages document length normalization; it adjusts the extent to which document length influences the score, ensuring that longer documents are neither unfairly favored nor penalized.

In essence, BM25 calculates a relevance score by cohesively balancing term frequency, inverse document frequency, and document length. It gives higher weight to rare terms (through IDF), accounts for the diminishing returns of term frequency, and normalizes based on document length. This adaptable approach makes BM25 suitable for a wide range of applications, including large-scale web search engines. Its computational efficiency enables it to process substantial document collections using relatively modest hardware resources compared to more complex algorithms.

## Trade-offs

When you compare vector search and BM25 side-by-side, it's hard to say one is definitively better. They each have trade-offs:

1. BM25 is computationally efficient, but it doesn't understand the semantic meaning of words.
2. Vector search excels at capturing semantics, often performing better for complex document sets and queries where meaning is key.
3. BM25 can rank all documents without imposing a result limit, while vector search typically returns only the top-k results.

For example, in legal document search or e-commerce, where exact keyword matches often matter more than nuanced meaning, BM25 tends to outperform vector search because of its ability to retrieve all relevant documents. On the other hand, for tasks like customer support chatbots or recommendation systems, where understanding the intent behind a query is crucial, vector embeddings might offer superior results.

While BM25 doesn't capture semantic nuances like vector search does, for many applications, especially those dealing with domain-specific content or structured information, the lexical matching provided by BM25 is often sufficient and, in some cases, can even outperform semantic search.

BM25 shines in scenarios where precision and recall are paramount. For instance, in scientific or medical databases where exact terminology is crucial, BM25’s focus on term frequency and document length can deliver more precise results than vector search, which might misinterpret technical terms.

If still you don’t believe me, just ask Perplexity CEO Aravind Srinivas, who recently shared his take on the Lex Friedman podcast[^7]: the biggest search competitor to Google is using BM25.

## But is it really all you need?

The title of this post is intentionally tongue-in-cheek, but the truth is BM25 isn’t always all you need—although it often comes close. Certainly, it’s better to start with BM25 rather than jumping into more sophisticated patterns using vector embeddings. BM25 is a great baseline, so if your vector search can’t outperform it, you should default to using it until you can improve those results. This is much more cost-effective and lower complexity to manage. There is no need to pay for a vector database or worry much about whether you have enough compute to run these algorithms at scale with concurrent users.

But even for Perplexity, BM25 is just a great way to improve their semantic search engine. Instead of just using one or the other, they use a hybrid system that gives them the best of both worlds: fast, instant results from BM25, plus a runtime re-ranker using vector embeddings for better semantic matching.

In a world where we often reach for the newest, shiniest tool, BM25 reminds us of the value of tried-and-true methods. It's computationally efficient, capable of ranking entire document collections, and often surprisingly effective.

Does this mean BM25 is always the answer? Of course not. But it does mean that before you jump into complex vector search implementations, it's worth considering whether BM25 might solve your problem just as well, if not better. Often, it offers the best balance of simplicity, performance, and cost-effectiveness.

Ultimately, the right search solution depends on your specific use case. But don't overlook BM25—sometimes, it really is all you need.

### Notes
[^1]: [What is an answer engine?](https://www.perplexity.ai/page/what-is-an-answer-engine-G7w5zRTmQw604cVDmaPHkw)
[^2]: [What is the difference between embeddings and transformers?](https://www.perplexity.ai/search/what-is-the-difference-between-Tr.H2evOS5qK.7MPKR3bxg)
[^3]: [TF-DF and it's shortcomings](https://www.perplexity.ai/search/what-is-tf-idf-and-what-are-it-GM13VNvWRgauuvvdDa_UcQ)
[^4]: [The OKAPI Information Retrieval System](https://smcse.city.ac.uk/doc/cisr/web/okapi/okapi.html)
[^5]: [History of the Okapi BM25 Algorithm](https://www.perplexity.ai/page/history-of-the-okapi-bm25-algo-ap40DDZKTUWu73bgcZ9FhA)
[^6]: [What is BM25?](https://pub.aimind.so/understanding-the-bm25-ranking-algorithm-19f6d45c6ce)
[^7]: [Perplexity CEO on Lex Fridman Podcast](https://youtu.be/e-gwvmhyU7A?si=jcxhNX58t9V_Vl9A&t=6987)