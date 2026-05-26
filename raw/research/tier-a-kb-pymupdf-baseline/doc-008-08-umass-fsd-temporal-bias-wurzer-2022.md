---
id: doc-008
source: 08-umass-fsd-temporal-bias-wurzer-2022.pdf
source_type: pdf
source_sha256: 0d3d944bd3e2ae01898c5349400bfb88859fd4e2111b0528218ba3050a5ec52a
extraction_method: pymupdf4llm@unknown
extraction_date: 2026-05-26
pages: 4
headings:
  - "**How UMass-FSD Inadvertently Leverages Temporal Bias**"
  - "**ABSTRACT**"
  - "Yumeng Qin[∗]"
  - "**Contributions:**"
  - "**KEYWORDS**"
  - "**ACM Reference Format:**"
  - "**1 INTRODUCTION**"
  - "∗Corresponding Author"
  - "**2 RELATED WORK**"
  - "**3 TEMPORAL BIAS THROUGH INCREMENTAL TERM STATISTICS**"
tokens_estimated: 6329
warnings: []
assets: [../assets/doc-008-page02-img1.png, ../assets/doc-008-page02-img2.png]
---
[page 1]

## **How UMass-FSD Inadvertently Leverages Temporal Bias**

Dominik Wurzer

School of Information Management Wuhan University, China wurzer.dominik@whu.edu.cn

## **ABSTRACT**

First Story Detection describes the task of identifying new events in a stream of documents. The UMass-FSD system is known for its strong performance in First Story Detection competitions. Recently, it has been frequently used as a high accuracy baseline in research publications. We are the first to discover that UMass-FSD inadvertently leverages temporal bias. Interestingly, the discovered bias contrasts previously known biases and performs significantly better. Our analysis reveals an increased contribution of temporally distant documents, resulting from an unusual way of handling incremental term statistics. We show that this form of temporal bias is also applicable to other well-known First Story Detection systems, where it improves the detection accuracy. To provide a more generalizable conclusion and demonstrate that the observed bias is not only an artefact of a particular implementation, we present a model that intentionally leverages a bias on temporal distance. Our model significantly improves the detection effectiveness of state-of-the-art First Story Detection systems.

## Yumeng Qin[∗]

School of Information Management Wuhan University, China yumeng.qin@whu.edu.cn

accuracy baseline by state-of-the-art FSD systems [9–11, 13], which try to scale to high volume streams while retaining a level of accuracy comparable to UMass-FSD. In this paper, we investigate the novelty computation algorithm of UMass and discover for the first time that it applies a new form of temporal bias in the decision making process. We show that this new form of bias towards the temporal is also applicable to modern FSD systems. In addition, we develop a new bias model that intentionally leverages the idea of bias on temporal distance. When learning optimal weights,

## **Contributions:**

- **Discovering Temporal Bias in UMass-FSD** We are the first to report about a temporal bias in the UMassFSD system.

- **a New Model for Temporal Bias on Distance** We present a new model that intentionally leverages a bias towards temporal distance and show how it significantly increases the effectiveness of state-of-the-art FSD systems.

## **KEYWORDS**

Temporal Bias, First Story Detection, Topic Detection and Tracking, UMass-FSD, LSH-FSD

## **ACM Reference Format:**

Dominik Wurzer and Yumeng Qin. 2020. How UMass-FSD Inadvertently Leverages Temporal Bias. In _Proceedings of the 43rd International ACM SIGIR Conference on Research and Development in Information Retrieval (SIGIR ’20), July 25–30, 2020, Virtual Event, China._ ACM, New York, NY, USA, 4 pages. https://doi.org/10.1145/3397271.3401306

## **1 INTRODUCTION**

First Story Detection (FSD), also called New Event Detection, is a research task introduced as part of the Topic Detection and Tracking (TDT) initiative [1]. The goal of FSD is to identify the very first document in a stream to mention a new event. This task has direct applications in news agencies and finance. The TDT initiative held several competitions during which the UMass-FSD [3] system was recognized for its strong performance in detection effectiveness [6, 9]. In recent years UMass-FSD has been actively used as a high

## ∗Corresponding Author

Permission to make digital or hard copies of all or part of this work for personal or classroom use is granted without fee provided that copies are not made or distributed for profit or commercial advantage and that copies bear this notice and the full citation on the first page. Copyrights for components of this work owned by others than ACM must be honored. Abstracting with credit is permitted. To copy otherwise, or republish, to post on servers or to redistribute to lists, requires prior specific permission and/or a fee. Request permissions from permissions@acm.org. _SIGIR ’20, July 25–30, 2020, Virtual Event, China_ © 2020 Association for Computing Machinery. ACM ISBN 978-1-4503-8016-4/20/07...$15.00 https://doi.org/10.1145/3397271.3401306

## **2 RELATED WORK**

The Topic Detection and Tracking (TDT) initiative [1] defined First Story Detection (FSD) to be a streaming task. As documents arrive continuously one at a time, decisions on whether they speak about a new topic need to be made instantly and without prior knowledge about the detection targets or term statistics [1]. The most successful approach to FSD estimates the novelty of a new document arriving from the stream by its distance to the most similar previously received document [13, 14]. This problem is also known as the single nearest neighbor (1-NN) task. The pilot study of TDT [2] found that TF.IDF weighted Cosine Similarities work best when computing novelty in streaming settings like FSD. Traditionally, the Inverse Document Frequency (Equation 3) of a term ( _𝑡_ ) is computed by the ratio of the collection size (| _𝐶_ |) to the Document Frequency (|{ _𝑑_ : _𝑡_ ∈ _𝑑,𝑑_ ∈ _𝐶_ }|), i.e. the number of documents containing term _𝑡_ [12]. In streaming settings, the collection size and Document Frequencies change on the arrival of each new document. This requires a re-computation of all affected Inverse Document Frequency (IDF) statistics, also referred to as incremental IDF [7, 9]. UMass-FSD [3], a system known for its high effectiveness [6, 9, 14], estimates a document’s novelty based on the distances to previously received documents, measured by incrementally weighted TF.IDF Cosine Similarities [4]. In this paper, we show for the first time that UMass-FSD’s unique incremental IDF update procedure can cause a temporal bias that significantly increases detection accuracy in FSD.

Temporal bias is not a new concept in FSD. Systems, like CMU-FSD [15], reported a slight increase in effectiveness when prioritizing documents with high temporal proximity. Instead of computing

[page 2]

novelty with respect to all previous documents, CMU-FSD retains a fixed-length window covering the most recent documents. Excluding older documents from the detection process through a sliding window implies a bias on recency. CMU-FSD further biases the novelty computation of new documents by decreasing the similarity to temporally distant documents.

**![page 2, image 1](../assets/doc-008-page02-img1.png)**

Equation 1 shows that CMU-FSD normalizes the Cosine Similarity between a new ( _𝑑𝑛_ ) and a previous document ( _𝑑𝑖_ ) by the fraction of the previous document’s position ( _𝑖_ ) within the window and the window size (| _𝑤𝑖𝑛𝑑𝑜𝑤_ |) [15]. The fixed window size substantially reduces the search space, which increases efficiency. Additionally, a slightly increased degree of effectiveness was measured when applying Equation 1 to CMU-FSD on the official TDT data sets [15]. Modern FSD systems, like LSH-FSD [9], apply a similar but more relaxed form of bias towards temporal proximity. LSH-FSD [9] was the first system to demonstrate that FSD is applicable to high volume social media streams, like Twitter[1] . LSH-FSD also applies a sliding window spanning the _𝑛_ most recent documents. Whenever the window does not contain a sufficiently close document, LSHFSD backs-off to an approximate nearest neighbor search (using Locality Sensitive Hashing - LSH) covering all previously encountered documents. The original publication on LSH-FSD [9] refers to this step as “Variance Reduction Strategy”, which prioritizes recent documents over temporally distant ones for the novelty computation process in FSD. The motivation for biasing novelty detection towards recency arises from the idea that events emerge, grow, and subsequently fade away. Additionally, it was shown that documents belonging to an event tend to appear in “clumps" [1]. Previous attempts [9, 15] to temporally bias FSD are based on the idea that documents with increasing temporal proximity should have progressively less influence on current decision making. This strategy, although empirically proven successful, contradicts the definition of detection target by TDT. According to the official (TDT) specification of FSD [1], detection targets are documents that are sufficiently different from _all_ previously seen documents.

In this paper, we present a new form of temporal bias - geared towards the temporal distance, which can significantly improve the effectiveness of state-of-the-art FSD systems. By intuition, a bias on temporal distance decreases a document’s novelty, if it is related to older topics. Interestingly, we discovered this form of temporal bias while studying an anomaly in the original UMass-FSD system, which is not known to apply temporal biases.

**![page 2, image 2](../assets/doc-008-page02-img2.png)**

**==> picture [11 x 9] intentionally omitted <==**

**==> picture [183 x 22] intentionally omitted <==**

## **3 TEMPORAL BIAS THROUGH INCREMENTAL TERM STATISTICS**

As is usual for streaming applications, UMass-FSD applies incremental term statistics and re-computes the IDF components on the arrival of each new document. None of the publications describing the UMass-FSD system reported about harnessing any form of temporal bias. According to the original publication [4], UMass-FSD solely bases its decisions on the distance to the closest previously encountered document, determined by the Cosine Similarity.

Incremental term statistics are updated on the arrival of each new document. This requires a subsequent re-computation of previous document vector lengths, which act as a length normalization factor in the Cosine Similarity function (Equation 2). We found that UMass-FSD accurately updates the term statistics, but omits the re-computation of the vector lengths for previously encountered documents (the highlighted grey area in Equation 2). The UMassFSD system descriptions do not mention the omission of the length update. We presume that it is skipped to increase the runtime efficiency - unaware of the impact it has on the detection accuracy. The following sections investigate the consequences of skipping vector length updates when applying incremental term statistics to a large number of documents.

## **3.1 Incremental IDF Over Time**

UMass-FSD scales its document vectors by TF.IDF, a product of Term Frequency (TF) and Inverse Document Frequency (IDF). The IDF component (Equation 3) consists of the logarithmic ratio between the collection size (| _𝐶_ | i.e., the number of previously received documents) and document frequency (i.e., the number of previously received documents containing term _𝑡_ ). In order to understand the impact of neglecting document length updates, we first focus on analyzing the behavior of IDF components over time. Figure 1 shows the average IDF value for 1 million chronologically sorted English tweets. The graph illustrates that the average IDF value increases continuously over time. The steady increase occurs because the number of documents rises faster than the document frequencies, as most terms do not appear in all documents.

**==> picture [182 x 110] intentionally omitted <==**

**Figure 1: Average Inverse Document Frequency (IDF) according to Equation 3 over 1 million chronologically (timestamp) sorted tweet.**

1https://www.twitter.com/

[page 3]

## **3.2 Analyzing the Effect of Omitting Length Updates**

Continuously rising IDF values increase the magnitudes of the term vectors over time. Usually, this does not alter the FSD novelty estimation procedure, as document vector magnitudes are re-computed when the term statistics are updated. UMass-FSD omits the vector length updates. Instead, it relies on constant vector lengths defined by the term statistics at the time of a document’s arrival. Equation 2 shows the Cosine Similarity between two documents and highlights the part that uses outdated term statistics (the vector length of the previous document B) in grey. We already ascertained that the average IDF and document vector magnitudes increase over time. The Cosine Similarity

(Equation 2) normalizes the dot product between two vectors by their vector lengths. Consequently, skipping the length updates decreases the normalization factor for older documents, which increases their similarity scores. UMass-FSD estimates a document’s degree of novelty by the distance to its most similar previously received document. We therefore conclude that the novelty computation of UMass-FSD is biased towards temporarily distant documents. To put it concisely, UMass-FSD decreases the novelty of a document if it is _relevant_ to an older topic. The following section explores the impact of UMass’s temporal bias on its effectiveness.

## **4 EXPERIMENTS**

In this section, we explore the impact of temporal bias on the effectiveness of First Story Detection. The reproducibility of our experiments is ensured by applying original FSD systems with default settings and evaluate them on publicly available data sets, using the standard TDT [1] evaluation metric and the official TDT evaluation script with default settings. We denote “temporal bias” by _TB_ to increase readability

## **Data Set**

We explore the impact of TB on three public FSD research data sets: cross-twitter[2] , a modern Twitter-based data set and the original TDT1 and TDT5 newswire data sets[3] . TDT1 consists of 25 topics and 15,863 documents and TDT5 consists of 126 topics and 278,108 documents. Cross-Twitter consists of 27 topics and comes in different corpora sizes. In this publication, we make use of crosstwitter-1.5mio, which consists of 1,500,000 tweets ordered by their publication time-stamp. The three data sets are frequently used in recent FSD publications [8–11, 13, 14].

## **Evaluation Metric**

Following the official TDT guideline [1], we evaluate the detection effectiveness by the normalized Topic Weighted Minimum Detection Cost ( _𝐶𝑚𝑖𝑛_ ). The detection cost _𝐶𝑚𝑖𝑛_ linearly combines miss and false alarm probabilities to provide a single value metric for comparing different systems [1, 4]. As is usual in the evaluation of FSD in the Topic Detection and Tracking (TDT) program [2, 14, 15], we apply Skip Evaluation. Skip Evaluation increases the number of

> 2The Cross Project is a joint venture between the University of Edinburgh and the University of Glasgow, http://demeter.inf.ed.ac.uk/cross

> 3TDT1 and TDT5 by Linguistic Data Consortium, NIST https://catalog.ldc.upenn.edu/ LDC2006T18

detection targets by iterating over the topics and replacing ( _skips_ ) all detection targets by their first follow-up documents. To prevent small scale topics from vanishing, we limited Skip Evaluation to 9 rounds for cross-twitter and 3 rounds for TDT1 and TDT5.

## **4.1 The Effect of Temporal Bias on FSD effectiveness**

To assess the impact of temporal bias (TB) on FSD effectiveness, we compare the original UMass-FSD system (denoted by “ _TB on distance_ ”) to UMass-FSD with correct term statistic updates (denoted by “ _no TB_ "). Furthermore, we add a TB on recency (Equation 1), denoted by “TB on recency”. Table 1 shows a diverging result for TB on recency. On small scale data sets, like TDT1, the detection cost is decreased (lower is better) by 3.27%. The positive impact diminishes on the medium-sized TDT5 data set and becomes negative when applied to the large scale cross-twitter data set. When applied to large collection sizes, the fixed-sized window trades effectiveness against efficiency. Small window sizes are likely to miss the true nearest neighbor, whereas the bias overpowers the Cosine Similarity in larger windows. On the contrary, TB on distance significantly ( _𝑝 <_ 0 _._ 05) decreases the detection cost ( _𝐶𝑚𝑖𝑛_ ) on TDT5 and cross-twitter. Our analysis revealed that the positive effect of TB on distance increases when a topic’s lifespan covers a large volume of documents. When applied to small scale data sets, like TDT1, the positive effect diminishes following neglectable changes in incremental term statistics. A side effect of biasing by omitting the vector length updates is an increase in efficiency by 66% on cross-twitter for UMass-FSD.

The TB on distance, found in UMass-FSD, is also applicable to modern FSD systems. LSH-FSD narrows the search field through randomized approximation and exhaustively search the resulting candidate set by incrementally weighted TF.IDF Cosine Similarity. This allows biasing LSH-FSD towards temporally distant documents by omitting the vector length updates. Table 2 shows that TB on distance significantly ( _𝑝 <_ 0 _._ 05) improves the effectiveness of LSH-FSD on TDT5 and cross-twitter. Interestingly, we measured a slightly lower decrease in detection cost for LSH-FSD in comparison with UMass-FSD. Instead of identifying the true nearest neighbor, LSH-FSD approximates it and stops the search once a _sufficiently_ close (variance reduction)[9] document is found. The combination of the approximated search and “Variance Reduction Strategy”, limits the impact of the temporal bias on detection effectiveness. When applied to small data sets (TDT1), we found that LSH-FSD omits its approximation strategy and relies on exhaustive search - like UMass-FSD. This explains the comparable performance of the two systems on TDT1.

## **4.2 Optimizing the Temporal Bias**

The previous section revealed that prioritizing relevant and temporally distant documents, can reduce the detection cost in FSD systems. In this section, we create our own bias on temporal distance (Equation 4).

**==> picture [234 x 23] intentionally omitted <==**

[page 4]

|UMass-FSD|UMass-FSD|UMass-FSD|UMass-FSD|UMass-FSD||LSH-FSD|LSH-FSD|LSH-FSD|LSH-FSD|LSH-FSD|
|---|---|---|---|---|---|---|---|---|---|---|
|**data set**|**no TB**<br>(_𝐶𝑚𝑖𝑛_/Dif.)|**TB on**<br>**recency**<br>(_𝐶𝑚𝑖𝑛_/Dif.)|**TB on**<br>**distance****<br>(_𝐶𝑚𝑖𝑛_/Dif.)|**TB**<br>**optimized**<br>(_𝐶𝑚𝑖𝑛_/Dif.)||**data set**|**no TB****<br>(_𝐶𝑚𝑖𝑛_/Dif.)|**TB on**<br>**recency**<br>(_𝐶𝑚𝑖𝑛_/Dif.)|**TB on**<br>**distance**<br>(_𝐶𝑚𝑖𝑛_/Dif.)|**TB**<br>**optimized**<br>(_𝐶𝑚𝑖𝑛_/Dif.)|
|TDT1|0.642<br>-|**0.621**<br>**(-3.27%)**|0.641<br>(-0.16%)|0.640<br>(-0.31%)||TDT1|0.679<br>-|**0.665**<br>**(-2.06%)**|0.677<br>(-0.29%)|0.675<br>(-0.59%)|
|TDT5|0.756<br>-|0.751<br>(-0.66%)|0.697*<br>(-7.80%)|**0.688***<br>(**-7.99%**)||TDT5|0.762<br>-|0.758<br>(-0.53%)|0.714*<br>(-6.30%)|**0.706***<br>(**-7.40%**)|
|cross<br>twitter|0.872<br>-|0.936<br>(+7.3%)|0.798*<br>(-8.47%)|**0.787***<br>(**-9.75%**)||cross<br>twitter|0.906<br>-|0.942<br>(+3.97%)|0.837*<br>(-7.62%)|**0.831***<br>(**-8.28%**)|

**Table 1: Comparing the impact of temporal bias on UMassFSD’s detection cost (** _𝐶𝑚𝑖𝑛_ **: lower is better) for 3 data sets. Temporal bias is denoted by** _**TB**_ **. Asterisk (*) indicates statistical significance, (**) indicates the original system.**

**Table 2: Comparing the impact of temporal bias on LSHFSD’s detection cost (** _𝐶𝑚𝑖𝑛_ **: lower is better) for 3 data sets. Temporal bias is denoted by** _**TB**_ **. Asterisk (*) indicates statistical significance, (**) indicates the original system.**

We base the bias on the logarithmic difference between a document’s ( _𝑑𝑛_ ) position ( _𝑛_ ) to a previously encountered document ( _𝑑𝑖_ ). The subscript ( _𝑖_ : _𝑖_ ∈{1 _...𝑛_ }) indicates the previous document’s position within the stream. We optimize the weights ( _𝛿_ = 0 _._ 036 _,𝛾_ = 0 _._ 61) on a training data set[4] by an SVM[5], using a radial basis function kernel with a convergence tolerance of 0.01 and class weights [14] to address the class imbalance. The bias becomes effective when the Cosine Similarity exceeds the threshold parameter _𝛾_ , which is _𝛾_ = 0.61 on our training data set. The threshold parameter limits the bias to “relevant” documents instead of all older documents. The novelty score of a new document ( _𝑑𝑛_ ) is computed by: _𝑁𝑜𝑣𝑒𝑙𝑡𝑦_ ( _𝑑𝑛_ ) = 1 − max{ _𝑐𝑜𝑠𝑖𝑛𝑒𝑆𝑖𝑚_ ( _𝑑𝑛,𝑑𝑖_ ) ∗ _𝑏𝑖𝑎𝑠_ ( _𝑑𝑛,𝑑𝑖_ )}. For example, in Cross-Twitter, document _𝑑_ 286 reports about a new event. A follow-up document ( _𝑑_ 10 _,_ 067 ) reports about the same event 9,781 documents later. The novelty score for document _𝑑_ 10 _,_ 067 resulting from the default cosine similarity is 0.3871. Based on the temporal distance, Equation 4 inflates the cosine similarity and reduces the novelty score of the follow-up document ( _𝑑_ 10 _,_ 067) to 0.365. Table 1 and Table 2 show the impact of the optimized temporal bias (denoted “TB optimized") on the detection effectiveness for UMassFSD and LSH-FSD. Both systems reach their highest effectiveness (lowest detection cost) on TDT5 and cross-twitter when applying our optimized TB (Equation 4). The difference reaches statistical significance ( _𝑝 <_ 0 _._ 05) when applied to large data sets. The positive effect diminishes on small-scale data sets (TDT1) due to lower document volumes during the event time-spans.

## **5 CONCLUSION**

This paper described how UMass-FDS inadvertently leverages a bias on temporal distance. The novelty scores of new documents are lowered, if they are relevant to older and previously known topics. We showed that the bias results from an implementation decision not to update the document vector lengths corresponding to older documents. This places higher weights on older topic and increases their contribution to the decision-making process. Our analysis showed that the discovered bias is also applicable to other wellknown FSD systems, where it improves the detection effectiveness on large-scale data sets. Additionally, we presented a new bias model that intentionally leverages the idea of bias towards the

4Wurzer et, al. (2018) Parameterizing Kterm Hashing - consists of 15 topics + 10 rounds skip evaluation

temporal distance. Our experiments demonstrated that our model significantly increases the detection effectiveness of state-of-the-art FSD systems.

## **ACKNOWLEDGMENTS**

We thank Dr. Victor Lavrenko for providing the source code and guidance for the original UMass-FSD and LSH-FSD systems. We also thank Dean Qing Fang for providing the computing power necessary to carrying out the experiments.

## **REFERENCES**

- [1] James Allan (Ed.). 2002. _Topic Detection and Tracking: Event-based Information Organization_ . Kluwer Academic Publishers, Norwell, MA, USA.

- [2] James Allan, Jaime Carbonell, George Doddington, Jonathan Yamron, Yiming Yang, James Allan, Brian Archibald, Doug Beeferman, Adam Berger, Ralf Brown, Ira Carp, George Doddington, Alex Hauptmann, John Lafferty, Victor Lavrenko, Xin Liu, Steve Lowe, Paul Van Mulbregt, Ron Papka, Thomas Pierce, Jay Ponte, and Mike Scudder. 1998. Topic Detection and Tracking Pilot Study Final Report. In _In Proceedings of the DARPA Broadcast News Transcription and Understanding_ .

- [3] James Allan, Victor Lavrenko, and Hubert Jin. 2000. First story detection in TDT is hard. _conference on information and knowledge management_ (2000), 374–381.

- [4] James Allan, Victor Lavrenko, Daniella Malin, and Russell Swan. 2000. Detections, Bounds, and Timelines: UMass and TDT-3. In _In Proceedings of Topic Detection and Tracking Workshop (TDT-3)_ .

- [5] Bernhard E. Boser, Isabelle M. Guyon, and Vladimir N. Vapnik. 1992. A Training Algorithm for Optimal Margin Classifiers. (1992), 144–152.

- [6] Jonathan G Fiscus. 2004. Results of the 2003 Topic Detection and Tracking Evaluation. (2004).

- [7] Jeyakumar Kannan, Ar Md Shanavas, and Sridhar Swaminathan. 2018. Real Time Event Detection Adopting Incremental TF-IDF based LSH and Event Summary Generation. _International Journal of Computer Applications_ 180, 13 (2018), 22–30.

- [8] Sean Moran, Richard Mccreadie, Craig Macdonald, and Iadh Ounis. 2016. Enhancing First Story Detection using Word Embeddings. _international acm SIGIR conference on research and development in information retrieval_ (2016), 821–824.

- [9] Sasa Petrovic, Miles Osborne, and Victor Lavrenko. 2010. Streaming First Story Detection with application to Twitter. (2010), 181–189.

- [10] Sasa Petrovic, Miles Osborne, and Victor Lavrenko. 2012. Using paraphrases for improving first story detection in news and Twitter. (2012), 338–346.

- [11] Yumeng Qin, Dominik Wurzer, Victor Lavrenko, and Cunchen Tang. 2017. Counteracting Novelty Decay in First Story Detection. _ECIR 2017: Advances in Information Retrieval pp 555-560_ (2017).

- [12] Michael Wong, Wojciech Ziarko, and Patrick Wong. 1985. Generalized vector spaces model in information retrieval. (1985), 18–25.

- [13] Dominik Wurzer, Victor Lavrenko, and Miles Osborne. 2015. Twitter-scale New Event Detection via K-term Hashing. _In Proceedings of the EMNLP_ (2015).

- [14] Dominik Wurzer and Yumeng Qin. 2018. Parameterizing Kterm Hashing. _international acm SIGIR conference on research and development in information retrieval_ (2018), 945–948.

- [15] Yiming Yang, Tom Pierce, and Jaime Carbonell. 1998. A study on retrospective and on-line event detection. In _In Proc. of the SIGIR Conference on Research and Development in Information Retrieval_ .
