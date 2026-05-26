---
id: doc-006
source: 06-stanford-news-narratives-hanley-2025.pdf
source_type: pdf
source_sha256: e127320ad8507ffcee16eafea9b168754578a286fadffbd8b373765280d10f31
extraction_method: pymupdf4llm@unknown
extraction_date: 2026-05-26
pages: 33
headings:
  - "**Tracking the Takes and Trajectories of English-Language News Narratives across Trustworthy and Worrisome Websites**"
  - "**Abstract**"
  - "**1 Introduction**"
  - "**2 Related Work**"
  - "**3 Methodology**"
  - "**3.1 News Websites**"
  - "**3.2 Definition of a News Story**"
  - "**3.3 System Architecture**"
  - "**4 Characterizing News Ecosystems**"
  - "**5 Underlying Website Relationships**"
tokens_estimated: 33975
warnings:
  - "ligatures_recovered: pymupdf4llm dropped letters from 2 word(s) with fi/ff/fl glyphs (e.g. 'Ofcial'→'Official', 'fexible'→'flexible'); fixed via the doc2kb ligature-recovery table — no manual action needed"
  - "ligature_residual: 12 suspicious word(s) with f-consonant patterns still present (sample: FBI, FDA, Fda, Gaffney, Pfzer); if these are broken ligatures, extend _LIGATURE_FIXES in scripts/_common.py"
  - "dropped_pictures: 4/24 placeholder(s) were auto-recovered as assets, but 20 still remain over 33 page(s) (0.61/page). Re-extract this PDF by reading the source file directly via the Read tool and overwrite the body with a manual transcription of the remaining figures"
assets: [../assets/doc-006-page03-img1.png, ../assets/doc-006-page09-img1.png, ../assets/doc-006-page09-img2.png]
---
[page 1]

# **Tracking the Takes and Trajectories of English-Language News Narratives across Trustworthy and Worrisome Websites**

Hans W. A. Hanley _Stanford University_

Emily Okabe Zakir Durumeric _Stanford University Stanford University_

## **Abstract**

Understanding how misleading and outright false information enters news ecosystems remains a difficult challenge that requires tracking how narratives spread across thousands of fringe and mainstream news websites. To do this, we introduce a system that utilizes encoder-based large language models and zero-shot stance detection to scalably identify and track news narratives and their attitudes across over 4,000 factually unreliable, mixed-reliability, and factually reliable English-language news websites. Running our system over an 18 month period, we track the spread of 146K news stories. Using network-based interference via the NETINF algorithm, we show that the paths of news narratives and the stances of websites toward particular entities can be used to uncover slanted propaganda networks ( _e.g._ , anti-vaccine and anti-Ukraine) and to identify the most influential websites in spreading these attitudes in the broader news ecosystem. We hope that increased visibility into our distributed news ecosystem can help with the reporting and fact-checking of propaganda and disinformation.

## **1 Introduction**

Misinformation has promoted dangerous fake health cures [16], promoted jingoism and propaganda during wars [84, 109, 121], and incited violence [6, 17]. While there has been significant investigation into how misleading information spreads across social media platforms and fringe websites [80, 81, 127], recent work has emphasized that the vast majority of people do not visit fringe websites or regularly encounter misinformation on social media [10, 101]. Rather, most people consume news through more mainstream platforms like television news [10]. However, systematically tracking how misleading, propagandistic, and outright false information spreads from untrustworthy websites into mainstream media and how fringe sites influence the broader news ecosystem remains a significant technical challenge due to the magnitude and distributed nature of the global news ecosystem [9, 19, 61, 127].

In this work, we introduce and validate a system for scalably identifying and tracking potentially unreliable news narratives across different English-language media ecosystems. Building on past work [3, 62, 92, 145], our proposed approach: (1) collects articles by continually crawling news sites from across media ecosystems; (2) extracts semantic narratives and sites’ stances towards different topics using a fine-tuned version of the e5-base-v2 large language model [138], DP-Means clustering [38], and zero-shot stance detection [8]; and (3) identifies the relationships between news sites and broader ecosystems using the NETINF algorithm [49]. We emphasize that our approach does not make factual assessments of individual stories, which is a deeply nuanced task. Rather, our system allows us to shed light on how stories travel across the distributed news ecosystem.

We analyze the results from our deployed system for an 18 month period during which we collected articles from pre-curated lists of 1,003 factually unreliable news websites ( _e.g._ , twisted.news), 1,012 mixed factuality reliability websites ( _e.g._ , foxnews.com), and 2,061 factually reliable news websites ( _e.g._ , washingtonpost.com) maintained by MediaBias/Fact-Check [33]. Analyzing 146K stories that our system extracted from 29M articles on these news websites, we observe significant crossover in the stories covered by different news ecosystems [136]. We show that reliable and mixedreliability news websites play the largest role in setting the stories and narratives addressed by other websites. However, despite covering similar topics, our stance analysis reveals that each type of website adopts distinctive stances towards shared topics, with reliable news websites generally being left-leaning and pro-Ukraine and unreliable websites being the most right-leaning and anti-Ukraine.

Framing our story clusters as cascades, our system uses NETINF [49] to uncover relationships between news sites and to detect potential networks of coordinating websites that spread particular slanted content and narratives. For example, using this approach we identify a network of rightleaning news websites that ostensibly act as local-news websites all operated by Metric Media, LLC. From the out-

[page 2]

putted results, we further identify the sites most influential in spreading stories to unreliable sites ( _e.g._ , thegatewaypundit.com) and the sites from which both reliable and unreliable news websites most commonly adopt stories ( _e.g._ , dailymail.co.uk and ussanews.com). Additionally, we identify the sites that most effectively promote specific types of information across ecosystems like anti-vaccine misinformation (naturalnews.com, theepochtimes.com, and vaccines.news) and anti-Ukrainian propaganda (rt.com, sputniknews.com, and news-front.info).

Ultimately, our work introduces an end-to-end system for building a near-global perspective of the English-language news ecosystem and explores how tracking how narratives travel within it can help us to understand how misleading information enters mainstream news and to uncover previously unknown relationships between news sites. We hope that our approach can serve as the foundation for further study of how information spreads online. Our code and URL data is available at https://github _._ com/hanshanley/tracking-takes.

## **2 Related Work**

Significant prior work has studied news ecosystems and analyzed how misinformation spreads online. Here, we summarize the prior work that our study builds on:

**Tracking Narratives on News Websites.** Several studies have utilized online document clustering [22, 142] for tracking news stories. For example, Zhang et al. [146] identify potential events by monitoring for the appearance of specific phrases or keywords, cluster identified phrases that may indicate news events, and train a series of classifiers to assign news articles to identified clusters. Similarly, by clustering a collection of short phrases or “memes,” Leskovec et al. find that smaller blogs often play a definitive role in encouraging the adoption of particular language onto mainstream websites [85]. Rodriguez et al. [49, 50] examine the changing relationships between websites during the discussion of news events, finding that connections between websites increase during periods of high activity.

While many studies have analyzed topics using statistical word-association approaches like Latent Dirichlet Allocation (LDA) and Dynamic Topic Models [5,100,147], recent works such as those by Meng et al. [96], Hanley et al. [56, 61], and Grootendorst [52] have used large language models (LLMs) for more granular topic modeling. In line with our work, Nakshatri et al. [104] utilize peak detection and HDBSCAN [93] on news article embeddings to identify the most prominent news events in a stream of news articles. Saravanakumar et al. [119] similarly utilize an external named entity recognition system to embed entity knowledge into a BERT language model to differentiate between news articles about different events. Beyond these quantitative approaches, many prior works have qualitatively investigated the spread

of individual news stories ( _e.g._ , [112, 120, 127]).

Most similar to our work, Hanley et al. [62], using MPNet and DP-Means clustering, track news narratives across a smaller number of fringe websites to determine the role that individual unreliable news websites play in originating and amplifying news narratives. Their work finds that less-popular websites oftentimes play an outsized role in promoting narratives that reverberate across the unreliable news ecosystem.

In contrast to these prior works, our study accounts for the _stance_ towards each topic in order to better differentiate between articles that cover the same topic. Tracking stance enables our work to understand the widespread understanding of individual websites’ ideologically skew, changes in coverage of individual topics, and the detection of websites that coordinate in spreading particular types of propaganda.

**Analyzing the Spread of Misinformation.** While our approach is one of the first to track both topic and valence/stance towards that topic in a programmatic manner, several prior works have focused on the peculiarities, detection, and the spread of misinformation. For example, Ma et al. [88] and Jin et al. [71] utilize recurrent neural networks to analyze and detect the spread of unreliable rumors on social media. Abdali [1] et al., taking a domain-based approach, use website screenshots to assess the credibility of news websites. In addition to analyzing the spread of general misinformation on particular social platforms, other works have further investigated the spread of specific narratives, including those concerning the Syrian White Helmets [127], QAnon [11, 58, 107], the Russo-Ukrainian War [59, 61, 109], and COVID-19 [4, 31, 89]. We note that because work utilizes topic analysis followed by stance detection, our system can be used to quickly identify websites and topics that deserve in-depth investigation of particular types of coverage of individual events.

Building off these studies, several works have analyzed the characteristics of misinformation. Juul and Ugander find that often false information on Twitter spreads faster and wider than factual information [73]. Indeed, Kwon et al. [81], utilizing the distinct temporal differences between reliable information and unreliable rumors, are able to classify these rumors with an _F_ 1-score as high as 0.878. In a different work [80], Kwon et al. analyze the semantic and structural characteristics of rumors on Twitter. In a different vein, Using a learning-torank-based approach and ClaimBuster API, Paudel et al. [108] identify potential claims that should be fact-checked on Twitter [64]. Beyond studying the dynamics of misinformation, Bak et al. [15] have proposed concrete steps to ameliorate the spread of misinformation, including removal and nudges. Finally, Kaiser et al. [74] have studied how borrowing techniques from the security warning landscape might help inform users of potential misinformation.

Unlike the past approaches outlined above, by utilizing fine-tuned encoder-based large language models, our work scalably tracks and identifies unique news stories across thousands of news websites without depending on particular key-

[page 3]

**![page 3, image 1](../assets/doc-006-page03-img1.png)**

**----- Start of picture text -----**<br>
Article Text and Date Extraction<br>Russia<br>News Article invaded...<br>Website<br>Websites Scrapes, 02-24-22 responded ...Ukraine<br>RSS feeds<br>News Article Daily Document Stream Separate Document into Passages<br>Narrative 1<br>Narrative 2 Narrative 3 Narrative 2<br>Update Cluster Keywords<br> Stance with Pointwise Mutual Russia<br> Detect  Information and Extract invaded...<br>Summary Narrative 4<br>Determine Stance of Texts within Update Cluster Centers or Create New Calculate Passage<br>Narrative Clusters with Respect  Cluster based on Semantic Similarity to Embeddings<br>Bias Estimation to Extracted Keywords Current Clusters<br>Pro<br>Neutral<br>Against<br>**----- End of picture text -----**<br>

Figure 1: Our pipeline for identifying, labeling, and extracting the stance of story clusters from the daily publications of news websites.

words or by limiting analysis to a subset of unreliable websites previously fact-checked or curated by experts [62, 127]. By utilizing network analysis combined with stance detection, our work further provides a highly interpretable means of understanding the spread and dynamics of propagandistic, biased, or factually unreliable narratives across multiple types of media ecosystems.

## **3 Methodology**

In this section, we provide an overview of our data collection and approach for extracting and tracking narratives across different types of news websites.

## **3.1 News Websites**

Our study analyzes articles collected from three sets of English-language news websites of varying factual reliability. We specifically track narratives on websites rated by Media-Bias/Fact-Check [33], a media monitoring website founded by Dave M. Van Zandt to assess the factual reliability of individual websites given its widespread use in prior work [14, 62, 103, 139] and its ratings’ high agreement with other organizations like NewsGuard.

**Unreliable News Websites.** We collect news articles from 1,003 websites labeled as having “low” or “very low” factual reporting by Media-Bias/Fact-Check [33]. We extend this list with conspiracy theory-promoting websites identified by Hanley et al. [60]. Our list of _unreliable_ news websites includes pseudo-science sites like vaccine.news, state-propaganda outlets such as rt.com, and partisan websites with low-factuality ratings like the liberal-leaning occupydemocrats.com.

**Mixed-Reliability News Websites.** We collect articles from 1,012 _mixed-reliability_ news websites labeled as having “mixed” factual reporting by Media-Bias/Fact-Check [33]. This list includes websites across the political spectrum, such as foxnews.com, nypost.com, and theguardian.com.

**Reliable News Websites.** We collect articles from 2,061 _reliable_ news websites labeled as having “high”, “very high”, or “mostly factual” reporting by Media-Bias/Fact-Check [33]. The category “mostly factual” is included to capture sources with strong reputations like The Washington Post. This list features websites such as reuters.com and apnews.com.

We lastly note that we utilize the full set of English-language news websites from the lists of Media-Bias/Fact-Check [33] and Hanley et al. [60] that were accessible to us from the beginning of our study.

## **3.2 Definition of a News Story**

Our approach tracks specific news stories and their propagation across websites rather than analyzing broader themes as captured by methods like LDA [7,36,70]. Following previous research [61, 62], we adopt Event Registry’s definition of a _news story_ as “collections of documents that seek to address the same _event_ or _issue_ ” [83, 98]. It is important to note that even if two ideas are related, they may not constitute the same news story. For example, while “Florida Governor Ron DeSantis declares for President” and “Nikki Haley surpasses Ron DeSantis in the polls” are related, they are considered separate news stories in our work.

## **3.3 System Architecture**

Our approach for capturing and tracking news stories builds on the LLM-based narrative tracking methodology introduced by Hanley et al. [62]. However, while Hanley et al.’s method scalably tracks individual topics, their work does not incorporate articles’ attitudes towards a topic. While this was not problematic for their work, which focused on the spread of stories amongst _unreliable_ news websites, the approach cannot track news stories across a broader set of news websites that present stories in dramatically different ways. We expand their method to additionally account for the _stance_ /valence of news articles towards a topic ( _i.e._ , we distinguish between

[page 4]

|||all-mpnet|all-mpnet|e5-base-v2|
|---|---|---|---|---|
|BERT|USE|specious|peft+lora|peft+lora|
|0.464|0.749|0.856|0.860|**0.866**|

Table 1: Model Performance on SemEval STS Benchmark. Our PEFT+LoRA models fine-tuned using unsupervised contrastive loss perform better than prior work [26, 27, 37, 62, 114].

articles that cover vaccines positively vs. negatively).

As shown in Figure 1, our system identifies stories by: (1) scraping articles from news sites, (2) splitting articles into passages of 100 words [62,110], (3) embedding passages with a fine-tuned LLM [138], and (4) clustering news articles using an optimized version of the DP-Means algorithm [38, 72]. To describe clusters that each represent a story, we extract keywords from the resulting cluster using Pointwise Mutual Information (PMI) and performing multi-document summarization with an open source LLM. Building on the clusters, we utilize network inference techniques to identify website relationships and _zero-shot_ stance detection [8, 55] to determine the stance/position of individual passages within each cluster. Finally, based on individual websites’ stances toward their given topics, we perform bias estimation to quantify websites’ biases along various political and non-political axes. We detail each stage below:

**Collecting and Preparing News Articles.** We crawl our set of 4,076 websites daily using the Go Colly library [125] from January 1, 2022 to July 1, 2023. Each day, we collect every site’s homepage, RSS feeds, and linked articles. We collected a total 29.0M articles: 17.9M articles from reliable news sites (median 2,467 articles/site), 8.7M articles from mixed-reliability news sites (median 964 articles/site), and 2.5M articles from unreliable news websites (median 219 articles/site). We will provide to URLs researchers on request.

To prepare our news article data for embedding, we first remove any URLs, emojis, and HTML tags from the text. Then, inline with prior work, after first separating articles into paragraphs by splitting text on (\n) or tab (\t) characters [57], we subsequently divide paragraph into constituent _passages_ with at most 100 words [57, 61, 110]. This enables us to fit passages into the context window of our LLM embedding model. Further, given that articles often address multiple ideas, embedding passages allows us to track the often single idea present within the passage [57, 110]. Our dataset consists of 428M passages. For additional details, see Appendix A.

**Embedding Passages.** Before embedding our articles’ passages, to ensure that our embedding model is attuned to the language of news articles, we tailor our model to our domain of our collected articles using _Parameter Efficient FineTuning_ /PEFT [86] through _Low-Rank Adaption_ /LoRA [69] with an unsupervised contrastive learning step based on SimCSE [47]. Rather than directly fine-tuning the original model’s weights as in Hanley et al. [62], this approach freezes

the originally trained large language model and introduces an additional set of parameters of reduced dimensionality that are then fine-tuned for purposes, allowing for better generalizability [69]. We utilize default LoRA hyperparameters of rank=8 and α=16.[1] See Appendix B and C for additional details. We utilize cosine similarity of embeddings to determine passages’ estimated semantic similarity [28, 47, 52, 110].

We specifically fine-tune and evaluate two public opensource large language models, e5-base-v2 [138] and MPNet [126] using this approach. We benchmark these two fine-tuned models on the SemEval STS-benchmark (Table 1) and find that the approach outperforms prior work as general models for semantic similarity. We use the fine-tuned e5-base-v2 model in this work given its top performance.

**Story Identification.** We base our story-identification algorithm on Dinari et al.’s optimized and parallelizable version of the DP-Means algorithm, a non-parametric version of K- means [38]. We utilize this approach as it is highly scalable (able to cluster our 428M embeddings) unlike other LLMbased approaches [52] while also allowing us to identify stories without _a priori_ knowledge. To further scale the approach, we re-implement DP-Means [38] to use the GPU-enhanced FAISS library [72] to perform the embedding-to-cluster assignments and similarity calculations required by DP-Means. To determine a suitable threshold for clustering two news passages together, after fine-tuning e5-base-v2, we benchmark our model on the English portion SemEval 2022 Task 8 dataset [29]. The SemEval 2022 Task 8 dataset consists of two parallel lists of news articles where each pair is graded on whether they are about the same news story. Our model achieves a max _F_ 1-score of 0.793 on this dataset near a cosine similarity threshold of 0.50, which we use in this work. We provide examples of passage pairs in Appendix F.

From January 1, 2022 to July 1, 2023, clustering all our embeddings required the equivalent of 12 days using an NVIDIA A100 GPU. After clustering, like in other works [62, 85], we filter out clusters where 50% or more of the passages are from only one website ( _e.g._ , website-specific headers or author bios). After this pruning, we identified 146,212 story clusters. We provide 30 cluster examples in Appendix I and evaluate these 30 clusters to ensure that they contain coherent stories using the method outlined by Hanley et al. [62]. We achieve an estimated precision of 99.3% of assigning passages to appropriate story clusters where each passage matches the summary, keywords, and other passages in the cluster.

**Story Summarization and Labeling.** To build humanunderstandable representations of our clusters, we extract keywords using pointwise mutual information (PMI), an information-theoretic for uncovering associations [23], to uncover the words most associated with each story cluster [59]. To make these words more uniform, we lemmatize each word to each cluster before calculating PMI. For details on PMI,

> 1https://huggingface _._ co/docs/peft/task_guides/semantic-similarity-lora

[page 5]

see Appendix D. In addition, we perform multi-document summarization utilizing an instruction fine-tuned version of Llama 3 [39].[2] This enables us to summarize the different perspectives of the passages within a given cluster, while also allowing humans to easily understand a story cluster’s contents. We utilize the following prompt to summarize the contents of each of our clusters: _You work for a news researcher and your job is to summarize articles. Write a single concise collective abstractive summary of the texts, where individual texts are separated by |||||, and return your response as a single summary that covers the key points of the text._

**Website Relationship Inference.** To further understand the relationships between news sites, we analyze how stories spread across websites over time. We consider the set of articles in a cluster as a time cascade based on the date that each article was published, and we use an open source version of NETINF [49] to infer the underlying structure and relationship amongst our set of news websites.[3] Given a set of time cascades ( _e.g.,_ the time steps for when a particular website posts an article within a given story cluster), while assuming that each node in a particular cascade is influenced by exactly one other node, the NETINF algorithm attempts to infer the optimal network to explain the observed posting behavior [49]. Based on each website posting behavior across the different cascades, NETINF estimates the number of times that each website copied information from another as well as the time delay between copies. We provide additional details in Appendix G.

**Stance Detection.** While passages may cover the same story, they often adopt different _stances_ [61,78,99] in addressing the same event. After identifying the stories on our set of news websites, we employ stance detection to understand how different websites address each story. Stance detection methods determine the attitude of an author toward a specific topic or target [20]. Typically, stance detection involves taking a passage _pi_ and a topic or target _ti_ , and outputting the stance _si ∈{Pro, Against, Neutral}_ of the passage towards the target, where the target is a _noun_ or a _noun phrase_ . Given that most stance detection methods heavily rely on the topic or target, with many models struggling to generalize to topics or targets outside their domain, various models have been developed to perform stance detection in _zero-shot_ (where the tested topics or targets are not in the training data) and _few-shot_ (where very few examples of the tested topics or targets are in the training data) settings [8, 87].

To perform this stance detection, we utilize the current stateof-the-art zero-shot TATA model [55], which was trained on the VAST dataset [8]. We note that the size of our dataset of stance pairs precluded us from using popular large language model services like GPT-4 or Claude Sonnet. To enhance this model, we retrained it on both the VAST dataset and news-

> 2https://huggingface _._ co/meta-llama/Meta-Llama-3 _._ 1-8B-Instruct

> 3https://snap _._ stanford _._ edu/netinf/

**==> picture [242 x 146] intentionally omitted <==**

**----- Start of picture text -----**<br>
Reliable (µ=-0.21)<br>Mixed (µ=0.24)<br>Unreliable (µ=0.58)<br>blackpressusa.com<br>gopdailybrief.com<br>freespeech.org<br>wethepeopledaily.com<br>3 2 1 0 1 2 3<br>Estimated Bias (Pro-Democrat -> Pro-Republican)<br>**----- End of picture text -----**<br>

Figure 2: Estimated Partisanship via Bayesian regression of our websites based on their stances to articles’ topics.

specific stance detection NewsMTSC dataset [53]. By training the TATA model using this extended dataset, we achieved state-of-the-art _F_ 1 scores of 0 _._ 781 in the zero-shot setting and 0 _._ 741 in the few-shot setting on the VAST test dataset, and a macro _F_ 1 score of 0 _._ 849 on the NewsMTSC test dataset.

Specifically, rather than performing stance detection on a pre-determined set of topics [51, 78, 82], we leverage our topic and story modeling to conduct stance detection across each story cluster. Once we extract story keywords using PMI, we utilize the Python NLTK library’s Part-of-Speech (POS) tagging function to identify the most distinctive noun keywords [21], capturing the topic addressed in each passage. We further use the NLTK library to filter out common first names ( _e.g._ , Michael, Jessica) from our stance detection algorithm and employ the Python spaCy library [135] to exclude nouns that fall into the following categories: _FAC, LOC, WORK_OF_ART, DATE, TIME, PERCENT, MONEY, QUANTITY, ORDINAL, CARDINAL_ . This approach ensures that passages are not erroneously categorized as _Pro_ or _Against_ particular dates or monetary amounts. To ensure robust measurements of the collective ecosystems’ and websites’ stances toward specific entities, we gather the top 5,000 noun entities from our data and perform stance detection on each passage within each cluster where it appears among the top 10 PMI keywords. Altogether, this process involves running stance detection on 96.3M passage and keyword pairs, requiring the equivalent of 15 days of computation on a NVIDIA A100.

**Interpretable Mapping of Websites’ Biases.** A simplistic approach to understanding a website’s overall bias ( _i.e_ how anti or pro) toward an entity such as “Ukraine” would involve aggregating the percentage of their articles that had pro“Ukraine” and anti-“Ukraine” stances ( _i.e._ , % pro-Ukraine articles _−_ %anti-Ukraine articles). However, this approach could potentially fail given that some websites may not have an abundance of articles focused on Ukraine or may only discuss Ukraine-related entities to obfuscate their bias. As such, taking inspiration from Waller et al. [137] who train Word2Vec models to predict subreddit’s bias, we instead take

[page 6]

|Reliable News|Mixed News|Unreliable News|
|---|---|---|
|Pro CDC|Against Kardashian|Against Pfzer|
|Pro Quantum|Pro Gunnar|Against Vaccine|
|Pro Senate|Pro Alnassar|Against Wuhan|

Table 2: Keywords most associated with each news ecosystem estimated using PMI.

a holistic approach by aggregating each website’s respective stances to their written-about entities and predicting bias via Bayesian regression models.

To estimate websites’ biases toward a subject along a given axis, we first gather a seed set of websites with at least 250 articles[4] discussing the entity and compute their simplistic bias score ( _i.e._ , % pro-entity articles _−_ % anti-entity articles). To make these values more interpretable, we normalize these scores as z-scores ( _i.e._ , mean 0 and variance 1), such that a score of 1.0 can be interpreted as bias in favor of entity one standard deviation above the mean [137]. Following this calculation, we subsequently train a linear Bayesian regression model with _L_ 2 regularization to predict this bias score by utilizing our seed set of websites’ stances to other entities (besides the one in question). Finally, once trained, using the model, we estimate the rest of our websites’ bias scores to the given entity. We adopt a Bayesian model approach as this directly enables us to quantify how individual stances contribute to our prediction of a given website’s bias.

To validate this approach, we mapped our websites to partisanship scores along the US left–right political spectrum (Figure 2) using the keywords “democrat” and “republican,” and a seed set of 105 websites. The partisanship scores from the resulting model had a ρ = 0 _._ 51 Spearman correlation with the partisanship labels (Far-Right, Right, Right-Center, Center, Left-Center, etc.) provided by Media-Bias/Fact-Check. As seen in Table 3, some of the most right-leaning partisan keywords included positive stances towards Dinesh D’Souza, a right-leaning commentator [140], and America, while having a negative stance toward communism. On the Democratic side, the associated stances include being against Texas, conservatives, and the former Republican Congressman George Santos. Similarly, as seen in Figure 3 and matching the partisan labels from Media-Bias/Fact-Check, we broadly observe that our set of reliable websites is left-leaning and the unreliable websites are right-leaning.

## **4 Characterizing News Ecosystems**

Having detailed our methodology, we now characterize the ecosystem of reliable, mixed reliability, and unreliable news websites. Visualized in Figure 3, the most heavily discussed stories among our set of reliable news websites included

> 4This ensures that the margin of error for probabilities is below 0.10 with a 95% confidence interval based on the normal distribution.

|Republican Stances|Coeff.|Std.|
|---|---|---|
|Pro Souza|0.311|0.083|
|Pro America|0.245|0.122|
|Against Communist|0.215|0.102|
|Democratic Stances|Coeff.|Std.|
|Against Santos|-0.323|0.105|
|Against Texas|-0.315|0.075|
|Against Conservative|-0.282|0.098|

Table 3: The stances most associated with U.S. partisanship factions, estimated using Bayseian regression.

the U.S. Republican primary (62,911 articles), business news quarterly revenue (57,453 articles), the U.S. Supreme Court’s decision to overturn federal abortion rights (Roe v. Wade) (38,358 articles), and the Russian invasion of Ukraine (35,135 articles). Looking at the top stories spread by unreliable news websites, we observe many of the same topics, most notably one concerning the U.S. Republican primary (13,393 articles). Indeed, across all shared story clusters (91,390 stories, 62.5%), we observe an average Pearson correlation of 0.501 between the volume of articles from our unreliable and reliable news websites.

Beyond these shared stories, we observe a focus on corruption and government failures (9,094 articles), the U.S. Federal Bureau of Investigation’s (FBI) search of President Donald Trump’s Mar-a-Lago estate (7,678 articles), and the investigation into Hunter Biden’s (U.S. President Joe Biden’s son) laptop (7,509 articles) [105] on unreliable websites. Finally, for our set of mixed-reliability news websites, we observe a heavy focus on sports and pop culture; two of the top five topics focus on the celebrity Kardashian family and one on the footballer Cristiano Ronaldo. Mixed-reliability news volume isalso highly correlated with the volume of stories on reliable (127,106/86.9% shared stories with a ρ = 0 _._ 689 Pearson correlation for the story volumes) and unreliable new websites (91,205/62.4% shared stories with a ρ = 0 _._ 646). We detail each ecosystem’s stories in Appendix K.

Using the stance of each website toward the top 5,000 entities in our dataset, as output by our augmented TATA model, we further characterize the attitudes of our reliable, mixedreliability, and unreliable news websites. To do this, we utilize PMI to determine the non-neutral stances most associated with each ecosystem (we limit this analysis to stances represented in at least 500 articles within each ecosystem to avoid spurious values; see Section D for details). As seen in Table 2, reliable news websites are more pro-CDC (Centers for Disease Control), pro-Quantum, and pro-Senate (than mixed-reliability and unreliable websites). The most distinctive stances of mixed-reliability websites concern pop culture and football (Gunnar is a Norwegian football manager and Al Nassr Football Club is a Saudi-Arabian football team). In contrast, the most distinctive stances among the unreliable news

[page 7]

**==> picture [505 x 284] intentionally omitted <==**

**----- Start of picture text -----**<br>
Elon Musk's acquisition of<br>Twitter for $44 billion has<br>Symptoms of respiratory illnesses such as COVID- been tumultuous, with the<br>19, the flu, and common colds often overlap, including fever, cough, sore throat, runny or stuffy nose, and fatigue, making it difficult to determine the specific infection. Tests are necessary to confirm the diagnosis, as symptoms can be similar to other common illnesses like allergies or respiratory conditions.  The US Supreme Court's overturning of the landmark 1973 Roe v. Wade decision has given individual states the authority to decide whether abortion should be legal within their borders company's stock value plummeting 65% in 2022 and a 44% drop in December. The indictment of Donald Trump comes as his Super PAC spends $1.3 million to attack potential 2024 Republican primary challenger Ron DeSantis.  Meanwhile, DeSantis has been focusing on his own  presidential campaign, taking a confrontational stance against Trump<br>Small businesses are facing  The international community,  The match was characterized by<br>significant challenges due to  particularly the U.S. and Europe, has  Artificial Intelligence  a mix of dominant and even<br>rising inflation, supply chain  pledged unwavering support to  (AI) is a complex topic  halves, with both teams<br>issues, and labor shortages,  Ukraine in upholding its sovereignty  that refers to the  creating chances but struggling<br>making it harder for them to  and territorial integrity, and in  simulation of human  to convert them into goals.<br>succeed.  defending itself against Russian  intelligence in<br>Key companies in the financial  aggression. machines, enabling<br>sector reported significant year-over-year growth in 2022, with some suffering a  Ukrainian President  them to think, act, and learn like humans.<br>significant COVID-19 hit Volodymyr Zelenskyy is facing<br>pressure to protect his troops<br>and maintain public support<br>as Russia gains ground in the<br>Donbas region.<br>**----- End of picture text -----**<br>

Figure 3: The most commonly discussed stories on reliable news websites labeled with their LLM-generated summaries.

websites primarily concern the COVID-19 pandemic, with these websites distinctly opposing vaccines, Pfizer (one of the leading companies that developed a COVID-19 vaccine), and Wuhan, China (the origin of COVID-19) [102].

The stances between different news ecosystems are fairly distinctive. Indeed, by fitting a random forest classifier to 80% (3,260 websites) of the websites’ stance data based on their percentage for and against different entities (using 10% of the websites as validation (408 websites) and 10% as test data), we achieve an accuracy of 85.9% and an AUC of 0.889 in differentiating unreliable news websites from reliable and mixed-reliability websites. This illustrates the ease of differentiating between types of websites by their stances and the ability to predict a potentially unlabeled website’s reliability based on its stance towards popular news stories.

**Bias Case Study: Ukraine and Vaccines.** Beyond the most distinctive stances that each website has, to further understand the underlying attitudes within each ecosystem, we perform a case study on each website ecosystem’s attitudes towards _Ukraine_ and _Vaccines_ —two of the most commonly covered topics in our dataset—using the methodology outlined in Section 3.3. While this analysis specifically addresses Ukraine and vaccines, similar to how we analyzed U.S.-based political partisanship in Section 3.3, this approach can be applied to any popular entity within our dataset. We additionally present analyses for America, China, and Iran in Appendix J.

Fitting our Bayesian regression models with the stances for the remaining 4,999 entities for both Ukraine and vaccines, we map all of our news articles to a bias latent for both

|Pro-Ukraine Stances|Coeff.|Std.|
|---|---|---|
||||
|Pro Zelenskyy<br>Pro Zelensky<br>Against Syria|0.378<br>0.368<br>0.225|0.114<br>0.110<br>0.114|
|Anti-Ukraine Stances|||
||||
|Against Zelenskiy<br>Against Biden<br>Against DHS|-0.500<br>-0.370<br>-0.345|0.111<br>0.103<br>0.119|

Table 4: Stances associated with Ukraine estimated by a Bayesian regression model.

entities in Figure 4. We observe that reliable news websites express higher support for Ukraine and vaccines ( _µvaccine_ =0.32, _µukraine_ =0.36), while unreliable news websites oppose both ( _µvaccine_ =-0.82, _µukraine_ =-0.87), and mixed-reliability websites in the middle ( _µvaccine_ = _−_ 0 _._ 11 _, µukraine_ = 0 _._ 04). This matches the average distribution where 31.9% of unreliable news articles were anti-Ukraine and 23.8% were anti-vaccine; for mixed-reliability websites, 17.8% were anti-Ukraine and 8.5% were anti-vaccine; and for reliable news websites 12.9% of articles were anti-Ukraine and 7.1% were anti-vaccine.

Among our dataset, the news sites most anti-Ukraine include rt.com ( _zukraine_ = -2.36), strategic-culture.org ( _zukraine_ = -2.54), and southfront.org ( _zukraine_ = -2.41)—three websites known for spreading Russian propaganda [106]. Some of the most pro-Ukraine websites include nationaljournal.com ( _zukraine_ = +2.53), a U.S. political policy-oriented website, kyivpost.com ( _zukraine_ = +0.80), a Ukrainian website, as well

[page 8]

**==> picture [502 x 151] intentionally omitted <==**

**----- Start of picture text -----**<br>
zerohedge.com Reliable (µ=0.36) Reliable (µ=0.32)<br>Mixed (µ=0.04) Mixed (µ=-0.11)<br>Unreliable (µ=-0.87) Unreliable (µ=-0.82)<br>patrioticviralnews.com<br>europereloaded.com bipartisanpolicy.org who.int<br>vaccines.news<br>conservativefighters.co hopkinsmedicine.org<br>3 2 1 0 1 2 3 3 2 1 0 1 2 3<br>Estimated Bias (Anti-Ukraine -> Pro-Ukraine) Estimated Bias (Anti-Vaccines -> Pro-Vaccines)<br>**----- End of picture text -----**<br>

Figure 4: Distribution of Ukraine and Vaccine bias across unreliable, mixed-reliability, and reliable news websites estimated by Bayesian regression models.

|Pro-Vaccine Stances|Coeff.|Std.|
|---|---|---|
||||
|Pro Ukraine<br>Pro Trans<br>Pro Healthcare|0.343<br>0.259<br>0.233|0.111<br>0.110<br>0.093|
||||
|Anti-Vaccine Stances|||
||||
|Against COVID<br>Against FDA<br>Against Pfzer-BioNTech|-0.360<br>-0.334<br>-0.333|0.144<br>0.122<br>0.143|

Table 5: Stances associated with vaccines estimated by a Bayesian regression model.

as a selection of NBC and ABC affiliate websites including wbaltv.com ( _zukraine_ = +2.04), wvtm13.com ( _zukraine_ = +2.14), and ketv.com ( _zukraine_ = +2.55) [33]. The most antivaccine websites are vaccineimpact.com ( _zvaccine_ = _−_ 3 _._ 41) and pantsonfirenews.com ( _zvaccine_ = -2.56), both known for spreading misinformation [33]. Conversely, the most provaccine websites include Johns Hopkins ( _zvaccine_ = +1.28) and the World Health Organization ( _zvaccine_ = +0.94).

Examining the stances most associated with each topic latent (Tables 4 and 5), we observe that for Ukraine, this includes being pro the current president of Ukraine, Volodymyr Zelensky [131]. Beyond this entity, we further observe the entities associated with attitudes towards toward Ukraine include other Ukrainian allies ( _e.g._ , Biden and DHS) and countries in the Global South that have battled for attention and aid following the Russian invasion of Ukraine [25]. For the vaccine latent, we observe that website stances most associated with being pro vaccines have to do with being pro-health interventions like healthcare, as well as left-leaning causes like transgender rights and Ukraine [75, 77]. In contrast, we observe that being against vaccines is associated with being against COVID (the cause of the polarization of vaccination [75]), the US Food and Drug Administration (FDA), and Pfizer, one of the companies that developed COVID-19 vaccines [75, 122].

## **5 Underlying Website Relationships**

As observed in Section 4, unreliable, mixed-reliability, and reliable news websites often cover the same stories simultaneously, suggesting an interdependence [127]. To further understand these relationships, we utilize an open source version of the NETINF [49] algorithm to infer the underlying structure and relationships amongst our sets of news websites [85]. Specifically, we first run NETINF using all of the extracted stories within our dataset as time cascades. To determine the appropriate number of iterations to run NETINF algorithm, as in Gomez et al. [49], we utilize the point at which the marginal gain of adding new edges plateaus (90% of the total marginal gain). We find that margin gain reaches a plateau at 37,670 iterations in our dataset.

**Ecosystem Relationships Across All News Stories.** Using the estimated number of copies between websites and the time delay between copies as found by NETINF, we first examine the overall relationships between ecosystems. We find that reliable and mixed-reliability news websites have a large role in introducing stories adopted by the rest of the news ecosystem. As seen in Figure 5a, 60% of the news articles on reliable news websites that were copied/influenced from elsewhere came from other reliable news websites, 43% on mixed-reliability websites came from reliable sites, and 32% on unreliable sites came from reliable sites. Unreliable news websites had significantly less influence, with only 10% of the stories on reliable news websites originating from unreliable news websites (13% for mixed-reliability, 27% for unreliable).

Looking at the set of reliable websites that are the most common sources of copied stories throughout the entire news ecosystem, we see several popular websites including yahoo.com (1.19%), apnews.com (0.73%), abcnews.go.com (0.60%), and cnn.com (0.60%). Despite popular, reliable news websites being common sources, website popularity had only a slight Pearson correlation with their percentage of copies. Using data from the Google Chrome User Report (CrUX)

[page 9]

**![page 9, image 1](../assets/doc-006-page09-img1.png)**

**----- Start of picture text -----**<br>
0.6 8<br>0.7<br>0.6 0.29 0.1 0.5 -1.07 days -0.44 days 7.81 days 6 0.22 0.34 0.44 0.6 1.67 days 2.96 days 8.40 days 6<br>0.4 4 0.5 4<br>0.43 0.44 0.13 -1.87 days -1.51 days 4.64 days 0.12 0.35 0.53 0.4 0.17 days -3.47 days 2.16 days 2<br>0.3 2 0.3 0<br>0.32 0.41 0.27 0.2 2.41 days 0.71 days 2.08 days 0 0.041 0.21 0.75 0.2 -3.40 days -5.35 days -2.09 days 2<br>0.1 4<br>Reliable Mixed Unreliable Reliable Mixed Unreliable Reliable Mixed Unreliable Reliable Mixed Unreliable<br>Copied From Copied from Copied From Copied from<br>(a) Copies for All Stories (b) ∆-Copy Times for All Stories (c) Copies for Unrel. Stories (d) ∆-Copy Times for Unrel. Stories<br>Reliable Reliable Reliable Reliable<br>Mixed Mixed Mixed Mixed<br>Copied To Copied to Copied To Copied to<br>Unreliable Unreliable Unreliable Unreliable<br>**----- End of picture text -----**<br>

Figure 5: The percentage of each ecoystems copied stories that came from each different ecosystem as well as the change in the average time delay between website copy/reposting on the same narrative depending on the combination of news ecosystems.

from October 2022 (which Ruth et al. [116,117] showed to be the most reliable website popularity metric), we find that for unreliable news websites copying from reliable websites, the corresponding reliable websites’ popularity had a correlation of ρ=0.225 with the tendency of unreliable website’s to copy from them (ρ=0.189 for reliable websites copying from reliable websites, ρ=0.311 for mixed-reliability news websites copying from reliable websites).

As seen in Figure 5b, reliable news websites adopt the stories of other reliable news websites more quickly (-1.07 days) compared to the average copy delay (38.4 days). MannWhitney U-tests indicate that these differences are all significant. This compares to a nearly +7.81 day additional delay of reliable news websites picking up the stories from unreliable news websites and -0.44 days from mixed-reliability websites. We find a similar pattern amongst mixed-reliability websites, who adopt stories from reliable news sites (-1.87 days) more quickly than from unreliable news sites (+4.64 days).

**Influence on the Full News Ecosystem.** Having examined the website copies and rates of adoption between the different ecosystems, we next consider which websites are the most influential using the graph of the edge connections between individual news sites. Eigenvector centralities are utilized to determine the relative influence of nodes within graphs [115] and, as such, we utilize this metric to understand websites’ influence. We further compute hub centralities as a metric for websites’ influence in originating stories that spread to other websites (given the directionality of the arrows in our graph, this metric determines the most important websites for supplying content [76]). We show the most influential sites in Table 6 and Figure 6.

|All stories|Hub|Eign.|
|---|---|---|
|yahoo.com|0.149|0.111|
|apnews.com|0.101|0.092|
|dailymail.co.uk|0.097|0.099|
|nypost.com|0.052|0.076|
|independent.co.uk|0.049|0.097|

Table 6: Websites with the largest influence in the underlying influence graph determined by NETINF with all stories considered.

We find that website popularity is correlated with the relative influence of websites within the news ecosystems (when looking at all news sites compared to only reliable sites in the last section). Again using website popularity data from the Google Chrome User Report (CrUX), we find that a website’s eigenvector centrality/influence has a Spearman correlation of ρ = 0.571 (0.396 for hub centrality) with that website’s popularity rank. Despite making up 24.6% of the news websites in our dataset, unreliable news websites do not make up a proportional percentage amongst the most influential news websites. Directly comparing the eigenvector centralities of the reliable news websites to those of the unreliable news websites, we find that reliable news websites are significantly more influential in this ecosystem than unreliable news websites (Cohen’s D = 0.64, p-value _≈_ 0),[5] with mixed reliability websites having comparable influence to reliable ones (no significant difference through Mann Whitney U- test). In terms of origination (hub centralities), we observe a slightly different trend with mixed-reliability websites having slightly more influence in originating stories compared to reliable news websites (Cohen’s D = 0.04, p-value _≈_ 0) and unreliable news websites (Cohen’s D = 0.05, p-value _≈_ 0).

**Stories Spread by Unreliable News Websites.** To identify the websites most inflential in spreading potentially unreliable stories, we run the NETINF algorithm on the set of 6,762 news stories where unreliable news websites posted the plurality of articles about those stories. Again applying the same methodology for identifying the appropriate number of edges to add, the marginal gain plateaus at 16,196 edges. The most popular story amongst these clusters was about government censorship and control (9,094 articles) summarized as: _There is censorship, propaganda, and government control in the US. Cancel culture is a form of censorship, and that governmentfunded media outlets can exercise control over editorial content. The text also warns about the influence of the “Deep State” and far-left communists in US institutions, including the government, media, education, and Big Business._

As expected, given how we narrow our set of stories, as seen in Figure 5c, relative to all news stories, unreliable news

> 5The p-value is computed using the Mann-Whitney U-test.

#### Additional embedded images on page 9

![page 9, image 2 (additional)](../assets/doc-006-page09-img2.png)

![page 9, image 3 (additional)](../assets/doc-006-page09-img1.png)

![page 9, image 4 (additional)](../assets/doc-006-page09-img2.png)

[page 10]

**==> picture [227 x 212] intentionally omitted <==**

**----- Start of picture text -----**<br>
wavy.com<br>washingtonpost.com<br>khon2.com<br>yahoo.com<br>bostonglobe.com<br>cnn.com<br>abcnews.go.com<br>nypost.com mercurynews.comupi.com<br>breitbart.com indianexpress.com<br>newsbreak.com latimes.com<br>abovetopsecret.com headtopics.com wn.comapnews.comcbsnews.combusinessinsider.comreuters.comfoxnews.comthenationalnews.com ibtimes.com<br>thehill.comnecn.comforbes.comsandiegouniontribune.com<br>independent.co.uk<br>usatoday.comnewsweek.comtheguardian.com<br>metro.co.ukthe-sun.com<br>dailystar.co.uk theepochtimes.com<br>dailymail.co.uk<br>thesun.co.uk<br>**----- End of picture text -----**<br>

Figure 6: The most influential websites and their interactions. The size of nodes is proportional to their hub centrality. Reliable news websites are colored blue, mixed-reliability websites are colored grey, and unreliable news websites are colored red.

websites had significantly more influence in originating potentially unreliable content. For example, while for all stories, reliable news websites sourced less than 10% of all of their stories from unreliable news websites, within this specific set of news stories, the figure was 44%. Similarly, for mixedreliability websites, this percentage increased from 13% to 53%. Furthermore, we find that unreliable websites source the majority of their influenced or copied stories from other unreliable news websites, at a rate of 75%. Looking at the set of websites that are the common source for other sites to copy from (Table 7), we find a heavy reliance on dailymail.co.uk, a United Kingdom-based tabloid that Media-Bias/Fact-Check describes as having “low” factual reporting due to “numerous failed fact checks and poor information sourcing.” We also find that ussanews.com, described by Media-Bias/Fact-Check as promoting “entirely false, so-called facts,” was a common source of unreliable news stories.

For this selection of news stories predominately published by unreliable news websites, comparing the copy times of these stories in Figure 5d to those in Figure 5b, we find that reliable news websites are slower to adopt the stories, regardless of from which news ecosystem the story originated. We thus observe a reticence amongst our reliable news websites to report on the news stories primarily spread by unreliable news outlets. However, we find that for mixed-reliability websites, if the news story began amongst other mixed-reliability news outlets, these news outlets are faster to adopt the story (-3.47 days). We further observe that unreliable news websites are the fastest at picking up these news stories compared, picking them up quicker if they initially came from a mixedreliability (-5.35 days) or reliable news website (-3.40 days).

|Reliable|Propor.|
|---|---|
|dailymail.co.uk|0.140|
|abovetopsecret.com|0.039|
|ussanews.com|0.035|
|Mixed||
|dailymail.co.uk|0.062|
|thegatewaypundit.com|0.030|
|ussanews.com|0.027|
|Unreliable||
|naturalnews.com|0.025|
|ussanews.com|0.021|
|theburningplatform.com|0.020|

Table 7: Websites that are the most common source of unreliable news stories for each news ecosystem.

|Predom. Unreliable News Stories|Hub|Eign.|
|---|---|---|
|thegatewaypundit.com|0.129|0.109|
|dailymail.co.uk|0.075|0.125|
|theburningplatform.com|0.060|0.103|

Table 8: Websites with the largest influence in the underlying influence graph for stories predominated spread by unreliable websites.

**Influence in the Unreliable News Ecosystem.** To understand which websites are the most influential in the unreliable news ecosystem, we utilize the eigenvector centrality of each website in the resultant graph created by running NETINF on our set of predominantly unreliable news stories (Table 8). For this ecosystem, we find the popularity of websites is only slightly correlated with eigenvector centrality/influence (ρ= 0.158) and hub centrality (ρ= 0.175). Examining the set of websites that are most prominent within the unreliable news ecosystem (Table 8 and Figure 7), we find that many well-documented websites known for spreading unreliable information are among the most prominent, including theepochtimes.com, dailymail.co.uk, and thegatewaypundit.com [127].

Comparing the eigenvector centralities of the unreliable news websites to those of the authentic news websites, we find that unreliable news websites are more influential within this ecosystem (Cohen’s D = 0.219, p-value _<_ 0 _._ 001), but that unreliable and mixed-reliability websites had comparable influence (no significant difference via the Mann-Whitney U-test). However, most notably, we observe that among the top influencers within this ecosystem are the reliable news website, Yahoo News, and the mixed-reliability Fox News (not shown in the table). Yahoo News primarily serves as a news aggregator, gathering reports from various sources including Fox News, the BBC, and Reuters [143]. Given its role as an aggregator, Yahoo News appears to have a prominent role in disseminating current events that are reported by other outlets.

[page 11]

**![page 11, image 1](../assets/doc-006-page09-img1.png)**

**----- Start of picture text -----**<br>
childrenshealthdefense.org<br>lifesitenews.com noqreport.com<br>abovetopsecret.com<br>freerepublic.com zerohedge.comlewrockwell.com<br>newswars.com<br>thelibertybeacon.com<br>thegatewaypundit.com dailycaller.comwnd.com sgtreport.com theburningplatform.comtheepochtimes.com naturalnews.com<br>ussanews.com<br>welovetrump.com<br>survivethenews.com beforeitsnews.com<br>westernjournal.com<br>foxnews.com<br>redstate.com nypost.com<br>breitbart.com yahoo.com<br>independent.co.uk<br>dailymail.co.uk thesun.co.uk<br>**----- End of picture text -----**<br>

Figure 7: Most influential websites and their interaction for stories that are predominantly spread by unreliable news websites. Nodes sizes are proportional to their hub centralities.

Classified as a mixed-reliability news source, Fox News has been widely commented upon for its role in disseminating hyperpartisan news and misinformation [18, 34, 67].

**Case Study: News Website Coordination.** To identify potential coordination among our websites, we utilize NETINF to discern the relationships between websites involved in stories predominantly published articles spread by unreliable and mixed-reliability news websites (encompassing 40,325 news stories). After running the NETINF algorithm, we further clustered the resulting graph using the Louvain clustering algorithm [35]. Qualitatively, the largest of these clusters comprised 885 relatively mainstream and tabloid websites that report on general news ( _e.g._ , wpxi.com, nbc29.com, wvva.com), with the top stories concerning the Kardashians ( _Keywords: Kourtney, Kardashian, Travis, Khloe, Barker_ ). The second largest cluster consisted of 492 locally-oriented news websites ( _e.g._ , cbs4local.com, idahostatejournal.com), where the top stories focused on immigration ( _Migrant, Border, Patrol, Customs, Smuggling_ ) and the US Constitution ( _Constitution, Oath, Amendment, Constitutional_ ). Finally, the third largest cluster ( _Crore, Yoy, Profit, FY23, Quarter_ ) included 334 international websites ( _e.g._ , sputniknews.com, alarabiya.net), where the top story involved international companies’ profits.

Most notably among our clusters was a set of 338 websites, all with seemingly innocuous names such as southindynews.com and northalaskanews.com, which appeared to be dedicated to local news. Upon further investigation through querying WHOIS, we discovered that each of these websites was registered by the domain registrar Epik, Inc., a popular provider for misinformation and online hate sites [54]. We find that this set of 338 ostensibly local websites is owned and operated by the same entity, Metric Media LLC, which produces algorithmically generated content and promotes rightwing views [144]. Indeed, using our mapping of websites to their respective political partisanship, we found that despite

**==> picture [177 x 147] intentionally omitted <==**

**----- Start of picture text -----**<br>
0.7<br>0.23 0.24 0.53 0.6<br>0.5<br>0.17 0.22 0.61 0.4<br>0.3<br>0.12 0.18 0.7 0.2<br>Reliable Mixed Unreliable<br>Copied From<br>Reliable<br>Mixed<br>Copied To<br>Unreliable<br>**----- End of picture text -----**<br>

Figure 8: Anti-Ukraine Copy Matrix.

these websites rarely writing articles about Republicans or Democrats, they have an average partisanship _µpolitics_ = 0 _._ 22, indicating a slight right-leaning bias, with 88.2% of these websites classified as right-leaning. These websites largely repeat the same text including articles promoting herd immunity from COVID-19 in the United States: _More than 50 percent of US citizens are considered fully vaccinated against COVID-19, nearing the target for “herd immunity” Herd immunity happens when enough of the population has become immune to the virus from the previous infection that it effectively protects those who are not immune._

## **6 Propaganda and Slanted Influence Networks**

As seen in the last section, news sites, regardless of their factual reliability, often report on the same stories, with unreliable news websites in select cases influencing both reliable and mixed-reliability news platforms. Furthermore, while reliable and mixed-reliability news websites predominantly adopt stories from other reliable and mixed-reliability sources (Figure 5a), for topics primarily spread by unreliable news websites, these specious sources often act as the originators of the content (Figure 5c). Within this vein, tracking the spread of unreliable news and propaganda and determining which sources are most effective at seeding these stories into the mainstream media is critical for fact-checkers, journalists, and researchers [62, 127]. To this effect, in this section, we utilize our system to map out and understand the sites originating and spreading specific propaganda and influence campaigns.

To map the influence networks targeting specific entities (either positively or negatively), we gather news articles and the associated sites that exhibit a particular valence towards a given entity ( _e.g._ , anti-vaccine articles). Upon gathering this subset of news articles, we run the NETINF algorithm over these cascades of news article clusters with specific stances. We subsequently perform network analysis using eigenvector centrality and hub centrality, as discussed in the previous section, to identify the most prominent and influential sites promoting a given stance towards a particular subject. By

[page 12]

further examining day-to-day increases in news stories with specific stances and comparing their spread in reliable and unreliable news ecosystems, we further document _new_ individual stories meant to spread particular views or stances.

This programmatic approach can help identify stories that are receiving renewed focus from unreliable news websites and which websites are influential in propagating stances towards entities of interest in a particularly damaging manner, thereby facilitating the identification and mitigation of misinformation [62, 113, 118, 141]. To illustrate, we perform this analysis for anti-vaccine and anti-Ukraine news stories.

|Anti-Ukraine|Hub|Eign.|
|---|---|---|
|rt.com|0.155|0.210|
|sputniknews.com|0.073|0.129|
|news-front.info|0.054|0.163|
|Anti-Vaccine|||
|naturalnews.com|0.141|0.179|
|theepochtimes.com|0.086|0.196|
|vaccines.news|0.049|0.170|

Table 9: Websites with the largest influence in the underlying influence graph of anti-vaccine and anti-Ukraine news.

**Anti-Ukraine Messaging.** As seen in Figure 9 and Table 9, the most prominent anti-Ukrainian news websites during our study included well-known Russian propaganda websites such as Russia Today (RT), Sputnik News, and NewsFront [106]. Beyond known Russian propaganda sites, we also find that antiwar.com, described as a “libertarian noninterventionist website” [33], is one of the most prominent websites in spreading anti-Ukrainian content. Altogether, as seen in Figure 8, unreliable news websites largely supply the majority of the stories used across the entire news ecosystem, with reliable websites copying 53% of anti-Ukrainian stories from unreliable outlets, mixed-reliability websites copying 61%, and unreliable sites 70%.

The most common story pushed in this ecosystem of websites concerned justifications for Russia’s invasion of Ukraine, with one Russia Today article writing [132]: _Moscow attacked the neighboring state in late February, following Ukraine’s failure to implement the terms of the Minsk agreements signed in 2014, and Russia’s eventual recognition of the Donbass republics of Donetsk and Lugansk_ . Further, the anti-Ukrainian news story that received the largest increase in relative popularity among our unreliable news websites in the last week of our study (June 25 to July 1, 2023) featured a series of articles with the keywords _Ukraine, MacGregor, Douglas, Colonel, Zelensky_ , showing a ratio of 9 articles in the unreliable news ecosystem for every 1 article in the reliable news ecosystem. This story, which predominantly spread within the unreliable news ecosystem, concerned an interview with retired US Colonel Douglas MacGregor suggesting that the war between Ukraine and Russia was unwinnable and that Ukrainian

**==> picture [234 x 146] intentionally omitted <==**

**----- Start of picture text -----**<br>
theduran.com<br>telesurenglish.net<br>news-front.info<br>veteranstoday.com themoscowtimes.com<br>nationandstate.com zerohedge.com<br>sott.net hotair.com theconservativetreehouse.cominvestmentwatchblog.com<br>theautomaticearth.com<br>defenddemocracy.press naturalnews.com freerepublic.com<br>moonofalabama.org independentsentinel.com<br>conservapedia.com thegatewaypundit.com<br>abovetopsecret.com asiatimes.com southfront.orgbeforeitsnews.com<br>strategic-culture.org<br>theburningplatform.com biggovernment.news<br>sputniknews.com tass.com lewrockwell.comantiwar.com<br>ussanews.com<br>rt.com<br>**----- End of picture text -----**<br>

Figure 9: Anti-Ukraine Influence Network determined by the NETINF algorithm. The nodes’ sizes are proportional to their hub centralities.

President Zelensky was a puppet of Western powers: _“The war is really over for the Ukrainians. I don’t see anything heroic about the man. And I think the most heroic thing he can do right now is to come to terms with reality," retired Army Colonel Douglas MacGregor told Fox Business News. "I think Zelensky is a puppet, and he is putting huge numbers of his own population in unnecessary risk," he said._ The website that spread this story the most was paulcraigroberts.org ( _zukraine_ =-3.59, 3 articles).

Beyond the set of unreliable news websites spreading antiUkrainian messaging, we further observe several international news websites including asiatimes.com ( _zukraine_ =-1.13), themoscowtimes.com ( _zukraine_ =-0.67), and the right-leaning website hotair.com ( _zukraine_ =-1.21) as purveyors of influential anti-Ukrainian content in this ecosystem. Based on the inwardweighted edges, the most influenced mainstream news website in this ecosystem was haaretz.com, an Israeli outlet ( _zukraine_ =+0.002 for Ukraine bias), and the most influenced mixedreliability news website was salon.com ( _zukraine_ = -0.056), a US-based left-leaning news outlet. We thus observe that even relatively neutral and pro-Ukrainian websites can be potentially influenced by anti-Ukrainian news articles.

**Anti-Vaccine Messaging.** As seen in Figure 11 and Table 9, the largest source of anti-vaccine stories was naturalnews.com, while the most influential anti-vaccine website was theepochtimes.com, both known for spreading anti-vaccine misinformation [33, 111]. As with anti-Ukraine stories, we observe that each website category predominantly sourced their content from unreliable news websites: 51% for reliable news websites, 66% for mixed-reliability news websites, and 81% for unreliable news websites. In addition to the theepochtimes.com and naturalnews.com, we find that childrenshealthdefense.org, a website associated with former presidential candidate Robert F. Kennedy Jr., had a major influence on spreading anti-vaccine content, including one article sug-

[page 13]

**![page 13, image 1](../assets/doc-006-page09-img1.png)**

**----- Start of picture text -----**<br>
abovetopsecret.com<br>theautomaticearth.com naturalnews.com<br>thelibertybeacon.com<br>newswars.com<br>beforeitsnews.com<br>sgtreport.com lewrockwell.com vaccineimpact.com<br>expose-news.com<br>childrenshealthdefense.org<br>australiannationalreview.com<br>lifesitenews.com<br>survivethenews.com<br>theburningplatform.com<br>vaccines.news theepochtimes.com<br>pandemic.news health.news<br>**----- End of picture text -----**<br>

Figure 10: Anti-Vaccine Influence Network determined by NETINF. The nodes’ sizes are proportional to their hub centralities.

**==> picture [178 x 146] intentionally omitted <==**

**----- Start of picture text -----**<br>
0.8<br>0.27 0.22 0.51 0.7<br>0.6<br>0.5<br>0.11 0.23 0.66 0.4<br>0.3<br>0.2<br>0.031 0.16 0.81<br>0.1<br>Reliable Mixed Unreliable<br>Copied From<br>Reliable<br>Mixed<br>Copied To<br>Unreliable<br>**----- End of picture text -----**<br>

Figure 11: Anti-Vaccine Copy Matrix

gesting that a vaccine was not as safe as the US Food and Drug Administration claimed [30].

The most prominent-anti-vaccine story in terms of article volume raised concerns about children receiving COVID-19 vaccines, as highlighted by childrenshealthdefense.org [97]: _Pfizer, at the urging of federal health officials, is hustling to get infants and toddlers injected with experimental COVID vaccines_ . The story that saw the largest relative increase in news articles (14 articles in the unreliable news ecosystem for every 1 in the reliable news ecosystem) was one with the keywords _Pfizer, Batch, Danish, Bnt162b2, Adverse_ . This story concerned Danish scientists ostensibly discovering that batches of Pfizer vaccines were actually placebos: _The Danish scientists uncovered “compelling evidence” that a significant percentage of the batches distributed in the EU likely consisted of “placebos and non-placebos,” prompting the researchers to call for further investigation._ . The top sites that spread this narrative were sgtreport.com ( _zvaccine_ =-1.31 for vaccine-bias), theautomaticearth.com ( _zvaccine_ =-1.08), and theburningplatform.com ( _zvaccine_ =-1.86) with two articles each.

We find that the reliable news website most influenced (by the weighted in-degree within the resulting NETINF graph) was sciencebasedmedicine.org ( _zvaccine_ = +0.06), which frequently reports on and quotes anti-vaccine information [94], detected by our system. Additionally, the most influenced mixed-reliability website (besides theepochtimes.com) was thelibertyloft.com ( _zvaccine_ =-0.81), a right-leaning website that Media-Bias/Fact-Check has identified as spreading COVID-19 related misinformation [33].

## **7 Limitations and Future Work**

Our work shows the promise of mapping the global trajectories of news stories and the takes of news sites towards specific entities. However, we the emphasize the complexity of the global news ecosystem and the considerable future work that remains to understand how information travels online. Below, we discuss the limitations of our work and potential future research directions.

**English-Language Websites.** Our work is limited to English-language news articles and focuses predominantly on US, UK, and Australian websites. As a result, our analysis of the spread of particular stories is limited largely to the English speaking world and could miss other sources of news ( _i.e._ , a Russian-language website for example may be more influential in spreading pro-Russian propaganda than the websites in our dataset). This restriction is largely due to our use of PMI for identifying keywords for stance detection amongst our story clusters, which does not directly work in a multilingual setting. Similarly, we currently lack highly accurate multilingual topic-agnostic stance-detection models [55, 63]. We encourage future work to consider how to semantically map both news topics and stances towards them in multilingual settings, as well as to consider how to source news content from websites in additional languages.

**Automated Fact-Checking of Narratives.** As previously noted, we do not fact check individual news stories, which we argue is a journalistic task beyond the scope of our automated approach. While our system can be utilized to uncover networks of websites pushing potentially unreliable news narratives allowing journalists to prioritize which stories need to be fact-checked by their relative spread, these stories still require human investigation to determine their veracity. However, we note that for stories that have already fact-checked on reputable websites, it may be possible to incorporate the approaches of Hanley et al. [62], Zhou et al. [148], and others to automatically label particular stories. Hanley et al.’s approach involves gathering fact-checks from reputable sources and using a DeBERTa-based model [65] to identify unreliable news stories that directly contradict these fact-checks [62]. In a similar fashion, Zhou et al.’s [148] approach involves using a LLM agent and Google Search to identify which unreliable news stories contradict fact-checks.

[page 14]

**Ephemeral Unreliable News Websites.** Factually unreliable news tend to be ephemeral [32, 58, 68, 101], often only being active long enough to spread misinformation to other platforms before shutting down themselves. As such, finding news sites as soon as they come online is critical long term. We note that while our current system relies on previously curated lists of websites, it can easily incorporate new websites as they appear ( _e.g._ , using the methods outlined by Hounsel et al. [68] for identifying new unreliable news websites based on their domain registration and network infrastructure characteristics). This inclusion would enable our system to surface potentially unreliable news stories that have not spread onto more popular websites. It would also potentially enable uncovering malicious Doppelgänger sites that masquerade as ordinary local websites but that actually spread propaganda as soon as they come online [46, 90, 134] similar to past work that has detected phishing and malware domains [12, 13].

facilitating the tracking of propaganda ( _e.g._ , anti-Ukraine) or misinformation ( _e.g._ , anti-vaccine) within the news ecosystem. This method also aids in identifying which otherwise reliable news sources may be influenced by disinformation and propaganda campaigns. Our approach, which considers the context of authentic and mainstream websites, provides a valuable tool for identifying dubious networks of websites spreading particular types of slanted information, which we argue can assist fact-checkers, journalists, and researchers in better understanding potential online misinformation.

We hope that our work encourages further quantitative analysis of the distributed news ecosystem, particular as social media platforms become more opaque to researchers. Prior security research has uncovered weaknesses and attacks through large-scale analysis ( _e.g._ , [2, 40, 42, 66, 95, 128–130]), and we argue that there is significant potential for future work within the security community on understanding attacks against and strengthening the resilience of the news ecosystem.

## **8 Discussion and Conclusion**

## **Acknowledgments**

In this work, we investigated the spread and stance of news stories across 4,076 news websites from January 1, 2022, to July 1, 2023. Our approach, which advances previous methodologies for understanding news flows by incorporating stance into how we track semantic narratives, allows us to track stories across a mix of reliable, mixed-reliability, and unreliable news websites. (Neglecting stance in understanding the spread of narratives, while helpful for examining a singular ecosystem [62, 127], would likely led to misrepresentations of the interactions between different types of websites.)

This work was supported in part by the NSF Graduate Fellowship DGE-1656518, a Meta Ph.D. Fellowship, and a Sloan Research Fellowship. Any opinions, findings, and conclusions or recommendations expressed in this paper are those of the authors and do not necessarily reflect the views of the National Science Foundation or other funding agencies.

Our work demonstrates the key role that reliable news platforms play in dictating the stories covered by the entire news ecosystem. These popular and largely factual websites maintain the largest degree of influence on the broader news ecosystem (Figure 6) and are the source of much content on mixed-reliability and unreliable websites (Figure 5). To understand which stories unreliable websites will spin or contort, researchers should consider reliable outlets as agendasetters [24, 45, 91]. However, we simultaneously highlight that while a minimum of 62.4% of stories are shared between different types of news websites (Section 4), different ecosystems often have distinctive attitudes towards stories. For example, using our analysis, inline with prior work [44, 48], we show that current lists of unreliable websites, among other biases, tend to be more conservative and have distinctive biases against COVID-19 vaccines and Pfizer (Table 2), informing which larger topics may particularly need additional fact-checking. We also find that biased coverage of particular entities ( _e.g._ , Ukraine, or vaccines) that otherwise reliable news websites produce are often sourced from unreliable news sites.

Finally, our work demonstrates how, by analyzing the stance of articles towards specific topics, we can uncover and understand influence networks directed at specific entities,

[page 15]

## **Ethical Considerations**

Trustworthy news media is fundamental to a democratic society. Previously, false information has incited real-world violence and had major consequences on public health and elections. Disinformation and propaganda are _attacks_ , and it behooves the security community to understand how these attacks are conducted and how to build better defenses against them. Advances in this space help both citizens and news outlets themselves, who regularly fact-check articles. At the same time, like all active measurements, web crawling and programmatic analysis of online content have potential ethical ramifications that we must carefully consider.

Our work collects only publicly available news content in line with prior work ( _e.g._ , [60, 123, 124]). We follow best practices when scraping websites by slowly collecting content over time to reduce load. Our scraping also includes built-in safety mechanisms to prevent making requests more often than once every 10 seconds. We never attempt to access any privileged or private data but rather focus on public stories that are linked from news platforms’ public homepages.

We also adhere to the best practices set forth for conducting active Internet measurements [2, 41, 43]. The servers we use for collecting content are identified as part of a research study through WHOIS, reverse DNS, and informational websites that indicate how to reach the researchers. Our IT and security teams are also informed about how to route any questions, requests, or complaints to our team. We received no requests to opt out of our data collection during our study.

Our study does not generate any new content or redistribute existing content. Instead, we analyze how context spreads. We emphasize that while we utilize labels of individual websites as _unreliable_ or _mixed-reliability_ from Media-Bias/FactCheck [33] and on existing previously-curated lists, this does not necessarily mean that every news story spread by these websites is misinformation. Many unreliable news websites report factual information [127], and at times, otherwise reliable websites may mistakenly report incorrect information. We only label stories that have been previously and individually expertly labeled as _misinformation_ .

## **Open Science**

We are committed to sharing our data with other researchers at academic or non-profit institutions seeking to conduct future work or re-implement our approach. We will publicly release the weights and the code for the models used in this study. Additionally, we will supply the URLs of crawled news stories used in this study upon request.

[page 16]

## **References**

- [1] Sara Abdali, Rutuja Gurav, Siddharth Menon, Daniel Fonseca, Negin Entezari, Neil Shah, and Evangelos E Papalexakis. Identifying misinformation from website screenshots. In _International AAAI Conference on Web and Social Media_ , 2021.

- [2] Gunes Acar, Christian Eubank, Steven Englehardt, Marc Juarez, Arvind Narayanan, and Claudia Diaz. The web never forgets: Persistent tracking mechanisms in the wild. In _ACM SIGSAC Conference on Computer and Communications Security_ , 2014.

- [3] Sadia Afroz, Aylin Caliskan Islam, Ariel Stolerman, Rachel Greenstadt, and Damon McCoy. Doppelgänger finder: Taking stylometry to the underground. In _IEEE Symposium on Security and Privacy_ , 2014.

- [4] Hamidreza Aghababaeian, Lara Hamdanieh, and Abbas Ostadtaghizadeh. Alcohol intake in an attempt to fight covid-19: A medical myth in iran. _Alcohol_ , 88:29–32, 2020.

- [5] Rania Albalawi, Tet Hin Yeap, and Morad Benyoucef. Using topic modeling methods for short-text data: A comparative analysis. _Frontiers in artificial intelligence_ , 3:42, 2020.

- [6] Maxwell Aliapoulios, Antonis Papasavva, Cameron Ballard, Emiliano De Cristofaro, Gianluca Stringhini, Savvas Zannettou, and Jeremy Blackburn. The gospel according to Q: Understanding the QAnon conspiracy from the perspective of canonical information. In _International AAAI Conference on Web and Social Media_ , 2022.

- [7] James Allan. Detection as multi-topic tracking. _Information Retrieval_ , 5(2-3):139–157, 2002.

- [8] Emily Allaway and Kathleen McKeown. Zero-Shot Stance Detection: A Dataset and Model using Generalized Topic Representations. In _Empirical Methods in Natural Language Processing_ , 2020.

- [9] Hunt Allcott and Matthew Gentzkow. Social media and fake news in the 2016 election. _Journal of economic perspectives_ , 31(2), 2017.

- [10] Jennifer Allen, Baird Howland, Markus Mobius, David Rothschild, and Duncan J Watts. Evaluating the fake news problem at the scale of the information ecosystem. _Science advances_ , 6(14), 2020.

- [11] Amarnath Amarasingam and Marc-André Argentino. The qanon conspiracy theory: A security threat in the making. _CTC Sentinel_ , 13(7):37–44, 2020.

- [12] Manos Antonakakis, Roberto Perdisci, David Dagon, Wenke Lee, and Nick Feamster. Building a dynamic reputation system for DNS. In _USENIX Security Symposium_ , 2010.

- [13] Manos Antonakakis, Roberto Perdisci, Wenke Lee, Nikolaos Vasiloglou II, and David Dagon. Detecting malware domains at the upper DNS hierarchy. In _USENIX Security Symposium_ , 2011.

- [14] Mahmoudreza Babaei, Juhi Kulshrestha, Abhijnan Chakraborty, Elissa M Redmiles, Meeyoung Cha, and Krishna P Gummadi. Analyzing biases in perception of truth in news stories and their implications for fact checking. _IEEE Transactions on Computational Social Systems_ , 9(3):839–850, 2021.

- [15] Joseph B Bak-Coleman, Ian Kennedy, Morgan Wack, Andrew Beers, Joseph S Schafer, Emma S Spiro, Kate Starbird, and Jevin D West. Combining interventions to reduce the spread of viral misinformation. _Nature Human Behaviour_ , 6(10):1372–1380, 2022.

- [16] Philip Ball and Amy Maxmen. The epic battle against coronavirus misinformation and conspiracy theories. _Nature_ , 2020.

- [17] Shakuntala Banaji, Ramnath Bhat, Anushi Agarwal, Nihal Passanha, and Mukti Sadhana Pravin. Whatsapp vigilantes: An exploration of citizen reception and circulation of whatsapp misinformation linked to mob violence in India. 2019.

- [18] AJ Bauer, Anthony Nadler, and Jacob L Nelson. What is fox news? partisan journalism, misinformation, and the problem of classification. _Electronic News_ , 16(1):18–29, 2022.

- [19] Priscila Biancovilli, Lilla Makszin, and Claudia Jurberg. Misinformation on social networks during the novel coronavirus pandemic: a quali-quantitative case study of Brazil. _BMC Public Health_ , 21(1):1–10, 2021.

- [20] Douglas Biber and Edward Finegan. Adverbial stance types in english. _Discourse processes_ , 11(1), 1988.

- [21] Steven Bird, Ewan Klein, and Edward Loper. _Natural language processing with Python: analyzing text with the natural language toolkit_ . 2009.

- [22] David M Blei, Thomas L Griffiths, and Michael I Jordan. The nested chinese restaurant process and bayesian nonparametric inference of topic hierarchies. _Journal of the ACM_ , 2010.

- [23] Gerlof Bouma. Normalized (pointwise) mutual information in collocation extraction. _GSCL_ , 2009.

[page 17]

- [24] George R Boynton and Glenn W Richardson Jr. Agenda setting in the twenty-first century. _New Media & Society_ , 18(9):1916–1934, 2016.

- [25] Malte Brosig and Raj Verma. The war in ukraine, the global south and the evolving global order. _Global Policy_ , 2024.

- [26] Daniel Cer, Mona Diab, Eneko Agirre, Iñigo LopezGazpio, and Lucia Specia. Semeval-2017 task 1: Semantic textual similarity multilingual and crosslingual focused evaluation. In _11th International Workshop on Semantic Evaluation_ , 2017.

- [27] Daniel Cer, Yinfei Yang, Sheng-yi Kong, Nan Hua, Nicole Limtiaco, Rhomni St John, Noah Constant, Mario Guajardo-Cespedes, Steve Yuan, Chris Tar, et al. Universal sentence encoder for English. In _Conference on Empirical Methods in Natural Language Processing: System Demonstrations_ , 2018.

- [28] Dhivya Chandrasekaran and Vijay Mago. Evolution of semantic similarity—a survey. _ACM Computing Surveys (CSUR)_ , 54(2):1–37, 2021.

- [29] Xi Chen, Ali Zeynali, Chico Camargo, Fabian Flöck, Devin Gaffney, Przemyslaw Grabowicz, Scott Hale, David Jurgens, and Mattia Samory. Semeval-2022 task 8: Multilingual news article similarity. In _16th International Workshop on Semantic Evaluation_ , 2022.

- [30] Julie Comber. Fda authorizes[´] traditional´novavax covid vaccine, but critics question safety claims. https://web _._ archive _._ org/web/20220713202551/https: //childrenshealthdefense _._ org/defender/fda-authorizetraditional-novavax-covid-vaccine-safety-claims/, 7 2022.

- [31] Jose Yunam Cuan-Baltazar, Maria José Muñoz-Perez, Carolina Robledo-Vega, Maria Fernanda Pérez-Zepeda, and Elena Soto-Vega. Misinformation of covid-19 on the internet: infodemiology study. _JMIR public health and surveillance_ , 6(2):e18444, 2020.

- [32] Ross Dahlke, Deepak Kumar, Zakir Durumeric, and Jeffrey T Hancock. Quantifying the systematic bias in the accessibility and inaccessibility of web scraping content from url-logged web-browsing digital trace data. _Social Science Computer Review_ .

- [33] Dave Van Zandt. Media bias/fact check. https: //mediabiasfactcheck _._ com/, 2023.

- [34] Randall Chase David Bauder and Geoff Mulvihill. Fox, dominion reach 787m settlement over election claims. https://web _._ archive _._ org/ web/20230418103714/https://apnews _._ com/article/ fox-news-dominion-lawsuit-trial-trump-20200ac71f75acfacc52ea80b3e747fb0afe, 4 2023.

- [35] Pasquale De Meo, Emilio Ferrara, Giacomo Fiumara, and Alessandro Provetti. Generalized louvain method for community detection in large networks. In _International conference on intelligent systems design and applications_ , 2011.

- [36] Peter Devine and Kelly Blincoe. Unsupervised extreme multi label classification of stack overflow posts. In _1st International Workshop on Natural Language-based Software Engineering_ , 2022.

- [37] Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova. Bert: Pre-training of deep bidirectional transformers for language understanding. In _North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1_ , 2019.

- [38] Or Dinari and Oren Freifeld. Revisiting dp-means: fast scalable algorithms via parallelism and delayed cluster creation. In _Uncertainty in Artificial Intelligence_ , 2022.

- [39] Abhimanyu Dubey, Abhinav Jauhri, Abhinav Pandey, Abhishek Kadian, Ahmad Al-Dahle, Aiesha Letman, Akhil Mathur, Alan Schelten, Amy Yang, Angela Fan, et al. The llama 3 herd of models. _arXiv preprint arXiv:2407.21783_ , 2024.

- [40] Zakir Durumeric, David Adrian, Ariana Mirian, James Kasten, Elie Bursztein, Nicolas Lidzborski, Kurt Thomas, Vijay Eranti, Michael Bailey, and J Alex Halderman. Neither snow nor rain nor mitm... an empirical analysis of email delivery security. In _ACM Internet Measurement Conference_ , 2015.

- [41] Zakir Durumeric, David Adrian, Phillip Stephens, Eric Wustrow, and J Alex Halderman. Ten years of zmap. In _ACM Internet Measurement Conference_ , 2024.

- [42] Zakir Durumeric, James Kasten, Michael Bailey, and J Alex Halderman. Analysis of the https certificate ecosystem. In _ACM Internet measurement conference_ , 2013.

- [43] Zakir Durumeric, Eric Wustrow, and J Alex Halderman. ZMap: fast internet-wide scanning and its security applications. In _22nd USENIX Security Symposium_ , 2013.

- [44] Ullrich KH Ecker and Li Chang Ang. Political attitudes and the processing of misinformation corrections. _Political Psychology_ , 40(2):241–260, 2019.

- [45] Lutz Erbring, Edie N Goldenberg, and Arthur H Miller. Front-page news and real-world cues: A new look at agenda-setting by the media. _American journal of political science_ , pages 16–49, 1980.

[page 18]

- [46] EU Disinfo Lab. What is the doppelganger operation? https://www _._ disinfo _._ eu/doppelganger-operation/.

- [47] Tianyu Gao, Xingcheng Yao, and Danqi Chen. SimCSE: Simple contrastive learning of sentence embeddings. In _Empirical Methods in Natural Language Processing (EMNLP)_ , 2021.

- [48] R Kelly Garrett and Robert M Bond. Conservatives’ susceptibility to political misperceptions. _Science Advances_ , 2021.

- [49] Manuel Gomez-Rodriguez, Jure Leskovec, and Andreas Krause. Inferring networks of diffusion and influence. _ACM Transactions on Knowledge Discovery from Data (TKDD)_ , 5(4):1–37, 2012.

- [50] Manuel Gomez Rodriguez, Jure Leskovec, and Bernhard Schölkopf. Structure and dynamics of information pathways in online media. In _ACM international conference on Web search and data mining_ , 2013.

- [51] Lara Grimminger and Roman Klinger. Hate towards the political opponent: A twitter corpus study of the 2020 us elections on the basis of offensive speech and stance detection. In _Proceedings of the Eleventh Workshop on Computational Approaches to Subjectivity, Sentiment and Social Media Analysis_ , 2021.

- [52] Maarten Grootendorst. Bertopic: Neural topic modeling with a class-based tf-idf procedure. _arXiv preprint arXiv:2203.05794_ , 2022.

- [53] Felix Hamborg and Karsten Donnay. Newsmtsc: (multi-)target-dependent sentiment classification in news articles. In _European Chapter of the Association for Computational Linguistics_ , 2021.

- [54] Catherine Han, Deepak Kumar, and Zakir Durumeric. On the infrastructure providers that support misinformation websites. In _International AAAI Conference on Web and Social Media_ , 2022.

- [55] Hans WA Hanley and Zakir Durumeric. TATA: Stance detection via topic-agnostic and topic-aware embeddings. In _The 2023 Conference on Empirical Methods in Natural Language Processing_ , 2023.

- [56] Hans WA Hanley and Zakir Durumeric. Machinemade media: Monitoring the mobilization of machinegenerated articles on misinformation and mainstream news websites. In _International AAAI Conference on Web and Social Media_ , 2024.

- [57] Hans WA Hanley and Zakir Durumeric. Partial mobilization: Tracking multilingual information flows amongst russian media outlets and telegram. In _International AAAI Conference on Web and Social Media_ , 2024.

- [58] Hans WA Hanley, Deepak Kumar, and Zakir Durumeric. No calm in the storm: investigating QAnon website relationships. In _International AAAI Conference on Web and Social Media_ , 2022.

- [59] Hans WA Hanley, Deepak Kumar, and Zakir Durumeric. “A Special Operation”: A quantitative approach to dissecting and comparing different media ecosystems’ coverage of the Russo-Ukrainian war. In _International AAAI Conference on Web and Social Media_ , 2023.

- [60] Hans WA Hanley, Deepak Kumar, and Zakir Durumeric. A golden age: Conspiracy theories’ relationship with misinformation outlets, news media, and the wider internet. _Proceedings of the ACM on HumanComputer Interaction_ , 7(CSCW2):1–33, 2023.

- [61] Hans WA Hanley, Deepak Kumar, and Zakir Durumeric. Happenstance: Utilizing semantic search to track russian state media narratives about the russoukrainian war on reddit. In _International AAAI conference on web and social media_ , 2023.

- [62] Hans WA Hanley, Deepak Kumar, and Zakir Durumeric. Specious sites: Tracking the spread and sway of spurious news stories at scale. In _IEEE Symposium on Security and Privacy_ , 2024.

- [63] Momchil Hardalov, Arnav Arora, Preslav Nakov, and Isabelle Augenstein. Few-shot cross-lingual stance detection with sentiment-based pre-training. In _AAAI Conference on Artificial Intelligence_ , 2022.

- [64] Naeemul Hassan, Gensheng Zhang, Fatma Arslan, Josue Caraballo, Damian Jimenez, Siddhant Gawsane, Shohedul Hasan, Minumol Joseph, Aaditya Kulkarni, Anil Kumar Nayak, et al. Claimbuster: The first-ever end-to-end fact-checking system. _VLDB_ , 2017.

- [65] Pengcheng He, Jianfeng Gao, and Weizhu Chen. Debertav3: Improving deberta using electra-style pretraining with gradient-disentangled embedding sharing. In _11th Intl. Conf. on Learning Representations_ , 2022.

- [66] Nadia Heninger, Zakir Durumeric, Eric Wustrow, and J Alex Halderman. Mining your Ps and Qs: Detection of widespread weak keys in network devices. In _21st USENIX Security Symposium_ , 2012.

- [67] Jennifer Hoewe, Kathryn Cramer Brownell, and Eric C Wiemer. The role and impact of fox news. In _The forum_ , volume 18, pages 367–388. De Gruyter, 2020.

- [68] Austin Hounsel, Jordan Holland, Ben Kaiser, Kevin Borgolte, Nick Feamster, and Jonathan Mayer. Identifying disinformation websites using infrastructure features. In _USENIX Workshop on Free and Open Communications on the Internet_ , 2020.

[page 19]

- [69] Edward J Hu, Phillip Wallis, Zeyuan Allen-Zhu, Yuanzhi Li, Shean Wang, Lu Wang, Weizhu Chen, et al. Lora: Low-rank adaptation of large language models. In _International Conference on Learning Representations_ , 2021.

- [70] Hamed Jelodar, Yongli Wang, Chi Yuan, Xia Feng, Xiahui Jiang, Yanchao Li, and Liang Zhao. Latent dirichlet allocation (lda) and topic modeling: models, applications, a survey. _Multimedia Tools and Applications_ , 2019.

- [71] Zhiwei Jin, Juan Cao, Han Guo, Yongdong Zhang, and Jiebo Luo. Multimodal fusion with recurrent neural networks for rumor detection on microblogs. In _25th ACM international conference on Multimedia_ , 2017.

- [72] Jeff Johnson, Matthijs Douze, and Hervé Jégou. Billion-scale similarity search with GPUs. _IEEE Transactions on Big Data_ , 7(3), 2019.

- [73] Jonas L Juul and Johan Ugander. Comparing information diffusion mechanisms by matching on cascade size. _Proceedings of the National Academy of Sciences_ , 118(46), 2021.

- [74] Ben Kaiser, Jerry Wei, Eli Lucherini, Kevin Lee, J Nathan Matias, and Jonathan Mayer. Adapting security warnings to counter online disinformation. In _30th USENIX Security Symposium_ , 2021.

- [75] John Kerr, Costas Panagopoulos, and Sander Van Der Linden. Political polarization on covid-19 pandemic response in the united states. _Personality and individual differences_ , 179:110892, 2021.

- [76] Jon M Kleinberg, Ravi Kumar, Prabhakar Raghavan, Sridhar Rajagopalan, and Andrew S Tomkins. The web as a graph: Measurements, models, and methods. In _Computing and Combinatorics Conference_ , 1999.

- [77] Peter Kreko. Political tribalism, polarization, and the motivated rejection of science. In _The Tribal Mind and the Psychology of Collectivism_ . 2024.

- [78] Dilek Küçük and Fazli Can. Stance detection: A survey. _ACM Computing Surveys (CSUR)_ , 2020.

- [79] Brian Kulis and Michael I Jordan. Revisiting k-means: new algorithms via bayesian nonparametrics. In _International Conference on Machine Learning_ , 2012.

- [80] Sejeong Kwon, Meeyoung Cha, Kyomin Jung, Wei Chen, and Yajun Wang. Aspects of rumor spreading on a microblog network. In _Social Informatics: 5th International Conference_ , 2013.

- [81] Sejeong Kwon, Meeyoung Cha, Kyomin Jung, Wei Chen, and Yajun Wang. Prominent features of rumor propagation in online social media. In _IEEE international conference on data mining_ , 2013.

- [82] Mirko Lai, Viviana Patti, Giancarlo Ruffo, and Paolo Rosso. Stance evolution and twitter interactions in an italian political debate. In _Conference on Applications of Natural Language to Information Systems_ , 2018.

- [83] Gregor Leban, Blaz Fortuna, Janez Brank, and Marko Grobelnik. Event registry: learning about world events from news. In _23rd International Conference on World Wide Web_ , 2014.

- [84] David Leonhardt. Revisiting the gaza hospital explosion. https://www _._ nytimes _._ com/2023/11/03/briefing/ gaza-hospital-explosion _._ html, 11 2023.

- [85] Jure Leskovec, Lars Backstrom, and Jon Kleinberg. Meme-tracking and the dynamics of the news cycle. In _15th ACM SIGKDD international conference on Knowledge discovery and data mining_ , 2009.

- [86] Brian Lester, Rami Al-Rfou, and Noah Constant. The power of scale for parameter-efficient prompt tuning. In _Conference on Empirical Methods in Natural Language Processing_ , 2021.

- [87] Bin Liang, Qinlin Zhu, Xiang Li, Min Yang, Lin Gui, Yulan He, and Ruifeng Xu. Jointcl: A joint contrastive learning framework for zero-shot stance detection. In _60th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)_ , 2022.

- [88] Jing Ma, Wei Gao, Prasenjit Mitra, Sejeong Kwon, Bernard J Jansen, Kam-Fai Wong, and Meeyoung Cha. Detecting rumors from microblogs with recurrent neural networks. 2016.

- [89] Golshan Madraki, Isabella Grasso, Jacqueline M. Otala, Yu Liu, and Jeanna Matthews. Characterizing and comparing covid-19 misinformation across languages, countries and platforms. In _The web conference_ , 2021.

- [90] Alexander Martin. Russians impersonate washington post and fox news with anti-ukraine stories. https: //therecord _._ media/russians-fake-news-anti-ukraine.

- [91] Maxwell McCombs and DL Shaw. The agenda-setting function of the press. _The Press. Oxford, England: Oxford University Press Inc_ , pages 156–168, 2005.

- [92] Damon McCoy, Andreas Pitsillidis, Jordan Grant, Nicholas Weaver, Christian Kreibich, Brian Krebs, Geoffrey Voelker, Stefan Savage, and Kirill Levchenko. PharmaLeaks: Understanding the business of online pharmaceutical affiliate programs. In _21st USENIX Security Symposium_ , 2012.

[page 20]

- [93] Leland McInnes, John Healy, Steve Astels, et al. hdbscan: Hierarchical density based clustering. _J. Open Source Softw._ , 2(11):205, 2017.

- [94] Science Based Medicine. Vaccines. https:// sciencebasedmedicine _._ org/category/vaccines/, 2024.

- [95] Sarah Meiklejohn, Marjori Pomarole, Grant Jordan, Kirill Levchenko, Damon McCoy, Geoffrey M Voelker, and Stefan Savage. A fistful of bitcoins: characterizing payments among men with no names. In _ACM Internet measurement conference_ , 2013.

- [96] Yu Meng, Yunyi Zhang, Jiaxin Huang, Yu Zhang, and Jiawei Han. Topic discovery via latent space clustering of pretrained language model representations. In _ACM Web Conference_ , 2022.

- [97] Joseph Mercola. Fda anxious for pfizer to rush covid shots for babies and toddlers. but why? https://web _._ archive _._ org/web/20220208225347/https: //childrenshealthdefense _._ org/defender/fda-pfizerrush-covid-shots-babies-toddlers/, 2 2022.

- [98] Sebastião Miranda, Arturs Znoti¯ n, š, Shay B. Cohen, and Guntis Barzdins. Multilingual clustering of streaming news. In _Conference on Empirical Methods in Natural Language Processing_ , 2018.

- [99] Saif Mohammad, Svetlana Kiritchenko, Parinaz Sobhani, Xiaodan Zhu, and Colin Cherry. Semeval-2016 task 6: Detecting stance in tweets. In _International workshop on semantic evaluation_ , 2016.

- [100] Elaheh Momeni, Shanika Karunasekera, Palash Goyal, and Kristina Lerman. Modeling evolution of topics in large-scale temporal text corpora. In _International AAAI Conference on Web and Social Media_ , 2018.

- [101] Ryan C Moore, Ross Dahlke, and Jeffrey T Hancock. Exposure to untrustworthy websites in the 2020 us election. _Nature Human Behaviour_ , 2023.

- [102] Benjamin Mueller and Sheryl Gay Stolberg. Fauci grilled by lawmakers on masks, vaccine mandates and lab leak theory. https://web _._ archive _._ org/save/https: //www _._ nytimes _._ com/2024/06/03/science/faucihearing-covid-origins _._ html, 6 2024.

- [103] Preslav Nakov and Giovanni Da San Martino. Fake news, disinformation, propaganda, and media bias. In _ACM International Conference on Information & Knowledge Management_ , 2021.

- [104] Nishanth Nakshatri, Siyi Liu, Sihao Chen, Dan Roth, Dan Goldwasser, and Daniel Hopkins. Using llm for improving key event discovery: Temporal-guided news stream clustering with event summaries. In _Empirical Methods in Natural Language Processing_ , 2023.

- [105] David Ng. Left-wing guardian triggered by my son hunter: Stop trying to make hunter biden conspiracy theories happen. https://web _._ archive _._ org/web/20220903140730/https: //www _._ breitbart _._ com/entertainment/2022/09/03/ leftwing-guardian-triggered-by-my-son-hunter-stoptrying-to-make-hunter-biden-conspiracy-theorieshappen/, 9 2022.

- [106] US Department of State Global Engagement Center. Gec special report: Russia’s pillars of disinformation and propaganda - united states department of state. https://www _._ state _._ gov/russias-pillars-ofdisinformation-and-propaganda-report/, 8 2020.

- [107] Antonis Papasavva, Jeremy Blackburn, Gianluca Stringhini, Savvas Zannettou, and Emiliano De Cristofaro. “is it a qoincidence?”: An exploratory study of qanon on voat. In _Proceedings of the Web Conference 2021_ , pages 460–471, 2021.

- [108] Pujan Paudel, Jeremy Blackburn, Emiliano De Cristofaro, Savvas Zannettou, and Gianluca Stringhini. Lambretta: learning to rank for twitter soft moderation. In _IEEE Symposium on Security and Privacy_ , 2023.

- [109] Francesco Pierri, Luca Luceri, Nikhil Jindal, and Emilio Ferrara. Propaganda and misinformation on facebook and twitter during the russian invasion of ukraine. In _Proceedings of the 15th ACM web science conference 2023_ , pages 65–74, 2023.

- [110] Aleksandra Piktus, Fabio Petroni, Vladimir Karpukhin, Dmytro Okhonko, Samuel Broscheit, Gautier Izacard, Patrick Lewis, Barlas O˘guz, Edouard Grave, Wen-tau Yih, et al. The web is your oyster–knowledge-intensive nlp against a very large web corpus. _arXiv preprint arXiv:2112.09924_ , 2021.

- [111] The Associated Press. Not real news: A look at what didn’t happen this week. https://web _._ archive _._ org/web/20231124154018/https: //apnews _._ com/article/fact-check-misinformationf3c1d54f2d059de0532360d638335e99, 11 2023.

- [112] Stephen Prochaska, Kayla Duskin, Zarine Kharazian, Carly Minow, Stephanie Blucker, Sylvie Venuto, Jevin D West, and Kate Starbird. Mobilizing manufactured reality: How participatory disinformation shaped deep stories to catalyze action during the 2020 us presidential election. _Proceedings of the ACM on Human-Computer Interaction_ , 7(CSCW1):1–39, 2023.

- [113] Meet Rajdev and Kyumin Lee. Fake and spam messages: Detecting misinformation during natural disasters on social media. In _Intl. Conf. on Web Intelligence and Intelligent Agent Technology_ , 2015.

[page 21]

- [114] Nils Reimers and Iryna Gurevych. Sentence-bert: Sentence embeddings using siamese bert-networks. In _Conference on Empirical Methods in Natural Language Processing and the 9th International Joint Conference on Natural Language Processing_ , 2019.

- [115] Britta Ruhnau. Eigenvector-centrality—a nodecentrality? _Social networks_ , 22(4):357–365, 2000.

- [116] Kimberly Ruth, Aurore Fass, Jonathan Azose, Mark Pearson, Emma Thomas, Caitlin Sadowski, and Zakir Durumeric. A world wide view of browsing the world wide web. In _ACM Internet Measurement Conference_ , 2022.

- [117] Kimberly Ruth, Deepak Kumar, Brandon Wang, Luke Valenta, and Zakir Durumeric. Toppling top lists: Evaluating the accuracy of popular website lists. In _22nd ACM Internet Measurement Conference_ , 2022.

- [118] Mohammad Hammas Saeed, Shiza Ali, Jeremy Blackburn, Emiliano De Cristofaro, Savvas Zannettou, and Gianluca Stringhini. Trollmagnifier: Detecting statesponsored troll accounts on reddit. In _IEEE Symposium on Security and Privacy_ , 2022.

- [119] Kailash Karthik Saravanakumar, Miguel Ballesteros, Muthu Kumar Chandrasekaran, and Kathleen Mckeown. Event-driven news stream clustering using entityaware contextual embeddings. In _Conference of the European Chapter of the Association for Computational Linguistics: Main Volume_ , 2021.

- [120] Mike S Schäfer and James Painter. Climate journalism in a changing media ecosystem: Assessing the production of climate change-related news around the world. _Wiley Interdisciplinary Reviews: Climate Change_ , 12(1):e675, 2021.

- [121] Gautam Kishore Shahi. Warclaim: A dataset for fake news on 2023 Israel–Hamas war. In _ACM Web Science Conference_ , 2024.

- [122] Laura Silver and Aiden Connaughton. Partisanship colors views of covid-19 handling across advanced economies. https://www _._ pewresearch _._ org/global/ 2022/08/11/partisanship-colors-views-of-covid-19handling-across-advanced-economies/, 8 2022.

- [123] Vidhi Singrodia, Anirban Mitra, and Subrata Paul. A review on web scrapping and its applications. In _2019 international conference on computer communication and informatics (ICCCI)_ , pages 1–6. IEEE, 2019.

- [124] Jason Smith, Herve Saint-Amand, Magdalena Plamad˘a, Philipp Koehn, Chris Callison-Burch, and Adam Lopez. Dirt cheap web-scale parallel text from the common crawl. In _Annual Meeting of the Association for Computational Linguistics_ , 2013.

- [125] Vincent Smith. _Go Web Scraping Quick Start Guide: Implement the power of Go to scrape and crawl data from the web_ . Packt Publishing Ltd, 2019.

- [126] Kaitao Song, Xu Tan, Tao Qin, Jianfeng Lu, and TieYan Liu. Mpnet: Masked and permuted pre-training for language understanding. _Adv. in Neural Information Processing Systems_ , 2020.

- [127] Kate Starbird, Ahmer Arif, Tom Wilson, Katherine Van Koevering, Katya Yefimova, and Daniel Scarnecchia. Ecosystem or echo-system? exploring content sharing across alternative media domains. In _International AAAI Conference on Web and Social Media_ , 2018.

- [128] Ram Sundara Raman, Louis-Henri Merino, Kevin Bock, Marwan Fayed, Dave Levin, Nick Sullivan, and Luke Valenta. Global, passive detection of connection tampering. In _ACM SIGCOMM_ , 2023.

- [129] Ram Sundara Raman, Prerana Shenoy, Katharina Kohls, and Roya Ensafi. Censored planet: An internetwide, longitudinal censorship observatory. In _ACM SIGSAC conference on computer and communications security_ , 2020.

- [130] Kurt Thomas, Elie Bursztein, Chris Grier, Grant Ho, Nav Jagpal, Alexandros Kapravelos, Damon McCoy, Antonio Nappa, Vern Paxson, Paul Pearce, et al. Ad injection at scale: Assessing deceptive advertisement modifications. In _IEEE Symposium on Security and Privacy_ , 2015.

- [131] Filip Timotija. Ukraine defense minister presses us to allow use of long-range weapons on russia. https://web _._ archive _._ org/web/20240831192927/https: //thehill _._ com/policy/international/4857208-ukrainedefense-minister-rustem-umerov-long-rangemissiles-restriction/, 8 2024.

- [132] Russia Today. Finland rules on fate of seized russian artwork. https://web _._ archive _._ org/web/ 20220524233445/https://www _._ rt _._ com/russia/553529finland-russia-art-decision/, 4 2022.

- [133] Peter D Turney. Mining the web for synonyms: Pmi-ir versus lsa on toefl. In _European conference on machine learning_ , 2001.

- [134] U.S. Department of Justice. Justice department disrupts covert russian government-sponsored foreign malign influence operation targeting audiences in the united states and elsewhere. https://www _._ justice _._ gov/ opa/pr/justice-department-disrupts-covert-russiangovernment-sponsored-foreign-malign-influence.

[page 22]

- [135] Yuli Vasiliev. _Natural language processing with Python and spaCy: A practical introduction_ . No Starch Press, 2020.

- [136] Soroush Vosoughi, Deb Roy, and Sinan Aral. The spread of true and false news online. _Science_ , 2018.

   - [148] Xinyi Zhou, Ashish Sharma, Amy X Zhang, and Tim Althoff. Correcting misinformation on social media with a large language model. _arXiv preprint arXiv:2403.11169_ , 2024.

- [137] Isaac Waller and Ashton Anderson. Quantifying social organization and political polarization in online platforms. _Nature_ , 600(7888):264–268, 2021.

- [138] Liang Wang, Nan Yang, Xiaolong Huang, Binxing Jiao, Linjun Yang, Daxin Jiang, Rangan Majumder, and Furu Wei. Text embeddings by weakly-supervised contrastive pre-training. _arXiv preprint arXiv:2212.03533_ , 2022.

- [139] Galen Weld, Maria Glenski, and Tim Althoff. Political bias and factualness in news sharing across more than 100,000 online communities. In _International AAAI Conference on Web and Social Media_ , 2021.

- [140] Christina Wilkie. Dinesh d´souza election fraud film, book 2000[´] mules pulled after defamation suit. https://web _._ archive _._ org/web/20240601000808/https: //www _._ cnbc _._ com/2024/05/31/dinesh-dsouzaelection-film-2000-mules-pulled _._ html, 5 2024.

- [141] Liang Wu, Fred Morstatter, Kathleen M Carley, and Huan Liu. Misinformation in social media: definition, manipulation, and detection. _ACM SIGKDD Explorations Newsletter_ , 21(2):80–90, 2019.

- [142] Jianhua Yin, Daren Chao, Zhongkun Liu, Wei Zhang, Xiaohui Yu, and Jianyong Wang. Model-based clustering of short text streams. In _24th ACM SIGKDD international conference on knowledge discovery & data mining_ , 2018.

- [143] Dave Van Zandt. Media-Bias/Fact-Check. https:// mediabiasfactcheck _._ com/yahoo-news/, 2022.

- [144] Dave Van Zandt. Media-Bias/Fact-Check. https:// mediabiasfactcheck _._ com/north-alaska-news/, 2022.

- [145] Eric Zeng, Tadayoshi Kohno, and Franziska Roesner. Bad news: Clickbait and deceptive ads on news and misinformation websites. In _Workshop on Technology and Consumer Protection_ , 2020.

- [146] Yunyi Zhang, Fang Guo, Jiaming Shen, and Jiawei Han. Unsupervised key event detection from massive text corpora. In _ACM SIGKDD conference on knowledge discovery and data mining_ , 2022.

- [147] Deyu Zhou, Haiyang Xu, and Yulan He. An unsupervised Bayesian modelling approach for storyline detection on news articles. In _Conference on Empirical Methods in Natural Language Processing_ , 2015.

[page 23]

## **A Article Preprocessing**

After collecting each page’s HMTL, we then parse the content to extract the news article text and publication date using the Python libraries newspaper3k and htmldate. We subsequently remove any leftover boilerplate language ( _i.e._ , navigation links, headers, and footers) from the text using the justext Python library and remove any non-English articles based on labels provided by the Python langdetect library.

To prepare our news article data for embedding, we first remove any URLs, emojis, and HTML tags from the text. Then, in line with prior work, we subsequently divide these our articles in constituent _passages_ with at most 100 words [57, 61, 110]. Specifically, after first separating articles into different paragraphs by splitting their text on (\n) or tab (\t) characters and breaking apart each paragraph into its constituent sentences [21], we add sentences from a single paragraph to create a _passage_ until its length is at most 100 words. We embed the constituent _passages_ , rather than full articles given the context window size limitations of the large language that we use in this work. Furthermore, as argued by Hanley et al. [62] and shown by Pikbus et al. [110], given that articles often address multiple ideas, embedding _passages_ allows us to track the often single idea present within the passage.[6] Our dataset consists of 428,051,085 passages.

(where _passagei_ is the passage text) twice (with dropout both times) with a given model by inputting [ _CLS_ ] _texti_ [ _SEP_ ] and averaging the contextual word vectors of the resulting output as a hidden vector **h** _i_ and **h**[˜] _i_ for _passagei_ as its representations. Then, given a set of hidden vectors _{_ **h** _i}[N] i_ = _[b]_ 0[and] _[ {]_ **[h]**[˜] _[j][}][N] j_ = _[b]_ 0[(dif-] ferent dropout), where _Nb_ is the size of the batch, we perform a contrastive learning step for each batch. This is such that for each Batch _B_ , for an _anchor_ hidden embedding **hi** within the batch, the set of hidden vectors **hi** _,_ **h[˜] j** _∈ B_ , vectors where _i_ = _j_ are positive pairs. Other pairs where _i ̸_ = _j_ are considered negative pairs. Within each batch _B_ , the contrastive loss is computed across all positive pairs in the batch:

**==> picture [151 x 79] intentionally omitted <==**

where, as in prior work [87], we utilize a temperature τ = 0 _._ 07. When performing fine-tuning, we utilize default hyperparameters (learning rate 3 _×_ 10 _[−]_[5] , batch size=128, and 1M examples) specified in Gao et al. [47].

## **D Pointwise Mutual Information**

## **B PEFT through LoRA**

We utilize _Parameter Efficient Fine-Tuning_ /PEFT [86] through _Low-Rank Adaption_ /LoRA [69] to fine-tune and adapt pre-trained models to our datasets or to better their performance. LoRA, specifically, after freezing the weights of the original pre-trained model learns pairs of low-rankdecomposition matrices, reducing the amount of parameters that need to be learned. LoRA has been shown to often outperform other types of adaptions including full-tuning [69]. Once learned, these matrices are merged with the original frozen weights. LoRA requires the specification of the rank of the matrices learned and an α value that scales the learned parameters. Within this work, we learn LoRA matrices for the attention and the dense/linear layers of our models and utilize the commonly used defaults of rank=8 and α=16 [69].

## **C Training with Unsupervised Contrastive Loss**

To adapt our embedding models to our news dataset, we utilize unsupervised contrastive learning [47]. For training, this is such that we embed each example _xi_ = ( _passagei_ ) _∈ DNews_

> 6For example, a New York Times article addressing a novel virus spreading in China may also address the Chinese government’s previous approaches to dealing with the COVID-19 pandemic.https: //web _._ archive _._ org/web/20231125001740/https://www _._ nytimes _._ com/2023/

The PMI of a word _wordi_ in a cluster _C j_ is calculated:

**==> picture [151 x 24] intentionally omitted <==**

where _P_ is the probability of occurrence and a scaling parameter α = 1 is added to the counts of each word per cluster. This scaling parameter α prevents low-frequency words in each cluster from having the highest PMI value [133].

## **E Evaluation on SemEval22**

**==> picture [242 x 122] intentionally omitted <==**

**----- Start of picture text -----**<br>
1.0<br>0.9<br>0.8<br>0.7<br>0.6<br>0.5<br>0.4 Precision<br>0.3 Recall<br>0.2 F1-Score<br>0.1<br>0.0<br>Cosine Similarity Threshold<br>0.00 0.10 0.20 0.30 0.40 0.50 0.60 0.70 0.80<br>Metric on STS22-EN<br>**----- End of picture text -----**<br>

Figure 12: Evaluation of our model’s precision, recall, and _F_ 1 scores on the English portion of the SemEval22 test dataset [29] (using 3.0 as the cut-off for the two articles being about the same event [57]).

> 11/23/world/asia/who-china-respiratory-children _._ html

[page 24]

## **F Passage Pairs at Various Thresholds**

## **0.35 Similarity**

**PASSAGE 1:** Russias war in Ukraine created a full-on energy crisis as Moscow reduced or cut off natural gas flows to European countries that rely on the fuel to power industry, generate electricity and heat and cool homes. Shrinking supplies, higher demand and fears of a complete Russian cutoff have driven natural gas prices to record highs, further fueling inflation that has squeezed peoples ability to spend and raised the risk of a recession in Europe and the U.K.

**PASSAGE 2:** Fingrid had been expecting that Olkiluoto 3 alone would more than compensate for the loss of Russian power imports this winter, he added. Imports of Russian power stopped in May after Russian utility Inter RAO said it had not been paid for the power it sold via pan European exchange Nord Pool since May 6. Without Olkiluoto 3 the situation is quite tight because that would have been more than 10 of the peak demand alone, Ruusunen said.

## **0.50 Similarity**

## **0.40 Similarity**

**PASSAGE 1:** HONG KONG, Jan 13 (Reuters Breakingviews) - WM Motor, a Chinese electric-car star that has fallen on hard times, is reversing into an ambitious Plan C. After two earlier attempts at an initial public offering floundered, the group founded by Zhejiang Geely veteran Freeman Shen will at last go public by selling its auto business to Hong Kong-listed Apollo Future Mobility (0860.HK) for $2 billion. They make an odd couple. Although both are car companies, their cars have little in common.

**PASSAGE 2:** Global and Chinese automakers plan to unveil more than a dozen new electric SUVs, sedans and muscle cars this week at the Shanghai auto show, their first full-scale sales event in four years in a market that has become a workshop for developing electrics, self-driving cars and other technology.

## **0.45 Similarity**

**PASSAGE 1:** Diseases like Ebola and other hemorrhagic fevers were responsible for 70% of those outbreaks, in addition to illnesses like monkeypox, dengue, anthrax and plague. We must act now to contain zoonotic diseases before they can cause widespread infections and stop Africa from becoming a hotspot for emerging infectious diseases, WHOs Africa director, Dr. Matshidiso Moeti said in a statement.

**PASSAGE 1:** The fatal accident occurred around 4 a.m., and it took several hours to clear the freeway. The firetruck had to be towed away. The Model S was among the nearly 363,000 vehicles Tesla recalled on Thursday because of potential flaws in its Full Self-Driving system. While the recall is aimed at correcting possible problems at intersections and with speed limits, it comes amid a broader investigation by U.S. safety regulators into Teslas automated driving systems.’

**PASSAGE 2:** The National Highway Traffic Safety Administration (NHTSA) is opening a special investigation into the crash of a 2021 Tesla Model Y vehicle that killed a motorcyclist in California, it said on Monday. Since 2016, NHTSA has opened 37 special investigations of crashes involving Tesla vehicles and where advanced driver assistance systems such as Autopilot were suspected of being used. A total of 18 crash deaths were reported in those Tesla-related investigations, including the most recent fatal California crash.

Figure 13: Example of passage pairs at different levels of cosine similarity.

**PASSAGE 2:** Equatorial Guinea has confirmed 13 cases of Marburg disease since the beginning of the epidemic, its health officials said on Wednesday after the head of the World Health Organization (WHO) urged the Central African country’s government to report new cases officially. Marburg virus disease is a viral haemorrhagic fever that can have a fatality rate of up to 88%, according to the WHO.

[page 25]

## **G NETINF Algorithm**

NETINF is a greedy algorithm that iteratively computes the marginal gain ( _i.e._ , the explanatory power of adding the edge given the set of cascades) of adding a particular weighted edge between two entities/nodes and by only considering the most probable transmission tree ( _i.e._ , the steps taken for a given narrative to reach a particular website), NETINF efficiently infers the relationships within the underlying network. The NETINF algorithm returns both the marginal gain as well the rate of information flow between two nodes/websites for each edge. Thus given a set of cascades _C_ , NETINF aims to find the the graph _G_[ˆ] that solves the optimization problem [49]:

**==> picture [84 x 19] intentionally omitted <==**

## **H Optimized DP-Means**

DP-Means [79] is a non-parametric extension of the K-means algorithm that does not require the specification of the number of clusters _a priori_ . Within DP-Means, when a given datapoint is a chosen parameter λ away from the closest cluster, a new cluster is formed. Dinari et al. [38] parallelize this algorithm by _delaying cluster creation_ until the end of the assignment step. Namely, instead of creating a new cluster each time a new datapoint is discovered, the algorithm instead determines which datapoint is furthest from the current set of clusters and then creates a new cluster with that datapoint. By delaying cluster creation, the DP-means algorithm can be trivially parallelized. Furthermore, by delaying cluster creation, this version of DP-Means avoids over-clustering the data ( _i.e.,_ only the most disparate datapoints create new clusters) [38].

where

**==> picture [218 x 50] intentionally omitted <==**

and where _c_ is a cascade, _T_ ( _G_ ) is the set of all directed spanning trees on _G_ , andd _Pc_ ( _i, j_ ) (or that the node _i_ influences node _j_ in a cascade) is proportional to the time difference between when the two nodes are infected ( _i.e._ , when the two websites post a given story about a particular narrative), given an exponential waiting time for infection.

To optimize this formulation, NETINF only considers the most likely propagation tree _T_ for a given cascade _c_

**==> picture [206 x 23] intentionally omitted <==**

The improvement of the log-likelihood of a given cascade _c_ for a graph _G_ over the empty graph _K_ is then:

**==> picture [182 x 17] intentionally omitted <==**

and the NETINF algorithm optimizes the following objective function by iteratively and greedily adding edges with the highest marginal gain to the objective function:

**==> picture [76 x 20] intentionally omitted <==**

[page 26]

## **I Evaluation of Clusters**

|||Passages||
|---|---|---|---|
|Narr.|Keywords|Checked|Prec.|
|1|laissez-faire, progressivism, liberalism, laissez, corpus|193|96.89%|
|2|quake, earthquake, aftershock, turkey, rubble|500|100.00%|
|3|sinema, manchin, flibuster, kyrsten, senate|500|100.00%|
|4|williamson, marianne, self-help, williamsons, sander|500|97.40%|
|5|dysphoria, puberty, blocker, crosssex, hormone|500|100.00%|
|6|sudan, anand, evacuation, sudanese, khartoum|500|100.00%|
|7|rioter, slogan, bearing, capitol, drum|500|99.20%|
|8|teixeira, dighton, guardsman, teixeiras, massachusetts|500|99.40%|
|9|fdny, frefghter, frehouse, klein, kavanagh|500|97.00%|
|10|bragg, alvin, rouser, nypd, rabble|500|95.60%|
|11|taliban, afghan, afghanistan, hunger, malnutritio|500|100.00%|
|12|eyesight, blindness, blind, eye, sight|500|99.40%|
|13|maralago, classifed, ballroom, fundraiser, document|500|100.0%|
|14|carolina, vetoproof, map, raleigh, cooper|500|99.80%|
|15|tarantino, quentin, pulp, cinema, flmmaker|500|99.20%|
|16|seoul,korea, posco, compensate, keb|500|100.00%|
|17|miscarriage, pregnant, pregnancy, csection, motherhood|500|100.00%|
|18|faucis, niaid, anthony, gain-of-function, allergy|500|100.00%|
|19|crump, arbery, breonna, ahmaud, trayvon|500|99.08%|
|20|portuguese, slave, plantation, colony, dutch|500|100.00%|
|21|cadet, guard, harassment, assault, adjutant|500|100.00%|
|22|spam, bot, musk, twitter, elon|500|98.80%|
|23|ufo, roswell, sighting, saucer, alien|500|100.00%|
|24|cpu, intel, x86, processor, amd|500|96.40%|
|25|chappelle, comedian, isaiah, onstage, attacker|500|100.00%|
|26|burisma, pozharskyi, vadym, hunter, zlochevsky|500|100.00%|
|27|ubridgerton, penelope, featherington, daphne, coughland|500|100.00%|
|28|naloxone, narcan, over-the-counter, emergent, nasal|500|100.00%|
|29|schmitt, greitens, hartzler, missouri, trudy|100|99.20%|
|30|currency, dollar, yuan, reserve, de-dollarization|500|99.80%|
|||**Prec.**|**99.26%**|

[page 27]

## **J Additional Stances**

|Pro-China Stances<br>Coeff.<br>Std.<br>Pro self-reliance<br>0.286<br>0.092<br>Pro communist<br>0.180<br>0.093<br>Pro africa<br>0.126<br>0.103<br>Anti-China Stances<br>Against communist<br>-0.288<br>0.087<br>Against covid<br>-0.228<br>0.091<br>Against russia<br>-0.215<br>0.072|Coeff.|Std.|
|---|---|---|

Table 10: The stances associated with China according to the Bayesian model.

|Pro-Iran Stances<br>Coeff.<br>Std.<br>Against yemeni<br>0.055<br>0.061<br>Pro islamic<br>0.052<br>0.042<br>Pro armenia<br>0.049<br>0.036<br>Anti-Iran Stances<br>Against tehran<br>-0.073<br>0.060<br>Against islamic<br>-0.058<br>0.043<br>Against communist<br>-0.047<br>0.038|Coeff.|Std.|
|---|---|---|
||-0.073<br>-0.058<br>-0.047|0.060<br>0.043<br>0.038|

Table 11: The stances associated with Iran according to the Bayesian model.

|Pro-America Stances|Coeff.|Std.|
|---|---|---|
||||
|Pro harvard<br>Pro allstar<br>Pro mvp|0.111<br>0.085<br>0.070|0.064<br>0.055<br>0.045|
||||
|Anti-America Stances|||
||||
|Against graham<br>Against cia<br>Against canada|-0.143<br>-0.126<br>-0.126|0.070<br>0.069<br>0.060|

Table 12: The stances associated with America according to the Bayesian model.

[page 28]

**==> picture [506 x 500] intentionally omitted <==**

**----- Start of picture text -----**<br>
Unreliable,  = 0.592 Unreliable,  = 0.245<br>messengernews.net<br>Mixed Reliability  = 0.714 bluegrasstimes.com Mixed Reliability  = 0.149<br>Reliable,  = 0.774 Reliable,  = 0.074<br>adflegal.org<br>thepeoplescube.com<br>infostormer.com<br>thepatriotjournal.com<br>0.0 0.2 0.4 0.6 0.8 1.0 0.0 0.2 0.4 0.6 0.8 1.0<br>% of Articles PRO America % of Articles AGAINST America<br>(a) Dist. of Pro America (b) Dist. of Against America<br>Unreliable,  = 0.078 Unreliable,  = 0.333<br>tabletmag.com<br>Mixed Reliability  = 0.104 Mixed Reliability  = 0.273<br>Reliable,  = 0.123 Reliable,  = 0.212<br>voterig.com<br>dailyhive.com<br>discoverthenetworks.org<br>boundingintocomics.com<br>cctv.com<br>0.0 0.2 0.4 0.6 0.8 1.0 0.0 0.2 0.4 0.6 0.8 1.0<br>% of Articles PRO China % of Articles AGAINST China<br>(c) Dist. of Pro China (d) Dist. of Against China<br>Unreliable,  = 0.072 Unreliable,  = 0.331 castanet.net<br>Mixed Reliability  = 0.086 Mixed Reliability  = 0.297<br>Reliable,  = 0.091 Reliable,  = 0.286<br>hagmannreport.com<br>cambridge.org<br>presstv.ir<br>thefederalist.com<br>tasnimnews.com<br>0.0 0.2 0.4 0.6 0.8 1.0 0.0 0.2 0.4 0.6 0.8 1.0<br>% of Articles PRO Iran % of Articles AGAINST Iran<br>(e) Dist. of Pro Iran (f) Dist. of Against Iran<br>Density Density<br>Density Density<br>Density Density<br>**----- End of picture text -----**<br>

Figure 14: Distribution of stances to various entities.

[page 29]

**==> picture [253 x 507] intentionally omitted <==**

**----- Start of picture text -----**<br>
Reliable (µ=0.10)<br>Mixed (µ=-0.03)<br>Unreliable (µ=-0.46)<br>wonkette.com uniteamericafirst.com<br>sonsoflibertymedia.com<br>espn.com<br>3 2 1 0 1 2 3<br>Estimated Bias (Anti-America -> Pro-America)<br>(a) America Latent<br>Reliable (µ=0.17)<br>Mixed (µ=0.11) tass.com<br>Unreliable (µ=-0.37)<br>nymag.com<br>spectator.org cctv.com<br>3 2 1 0 1 2 3<br>Estimated Bias (Anti-China -> Pro-China)<br>(b) China Latent<br>Reliable (µ=-0.07)<br>Mixed (µ=-0.10)<br>Unreliable (µ=-0.19)<br>gatestoneinstitute.org<br>tehrantimes.com<br>china.org.cn<br>foxnews.com<br>3 2 1 0 1 2 3<br>Estimated Bias (Anti-Iran -> Pro-Iran)<br>(c) Iran Latent<br>**----- End of picture text -----**<br>

Figure 15: Latents for Biases to entities.

[page 30]

**Pro America**

|||**Pro America**|||
|---|---|---|---|---|
|Reliable||Mixed||Unreliable|
|messengernews.net (100.0%)||bluegrasstimes.com (100.0%)||adfegal.org (100.0%)|
|nationalgeographic.com (100.0%)||tribunnews.com (100.0%)||worldcouncilforhealth.org (100.0%)|
|fee.org (100.0%)||yaf.org (100.0%)||nvic.org (100.0%)|
|||**Against America**|||
|Reliable||Mixed||Unreliable|
|thepeoplescube.com (100.0%)||thepatriotjournal.com (76.9%)||infostormer.com (80.0%)|
|cjr.org (50.0%)||greanvillepost.com (68.9%)||paulcraigroberts.org (71.4%)|
|techdirt.com (46.2%)||newscorpse.com (58.8%)||gellerreport.com (64.9%)|
|||**Pro China**|||
|Reliable||Mixed||Unreliable|
|dailyhive.com (64.1%)||cctv.com (55.1%)||discoverthenetworks.org (50.0%)|
|emerging-europe.com (64.0%)||egypttoday.com (47.1%)||occupydemocrats.com (41.7%)|
|tdn.com (58.3%)||thecountersignal.com (45.5%)||medicalkidnap.com (37.8%)|
|||**Against China**|||
|Reliable||Mixed||Unreliable|
|tabletmag.com (70.0%)||boundingintocomics.com (100.0%)||voterig.com (94.6%)|
|outsidethebeltway.com (69.8%)||faithwire.com (81.8%)||govtslaves.com (93.3%)|
|icij.org (63.6%)||fff.org (81.8%)||conservativeplaylist.com (82.4%)|
|||**Pro Iran**|||
|Reliable|Mixed||Unreliable||
|cambridge.org (55.9%)|tasnimnews.com (36.9%)||presstv.ir (34.8%)||
|lamag.com (50.0%)|almanar.com.lb (34.5%)||theconservativetreehouse.com (33.3%)||
|msmagazine.com (46.4%)|mehrnews.com (32.6%)||healthimpactnews.com (25.0%)||
|||**Against Iran**|||
|Reliable|Mixed||Unreliable||
|castanet.net (78.1%)|thefederalist.com (78.6%)||hagmannreport.com (100.0%)||
|dailysignal.com (72.2%)|smirkingchimp.com (78.6%)||clarionproject.org (69.2%)||
|wearethemighty.com (70.0%)|patriotnewsalerts.com (76.9%)||thewashingtonstandard.com (68.8%)||

Table 13: The set of news websites with the highest percentage of _Pro_ -articles about various entities/topics.

[page 31]

## **K Articles over Time**

**==> picture [454 x 256] intentionally omitted <==**

**----- Start of picture text -----**<br>
Hunter Biden laptop scandal, which emerged in 2020.<br>The laptop, left at a Delaware repair shop, contained<br>emails and photos that implicated Hunter Biden in<br>Governments should  business dealings with foreign actors and raised<br>Ukrainian President Volodymyr  Zelenskyy has expressed his unwavering determination for solidarity with the West in the face of Russia's invasion, but has been met with hesitation from some NATO members,  Calls to protect the US Constitution and its principles, uphold individual rights and liberties, and reaffirm the country's founding values. prioritize expression over censorship, especially when content is controversial or inconvenient. Florida Governor Ron DeSantis is gearing up for a potential 2024 presidential bid,  having successfully led the charge  against "woke" ideology in his state, pushing conservative policies and rallying the GOP base questions about his father, Joe Biden's, involvement.Public figures and politicians have emphasized the importance of dignity, respect, and human rights in various contexts.<br>particularly the US Scientists warn that brief exposure to viral infections like the flu and Covid  Multiple high-ranking US officials,<br>There is censorship, propaganda, and government control in the US. cancel culture is a form of censorship, and that government-funded media outlets can exercise control over editorial content. The text also warns about the influence of the "Deep State" and far-left  may not cause illness, but prolonged  exposure can be hazardous, particularly for individuals with respiratory issues such as asthma. including former Vice President Mike Pence, President Joe Biden, and former President Donald Trump, have been found possessing classified material in their personal homes.  Multiple migrant  incidents have been reported along the US-Mexico border, with 15 Chinese migrants arriving in Dania Beach, Florida, and being processed  for removal.<br>communists in US institutions,<br>including the government, media,<br>education, and Big Business.<br>**----- End of picture text -----**<br>

**==> picture [150 x 8] intentionally omitted <==**

**----- Start of picture text -----**<br>
(a) Story Spread on Unreliable News Websites<br>**----- End of picture text -----**<br>

**==> picture [455 x 258] intentionally omitted <==**

**----- Start of picture text -----**<br>
The US government has been dealing<br>In a recent interview, Zelensky acknowledged  that Ukraine is not a member of NATO, but submitted an emergency application for accelerated accession, citing a "decisive step" towards gaining legal recognition as a NATO member. Several companies have  Elon Musk, Twitter's largest shareholder, has made a $43 billion bid to acquire the company, citing its potential to be a platform for free speech.Kim Kardashian West has condemned  antisemitism, following comments  Common illnesses such as E. coli, the common cold, Legionnaires' disease, human metapneumovirus (HMPV), COVID-19, and monkeypox can cause a range of symptoms,  Cristiano Ronaldo, the 37-year-old Portuguese forward, has been a dominant force in international soccer for nearly two decades, but his future is uncertain. with multidocuments found at the homes and offices of former and current presidents. ple cases of classified<br>recently released their  made by her ex-husband Kanye West.  including fever, diarrhea,<br>financial reports, showcasing  This stance is in line with other family  respiratory issues, and rashes.<br>mixed results. members, who have also denounced  Several sports teams<br>antisemitism. Meanwhile, Kim has  experienced contrasting<br>been open about her experiences, DeSantis is gaining  outcomes in their recent<br>The Kardashian family made a  significant popularity, with  games.<br>statement, with multiple family  some considering a<br>members attending a gala in  presidential run in 2024 a<br>high-end designer outfits. "sure thing," despite former<br>President Donald Trump<br>currently leading in<br>Republican primary polls.<br>(a) Story Spread on Mixed-Reliability News Websites<br>**----- End of picture text -----**<br>

[page 32]

||||**Reliable News**|
|---|---|---|---|
|Keywords|Articles|Websites|Most Prolifc Domains|
|desantis, ron, forida,|62,911|1,330|yahoo.com (5,454), foridapolitics.com (3,098), thehill.com (1,900)|
|gov, governor||||
|quarter, net, revenue, ex-|57,453|824|benzinga.com (19,266), yahoo.com (3,356), marketwatch.com (3,106)|
|pense, loss||||
|half, halftime, minute,|52,362|809|yahoo.com (2,785), espn.com (2,527), rte.ie (2,124)|
|goal, possession||||
|symptom, fever, cough,|42,581|1,241|yahoo.com (1,685), webmd.com (1,023), news-medical.net (869)|
|throat, sore||||
|roe,<br>wade,<br>abortion,|38,358|1,317|news-yahoo.com (2,118), thehill.com (798), cnn.com (615)|
|dobbs, supreme||||
||||**Mixed-Reliability News**|
|Keywords|Articles|Websites|Most Prolifc Domains|
|desantis, ron, forida,|32,723|386|tampafp.com (1,762), theepochtimes.com (1,441), nypost.com (1,220)|
|gov, governor||||
|half, halftime, minute,|21,113|228|the-sun.com (2,402), thesun.co.uk (2,354), independent.co.uk (1,968)|
|goal, possession||||
|kourtney,<br>kardashian,|19,226|117|the-sun.com (7,046), thesun.co.uk (4,951), metro.co.uk (1,028)|
|travis, khloe, barker||||
|ronaldo, cristiano, por-|17,791|126|the-sun.com (3,307), thesun.co.uk (3,024), dailystar.co.uk (1,732)|
|tugal, football, manch-||||
|ester||||
|kardashian, khloe, kim,|16,578|145|the-sun.com (5,603), thesun.co.uk (3,781), metro.co.uk (987)|
|kourtney, jenner||||
||||**Unreliable News**|
|Keywords|Articles|Websites|Most Prolifc Domains|
|desantis, ron, forida,|13,963|328|dailymail.co.uk (2,831), ussanews.com (902), occupydemocrats.com (496)|
|gov, governor||||
|dictatorship, democracy,|9,094|358|abovetopsecret.com (2,549), noqreport.com (384), theburningplatform.com (293)|
|censorship, propaganda,||||
|authoritarian||||
|respect, dignity, equal,|7,950|333|dailymail.co.uk (3,090), abovetopsecret.com (2,183), lifesitenews.com (160)|
|equality, freedom||||
|classifed,<br>document,|7,678|249|dailymail.co.uk (1,393), thegatewaypundit.com (658), survivethenews.com (253)|
|maralago,<br>archive,||||
|wilmington||||
|constitution,<br>oath,|7,655|353|abovetopsecret.com (2,044), dailymail.co.uk (452), theqtree.com (307)|
|amendment,<br>constitu-||||
|tional, defend||||

Table 14: Top Narratives from Different News Sources by Number of Articles in Our Dataset.

[page 33]

## **L Keywords and Auto-Generated Summaries**

|Story.<br>Keywords||
|---|---|
|1<br>transgender, trans, minor,<br>banning, restrict|Auto-Generated Summary<br>Across the United States, anti-trans legislation is on the rise, with multiple states imposing<br>restrictions on transgender individuals, including bans on gender-affrming care for minors,<br>drag shows, and participation in female school sports. At least 20 states have imposed similar<br>limits on trans athletes, and nearly half of all states have laws that make it difficult for<br>transgender youth to receive necessary care. Companies and lawmakers are being urged<br>to take a stance against these laws, which are seen as a personal attack on the LGBTQ+<br>community.<br>Random Sample Passage<br>Contino described how anti-trans legislation has grown across the country, including two<br>bills in Tennessee that ban gender-affrming care for minors as well as drag shows. She says<br>the overarching impact this culture can have on transgender people is huge, and companies<br>need to take a stance.|
|2<br>buckingham, mall, palace,<br>procession, royal|Auto-Generated Summary<br>Large crowds have gathered in London to pay respects to the Queen, with many camping out<br>for days to secure a prime viewing spot for the procession and potentially catch a glimpse of<br>the newlycrowned monarch andQueen Camilla.<br>Random Sample Passage<br>Some 100 heads of state, representatives from 200 countries and hundreds of thousands of<br>visitors are expected to descend on London for the historic event. Many die-hard royal fans<br>are alreadycamped out near Buckingham Palace to secure the best viewingspot.|
|3<br>card, debit, atm, credit,<br>fraudulent|Auto-Generated Summary<br>To protect against credit card theft and unauthorized transactions, it’s essential to keep<br>important documents secure and be aware of potential scams, such as card skimming. Credit<br>card data can also indicate changes in consumer spending habits. However, the use of<br>credit and debit cards has become increasingly popular, with many retailers now accepting<br>these forms of payment. Despite the convenience of these cards, there is still a risk of theft<br>and unauthorized transactions, with some cases involving large-scale data breaches and<br>individuals usingsleight-of-hand techniques to stealgift cards.<br>Random Sample Passage<br>Card skimming involves the use of a device that looks like a normal part of a point-of-sale<br>machine or PIN pad but instead copies EBT card information for the thief. These card<br>skimmer devices are difficult to spot, to the point that retailers may not be aware of their<br>installation.|
