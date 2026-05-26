---
id: doc-010
source: 10-centroid-baseline-mds-goncalves-2023.pdf
source_type: pdf
source_sha256: 3d3ee08764cf0b3b3f94783f29d9fa3ee7243edcda7076369da26f0e0a6e6b8f
extraction_method: pymupdf4llm@unknown
extraction_date: 2026-05-26
pages: 10
headings:
  - "**Supervising the Centroid Baseline for Extractive Multi-Document Summarization**"
  - "**Abstract**"
  - "**1 Introduction**"
  - "**2 Related Work**"
  - "**3 Methodology**"
  - "**3.1 Centroid Estimation**"
  - "**3.2 Sentence Selection**"
  - "**4 Experimental Setup**"
  - "**5 Results**"
  - "**6 Conclusions**"
tokens_estimated: 11546
warnings:
  - "dropped_pictures: pymupdf4llm omitted 8 picture(s) over 10 page(s) (0.8/page); in scientific/lab PDFs these placeholders typically hide equations, matrices, or block diagrams — body text will reference formulas that aren't in the extraction. Re-extract this PDF by reading the source file directly via the Read tool and overwrite the body with a manual transcription of the remaining figures"
---
[page 1]

# **Supervising the Centroid Baseline for Extractive Multi-Document Summarization**

**Simão Gonçalves**[�] **Gonçalo Correia**[�] **Diogo Pernes**[��] **Afonso Mendes**[�] �Priberam Labs, Alameda D. Afonso Henriques, 41, 2º, 1000-123 Lisboa, Portugal

�Faculdade de Engenharia da Universidade do Porto, Porto, Portugal

{simao.goncalves, goncalo.correia, diogo.pernes, amm}@priberam.pt

## **Abstract**

The centroid method is a simple approach for extractive multi-document summarization and many improvements to its pipeline have been proposed. We further refine it by adding a beam search process to the sentence selection and also a centroid estimation attention model that leads to improved results. We demonstrate this in several multi-document summarization datasets, including in a multilingual scenario.

## **1 Introduction**

Multi-document summarization (MDS) addresses the need to condense content from multiple source documents into concise and coherent summaries while preserving the essential context and meaning. Abstractive techniques, which involve generating novel text to summarize source documents, have gained traction in recent years (Liu and Lapata, 2019; Jin et al., 2020; Xiao et al., 2022), following the advent of large pre-trained generative transformers. However, their effectiveness in summarizing multiple documents remains challenged. This is attributed not only to the long input context imposed by multiple documents but also to a notable susceptibility to factual inconsistencies. In abstractive methods, this is more pronounced when compared to their extractive counterparts due to the hallucination-proneness of large language models.

Extractive approaches, on the other hand, tackle this problem by identifying and selecting the most important sentences or passages from the given documents to construct a coherent summary. Extractive MDS usually involves a sentence importance estimation step (Hong and Nenkova, 2014; Cao et al., 2015; Cho et al., 2019), in which sentences from the source document are scored according to their relevance and redundancy with respect to the remaining sentences. Then, the summary is built by selecting a set of sentences achieving high relevance and low redundancy. The centroid-based

method (Radev et al., 2000) is a cheap unsupervised solution in which each cluster of documents is represented by a centroid that consists of the sum of the TF-IDF representations of all the sentences within the cluster and the sentences are ranked by their cosine similarity to the centroid vector. While the original method is a baseline that can be easily surpassed, subsequent enhancements have been introduced to make it a more competitive yet simple approach (Rossiello et al., 2017; Gholipour Ghalandari, 2017; Lamsiyah et al., 2021).

In this work, we refine the centroid method even further: i) we utilize multilingual sentence embeddings to enable summarization of clusters of documents in various languages; ii) we employ beam search for sentence selection, leading to a more exhaustive exploration of the candidate space and ultimately enhancing summary quality; iii) we leverage recently proposed large datasets for multidocument summarization by adding supervision to the centroid estimation process. To achieve this, we train an attention-based model to approximate the oracle centroid obtained from the ground-truth target summary, leading to significant ROUGEscore improvements in mono and multilingual settings. To the best of our knowledge, we are the first to tackle the problem within a truly multilingual framework, enabling the summarization of a cluster of documents in different languages.[1]

## **2 Related Work**

Typical supervised methods for extractive summarization involve training a model to predict sentence saliency, i.e. a model learns to score sentences in a document with respect to the target summary, either by direct match in case an extractive target is available or constructed (Svore et al., 2007; Woodsend and Lapata, 2012; Mendes et al., 2019) or by maximizing a similarity score ( _e.g._ , ROUGE)

1https://github.com/Priberam/cera-summ

[page 2]

with respect to the abstractive target summaries (Narayan et al., 2018). Attempts to reduce redundancy exploit the notion of maximum marginal relevance (MMR; Carbonell and Goldstein, 1998; McDonald, 2007) or are coverage-based (Gillick et al., 2008; Almeida and Martins, 2013), seeking a set of sentences that cover as many concepts as possible while respecting a predefined budget. During inference, the model is then able to classify the sentences with respect to their salience, selecting the highest-scored sentences for the predicted summary. Rather than training a model that predicts salience for each individual sentence, we employ a supervised model that directly predicts an overarching summary representation, specifically predicting the centroid vector of the desired summary. Training this model can thus be more direct when training with abstractive summaries (as is the case in most summarization datasets), since computing the reference summary centroid is independent of whether the target is extractive or abstractive.

Regarding enhancements to the centroid method for extractive MDS, Rossiello et al. (2017) refined it by substituting the TF-IDF representations with word2vec embeddings (Mikolov et al., 2013), and further incorporated a redundancy filter into the algorithm. Gholipour Ghalandari (2017), on the other hand, retained the utilization of TF-IDF sentence representations but improved the sentence selection process. Recently, Lamsiyah et al. (2021) introduced modifications to the sentence scoring mechanism, incorporating novelty and position scores, and evaluated a diverse array of sentence embeddings with the proposed methodology, including contextual embeddings provided by ELMo (Peters et al., 2018) and BERT (Devlin et al., 2019).

While there have been initiatives to foster research in multilingual extractive MDS (Giannakopoulos, 2013; Giannakopoulos et al., 2015), the proposed approaches (Litvak and Vanetik, 2013; Aries et al., 2015; Huang et al., 2016) are only language-agnostic, requiring all the documents within each cluster to be in the same language. In contrast, we address extractive MDS in a scenario where each cluster is multilingual.

## **3 Methodology**

The pipeline of our proposed model is divided into two stages. In the first stage, we use an attention model to obtain a cluster representation that replaces the naive centroid obtained by averaging

sentence embeddings of the documents in a cluster. The rationale behind this approach is that the contribution of each sentence to the cluster centroid should depend on its relevance to the cluster summary. In order to capture the whole cluster context, a sentence-level attention model is employed, assigning variable weights to each sentence embedding so as to approximate the resulting average to the centroid that would be obtained by averaging the sentence embeddings of the target summary. In the second stage, an adapted version of the greedy sentence selection algorithm from Gholipour Ghalandari (2017) for extractive MDS is used to select the sentences included in the predicted summary. This adapted version uses our proposed supervised centroid and also includes a beam search algorithm to better explore the space of candidate summaries.

## **3.1 Centroid Estimation**

Gholipour Ghalandari (2017) builds a centroid by summing TF-IDF sentence representations of all the sentences that compose the cluster to summarize. In our research, we compute the centroid from a learnable weighted average of the contextual sentence embeddings, via an attention model.

**Attention Model** In our centroid estimation procedure, we use a pre-trained multilingual sentence transformer from Yang et al. (2020) to encode the sentences from the news articles, obtaining contextual embeddings _**e** k ∈_ R _[d]_ , _k ∈{_ 1 _, . . . , N }_ , for each of the _N_ sentences in a cluster. Since it is often the case that the first sentences of a document are especially important for news summarization tasks, we add sentence-level learnable positional embeddings to the contextual embeddings at the input of the attention model. Specifically, given a cluster _D_ comprising _N_ sentences, we compute:

**==> picture [159 x 13] intentionally omitted <==**

where pos( _k_ ) is the position within the respective document of the _k_ -th sentence in the cluster and _**p**_ pos( _k_ ) _∈_ R _[d]_ is the corresponding learnable positional embedding. Each _**e**_ pos _,k ∈_ R _[d]_ is then concatenated with the mean-pool vector of the cluster,[2] denoted by _**e**_ pos _∈_ R _[d]_ , resulting in _**e**[′]_ pos _,k_[=][concat(] _**[e]**_[pos] _[,k][,]_ _**e**_ pos) for each sentence. This concatenation ensures that the computation of

2This is calculated by averaging the sentence embeddings within each document and then computing the mean of these individual document averages.

[page 3]

the attention weight for each position uses information from all the remaining positions. The vector _**β** ∈_ R _[N]_ of attention weights is obtained as:

**==> picture [218 x 25] intentionally omitted <==**

where MLP is a two-layer perceptron shared by all the positions. It has a single output neuron and a hidden layer with _d_ units and a tanh activation.

After computing the attention weights for the cluster, we take the original sentence embeddings _**e** k_ , _k ∈{_ 1 _, . . . , N }_ , and compute a weighted sum of these representations:

**==> picture [143 x 33] intentionally omitted <==**

Consequently, the resultant vector _**h** ∈_ R _[d]_ is a convex combination of the input sentence embeddings. Since it is not guaranteed that the target centroid lies within this space, _**h**_ is subsequently mapped to the output space through a linear layer, yielding an estimate ˆ _**c**_ attn _∈_ R _[d]_ of the centroid. Hereafter we refer to this attention model as **Ce** ntroid **R** egression **A** ttention (CeRA).

**Interpolation** The original (unsupervised) approach involves estimating the centroid by computing the average of all sentence representations _**e** k_ within a cluster, which has consistently demonstrated strong performance. Let _**e** D_ represent this centroid for cluster _D_ . To leverage the advantages of this effective technique, we introduce _**e** D_ as a residual component to enhance the estimate produced by the attention model. Thus, our final centroid estimate is computed as:

**==> picture [180 x 12] intentionally omitted <==**

where _**α** ∈_ [0 _,_ 1] _[d]_ is a vector of interpolation weights and _⊙_ denotes elementwise multiplication. The interpolation weights are obtained from concatenating ˆ _**c**_ attn and _**e** D_ and mapping it through an MLP of two linear linear layers with _d_ units each. The two layers are interleaved with a ReLU activation and a sigmoid is applied at the output. We call the model with interpolation CeRAI.

**Training Objective** Finally, we minimize the cosine distance between the model predictions ˆ _**c**_ and the mean-pool of the sentence embeddings of the target summary _**c**_ gold.

## **3.2 Sentence Selection**

Considering the cluster _D_ and a set _S_ with the current sentences in the summary. at each iteration of greedy sentence selection (Gholipour Ghalandari, 2017), we have

**==> picture [162 x 25] intentionally omitted <==**

for each sentence _s ∈ D \ S_ . Then, the new sentence _s[∗]_ to be included in the summary is

**==> picture [190 x 21] intentionally omitted <==**

where cos sim is the cosine similarity. The algorithm stops when the summary length reaches the specified budget.[3] As demonstrated in that work, redundancy is mitigated since the centroid is compared to the whole candidate summary _S ∪{s}_ at each iteration and not only to the new sentence _s_ .

In our version of the algorithm, we not only estimate the cluster centroids as explained in §3.1, replacing _**e** D_ by ˆ _**c**_ in equation (6), but also employ a beam search (BS) algorithm so that the space of candidate summaries is explored more thoroughly. Moreover, in order to exhaust the chosen budget, we add a final greedy search to do further improvements to the extracted summary. The procedure is defined in Algorithm 1, shown in Appendix A, and we describe it less formally below.

**Beam Search** The process begins by preselecting sentences, retaining only the first _n_ sentences from each document. Beam search initiates by selecting the top _B_ sentences with the highest similarity scores with the centroid, where _B_ represents the beam size. In each subsequent iteration, the algorithm finds the highest-scoring _B_ sentences on each beam, generating a total of _B_[2] candidates. Among these candidates, only the highest-ranked _B_ sentences are retained. Suppose any of these sentences exceed the specified budget length for the summary. In that case, we preserve the corresponding previous state, and no further exploration is conducted on that beam. The beam search concludes when all candidate beams have exceeded the budget or when no more sentences are available.

**Greedy Search** To exhaust the specified budget and improve results, we add a greedy search of

3While the original algorithm would stop after the first sentence that exceeded the budget, we stop before it is exceeded, and thus we do not need truncation to respect the budget.

[page 4]

|Method|Multi-News|WCEP-10|TAC2008|DUC2004|
|---|---|---|---|---|
|Oracle centroid|21.72 _±_0.33|28.54 _±_1.21|11.99 _±_1.32|10.29_±_1.01|
|Gholipour Ghalandari|16.07 _±_0.26|15.09 _±_0.92|7.36 _±_1.15|6.82 _±_0.76|
|Lamsiyah et al.|13.92 _±_0.22|16.10 _±_0.96|7.91 _±_1.31|**7.80** _±_0.78|
|BS (_Ours_)|16.22 _±_0.25|15.64 _±_0.97|8.10 _±_1.32|7.03 _±_0.64|
|BS+GS (_Ours_)|16.70 _±_0.26|16.41 _±_0.91|8.16 _±_1.25|7.46 _±_0.83|
|CeRA (_Ours_)|17.98 _±_0.23|**17.46** _±_0.98|8.27 _±_1.26|7.31 _±_0.74|
|CeRAI (_Ours_)|**17.99** _±_0.27|17.24 _±_0.93|**8.37** _±_1.24|7.72 _±_0.77|

Table 1: ROUGE-2 recall with 95% bootstrap confidence intervals of different extractive methods on the considered test sets. CeRA and CeRAI were only trained on the Multi-News training dataset.

sentences that are allowed within the word limit. The top-scoring _B_ states from the beam search are used as starting points for this greedy search. Then, for each state, we greedily select the highestscoring sentence that does not exceed the budget among the top _T_ ranked sentences. This process iterates until either all of the top _T_ ranked sentences would exceed the budget or there are no further sentences left for consideration.

## **4 Experimental Setup**

Herein, we outline the methods, datasets, and evaluation metrics employed in our experiments.

**Methods** We compare our approaches with the centroid-based methods from Gholipour Ghalandari (2017) and Lamsiyah et al. (2021), described in §2. To be consistent with the remaining methods, the approach by Gholipour Ghalandari (2017) was implemented on top of contextual sentence embeddings instead of TF-IDF. Additionally, we perform ablation evaluations in three scenarios: i) a scenario (BS) where we do not use the centroid estimation model (§3.1) and rely solely on the beam search for the sentence selection step (§3.2); ii) a scenario (BS+GS) identical to the previous one, except that we perform the greedy search step after the beam search; iii) two scenarios (CeRAI and CeRA) where we utilize the centroid estimation model with and without incorporating interpolation, and apply the BS+GS algorithm on the predicted centroid. The “Oracle centroid” upperbounds our approaches, since it results from applying BS+GS on the mean-pool of the sentence embeddings of the target summary, _**c**_ gold, as the cluster centroid. Appendix C provides additional details about data processing and hyperparameters.

**Datasets** We used four English datasets, Multi-News (Fabbri et al., 2019), WCEP-10 (Gholipour Ghalandari et al., 2020), TAC2008, and

DUC2004, and one multilingual dataset, CrossSum (Bhattacharjee et al., 2023), in our experiments. We used the centroid-estimation models trained on Multi-News to evaluate CeRA and CeRAI on WCEP-10, TAC2008, and DUC2004 since these datasets do not provide training splits. CrossSum was conceived for single-document cross-lingual summarization, so we had to adapt it for multilingual MDS. This adaptation results in clusters that encompass documents in multiple languages, with each cluster being associated with a single reference summary containing sentences in various languages. We explain this procedure and provide further details about each dataset in Appendix B.

**Evaluation Metrics** We evaluate ROUGE scores (Lin, 2004) in all the experiments. When evaluating models in the multilingual setting, we translated both the reference summaries and the extracted summaries into English prior to ROUGE computation. As we optimized for R2-R on the validation sets, we report it as our main metric in Tables 1 and 2. The remaining scores are shown in Appendix D.

## **5 Results**

**Monolingual Setting** The ROUGE-2 recall (R2R) of all the methods in the monolingual datasets are presented in Table 1. F1 scores and results for the other ROUGE variants are presented in Table 4, in Appendix D. The first observation is that BS alone outperforms Gholipour Ghalandari (2017) in all datasets, with additional improvements obtained when the greedy search step is also performed (BS+GD). This was expected since our approach explores the candidate space more thoroughly. The motivation for using a supervised centroid estimation model arose from the excellent ROUGE results obtained when using the target summaries to build the centroid (“Oracle centroid” in the tables), showing that an enhanced centroid estimation procedure

[page 5]

|Method|CrossSum|CrossSum-ZS|
|---|---|---|
|Oracle centroid|11.74 _±_0.55|14.91 _±_0.49|
|Gholipour Ghalandari|7.72 _±_0.43|10.03 _±_0.40|
|Lamsiyah et al.|8.01 _±_0.52|10.45 _±_0.46|
|BS (_Ours_)|7.74 _±_0.44|10.16 _±_0.40|
|BS+GS (_Ours_)|8.23 _±_0.43|10.85 _±_0.41|
|CeRA (_Ours_)|**9.65** _±_0.49|11.67 _±_0.41|
|CeRAI (_Ours_)|9.38 _±_0.50|**11.73** _±_0.43|

Table 2: ROUGE-2 recall results with 95% bootstrap confidence intervals of different extractive methods on the multilingual test sets. The CrossSum set contains the same languages used for training the centroid estimation model, whereas CrossSum-ZS ( _zero-shot_ ) consists of languages that were not present in the training data.

could improve the results substantially. This is confirmed by the two methods using the centroid estimation model (CeRA and CeRAI), which improve R2-R significantly in Multi-News and WCEP-10 and perform at least on par with Lamsiyah et al. (2021) in TAC2008 and DUC2004. It’s also worth noting that CeRA and CeRAI were only trained on the Multi-News training set and nevertheless performed better or on par with the remaining baselines on the test sets of the remaining corpora. Incorporating the interpolation step (CeRAI) appears to yield supplementary enhancements compared to the non-interpolated version (CeRA) across various settings, which we attribute to this method adding regularization to the estimation process, improving results on harder scenarios.

**Multilingual Setting** The R2-R scores of all the methods in CrossSum can be found in Table 2, while additional results are in Table 5 of Appendix D. Once again, we observe the superiority of the centroid estimation models, CeRA and CeRAI, in comparison to all the remaining methods, with the variants with and without interpolation performing on par with each other. Most notably, these models prove to be useful even when tested with languages unseen during the training phase, underscoring their robustness and applicability in a zero-shot setting.

## **6 Conclusions**

We enhanced the centroid method for multidocument summarization by extending a previous approach with a beam search followed by a greedy search. Additionally, we introduced a novel attention-based regression model for better centroid prediction. These improvements outperform

existing methods across various datasets, including a multilingual setting, offering a robust solution for this challenging scenario. Regarding future work, we believe an interesting research direction would be to further explore using the supervised centroids obtained by the CeRA and CeRAI models, by having them as a proxy objective to obtain improved abstractive summaries.

## **Limitations**

While we believe that our approach possesses merits, it is equally important to recognize its inherent limitations. Diverging from conventional centroid methods that operate entirely in an unsupervised manner, our centroid estimation model necessitates training with reference summaries. Nevertheless, its robustness to dataset shifts was demonstrated: the model trained on Multi-News consistently yielded strong results when assessed on different English datasets, and the model trained on a subset of languages from CrossSum displayed successful generalization to other languages.

Finally, our method introduces increased computational complexity. This arises from both the forward pass through the attention model and the proposed beam search algorithm, which incurs a greater computational cost compared to the original, simpler greedy approach proposed by Gholipour Ghalandari (2017).

## **Acknowledgements**

This work is supported by the EU H2020 SELMA project (grant agreement No. 957017).

## **References**

- Miguel Almeida and André Martins. 2013. Fast and robust compressive summarization with dual decomposition and multi-task learning. In _Proceedings of the 51st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)_ , pages 196–206, Sofia, Bulgaria. Association for Computational Linguistics.

- Abdelkrime Aries, Djamel Eddine Zegour, and Khaled Walid Hidouci. 2015. AllSummarizer system at MultiLing 2015: Multilingual single and multidocument summarization. In _Proceedings of the 16th Annual Meeting of the Special Interest Group on Discourse and Dialogue_ , pages 237–244, Prague, Czech Republic. Association for Computational Linguistics.

- Jimmy Lei Ba, Jamie Ryan Kiros, and Geoffrey E. Hinton. 2016. Layer normalization. _preprint arXiv:1607.06450_ .

[page 6]

- Abhik Bhattacharjee, Tahmid Hasan, Wasi Uddin Ahmad, Yuan-Fang Li, Yong-Bin Kang, and Rifat Shahriyar. 2023. CrossSum: Beyond English-centric cross-lingual summarization for 1,500+ language pairs. In _Proceedings of the 61st Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)_ , pages 2541–2564, Toronto, Canada. Association for Computational Linguistics.

- Steven Bird, Ewan Klein, and Edward Loper. 2009. _Natural language processing with Python: analyzing text with the natural language toolkit_ . "O’Reilly Media, Inc.".

- Ziqiang Cao, Furu Wei, Li Dong, Sujian Li, and Ming Zhou. 2015. Ranking with recursive neural networks and its application to multi-document summarization. In _Proceedings of the AAAI conference on artificial intelligence_ , volume 29.

- Jaime Carbonell and Jade Goldstein. 1998. The use of MMR, diversity-based reranking for reordering documents and producing summaries. In _Proceedings of the 21st annual international ACM SIGIR conference on Research and development in information retrieval_ , pages 335–336.

- Sangwoo Cho, Chen Li, Dong Yu, Hassan Foroosh, and Fei Liu. 2019. Multi-document summarization with determinantal point processes and contextualized representations. In _Proceedings of the 2nd Workshop on New Frontiers in Summarization_ , pages 98–103, Hong Kong, China. Association for Computational Linguistics.

- Jacob Devlin, Ming-Wei Chang, Kenton Lee, and Kristina Toutanova. 2019. BERT: Pre-training of deep bidirectional transformers for language understanding. In _Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long and Short Papers)_ , pages 4171–4186, Minneapolis, Minnesota. Association for Computational Linguistics.

- Alexander Fabbri, Irene Li, Tianwei She, Suyi Li, and Dragomir Radev. 2019. Multi-news: A large-scale multi-document summarization dataset and abstractive hierarchical model. In _Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics_ , pages 1074–1084, Florence, Italy. Association for Computational Linguistics.

- Angela Fan, Shruti Bhosale, Holger Schwenk, Zhiyi Ma, Ahmed El-Kishky, Siddharth Goyal, Mandeep Baines, Onur Celebi, Guillaume Wenzek, Vishrav Chaudhary, et al. 2021. Beyond english-centric multilingual machine translation. _The Journal of Machine Learning Research_ , 22(1):4839–4886.

- Demian Gholipour Ghalandari, Chris Hokamp, Nghia The Pham, John Glover, and Georgiana Ifrim. 2020. A large-scale multi-document summarization dataset from the wikipedia current events portal. _preprint arXiv:2005.10070_ .

- Demian Gholipour Ghalandari. 2017. Revisiting the centroid-based method: A strong baseline for multidocument summarization. In _Proceedings of the Workshop on New Frontiers in Summarization_ , pages 85–90, Copenhagen, Denmark. Association for Computational Linguistics.

- Demian Gholipour Ghalandari, Chris Hokamp, Nghia The Pham, John Glover, and Georgiana Ifrim. 2020. A large-scale multi-document summarization dataset from the Wikipedia current events portal. In _Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics_ , pages 1302–1308, Online. Association for Computational Linguistics.

- George Giannakopoulos. 2013. Multi-document multilingual summarization and evaluation tracks in ACL 2013 MultiLing workshop. In _Proceedings of the MultiLing 2013 Workshop on Multilingual Multidocument Summarization_ , pages 20–28, Sofia, Bulgaria. Association for Computational Linguistics.

- George Giannakopoulos, Jeff Kubina, John Conroy, Josef Steinberger, Benoit Favre, Mijail Kabadjov, Udo Kruschwitz, and Massimo Poesio. 2015. MultiLing 2015: Multilingual summarization of single and multi-documents, on-line fora, and call-center conversations. In _Proceedings of the 16th Annual Meeting of the Special Interest Group on Discourse and Dialogue_ , pages 270–274, Prague, Czech Republic. Association for Computational Linguistics.

- Daniel Gillick, Benoit Favre, and Dilek Hakkani-Tür. 2008. The ICSI summarization system at TAC 2008. In _Proceedings of Text Understanding Conference_ .

- Tahmid Hasan, Abhik Bhattacharjee, Md. Saiful Islam, Kazi Mubasshir, Yuan-Fang Li, Yong-Bin Kang, M. Sohel Rahman, and Rifat Shahriyar. 2021. XLsum: Large-scale multilingual abstractive summarization for 44 languages. In _Findings of the Association for Computational Linguistics: ACL-IJCNLP 2021_ , pages 4693–4703, Online. Association for Computational Linguistics.

- Kai Hong and Ani Nenkova. 2014. Improving the estimation of word importance for news multi-document summarization. In _Proceedings of the 14th Conference of the European Chapter of the Association for Computational Linguistics_ , pages 712–721, Gothenburg, Sweden. Association for Computational Linguistics.

- Taiwen Huang, Lei Li, and Yazhao Zhang. 2016. Multilingual multi-document summarization with enhanced hlda features. In _Chinese Computational Linguistics and Natural Language Processing Based on Naturally Annotated Big Data_ , pages 299–312, Cham. Springer International Publishing.

- Hanqi Jin, Tianming Wang, and Xiaojun Wan. 2020. Multi-granularity interaction network for extractive and abstractive multi-document summarization. In

[page 7]

_Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics_ , pages 6244– 6254, Online. Association for Computational Linguistics.

- Salima Lamsiyah, Abdelkader El Mahdaouy, Bernard Espinasse, and Saïd El Alaoui Ouatik. 2021. An unsupervised method for extractive multi-document summarization based on centroid approach and sentence embeddings. _Expert Systems with Applications_ , 167:114152.

- Chin-Yew Lin. 2004. ROUGE: A package for automatic evaluation of summaries. In _Text Summarization Branches Out_ , pages 74–81, Barcelona, Spain. Association for Computational Linguistics.

- Marina Litvak and Natalia Vanetik. 2013. Multilingual multi-document summarization with POLY2. In _Proceedings of the MultiLing 2013 Workshop on Multilingual Multi-document Summarization_ , pages 45– 49, Sofia, Bulgaria. Association for Computational Linguistics.

- Yang Liu and Mirella Lapata. 2019. Hierarchical transformers for multi-document summarization. In _Proceedings of the 57th Annual Meeting of the Association for Computational Linguistics_ , pages 5070– 5081, Florence, Italy. Association for Computational Linguistics.

- Ryan McDonald. 2007. A study of global inference algorithms in multi-document summarization. In _European Conference on Information Retrieval_ , pages 557–564. Springer.

- Afonso Mendes, Shashi Narayan, Sebastião Miranda, Zita Marinho, André F. T. Martins, and Shay B. Cohen. 2019. Jointly extracting and compressing documents with summary state representations. In _Proceedings of the 2019 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long and Short Papers)_ , pages 3955–3966, Minneapolis, Minnesota. Association for Computational Linguistics.

- Tomas Mikolov, Ilya Sutskever, Kai Chen, Greg S Corrado, and Jeff Dean. 2013. Distributed representations of words and phrases and their compositionality. In _Advances in Neural Information Processing Systems_ , volume 26. Curran Associates, Inc.

- Shashi Narayan, Shay B. Cohen, and Mirella Lapata. 2018. Ranking sentences for extractive summarization with reinforcement learning. In _Proceedings of the 2018 Conference of the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long Papers)_ , pages 1747–1759, New Orleans, Louisiana. Association for Computational Linguistics.

_the North American Chapter of the Association for Computational Linguistics: Human Language Technologies, Volume 1 (Long Papers)_ , pages 2227–2237, New Orleans, Louisiana. Association for Computational Linguistics.

   - Dragomir R. Radev, Hongyan Jing, and Malgorzata Budzikowska. 2000. Centroid-based summarization of multiple documents: sentence extraction, utilitybased evaluation, and user studies. In _NAACL-ANLP 2000 Workshop: Automatic Summarization_ .

   - Gaetano Rossiello, Pierpaolo Basile, and Giovanni Semeraro. 2017. Centroid-based text summarization through compositionality of word embeddings. In _Proceedings of the MultiLing 2017 Workshop on Summarization and Summary Evaluation Across Source Types and Genres_ , pages 12–21, Valencia, Spain. Association for Computational Linguistics.

   - Krysta Svore, Lucy Vanderwende, and Christopher Burges. 2007. Enhancing single-document summarization by combining RankNet and third-party sources. In _Proceedings of the 2007 Joint Conference on Empirical Methods in Natural Language Processing and Computational Natural Language Learning (EMNLP-CoNLL)_ , pages 448–457, Prague, Czech Republic. Association for Computational Linguistics.

   - Kristian Woodsend and Mirella Lapata. 2012. Multiple aspect summarization using integer linear programming. In _Proceedings of the 2012 Joint Conference on Empirical Methods in Natural Language Processing and Computational Natural Language Learning_ , pages 233–243, Jeju Island, Korea. Association for Computational Linguistics.

   - Wen Xiao, Iz Beltagy, Giuseppe Carenini, and Arman Cohan. 2022. PRIMERA: Pyramid-based masked sentence pre-training for multi-document summarization. In _Proceedings of the 60th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers)_ , pages 5245–5263, Dublin, Ireland. Association for Computational Linguistics.

   - Yinfei Yang, Daniel Cer, Amin Ahmad, Mandy Guo, Jax Law, Noah Constant, Gustavo Hernandez Abrego, Steve Yuan, Chris Tar, Yun-hsuan Sung, Brian Strope, and Ray Kurzweil. 2020. Multilingual universal sentence encoder for semantic retrieval. In _Proceedings of the 58th Annual Meeting of the Association for Computational Linguistics: System Demonstrations_ , pages 87–94, Online. Association for Computational Linguistics.

- Matthew E. Peters, Mark Neumann, Mohit Iyyer, Matt Gardner, Christopher Clark, Kenton Lee, and Luke Zettlemoyer. 2018. Deep contextualized word representations. In _Proceedings of the 2018 Conference of_

[page 8]

## **A Sentence Selection Algorithm**

**Algorithm 1** Sentence Selection

**Require:** Cluster _D_ , centroid ˆ _**c**_ , summary budget _ℓ_ , number of sentences _n_ to pre-select, beam size _B_ , number of candidates _T_ for greedy search.

- 1: _Dn ←_ select-first( _D, n_ )

- 2: _π, π_ next _, π_ bs _←_ empty list

- 3: **while** _∃b_ : length( _π_ next[ _b_ ]) _< ℓ_ **do** : _▷_ Beam Search

- 4: _π_ next _←_ BSstep( _π, Dn, B,_ ˆ _**c**_ )[(][4][)]

- 5: **if** _∃b_ : length( _π_ next[ _b_ ]) _> ℓ_ **then** 6: _π_ bs _._ append( _π_ ) 7: **end if** 8: _π ←∀π_ next[ _b_ ] : length( _π_ next[ _b_ ]) _≤ ℓ_

- 9: **end while**

- 10: _π_ best _←_ highest-scored _B_ states in _π_ bs (sorted)

- 11: **for** _b_ = 1 _,_ 2 _, . . . , B_ **do** : _▷_ Greedy Search 12: _t ←_ 0

**==> picture [121 x 24] intentionally omitted <==**

**==> picture [216 x 139] intentionally omitted <==**

25: **end for**

26: **return** _S ←_ highest-scored state in _π_ best

## **B Datasets**

We now describe each of the datasets used for evaluation and explain how we have adapted CrossSum for the task of MDS.

**Multi-News** The Multi-News dataset (Fabbri et al., 2019) is a large-scale dataset for MDS of news articles. It contains up to 10 documents per cluster and more than 50 thousand clusters divided into training, validation, and test splits. There is a single human-written reference summary for each cluster.

> 4BSstep denotes a step of the usual beam search algorithm. Details omitted for brevity.

**WCEP-10** This dataset (Ghalandari et al., 2020; Xiao et al., 2022) consists of short human-written target summaries extracted from the Wikipedia Current Events Portal (WCEP). Each news cluster associated with a certain event is paired with a single reference summary, and there are at most 10 documents per cluster. The dataset comprises 1022 clusters, all of which are used for testing.

**TAC2008** This is a multi-reference dataset introduced by the Text Analysis Conference (TAC)[5] . It provides no training nor validation sets and the test set consists of 48 news clusters, each with 10 related documents and 4 human-written summaries as references.

**DUC2004** Another multi-reference news summarization dataset[6] designed and used for testing only. It contains 50 clusters with 10 documents and 4 human-written reference summaries each.

**CrossSum** To assess the performance of the models in a multilingual context, we have adapted the CrossSum dataset (Bhattacharjee et al., 2023) for the task of MDS. Initially designed for cross-lingual summarization, this dataset offers document-summary pairs for more than 1500 language directions. The dataset is derived from pairs of articles sourced from the multilingual summarization dataset XL-Sum (Hasan et al., 2021). Notably, these pairings were established using an automatic similarity metric, resulting in many pairs covering similar topics rather than the exact same stories, rendering it well-suited MDS.

To tailor this dataset for our specific task, we began by selecting the data from a predefined subset of the languages. Subsequently, we aggregated the documents into clusters, taking into account their pairings. For instance, if document _A_ was paired with document _B_ and document _B_ was paired with document _C_ , then _A_ , _B_ , and _C_ would belong to the same cluster. Clusters containing only one document were discarded. For obtaining multilingual reference summaries for each cluster, we interleaved the sentences from the individual summaries until we reached a predefined limit of 100 words. We have built training, validation, and test sets using data in English, Spanish, and French, and another test set using data in Portuguese, Russian, and Turkish to evaluate our model in a zero-shot

5https://tac.nist.gov

6https://duc.nist.gov

[page 9]

setting. Statistics about each split are presented in Table 3.

## **C Experimental Details**

**Data Processing** To ensure a fair comparison, all the models we evaluated used the same sentence representations, specifically, sentence embeddings obtained from the distiluse-base-multilingual-cased-v2[7] sentence encoder (Yang et al., 2020).

For monolingual datasets, the documents were split into sentences using sent_tokenize from the NLTK library (Bird et al., 2009). For CrossSum, we used SentSplitter from the multilingual ICUtokenizer.[8] Regular expressions were applied to replace redundant white spaces and excessive paragraphs and empty sentences were excluded. Before sentence selection (Algorithm 1), the data goes through a second processing step, during which duplicate sentences and sentences that individually exceed the summary budget are eliminated.

When evaluating models in CrossSum, we translated both the reference summaries and the extracted summaries into English prior to ROUGE computation. All the translations were performed using the M2M-100 12-billion-parameter model (Fan et al., 2021).

search on Multi-News. The hyperparameters yielding the highest R2-R score on the validation set for the produced summaries were kept. The CeRAI model was trained using the optimal hyperparameters found for CeRA. The optimal parameters were: _batch size_ = 2, _learning rate_ = 5 _×_ 10 _[−]_[4] , and _number of positional encodings_ = 35. We utilized the Adam optimizer with a multi-step learning rate scheduler configured with _step size_ = 3 and _γ_ = 0.1.

**Implementation Details** Our CeRA and CeRAI models used early stopping, where the stopping criteria metric was based on R2-R. Layer normalization (Ba et al., 2016) was applied on the input data before adding the positional information to it and before passing the data through the last linear layer that transforms _**h**_ (equation (3)) into ˆ _**c**_ attn in the CeRA and CeRAI models. We have also normalized the input data to have a unit L2 norm.

## **D Additional Results**

The ROUGE-1/2/L recall and F1 scores obtained by all the methods in the monolingual datasets are shown in Table 4. Table 5 presents the same quantities for the multilingual case.

The following word-limit budgets were used by all models: 230 words for the Multi-News dataset, 100 words for TAC2008, DUC2004 and CrossSum, and 50 words for WCEP-10.[9]

**Hyperparameters** The hyperparameters for the beam search-based methods were tuned by running a grid search on the BS+GS approach on the MultiNews validation set. For the number of sentences _n_ , odd numbers from 1 to 9 were tested. For the beam width _B_ values 1,5, and 9 were examined, and regarding the number of candidates _T_ , values 1,5, and 9 were considered. The values that maximized R2-R on this validation set were _n_ = 9, _B_ =5, and _T_ =9. In all of our experiments, these were the values we considered for the parameters. Note that for the BS method only _n_ and _B_ are relevant.

The hyperparameters of the centroid estimation model used in CeRA were obtained by random

> 7https://huggingface.co/sentence-transformers/ distiluse-base-multilingual-cased-v2

> 8https://pypi.org/project/icu-tokenizer

> 9We used ROUGE 1.5.5 toolkit with the following arguments: -n 4 -m -2 4 -l budget -u -c 95 -r 1000 -f A -p 0.5 -t 0 -a

[page 10]

|Split|Languages|#Clusters|#Docs per cluster|#Docs per cluster|Avg #sentences per doc|Avg #words per summary|
|---|---|---|---|---|---|---|
|Train|en, es, fr|6541||2_−_10|38.5 _±_28.8|52.5 _±_16.1|
|Val|en, es, fr|889||2_−_6|34.4 _±_27.4|52.3 _±_15.5|
|Test|en, es, fr|853||2_−_6|36.6 _±_35.4|52.2 _±_16.2|
|Test-ZS|pt, ru, tr|933||2_−_5|23.4 _±_21.1|60.2 _±_20.8|

Table 3: CrossSum: statistics of each split. Averages are indicated with standard deviations.

|Test set|Method|R1-R|R1-F|R2-R|R2-F|RL-R|RL-F|
|---|---|---|---|---|---|---|---|
||Oracle centroid|54.26|50.36|21.72|20.02|24.33|22.42|
||Gholipour Ghalandari|47.91|45.64|16.07|15.16|21.41|20.24|
|Multi-News|Lamsiyah et al.<br>BS (_Ours_)|44.91<br>48.34|43.02<br>45.81|13.93<br>16.22|13.18<br>15.24|20.56<br>21.34|19.53<br>20.08|
||BS+GS (_Ours_)|49.54|45.98|16.70|15.36|21.81|20.08|
||CeRA (_Ours_)|50.75|47.07|17.98|16.52|**22.69**|20.86|
||CeRAI (_Ours_)|**50.76**|**47.08**|**17.99**|**16.53**|**22.69**|**20.87**|
||Oracle centroid|58.72|44.94|28.54|21.50|42.38|31.94|
||Gholipour Ghalandari|41.26|35.09|15.09|12.61|29.42|24.86|
|WCEP-10|Lamsiyah et al.<br>BS (_Ours_)|41.65<br>43.48|**35.62**<br>35.07|16.10<br>15.64|**13.38**<br>12.42|30.53<br>30.49|**25.75**<br>24.44|
||BS+GS (_Ours_)|46.23|34.72|16.41|12.05|31.85|23.60|
||CeRA (_Ours_)|**47.14**|35.23|**17.46**|12.65|**33.03**|24.28|
||CeRAI (_Ours_)|46.85|35.17|17.24|12.59|32.81|24.24|
||Oracle centroid|41.07|42.02|11.99|12.26|20.66|21.11|
||Gholipour Ghalandari|32.00|34.38|7.36|7.91|16.64|17.87|
|TAC2008|Lamsiyah et al.<br>BS (_Ours_)|31.00<br>33.93|33.75<br>35.62|7.91<br>8.10|**8.65**<br>8.53|16.65<br>17.62|18.16<br>**18.50**|
||BS+GS (_Ours_)|**35.12**|**35.98**|8.16|8.34|**17.99**|18.40|
||CeRA (_Ours_)|34.43|35.07|8.27|8.42|17.35|17.66|
||CeRAI (_Ours_)|34.44|35.11|**8.37**|8.52|17.73|18.06|
||Oracle centroid|39.93|41.10|10.29|10.60|19.48|20.05|
||Gholipour Ghalandari|32.82|35.86|6.82|7.48|16.00|17.51|
|DUC2004|Lamsiyah et al.<br>BS (_Ours_)|32.81<br>34.01|36.03<br>36.20|**7.80**<br>7.03|**8.61**<br>7.51|16.66<br>16.35|**18.34**<br>17.41|
||BS+GS (_Ours_)|35.11|36.37|7.46|7.74|**16.98**|17.60|
||CeRA (_Ours_)|34.88|36.06|7.31|7.56|16.67|17.23|
||CeRAI (_Ours_)|**35.16**|**36.38**|7.72|7.99|16.89|17.48|

Table 4: ROUGE-1/2/L recall and F1 results of different extractive methods on the considered monolingual test sets.

|Test set|Method|R1-R|R1-F|R2-R|R2-F|RL-R|RL-F|
|---|---|---|---|---|---|---|---|
||Oracle centroid|46.86|31.85|11.74|7.93|27.64|18.57|
||Gholipour Ghalandari|38.64|27.88|7.72|5.56|23.30|16.65|
|CrossSum|Lamsiyah et al.<br>BS (_Ours_)|37.89<br>39.24|27.53<br>27.83|8.01<br>7.74|5.77<br>5.48|23.81<br>23.60|17.13<br>16.53|
||BS+GS (_Ours_)|40.78|27.71|8.23|5.57|24.42|16.39|
||CeRA (_Ours_)|**42.45**|**28.89**|**9.65**|**6.52**|**25.64**|**17.27**|
||CeRAI (_Ours_)|42.31|28.73|9.38|6.31|25.55|17.15|
||Oracle centroid|50.55|37.30|14.91|11.00|28.90|21.08|
||Gholipour Ghalandari|41.70|32.65|10.03|7.82|24.52|19.02|
|CrossSum-ZS|Lamsiyah et al.<br>BS (_Ours_)|41.14<br>42.53|32.39<br>32.65|10.45<br>10.16|8.17<br>7.81|24.81<br>24.87|19.31<br>18.90|
||BS+GS (_Ours_)|44.36|32.65|10.85|7.99|25.74|18.74|
||CeRA (_Ours_)|**45.44**|**33.43**|11.67|8.57|**26.52**|**19.30**|
||CeRAI (_Ours_)|45.37|33.38|**11.73**|**8.62**|26.51|19.26|

Table 5: ROUGE-1/2/L recall and F1 results of different extractive methods on the considered multilingual test sets.
