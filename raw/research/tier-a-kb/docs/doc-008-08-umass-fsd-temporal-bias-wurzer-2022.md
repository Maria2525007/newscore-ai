---
id: doc-008
source: 08-umass-fsd-temporal-bias-wurzer-2022.pdf
source_type: pdf
source_sha256: 0d3d944bd3e2ae01898c5349400bfb88859fd4e2111b0528218ba3050a5ec52a
extraction_method: mineru-vlm@3.2.0
extraction_date: 2026-05-26
pages: 4
headings:
  - How UMass-FSD Inadvertently Leverages Temporal Bias
  - ABSTRACT
  - KEYWORDS
  - "ACM Reference Format:"
  - 1 INTRODUCTION
  - "Contributions:"
  - 2 RELATED WORK
  - 3 TEMPORAL BIAS THROUGH INCREMENTAL TERM STATISTICS
  - 3.1 Incremental IDF Over Time
  - 3.2 Analyzing the Effect of Omitting Length Updates
tokens_estimated: 6256
warnings: []
assets: [../assets/doc-008-page02-img1.jpeg, ../assets/doc-008-page04-img1.jpeg, ../assets/doc-008-page04-img2.jpeg]
---
#

[page 1]

How UMass-FSD Inadvertently Leverages Temporal Bias

Dominik Wurzer

School of Information Management

Wuhan University, China

wurzer.dominik@whu.edu.cn

# ABSTRACT

First Story Detection describes the task of identifying new events in a stream of documents. The UMass-FSD system is known for its strong performance in First Story Detection competitions. Recently, it has been frequently used as a high accuracy baseline in research publications. We are the first to discover that UMass-FSD inadvertently leverages temporal bias. Interestingly, the discovered bias contrasts previously known biases and performs significantly better. Our analysis reveals an increased contribution of temporally distant documents, resulting from an unusual way of handling incremental term statistics. We show that this form of temporal bias is also applicable to other well-known First Story Detection systems, where it improves the detection accuracy. To provide a more generalizable conclusion and demonstrate that the observed bias is not only an artefact of a particular implementation, we present a model that intentionally leverages a bias on temporal distance. Our model significantly improves the detection effectiveness of state-of-the-art First Story Detection systems.

# KEYWORDS

Temporal Bias, First Story Detection, Topic Detection and Tracking, UMass-FSD, LSH-FSD

# ACM Reference Format:

Dominik Wurzer and Yumeng Qin. 2020. How UMass-FSD Inadvertently Leverages Temporal Bias. In Proceedings of the 43rd International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR '20), July 25–30, 2020, Virtual Event, China. ACM, New York, NY, USA, 4 pages. https://doi.org/10.1145/3397271.3401306

# 1 INTRODUCTION

First Story Detection (FSD), also called New Event Detection, is a research task introduced as part of the Topic Detection and Tracking (TDT) initiative [1]. The goal of FSD is to identify the very first document in a stream to mention a new event. This task has direct applications in news agencies and finance. The TDT initiative held several competitions during which the UMass-FSD [3] system was recognized for its strong performance in detection effectiveness [6, 9]. In recent years UMass-FSD has been actively used as a high

Yumeng Qin\*

School of Information Management

Wuhan University, China

yumeng.qin@whu.edu.cn

accuracy baseline by state-of-the-art FSD systems [9–11, 13], which try to scale to high volume streams while retaining a level of accuracy comparable to UMass-FSD. In this paper, we investigate the novelty computation algorithm of UMass and discover for the first time that it applies a new form of temporal bias in the decision making process. We show that this new form of bias towards the temporal is also applicable to modern FSD systems. In addition, we develop a new bias model that intentionally leverages the idea of bias on temporal distance. When learning optimal weights,

# Contributions:

• Discovering Temporal Bias in UMass-FSD
We are the first to report about a temporal bias in the UMass-FSD system.

\- a New Model for Temporal Bias on Distance

We present a new model that intentionally leverages a bias towards temporal distance and show how it significantly increases the effectiveness of state-of-the-art FSD systems.

# 2 RELATED WORK

The Topic Detection and Tracking (TDT) initiative [1] defined First Story Detection (FSD) to be a streaming task. As documents arrive continuously one at a time, decisions on whether they speak about a new topic need to be made instantly and without prior knowledge about the detection targets or term statistics [1]. The most successful approach to FSD estimates the novelty of a new document arriving from the stream by its distance to the most similar previously received document [13, 14]. This problem is also known as the single nearest neighbor (1-NN) task. The pilot study of TDT [2] found that TF.IDF weighted Cosine Similarities work best when computing novelty in streaming settings like FSD. Traditionally, the Inverse Document Frequency (Equation 3) of a term (t) is computed by the ratio of the collection size ( $|C|$ ) to the Document Frequency ( $|\{d : t \in d, d \in C\}|$ ), i.e. the number of documents containing term t [12]. In streaming settings, the collection size and Document Frequencies change on the arrival of each new document. This requires a re-computation of all affected Inverse Document Frequency (IDF) statistics, also referred to as incremental IDF [7, 9]. UMass-FSD [3], a system known for its high effectiveness [6, 9, 14], estimates a document's novelty based on the distances to previously received documents, measured by incrementally weighted TF.IDF Cosine Similarities [4]. In this paper, we show for the first time that UMass-FSD's unique incremental IDF update procedure can cause a temporal bias that significantly increases detection accuracy in FSD.

Temporal bias is not a new concept in FSD. Systems, like CMU-FSD [15], reported a slight increase in effectiveness when prioritizing documents with high temporal proximity. Instead of computing

[page 2]

novelty with respect to all previous documents, CMU-FSD retains a fixed-length window covering the most recent documents. Excluding older documents from the detection process through a sliding window implies a bias on recency. CMU-FSD further biases the novelty computation of new documents by decreasing the similarity to temporally distant documents.

$$
\text {novelty} (d _ {n}) = 1 - \max _ {d _ {i} \in \text {window}} \left\{\cos \operatorname{Sim} (d _ {n}, d _ {i}) * \frac {i}{| \text {window} |} \right\} \tag {1}
$$

Equation 1 shows that CMU-FSD normalizes the Cosine Similarity between a new $(d_{n})$ and a previous document $(d_{i})$ by the fraction of the previous document's position $(i)$ within the window and the window size ( $|window|$ ) [15]. The fixed window size substantially reduces the search space, which increases efficiency. Additionally, a slightly increased degree of effectiveness was measured when applying Equation 1 to CMU-FSD on the official TDT data sets [15]. Modern FSD systems, like LSH-FSD [9], apply a similar but more relaxed form of bias towards temporal proximity. LSH-FSD [9] was the first system to demonstrate that FSD is applicable to high volume social media streams, like Twitter $^{1}$ . LSH-FSD also applies a sliding window spanning the n most recent documents. Whenever the window does not contain a sufficiently close document, LSH-FSD backs-off to an approximate nearest neighbor search (using Locality Sensitive Hashing - LSH) covering all previously encountered documents. The original publication on LSH-FSD [9] refers to this step as “Variance Reduction Strategy”, which prioritizes recent documents over temporally distant ones for the novelty computation process in FSD. The motivation for biasing novelty detection towards recency arises from the idea that events emerge, grow, and subsequently fade away. Additionally, it was shown that documents belonging to an event tend to appear in “clumps” [1]. Previous attempts [9, 15] to temporally bias FSD are based on the idea that documents with increasing temporal proximity should have progressively less influence on current decision making. This strategy, although empirically proven successful, contradicts the definition of detection target by TDT. According to the official (TDT) specification of FSD [1], detection targets are documents that are sufficiently different from all previously seen documents.

In this paper, we present a new form of temporal bias - geared towards the temporal distance, which can significantly improve the effectiveness of state-of-the-art FSD systems. By intuition, a bias on temporal distance decreases a document's novelty, if it is related to older topics. Interestingly, we discovered this form of temporal bias while studying an anomaly in the original UMass-FSD system, which is not known to apply temporal biases.

$$
\operatorname{cosineSim} (\mathrm{A}, \mathrm{B}) = \frac {\sum_ {i = 1} ^ {n} A _ {i} B _ {i}}{\sqrt {\sum_ {i = 1} ^ {n} A _ {i} ^ {2}} \sqrt {\sum_ {i = 1} ^ {n} B _ {i} ^ {2}}} \tag {2}
$$

$$
i d f (t) = \log (\frac {| C |}{| \{d : t \in d , d \in C \} |}) \tag {3}
$$

# 3 TEMPORAL BIAS THROUGH INCREMENTAL TERM STATISTICS

As is usual for streaming applications, UMass-FSD applies incremental term statistics and re-computes the IDF components on the arrival of each new document. None of the publications describing the UMass-FSD system reported about harnessing any form of temporal bias. According to the original publication $[4]$ , UMass-FSD solely bases its decisions on the distance to the closest previously encountered document, determined by the Cosine Similarity.

Incremental term statistics are updated on the arrival of each new document. This requires a subsequent re-computation of previous document vector lengths, which act as a length normalization factor in the Cosine Similarity function (Equation 2). We found that UMass-FSD accurately updates the term statistics, but omits the re-computation of the vector lengths for previously encountered documents (the highlighted grey area in Equation 2). The UMass-FSD system descriptions do not mention the omission of the length update. We presume that it is skipped to increase the runtime efficiency - unaware of the impact it has on the detection accuracy. The following sections investigate the consequences of skipping vector length updates when applying incremental term statistics to a large number of documents.

# 3.1 Incremental IDF Over Time

UMass-FSD scales its document vectors by TF.IDF, a product of Term Frequency (TF) and Inverse Document Frequency (IDF). The IDF component (Equation 3) consists of the logarithmic ratio between the collection size ( $|C|$ i.e., the number of previously received documents) and document frequency (i.e., the number of previously received documents containing term t). In order to understand the impact of neglecting document length updates, we first focus on analyzing the behavior of IDF components over time. Figure 1 shows the average IDF value for 1 million chronologically sorted English tweets. The graph illustrates that the average IDF value increases continuously over time. The steady increase occurs because the number of documents rises faster than the document frequencies, as most terms do not appear in all documents.

![](../assets/doc-008-page02-img1.jpeg)

<details>
<summary>line</summary>

| Tweets | avg. IDF |
| --- | --- |
| 0 | ~8.7 |
| 10k | ~9.4 |
| 20k | ~9.8 |
| 30k | ~10.1 |
| 40k | ~10.3 |
| 50k | ~10.5 |
| 60k | ~10.7 |
| 70k | ~10.8 |
| 80k | ~10.9 |
| 90k | ~11.0 |
| 100k | ~11.1 |
| 150k | ~11.4 |
| 200k | ~11.6 |
| 250k | ~11.8 |
| 300k | ~12.0 |
| 350k | ~12.1 |
| 400k | ~12.2 |
| 450k | ~12.3 |
| 500k | ~12.4 |
| 550k | ~12.5 |
| 600k | ~12.6 |
| 650k | ~12.7 |
| 700k | ~12.8 |
| 750k | ~12.9 |
| 800k | ~13.0 |
| 850k | ~13.1 |
| 900k | ~13.2 |
| 950k | ~13.3 |
| 1e+06 | ~13.4 |
</details>

Figure 1: Average Inverse Document Frequency (IDF) according to Equation 3 over 1 million chronologically (timestamp) sorted tweet.

#

[page 3]

3.2 Analyzing the Effect of Omitting Length Updates

Continuously rising IDF values increase the magnitudes of the term vectors over time. Usually, this does not alter the FSD novelty estimation procedure, as document vector magnitudes are re-computed when the term statistics are updated. UMass-FSD omits the vector length updates. Instead, it relies on constant vector lengths defined by the term statistics at the time of a document's arrival. Equation 2 shows the Cosine Similarity between two documents and highlights the part that uses outdated term statistics (the vector length of the previous document B) in grey. We already ascertained that the average IDF and document vector magnitudes increase over time. The Cosine Similarity

(Equation 2) normalizes the dot product between two vectors by their vector lengths. Consequently, skipping the length updates decreases the normalization factor for older documents, which increases their similarity scores. UMass-FSD estimates a document's degree of novelty by the distance to its most similar previously received document. We therefore conclude that the novelty computation of UMass-FSD is biased towards temporarily distant documents. To put it concisely, UMass-FSD decreases the novelty of a document if it is relevant to an older topic. The following section explores the impact of UMass's temporal bias on its effectiveness.

# 4 EXPERIMENTS

In this section, we explore the impact of temporal bias on the effectiveness of First Story Detection. The reproducibility of our experiments is ensured by applying original FSD systems with default settings and evaluate them on publicly available data sets, using the standard TDT [1] evaluation metric and the official TDT evaluation script with default settings. We denote “temporal bias” by TB to increase readability

# Data Set

We explore the impact of TB on three public FSD research data sets: cross-twitter $^{2}$ , a modern Twitter-based data set and the original TDT1 and TDT5 newswire data sets $^{3}$ . TDT1 consists of 25 topics and 15,863 documents and TDT5 consists of 126 topics and 278,108 documents. Cross-Twitter consists of 27 topics and comes in different corpora sizes. In this publication, we make use of cross-twitter-1.5mio, which consists of 1,500,000 tweets ordered by their publication time-stamp. The three data sets are frequently used in recent FSD publications [8–11, 13, 14].

# Evaluation Metric

Following the official TDT guideline [1], we evaluate the detection effectiveness by the normalized Topic Weighted Minimum Detection Cost ( $C_{min}$ ). The detection cost $C_{min}$ linearly combines miss and false alarm probabilities to provide a single value metric for comparing different systems [1, 4]. As is usual in the evaluation of FSD in the Topic Detection and Tracking (TDT) program [2, 14, 15], we apply Skip Evaluation. Skip Evaluation increases the number of

detection targets by iterating over the topics and replacing (skips) all detection targets by their first follow-up documents. To prevent small scale topics from vanishing, we limited Skip Evaluation to 9 rounds for cross-twitter and 3 rounds for TDT1 and TDT5.

# 4.1 The Effect of Temporal Bias on FSD effectiveness

To assess the impact of temporal bias (TB) on FSD effectiveness, we compare the original UMass-FSD system (denoted by “TB on distance”) to UMass-FSD with correct term statistic updates (denoted by “no TB”). Furthermore, we add a TB on recency (Equation 1), denoted by “TB on recency”. Table 1 shows a diverging result for TB on recency. On small scale data sets, like TDT1, the detection cost is decreased (lower is better) by 3.27%. The positive impact diminishes on the medium-sized TDT5 data set and becomes negative when applied to the large scale cross-twitter data set. When applied to large collection sizes, the fixed-sized window trades effectiveness against efficiency. Small window sizes are likely to miss the true nearest neighbor, whereas the bias overpowers the Cosine Similarity in larger windows. On the contrary, TB on distance significantly (p < 0.05) decreases the detection cost ( $C_{min}$ ) on TDT5 and cross-twitter. Our analysis revealed that the positive effect of TB on distance increases when a topic’s lifespan covers a large volume of documents. When applied to small scale data sets, like TDT1, the positive effect diminishes following neglectable changes in incremental term statistics. A side effect of biasing by omitting the vector length updates is an increase in efficiency by 66% on cross-twitter for UMass-FSD.

The TB on distance, found in UMass-FSD, is also applicable to modern FSD systems. LSH-FSD narrows the search field through randomized approximation and exhaustively search the resulting candidate set by incrementally weighted TF.IDF Cosine Similarity. This allows biasing LSH-FSD towards temporally distant documents by omitting the vector length updates. Table 2 shows that TB on distance significantly ( $p < 0.05$ ) improves the effectiveness of LSH-FSD on TDT5 and cross-twitter. Interestingly, we measured a slightly lower decrease in detection cost for LSH-FSD in comparison with UMass-FSD. Instead of identifying the true nearest neighbor, LSH-FSD approximates it and stops the search once a sufficiently close (variance reduction)[9] document is found. The combination of the approximated search and “Variance Reduction Strategy”, limits the impact of the temporal bias on detection effectiveness. When applied to small data sets (TDT1), we found that LSH-FSD omits its approximation strategy and relies on exhaustive search - like UMass-FSD. This explains the comparable performance of the two systems on TDT1.

# 4.2 Optimizing the Temporal Bias

The previous section revealed that prioritizing relevant and temporally distant documents, can reduce the detection cost in FSD systems. In this section, we create our own bias on temporal distance (Equation 4).

$$
\text {bias} (d _ {n}, d _ {i}) = \left\{ \begin{array}{c c} 1 + \delta * \log (n - i) & : \text {cosineSim} (d _ {n}, d _ {i}) \geqslant \gamma \\ 1 & : \text {cosineSim} (d _ {n}, d _ {i}) <   \gamma \end{array} \right\} \tag {4}
$$

<table><tr><td colspan="5">UMass-FSD</td></tr><tr><td>data set</td><td>no TB $(C_{min}/Dif.)$ </td><td>TB on recency $(C_{min}/Dif.)$ </td><td>TB on distance** $(C_{min}/Dif.)$ </td><td>TB optimized $(C_{min}/Dif.)$ </td></tr><tr><td>TDT1</td><td>0.642-</td><td>0.621(-3.27%)</td><td>0.641(-0.16%)</td><td>0.640(-0.31%)</td></tr><tr><td>TDT5</td><td>0.756-</td><td>0.751(-0.66%)</td><td>0.697*(-7.80%)</td><td>0.688*(-7.99%)</td></tr><tr><td>cross</td><td>0.872</td><td rowspan="2">0.936(+7.3%)</td><td rowspan="2">0.798*(-8.47%)</td><td rowspan="2">0.787*(-9.75%)</td></tr><tr><td>twitter</td><td>-</td></tr></table>

Table 1: Comparing the impact of temporal bias on UMass-FSD's detection cost ( $C_{min}$ : lower is better) for 3 data sets. Temporal bias is denoted by TB. Asterisk (\*) indicates statistical significance, (\*\*) indicates the original system.

[page 4]

We base the bias on the logarithmic difference between a document's $(d_{n})$ position $(n)$ to a previously encountered document $(d_{i})$ . The subscript $(i:i\in\{1\ldots n\})$ indicates the previous document's position within the stream. We optimize the weights $(\delta=0.036,\gamma=0.61)$ on a training data set $^{4}$ by an SVM[5], using a radial basis function kernel with a convergence tolerance of 0.01 and class weights [14] to address the class imbalance. The bias becomes effective when the Cosine Similarity exceeds the threshold parameter $\gamma$ , which is $\gamma=0.61$ on our training data set. The threshold parameter limits the bias to “relevant” documents instead of all older documents. The novelty score of a new document $(d_{n})$ is computed by: $Novelty(d_{n})=1-\max\{\cosineSim(d_{n},d_{i})*bias(d_{n},d_{i})\}$ . For example, in Cross-Twitter, document $d_{286}$ reports about a new event. A follow-up document $(d_{10,067})$ reports about the same event 9,781 documents later. The novelty score for document $d_{10,067}$ resulting from the default cosine similarity is 0.3871. Based on the temporal distance, Equation 4 inflates the cosine similarity and reduces the novelty score of the follow-up document $(d_{10,067})$ to 0.365. Table 1 and Table 2 show the impact of the optimized temporal bias (denoted “TB optimized”) on the detection effectiveness for UMass-FSD and LSH-FSD. Both systems reach their highest effectiveness (lowest detection cost) on TDT5 and cross-twitter when applying our optimized TB (Equation 4). The difference reaches statistical significance $(p<0.05)$ when applied to large data sets. The positive effect diminishes on small-scale data sets (TDT1) due to lower document volumes during the event time-spans.

# 5 CONCLUSION

This paper described how UMass-FDS inadvertently leverages a bias on temporal distance. The novelty scores of new documents are lowered, if they are relevant to older and previously known topics. We showed that the bias results from an implementation decision not to update the document vector lengths corresponding to older documents. This places higher weights on older topic and increases their contribution to the decision-making process. Our analysis showed that the discovered bias is also applicable to other well-known FSD systems, where it improves the detection effectiveness on large-scale data sets. Additionally, we presented a new bias model that intentionally leverages the idea of bias towards the

<table><tr><td colspan="5">LSH-FSD</td></tr><tr><td>data set</td><td>no TB** $(C_{min}/Dif.)$ </td><td>TB on recency $(C_{min}/Dif.)$ </td><td>TB on distance $(C_{min}/Dif.)$ </td><td>TB optimized $(C_{min}/Dif.)$ </td></tr><tr><td>TDT1</td><td>0.679-</td><td>0.665(-2.06%)</td><td>0.677(-0.29%)</td><td>0.675(-0.59%)</td></tr><tr><td>TDT5</td><td>0.762-</td><td>0.758(-0.53%)</td><td>0.714*(-6.30%)</td><td>0.706*(-7.40%)</td></tr><tr><td>cross</td><td>0.906</td><td rowspan="2">0.942(+3.97%)</td><td rowspan="2">0.837*(-7.62%)</td><td rowspan="2">0.831*(-8.28%)</td></tr><tr><td>twitter</td><td>-</td></tr></table>

Table 2: Comparing the impact of temporal bias on LSH-FSD's detection cost ( $C_{min}$ : lower is better) for 3 data sets. Temporal bias is denoted by TB. Asterisk (\*) indicates statistical significance, (\*\*) indicates the original system.

temporal distance. Our experiments demonstrated that our model significantly increases the detection effectiveness of state-of-the-art FSD systems.

# ACKNOWLEDGMENTS

We thank Dr. Victor Lavrenko for providing the source code and guidance for the original UMass-FSD and LSH-FSD systems. We also thank Dean Qing Fang for providing the computing power necessary to carrying out the experiments.

# REFERENCES

[1] James Allan (Ed.). 2002. Topic Detection and Tracking: Event-based Information Organization. Kluwer Academic Publishers, Norwell, MA, USA.
[2] James Allan, Jaime Carbonell, George Doddington, Jonathan Yamron, Yiming Yang, James Allan, Brian Archibald, Doug Beeferman, Adam Berger, Ralf Brown, Ira Carp, George Doddington, Alex Hauptmann, John Lafferty, Victor Lavrenko, Xin Liu, Steve Lowe, Paul Van Mulbregt, Ron Papka, Thomas Pierce, Jay Ponte, and Mike Scudder. 1998. Topic Detection and Tracking Pilot Study Final Report. In In Proceedings of the DARPA Broadcast News Transcription and Understanding.
[3] James Allan, Victor Lavrenko, and Hubert Jin. 2000. First story detection in TDT is hard. conference on information and knowledge management (2000), 374–381.
[4] James Allan, Victor Lavrenko, Daniella Malin, and Russell Swan. 2000. Detections, Bounds, and Timelines: UMass and TDT-3. In In Proceedings of Topic Detection and Tracking Workshop (TDT-3).
[5] Bernhard E. Boser, Isabelle M. Guyon, and Vladimir N. Vapnik. 1992. A Training Algorithm for Optimal Margin Classifiers. (1992), 144–152.
[6] Jonathan G Fiscus. 2004. Results of the 2003 Topic Detection and Tracking Evaluation. (2004).
[7] Jeyakumar Kannan, Ar Md Shanavas, and Sridhar Swaminathan. 2018. Real Time Event Detection Adopting Incremental TF-IDF based LSH and Event Summary Generation. International Journal of Computer Applications 180, 13 (2018), 22–30.
[8] Sean Moran, Richard Mccreadie, Craig Macdonald, and Iadh Ounis. 2016. Enhancing First Story Detection using Word Embeddings. international acm SIGIR conference on research and development in information retrieval (2016), 821–824.
[9] Sasa Petrovic, Miles Osborne, and Victor Lavrenko. 2010. Streaming First Story Detection with application to Twitter. (2010), 181–189.
[10] Sasa Petrovic, Miles Osborne, and Victor Lavrenko. 2012. Using paraphrases for improving first story detection in news and Twitter. (2012), 338–346.
[11] Yumeng Qin, Dominik Wurzer, Victor Lavrenko, and Cunchen Tang. 2017. Counteracting Novelty Decay in First Story Detection. ECIR 2017: Advances in Information Retrieval pp 555-560 (2017).
[12] Michael Wong, Wojciech Ziarko, and Patrick Wong. 1985. Generalized vector spaces model in information retrieval. (1985), 18–25.
[13] Dominik Wurzer, Victor Lavrenko, and Miles Osborne. 2015. Twitter-scale New Event Detection via K-term Hashing. In Proceedings of the EMNLP (2015).
[14] Dominik Wurzer and Yumeng Qin. 2018. Parameterizing Kterm Hashing. international acm SIGIR conference on research and development in information retrieval (2018), 945–948.
[15] Yiming Yang, Tom Pierce, and Jaime Carbonell. 1998. A study on retrospective and on-line event detection. In Proc. of the SIGIR Conference on Research and Development in Information Retrieval.
