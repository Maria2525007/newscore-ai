---
id: doc-005
source: 05-milco-lsr-nguyen-2025.pdf
source_type: pdf
source_sha256: 58e9cf4a0a0bc7c4f4b5b887917daeecdf9df5c2b532c1651fbf494822b97ccc
extraction_method: pymupdf4llm@unknown
extraction_date: 2026-05-26
pages: 25
headings:
  - MILCO: LEARNED SPARSE RETRIEVAL ACROSS LANGUAGES VIA A MULTILINGUAL CONNECTOR
  - "**Thong Nguyen, Yibin Lei & Jia-Huei Ju**"
  - "**Eugene Yang & Andrew Yates**"
  - ABSTRACT
  - 1 INTRODUCTION
  - "**Our Contributions:**"
  - 2 RELATED WORK
  - 3 PROPOSED METHODOLOGY
  - 3.1 MILCO ARCHITECTURE
  - 3.2 TRAINING: SPARSE ALIGNMENT AND CONTRASTIVE REFINEMENT
tokens_estimated: 38454
warnings:
  - "dropped_pictures: 1/14 placeholder(s) were auto-recovered as assets, but 13 still remain over 25 page(s) (0.52/page). Re-extract this PDF by reading the source file directly via the Read tool and overwrite the body with a manual transcription of the remaining figures"
assets: [../assets/doc-005-page02-img1.jpeg]
---
[page 1]

Published as a conference paper at ICLR 2026

# MILCO: LEARNED SPARSE RETRIEVAL ACROSS LANGUAGES VIA A MULTILINGUAL CONNECTOR

## **Thong Nguyen, Yibin Lei & Jia-Huei Ju**

University of Amsterdam

_{_ t.nguyen2,y.lei,j.ju _}_ @uva.nl

## **Eugene Yang & Andrew Yates**

Johns Hopkins University, HLTCOE _{_ eugene.yang, andrew.yates _}_ @jhu.edu

## ABSTRACT

Learned Sparse Retrieval (LSR) combines the efficiency of bi-encoders with the transparency of lexical matching, but existing approaches struggle to scale beyond English. We introduce MILCO, an LSR architecture that maps queries and documents from different languages into a shared English lexical space via a multilingual connector. MILCO is trained with a specialized two-stage regime that combines Sparse Alignment Pretraining with contrastive training to provide representation transparency and effectiveness while mitigating semantic collapse. Motivated by the observation that uncommon entities are often lost when projected into English, we propose a new LexEcho head, which enhances robustness by augmenting the English lexical representation with a source-language view obtained through a special [ **ECHO** ] token. MILCO achieves state-of-the-art multilingual and cross-lingual LSR performance, outperforming leading dense, sparse, and multi-vector baselines such as BGE-M3 and Qwen3-Embed on standard multilingual benchmarks, while supporting dynamic efficiency through post-hoc pruning. Notably, when using mass-based pruning to reduce document representations to only 30 active dimensions on average, MILCO 560M outperforms the similarlysized Qwen3-Embed 0.6B with 1024 dimensions, while achieving 3 _×_ lower retrieval latency and 10 _×_ smaller index size.[1]

## 1 INTRODUCTION

Learned Sparse Retrieval (LSR) represents queries and documents as sparse lexical embeddings and retains the scalability benefits of bi-encoders (MacAvaney et al., 2020; Formal et al., 2021; Nguyen et al., 2023) . Unlike dense methods, LSR aligns representation with a natural language vocabulary, yielding transparent representations that facilitate error tracing and bias inspection. LSR naturally supports dynamic post-hoc pruning at inference time (Bruch et al., 2024), providing Matryoshka-like latency control (Kusupati et al., 2022) without requiring auxiliary training objectives. Empirically, LSR (Lassance et al., 2024; Lei et al., 2025) is competitive on benchmarks like BEIR (Thakur et al., 2021) and MTEB (Enevoldsen et al., 2025). Theoretically, recent work shows sparse lexical embeddings exhibit higher representational capacity than dense embeddings, which is illustrated by their superior performance on the LIMIT benchmark (Weller et al., 2025) where even state-of-the-art dense models fail catastrophically.

Thus far, LSR progress has been driven primarily by English (Formal et al., 2022; Shen et al., 2025; Nardini et al., 2025), where models such as SPLADE (Lassance et al., 2024) deliver strong zero-shot effectiveness and have seen wide adoption in production systems (e.g., OpenSearch, ElasticSearch, Sentence Transformers). Extensions beyond English remain fragmented: BGE-M3 (Chen et al., 2024) combines dense, sparse, and multi-vector heads under a shared backbone, but its sparse component underperforms and lacks cross-lingual support; conversely, SPLADE-X (Nair et al., 2022b)

> 1 Our code is available at: https://github.com/thongnt99/milco.

[page 2]

Published as a conference paper at ICLR 2026

and BLADE (Nair et al., 2023) target cross-lingual retrieval only and rely on training separate models for each language pair, limiting their applications.

A straightforward multilingual LSR approach is to attach a multilingual MLM head to a multilingual base encoder, projecting inputs into the full multilingual vocabulary. However, directly optimizing such models can lead to severe semantic collapse (Nguyen et al., 2024), where representations lose interpretable term semantics, resulting in significant degradation of the model’s transparency and effectiveness. This behavior is demonstrated both qualitatively and quantitatively in Section 5.

**![page 2, image 1](../assets/doc-005-page02-img1.jpeg)**

**----- Start of picture text -----**<br>
陌 陌 直播 音乐 怎么 导 入 手机<br>[ECHO] * * * * * * * *<br>phone * Source View English View<br>…<br>transfer * Token Weight Note Token Weight<br>step… * LexEcho  陌 1.46 mo music 1.16<br>import… * Head 手机 0.97 phone phoneimport 0.950.88<br>live… * 导 0.68 import step 0.80<br>music * 直播 0.67 live transfer 0.72<br>Multilingual Connector 音乐 0.65 music songs 0.55<br>song 0.49<br>怎么 0.38 how<br>live 0.51<br>Multilingual Encoder 入 0.36 import … …<br>陌 陌 直播 音乐 怎么 导 入 手机 陌陌直播音乐怎么导入手机？<br> How to import Momo Live music to mobile phone? (Translation)  How to import Momo Live music to mobile phone? (Translation)<br>Non-English Input (Chinese)<br>**----- End of picture text -----**<br>

Figure 1: MILCO’s LexEcho head produces two lexical views: (1) a pivot (English) view supporting cross-lingual and multilingual retrieval, and (2) a source view for robustness to uncommon entities.

To overcome those challenges, we introduce MILCO, illustrated in Figure 1, an LSR architecture that uses a multilingual connector between a multilingual base encoder and an English MLM head, mapping text from all languages into a shared English vocabulary space. MILCO collapses the multilingual vocabulary to English to create a universal representation, which also reduces memory and computation during training. This approach enables one single MILCO model to support both multilingual and cross-lingual retrieval across many languages.

**MILCO Training.** We adopt a two-stage training procedure. First, we propose _Sparse Alignment Pretraining (SAP)_ , which maps multilingual inputs to English lexical targets, in contrast to prior dense alignment methods that operate in low-dimensional latent space (Reimers & Gurevych, 2020). SAP leverages widely available bitext corpora instead of scarce multilingual relevance labels, enabling large-scale multilingual pretraining. Alignment pretraining enables the model to then be fine-tuned with contrastive training using distillation (Lassance et al., 2024), which enhances retrieval effectiveness while preserving grounding. Crucially, SAP is a prerequisite: without alignment, contrastive training leads to semantic collapse, harming effectiveness.

**LexEcho Head.** We observe that uncommon entities, especially from non-Latin languages, are often lost when projected into English. To address this, we introduce LexEcho, a dual-view LSR head illustrated in Figure 1. The _pivot (English) view_ is obtained by max-pooling over the logit matrix of an English MLM head, with our multilingual connector enabling it to operate across many languages. The _source view_ selectively echoes input tokens through a special [ **ECHO** ] token, preserving entities that the English view fails to capture and assigning higher scores to more important tokens. This approach allows the model to represent entities it has never seen before or cannot translate.

Across 39 languages, our 560M MILCO model sets a new state of the art for Learned Sparse Retrieval in both multilingual and cross-lingual settings. On MIRACL, our best model surpasses BGESparse, BGE-Dense, and Qwen3-Embed 8B by +34.1%, +4.5%, and +3.6% nDCG@10, respectively, while also providing transparent representations. Experiments also show that the proposed LexEcho head enhances robustness to tail entities, yielding an +4.2% overall improvement on MIRACL. Like Matryoshka Representation Learning, MILCO supports controllable efficiency via post-

[page 3]

Published as a conference paper at ICLR 2026

hoc pruning, surpassing Qwen3-Embed 0.6B with only 30 active dimensions per document, while achieving 3 _×_ lower retrieval latency and 10 _×_ smaller index size.

## **Our Contributions:**

- We introduce MILCO, a multilingual connector architecture that maps queries and documents into a shared English lexical space, unifying multilingual and cross-lingual retrieval within a single model. Its LEXECHO head provides dual lexical views, enhancing robustness to unseen or uncommon entities or concepts.

- We introduce a new Sparse Alignment Pretraining (SAP) pretraining strategy tailored to multilingual LSR that addresses semantic collapse and provides the foundation for contrastive training, leading to an effective and transparent model.

- Through comprehensive experiments on multilingual and cross-lingual benchmarks across 39 languages, we demonstrate that the MILCO architecture and Sparse Alignment Pretraining are key to achieving state-of-the-art multilingual and cross-lingual sparse retrieval.

## 2 RELATED WORK

**Learned Sparse Retrieval (LSR).** Zamani et al. (2018) first proposed SNRM, an n-gram neural model for learning sparse representations compatible with inverted indexes, though its representations remained latent. Subsequent work (MacAvaney et al., 2020; Formal et al., 2021) replaced SNRM with Transformer architectures that map text directly into the English lexicon, yielding more transparent and effective models. Nguyen et al. (2023) categorize LSR architectures into three groups: Binary Encoders, which assign binary weights to tokens and enable efficient inference-free query encoding with modest effectiveness trade-offs (Nardini et al., 2025; Shen et al., 2025); MLP Encoders, which score tokens by contextual importance (MacAvaney et al., 2020; Lin & Ma, 2021); and MLM Encoders, used in state-of-the-art methods like Splade (Formal et al., 2021), which provide differentiable query weighting and expansion. Beyond architecture, training protocols such as hard negative mining and distillation (e.g., from cross-encoders) are key to narrowing the gap with dense and hybrid systems (Formal et al., 2022; Lassance et al., 2024). In this work, we introduce MILCO, a new LSR architecture with a LexEcho head for multilingual sparse retrieval.

**Multilingual/Cross-language Retrieval.** A central challenge in cross-language IR is the language mismatch between queries and documents. Existing approaches address this either through translation pipelines or multilingual encoders that map text from different languages into a shared latent space for cross-lingual matching. Representative efforts include dense encoder methods (Zhang et al., 2024; Wang et al., 2024; Zhang et al., 2025) and multi-vector methods with multilingual pretraining (Louis et al., 2024; Yang et al., 2024a). Community benchmarks such as MIRACL (Zhang et al., b) and NeuCLIR (Lawrie et al., 2024) provide standardized evaluation across many languages, while studies on translationese highlight biases introduced by translated text (Gellerstam, 1986; Riley et al., 2020; Nair et al., 2022a; Zhang et al., a). For sparse retrieval, BGE-M3 (Chen et al., 2024) combines dense, sparse, and multi-vector heads for multilingual retrieval, but its sparse component underperforms and offers limited cross-language support. Other sparse models such as SPLADE-X (Nair et al., 2022b) and BLADE (Nair et al., 2023) focus on cross-language retrieval with language-specific models. In contrast, our sparse model, MILCO, supports both multilingual and cross-language retrieval within a single model while substantially outperforming prior approaches.

**Alignment Pretraining.** Previous work highlights the importance of multilingual pre-training for building shared cross-language semantic spaces (Conneau et al., 2020; Chi et al.; Feng et al., 2022; Yang et al., 2022). For retrieval, pre-training directly on relevance objectives has been explored, often using in-batch negatives and hard-negative mining (Zhang et al., 2024). Another direction focuses on distilling efficient models, where cross-encoder or ensemble teachers guide bi-encoder students to produce retrieval-friendly embeddings (Kim et al., 2023; Campos et al., 2023). In multilingual IR, distillation also yields compact, language-agnostic dense embeddings for scalable crosslanguage retrieval (Reimers & Gurevych, 2020; Yang et al., 2024a). While prior work has mainly focused on dense models, we are the first to explore multilingual sparse alignment and introduce a sparse alignment pre-training method that enables LSR to perform well on multilingual data.

[page 4]

Published as a conference paper at ICLR 2026

## 3 PROPOSED METHODOLOGY

## 3.1 MILCO ARCHITECTURE

MILCO consists of three main components: (i) a **Multilingual Encoder** , (ii) a **Multilingual Connector** , and (iii) a **LexEcho Head** . Figure 1 illustrates MILCO processing the Chinese input: _“How to import Momo Live music to a mobile phone?”_ Let _L_ denote the set of supported languages. For an input text _x_ in language _ℓ ∈L_ , we first tokenize it into a sequence of _n_ source tokens:

**==> picture [238 x 13] intentionally omitted <==**

**Multilingual Encoder.** A transformer-based Multilingual Encoder _Enc_ ( _·_ ) maps the input tokens _s_[(] _[ℓ]_[)] into a sequence of hidden states of dimension _dL_ in a multilingual embedding space:

**==> picture [256 x 12] intentionally omitted <==**

where **H**[(] _[ℓ]_[)] represents the contextualized embeddings for the _n_ input tokens. For conciseness, we omit the superscript ( _ℓ_ ) whenever the language space of the variable is unambiguous, making it **H** .

**Multilingual Connector.** The Multilingual Connector _ϕ_ then projects these multilingual hidden states **H** into **Z** of dimension _de_ , which live in the embedding space of the pivot language:

**==> picture [354 x 12] intentionally omitted <==**

For simplicity, we implement the connector _ϕ_ with a Multi-Layer Perceptron. This projection unifies representations across different languages through English as the pivot, allowing our LexEcho Head to project them into a shared English lexicon. While architecturally there is no restriction on the selection of the pivot language, we select English because of its rich resources and the availability of LSR teacher models for alignment, which we discuss later in this section.

**LexEcho Head.** The LexEcho head produces a dual-view lexical representation from the projected states **Z** . It generates two complementary sparse views: ① an _Pivot (English) View_ that captures semantic concepts in English and ② a _Source View_ that preserves important source input tokens.

① _Pivot (English) View_ : The English lexical representation is generated by an English MLM head, as in LSR models like SPLADE (Lassance et al., 2024), but our multilingual connector extends this to the 39+ languages supported by our base model.

Multilingual representations **Z** (Eq. 3) are linearly refined and decoded onto the English vocabulary _Ve_ via an embedding matrix _**E** ∈_ R _[|][V][e][|×][d][e]_ and bias **b** _v_ , yielding logits that score each source token against every English token.

**==> picture [357 x 16] intentionally omitted <==**

Here, we define the log-saturation effect function, introduced by MacAvaney et al. (2020); Formal _·_ et al. (2021) as LogSat( ) for simplicity,

**==> picture [267 x 11] intentionally omitted <==**

Next, max-pooling across source tokens ( _n_ ) yields the final English lexical representation:

**==> picture [331 x 19] intentionally omitted <==**

This English view **t**[(] _[e]_[)] is sparse and includes not only direct translations ( _live_ , _music_ , _phone_ ) but semantically related terms ( _song_ , _stream_ , _step_ ) that supports semantic retrieval.

② _Source View_ : The connector maps common concepts into English but can fail on uncommon or unseen entities, especially in non-Latin scripts (e.g., _Momo_ in Figure 1), or when names differ across languages (e.g., _Douyin_ vs. _TikTok_ ). Scaling model size alone cannot solve this, as new entities continually appear.

[page 5]

Published as a conference paper at ICLR 2026

Our LexEcho head tackles this by selectively echoing key tokens from the source. A dedicated [ **ECHO** ] token in the MLM head, denoted _Dec_ **[ECHO]** ( _·_ ), produces a weight vector **w** for each source token to ensure crucial tokens are selected:

**==> picture [275 x 12] intentionally omitted <==**

By combining the English **t**[(] _[e]_[)] and the weighted source views _{_ **s**[(] _i[l]_[)] _[,]_ **[ w]** _[i][}] i[n]_ =1[,][MILCO][produces][a] dual-view representation **o** = _{_ **t**[(] _[e]_[)] _,_ **s**[(] _[l]_[)] _,_ **w** _}_ that leverages cross-lingual projection to form a unified lexical view preserving crucial source-language tokens that would otherwise be lost in translation.

## 3.2 TRAINING: SPARSE ALIGNMENT AND CONTRASTIVE REFINEMENT

We propose a two-stage training recipe for MILCO: Sparse Alignment Pretraining to ground multilingual text to English lexical space, followed by Sparse Contrastive Training to refine alignment and optimize retrieval effectiveness, with sparsity enforced throughout.

**Sparse Alignment Pretraining (SAP).** To ensure the English view **t**[(] _[e]_[)] is grounded in the English lexicon, we leverage widely available parallel (xx–en) sentences to align the English view of a non-English sentence to the representation of its corresponding English sentence. Given a pair of tokenized parallel sentences ( **s**[(] _[ℓ]_[)] _,_ **s**[(] _[e]_[)] ) in language _ℓ_ and English, we employ an oracle teacher English LSR model, such as SPLADEv3 (Lassance et al., 2024), denoted as LSR _[∗]_ , to produce the target English sparse representation **t** _[∗]_ .

We design a sparse-aware MSE (SMSE) loss, specifically to minimize the difference between two sparse vectors. Since most coordinates are zero, the learning signal should concentrate on the few active ones. Also, with the LogSat( _·_ ) activation, negative pre-activation values yield zero gradients. Therefore, we compute the loss directly on the decoded logits, i.e. _Dec_ ( **Z** ), which were the input to _·_ LogSat( ), with max-pooling across the input tokens and restrict it to coordinates where at least one side is positive. For clarity, we denote such augmented representations as[˜] **t**[(] _[e]_[)] and[˜] **t** _[∗]_ . Formally, the SMSE loss can be written as

**==> picture [334 x 41] intentionally omitted <==**

where **1** ( _·_ ) denotes the indicator function. This SMSE objective mitigates gradient dilution and focuses training on informative lexical coordinates, yielding more stable alignment. During training, we apply SMSE over batches flattened into single vectors.

**Sparse Contrastive Training (SCT).** Alignment pretraining grounds multilingual inputs in a shared English lexicon but is not directly optimized for retrieval. To improve effectiveness, we further train MILCO with a LexEcho head using a contrastive objective on retrieval datasets. Following Lassance et al. (2024), we use a KL distillation loss (details in Section A.7) to transfer knowledge from a cross-encoder to MILCO. To promote sparsity, we add _ℓ_ 1-norm regularization on query and document representations _q_ and _p_ . Concretely, the training objective is _L_ contrastive = _L_ KLD + _αq∥q∥_ 1 + _αd∥p∥_ 1, where the _ℓ_ 1-norms are implemented as means over the training batch.

## 4 EXPERIMENTAL SETTINGS

**Pretraining, Training and Evaluation Data.** For Sparse Alignment Pretraining, we use 594M bitext pairs from diverse domains collected with Sentence Transformers (Reimers & Gurevych, 2019), where each pair contains an English sentence and its translation. Dataset statistics are shown in Table 14. For Sparse Contrastive Training, we adopt the 1.4M multilingual queries released by Chen et al. (2024), with positive/negative documents and teacher scores obtained from bge-rerankerv2.5[2] reranker. More details are in Table 15.

> 2bge-reranker-v2.5-gemma2-lightweight

[page 6]

Published as a conference paper at ICLR 2026

Following Chen et al. (2024), we evaluate MILCO on four benchmarks: MIRACL (Zhang et al., b), a large-scale multilingual retrieval benchmark covering 18 languages with high-quality human annotations; MTEB v2 (Enevoldsen et al., 2025) for large-scale multilingual retrieval; MLDR (Chen et al., 2024), a multilingual long-document retrieval benchmark in 13 languages; and MKQA (Longpre et al., 2021), a cross-lingual benchmark with English documents and queries in 25 languages. Additional results on BEIR (Thakur et al., 2021), NeuCLIR (Lawrie et al., 2024) and LIMIT (Weller et al., 2025) are also included in the Appendix. Our evaluation spans 39 languages in total.

Table 1: Multilingual passage retrieval performance on the MIRACL dev set (measured by nDCG@10). Superscript _[∗]_ : results obtained from Lassance (2023).

|Table 1:<br>Multilingual passage retrieval performance on the MIRACL dev set (measured by<br>nDCG@10). Superscript _∗_: results obtained from Lassance(2023).|Table 1:<br>Multilingual passage retrieval performance on the MIRACL dev set (measured by<br>nDCG@10). Superscript _∗_: results obtained from Lassance(2023).|
|---|---|
|**Model**<br>**Size**<br>**Avg**<br>**ar**<br>**bn**<br>**en**<br>**es**<br>**fa**<br>**f**<br>**fr**<br>**hi**<br>**id**<br>**ja**<br>**ko**<br>**ru**<br>**sw**<br>**te**<br>**th**<br>**zh**<br>**de**<br>**yo**||
|_Dense, multi-vector and hybrid baselines_||
|mE5large<br>560M<br>66.6<br>E5mistral-7b<br>7.11B<br>63.4<br>M3-Dense<br>560M<br>69.2<br>M3-Multi-vec<br>560M<br>70.5<br>M3-Dense+Sparse<br>560M<br>70.4<br>M3-Dense+Sparse+Multivector<br>560M<br>71.5<br>PLAID-X (Multivector)<br>560M<br>55.5<br>Qwen3-Embed - 0.6B<br>596M<br>60.5<br>Qwen3-Embed - 8B<br>7.57B<br>69.8<br>MILCO-dense (align + distill)<br>560M<br>67.9<br>MILCO-dense (distill)<br>560M<br>70.9|76.0<br>75.9<br>52.9<br>52.9<br>59.0<br>77.8<br>54.5<br>62.0<br>52.9<br>70.6<br>66.5<br>67.4<br>74.9<br>84.6<br>80.2<br>56.0<br>56.4<br>78.3<br>73.3<br>70.3<br>57.3<br>52.2<br>52.1<br>74.7<br>55.2<br>52.1<br>52.7<br>66.8<br>61.8<br>67.7<br>68.4<br>73.9<br>74.0<br>54.0<br>54.1<br>79.7<br>78.4<br>80.0<br>56.9<br>56.1<br>60.9<br>78.6<br>58.3<br>59.5<br>56.1<br>72.8<br>69.9<br>70.1<br>78.7<br>86.2<br>82.6<br>62.7<br>56.7<br>81.8<br>79.6<br>81.0<br>59.3<br>57.8<br>62.0<br>80.1<br>59.4<br>61.5<br>58.3<br>74.5<br>71.2<br>71.2<br>79.1<br>87.9<br>83.0<br>63.7<br>58.0<br>82.4<br>79.6<br>80.7<br>58.8<br>58.1<br>62.3<br>79.7<br>58.0<br>62.9<br>58.3<br>73.9<br>71.2<br>69.8<br>78.5<br>87.2<br>83.1<br>63.5<br>57.7<br>83.3<br>80.2<br>81.5<br>59.6<br>59.7<br>**63.4**<br>80.4<br>61.2<br>63.3<br>59.0<br>75.2<br>72.1<br>71.7<br>79.6<br>88.1<br>83.7<br>64.9<br>59.8<br>83.5<br>66.0<br>68.0<br>46.4<br>51.4<br>48.3<br>52.5<br>61.9<br>42.8<br>56.8<br>44.6<br>61.2<br>63.4<br>61.2<br>32.9<br>75.6<br>**72.0**<br>44.5<br>49.1<br>69.9<br>66.3<br>51.5<br>54.2<br>52.7<br>69.7<br>54.4<br>51.3<br>51.4<br>63.3<br>60.1<br>59.7<br>48.6<br>77.2<br>73.8<br>58.3<br>52.9<br>74.0<br>78.2<br>78.3<br>59.8<br>59.6<br>60.5<br>79.0<br>61.0<br>63.1<br>56.1<br>74.3<br>67.5<br>73.5<br>72.2<br>84.3<br>81.5<br>63.3<br>60.5<br>84.5<br>77.0<br>76.6<br>55.3<br>57.5<br>60.2<br>77.1<br>59.0<br>60.5<br>55.5<br>70.5<br>70.9<br>67.5<br>74.4<br>86.1<br>80.6<br>62.5<br>57.6<br>72.8<br>79.5<br>80.2<br>56.8<br>60.4<br>**63.4**<br>78.5<br>**62.6**<br>62.2<br>58.4<br>74.7<br>70.5<br>72.1<br>79.6<br>87.0<br>82.9<br>64.2<br>59.5<br>83.2|
|_Sparse baselines_||
|BM25<br>2<br>31.9<br>T-Splade_∗_<br>3.4B<br>54.5<br>mSPLADEsTok_∗_<br>-<br>63.9<br>OpenSearch3<br>167M<br>M3-Sparse<br>560M<br>53.9|39.5<br>48.2<br>26.7<br>7.7<br>28.7<br>45.8<br>11.5<br>35.0<br>29.7<br>31.2<br>37.1<br>25.6<br>35.1<br>38.3<br>49.1<br>17.5<br>12.0<br>56.1<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>–<br>74.0<br>67.0<br>57.5<br>54.2<br>51.4<br>76.7<br>55.8<br>48.6<br>58.2<br>66.9<br>60.7<br>65.8<br>76.8<br>74.0<br>–<br>56.2<br>–<br>–<br>67.1<br>68.9<br>43.8<br>38.6<br>45.1<br>65.4<br>35.3<br>48.2<br>48.9<br>56.1<br>61.5<br>44.5<br>57.9<br>79.1<br>70.9<br>36.1<br>32.5<br>70.0|
|①**MILCO**(SAP, SCTKD, LexEcho)<br>560M<br>**72.3**<br>②**MILCO**(SAP, SCTKD, MLMen)<br>560M<br>69.4<br>③**MILCO**(SAP, SCT, LexEcho)<br>560M<br>70.1<br>④**MILCO**(SAP, MLMen)<br>560M<br>54.5<br>⑤**MILCO**(SCTKD, MLMen)<br>560M<br>59.2<br>⑥**noMILCO**(SCTKD, MLMm)<br>560M<br>50.7|**80.4**<br>**82.6**<br>**60.4**<br>**60.9**<br>62.3<br>**81.2**<br>61.7<br>**64.4**<br>**60.9**<br>**77.2**<br>**72.1**<br>**74.6**<br>**80.3**<br>**87.9**<br>**84.2**<br>65.5<br>**61.4**<br>**83.6**<br>77.3<br>79.5<br>57.6<br>59.7<br>58.5<br>78.8<br>60.6<br>63.4<br>57.7<br>72.8<br>67.7<br>72.6<br>78.1<br>82.3<br>80.4<br>60.6<br>59.7<br>81.2<br>79.4<br>80.8<br>57.6<br>57.2<br>60.6<br>80.1<br>57.7<br>63.3<br>58.4<br>75.2<br>71.0<br>72.6<br>77.2<br>87.2<br>82.7<br>60.8<br>59.3<br>81.6<br>59.8<br>59.7<br>57.0<br>56.0<br>44.9<br>66.0<br>48.2<br>58.6<br>48.8<br>54.9<br>59.4<br>51.2<br>47.8<br>55.0<br>55.9<br>46.7<br>48.5<br>62.2<br>72.7<br>72.3<br>47.7<br>47.6<br>50.9<br>72.5<br>48.8<br>50.4<br>51.8<br>64.0<br>62.7<br>53.6<br>62.3<br>77.7<br>72.8<br>46.2<br>44.8<br>66.2<br>65.8<br>62.0<br>39.7<br>39.4<br>42.0<br>67.0<br>38.5<br>36.9<br>44.9<br>56.1<br>52.9<br>47.3<br>58.6<br>71.0<br>67.0<br>41.8<br>34.6<br>46.9|

**Baselines.** We compare MILCO against two group of baselines: Dense/Multi-vector and Sparse methods. _For dense/multi-vector baselines_ , we include recent state-of-the-art methods, including multilingual E5 (Wang et al., 2024), BGE-M3 (Chen et al., 2024), PLAID-X (Yang et al., 2024b), Qwen3 Embeddings (Zhang et al., 2025). _For sparse baselines_ , we include unsupervised BM25, M3-Sparse (Chen et al., 2024) and also OpenSearch (Shen et al., 2025), T-Splade (Lassance, 2023), mSplade (Lassance, 2023). Among these, T-Splade is the approach that translates text into English and encodes the translated text by the Splade model (Formal et al., 2021).

**MILCO configurations.** We consider the following configurations in experiments:

- ① MILCO (SAP, SCTKD, LexEcho): Our strongest setup, which combines alignment with contrastive distillation training and the LexEcho head, producing dual-view lexical representations.

- ② MILCO (SAP, SCTKD, MLMen): Similar to (1), but the source view is removed from LexEcho’s output, producing only English lexical representations.

- ③ MILCO (SAP, SCT, LexEcho): Similar to (1), but without distillation. Instead, the InfoNCE loss (Oord et al., 2018) with in-batch negatives is used for Sparse Contrastive Training.

- ④ MILCO (SAP, MLMen): Similar to (2), but without Sparse Contrastive Training.

- ⑤ MILCO (SCTKD, MLMen): Similar to (2), but without Sparse Alignment Pre-training.

- ⑥ noMILCO (SCTKD, MLMm): A baseline model trained directly with the full multilingual MLM head (without our multilingual connector).

We initialized MILCO from the _bge-m3-unsupervised_[4] multilingual base encoder and initialized the LexEcho head with Splade-v3’s English MLM head (Lassance et al., 2024). We use Spladev3 representations of English text for alignment pretraining. More details on hyperparameters and hardware are provided in Section A.8 of the Appendix.

> 4BAAI/bge-m3-unsupervised

[page 7]

Published as a conference paper at ICLR 2026

## 5 RESULTS AND DISCUSSION

**RQ1: How does MILCO perform compared to state-of-the-art baselines?** Table 1 reports the performance of MILCO and baselines on the MIRACL benchmark (18 languages). Overall, the MILCO ① model, trained with our two-stage pipeline and LexEcho head, achieves the highest effectiveness with an average nDCG@10 of 72.3.

Against sparse baselines, MILCO outperforms M3-Sparse (Chen et al., 2024) by 34.1%, T- Splade (Lassance, 2023) by 32.7%, and MSpladesTok (Lassance, 2023) by 13.1%. Against dense baselines, MILCO still shows substantially higher effectiveness, though with smaller margins. Compared to models of similar size, it outperforms Qwen3 0.6B (Zhang et al., 2025) and M3Dense (Chen et al., 2024) by 19.5% and 4.5%, respectively, on MIRACL. This advantage generalizes to 39 languages on MTEB v2 cross-lingual and multilingual retrieval (Table 3). Despite being _∼_ 14 _×_ smaller, it outperforms E5-Mistral 7B (Wang et al., 2023) and Qwen3 8B on MIRACL, though Qwen3 8B performs better on MTEBv2 where it better leverages task-specific instructions. We additionally train two dense baselines using the same backbone and training data as MILCO. The first, MILCO-dense (align + distill), which uses dense alignment to thenlper/gte-base[5] and distillation, achieves an average nDCG@10 of 67.9 on MIRACL. A variant trained with distillation only performs better, reaching 70.9 nDCG@10 on MIRACL. However, both dense baselines still substantially underperform our best sparse MILCO① trained with the two-stage recipe.

Table 2: Performance on Multilingual Long Table 3: Performance on multilingual and crossDocument Retrieval (nDCG@10, 13 languages). lingual retrieval tasks on Multilingual MTEBv2. More language-specific details in Table 6. (39 languages). More details in Table 7.

|**Model**|**Size**|**Max Length**|**Avg**|**Model**|**Size**|**Avg**|
|---|---|---|---|---|---|---|
|_Dense, multi-vector and hybrid baselines_||||_Large Models (≥1B)_|||
|mE5large|560M|512|34.2|Qwen3-Embed-8B|8B|**75.59**|
|E5mistral-7b|7B|8192|42.6|jina-embeddings-v4|3.8B|73.84|
|M3-Dense|560M|8192|52.5|inf-retriever-v1|7.1B|71.21|
|M3-Multi-vector|560M|8192|57.6|SFR-Embedding-Mistral|7.1B|68.50|
|M3-Dense+Sparse|560M|8192|64.8|gte-Qwen2-7B-inst|7B|67.22|
|M3-All|560M|8192|65.0|inf-retriever-v1-1.5b|1.5B|65.34|
|mGTE-TRM Dense|304M|8192|56.9|gte-Qwen2-1.5B-inst|1.5B|65.12|
|mGTE-TRM Dense + Sparse|304M|8192|71.3|GritLM-7B|7B|62.82|
|PLAID-X (Multi-vector)|560M|512|74.2|NV-Embed-v2|7.9B|58.65|
|Qwen3-Embed-0.6B|0.6B|32768|50.1|NV-Embed-v1|7.9B|56.64|
|Qwen3-Embed-8B<br>_Sparse baselines_|8B|32678|59.1|_Small Models (<1B)_<br>gte-multilingual-base|305M|64.72|
|BM25|2|8192|53.6|Qwen3-Embed-0.6B|0.6B|63.93|
|M3-Sparse|560M|8192|62.2|bge-m3|560M|62.02|
|mGTE-TRM Sparse|304M|8192|71.0|granite-278m-multi|278M|55.80|
|①**MILCO**(SAP, SCTKD, LexEcho)<br>②**MILCO**(SAP, SCTKD, MLMen)|560M<br>560M|512<br>512|**74.4**<br>69.9|granite-107m-multi<br>①**MILCO**(SAP, SCTKD, LexEcho)|107M<br>560M|49.88<br>66.83|

We further evaluate MILCO on the Multilingual Long Document Retrieval (MLDR) benchmark (Table 2). Because MILCO is trained with a 512-token limit, we split long documents into 512token passages and score documents by their best passage. Under this setup, MILCO achieves an average nDCG@10 of 74.4, which is 14% higher than M3-All, the dense+sparse+multi-vector ensemble, and substantially surpasses Qwen3 0.6B and 8B with native long-context support.

In the Appendices, we report results on LIMIT Test (Weller et al., 2025) (Table 11) and BEIR (Thakur et al., 2021) (Table 10). On LIMIT, MILCO substantially outperforms all dense baselines regardless of size. On BEIR (English), it trails Qwen3 0.6B slightly, but scales better on large collections.

**RQ2: What is the effect of sparse alignment and contrastive training in MILCO?** We observe that Sparse Alignment Pretraining is crucial to ensure that the model’s output is grounded in the English vocabulary. In Figure 2, we show two examples of MILCO’s output under three training setups. Without SAP, contrastive training leads to semantic collapse, where the model produces

> 5thenlper/gte-base is similar in size and BEIR (English) performance to our SPLADE-v3 sparse English teacher (GTE-base: 52.61 nDCG@10, SPLADE-v3: 51.69 nDCG@10).

[page 8]

Published as a conference paper at ICLR 2026

completely random and unexplainable (latent) output tokens with no clear relation to the input. We observe the same effect when we train **noMILCO** ⑥, a multilingual LSR model without the multilingual connector (similar to Splade training). With alignment pretraining, MILCO produces understandable and semantically equivalent English tokens as demonstrated in the figure. However, we observe that both Alignment-only and Contrastive-only result in mediocre multilingual retrieval effectiveness. On MIRACL results in Table 1, Alignment-only **MILCO** ④ and Contrastive-only **MILCO** ⑤ only achieve the average nDCG@10 of 54.5 and 59.2 respectively. Direct training without our connector (noMILCO ⑥) leads to a larger drop in performance, resulting in nDCG@10 of 50.7.

To further improve retrieval effectiveness, we finetune MILCO on retrieval data with a contrastive objective. We experiment with two contrastive losses: InfoNCE with dataset-provided labels (MILCO ③) and KL divergence for knowledge distillation (MILCO ①). With an InfoNCE loss, MILCO ③’s average nDCG@10 improves by 28.62%, from 54.5 with only alignment to 70.1, becoming competitive to BGE-M3-Dense and Multi-vector models. Adding distillation further boosts effectiveness, increasing nDCG@10 to 72.3 and making MILCO subtantially outperform all baselines, including the hybrid BGE-M3 dense-sparse-multivector model and Qwen3 models.

**RQ3: Does the proposed LexEcho head improve robustness?** Unlike dense or multi-vector methods, the transparency of MILCO’s sparse, lexicalized representations make errors traceable. When analyzing the English view, we found that representations often miss uncommon entities like _Momo_ in Figure 3, leading to reduced retrieval accuracy. In the figure, Doc2 (score = 9.64) is ranked below Doc1 (score = 9.89), despite being more relevant.

The LexEcho head addresses this with a dual-view representation composed of an English view and a source view. When an important entity is missing from the English view, MILCO can fall back to the source view for source-token matching. In Figure 3, LexEcho seems to recognize the model’s missing knowledge of _Momo_ in English and assigns a high weight to `陌` in the Chinese view. In contrast, for _Apple_ , the model relies primarily on English representations (assigning them the highest weights in Doc1 and Doc3) while assigning `苹果` ( _Apple_ ) a low weight in the Chinese view.

On MIRACL (Table 1), MILCO ① with a LexEcho head consistently outperforms MILCO ② with only an English view across all 18 languages, achieving an average nDCG@10 of 72.3 (+4.17% over 69.4). The largest gains occur in non-Latin languages such as Chinese (zh: +8.09%), Telugu (te: +6.8%), Farsi (fa: +6.5%), Korean (ko: +6.5%), and Japanese (ja: +6.04%), where mapping entities into English is particularly difficult since entities could be named differently in English. The benefits of the LexEcho head also extend to long-document retrieval: on MLDR (Table 2), MILCO with LexEcho achieves 74.4 nDCG@10, a 6.43% improvement over MILCO with only an English view (69.5). These highlight the broader robustness of our approach.

**RQ4: Can MILCO perform zero-shot cross-lingual retrieval?** MILCO uses the multilingual connector to maps text across languages into a unified English lexical view. This allows MILCO to perform zero-shot cross-lingual retrieval, which is not possible with sparse models like M3-Sparse that rely on only a source view. We benchmark the cross-lingual capability of MILCO (zero-shot) and baselines on MKQA with R@100 in Table 4.

Prior sparse methods (e.g., BM25, BGE-M3-Sparse) generate source-view representations including input tokens with scalar weights. Their vocabularies are language-specific, so inputs in Chinese

|**Alignment Only**|**Alignment + Contrastive**|**Contrastive Only**|
|---|---|---|
|Input (de)**:**Baltimore Maryland die großartigste Stadt in Amerika (_Baltimore Maryland the greatest city in America_)|||
|**baltimore**(2.22),**maryland**(1.86),**city**(1.40),<br>**greatest**(1.25),**biggest**(0.98),**garrison**(0.35),<br>**geography**(0.31),**tourism**(0.19) …|**baltimore**(1.77),**city**(1.52),**maryland**(1.23),<br>**america**(1.19),**greatest**(0.89),**usa**(0.81),<br>**best**(0.62),**urban**(0.26) …|**governing**(1.17),**past**(1.07),**match**(0.95),<br>**worn**(0.86),**sky**(0.65),**gas**(0.52),**boot**(0.34),<br>**mayor**(0.31) …|
|Input (vi): Giá trị tài sản ròng của Tesla là bao nhiêu? (_What is Tesla’s net worth?_)|||
|**tesla**(3.36),**worth**(2.61),**price**(1.84),**net**(1.52),<br>**salary**(1.14),**money**(0.80),**mining**(0.35),<br>**generation**(0.33) …|**tesla**(3.02),**worth**(1.89),**price**(1.47),**net**(1.37),<br>**wealth**(0.71),**asset**(0.63),**stock**(0.42),<br>**company**(0.41) …|**relative**(0.97),**drinks**(0.75),**gaelic**(0.75),<br>**contaminated**(0.73),**sigh**(0.67),**webb**(0.60),<br>**dust**(0.46),**‒**(1.22)  …|

Figure 2: Sparse representations with different training strategies. _Alignment only_ produces many grounded tokens ( **green** ) but also distantly relevant tokens ( **orange** ), _Contrastive_ further prunes and refines. _Contrastive-only_ suffers from semantic collapse, drifting toward ungrounded tokens ( **red** ).

[page 9]

Published as a conference paper at ICLR 2026

|**Input**|**Translation**|**(1) LexEcho (English View)**|**(2) LexEcho (Source View)**|**Score (1)**|**Score (1)+(2)**|
|---|---|---|---|---|---|
|**Query:**<br>陌陌直播音乐怎么导<br>入手机?|How to import**Momo**Live Music<br>into mobile phone?|music(1.16), import(0.95), phone(0.88), step(0.80),<br>transfer(0.72), no(0.69), songs(0.55), live(0.51),<br>song(0.49), phones(0.46), stream(0.44) ...<br><br> <br>?|陌(1.46),  手机(0.97),  导(0.68),  直播(0.67),<br>音乐(0.65),  <s>(0.38),  怎么(0.38),  入(0.36),<br>(0.34),  ▁(0.19)|||
|**Doc1:**用户可将苹果音<br>乐歌曲下载或录音保<br>存，再导入手机播放|Users can download**Apple**Music<br>songs and then import them into<br>their phones …|**apple**(1.72), music(1.58), step(1.33), songs(1.30),<br>download(1.27), phone(1.18), is(1.18), play(1.14),<br>song(1.09), can(1.03), save(1.03), app(0.95),...<br> <br>(<br>|音乐(0.46),  用户(0.45),  歌曲(0.44),  选择<br>0.40),  导(0.40),  的方式(0.34),  上的(0.34),<br>保存(0.28),  可以(0.27),苹果(0.23) …|**9.89**<br>Rank 1|**11.66**<br>Rank 2|
|**Doc2:** 陌陌直播的歌<br>曲可以用保存功能转<br>到手机.|Songs from**Momo**Live can be<br>saved to your phone using the<br>save function.|step(1.62), songs(1.32), save(1.29), phone(1.20),<br>song(1.15), music(1.07), storage(1.01), live(0.84),<br>can(0.81), transfer(0.81), stream(0.79), …<br> <br>(<br>(|陌(1.54),  歌曲(0.72),  直播(0.71),  功能<br>0.67),  手机(0.64),  你可以(0.59),  保存<br>0.56),  用(0.54),  ▁(0.53),  把(0.51) ...|**9.64**<br>Rank 2|**13.27**<br>Rank 1|

Figure 3: The tail entity _Momo_ is missing in the English view of the query and Doc2, reducing Doc2’s score despite its higher relevance. The LexEcho head resolves this by selectively retaining missing entities from source tokens, correctly ranking Doc2 on top.

yield only Chinese tokens. This causes vocabulary mismatch and poor cross-lingual retrieval, with average R@100 scores of just 39.9 and 45.3 on MKQA. In contrast, MILCO avoids this issue with a shared English lexical space. Despite not being trained for cross-lingual retrieval, MILCO achieves strong results on MKQA, with a zero-shot R@100 of 76.6, improving 91.9% and 69.1% over BM25 and BGE-M3-Sparse, respectively.

Dense and multi-vector methods operate in a latent space, so they do not suffer from vocabulary mismatch and perform reasonably well on MKQA. BGE-Dense and multivector models are among the strongest baselines, with an average R@100 of around 75. While these methods outperform sparse baselines (e.g., BM25 or BGE-M3Sparse), MILCO achieves about 1.7–1.9% higher R@100 than the BGE dense and multi-vector baselines, while also retaining the transparency that facilitate model analysis and error tracing. MILCO is about 9% and 12.8% better than E5-Mistral 7B and Qwen3 8B, respectively, despite having only 560M parameters.

6 EFFICIENCY AND EFFECTIVENESS TRADEOFFS

Table 4: Cross-lingual retrieval performance on MKQA, averaged across 25 languages. More details in Table 9.

|languages. More details in Table 9.|languages. More details in Table 9.|
|---|---|
|**Model**<br>**Avg (R@100)**||
|**Baselines**||
|E5-large<br>E5-mistral-7b<br>BGE-M3 Dense<br>BGE-M3 Multi-Vec<br>BGE-M3 Dense+Sparse<br>PLAID-X (multivector)<br>Qwen3-Embed-0.6B<br>Qwen3-Embed-8B<br>BM25<br>BGE-M3 Sparse|70.9<br>70.1<br>75.1<br>75.3<br>75.3<br>73.4<br>54.4<br>67.9<br>39.9<br>45.3|
|||
|①**MILCO**(SAP, SCTKD, LexEcho)<br>**76.6**||

**Model Size vs. Effectiveness.** In Figure 4, we plot MILCO’s effectiveness against model size compared to baselines. We observe that MILCO, with 560M parameters, is the most effective model within its size range and even substantially outperforms larger models (e.g., Qwen3-8B and E5-Mistral-7B) across all 18 MIRACL languages. With the same model size, the BGE-M3-Multivector model underperforms MILCO despite producing multiple dense vectors for each query/document.

**Sparsity vs. Effectiveness.** Dense retrieval models like Matryoshka representations (Kusupati et al., 2022) support truncating embeddings for efficiency, but require additional Matryoshka training losses. MILCO and LSR methods naturally allow post-hoc pruning (Lei et al., 2025; Wen et al., 2025; Bruch et al., 2024), because LSR encodes queries and documents as weighted tokens that can be ranked and truncated at inference. Unlike Matryoshka, which applies the same truncation size to all inputs, LSR supports variable _k_ (e.g., fewer tokens for shorter texts). Figure 5 compares two pruning strategies: top- _k_ pruning and mass-based pruning, which removes the p-tail percentile of token weights, yielding variable tokens per document. Exact numbers are included in the Appendix 12. Mass-based pruning delivers a slightly more favorable trade-off than top-k pruning. At _p_ = 95, it averages only 30 tokens/document yet already surpasses Qwen3-Embed 0.6B on nDCG@10 (62.2). It reaches 96% of full performance at _p_ = 86 (86.4 tokens/doc) and achieves SOTA at 300 tokens, with only marginal gains beyond. With LexEcho’s vocabulary of 280k terms, activating just 300 tokens (0.1%) yields representations that are 99.9% sparse, transparent, and highly effective.

**Sparsity vs. Efficiency.** We report index statistics and retrieval latency with MILCO under an inverted-index setting. We use Seismic (Bruch et al., 2024), an ANN method built on top of an inverted index. All results are on MIRACL (English subset, about 32M passages), with retrieval run

[page 10]

Published as a conference paper at ICLR 2026

**==> picture [396 x 143] intentionally omitted <==**

**----- Start of picture text -----**<br>
72.3<br>70 M3-Multi-vecM3-Dense MILCO LexEcho MILCO MLM _ en Qwen3 8B 70 67.4 70.6<br>E5large<br>E5mistral 7B<br>Qwen3 0.6B 60<br>60 56.0<br>M3-Sparse T-Splade* 50 Top-K Pruning<br>50 Mass-based Pruning<br>M3-Sparse (53.9)<br>Model Type<br>mContriever Dense Qwen3-0.6B (61.23)<br>mDPR Sparse 40 M3-Multivector (70.5)<br>0.1 0.2 0.5 1 2 5 10 0 100 200 300 400<br>Model Size (Billion Parameters, log scale) Tokens Kept<br>nDCG@10 nDCG@10<br>**----- End of picture text -----**<br>

Figure 4: Model size versus effectiveness on MIRACL. MILCO is lightweight (560M params), while being highly effective.

Figure 5: Effectiveness (nDCG@10, MIRACL) of MILCO with varying sparsity levels obtained by post-hoc pruning methods.

Table 5: Retrieval Latency of MILCO sparse retrieval with Seismic and Qwen3-Embedding-0.6B dense retrieval with Faiss.

|**Model**|**Index**|**Avg Latency (ms)**|**P95 Latency (ms)**|**QPS**|**nDCG@10**|**Index Size**|
|---|---|---|---|---|---|---|
|Qwen3-Embed-0.6B|HNSW|1.29|1.47|777|50.4|134G|
|MILCO (p=0)|Seismic|1.85|4.32|538|56.4|61G|
|MILCO (p=10)|Seismic|1.29|2.92|774|56.3|40G|
|MILCO (p=30)|Seismic|0.61|1.26|1647|54.4|25G|
|MILCO (p=50)|Seismic|0.65|1.33|1545|53.3|16G|
|MILCO (p=60)|Seismic|0.44|0.82|2265|50.3|12G|

on a single AMD EPYC 7763 CPU core. We build several indexes of the pivot view with hyperparameters (n ~~p~~ ostings=15000, query ~~c~~ ut=10, heap ~~f~~ actor=0 _._ 9) and different amounts of post-hoc pruning. The unpruned index ( _p_ = 0) has an average posting-list length of 4636.09, resulting in a 61 GB index and an average retrieval latency of 1.85 ms/query. We then prune the lowest-weight dimensions whose cumulative weights account for _p ∈{_ 10 _,_ 30 _,_ 50 _,_ 60 _}_ % of the total, which shrinks the inverted index and speeds up retrieval. Results are shown in Table 5.

Regarding index size, post-hoc pruning substantially shrinks the index: 40 GB at _p_ = 10, 25 GB at _p_ = 30, 16 GB at _p_ = 50, and 12 GB at _p_ = 60. Thus, at the most aggressive pruning level, we reduce index size by roughly 80% while keeping strong retrieval effectiveness. To contextualize these index sizes, we compare against Qwen3-Embedding-0.6B with a Faiss dense HNSW index (Douze et al., 2024) (M = 32, ef = 64) on the same hardware and collection. This dense baseline has an index size of 134 GB, whereas MILCO’s pruned Seismic index is already smaller at _p_ = 10 (40 GB) and becomes 5–10 _×_ smaller at higher pruning levels (25 GB at _p_ = 30, 12 GB at _p_ = 60).

Regarding latency, pruning also yields consistent improvements over the full representation: _p_ = 10 reduces average latency from 1.85 ms to 1.29 ms ( _∼_ 30% speed-up) with virtually no loss in nDCG@10 (56.4 _→_ 56.3), _p_ = 30 makes queries about 3 _×_ faster (0.61 ms, nDCG@10 = 54.4), and even _p_ = 60 achieves a _>_ 4 _×_ speed-up (0.44 ms) while remaining competitive (nDCG@10 = 50.3). For comparison, the Qwen3-Embedding-0.6B + Faiss HNSW achieves an average latency of 1.29 ms and nDCG@10 = 50.4. Seismic’s ANN inverted index with pruning therefore allows MILCO to (i) match this latency at _p_ = 10 while achieving substantially higher effectiveness (nDCG@10 = 56.3), and (ii) further reduce latency to _≈_ 0 _._ 44 ms at _p_ = 60, while remaining at least as effective overall.

## 7 CONCLUSION

We introduced MILCO, a novel multilingual learned sparse retriever that connects 39 languages to a shared English lexical space through a lightweight connector. Alignment pretraining enables the use of contrastive training, whereas the LexEcho preserves entities lost during cross-lingual projection. MILCO delivers strong zero-shot cross-lingual retrieval, showing competitive performance without cross-lingual retrieval training. Overall, MILCO achieves state-of-the-art multilingual retrieval results, while offering transparent representations and efficient post-hoc pruning.

[page 11]

Published as a conference paper at ICLR 2026

## REPRODUCIBILITY STATEMENT

We have taken several measures to ensure the transparency and reproducibility of our work.

**Datasets.** All datasets used for pretraining and training MILCO models are publicly available. Table 14 (Appendix) reports statistics on the number and sources of parallel sentences used for Sparse Alignment Pretraining, while Table 15 (Appendix) describes the datasets used for Sparse Contrastive Training. These datasets are widely adopted in prior work on dense retrieval (Wang et al., 2024; Chen et al., 2024; Li et al.). We note, however, that some recent models such as Qwen3Embed (Zhang et al., 2025) do not disclose their training data, which makes direct comparisons not strictly fair.

**Hyper-parameters and hardware.** All hyper-parameters and hardware specifications used for Sparse Alignment and Sparse Contrastive Training are described in Section A.8 (Appendix). Any hyper-parameters not explicitly listed are set to the default values provided in HuggingFace’s Trainer (Wolf et al., 2019), which we use to train our models. During pretraining and training, we hard-coded the random seed to 42.

## **Code.** Our code is available at: https://github.com/thongnt99/milco.

**Models and evaluation.** MILCO is trained on 63 languages and evaluated on 39 languages, as detailed in Section A.9 (Appendix). Trained MILCO checkpoints are released at: https:// github.com/thongnt99/milco. To illustrate the multilingual capabilities of our model, we provide example inputs and their corresponding sparse representations across multiple languages in Section A.1 (Appendix).

## ETHICS STATEMENT

We present MILCO, a multilingual learned sparse retrieval method supporting 39 languages. All datasets and models used to train MILCO are publicly available, and we do not introduce any proprietary or sensitive data. Since our work builds on public data, it may reflect biases present in those sources. We aims to broaden access to multilingual information retrieval research, especially for underrepresented languages.

## ACKNOWLEDGMENT

This research was supported by the Hybrid Intelligence Center, a 10-year program funded by the Dutch Ministry of Education, Culture and Science through the Netherlands Organisation for Scientific Research, project VI.Vidi.223.166 of the NWO Talent Programme which is (partly) financed by the Dutch Research Council (NWO). We acknowledge the Dutch Research Council for awarding this project access to the LUMI supercomputer, owned by the EuroHPC Joint Undertaking, hosted by CSC (Finland) and the LUMI consortium through project number NWO-2024.050.

## REFERENCES

- Luiz Bonifacio, Vitor Jeronymo, Hugo Queiroz Abonizio, Israel Campiotti, Marzieh Fadaee, Roberto Lotufo, and Rodrigo Nogueira. mmarco: A multilingual version of the ms marco passage ranking dataset. _arXiv:2108.13897_ , 2021.

- Sebastian Bruch, Franco Maria Nardini, Cosimo Rulli, and Rossano Venturini. Efficient inverted indexes for approximate retrieval over learned sparse representations. In _Proc. of SIGIR_ , pp. 152–162, 2024.

- Daniel Campos, Alessandro Magnani, and Chengxiang Zhai. Quick dense retrievers consume KALE: Post training KullbackLeibler alignment of embeddings for asymmetrical dual encoders. In _Proc. of ACL Workshop on SustaiNLP_ , pp. 59–77, 2023.

- Jianlv Chen, Shitao Xiao, Peitian Zhang, Kun Luo, Defu Lian, and Zheng Liu. Bge m3-embedding: Multi-lingual, multi-functionality, multi-granularity text embeddings through self-knowledge distillation. _arXiv:2402.03216_ , 2024.

[page 12]

Published as a conference paper at ICLR 2026

Zewen Chi, Li Dong, Furu Wei, Nan Yang, Saksham Singhal, Wenhui Wang, Xia Song, Xian-Ling Mao, Heyan Huang, and Ming Zhou. InfoXLM: An information-theoretic framework for crosslingual language model pre-training. In _Proc. of NAACL-HLT_ .

- Arman Cohan, Sergey Feldman, Iz Beltagy, Doug Downey, and Daniel S Weld. Specter: Documentlevel representation learning using citation-informed transformers. In _Proc. of ACL_ , pp. 2270– 2282, 2020.

- Alexis Conneau, Kartikay Khandelwal, Naman Goyal, Vishrav Chaudhary, Guillaume Wenzek, Francisco Guzm´an, Edouard[´] Grave, Myle Ott, Luke Zettlemoyer, and Veselin Stoyanov. Unsupervised cross-lingual representation learning at scale. In _Proc. of ACL_ , pp. 8440–8451, 2020.

- Matthijs Douze, Alexandr Guzhva, Chengqi Deng, Jeff Johnson, Gergely Szilvasy, PierreEmmanuel Mazar´e, Maria Lomeli, Lucas Hosseini, and Herv´e J´egou. The faiss library. 2024.

- Kenneth Enevoldsen, Isaac Chung, Imene Kerboua, M´arton Kardos, Ashwin Mathur, David Stap, Jay Gala, Wissam Siblini, Dominik Krzemi´nski, Genta Indra Winata, et al. Mmteb: Massive multilingual text embedding benchmark. _arXiv:2502.13595_ , 2025.

- Angela Fan, Yacine Jernite, Ethan Perez, David Grangier, Jason Weston, and Michael Auli. Eli5: Long form question answering. In _Proc. of ACL_ , pp. 3558–3567, 2019.

- Fangxiaoyu Feng, Yinfei Yang, Daniel Cer, Naveen Arivazhagan, and Wei Wang. Languageagnostic bert sentence embedding. In _Proc. of ACL (Volume 1: Long Papers)_ , pp. 878–891, 2022.

- Thibault Formal, Benjamin Piwowarski, and St´ephane Clinchant. Splade: Sparse lexical and expansion model for first stage ranking. In _Proc. of SIGIR_ , pp. 2288–2292, 2021.

- Thibault Formal, Carlos Lassance, Benjamin Piwowarski, and St´ephane Clinchant. From distillation to hard negative sampling: Making sparse neural ir models more effective. In _Proc. of SIGIR_ , pp. 2353–2359, 2022.

- Martin Gellerstam. Translationese in swedish novels translated from english. _Translation studies in Scandinavia_ , 1:88–95, 1986.

- Wei He, Kai Liu, Jing Liu, Yajuan Lyu, Shiqi Zhao, Xinyan Xiao, Yuan Liu, Yizhong Wang, Hua Wu, Qiaoqiao She, et al. Dureader: a chinese machine reading comprehension dataset from realworld applications. _arXiv:1711.05073_ , 2017.

- Mandar Joshi, Eunsol Choi, Daniel Weld, and Luke Zettlemoyer. TriviaQA: A large scale distantly supervised challenge dataset for reading comprehension. In _Proc. of ACL (Volume 1: Long Papers)_ , 2017.

- Seungyeon Kim, Ankit Singh Rawat, Manzil Zaheer, Sadeep Jayasumana, Veeranjaneyulu Sadhanala, Wittawat Jitkrittum, Aditya Krishna Menon, Rob Fergus, and Sanjiv Kumar. Embeddistill: A geometric knowledge distillation for information retrieval. _arXiv:2301.12005_ , 2023.

- Aditya Kusupati, Gantavya Bhatt, Aniket Rege, Matthew Wallingford, Aditya Sinha, Vivek Ramanujan, William Howard-Snyder, Kaifeng Chen, Sham Kakade, Prateek Jain, et al. Matryoshka representation learning. _Proc. of NeurIPS_ , 35:30233–30249, 2022.

- Tom Kwiatkowski, Jennimaria Palomaki, Olivia Redfield, Michael Collins, Ankur Parikh, Chris Alberti, Danielle Epstein, Illia Polosukhin, Jacob Devlin, Kenton Lee, et al. Natural questions: a benchmark for question answering research. _Transactions of the Association for Computational Linguistics_ , 7:453–466, 2019.

- Carlos Lassance. Extending english ir methods to multi-lingual ir. _arXiv:2302.14723_ , 2023.

- Carlos Lassance, Herv´e D´ejean, Thibault Formal, and St´ephane Clinchant. Splade-v3: New baselines for splade. _arXiv:2403.06789_ , 2024.

- Dawn Lawrie, Sean MacAvaney, James Mayfield, Paul McNamee, Douglas W Oard, Luca Soldaini, and Eugene Yang. Overview of the trec 2023 neuclir track. 2024.

[page 13]

Published as a conference paper at ICLR 2026

Yibin Lei, Tao Shen, Yu Cao, and Andrew Yates. Enhancing lexicon-based text embeddings with large language models. In _Proc. of ACL (Volume 1: Long Papers)_ , 2025.

- Chaofan Li, Minghao Qin, Shitao Xiao, Jianlyu Chen, Kun Luo, Defu Lian, Yingxia Shao, and Zheng Liu. Making text embedders few-shot learners. In _Proc. of ICLR_ .

- Jimmy Lin and Xueguang Ma. A few brief notes on deepimpact, coil, and a conceptual framework for information retrieval techniques. _arXiv:2106.14807_ , 2021.

- Shayne Longpre, Yi Lu, and Joachim Daiber. MKQA: A linguistically diverse benchmark for multilingual open domain question answering. _Trans. of ACL_ , 9, 2021.

- Antoine Louis, Vageesh Saxena, Gijs van Dijck, and Gerasimos Spanakis. ColBERT-XM: A modular multi-vector representation model for zero-shot multilingual information retrieval. _arXiv:2402.15059_ , 2024.

- Sean MacAvaney, Franco Maria Nardini, Raffaele Perego, Nicola Tonellotto, Nazli Goharian, and Ophir Frieder. Expansion via prediction of importance with contextualization. In _Proc. of SIGIR_ , pp. 1573–1576, 2020.

- Macedo Maia, Siegfried Handschuh, Andr´e Freitas, Brian Davis, Ross McDermott, Manel Zarrouk, and Alexandra Balahur. Www’18 open challenge: financial opinion mining and question answering. In _In Proc. WWW_ , pp. 1941–1942, 2018.

- Suraj Nair, Eugene Yang, Dawn Lawrie, Kevin Duh, Paul McNamee, Kenton Murray, James Mayfield, and Douglas W Oard. Transfer learning approaches for building cross-language dense retrieval models. In _In Proc. of ECIR_ , pp. 382–396. Springer, 2022a.

- Suraj Nair, Eugene Yang, Dawn J Lawrie, James Mayfield, and Douglas W Oard. Learning a sparse representation model for neural clir. In _DESIRES_ , pp. 53–64, 2022b.

- Suraj Nair, Eugene Yang, Dawn Lawrie, James Mayfield, and Douglas W Oard. Blade: combining vocabulary pruning and intermediate pretraining for scaleable neural clir. In _Proc. of SIGIR_ , pp. 1219–1229, 2023.

- Franco Maria Nardini, Thong Nguyen, Cosimo Rulli, Rossano Venturini, and Andrew Yates. Effective inference-free retrieval for learned sparse representations. In _Proc. of SIGIR_ , pp. 2936–2940, 2025.

- Thong Nguyen, Sean MacAvaney, and Andrew Yates. A unified framework for learned sparse retrieval. In _In Proc. of ECIR_ , pp. 101–116. Springer, 2023.

- Thong Nguyen, Mariya Hendriksen, Andrew Yates, and Maarten de Rijke. Multimodal learned sparse retrieval with probabilistic expansion control. In _In Proc. of ECIR_ , pp. 448–464. Springer, 2024.

- Tri Nguyen, Mir Rosenberg, Xia Song, Jianfeng Gao, Saurabh Tiwary, Rangan Majumder, and Li Deng. Ms marco: A human-generated machine reading comprehension dataset. _arXiv:1611.09268_ , 2016.

- Aaron van den Oord, Yazhe Li, and Oriol Vinyals. Representation learning with contrastive predictive coding. _arXiv:1807.03748_ , 2018.

- Pranav Rajpurkar, Jian Zhang, Konstantin Lopyrev, and Percy Liang. Squad: 100,000+ questions for machine comprehension of text. In _Proc. of EMNLP_ , pp. 2383–2392, 2016.

- Nils Reimers and Iryna Gurevych. Sentence-bert: Sentence embeddings using siamese bertnetworks. In _Proc. of EMNLP-IJCNLP_ , pp. 3982–3992, 2019.

- Nils Reimers and Iryna Gurevych. Making monolingual sentence embeddings multilingual using knowledge distillation. In _Proc. of EMNLP (EMNLP)_ , pp. 4512–4525, 2020.

- Parker Riley, Isaac Caswell, Markus Freitag, and David Grangier. Translationese as a language in “multilingual” NMT. In _Proc. of ACL_ , 2020.

[page 14]

Published as a conference paper at ICLR 2026

- Lakshay Sharma, Laura Graesser, Nikita Nangia, and Utku Evci. Natural language understanding with the quora question pairs dataset. _arXiv:1907.01041_ , 2019.

- Xinjie Shen, Zhichao Geng, and Yang Yang. Exploring l0 sparsification for inference-free sparse retrievers. In _Proc. of SIGIR_ , pp. 2572–2576, 2025.

- Nandan Thakur, Nils Reimers, Andreas R¨uckl´e, Abhishek Srivastava, and Iryna Gurevych. BEIR: A heterogeneous benchmark for zero-shot evaluation of information retrieval models. In _Proc. of NeurIPS_ , 2021.

- James Thorne, Andreas Vlachos, Christos Christodoulopoulos, and Arpit Mittal. FEVER: a largescale dataset for fact extraction and VERification. In _Proc. of NAACL-HLT (Volume 1: Long Papers)_ , 2018.

- Henning Wachsmuth, Shahbaz Syed, and Benno Stein. Retrieval of the best counterargument without prior topic knowledge. In _Proc. of ACL (Volume 1: Long Papers)_ , pp. 241–251, 2018.

- Liang Wang, Nan Yang, Xiaolong Huang, Linjun Yang, Rangan Majumder, and Furu Wei. Improving text embeddings with large language models. _arXiv:2401.00368_ , 2023.

- Liang Wang, Nan Yang, Xiaolong Huang, Linjun Yang, Rangan Majumder, and Furu Wei. Multilingual e5 text embeddings: A technical report. _arXiv:2402.05672_ , 2024.

- Orion Weller, Michael Boratko, Iftekhar Naim, and Jinhyuk Lee. On the theoretical limitations of embedding-based retrieval. _arXiv:2508.21038_ , 2025.

- Tiansheng Wen, Yifei Wang, Zequn Zeng, Zhong Peng, Yudi Su, Xinyang Liu, Bo Chen, Hongwei Liu, Stefanie Jegelka, and Chenyu You. Beyond matryoshka: Revisiting sparse coding for adaptive representation. _arXiv:2503.01776_ , 2025.

- Thomas Wolf, Lysandre Debut, Victor Sanh, Julien Chaumond, Clement Delangue, Anthony Moi, Pierric Cistac, Tim Rault, R´emi Louf, Morgan Funtowicz, et al. Huggingface’s transformers: State-of-the-art natural language processing. _arXiv:1910.03771_ , 2019.

- Xiaohui Xie, Qian Dong, Bingning Wang, Feiyang Lv, Ting Yao, Weinan Gan, Zhijing Wu, Xiangsheng Li, Haitao Li, Yiqun Liu, et al. T2ranking: A large-scale chinese benchmark for passage ranking. In _Proc. of SIGIR_ , pp. 2681–2690, 2023.

- Eugene Yang, Suraj Nair, Ramraj Chandradevan, Rebecca Iglesias-Flores, and Douglas W Oard. C3: Continued pretraining with contrastive weak supervision for cross language ad-hoc retrieval. In _Proc. of SIGIR_ , pp. 2507–2512, 2022.

- Eugene Yang, Dawn Lawrie, and James Mayfield. Distillation for multilingual information retrieval. In _Proc. of SIGIR_ , pp. 2368–2373, 2024a.

- Eugene Yang, Dawn Lawrie, James Mayfield, Douglas W. Oard, and Scott Miller. Translate-distill: Learning cross-language dense retrieval by translation and distillation. In _Proc. of ECIR_ , 2024b.

- Zhilin Yang, Peng Qi, Saizheng Zhang, Yoshua Bengio, William Cohen, Ruslan Salakhutdinov, and Christopher D Manning. Hotpotqa: A dataset for diverse, explainable multi-hop question answering. In _Proc. of EMNLP_ , pp. 2369–2380, 2018.

- Hamed Zamani, Mostafa Dehghani, W Bruce Croft, Erik Learned-Miller, and Jaap Kamps. From neural re-ranking to neural ranking: Learning a sparse representation for inverted indexing. In _Proc. of CIKM_ , pp. 497–506, 2018.

- Crystina Zhang, Jing Lu, Vinh Q Tran, Tal Schuster, Donald Metzler, and Jimmy Lin. Tomato, tomahto, tomate: Do multilingual language models understand based on subword-level semantic concepts? In _Proc. of NAACL (Findings)_ , a.

- Xinyu Zhang, Nandan Thakur, Odunayo Ogundepo, Ehsan Kamalloo, David Alfonso-Hermelo, Xiaoguang Li, Qun Liu, Mehdi Rezagholizadeh, and Jimmy Lin. MIRACL: A multilingual retrieval dataset covering 18 diverse languages. _Trans. Assoc. Comput. Linguist._ , b.

[page 15]

Published as a conference paper at ICLR 2026

- Xinyu Zhang, Xueguang Ma, Peng Shi, and Jimmy Lin. Mr. tydi: A multi-lingual benchmark for dense retrieval. _arXiv:2108.08787_ , 2021.

- Xinyu Zhang, Kelechi Ogueji, Xueguang Ma, and Jimmy Lin. Toward Best Practices for Training Multilingual Dense Retrieval Models. _ACM Trans. Inf. Syst._ , 42(2):1–33, 2024.

- Yanzhao Zhang, Mingxin Li, Dingkun Long, Xin Zhang, Huan Lin, Baosong Yang, Pengjun Xie, An Yang, Dayiheng Liu, Junyang Lin, et al. Qwen3 embedding: Advancing text embedding and reranking through foundation models. _arXiv:2506.05176_ , 2025.

[page 16]

Published as a conference paper at ICLR 2026

## A APPENDIX

## A.1 DEMONSTRATION EXAMPLES

In Figure 6, we present a list of demonstration examples. The inputs are in different languages, while the outputs are bag-of-words English tokens produced by our ① **MILCO** (SAP, SCTKD, LexEcho) model. These examples illustrate that MILCO generates transparent representations, making it possible for humans to interpret, inspect, and trace potential errors or biases.

**==> picture [393 x 515] intentionally omitted <==**

**----- Start of picture text -----**<br>
ID Language Input Text Sparse Representation (English View)<br>{"tesla": 3.4, "worth": 2.72, "net": 1.7, "price": 1.65, "salary": 0.8, "nikola": 0.78,<br>1 en what is tesla net worth? "stock": 0.58, "electric": 0.52, "car": 0.49, "generation": 0.49, "money": 0.48, "levi":<br>0.42, "mining": 0.31, "company": 0.27, "sale": 0.2, "milan": 0.12, "edmund": 0.12,<br>"revenue": 0.06}<br>{"tesla": 3.35, "worth": 2.79, "net": 1.73, "price": 1.56, "salary": 1.03, "money": 0.78,<br>1 hi टे�ला क� कुल संप�� �या है? "generation": 0.51, "stock": 0.5, "nikola": 0.49, "electric": 0.4, "car": 0.31, "company": 0.29, "mining": 0.29, "levi": 0.25, "wealth": 0.17, "total": 0.16, "sale": 0.11, "milan":<br>0.1}<br>{"tesla": 3.35, "worth": 2.71, "price": 1.91, "net": 1.76, "salary": 1.35, "money": 0.95,<br>1 zh 特斯拉的净资产是多少？ "stock": 0.79, "company": 0.58, "electric": 0.54, "nikola": 0.54, "generation": 0.49,<br>"car": 0.34, "mining": 0.32, "levi": 0.19, "motors": 0.15, "total": 0.03}<br>{"tesla": 3.34, "worth": 2.69, "net": 1.94, "price": 1.51, "stock": 0.78, "salary": 0.68,<br>1 de Was ist Teslas Nettowert? "money": 0.62, "electric": 0.48, "nikola": 0.46, "generation": 0.43, "sale": 0.34, "car":<br>0.25, "levi": 0.22, "company": 0.19, "mining": 0.16, "milan": 0.11, "wealth": 0.11,<br>"edmund": 0.11, "currently": 0.1, "revenue": 0.1}<br>{"tesla": 3.36, "worth": 2.75, "net": 1.89, "price": 1.66, "salary": 0.99, "stock": 0.87,<br>1 nl Wat is de nettowaarde van Tesla? "money": 0.61, "electric": 0.55, "nikola": 0.49, "company": 0.41, "generation": 0.41,<br>"sale": 0.32, "levi": 0.27, "mining": 0.23, "car": 0.22, "revenue": 0.15, "edmund": 0.12,<br>"currently": 0.11, "wealth": 0.08, "investment": 0.06}<br>{"tesla": 3.31, "worth": 2.64, "net": 1.81, "price": 1.52, "salary": 0.85, "stock": 0.82,<br>1 arﻣﺎ ھﻲ اﻟﻘﯾﻣﺔ اﻟﺻﺎﻓﯾﺔ ﻟﺷرﻛﺔ ﺗﯾﺳﻼ؟ "money": 0.58, "company": 0.53, "electric": 0.43, "levi": 0.43, "generation": 0.42,<br>"nikola": 0.28, "mining": 0.26, "revenue": 0.22, "sale": 0.18, "car": 0.16, "total": 0.1,<br>"investment": 0.08, "currently": 0.03, "wealth": 0.03}<br>{"tesla": 3.36, "worth": 2.61, "price": 1.84, "net": 1.52, "salary": 1.14, "money": 0.8,<br>1 vi Giá trị tài sản ròng của Tesla là bao nhiêu? "stock": 0.7, "electric": 0.52, "nikola": 0.45, "mining": 0.35, "generation": 0.33, "sale":<br>0.27, "company": 0.25, "milan": 0.21, "car": 0.16, "wealth": 0.16, "investment": 0.14,<br>"levi": 0.09, "revenue": 0.08, "total": 0.05}<br>{"baltimore": 2.47, "maryland": 2.07, "greatest": 1.68, "city": 1.59, "biggest": 1.38,<br>2 en Baltimore Maryland the greatest city in America "md": 1.26, "america": 1.11, "usa": 1.09, "great": 0.98, "cities": 0.93, "town": 0.7,<br>"american": 0.47, "us": 0.45, "urban": 0.41, "birthplace": 0.41, "was": 0.34, "famous":<br>0.29, "garrison": 0.25, "beautiful": 0.23, "geography": 0.21}<br>{"baltimore": 2.63, "maryland": 2.08, "largest": 1.7, "city": 1.55, "biggest": 1.5, "md":<br>2 hi बा�ट�मोर मैर�ल�ड अमे�रका का सबसे बड़ा शहर 1.49, "usa": 1.14, "cities": 1.06, "us": 0.78, "town": 0.65, "america": 0.65, "population": 0.64, "urban": 0.48, "metropolitan": 0.34, "census": 0.31, "garrison": 0.3,<br>"geography": 0.29, "size": 0.26, "headquarters": 0.26, "big": 0.19}<br>{"baltimore": 2.66, "maryland": 2.07, "greatest": 1.85, "city": 1.73, "md": 1.65,<br>2 zh 马里兰州巴尔的摩是美国最伟大的城市 "biggest": 1.53, "usa": 1.38, "great": 1.29, "cities": 1.26, "us": 1.02, "america": 0.91,<br>"town": 0.81, "best": 0.66, "urban": 0.61, "geography": 0.57, "birthplace": 0.57,<br>"beautiful": 0.55, "garrison": 0.51, "headquarters": 0.47, "location": 0.46}<br>{"baltimore": 2.22, "maryland": 1.86, "city": 1.4, "greatest": 1.25, "md": 1.16,<br>2 de Baltimore Maryland die großartigste Stadt in Amerika "biggest": 0.98, "great": 0.96, "cities": 0.95, "usa": 0.94, "america": 0.91, "town": 0.69, "beautiful": 0.57, "most": 0.52, "american": 0.49, "us": 0.46, "urban": 0.43, "best":<br>0.37, "garrison": 0.35, "geography": 0.31, "birthplace": 0.29}<br>{"baltimore": 2.35, "maryland": 2.0, "best": 1.94, "city": 1.51, "md": 1.27, "usa": 1.17,<br>2 nl Baltimore Maryland de beste stad in Amerika "america": 1.11, "beautiful": 1.05, "cities": 1.02, "biggest": 0.89, "town": 0.77,<br>"american": 0.61, "us": 0.54, "urban": 0.49, "birthplace": 0.37, "garrison": 0.35,<br>"popular": 0.3, "tourism": 0.29, "location": 0.28, "headquarters": 0.27}<br>{"baltimore": 2.57, "maryland": 2.09, "city": 1.63, "greatest": 1.55, "md": 1.53,<br>2 arﺑﺎﻟﺗﯾﻣور ﻣﺎرﯾﻼﻧد أﻋظم ﻣدﯾﻧﺔ ﻓﻲ أﻣرﯾﻛﺎ "biggest": 1.36, "great": 1.24, "usa": 1.21, "cities": 1.15, "america": 1.14, "town": 0.72,<br>"garrison": 0.66, "us": 0.61, "location": 0.57, "urban": 0.57, "headquarters": 0.53,<br>"american": 0.52, "best": 0.47, "beautiful": 0.43, "birthplace": 0.42}<br>{"baltimore": 2.45, "maryland": 2.05, "city": 1.47, "biggest": 1.38, "md": 1.28,<br>2 vi Baltimore Maryland thành phố vĩ đại nhất ở Mỹ "greatest": 1.08, "usa": 1.05, "cities": 0.95, "largest": 0.92, "us": 0.71, "america": 0.69,<br>"town": 0.65, "great": 0.47, "urban": 0.42, "headquarters": 0.34, "metropolitan": 0.3,<br>"garrison": 0.29, "population": 0.27, "metropolis": 0.22, "american": 0.21}<br>{"import": 1.6, "music": 1.46, "live": 1.17, "phone": 1.16, "imported": 0.95, "songs":<br>3 zh 有谁知道陌陌直播的音乐怎么导入手机里 0.86, "app": 0.84, "step": 0.71, "youtube": 0.68, "phones": 0.65, "stream": 0.63, "no":<br>0.62, "button": 0.62, "download": 0.58, "song": 0.48, "pandora": 0.48, "mp3": 0.47,<br>"player": 0.46, "sync": 0.46, "transfer": 0.45}<br>Alan Smithee is a pseudonym for a fictional director  {"alan": 3.02, "##ee": 3.0, "smith": 2.95, "pseudonym": 2.15, "director": 2.05,<br>4 de responsible for films in which the actual director does not want his name associated with the work. From  "directors": 1.93, "fictional": 1.9, "##ga": 1.86, "guild": 1.85, "responsible": 1.61, "d": 1.58, "who": 1.49, "film": 1.34, "alias": 1.29, "directed": 1.26, "##ees": 1.2, "actual":<br>1968 to 2000, it was recommended by the Directors  1.09, "1968": 1.07, "recommended": 1.05, "directing": 1.04}<br>Guild of America (DGA) for such situations.<br>Paul Jules Antoine Meillet, né le à Moulins (Allier) et  {"mei": 2.9, "##llet": 2.73, "jules": 2.62, "paul": 2.57, "antoine": 2.46, "##ulin": 2.41,<br>5 fr mort le à Châteaumeillant (Cher), est le principal  "allie": 2.3, "linguist": 2.21, "french": 2.08, "cher": 2.04, "chateau": 1.84, "france":<br>linguiste français des premières décennies du . Il est  1.77, "##mei": 1.72, "mo": 1.7, "who": 1.69, "linguistics": 1.66, "##llan": 1.6, "born":<br>aussi philologue. 1.51, "died": 1.39, "##let": 1.34}<br>金章宗完顏璟 女真名麻達葛，金朝第6位皇帝（1189年1<br>月20日—1208年12月29日在位），在位19年，享年41岁。 {"dynasty": 2.19, "emperor": 2.03, "qing": 2.01, "ming": 1.96, "sima": 1.8, "kim": 1.69,<br>6 zh 章宗為金世宗完颜雍之嫡孙，其在位期間修訂國內律法， "sixth": 1.67, "mongolian": 1.64, "6": 1.61, "khan": 1.54, "korea": 1.45, "age": 1.44,<br>政治清明，史稱明昌之治。章宗統治下的金朝文化發展達 "##chang": 1.44, "dynasties": 1.42, "date": 1.36, "who": 1.33, "died": 1.32, "china":<br>至頂峰，但同時軍事能力卻也日益低下，蒙古帝國也於同 1.31, "reign": 1.31, "empire": 1.3}<br>時崛起<br>**----- End of picture text -----**<br>

Figure 6: Examples of MILCO’s output representations (English view) on different languages.

[page 17]

Published as a conference paper at ICLR 2026

## A.2 DETAILED MULTILINGUAL/CROSS-LINGUAL RETRIEVAL RESULTS

In this section, we show the detailed language-specific results of MILCO and baselines in the following multilingual and cross-lingual retrieval datasets. The result on Multilingual Long Document Retrieval (MLDR) is shown in Table 6. The result on MTEBv2 (multilingual and cross-lingual tasks) is shown in Table 7. The result on the NeuCLIR benchmark (cross-lingual retrieval) is shown in Table 8. The result on MKQA (cross-lingual retrieval) is shown in Table 9.

Table 6: Multilingual (long) document retrieval on the MLDR (measured by nDCG@10).

|Table 6: Multilingual(long)document retrieval on the MLDR(measured bynDCG@10).|Table 6: Multilingual(long)document retrieval on the MLDR(measured bynDCG@10).|
|---|---|
|**Model**<br>**Max Length**<br>**Avg**<br>**ar**<br>**de**<br>**en**<br>**es**<br>**fr**<br>**hi**<br>**it**<br>**ja**<br>**ko**<br>**pt**<br>**ru**<br>**th**<br>**zh**||
|_Dense and multi-vector baselines_||
|mE5large<br>512<br>34.2<br>E5mistral-7b<br>8192<br>42.6<br>M3-Dense<br>8192<br>52.5<br>M3-Multi-vector<br>8192<br>57.6<br>M3-Dense+Sparse<br>8192<br>64.8<br>M3-All<br>8192<br>65.0<br>PLAID-X (Multi-vector)<br>512<br>74.2<br>Qwen3-Embed - 0.6B<br>32768<br>50.1<br>Qwen3-Embed - 8B<br>32678<br>59.1|33.0<br>26.9<br>33.0<br>51.1<br>49.5<br>21.0<br>43.1<br>29.9<br>27.1<br>58.7<br>42.4<br>15.9<br>13.2<br>29.6<br>40.6<br>43.3<br>70.2<br>60.5<br>23.2<br>55.3<br>41.6<br>32.7<br>69.5<br>52.4<br>18.2<br>16.8<br>47.6<br>46.1<br>48.9<br>74.8<br>73.8<br>40.7<br>62.7<br>50.9<br>42.9<br>74.4<br>59.5<br>33.6<br>26.0<br>56.6<br>50.4<br>55.8<br>79.5<br>77.2<br>46.6<br>66.6<br>52.8<br>48.8<br>77.5<br>64.2<br>39.4<br>32.7<br>63.0<br>56.4<br>64.2<br>88.7<br>84.2<br>52.3<br>75.8<br>58.5<br>53.1<br>86.0<br>75.6<br>42.9<br>42.0<br>64.7<br>57.9<br>63.8<br>86.8<br>83.9<br>52.2<br>75.5<br>60.1<br>55.7<br>85.4<br>73.8<br>44.7<br>40.0<br>78.5<br>65.5<br>81.4<br>90.9<br>87.5<br>64.0<br>84.2<br>67.3<br>66.9<br>85.5<br>86.9<br>43.7<br>62.7<br>44.7<br>45.0<br>75.5<br>48.4<br>69.7<br>24.8<br>62.6<br>49.7<br>38.3<br>73.2<br>61.2<br>30.7<br>26.9<br>57.7<br>54.5<br>86.1<br>56.1<br>79.5<br>35.1<br>72.7<br>58.3<br>50.4<br>79.6<br>69.6<br>37.9<br>30.8|
|_Sparse baselines_||
|BM25<br>8192<br>53.6<br>M3-Sparse<br>8192<br>62.2|45.1<br>52.6<br>57.0<br>78.0<br>75.7<br>43.7<br>70.9<br>36.2<br>25.7<br>82.6<br>61.3<br>33.6<br>34.6<br>58.7<br>53.0<br>62.1<br>87.4<br>82.7<br>49.6<br>74.7<br>53.9<br>47.9<br>85.2<br>72.9<br>40.3<br>40.5|
|①**MILCO**(SAP, SCTKD, LexEcho)<br>512<br>**74.4**|**75.3**<br>**66.1**<br>**82.5**<br>**93.2**<br>**90.8**<br>**59.5**<br>**81.9**<br>**68.8**<br>**67.9**<br>**90.7**<br>**85.5**<br>**45.8**<br>**59.0**|

Table 7: Performance of embedding models on MTEBv2’s multilingual and cross-lingual retrieval tasks (Enevoldsen et al., 2025). MILCO outperforms other models with similar sizes (e.g, Qwen30.6B, BGE-M3), while under-performs larger models, such as Qwen3-Embed-8B. (M = Multilingual, C = Cross-lingual). We evaluate English-only retrieval tasks separately in Section A.3.

|**Model**|**Avg.**|**Belebele (M)**|**MIRACL-HN (M)**|**MLQA (C)**|**Statcan (M)**|**Twitter (M)**|**Wiki (C)**|
|---|---|---|---|---|---|---|---|
|gte-multilingual-base|64.72|77.60|64.17|72.19|21.74|68.92|83.69|
|bge-m3|62.02|78.16|69.59|74.81|21.86|37.82|89.87|
|granite-278m-multi|55.80|62.20|59.45|62.99|30.14|34.98|85.06|
|granite-125m-eng|26.99|33.37|16.35|22.90|30.71|5.92|52.70|
|granite-107m-multi|49.88|55.12|57.25|60.47|27.50|17.06|81.88|
|gte-Qwen2-7B-inst|67.22|77.54|51.58|78.69|37.87|68.64|88.97|
|gte-Qwen2-1.5B-inst|65.12|66.59|63.23|72.89|33.25|67.01|87.77|
|NV-Embed-v2|58.65|69.79|55.54|70.61|19.55|45.57|90.83|
|inf-retriever-v1|71.21|77.37|60.93|80.31|37.30|79.30|92.02|
|jina-embeddings-v4|73.84|74.29|62.95|74.90|58.07|84.38|88.46|
|inf-retriever-v1-1.5b|65.34|66.06|62.35|72.93|31.31|70.46|88.93|
|Qwen3-Embed-0.6B|63.93|68.74|61.23|72.79|33.63|60.04|87.13|
|Qwen3-Embed-8B|75.59|88.81|70.58|83.55|40.46|78.20|91.96|
|①**MILCO**(SAP, SCTKD, LexEcho)|66.83|80.72|72.65|83.00|24.00|50.00|90.63|

Table 8: Results on NeuCLIR cross-lingual benchmarks (Lawrie et al., 2024) on three languages (Chinese, Persian, and Russian). The Avg. MLIR score (nDCG@20) is the mean across the two years. Our 560M MILCO model outperforms Qwen3 0.6B, but falls behind PLAID-X and Qwen3Embed 4B/8B. PLAID-X focuses exclusively on the test languages.

|**Model**|**2023 MLIR (C)**|**2024 MLIR (C)**|**Avg. MLIR (C)**|
|---|---|---|---|
|SPLADE v3 (transl. docs)|0.420|0.440|0.430|
|PLAID-X|0.404|0.468|0.436|
|Qwen3-Embed 0.6B|0.317|0.311|0.314|
|Qwen3-Embed 4B|0.440|0.415|0.428|
|Qwen3-Embed 8B|0.434|0.419|0.427|
|①**MILCO**(SAP, SCTKD, LexEcho)|0.395|0.427|0.411|

[page 18]

Published as a conference paper at ICLR 2026

Table 9: Cross-lingual retrieval performance on MKQA (Recall@100). Abbreviations: mCtr = mContriever, OA3 = OpenAI-3, PLD = PLAID-X, Q0.6 = Qwen3-0.6B, Q8 = Qwen3-8B.

|**Lang**|**Dense Baselines**<br>**Sparse Baselines**<br>**_MILCO_**<br>**mDPR**<br>**mCtr**<br>**E5-L**<br>**E5-M7B**<br>**OA3**<br>**M3-D**<br>**M3-MV**<br>**M3-DS**<br>**M3-All**<br>**PLD**<br>**Q0.6**<br>**Q8**<br>**BM25**<br>**M3-S**|**Dense Baselines**<br>**Sparse Baselines**<br>**_MILCO_**<br>**mDPR**<br>**mCtr**<br>**E5-L**<br>**E5-M7B**<br>**OA3**<br>**M3-D**<br>**M3-MV**<br>**M3-DS**<br>**M3-All**<br>**PLD**<br>**Q0.6**<br>**Q8**<br>**BM25**<br>**M3-S**|**Dense Baselines**<br>**Sparse Baselines**<br>**_MILCO_**<br>**mDPR**<br>**mCtr**<br>**E5-L**<br>**E5-M7B**<br>**OA3**<br>**M3-D**<br>**M3-MV**<br>**M3-DS**<br>**M3-All**<br>**PLD**<br>**Q0.6**<br>**Q8**<br>**BM25**<br>**M3-S**|
|---|---|---|---|
|ar<br>da<br>de<br>es<br>f<br>fr<br>he<br>hu<br>it<br>ja<br>km<br>ko<br>ms<br>nl<br>no<br>pl<br>pt<br>ru<br>sv<br>th<br>tr<br>vi<br>zh<br>~~c~~n<br>zh<br>~~h~~k<br>zh<br>~~t~~w|48.2<br>58.2<br>68.7<br>59.6<br>65.6<br>71.1<br>71.4<br>71.1<br>71.5<br>64.2<br>44.8<br>64.75<br>67.4<br>73.9<br>77.4<br>77.8<br>73.6<br>77.2<br>77.5<br>77.4<br>77.6<br>77.0<br>57.9<br>69.89<br>65.8<br>71.7<br>76.9<br>77.0<br>73.6<br>76.2<br>76.3<br>76.4<br>76.3<br>76.0<br>61.6<br>69.69<br>66.8<br>72.6<br>76.6<br>77.4<br>73.9<br>76.4<br>76.6<br>76.7<br>76.9<br>75.7<br>62.5<br>70.75<br>56.2<br>70.2<br>74.0<br>72.0<br>72.7<br>75.1<br>75.3<br>75.7<br>75.6<br>70.5<br>46.5<br>65.06<br>68.2<br>73.8<br>76.5<br>77.0<br>76.2<br>76.2<br>76.4<br>76.6<br>76.6<br>76.1<br>61.8<br>70.22<br>49.7<br>63.2<br>69.0<br>67.2<br>58.1<br>72.4<br>72.9<br>72.5<br>73.0<br>70.5<br>39.0<br>62.68<br>60.4<br>69.7<br>74.7<br>75.0<br>71.2<br>74.7<br>74.6<br>74.9<br>75.0<br>72.2<br>43.7<br>65.07<br>66.0<br>72.3<br>76.8<br>77.1<br>73.6<br>76.0<br>76.4<br>76.3<br>76.5<br>75.2<br>61.3<br>69.98<br>60.3<br>64.8<br>71.5<br>65.1<br>71.9<br>75.0<br>75.1<br>75.0<br>75.2<br>75.2<br>57.2<br>69.45<br>29.5<br>26.8<br>33.4<br>34.3<br>33.9<br>68.6<br>69.1<br>68.8<br>69.2<br>63.7<br>24.6<br>52.76<br>50.9<br>59.7<br>68.1<br>59.4<br>73.3<br>71.6<br>71.7<br>71.6<br>71.8<br>70.7<br>47.2<br>65.51<br>65.5<br>74.1<br>76.3<br>77.0<br>73.3<br>77.2<br>77.4<br>77.4<br>77.4<br>75.5<br>59.8<br>70.06<br>68.2<br>73.7<br>77.0<br>79.1<br>74.2<br>77.2<br>77.7<br>77.7<br>77.6<br>76.5<br>58.6<br>71.23<br>66.7<br>73.5<br>77.3<br>76.6<br>73.3<br>77.1<br>77.2<br>77.4<br>77.4<br>76.3<br>55.9<br>69.09<br>67.0<br>71.5<br>73.0<br>77.1<br>73.3<br>76.3<br>76.5<br>76.3<br>76.4<br>75.1<br>54.7<br>68.86<br>65.5<br>72.6<br>73.5<br>77.5<br>73.7<br>76.3<br>76.4<br>76.5<br>76.4<br>74.4<br>61.0<br>69.97<br>62.7<br>69.8<br>76.8<br>75.5<br>72.0<br>76.2<br>76.4<br>76.2<br>76.5<br>76.2<br>58.9<br>69.65<br>66.9<br>73.2<br>77.6<br>78.3<br>74.0<br>76.9<br>77.2<br>77.4<br>77.4<br>76.5<br>55.8<br>69.71<br>53.8<br>66.9<br>76.0<br>67.4<br>65.2<br>75.6<br>75.9<br>76.0<br>76.6<br>76.2<br>56.3<br>69.72<br>59.1<br>71.1<br>74.3<br>74.9<br>75.2<br>75.6<br>75.9<br>76.0<br>76.0<br>72.0<br>52.1<br>66.57<br>63.4<br>70.9<br>75.4<br>77.0<br>71.1<br>76.6<br>76.7<br>76.8<br>76.9<br>74.3<br>57.6<br>69.09<br>63.7<br>68.1<br>56.6<br>69.3<br>70.7<br>74.6<br>74.9<br>74.7<br>75.0<br>72.7<br>62.1<br>69.51<br>62.8<br>68.0<br>58.4<br>65.1<br>69.6<br>73.8<br>74.1<br>74.0<br>74.3<br>72.1<br>58.9<br>68.39<br>64.0<br>67.9<br>58.1<br>68.5<br>69.6<br>73.5<br>73.5<br>73.6<br>73.6<br>71.4<br>59.2<br>69.13|18.9<br>23.5<br>49.3<br>55.4<br>35.4<br>43.3<br>43.4<br>50.6<br>46.3<br>51.1<br>45.3<br>53.9<br>26.9<br>31.1<br>38.2<br>44.6<br>45.2<br>52.5<br>24.5<br>31.3<br>20.6<br>30.1<br>27.9<br>31.4<br>55.9<br>62.4<br>56.2<br>62.4<br>52.1<br>57.9<br>48.0<br>50.5<br>44.9<br>50.9<br>33.2<br>36.9<br>54.6<br>59.6<br>37.8<br>45.0<br>45.8<br>51.8<br>46.6<br>51.8<br>31.0<br>35.4<br>35.0<br>39.8<br>33.5<br>37.7|74.9<br>77.9<br>76.6<br>77.7<br>76.6<br>77.4<br>74.8<br>75.8<br>77.5<br>77.2<br>70.4<br>73.9<br>78.0<br>78.3<br>77.6<br>76.9<br>77.4<br>77.4<br>78.2<br>77.9<br>77.6<br>77.9<br>76.1<br>75.3<br>75.5|
|**Avg**|60.6<br>67.9<br>70.9<br>70.1<br>69.5<br>75.1<br>75.3<br>75.3<br>75.5<br>73.4<br>54.4<br>67.9|39.9<br>45.3|**76.6**|

Table 10: Performance comparison on BEIR English retrieval benchmark.

|**Dataset**<br>**Size**<br>**On MTEBv2**|**Large Models (**_≥_**1B params)**|**Small Models (**_<_**1B params)**|
|---|---|---|
||**Qwen3-8B**<br>**bge-en-icl**<br>**Qwen3-4B**<br>**inf-v1-1.5b**<br>**e5-large-inst**<br>**gte-large**<br>**LENS-d4K**<br>**inf-v1**|**gte-base**<br>**bge-large**<br>**gte-base-v1.5**<br>**e5-large**<br>**bge-lg-v1.5**<br>**Qwen3-0.6B**<br>**opensearch-gte**<br>**Splade-V3**<br>**MILCO**|
|_Small Collections (<1M documents)_|||
|ArguAna<br>8.7K<br>yes<br>FiQA2018<br>58K<br>yes<br>NFCorpus<br>3.6K<br>no<br>QuoraRetrieval<br>523K<br>no<br>SCIDOCS<br>26K<br>yes<br>SciFact<br>5.2K<br>no<br>TRECCOVID<br>171K<br>yes<br>Touche2020<br>383K<br>yes|76.9<br>**83.1**<br>75.6<br>81.5<br>58.5<br>57.2<br>77.3<br>84.9<br>**64.6**<br>59.7<br>62.7<br>56.1<br>48.4<br>44.5<br>60.4<br>62.4<br>41.5<br>41.9<br>41.1<br>38.6<br>36.3<br>38.2<br>41.6<br>**43.7**<br>88.9<br>**91.0**<br>88.1<br>89.6<br>89.2<br>88.3<br>90.8<br>90.4<br>**32.7**<br>25.3<br>31.4<br>26.3<br>19.2<br>23.4<br>27.5<br>30.8<br>78.5<br>79.1<br>78.3<br>82.8<br>71.6<br>74.3<br>78.4<br>**85.4**<br>**95.0**<br>79.1<br>92.9<br>72.4<br>82.5<br>70.2<br>69.7<br>75.1<br>**35.9**<br>30.5<br>35.4<br>21.3<br>27.4<br>25.5<br>25.9<br>24.4|57.1<br>62.5<br>63.5<br>54.4<br>64.5<br>71.0<br>52.1<br>50.9<br>61.8<br>40.8<br>45.0<br>48.7<br>43.8<br>45.0<br>46.6<br>40.7<br>37.4<br>42.7<br>37.9<br>34.6<br>35.9<br>34.0<br>38.1<br>36.7<br>36.0<br>35.7<br>36.3<br>88.2<br>89.0<br>88.4<br>89.3<br>89.1<br>87.8<br>87.3<br>81.4<br>88.2<br>23.1<br>22.2<br>21.9<br>17.5<br>22.6<br>24.4<br>16.7<br>15.8<br>16.8<br>76.2<br>72.4<br>76.8<br>70.2<br>74.6<br>69.7<br>72.5<br>71.0<br>70.1<br>68.8<br>75.4<br>73.1<br>71.2<br>74.7<br>90.5<br>73.3<br>74.8<br>74.0<br>22.6<br>26.6<br>25.2<br>23.1<br>24.8<br>33.2<br>39.0<br>29.3<br>28.0|
|_Large Collections (≥1M documents)_|||
|ClimateFEVER<br>5.4M<br>yes<br>DBPedia<br>4.6M<br>no<br>FEVER<br>5.4M<br>yes<br>HotpotQA<br>5.2M<br>yes<br>MSMARCO<br>8.8M<br>no<br>NQ<br>2.7M<br>no|**47.4**<br>45.4<br>47.4<br>41.5<br>29.9<br>28.8<br>44.6<br>41.8<br>49.7<br>**51.6**<br>48.2<br>48.6<br>38.4<br>42.4<br>50.1<br>50.4<br>91.9<br>92.8<br>91.6<br>90.9<br>78.0<br>84.5<br>92.4<br>**94.2**<br>76.8<br>**85.1**<br>74.7<br>76.3<br>69.3<br>67.2<br>85.1<br>82.0<br>43.6<br>46.8<br>42.7<br>41.0<br>40.4<br>40.9<br>**47.0**<br>44.1<br>65.3<br>**73.9**<br>63.1<br>64.2<br>57.8<br>54.8<br>73.1<br>69.7|28.1<br>38.2<br>40.4<br>25.7<br>36.6<br>42.1<br>31.2<br>23.3<br>30.8<br>41.2<br>43.9<br>39.9<br>41.3<br>44.1<br>39.5<br>45.5<br>45.0<br>45.1<br>81.5<br>86.7<br>94.8<br>82.8<br>87.2<br>88.2<br>86.1<br>79.6<br>83.4<br>65.8<br>74.6<br>67.8<br>71.2<br>74.1<br>65.7<br>71.6<br>69.2<br>77.7<br>40.2<br>42.6<br>42.6<br>43.7<br>42.5<br>38.0<br>42.6<br>44.0<br>42.0<br>52.8<br>53.2<br>53.0<br>64.0<br>55.0<br>53.5<br>58.2<br>58.6<br>64.9|
|**Avg (All)**<br>**Avg (Large)**|63.5<br>63.2<br>62.4<br>59.4<br>53.3<br>52.9<br>61.7<br>**62.8**<br>62.4<br>**66.0**<br>61.3<br>60.4<br>52.3<br>53.1<br>65.4<br>63.7|51.7<br>54.8<br>55.1<br>52.3<br>55.2<br>56.2<br>53.8<br>51.1<br>54.4<br>51.6<br>56.5<br>56.4<br>54.8<br>56.6<br>54.5<br>55.8<br>53.3<br>57.3|

## A.3 ENGLISH RETRIEVAL RESULTS (BEIR)

In Table 10, we report the performance of MILCO and baselines on various retrieval tasks evaluated on BEIR English benchmark (Thakur et al., 2021).

On average across BEIR benchmarks, MILCO attains 54.4, slightly behind the dense competitor Qwen3-0.6B (56.2; _−_ 1.8). This gap is expected, as Qwen3-0.6B benefits from instruction tuning, which the Qwen3 paper (Zhang et al., 2025) reports adds +1–5%, while MILCO does not use instructions. Compared to other English-only sparse baselines, MILCO is clearly stronger than Splade-V3 _−_ (+3.3) and marginally ahead of opensearch-gte (+0.6), while still trailing LENS-d4K ( 7.3), a much larger sparse model. It is worth noting, however, that the comparison to Splade-V3 is not entirely fair: Splade is only trained on MSMARCO, while MILCO (and most other baselines) is trained on much larger data, including BEIR’s in-domain training sets, which naturally favors transfer to the BEIR evaluation benchmark.

When focusing on the more challenging large-collection datasets ( _≥_ 1M documents), MILCO shows its main strength. It achieves an average of 57.3, surpassing Qwen3-0.6B (54.5; +2.8), Splade-V3 (53.3; +4.0), and opensearch-gte (55.8; +1.5). MILCO’s improvements are particularly pronounced on datasets such as HotpotQA (77.7 vs. 65.7; +12.0) and NQ (64.9 vs. 53.5; +11.4). Although it still falls behind LENS-d4K (65.4; _−_ 8.1), the strong performance on large collections is noteworthy because such scenarios are the most relevant to real-world search applications, where corpora often contain millions of documents.

[page 19]

Published as a conference paper at ICLR 2026

Table 11: Performance of MILCO compared to dense baselines on the LIMIT benchmark.

|**Model**|**Dim**|**Recall@2**|**Recall@10**|**Recall@100**|
|---|---|---|---|---|
|BM25|default|85.7|90.4|93.6|
|GTE-ModernColBERT|default|23.1|34.6|54.8|
|E5-Mistral 7B|32|0|0|0.5|
|E5-Mistral 7B|64|0|0.1|0.4|
|E5-Mistral 7B|128|0.1|0.3|1.0|
|E5-Mistral 7B|256|0.4|0.9|1.9|
|E5-Mistral 7B|512|0.7|1.3|3.8|
|E5-Mistral 7B|768|0.9|1.7|4.3|
|E5-Mistral 7B|1024|0.9|1.8|5.9|
|E5-Mistral 7B|2048|1.0|1.9|6.8|
|E5-Mistral 7B|3072|1.3|2.0|7.7|
|E5-Mistral 7B|4096|1.3|2.2|8.3|
|GritLM 7B|32|0|0|0.8|
|GritLM 7B|64|0|0.1|0.3|
|GritLM 7B|128|0.1|0.3|1.3|
|GritLM 7B|256|0.1|0.4|2.8|
|GritLM 7B|512|0.6|1.8|6.5|
|GritLM 7B|768|1.5|3.1|8.7|
|GritLM 7B|1024|1.8|3.5|10.6|
|GritLM 7B|2048|2.3|4.3|11.8|
|GritLM 7B|3072|2.0|4.3|12.9|
|GritLM 7B|4096|2.4|4.1|12.9|
|Qwen3-Embed|32|0|0.1|1.1|
|Qwen3-Embed|64|0|0.2|1.0|
|Qwen3-Embed|128|0.3|0.4|1.8|
|Qwen3-Embed|256|0.4|0.8|3.2|
|Qwen3-Embed|512|0.6|1.3|3.3|
|Qwen3-Embed|768|0.7|1.5|3.8|
|Qwen3-Embed|1024|0.7|1.6|4.6|
|Qwen3-Embed|2048|0.9|1.7|4.7|
|Qwen3-Embed|3072|0.8|1.6|4.8|
|Qwen3-Embed|4096|0.8|1.8|4.8|
|Gemini-Embed|2|0|0|0.1|
|Gemini-Embed|4|0|0|0.0|
|Gemini-Embed|8|0|0|0.0|
|Gemini-Embed|16|0|0|0.0|
|Gemini-Embed|32|0|0|0.0|
|Gemini-Embed|64|0|0|0.3|
|Gemini-Embed|128|0|0.1|0.3|
|Gemini-Embed|256|0|0.1|1.2|
|Gemini-Embed|512|0.2|1.1|3.6|
|Gemini-Embed|768|0.9|2.5|7.6|
|Gemini-Embed|1024|1.3|2.7|8.1|
|Gemini-Embed|2048|1.5|3.1|8.5|
|Gemini-Embed|3072|1.6|3.5|10.0|
|①**MILCO**(SAP, SCTKD, LexEcho)|280,524|26.2|47.0|73.5|

## A.4 EMBEDDING LIMIT TEST

Table 11 shows the advantage of MILCO over strong state-of-the-art dense baselines on the LIMIT test (Weller et al., 2025). MILCO achieves an R@100 of 73.5, whereas dense models such as Gemini-Embed and Qwen3-Embed nearly collapse to zero.

## A.5 CORRELATION BETWEEN TEXT LENGTH AND VECTOR SPARSITY

In Figure 7, we show a strong correlation between input length and the sparsity of vectors produced by MILCO. Unlike dense retrieval methods, which always generate fixed-length vectors for all queries and documents, LSR methods, including MILCO, adaptively determine the optimal sparsity

[page 20]

Published as a conference paper at ICLR 2026

**==> picture [238 x 170] intentionally omitted <==**

**----- Start of picture text -----**<br>
1000<br>800<br>600<br>400<br>200<br>0<br>0 500 1000 1500 2000<br>Text length (# of characters)<br>Vector sparsity (number of non-zeros)<br>**----- End of picture text -----**<br>

Figure 7: MILCO: Correlation between input text length and the sparsity of output vectors.

Table 12: MILCO: Effectiveness at different TopK (tokens). (nDCG@10, MIRACL)

|**TopK (tokens)**|**Avg**|**ar**|**bn**|**de**|**en**|**es**|**fa**|**f**|**fr**|**hi**|**id**|**ja**|**ko**|**ru**|**sw**|**te**|**th**|**yo**|**zh**|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|10|44.5|55.66|50.1|38.38|34.15|34.6|35.65|57.53|40.42|29.65|38.16|43.33|49.13|42.65|55.92|56.41|48.56|53.11|37.9|
|20|54.6|66.81|62.26|45.75|43.32|41.98|45.07|66.9|47.02|41.09|45.72|55.88|57.58|52.69|65.76|72.89|64.93|60.99|45.97|
|50|63.8|74.29|73.7|52.87|51.41|51.65|52.95|74.29|53.31|52.79|53.08|67.11|66.08|63.95|74.1|82.61|77.64|69.69|56.82|
|100|68.4|77.52|77.98|58.07|56.8|56.36|59.31|77.2|58.49|60.09|57.27|72.11|69.02|69.34|76.93|85.13|81.45|76.12|61.79|
|200|71.0|79.63|80.59|60.25|59.7|59.87|61.71|79.7|61.41|63.8|59.46|75.59|70.7|72.76|78.72|87.05|83.15|79.75|64.72|
|300|72.1|80.06|81.46|61.49|61.04|61.05|62.75|80.27|62.55|66.11|60.33|76.43|71.3|73.59|79.72|87.45|83.93|82.36|66.14|
|500|72.6|80.58|81.65|62.39|61.98|61.86|63.45|80.68|62.75|66.05|61.06|76.94|72.12|74.45|80.02|87.92|84.34|82.26|66.85|
|700|72.7|80.83|81.97|62.75|62.1|62.14|63.13|80.7|62.79|65.21|60.97|77.28|72.03|74.8|80.16|87.95|84.41|82.19|66.99|
|1000|72.7|80.81|82.12|62.83|62.09|62.17|63.04|80.63|62.74|65.12|60.99|77.28|71.94|74.89|80.26|87.75|84.48|82.36|66.94|

Table 13: MILCO: Effectiveness at different pruning percentile _P_ . (nDCG@10, MIRACL)

|**P**|**#Tokens**|**Avg**|**ar**|**bn**|**de**|**en**|**es**|**fa**|**f**|**fr**|**hi**|**id**|**ja**|**ko**|**ru**|**sw**|**te**|**th**|**yo**|**zh**|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|10|512.5|72.6|80.8|82.0|62.7|62.1|62.0|63.1|80.6|62.8|65.1|60.9|77.3|72.0|74.9|80.2|87.8|84.4|82.0|66.8|
|20|455.8|72.6|80.7|81.8|62.8|62.0|61.8|63.2|80.6|62.9|64.8|61.0|77.3|72.0|74.9|80.2|87.8|84.5|81.7|66.8|
|50|285.6|72.3|80.7|81.8|61.7|61.1|61.7|63.1|80.5|62.6|64.3|60.8|76.9|71.9|74.6|80.1|87.8|84.2|80.4|66.4|
|70|172.2|71.7|80.3|81.5|60.9|60.1|60.5|62.5|79.9|61.3|64.2|60.1|76.6|70.5|74.2|79.4|87.8|83.8|80.7|65.2|
|80|115.1|70.6|79.6|80.7|60.9|59.0|59.6|61.3|78.8|60.8|62.3|58.7|75.4|68.8|73.0|78.3|86.9|83.7|79.2|64.0|
|85|86.4|69.5|78.6|79.5|59.0|57.2|58.5|60.1|78.3|59.0|61.7|58.4|74.2|67.5|71.7|77.2|86.4|82.8|77.7|63.0|
|90|57.9|67.4|76.6|77.8|57.8|55.0|56.1|56.1|76.7|57.4|58.6|56.4|72.1|65.7|68.9|76.3|84.5|81.4|75.0|60.7|
|95|29.2|62.2|71.8|71.8|52.5|48.7|51.2|48.9|71.8|53.6|52.6|52.5|65.5|63.3|63.3|71.3|78.1|76.2|70.5|55.7|
|97|17.7|56.0|66.2|65.9|44.2|42.4|46.6|44.2|66.0|49.4|45.0|48.5|57.4|58.3|56.1|65.0|67.4|68.6|67.3|50.0|
|99|6.5|39.5|48.38|46.14|32.18|29.04|33.31|28.55|50.53|37.56|28.06|37.17|38.38|42.27|37.82|43.04|43.07|44.59|57.09|34.13|

(i.e., the number of non-zero elements) based on the content density of the input text, as approximiated by its length. This allows MILCO to allocate fewer tokens for short texts and more for longer ones, while maintaining the same average sparsity overall.

On Table 12 and Table 13, we show the results of two different post-hoc pruning methods (Top-k Pruning and Mass-based Pruning) applied on MILCO.

## A.6 ALIGNMENT AND CONTRASTIVE TRAINING DATA

The sources and statistics of the data used for our Sparse Alignment Pretraining are reported in Table 14. In total, the corpus consists of 594 million bi-text pairs, each containing one English sentence and one non-English sentence with the same semantic meaning.

The statistics of the data used for our contrastive training are shown in Table 15. This dataset contains 1.4M queries collected from 16 datasets, covering English, Chinese, and 16 additional languages from Mr.TYDI (Zhang et al., 2021) and MIRACL (Zhang et al., b). Similar to prior work (Chen et al., 2024; Li et al.; Lei et al., 2025), our training data also includes many in-domain datasets from BEIR (Thakur et al., 2021).

[page 21]

Published as a conference paper at ICLR 2026

Table 14: Pretraining datasets: Parallel Sentences collected from OPUS by Reimers & Gurevych (2019).

|**Dataset Name**|**#Pairs**|
|---|---|
|mmarco (passages)|115M|
|wikititles|14M|
|wikimatrix|19M|
|europarl|50M|
|opensubtitles|274M|
|talks|20M|
|tatoeba|8M|
|jw300|92M|
|news-commentary|2M|
|**Total**|**594M**|

Table 15: Contrastive Training Data obtained from Chen et al. (2024).

|**Dataset**|**Dataset**|**#Samples**|
|---|---|---|
|en|~~m~~smarco (Nguyen et al., 2016)|485,823|
|en|~~e~~li5 (Fan et al., 2019)|150,000|
|zh|~~m~~marco<br>~~z~~h (Bonifacio et al., 2021)|100,000|
|zh|~~t~~2ranking (Xie et al., 2023)|90,467|
|en|~~s~~quad (Rajpurkar et al., 2016)|87,599|
|en|~~h~~otpotqa (Yang et al., 2018)|84,516|
|zh|~~d~~ureader (He et al., 2017)|80,416|
|en|~~t~~rivia (Joshi et al., 2017)|60,315|
|en|~~q~~uora (Sharma et al., 2019)|60,202|
|en|~~n~~q (Kwiatkowski et al., 2019)|58,568|
|multilingual<br>~~m~~rtydi (Zhang et al., 2021)||48,729|
|multilingual<br>~~m~~iracl (Zhang et al., b)||40,203|
|en|~~f~~ever (Thorne et al., 2018)|29,096|
|en|~~f~~qa (Maia et al., 2018)|5,500|
|en|~~a~~rguana (Wachsmuth et al., 2018)|4,065|
|en|~~s~~cidocs (Cohan et al., 2020)|884|
|**Total**||**1,386,383**|

## A.7 CONTRASTIVE TRAINING: DISTILLATION

For each query _qi_ , we consider a document candidate set consisting of one positive _d_[+] and a set of negatives _D[−]_ . The precomputed teacher scores are from the cross-encoder, denoted as _θ_ CE( _d, q_ ). The student scores _θ_ milco( _d, q_ ) are estimated via the dot product of MILCO’s lexical representations. These scores are converted into distributions over the candidate set with a softmax:

**==> picture [284 x 29] intentionally omitted <==**

where _θx_ ( _q, d_ ) denotes either the teacher or student scoring function of the given query and document. The distillation objective is then defined as the KL divergence between the teacher’s and the student’s distributions across a batch of _B_ queries:

**==> picture [293 x 30] intentionally omitted <==**

[page 22]

Published as a conference paper at ICLR 2026

## A.8 TRAINING CONFIGURATIONS AND HYPER-PARAMETERS

The hyperparameters for pretraining and training are reported in Table 16 and Table 17. Both training stages are conducted on 16 GPU nodes, each equipped with 8 AMD Instinct MI250X GPU dies. We instantiate the Multilingual Connector with a simple randomly-initialized MLP layer with a GELU activation function. For sparse regularization, we set the regularization weight to 1e _−_ 5 for both queries and documents during contrastive training. We train MILCO using the HuggingFace framework (Wolf et al., 2019). Hyperparameters not listed in Table 16 and Table 17 are set to the default values defined in HuggingFace’s TrainingArguments.

Table 16: MILCO: Hyperparameters for Sparse Alignment Pre-training.

|**Hyperparameter**|**Hyperparameter**|||**Value**|
|---|---|---|---|---|
|training<br>type||||alignment|
|model<br>~~t~~ype||||bert|
|lsr<br>~~e~~ncoder<br>checkpoint||||naver/splade-v3|
|multilingual<br>~~e~~ncoder||checkpoint||BAAI/bge-m3-unsupervised|
|train<br>~~d~~atasets||||mmarco, wikititles, wikimatrix, europarl, opensubtitles, talks,|
|||||tatoeba, jw300, news-commentary|
|seed||||42|
|max<br>length||||256|
|per<br>~~d~~evice<br>~~t~~rain|~~b~~atch||~~s~~ize|64|
|per<br>~~d~~evice<br>~~e~~val|batch||~~s~~ize|128|
|num<br>~~t~~rain<br>epochs||||2|
|save<br>total<br>~~l~~imit||||2|
|warmup<br>~~s~~teps||||10000|
|lr<br>scheduler<br>~~t~~ype||||cosine|
|dataloader<br>~~n~~um|~~w~~orkers|||8|
|learning<br>~~r~~ate||||2e-5|
|bf16||||True|
|logging<br>steps||||500|
|save<br>steps||||20000|
|pooling||||max|
|remove<br>unused|~~c~~olumns|||False|
|dynamic<br>~~l~~ength||||True|

Table 17: MILCO: Hyperparameters for Sparse Contrastive Training.

|**Hyperparameter**||||**Value**|
|---|---|---|---|---|
|training<br>~~t~~ype||||distillation|
|model<br>~~t~~ype||||bert|
|lsr<br>~~e~~ncoder<br>~~c~~heckpoint||||naver/splade-v3|
|multilingual<br>~~e~~ncoder||~~c~~heckpoint||BAAI/bge-m3-unsupervised|
|train<br>~~g~~roup<br>~~s~~ize||||8|
|lambda<br>~~q~~||||1e-3|
|lambda<br>~~d~~||||1e-5|
|train<br>~~d~~atasets||||bge|
|seed||||42|
|max<br>~~l~~ength||||512|
|per<br>~~d~~evice<br>~~t~~rain|~~b~~atch||~~s~~ize|8|
|per<br>~~d~~evice<br>~~e~~val|~~b~~atch||size|32|
|num<br>~~t~~rain<br>~~e~~pochs||||8|
|save<br>~~t~~otal<br>~~l~~imit||||2|
|warmup<br>~~r~~atio||||0.03|
|lr<br>~~s~~cheduler<br>~~t~~ype||||cosine|
|dataloader<br>~~n~~um|~~w~~orkers|||1|
|learning<br>~~r~~ate||||2e-5|
|bf16||||True|
|logging<br>~~s~~teps||||500|

[page 23]

Published as a conference paper at ICLR 2026

## A.9 LIST OF LANGUAGES SUPPORTED BY MILCO

Table 18: Datasets and their supported languages.

|Table 18:|Datasets and their supported languages.||
|---|---|---|
|**Dataset**|**Languages (standardized)**|**#languages**|
|MIRACL|ar, bn, de, en, es, fa, f, fr, hi, id, ja, ko, ru, sw, te, th, yo,|18|
||zh||
|MLDR|ar, de, en, es, fr, hi, it, ja, ko, pt, ru, th, zh|13|
|MKQA|ar, da, de, es, f, fr, he, hu, it, ja, km, ko, ms, nl, no, pl, pt,|25|
||ru, sv, th, tr, vi, zh-cn, zh-hk, zh-tw||
|BelebeleRetrieval|acm, af, en|3|
|MLQARetrieval|ar, de, en, es, hi, vi|6|
|TwitterHjerneRetrieval|dan|1|
|WikipediaRetrievalMultilingual|bg, bn, cs, da, de, en, fa, f, hi, it, nl, no, pt, ro, sr, sv|16|
|WikiMatrix|ar, bg, ca, cs, da, de, el, es, et, fa, f, fr, gl, he, hi, hr, hu,|41|
||hy, id, it, ja, ka, ko, lt, lv, mk, ms, nl, pl, pt, ro, ru, sk, sl,||
||sq, sr, sv, th, tr, uk, ur, vi, zh-cn||
|parallel-sentences-opensubtitles|ar, bg, ca, cs, da, de, el, es, et, fa, f, fr, gl, he, hi, hr, hu,|38|
||id, it, ja, ka, ko, lt, mk, mr, nl, pl, pt, ro, ru, sk, sl, sq, sr,||
||sv, tr, uk, vi, zh||
|parallel-sentences-tatoeba|ar, bg, ca, cs, da, de, el, es, et, fa, f, fr, gl, gu, he, hi, hr,|46|
||hu, hy, id, it, ja, ka, ko, ku, lt, lv, mk, mn, mr, ms, my, nb,||
||nl, pl, pt, ro, ru, sk, sl, sq, sr, sv, th, tr, uk, ur, vi, zh||
|parallel-sentences-global-voices|ar, bg, ca, cs, da, de, el, es, fa, fr, he, hi, hu, id, it, ko, mk,|27|
||my, nl, pl, pt, ro, ru, sq, sr, sv, tr, ur||
|parallel-sentences-europarl|bg, cs, da, de, el, es, et, f, fr, hu, it, lt, lv, nl, pl, pt, ro, sk,|20|
||sl, sv||
|parallel-sentences-talks|ar, bg, ca, cs, da, de, el, es, et, fa, f, fr, fr-ca, gl, gu, he,|50|
||hi, hr, hu, hy, id, it, ja, ka, ko, ku, lt, lv, mk, mn, mr, ms,||
||my, nb, nl, pl, pt, pt-br, ro, ru, sk, sl, sq, sr, sv, th, tr, uk,||
||ur, vi, zh-cn, zh-tw||
|parallel-sentences-jw300|ar, bg, cs, da, de, el, es, et, fa, f, fr, gu, he, hi, hr, hu, hy,|43|
||id, it, ja, ka, ko, lt, lv, mk, mn, mr, my, nl, pl, pt, ro, ru,||
||sk, sl, sq, sr, sv, th, tr, uk, ur, vi||
|parallel-sentences-news-commentary|ar, cs, de, es, fr, it, ja, nl, pt, ru|10|
|mmarco|ar, zh, nl, en, fr, de, hi, id, it, ja, pt, ru, es, vi|14|
|All Test Datasets|acm, af, ar, bg, bn, cs, da, de, en, es, fa, f, fr, he, hi, hu,|39|
||id, it, ja, km, ko, ms, nl, no, pl, pt, ro, ru, sr, sv, sw, te, th,||
||tr, vi, yo, zh, zh-cn, zh-hk, zh-tw||
|All (Pretrain/Train + Test) datasets|acm, af, ar, bg, bn, ca, cs, da, de, el, en, es, et, fa, f, fr,|63|
||fr-ca, gl, gu, he, hi, hr, hu, hy, id, it, ja, ka, km, ko, ku, lt,||
||lv, mk, mn, mr, ms, my, nb, nl, no, pl, pt, pt-br, ro, ru, sk,||
||sl, sq, sr, sv, sw, te, th, tr, uk, ur, vi, yo, zh, zh-cn, zh-hk,||
||zh-tw||

## A.10 ABLATIONS ON LEXECHO HEAD.

To provide additional insights on our LexEcho head, we perform an ablation that interpolates between the pivot (English) and source views in LexEcho. Specifically, we multiply the English view by _α_ and the source view by (1 _− α_ ), with _α ∈{_ 0 _._ 0 _,_ 0 _._ 2 _, . . . ,_ 1 _._ 0 _}_ , and report MIRACL results in Table 19.

[page 24]

Published as a conference paper at ICLR 2026

Table 19: MILCO performance under different pivot–source weighting schemes on the MIRACL (hard negatives) benchmark.

|_α_|**ar**|**bn**|**en**|**es**|**fa**|**f**|**fr**|**hi**|**id**|**ja**|**ko**|**ru**|**sw**|**te**|**th**|**zh**|**de**|**yo**|**Avg**|
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
|0.00|5.21|9.61|3.56|0.09|1.74|8.18|0.14|1.56|4.71|3.33|11.14|2.19|2.75|31.35|14.90|0.00|0.20|0.27|5.61|
|0.20|11.01|17.51|6.16|0.91|4.23|17.80|1.51|3.95|9.55|7.16|19.09|5.35|6.95|43.42|22.47|0.11|1.84|4.49|10.19|
|0.40|79.38|79.30|56.55|55.89|57.29|79.72|60.70|57.46|58.46|75.36|71.99|73.10|77.52|86.77|82.44|56.95|59.67|63.23|68.43|
|0.50|80.79|82.00|62.08|62.06|63.08|80.64|62.73|65.06|60.91|77.25|72.00|74.96|80.18|87.82|84.46|66.80|62.83|82.14|72.66|
|0.60|80.08|81.43|62.03|62.00|62.34|79.91|63.14|64.94|60.14|76.64|71.13|74.30|79.61|87.11|83.81|65.54|61.73|81.72|72.09|
|0.80|78.19|80.22|60.18|61.27|60.36|78.81|62.16|64.00|58.39|74.66|69.12|72.95|78.49|84.05|81.47|63.63|60.58|80.86|70.52|
|1.00|77.77|79.35|59.53|60.98|59.73|78.43|62.19|63.31|57.97|73.80|68.52|72.74|78.04|82.90|80.72|63.33|60.55|80.46|70.02|

We find that MILCO performs very poorly with only the source view ( _α_ = 0 _._ 0; average nDCG@10 = 5 _._ 61), indicating that the English pivot is essential. With only the English view ( _α_ = 1 _._ 0), MILCO is already strong (average nDCG@10 = 70 _._ 02) but not optimal. The best result is obtained with a roughly balanced fusion ( _α_ = 0 _._ 5), reaching an average nDCG@10 of 72.66 (around 3–4% relative improvement over _α_ = 1 _._ 0). Performance for _α_ between 0.5 and 0.6 is very similar, suggesting that LexEcho is not overly sensitive to the exact weighting as long as both views contribute.

## A.11 EFFECT OF LANGUAGE COVERAGE IN ALIGNMENT PRETRAINING

We now investigate how language coverage in the parallel corpus used for MILCO’s sparse alignment pretraining affects the final retrieval performance across MIRACL languages. To this end, we compare MILCO (alignment + distillation) against our best-performing dense baseline (distillation only), trained with the same data and compute, and report per-language ∆nDCG@10. We then aggregate languages by their share of alignment data to analyze the relationship between coverage and effectiveness (Tables 20 and 21).

Table 20: Average ∆nDCG@10 as a function of alignment coverage. Languages are grouped into well-represented ( _P ≥_ 1%) and under-represented ( _P <_ 1%) buckets based on their proportion in the parallel corpus.

|**Percentage category:**|_P ≥_1|_P <_1|
|---|---|---|
|Avg.∆nDCG@10|1.59|0.77|

Table 21 lists nDCG@10 and ∆nDCG@10 for all 18 MIRACL languages, together with their proportion in the parallel corpus. Aggregating by coverage (Table 20), we observe an average gain of +1 _._ 59 ∆nDCG@10 for well-represented languages ( _P ≥_ 1%) and a smaller but still positive average gain of +0 _._ 77 for under-represented languages ( _P <_ 1%), including languages with 0 parallel samples (sw, te, yo, bn). The main exception is fa ( _−_ 1 _._ 09), which we plan to analyze further.

These results indicate that higher coverage in the alignment corpus amplifies the gains from MILCO, but is not strictly required: even languages that are weakly covered or entirely absent from the alignment corpus still benefit on average. This behavior highlights MILCO’s multilingual alignment pretraining as an effective mechanism for knowledge transfer and sharing across languages.

[page 25]

Published as a conference paper at ICLR 2026

Table 21: MILCO effectiveness vs. alignment data distribution across languages (MIRACL Hard Negatives.). We report nDCG@10, per-language ∆nDCG@10 (MILCO vs. dense baseline), and the number and proportion of parallel corpus samples used for alignment pretraining.

|**Lang**|**nDCG@10**|∆**nDCG@10**|**Samples**|**Percentage**|
|---|---|---|---|---|
|ar|80.4|0.919|19002229|5.5|
|bn|82.6|2.387|0|0|
|en|60.4|3.585|–|–|
|es|60.9|0.487|28470451|8.23|
|fa|62.3|-1.09|646913|0.19|
|f|81.2|2.676|4958793|1.43|
|fr|61.7|-0.922|22574836|6.53|
|hi|64.4|2.158|9626940|2.78|
|id|60.9|2.498|17591514|5.09|
|ja|77.2|2.524|11542221|3.34|
|ko|72.1|1.548|3648265|1.05|
|ru|74.6|2.458|16592711|4.8|
|sw|80.3|0.734|0|0|
|te|87.9|0.87|0|0|
|th|84.2|1.295|1668858|0.48|
|zh|65.5|1.328|9006690|2.6|
|de|61.4|1.823|24431450|7.07|
|yo|83.6|0.41|0|0|
