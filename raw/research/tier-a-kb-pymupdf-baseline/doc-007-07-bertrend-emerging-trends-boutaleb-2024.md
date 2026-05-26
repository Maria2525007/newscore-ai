---
id: doc-007
source: 07-bertrend-emerging-trends-boutaleb-2024.pdf
source_type: pdf
source_sha256: e4a8772d111195b345f8018c201253d31d1999e422086f12c5029a115df892b4
extraction_method: pymupdf4llm@unknown
extraction_date: 2026-05-26
pages: 17
headings:
  - "**BERTrend: Neural Topic Modeling for Emerging Trends Detection**"
  - "**Allaa Boutaleb**"
  - "**Abstract**"
  - "**1 Introduction**"
  - "**2 Background**"
  - "**3 BERTrend**"
  - "**3.1 Data Preprocessing and Time-based Document Slicing**"
  - "**3.2 Topic Extraction using BERTopic**"
  - "**Algorithm 1:** BERTrend Algorithm"
  - "**3.3 Topic Merging**"
tokens_estimated: 13998
warnings: []
assets:
  - ../assets/doc-007-page03-img1.png
  - ../assets/doc-007-page03-img2.png
  - ../assets/doc-007-page03-img3.png
  - ../assets/doc-007-page08-img1.png
  - ../assets/doc-007-page09-img1.png
  - ../assets/doc-007-page09-img2.png
  - ../assets/doc-007-page09-img3.png
  - ../assets/doc-007-page09-img4.png
  - ../assets/doc-007-page13-img1.png
  - ../assets/doc-007-page14-img1.png
  - ../assets/doc-007-page15-img1.png
  - ../assets/doc-007-page15-img2.png
  - ../assets/doc-007-page16-img1.png
  - ../assets/doc-007-page16-img2.png
  - ../assets/doc-007-page17-img1.png
---
[page 1]

# **BERTrend: Neural Topic Modeling for Emerging Trends Detection**

## **Allaa Boutaleb**

Sorbonne University | RTE France mohamed_allaa_eddine.boutaleb@etu.sorbonne-universite.fr

**Jérôme Picault** RTE France

**Guillaume Grosjean** RTE France

jerome.picault@rte-france.com guillaume.grosjean@rte-france.com

## **Abstract**

Detecting and tracking emerging trends and weak signals in large, evolving text corpora is vital for applications such as monitoring scientific literature, managing brand reputation, surveilling critical infrastructure and more generally to any kind of text-based event detection. Existing solutions often fail to capture the nuanced context or dynamically track evolving patterns over time. BERTrend, a novel method, addresses these limitations using neural topic modeling in an online setting. It introduces a new metric to quantify topic popularity over time by considering both the number of documents and update frequency. This metric classifies topics as noise, weak, or strong signals, flagging emerging, rapidly growing topics for further investigation. Experimentation on two large real-world datasets demonstrates BERTrend’s ability to accurately detect and track meaningful weak signals while filtering out noise, offering a comprehensive solution for monitoring emerging trends in large-scale, evolving text corpora. The method can also be used for retrospective analysis of past events. In addition, the use of Large Language Models together with BERTrend offers efficient means for the interpretability of trends of events.

## **1 Introduction**

The concept of weak signals, introduced by Ansoff (1975), refers to early indicators of emerging trends that can have significant implications across various domains. These include events like shifts in public opinion in social trends, early disruptive technologies in innovation, changes in activist groups and public sentiment in politics, and potential disease outbreaks in healthcare. Monitoring and analyzing weak signals offers valuable insights for organizations, researchers, and decisionmakers, aiding in informed decision-making.

Key data sources for identifying these trends include large text corpora such as news, social media,

research and technology journals or reports. The challenges are: distinguishing meaningful weak signals from irrelevant noise, dealing with context ambiguity, and tracking the extended period over which weak signals may gain significance.

With advances in NLP and AI, researchers have developed various techniques to detect weak signals across different fields,including statisticsbased methods, graph theory, machine learning, semantic-based approaches, and expert knowledge. However, most solutions fall short in fully addressing the challenge of detecting emerging trends (Rousseau et al., 2021), either by relying solely on keyword-based analysis, which misses contextual nuances, or by being static and unable to dynamically track evolving weak signals.

In this work, we introduce BERTrend, a novel framework for detecting and monitoring emerging trends and weak signals in large, evolving text corpora. BERTrend leverages neural topic modeling, specifically BERTopic, in an online learning setting to identify and track topic evolution over time. Its key contribution lies in dynamically classifying topics as noise, weak signals, or strong signals based on their popularity trends. The proposed metric quantifies topic popularity over time by considering both the number of documents within the topic and its update frequency, incorporating an exponentially growing decay if no updates occur for an extended period. By combining neural topic modeling with a dynamic popularity metric and adaptive classification thresholds, BERTrend provides a comprehensive solution for detecting and monitoring emerging trends in large-scale, evolving text corpora. We discuss the qualitative results on two comprehensive datasets, including the overall evolution of trends and specific case studies. Combined with Large Language Models (LLMs), the method an efficient way of interpreting the detected trends of events through various dimensions indicating how they evolve over time.

[page 2]

## **2 Background**

Among past works about weak signals detection, many are _keyword-based_ . Thus, portfolio maps, pioneered by Yoon (2012), involves constructing keyword emergence maps (KEM) and keyword issue maps (KIM) based on two key metrics: degree of visibility (DoV) that quantifies the frequency of a keyword within a document set; and degree of diffusion (DoD) that measures the document frequency of each keyword. Weak signals are identified as keywords with low frequency but high growth potential. Numerous studies, such as Park and Cho (2017), Donnelly et al. (2019), Lee and Park (2018), Roh and Choi (2020), Yoo and Won (2018), Griol-Barres et al. (2020), have extended and refined this approach with multi-word analysis, signal transformation analysis, and domain-specific applications. However KEMs and KIMs present two major drawbacks: by focusing on keywords only, they can miss the context surrounding a weak signal ; and the output is a single snapshot, which does not gives clear clues of evolution over time.

Topic modeling has emerged as a promising approach for weak signal detection, particularly in large textual datasets. Unlike general topic evolution or drift analysis, which focus on tracking changes in established topics over time, our task aims to identify early indicators of emerging trends. It emphasizes the temporal behavior and growth of small, nascent topics rather than specific content changes within established ones. Thus, Krigsholm and Riekkinen (2019) and Kim et al. (2019) apply text mining and Latent Dirichlet Allocation (LDA) (Blei et al., 2003), to identify future signals in the domain of land administration and policy research databases. Maitre et al. (2019) integrates LDA and Word2Vec to detect weak signals in weakly structured data. El Akrouchi et al. (2021) introduce furthermore two functions for deep filtering: Weakness, which measures the significance, similarity, and evolution of topics using coherence, closeness centrality, and autocorrelation metrics; and Potential Warning, which further filters the terms of the previously filtered topics to identify potential weak signals.

While traditional topic modeling methods like LDA have been useful for weak signal detection, they have notable limitations: it heavily relies on pre-set topic numbers and fails to benefit from the sophisticated, contextual embeddings provided by modern pre-trained models, resulting in less nu-

anced analysis. Additionally, it operates on a static basis, overlooking the crucial temporal dynamics of weak signals. RollingLDA (Rieger et al., 2021, 2022) uses a rolling window for the identification of gradual topic shifts comparing topic distributions across consecutive windows, RollingLDA can detect changes in the prominence of topics over time. The fixed number of topics is a drawback. It is rather used for long-term evolution monitoring rather than detecting weak signals; interpretability of shifts is limited to keyword comparison.

In contrast, our approach leverages dynamic, high-quality contextual embeddings from pretrained models. Our embedding-based technique provides a richer, more adaptive analysis that does not require preset topic counts. This shift from static, keyword-based methods to dynamic, embedding-based analysis allows for a more granular and accurate tracking of the evolution and significance of weak signals over time.

## **3 BERTrend**

In this section, we describe BERTrend (Figure 1), a method for identifying and tracking weak signals in large, evolving text corpora. It focuses on identifying emerging signals at a given moment, rather than tracking long-term topic evolution. It leverages the power of BERTopic (Grootendorst, 2022), a state-of-the-art topic model, and wraps it in an online learning framework. In this setting, new data arrives on a regular basis, allowing BERTrend to capture the dynamic evolution of topics over time. The method employs a set of metrics to characterize these topics as noise, weak signals, or strong signals based on their popularity trends. By combining the strengths of neural topic modeling with a dynamic, incremental learning approach, BERTrend enables the real-time monitoring and analysis of emerging trends and weak signals in vast, continuously growing text datasets.

BERTopic leverages pre-trained large embedding models to generate high-quality contextual embeddings of documents, enabling the discovery of meaningful and coherent topics. It utilizes HDBSCAN (McInnes et al., 2017), a hierarchical density-based clustering algorithm, which is robust to outliers and does not require the number of topics to be specified in advance, allowing the model to automatically determine the optimal number of topics based on the inherent structure of the data.

One of the key advantages of BERTopic is its

[page 3]

**![page 3, image 1](../assets/doc-007-page03-img1.png)**

**----- Start of picture text -----**<br>
Topic<br>JAN 24 FEB 2024 APR 2024<br>Raw<br>documents ... Restore<br>Merge History<br>Preprocessing Unit<br>Time<br>Processed<br>documents<br>Calculate<br>Estimate Thresholds<br>popularities<br>Fit<br>Topic Model ... Increase if topic gets merged popularity Dynamicallypopularity distribution over time  determined based on<br>Decrease  otherwise<br>Extract<br>topics ... Popularity<br>Merge with Strong  signal<br>previous topics Median<br>10 [th] Weak  signal<br>centile<br>Noise<br>Time<br>Monitor respiratory Popularity Zeroshot signals<br>diseases and nuclear More fine-grained monitoring<br>power plants  Zeroshot Zeroshot ... Zeroshot due  to  document-level<br>Expert Detection Detection Detection matching  with  the  topics<br>defined by the expert.<br>Time<br>**----- End of picture text -----**<br>

Figure 1: The BERTrend Framework processes data in time-sliced batches, undergoing preprocessing that includes unicode normalization and paragraph segmentation for very long documents. It applies a BERTopic model to extract topics for each batch, which are merged with prior batches using a similarity threshold to form a cumulative topic set. This data helps track topic popularity over time, identifying strong and weak signals based on dynamically chosen thresholds. Additionally, the framework includes a zero-shot detection feature for targeted topic monitoring, providing more fine-grained results due to document-level matching with topics defined by the expert.

ability to simulate online learning through model merging. Different BERTopic models can be fitted on documents from non-overlapping time periods and then merged together based on the pairwise cosine similarity between topics of consecutive models, enabling a form of dynamic topic modeling in an online learning setting.

## **3.1 Data Preprocessing and Time-based Document Slicing**

To accommodate the maximum token lengths recommended by pretrained embedding models and avoid input truncation, lengthy documents are segmented into paragraphs. Each paragraph is treated as an individual document, with a mapping to its original long document source. This ensures accurate calculation of a topic’s popularity over time by considering the original number of documents rather than the inflated number of paragraphs.We filter out documents that don’t contain at least 100 Latin characters. This threshold was determined by analyzing the corpus of NYT and arXiv after splitting by paragraphs. Documents below this threshold often represent noise (e.g., article endings, incomplete sentences, social media references).

After preprocessing, the entire text corpus _D_ ,

consisting of _N_ documents, is divided into document slices based on a selected time granularity (e.g., daily, weekly, monthly). A document slice _Dt_ is defined as a subset of documents from _D_ that fall within a specific time interval [ _t, t_ + ∆ _t_ ), where _t ∈{t_ 1 _, t_ 2 _, . . . , tM }_ , ∆ _t_ is the chosen time granularity, and _M_ is the total number of document slices. This slicing is crucial for analyzing the temporal dynamics of topics within the corpus.

## **3.2 Topic Extraction using BERTopic**

For each document slice _Dt_ , BERTopic extracts a set of topics _Tt_ = _{τt_[1] _[, τ] t_[ 2] _[, . . . , τ] t[ K][t] }_ , where _Kt_ is the number of topics in _Dt_ . The process involves: 1. _Document Embedding_ : Each document _d ∈ Dt_ is transformed into a dense vector **e** _d ∈_ R _[h]_ using a pre-trained sentence transformer model (Reimers and Gurevych, 2019), where _h_ is the embedding dimension. A topic _τt[j]_[is described as a set] of words _Wτt j_[=] _[{][w] t[j,]_[1] _[, w] t[j,]_[2] _[, . . . , w] t[j,M][j] }_ , where _Mj_ is the number of words representing the topic. 2. _Dimensionality Reduction_ : The embeddings are reduced to a lower-dimensional space using UMAP (McInnes et al., 2018), resulting in reduced embeddings **e** _[′] d[∈]_[R] _[r]_[, where] _[ r][< h]_[.]

3. _Document Clustering_ : The reduced embed-

#### Additional embedded images on page 3

![page 3, image 2 (additional)](../assets/doc-007-page03-img2.png)

![page 3, image 3 (additional)](../assets/doc-007-page03-img3.png)

[page 4]

dings are clustered using HDBSCAN (McInnes et al., 2017), to group semantically similar documents into clusters. Each cluster _Ct[j][∈C][t]_[is asso-] ciated with a centroid embedding **c** _[j] t[∈]_[R] _[r]_[.][These] clusters represent preliminary groupings of documents that will later be labeled as topics.

4. _Cluster Labeling_ : BERTopic assigns labels to clusters to form topics using class-based TF-IDF (cTF-IDF), considering the frequency and specificity of words within each cluster. Various methods, including LLMs, KeyBERT, and Maximal Marginal Relevance (MMR), can be used to refine the representation of topics. In our work, we maintained the default c-TF-IDF representation without employing additional refinement methods. After labeling, each cluster ( _Ct[j]_[)][ becomes a topic][ (] _[τ][ j] t_[)][.]

## **Algorithm 1:** BERTrend Algorithm

|**Algorithm 1:**BERTrend Algorithm|**Algorithm 1:**BERTrend Algorithm|**Algorithm 1:**BERTrend Algorithm|
|---|---|---|
|**Input:** Text corpus_D_, retrospective window size_W_,<br>time granularity_G_, similarity threshold_τ_,<br>decay factor_λ_<br>**Output:** Topics_T_, popularity_p_, signal categories_S_<br>**1** Initialize_T_ =_∅_,_p_=_∅_,_S_ =_∅_;<br>**2** _t_now =current time;<br>**3** _t_start =_t_now_−W_;<br>**4** time slices=slice data(_D, t_start_, t_now_, G_);<br>**5 for**_Dt ∈time slices_**do**|||
|**6**<br>**7**<br>**8**<br>**9**<br>**10**<br>**11**<br>**12**<br>**13**<br>**14**<br>**15**<br>**16**<br>**17**<br>**18**<br>**19**<br>**20**<br>**21**<br>**22**<br>**23**<br>**24**<br>**25**<br>**26**<br>**27**<br>**28**<br>**29**<br>**30**<br>**31**<br>**32**<br>**33**|_Tt_ =BERTopic(_Dt_);<br>**for**_τ j_<br>_t ∈Tt_ **do**<br>simmax = max_τk_<br>_t ∈T_ Similarity_cos_(**c**_j_<br>_t,_**c**_k_<br>_t_ );<br>**if**_simmax ≥τ_ **then**<br>_k∗_= arg max_k_Similarity_cos_(**c**_j_<br>_t,_**c**_k_<br>_t_ );<br>_Dk∗_<br>_t_<br>=_Dk∗_<br>_t_<br>_∪Dj_<br>_t_;<br>_pk∗_<br>_t_<br>=_pk∗_<br>_t−_1 +_|Dj_<br>_t|_;<br>**else**<br>_T_ =_T ∪{τ j_<br>_t }_;<br>_pj_<br>_t_ =_|Dj_<br>_t|_;<br>**for**_τ k_<br>_t ∈T_ **do**<br>**if**_τ k_<br>_t /∈Tt_ **then**<br>_pk_<br>_t_ =_pk_<br>_t−_1 _· e−λ_∆_t_2;<br>**P**all = �<br>_τk∈T {pk_<br>_j | j ∈_[_t −W_ + 1_, t_]_}_;<br>**P**all =sort(**P**all);<br>_P_10 =**P**all[_⌊_0_._1_· |_**P**all_|⌋_];<br>_P_50 =**P**all[_⌊_0_._5_· |_**P**all_|⌋_];<br>**for**_τ k_<br>_t ∈T_ **do**<br>**if**_pk_<br>_t < P_10 **then**<br>_Sk_<br>_t_ ="noise";<br>**else**<br>**if**_P_10 _≤pk_<br>_t ≤P_50 **then**<br>**if**_slope_(_{pk_<br>_j | j ∈_<br>[_t −W_ + 1_, t_]_}_)_>_0**then**<br>_Sk_<br>_t_ ="weak";<br>**else**<br>_Sk_<br>_t_ ="noise";<br>**else**<br>_Sk_<br>_t_ ="strong";||

## **3.3 Topic Merging**

BERTrend merges topics across document slices to capture their evolution. The topic merging process is formalized in Algorithm 1 (lines 10-12). For each time-based document slice _Dt_ +1, the extracted topics _Tt_ +1 are compared with the topics from the previous slice _Tt_ as follows:

1. _Similarity Calculation_ : Compute the cosine similarity between each topic embedding **c** _[j]_ ( _t_ +1) _[∈] Tt_ +1 and all topic embeddings **c** _[k] t[∈T][t]_[.]

2. _Topic Matching_ : If the maximum similarity between **c** _[j]_ ( _t_ +1)[and any] **[ c]** _t[k]_[exceeds a threshold] _[ α]_ (e.g., _α_ = 0 _._ 7), merge the topics and add the documents associated with _τ_ ( _[j] t_ +1)[to] _[ τ][ k] t_[.]

3. _New Topic Creation_ : If the maximum similarity is below _α_ , consider _τ_ ( _[j] t_ +1)[as a new topic and] add it to _Tt_ .

To maintain topic embedding stability, the embedding of the first occurrence of a topic is retained, preventing drift and over-generalization.

## **3.4 Popularity Estimation**

BERTrend estimates topic popularity over time and classifies them into signal categories based on popularity dynamics. The popularity of topic _τt[k]_[for] document slice _Dt_ is denoted as _p[k] t_[and calculated] as follows:

1. _Initial Popularity_ : For a new topic _τt[k]_[of docu-] ment slice _Dt_ , its initial popularity is set to the number of associated documents: _p[k] t_[=] _[|][D] t[k][|]_[,] where _Dt[k]_[is][the][set][of][documents][associated] with _τt[k]_[at time] _[ t]_[.]

2. _Popularity Update_ : For subsequent document slices _Dt′_ ( _t[′] > t_ ):

   - If _τt[k]_[is merged with a topic in] _[ T][t][′]_[, its popu-] larity is incremented by the number of new documents: _p[k] t[′]_[=] _[ p][k] t[′] −_ 1[+] _[ |][D] t[k][′][|]_[.]

   - If _τt[k]_[is not merged with any topic in] _[ T][t][′]_[, its] popularity decays exponentially: _p[k] t[′]_[=] _[ p][k] t[′] −_ 1 _[·] e[−][λ]_[∆] _[t]_[2] , where _λ_ is a constant decay factor (e.g., _λ_ = 0 _._ 01) and ∆ _t_ is the number of days since _τ[k]_ last received an update.

## **3.5 Trend Classification**

To classify topics into signal categories, BERTrend calculates percentiles of popularity values over a rolling window of size _W_ . For each document slice _Dt_ , two empirical thresholds - the 10th percentile ( _P_ 10) and the 50th percentile ( _P_ 50) of popularity values within the window [ _t − W, t_ ] - are computed. Trend classification is performed based on

[page 5]

the topic’s popularity _p[k] t_[and its recent popularity] trend:

- If _p[k] t[< P]_[10][,] _[ τ][ k] t_[is classified as a "noise" signal.]

- • If _P_ 10 _≤ p[k] t[≤][P]_[50][:]

- If the topic’s popularity has been increasing over the past few days, as determined by a positive slope of the linear regression line fitted to the topic’s popularity values within the window [ _t − W, t_ ], _τt[k]_[is][classified][as][a]["weak"] signal.

- If the topic’s popularity has been decreasing, as determined by a negative slope of the linear regression line, _τt[k]_[is classified as a "noise" sig-] nal, as it likely represents a previously popular topic that is losing relevance.

- If _p[k] t[> P]_[50][,] _[ τ][ k] t_[is classified as a "strong" signal.] BERTrend combines popularity trends with

- thresholds to identify emerging trends, distinguishing them from declining popular topics. This helps filter out fading "weak signals" that are actually strong but declining trends.

- Using percentiles calculated dynamically over a

- sliding window offers several advantages:

1. _Adaptability to datasets_ : The retrospective parameter allows the method to adapt to the input data’s velocity and production frequency.

2. _Forget gate mechanism_ : The sliding window avoids the influence of outdated signals on current threshold calculations.

3. _Robustness to outliers_ : Calculating thresholds based on the popularity distribution reduces sensitivity to outlier popularities and prevents thresholds from approaching zero when many signals have faded away.

## **3.6 Targeted Zero-shot Topic Monitoring**

BERTrend includes an optional zero-shot detection feature that allows domain experts to define a set of topics _Z_ = _{z_ 1 _, z_ 2 _, . . . , zL}_ , each represented by a textual description. The embeddings of these topics and the documents in each slice _Dt_ are calculated using the same embedding model. For each document _d ∈ Dt_ , the cosine similarity between its embedding **e** _d_ and the embedding of each defined topic _zl_ is computed. Documents with a similarity score above a predefined low threshold _β_ (typically 0.4-0.6) for any of the defined topics are considered relevant and included in the corresponding topic’s document set _Dt[z][l]_[.][The][low][threshold][ac-] counts for the presumed vagueness and generality of the expert-defined topics, as they have incomplete knowledge that would be supplemented by

new emerging information. Finally, the popularity and trend classification for the zero-shot topics are performed in the same manner as for the automatically extracted topics, using the document sets _Dt[z][l]_ instead of _Dt[k]_[.]

## **4 Experimental Setup**

## **4.1 Datasets**

We selected two diverse datasets for our evaluation: the arXiv dataset, comprising scientific paper abstracts from the computer science category (cs.*) (Cornell-University, 2023), and the New York Times (NYT) news dataset (Singh, 2023). Our choice aligns with recommendations from Rousseau et al. (2021) and Yoon (2012), who advocate for the use of scientific articles and news sources in weak signal detection due to their rich, evolving content. The arXiv dataset spans from January 2017 to December 2023, encompassing 367,248 abstracts, while the NYT dataset covers the period from January 2019 to January 2023, including 184,811 articles. These corpora offer a wealth of interpretable topics, facilitating qualitative analysis and interpretation. Moreover, the NYT dataset has been previously employed in weak signal detection research (El Akrouchi et al., 2021), further substantiating its relevance to our study. These datasets were chosen for their diverse content and potential to contain topics that could be considered weak signals, such as early warnings about the COVID-19 pandemic.

## **4.2 Algorithm parameters**

In our experiments, we used the BERTopic framework with carefully selected hyperparameters to optimize weak signal detection performance. We chose the "all-mpnet-base-v2"[1] sentence transformer for document embedding because of its strong performance on various natural language understanding tasks (Reimers and Gurevych, 2019).

In the UMAP dimensionality reduction step, the number of components is set to 5 (default value), and the number of neighbors to 15, which allows UMAP to balance local and global structure in the data, as lower values focus more on local structure while higher values emphasize broader patterns (McInnes et al., 2018). In the HDBSCAN clustering step, we set the minimum cluster size to 2, the smallest possible value, to detect fine-grained

1https://huggingface.co/sentence-transformers/ all-mpnet-base-v2

[page 6]

clusters. The minimum sample size was set to 1, the smallest possible value, to reduce the likelihood of points being declared as noise, as the high number of clusters obtained reduces the need for conservative clustering (McInnes et al., 2017).

Topics were represented by top unigrams and bigrams based on their c-TF-IDF scores. To determine the optimal minimum similarity threshold for merging topics across time slices, we conducted an ablation study varying the threshold from 0.5 to 0.95. We observed that lower thresholds (0.5-0.6) led to overly broad signals and unstable behavior, characterized by a phenomenon we term "threshold collapse." In this scenario, the disproportionate merging of topics results in a few dominant signals that skew the distribution of popularity values. Consequently, the dynamically determined classification thresholds (Q1 and Q3) become volatile, potentially shifting dramatically between consecutive timestamps. This instability compromises the reliability of signal categorization.

Conversely, higher thresholds (0.8-0.95) resulted in an overabundance of micro-signals, hindering the detection of meaningful trends. A threshold of 0.7 was found to provide a balanced approach, ensuring coherence and consistency of detected topics while allowing for semantic evolution without inducing threshold instability.

We also investigated the effect of the retrospective window size, varying it from 2 to 30 days. We found that its impact on BERTrend’s performance was minimal when using an appropriate merge similarity threshold. The choice of window size primarily depends on the desired amount of historical data to incorporate in threshold calculations, with larger windows providing more stable, but potentially less responsive, threshold determinations.

For the granularity of the time slices, we chose 2 and 7 days for the NYT News and arXiv datasets respectively, based on our analysis of topic evolution rates in these datasets. This selection accommodates the rapidly evolving nature of news compared to the slower pace of research papers, while maintaining a balance between signal detection sensitivity and computational efficiency.

It is important to note that these parameter choices have been fine-tuned based on the characteristics of the datasets used in this study. For datasets with significantly different topic evolution dynamics and update frequencies, these parameters may require adjustment to achieve optimal performance.

In the zero-shot example (subsection 5.4), we used a lower similarity threshold of 0.45 for merging topics to accommodate the vague and incomplete nature of the user-defined topics, allowing for a more flexible merging process. This approach maximizes the recall in detecting potentially relevant documents of weak signals.

## **5 Results**

Quantitative results about weak signal analysis are very challenging to obtain due to the lack of established metrics and methodology as detailed in section 9.3. Therefore, as in many past works in this research area (e.g. (El Akrouchi et al., 2021), we focus on a qualitative analysis, including retrospective analysis of known outcomes, to highlight its effectiveness and potential applications.

## **5.1 Overall results**

Figure 2 illustrates the evolution of signal type counts and topic counts in the NYT News dataset and the arXiv cs.* papers dataset We observe striking differences in the signal type distributions between these datasets, which can be attributed to the very nature of their respective domains.

In the NYT News dataset, the number of weak signals remains relatively stable over time, with a manageable quantity of 10 to 20 signals every 2 days. This is well-suited for real-time monitoring and trend detection in fast-paced news cycles, where emerging signals quickly evolve into hot topics of discussion. The occasional spikes in strong signals likely correspond to major events or trending news stories that capture significant attention.

Conversely, the arXiv cs.* papers dataset exhibits a consistently higher number of weak signals, reflecting the diverse range of emerging research topics in the computer science domain. The number of strong signals is comparatively lower, as only a subset of novel ideas and approaches eventually gain traction and become widely adopted. This aligns with the nature of scientific research, where numerous proposals emerge, but only a few ultimately make a significant impact.

Interestingly, while the number of topics per time slice in the NYT News dataset fluctuates but remains overall stable, the arXiv cs.* papers dataset shows an increasing trend in the number of topics detected per 7-day interval. This can be attributed to the exponential growth of research papers in recent years, leading to a more diverse and rapidly

[page 7]

**==> picture [455 x 145] intentionally omitted <==**

**----- Start of picture text -----**<br>
NYT News | Jan 2019 to Jan 2023 arXiv cs.* papers | Jan 2017 to Dec 2023 8000<br>160140120 Number of Noise Signals Number of Weak SignalsNumber of Strong Signals Number of Topics Number of Topics after merging 100008000 14001200 Number of Noise SignalsNumber of Weak Signals Number of Strong Signals Number of TopicsNumber of Topics after merging 70006000<br>100 1000 5000<br>6000<br>800<br>80 4000<br>60 4000 600 3000<br>400<br>40 2000<br>2000<br>20 200 1000<br>0 0 0<br>2019-01 2019-07 2020-01 2020-07 2021-01 2021-07 2022-01 2022-07 2023-01 2017 2018 2019 2020 2021 2022 2023 2024<br>(a) NYT News dataset (b) arXiv cs.* dataset<br>Count Count<br>Count After Merging Count After Merging<br>**----- End of picture text -----**<br>

Figure 2: Evolution of Signal Types and Topic Counts in the NYT News and arXiv cs.* Datasets

evolving research landscape. The total number of topics after merging (blue line) steadily increases over time in both datasets, reflecting the accumulation of new topics as the datasets grow.

## **5.2 Case study**

In this section, we conduct a qualitative analysis of the results. We focus on a subset of illustrative topics and zoom into key periods to observe their behavior more closely. The examples are selected for their ease for interpretation.

Figure 3a focuses on the period from 01/2020 to 02/2020, when news media began reporting on the COVID-19 outbreak. We observe the appearance of a new topic (blue signal), due to its dissimilarity with pre-existing topics. Initially, the blue signal is classified as weak because of the low number of articles discussing it. Shortly after, it gains traction, transitioning from a weak to a strong signal within a matter of days, as evidenced by its exponential rise in popularity on the log-scaled y-axis. Concurrently, other strong signals during this period include topics related to the impeachment trial of President Trump (orange signal) and the Taal Volcano eruption (Philippines) in Jan 2020 (green signal), while a topic discussing American football teams (red signal) is classified as noise.

In Figure 3b, we showcase the evolution of three selected topics from the arXiv cs.* papers dataset from 06/2017 to 10/2019. The blue signal, representing attention models, was initially a weak signal before June 2017, as attention methods were being used in conjunction with recurrent networks. However, the introduction of the transformer architecture (Vaswani et al., 2017) in June 2017 marked a turning point, after which the topic quickly gained traction, transitioning into a strong signal and eventually becoming a mega-trend. This rise of trans-

formers largely replaced RNNs (Rumelhart et al., 1986) and LSTMs (Hochreiter and Schmidhuber, 1997) (green signal) in NLP tasks, leading to a decline in the popularity of the green signal. In contrast, papers related to computer vision, especially those mentioning ImageNet (Deng et al., 2009), a widely-used dataset in computer vision, were classified as strong signals in June 2017 and continued to exhibit growth. This analysis demonstrates our method’s ability to identify potentially impactful research topics early on, track their evolution, and capture the dynamics between related topics.

## **5.3 Impact of zero-shot Topic Modeling**

Figure 4 illustrates the impact of incorporating zeroshot topic modeling in the BERTrend algorithm. In this approach, an expert defines a general topic of interest, and each document from a slice is compared against this topic using embedding similarity. Documents that surpass a certain similarity threshold are captured, allowing for targeted weak signal detection. This method enables experts to focus on specific topics of interest while offering higher precision and sensitivity in weak signal detection. By performing document-level comparisons using embeddings, the zero-shot approach minimizes the risk of missing relevant documents during the topic modeling pipeline.

In the provided example, we chose the generic zero-shot topic "Diseases, Outbreaks, Illnesses, Viruses," to detect the COVID-19 signal, simulating a scenario where an expert has a general idea of what to monitor but lacks precise knowledge of an impending outbreak. Remarkably, the zero-shot method identified the earliest article in the dataset mentioning the coronavirus pandemic on January 6th, 2020, referring to it as a "pneumonia-like mysterious virus" along-

[page 8]

**![page 8, image 1](../assets/doc-007-page08-img1.png)**

**----- Start of picture text -----**<br>
10 [3] NYT News (2020) | 01-15 to 02-15 | Arrow Timestamp: 2020-01-18 ArXiv cs.* | 2017-06 to 2019-10 | Arrow Timestamp: 2017-06-10<br>10 [2] Lower threshold: 0.09Upper threshold: 3.96 Signal StrengthStrong SignalsWeak Signals 10 [3] Lower threshold: 3.00 Upper threshold: 19.80<br>10 [1] 18.747.82 Noise 10 [2] 130.88<br>3.00<br>10 [0] 10 [1] 18.79<br>10 1 3.76<br>0.05 10 [0]<br>10 2 Topics<br>virus china - coronavirus - virus - state infected Topics<br>10 3 testify senate - impeachment proceedings - impeachment trial - impeachmenttaal volcano - volcano - mammoth eruption - earthquakes 10 1 attention models - attention network - neural transformer - attention based deep neural - imagenet datasets - 10 imagenet - imagenet<br>released coach - philadelphia eagles - pat shurmur - giants lstm - rnns - rnn - rnn architectures<br>10 4 10 2<br>2020-01-17 2020-01-21 2020-01-25 2020-01-292020-02-01 2020-02-05 2020-02-09 2020-02-13 2017-07 2017-10 2018-01 2018-04 2018-07 2018-10 2019-01 2019-04 2019-07 2019-10<br>Timestamp Timestamp<br>(a) NYT News dataset (b) arXiv cs.* papers<br>Figure 3: Log-scaled popularity of selected topics from (a) the NYT News dataset and (b) arXiv cs.* papers.<br>10 [3] NYT News - Coronavirus Signal | 2019-11-14 to 2020-03-01 6 Interpretation of trends with LLMs<br>Lower threshold: 0.08<br>Upper threshold: 3.80<br>Current timestamp: 2020-01-18<br>10 [2] Topic modeling methods often output topics as sets<br>10 [1] 3.74 | 36 Days Before 3.22 | 12 Days Before of keywords, which can be difficult to interpret and<br>1.9 8  | 58 Days Before may not fully capture the semantic meaning of the<br>10 [0] topic (Rijcken et al., 2023; Rüdiger et al., 2022).Rijcken et al., 2023; Rüdiger et al., 2022)., 2023; Rüdiger et al., 2022). 2023; Rüdiger et al., 2022).; Rüdiger et al., 2022). Rüdiger et al., 2022)., 2022). 2022).).<br>10 1 Signal StrengthStrong Signals Topics LLMs can be leveraged to enhance the interpre-<br>Weak Signals BERTrend tation of signals detected by BERTrend and of their<br>Noise BERTrend w/ 0-shot<br>102019-11-152 2019-12-01 2019-12-15 2020-01-01 2020-01-15 2020-02-01 2020-02-15 2020-03-01 evolution over time. Although this field of topic<br>Timestamp<br>Popularity (Log Scale) Popularity (Log Scale)<br>Popularity (Log Scale)<br>**----- End of picture text -----**<br>

Topic modeling methods often output topics as sets of keywords, which can be difficult to interpret and may not fully capture the semantic meaning of the topic (Rijcken et al., 2023; Rüdiger et al., 2022).Rijcken et al., 2023; Rüdiger et al., 2022)., 2023; Rüdiger et al., 2022). 2023; Rüdiger et al., 2022).; Rüdiger et al., 2022). Rüdiger et al., 2022)., 2022). 2022).).

LLMs can be leveraged to enhance the interpretation of signals detected by BERTrend and of their evolution over time. Although this field of topic analysis through LLMs is new, it is quite promising (Kirilenko and Stepchenkova, 2024).

**==> picture [220 x 92] intentionally omitted <==**

In this work, we go several steps further by using LLMs not only for having human-readable descriptions of topics, but also useful insights about their evolution between two timestamps, such a summary of the key developments of the event signal since previous timestamp, as well as novelty about the signal w.r.t. previous time period. In addition, we use the LLM to obtain an in-depth analysis of the signal, including: (1) impact, i.e. potential effects of this signal on various sectors, industries, and societal aspects, with both short-term and longterm implications; (2) evolution scenarios - both optimistic and pessimistic scenarios; (3) potential interactions /conflicts with other current trends; (4) drivers and inhibitors (factors/barriers related to the development of the signal. The associated prompt templates are provided in section A.2.

Figure 4: Comparison of COVID-19 Signal Detection with and without zero-shot Topic Modeling

side "coronavirus". This detection occurred 12 days before the automatic BERTrend usage without zero-shot. Furthermore, the zero-shot approach captured potential weak signals even earlier, such as a November 2019 article reporting school closures in Colorado due to a virus outbreak. While these signals may or may not be directly related to the pandemic, they demonstrate the method’s ability to identify potentially relevant events. The consistency of the signal’s growth is also notable. The automatically detected signal (blue) by BERTrend starts to decrease and becomes less stable around March 2020, not due to a loss in popularity, but because other signals discussing slightly different aspects of the pandemic begin to emerge.

In the example of Figure 5, we use the GPT-4o model[2] with a temperature of 0.1 to generate insightful summaries and highlight new information at each timestamp for a weak signal related to the new Bluetongue viral disease (Catarrhal fever) affecting ruminants that appeared in France in July 2024. This example was selected for its recency to ensure it lies beyond the LLM’s training data, minimizing the risk of analysis bias from the model’s

> 2https://platform.openai.com/docs/models/ gpt-4o

[page 9]

**![page 9, image 1](../assets/doc-007-page09-img1.png)**

Figure 5: Enhancing Signal Interpretation and Analysis using LLMs

## pre-existing knowledge..

By emphasizing new information at each timestamp through a multi-faceted description, the LLM helps to pinpoint key developments and changes within the topic. It provides a comprehensive summary of the signal’s evolution, which can then be reintroduced to the LLM for further analysis, assessing its potential impact and possible outcomes.

## **7 Conclusion**

In this paper, we introduced BERTrend, a novel framework for detecting and monitoring weak signals in large, evolving text corpora. BERTrend models the trends of topics over time and classifies them as weak signals, strong signals, or noise based on their popularity metric. The classification is performed using empirically chosen thresholds based on the distribution of topic popularities over a sliding window. The other contributions of this work include: (1) an extensive evaluation on two real-

world datasets that demonstrate the effectiveness of our approach; (2) proposals to leverage LLMs to enhance the interpretation of topic evolution.

We are currently exploring LLM-generated evolving knowledge graphs as a structured method for interpreting signals. These graphs monitor topic evolution by tracking the appearance and disappearance of entities and relationships. Future work will involve exploring new datasets, integrating live data, and developing metrics to compare weak signal detection methods.

## **8 Software availability**

In order to foster collaboration and advancement in weak signal detection, the code of BERTrend (and associated tools for visualization and LLMbased interpretation) has been open-sourced. It is available at the following URL:

https://github.com/rte-france/BERTrend.

#### Additional embedded images on page 9

![page 9, image 2 (additional)](../assets/doc-007-page09-img2.png)

![page 9, image 3 (additional)](../assets/doc-007-page09-img3.png)

![page 9, image 4 (additional)](../assets/doc-007-page09-img4.png)

[page 10]

## **9 Limitations**

## **9.1 Hyperparameter Sensitivity**

BERTrend’s performance is sensitive to various hyperparameters, including BERTopic parameters, merge threshold, granularity, and retrospective period. We chose BERTopic hyperparameters to produce the most fine-grained topics since larger topics will hinder the early detection process, and weak signals will get lost as the documents that should form them are assigned either to noise topics or other large, more generalized topics. To mitigate the variability of topic embeddings due to the small number of documents per topic, we selected a low merge threshold (0.6-0.7). Granularity depends on the amount of data available per time unit and the frequency of new documents. The retrospective period affects the influence of past signals on current thresholds; we found that a period of a week to a month doesn’t change thresholds significantly, but bigger changes can affect classification results. Empirically fixed thresholds (10th percentile and median) balance precision and recall.

## **9.2 Distinguishing Between Weak Signals and Noise**

There remains the challenge of distinguishing between what’s considered a weak signal and what’s considered noise. Relying on temporal popularity fluctuations alone isn’t ideal, as both weak and noise signals behave very similarly. There’s also the issue of characterizing what would be a "weak signal," since that changes from one person to another, one domain to another, etc. This is why we added the zero-shot detection to help an expert guide the detection process. We envision exploring the effect of using named entity recognition for better filtering in future work.

## **9.3 Evaluation Challenges**

Evaluating the effectiveness of our weak signal detection method is challenging due to many factors:

- the subjective nature of what constitutes a weak signal, since it depends on the context, the domain, and the specific goals of the analysis, making it difficult to raise a consensus even among domain experts.

- the lack of ground truth data: unlike many other natural language processing tasks, there are no widely accepted benchmark datasets or ground truth annotations specifically designed for evaluating weak signal detection. This lack of stan-

dardized benchmarks hinders the ability to objectively compare different approaches and quantify their performance.

- dynamics over time: weak signals are often transient and can grow or dissipate over time. This dynamic nature complicates the evaluation process, as the ground truth itself may change, requiring continuous monitoring and updating of the evaluation data.

To the best of our knowledge, there are currently no established metrics for comparing weak signal detection performance within large volumes of data. Traditional metrics used in evaluating topic models, such as topic coherence topic diversity, and perplexity, are not suitable for assessing weak signal detection. These metrics measure the quality and interpretability of topics over time, but they cannot determine whether a detected signal is truly a weak signal of emerging importance. Given this context, comparing BERTrend with dynamic topic models or other embedding techniques (as described in Balepur et al. (2023), Churchill and Singh (2022), Rudolph and Blei (2018), Yao et al. (2018), Meng et al. (2020), or Xu et al. (2023)) using these metrics would not provide meaningful insights into the nature of the weak signals detected. These methods and their evaluation metrics are designed for different objectives, primarily assessing topic quality and evolution over extended periods of time.

Comparing BERTrend with existing keywordbased approaches (e.g., Park and Cho (2017); Donnelly et al. (2019); Griol-Barres et al. (2020)) is not feasible due to fundamental differences in methodology and output: (1) These methods primarily use Degree of Visibility and Degree of Diffusion metrics on keyword emergence maps and keyword issue maps. Their output is a set of words indicating the presence of a weak signal, whereas BERTrend produces topic sequences over time. (2) BERTrend’s dynamic, embedding-based approach captures contextual nuances that keyword-based methods often miss. As noted by Rousseau et al. (2021), "the use of a single keyword may lead to a loss of objectivity" and "the lack of relations and context over the keywords limit the information."

To address the evaluation challenge, our future work will center on a large-scale user study involving domain experts. These experts will review BERTrend’s outputs at specific time instants, identifying potential weak signals in their fields.

[page 11]

## **References**

- H Igor Ansoff. 1975. Managing strategic surprise by response to weak signals. _California management review_ , 18(2):21–33.

- Nishant Balepur, Shivam Agarwal, Karthik Venkat Ramanan, Susik Yoon, Diyi Yang, and Jiawei Han. 2023. DynaMiTE: Discovering explosive topic evolutions with user guidance. In _Findings of the Association for Computational Linguistics: ACL 2023_ , pages 194– 217, Toronto, Canada. Association for Computational Linguistics.

- David M. Blei, Andrew Y. Ng, and Michael I. Jordan. 2003. Latent dirichlet allocation. _Journal of Machine Learning Research_ , 3:993–1022.

- Rob Churchill and Lisa Singh. 2022. Dynamic topicnoise models for social media. In _Advances in Knowledge Discovery and Data Mining: 26th Pacific-Asia Conference, PAKDD 2022, Chengdu, China, May 16–19, 2022, Proceedings, Part II_ , page 429–443, Berlin, Heidelberg. Springer-Verlag.

- Cornell-University. 2023. arxiv dataset. Accessed: 2024-06-14.

- Jia Deng, Wei Dong, Richard Socher, Li-Jia Li, Kai Li, and Li Fei-Fei. 2009. Imagenet: A large-scale hierarchical image database. In _2009 IEEE conference on computer vision and pattern recognition_ , pages 248–255. Ieee.

- Hayoung Kim Donnelly, Yoonsun Han, Juyoung Song, and Tae Min Song. 2019. Application of social big data to identify trends of school bullying forms in south korea. _International journal of environmental research and public health_ , 16(14):2596.

- Manal El Akrouchi, Houda Benbrahim, and Ismail Kassou. 2021. End-to-end lda-based automatic weak signal detection in web news. _Knowledge-Based Systems_ , 212:106650.

- Israel Griol-Barres, Sergio Milla, Antonio Cebrián, Huaan Fan, and Jose Millet. 2020. Detecting weak signals of the future: A system implementation based on text mining and natural language processing. _Sustainability_ , 12(19):7848.

- Maarten Grootendorst. 2022. Bertopic: Neural topic modeling with a class-based tf-idf procedure. _arXiv preprint arXiv:2203.05794_ .

- Sepp Hochreiter and Jürgen Schmidhuber. 1997. Long short-term memory. _Neural computation_ , 9(8):1735– 1780.

- Hyunuk Kim, Sang-Jin Ahn, and Woo-Sung Jung. 2019. Horizon scanning in policy research database with a probabilistic topic model. _Technological Forecasting and Social Change_ , 146:588–594.

- Andrei Kirilenko and Svetlana Stepchenkova. 2024. Automated topic analysis with large language models. In _Information and Communication Technologies in_

_Tourism 2024_ , pages 29–34, Cham. Springer Nature Switzerland.

- Pauliina Krigsholm and Kirsikka Riekkinen. 2019. Applying text mining for identifying future signals of land administration.

- Young-Joo Lee and Ji-Young Park. 2018. Identification of future signal based on the quantitative and qualitative text mining: a case study on ethical issues in artificial intelligence. _Quality & Quantity_ , 52(2):653–667.

- Julien Maitre, Michel Menard, Guillaume Chiron, and Alain Bouju. 2019. Détection de signaux faibles dans des masses de données faiblement structurées. _Recherche d’Information, Document et Web Sémantique_ , 3(1).

- Leland McInnes, John Healy, Steve Astels, et al. 2017. hdbscan: Hierarchical density based clustering. _J. Open Source Softw._ , 2(11):205.

- Leland McInnes, John Healy, and James Melville. 2018. Umap: Uniform manifold approximation and projection for dimension reduction. _arXiv preprint arXiv:1802.03426_ .

- Yu Meng, Jiaxin Huang, Guangyuan Wang, Zihan Wang, Chao Zhang, Yu Zhang, and Jiawei Han. 2020. Discriminative topic mining via category-name guided text embedding. In _Proceedings of The Web Conference 2020_ , WWW ’20, page 2121–2132, New York, NY, USA. Association for Computing Machinery.

- Chankook Park and Seunghyun Cho. 2017. Future sign detection in smart grids through text mining. _Energy Procedia_ , 128:79–85.

- Nils Reimers and Iryna Gurevych. 2019. Sentence-bert: Sentence embeddings using siamese bert-networks. _arXiv preprint arXiv:1908.10084_ .

- Jonas Rieger, Carsten Jentsch, and Jörg Rahnenführer. 2021. RollingLDA: An update algorithm of Latent Dirichlet Allocation to construct consistent time series from textual data. In _Findings of the Association for Computational Linguistics: EMNLP 2021_ , pages 2337–2347, Punta Cana, Dominican Republic. Association for Computational Linguistics.

- Jonas Rieger, Kai-Robin Lange, Jonathan Flossdorf, and Carsten Jentsch. 2022. Dynamic change detection in topics based on rolling ldas. In _Proceedings of Text2Story - Fifth Workshop on Narrative Extraction From Texts held in conjunction with the 44th European Conference on Information Retrieval (ECIR 2022), Stavanger, Norway, April 10, 2022_ , volume 3117 of _CEUR Workshop Proceedings_ , pages 5–13. CEUR-WS.org.

- Emil Rijcken, Floortje Scheepers, Kalliopi Zervanou, Marco Spruit, Pablo Mosteiro, and Uzay Kaymak. 2023. Towards interpreting topic models with chatgpt. In _The 20th World Congress of the International Fuzzy Systems Association_ .

[page 12]

- Seungkook Roh and Jae Young Choi. 2020. Exploring signals for a nuclear future using social big data. _Sustainability_ , 12(14):5563.

- Pauline Rousseau, Daniel Camara, and Dimitris Kotzinos. 2021. Weak signal detection and identification in large data sets: a review of methods and applications.

- Matthias Rüdiger, David Antons, Amol M Joshi, and Torsten-Oliver Salge. 2022. Topic modeling revisited: New evidence on algorithm performance and quality metrics. _Plos one_ , 17(4):e0266325.

- Maja Rudolph and David Blei. 2018. Dynamic embeddings for language evolution. In _Proceedings of the 2018 World Wide Web Conference_ , WWW ’18, page 1003–1011, Republic and Canton of Geneva, CHE. International World Wide Web Conferences Steering Committee.

- David E Rumelhart, Geoffrey E Hinton, and Ronald J Williams. 1986. Learning internal representations by error propagation, parallel distributed processing, explorations in the microstructure of cognition, ed. de rumelhart and j. mcclelland. vol. 1. 1986. _Biometrika_ , 71:599–607.

into different types of signals, as well as using a LLM to interpret and analyze certain signals. The UI is built using Streamlit[3] , and all the visualizations are done using the Plotly library[4] .

## **A.2 Prompt examples for topic evolution analysis**

This section gives some examples of the prompts we are using with a LLM (GPT-4o) to obtain detailed insights of topic evolution between two timestamps.

## **A.2.1 Prompt for evolving topic summary at a given timestamp**

As an expert analyst specializing in trend analysis and strategic foresight, your task is to provide a comprehensive evolution summary of Topic {topic_number}. Use only the information provided below:

{content_summary}

Structure your analysis as follows:

For the first timestamp:

- Aryan Singh. 2023. Nyt articles (21m+) 2000-present. Accessed: 2024-06-14.

- Ashish Vaswani, Noam Shazeer, Niki Parmar, Jakob Uszkoreit, Llion Jones, Aidan N Gomez, Łukasz Kaiser, and Illia Polosukhin. 2017. Attention is all you need. _Advances in neural information processing systems_ , 30.

- Weijie Xu, Wenxiang Hu, Fanyou Wu, and Srinivasan H. Sengamedu. 2023. Detime: Diffusion-enhanced topic modeling using encoder-decoder based llm. _ArXiv_ , abs/2310.15296.

- Zijun Yao, Yifan Sun, Weicong Ding, Nikhil Rao, and Hui Xiong. 2018. Dynamic word embeddings for evolving semantic discovery. In _Proceedings of the Eleventh ACM International Conference on Web Search and Data Mining_ , WSDM ’18, page 673–681, New York, NY, USA. Association for Computing Machinery.

- Sun Hi Yoo and DongKyu Won. 2018. Simulation of weak signals of nanotechnology innovation in complex system. _Sustainability_ , 10(2):486.

- Janghyeok Yoon. 2012. Detecting weak signals for long-term business opportunities using text mining of web news. _Expert Systems with Applications_ , 39(16):12543–12550.

## **A Software**

## **A.1 Some screenshots**

We present in this section some screenshots (Figures 6–12) of our prototype which utilizes BERTrend to explore trends and categorize them

## [Concise yet impactful title capturing the essence of the topic at this point]

### Date: [Relevant date or time frame]

### Key Developments

- [Bullet point summarizing a major development or trend]

- [Additional bullet points as needed]

### Analysis

[2-3 sentences providing deeper insights into the developments, their potential implications, and their significance in the broader context of the topic's evolution]

For all subsequent timestamps:

## [Concise yet impactful title capturing the essence of the topic at this point]

### Date: [Relevant date or time frame] ### Key Developments

- [Bullet point summarizing a major development

- or trend]

- [Additional bullet points as needed]

## ### Analysis

[2-3 sentences providing deeper insights into the developments, their potential implications, and their significance in the broader context of the topic's evolution]

## ### What's New

[1-2 sentences highlighting how this period differs from the previous one, focusing on new elements or significant changes]

Provide your analysis using only this format, based solely on the information given. Do not include any

3https://streamlit.io/

4https://plotly.com/

[page 13]

**![page 13, image 1](../assets/doc-007-page13-img1.png)**

Figure 6: The BERTrend main interface allows users to configure various hyperparameters, including those for BERTopic components and merging thresholds. Users can load and filter data, split text into paragraphs, select specific timeframes, and randomly sample the data. The interface also facilitates the embedding of documents for further analysis.

additional summary or overview sections beyond what is specified in this structure.

existing systems or paradigms.

4. Drivers and Inhibitors:

## **A.2.2 Prompt for signal analysis**

As an elite strategic foresight analyst with extensive expertise across multiple domains and industries, your task is to conduct a comprehensive evaluation of a potential signal derived from the following topic summary:

{summary_from_first_prompt}

Leverage your knowledge and analytical skills to provide an in-depth analysis of this signal's potential impact and evolution:

- Analyze factors that could accelerate or amplify

- this signal.

- Examine potential barriers or resistances that

- might hinder its development.

Your analysis should be thorough and nuanced, going beyond surface-level observations. Draw upon your expertise to provide insights that capture the complexity and potential significance of this signal. Don't hesitate to make well-reasoned predictions about its potential trajectory and impact.

Focus on providing a clear, insightful, and actionable analysis that can inform strategic decision-making and future planning.

1. Potential Impact Analysis:

   - Examine the potential effects of this signal

   - on various sectors, industries, and societal aspects.

   - Consider both short-term and long-term

   - implications.

   - Analyze possible ripple effects and

   - second-order consequences.

2. Evolution Scenarios:

   - Describe potential ways this signal could

   - develop or manifest in the future.

   - Consider various factors that could influence

   - its trajectory. - Explore both optimistic and pessimistic scenarios.

3. Interconnections and Synergies: - Identify how this signal might interact with other current trends or emerging phenomena. - Discuss potential synergies or conflicts with

[page 14]

**![page 14, image 1](../assets/doc-007-page14-img1.png)**

Figure 7: The model training interface enables the creation and merging of multiple BERTopic models based on the selected granularity and merging thresholds. Users can also define zero-shot topics for detection at each timestamp, providing a flexible approach to model training.

[page 15]

**![page 15, image 1](../assets/doc-007-page15-img1.png)**

Figure 8: The results page showcases zero-shot topics, allowing experts to visually inspect them with ease. A searchable dataframe accompanies the visualization, enabling users to explore documents related to defined zero-shot topics across various timestamps.

**![page 15, image 2](../assets/doc-007-page15-img2.png)**

Figure 9: The core functionality of BERTrend: users can define a retrospective period and select specific dates to investigate historical data, determining what was classified as noise, weak signals, or strong signals during that timeframe.

[page 16]

**![page 16, image 1](../assets/doc-007-page16-img1.png)**

Figure 10: For each selected date, corresponding dataframes classify topics based on their popularity, categorizing them as noise, weak signals, or strong signals. Users can easily retrieve and further analyze a topic by its identifier, as demonstrated with topic number 108.

**![page 16, image 2](../assets/doc-007-page16-img2.png)**

Figure 11: Upon selecting a topic identifier, an LLM generates a comprehensive analysis of the topic’s evolution and its various aspects, presented in a detailed report for further examination.

[page 17]

**![page 17, image 1](../assets/doc-007-page17-img1.png)**

Figure 12: The topic merging process is visualized using a Sankey Diagram, providing a clear and intuitive representation of how topics were combined over time.
