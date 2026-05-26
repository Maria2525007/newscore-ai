---
id: doc-005
source: 05-milco-lsr-nguyen-2025.pdf
source_type: pdf
source_sha256: 58e9cf4a0a0bc7c4f4b5b887917daeecdf9df5c2b532c1651fbf494822b97ccc
extraction_method: mineru-vlm@3.2.0
extraction_date: 2026-05-26
pages: 25
headings:
  - MILCO: LEARNED SPARSE RETRIEVAL ACROSS LANGUAGES VIA A MULTILINGUAL CONNECTOR
  - ABSTRACT
  - 1 INTRODUCTION
  - "Our Contributions:"
  - 2 RELATED WORK
  - 3 PROPOSED METHODOLOGY
  - 3.1 MILCO ARCHITECTURE
  - 3.2 TRAINING: SPARSE ALIGNMENT AND CONTRASTIVE REFINEMENT
  - 4 EXPERIMENTAL SETTINGS
  - "MILCO configurations. We consider the following configurations in experiments:"
tokens_estimated: 49971
warnings: []
assets:
  - ../assets/doc-005-page18-img1.jpeg
  - ../assets/doc-005-page24-img1.jpeg
  - ../assets/doc-005-page10-img2.jpeg
  - ../assets/doc-005-page24-img2.jpeg
  - ../assets/doc-005-page17-img2.jpeg
  - ../assets/doc-005-page20-img3.jpeg
  - ../assets/doc-005-page18-img2.jpeg
  - ../assets/doc-005-page09-img1.jpeg
  - ../assets/doc-005-page10-img1.jpeg
  - ../assets/doc-005-page25-img1.jpeg
  - ../assets/doc-005-page20-img1.jpeg
  - ../assets/doc-005-page20-img2.jpeg
  - ../assets/doc-005-page02-img1.jpeg
  - ../assets/doc-005-page09-img2.jpeg
  - ../assets/doc-005-page19-img1.jpeg
  - ../assets/doc-005-page22-img2.jpeg
  - ../assets/doc-005-page23-img1.jpeg
  - ../assets/doc-005-page17-img3.jpeg
  - ../assets/doc-005-page07-img1.jpeg
  - ../assets/doc-005-page08-img1.jpeg
  - ../assets/doc-005-page22-img1.jpeg
  - ../assets/doc-005-page17-img1.jpeg
  - ../assets/doc-005-page02-img2.jpeg
  - ../assets/doc-005-page21-img1.jpeg
  - ../assets/doc-005-page07-img2.jpeg
  - ../assets/doc-005-page06-img1.jpeg
  - ../assets/doc-005-page21-img2.jpeg
  - ../assets/doc-005-page10-img3.jpeg
  - ../assets/doc-005-page16-img1.jpeg
---
#

[page 1]

MILCO: LEARNED SPARSE RETRIEVAL ACROSS LANGUAGES VIA A MULTILINGUAL CONNECTOR

Thong Nguyen, Yibin Lei & Jia-Huei Ju

University of Amsterdam

{t.nguyen2,y.lei,j.ju}@uva.nl

Eugene Yang & Andrew Yates

Johns Hopkins University, HLTCOE

{eugene.yang, andrew.yates}@jhu.edu

# ABSTRACT

Learned Sparse Retrieval (LSR) combines the efficiency of bi-encoders with the transparency of lexical matching, but existing approaches struggle to scale beyond English. We introduce MILCO, an LSR architecture that maps queries and documents from different languages into a shared English lexical space via a multilingual connector. MILCO is trained with a specialized two-stage regime that combines Sparse Alignment Pretraining with contrastive training to provide representation transparency and effectiveness while mitigating semantic collapse. Motivated by the observation that uncommon entities are often lost when projected into English, we propose a new LexEcho head, which enhances robustness by augmenting the English lexical representation with a source-language view obtained through a special [ECHO] token. MILCO achieves state-of-the-art multilingual and cross-lingual LSR performance, outperforming leading dense, sparse, and multi-vector baselines such as BGE-M3 and Qwen3-Embed on standard multilingual benchmarks, while supporting dynamic efficiency through post-hoc pruning. Notably, when using mass-based pruning to reduce document representations to only 30 active dimensions on average, MILCO 560M outperforms the similarly-sized Qwen3-Embed 0.6B with 1024 dimensions, while achieving 3× lower retrieval latency and 10× smaller index size. $^{1}$

# 1 INTRODUCTION

Learned Sparse Retrieval (LSR) represents queries and documents as sparse lexical embeddings and retains the scalability benefits of bi-encoders (MacAvaney et al., 2020; Formal et al., 2021; Nguyen et al., 2023). Unlike dense methods, LSR aligns representation with a natural language vocabulary, yielding transparent representations that facilitate error tracing and bias inspection. LSR naturally supports dynamic post-hoc pruning at inference time (Bruch et al., 2024), providing Matryoshka-like latency control (Kusupati et al., 2022) without requiring auxiliary training objectives. Empirically, LSR (Lassance et al., 2024; Lei et al., 2025) is competitive on benchmarks like BEIR (Thakur et al., 2021) and MTEB (Enevoldsen et al., 2025). Theoretically, recent work shows sparse lexical embeddings exhibit higher representational capacity than dense embeddings, which is illustrated by their superior performance on the LIMIT benchmark (Weller et al., 2025) where even state-of-the-art dense models fail catastrophically.

Thus far, LSR progress has been driven primarily by English (Formal et al., 2022; Shen et al., 2025; Nardini et al., 2025), where models such as SPLADE (Lassance et al., 2024) deliver strong zero-shot effectiveness and have seen wide adoption in production systems (e.g., OpenSearch, ElasticSearch, Sentence Transformers). Extensions beyond English remain fragmented: BGE-M3 (Chen et al., 2024) combines dense, sparse, and multi-vector heads under a shared backbone, but its sparse component underperforms and lacks cross-lingual support; conversely, SPLADE-X (Nair et al., 2022b)

[page 2]

and BLADE (Nair et al., 2023) target cross-lingual retrieval only and rely on training separate models for each language pair, limiting their applications.

A straightforward multilingual LSR approach is to attach a multilingual MLM head to a multilingual base encoder, projecting inputs into the full multilingual vocabulary. However, directly optimizing such models can lead to severe semantic collapse (Nguyen et al., 2024), where representations lose interpretable term semantics, resulting in significant degradation of the model's transparency and effectiveness. This behavior is demonstrated both qualitatively and quantitatively in Section 5.

![](../assets/doc-005-page02-img1.jpeg)

<details>
<summary>text_image</summary>

[ECHO]
phone
...
transfer
...
step
...
import
...
live
music
[陌 陌 直播 音乐 怎么 导 入 手机
LexEcho Head
Multilingual Connector
Multilingual Encoder
陌 陌 直播 音乐 怎么 导 入 手机
How to import Momo Live music to mobile phone? (Translation)
⊕ Non-English Input (Chinese)
</details>

<table><tr><td colspan="3">Source View</td><td colspan="2">English View</td></tr><tr><td>Token</td><td>Weight</td><td>Note</td><td>Token</td><td>Weight</td></tr><tr><td>陌</td><td>1.46</td><td>mo</td><td>music</td><td>1.16</td></tr><tr><td>手机</td><td>0.97</td><td>phone</td><td>import</td><td>0.95</td></tr><tr><td>导</td><td>0.68</td><td>import</td><td>phone</td><td>0.88</td></tr><tr><td>直播</td><td>0.67</td><td>live</td><td>step</td><td>0.80</td></tr><tr><td>音乐</td><td>0.65</td><td>music</td><td>transfer</td><td>0.72</td></tr><tr><td>怎么</td><td>0.38</td><td>how</td><td>songs</td><td>0.55</td></tr><tr><td>入</td><td>0.36</td><td>import</td><td>song</td><td>0.49</td></tr><tr><td></td><td></td><td></td><td>live</td><td>0.51</td></tr><tr><td></td><td></td><td></td><td>...</td><td>...</td></tr></table>

Figure 1: MILCO's LexEcho head produces two lexical views: (1) a pivot (English) view supporting cross-lingual and multilingual retrieval, and (2) a source view for robustness to uncommon entities.

To overcome those challenges, we introduce MILCO, illustrated in Figure 1, an LSR architecture that uses a multilingual connector between a multilingual base encoder and an English MLM head, mapping text from all languages into a shared English vocabulary space. MILCO collapses the multilingual vocabulary to English to create a universal representation, which also reduces memory and computation during training. This approach enables one single MILCO model to support both multilingual and cross-lingual retrieval across many languages.

MILCO Training. We adopt a two-stage training procedure. First, we propose Sparse Alignment Pretraining (SAP), which maps multilingual inputs to English lexical targets, in contrast to prior dense alignment methods that operate in low-dimensional latent space (Reimers & Gurevych, 2020). SAP leverages widely available bitext corpora instead of scarce multilingual relevance labels, enabling large-scale multilingual pretraining. Alignment pretraining enables the model to then be fine-tuned with contrastive training using distillation (Lassance et al., 2024), which enhances retrieval effectiveness while preserving grounding. Crucially, SAP is a prerequisite: without alignment, contrastive training leads to semantic collapse, harming effectiveness.

LexEcho Head. We observe that uncommon entities, especially from non-Latin languages, are often lost when projected into English. To address this, we introduce LexEcho, a dual-view LSR head illustrated in Figure 1. The pivot (English) view is obtained by max-pooling over the logit matrix of an English MLM head, with our multilingual connector enabling it to operate across many languages. The source view selectively echoes input tokens through a special [ECHO] token, preserving entities that the English view fails to capture and assigning higher scores to more important tokens. This approach allows the model to represent entities it has never seen before or cannot translate.

Across 39 languages, our 560M MILCO model sets a new state of the art for Learned Sparse Retrieval in both multilingual and cross-lingual settings. On MIRACL, our best model surpasses BGE-Sparse, BGE-Dense, and Qwen3-Embed 8B by +34.1%, +4.5%, and +3.6% nDCG@10, respectively, while also providing transparent representations. Experiments also show that the proposed LexEcho head enhances robustness to tail entities, yielding an +4.2% overall improvement on MIRACL. Like Matryoshka Representation Learning, MILCO supports controllable efficiency via post-

[page 3]

hoc pruning, surpassing Qwen3-Embed 0.6B with only 30 active dimensions per document, while achieving $3\times$ lower retrieval latency and $10\times$ smaller index size.

# Our Contributions:

- We introduce MILCO, a multilingual connector architecture that maps queries and documents into a shared English lexical space, unifying multilingual and cross-lingual retrieval within a single model. Its LEXECHO head provides dual lexical views, enhancing robustness to unseen or uncommon entities or concepts.
- We introduce a new Sparse Alignment Pretraining (SAP) pretraining strategy tailored to multilingual LSR that addresses semantic collapse and provides the foundation for contrastive training, leading to an effective and transparent model.
- Through comprehensive experiments on multilingual and cross-lingual benchmarks across 39 languages, we demonstrate that the MILCO architecture and Sparse Alignment Pretraining are key to achieving state-of-the-art multilingual and cross-lingual sparse retrieval.

# 2 RELATED WORK

Learned Sparse Retrieval (LSR). Zamani et al. (2018) first proposed SNRM, an n-gram neural model for learning sparse representations compatible with inverted indexes, though its representations remained latent. Subsequent work (MacAvaney et al., 2020; Formal et al., 2021) replaced SNRM with Transformer architectures that map text directly into the English lexicon, yielding more transparent and effective models. Nguyen et al. (2023) categorize LSR architectures into three groups: Binary Encoders, which assign binary weights to tokens and enable efficient inference-free query encoding with modest effectiveness trade-offs (Nardini et al., 2025; Shen et al., 2025); MLP Encoders, which score tokens by contextual importance (MacAvaney et al., 2020; Lin & Ma, 2021); and MLM Encoders, used in state-of-the-art methods like Splade (Formal et al., 2021), which provide differentiable query weighting and expansion. Beyond architecture, training protocols such as hard negative mining and distillation (e.g., from cross-encoders) are key to narrowing the gap with dense and hybrid systems (Formal et al., 2022; Lassance et al., 2024). In this work, we introduce MILCO, a new LSR architecture with a LexEcho head for multilingual sparse retrieval.

Multilingual/Cross-language Retrieval. A central challenge in cross-language IR is the language mismatch between queries and documents. Existing approaches address this either through translation pipelines or multilingual encoders that map text from different languages into a shared latent space for cross-lingual matching. Representative efforts include dense encoder methods (Zhang et al., 2024; Wang et al., 2024; Zhang et al., 2025) and multi-vector methods with multilingual pretraining (Louis et al., 2024; Yang et al., 2024a). Community benchmarks such as MIRACL (Zhang et al., b) and NeuCLIR (Lawrie et al., 2024) provide standardized evaluation across many languages, while studies on translationese highlight biases introduced by translated text (Gellerstam, 1986; Riley et al., 2020; Nair et al., 2022a; Zhang et al., a). For sparse retrieval, BGE-M3 (Chen et al., 2024) combines dense, sparse, and multi-vector heads for multilingual retrieval, but its sparse component underperforms and offers limited cross-language support. Other sparse models such as SPLADE-X (Nair et al., 2022b) and BLADE (Nair et al., 2023) focus on cross-language retrieval with language-specific models. In contrast, our sparse model, MILCO, supports both multilingual and cross-language retrieval within a single model while substantially outperforming prior approaches.

Alignment Pretraining. Previous work highlights the importance of multilingual pre-training for building shared cross-language semantic spaces (Conneau et al., 2020; Chi et al.; Feng et al., 2022; Yang et al., 2022). For retrieval, pre-training directly on relevance objectives has been explored, often using in-batch negatives and hard-negative mining (Zhang et al., 2024). Another direction focuses on distilling efficient models, where cross-encoder or ensemble teachers guide bi-encoder students to produce retrieval-friendly embeddings (Kim et al., 2023; Campos et al., 2023). In multilingual IR, distillation also yields compact, language-agnostic dense embeddings for scalable cross-language retrieval (Reimers & Gurevych, 2020; Yang et al., 2024a). While prior work has mainly focused on dense models, we are the first to explore multilingual sparse alignment and introduce a sparse alignment pre-training method that enables LSR to perform well on multilingual data.

#

[page 4]

3 PROPOSED METHODOLOGY

# 3.1 MILCO ARCHITECTURE

MILCO consists of three main components: (i) a Multilingual Encoder, (ii) a Multilingual Connector, and (iii) a LexEcho Head. Figure 1 illustrates MILCO processing the Chinese input: "How to import Momo Live music to a mobile phone?" Let $\mathcal{L}$ denote the set of supported languages. For an input text $x$ in language $\ell \in \mathcal{L}$ , we first tokenize it into a sequence of $n$ source tokens:

$$
\mathbf {s} ^ {(\ell)} = (s _ {1}, \dots , s _ {n}) \tag {1}
$$

Multilingual Encoder. A transformer-based Multilingual Encoder $Enc(\cdot)$ maps the input tokens $s^{(\ell)}$ into a sequence of hidden states of dimension $d_{L}$ in a multilingual embedding space:

$$
\mathbf {H} ^ {(\ell)} = E n c (\mathbf {s} ^ {(\ell)}) \in \mathbb {R} ^ {n \times d _ {\mathcal {L}}} \tag {2}
$$

where $\mathbf{H}^{(\ell)}$ represents the contextualized embeddings for the n input tokens. For conciseness, we omit the superscript $(\ell)$ whenever the language space of the variable is unambiguous, making it H.

Multilingual Connector. The Multilingual Connector $\phi$ then projects these multilingual hidden states H into Z of dimension $d_{e}$ , which live in the embedding space of the pivot language:

$$
\mathbf {Z} = \text {LayerNorm} \left(\text {Linear} (\phi (\mathbf {H})) \in \mathbb {R} ^ {n \times d _ {e}}, \quad \text {where} \phi (\cdot): \mathbb {R} ^ {n \times d _ {\mathcal {L}}} \rightarrow \mathbb {R} ^ {n \times d _ {e}} \right. \tag {3}
$$

For simplicity, we implement the connector $\phi$ with a Multi-Layer Perceptron. This projection unifies representations across different languages through English as the pivot, allowing our LexEcho Head to project them into a shared English lexicon. While architecturally there is no restriction on the selection of the pivot language, we select English because of its rich resources and the availability of LSR teacher models for alignment, which we discuss later in this section.

LexEcho Head. The LexEcho head produces a dual-view lexical representation from the projected states Z. It generates two complementary sparse views: ① an Pivot (English) View that captures semantic concepts in English and ② a Source View that preserves important source input tokens.

① Pivot (English) View: The English lexical representation is generated by an English MLM head, as in LSR models like SPLADE (Lassance et al., 2024), but our multilingual connector extends this to the 39+ languages supported by our base model.

Multilingual representations $\mathbf{Z}$ (Eq. 3) are linearly refined and decoded onto the English vocabulary $V_{e}$ via an embedding matrix $\boldsymbol{E} \in \mathbb{R}^{|V_{e}| \times d_{e}}$ and bias $\mathbf{b}_{v}$ , yielding logits that score each source token against every English token.

$$
\mathbf {T} ^ {(e)} = \log \left(1 + \operatorname{ReLU} \left(D e c (\mathbf {Z})\right)\right) \in \mathbb {R} _ {\geq 0} ^ {n \times | V _ {e} |}, \quad \text {where} D e c (\mathbf {x}) = \mathbf {x} \boldsymbol {E} ^ {\top} + \mathbf {b} _ {v}. \tag {4}
$$

Here, we define the log-saturation effect function, introduced by MacAvaney et al. (2020); Formal et al. (2021) as LogSat( $\cdot$ ) for simplicity,

$$
\mathrm{LogSat} (\mathbf {x}) = \log (1 + \mathrm{ReLU} (\mathbf {x})) \tag {5}
$$

Next, max-pooling across source tokens (n) yields the final English lexical representation:

$$
\mathbf {t} ^ {(e)} = \left(\max _ {i} \mathbf {T} _ {i 1} ^ {(e)}, \max _ {i} \mathbf {T} _ {i 2} ^ {(e)}, \dots , \max _ {i} \mathbf {T} _ {i \mid V _ {e} \mid} ^ {(e)}\right), \quad \text {where} i \in [ 1, n ] \tag {6}
$$

This English view $\mathbf{t}^{(e)}$ is sparse and includes not only direct translations (live, music, phone) but semantically related terms (song, stream, step) that supports semantic retrieval.

② Source View: The connector maps common concepts into English but can fail on uncommon or unseen entities, especially in non-Latin scripts (e.g., Momo in Figure 1), or when names differ across languages (e.g., Douyin vs. TikTok). Scaling model size alone cannot solve this, as new entities continually appear.

[page 5]

Our LexEcho head tackles this by selectively echoing key tokens from the source. A dedicated [ECHO] token in the MLM head, denoted $Dec_{[ECHO]}(\cdot)$ , produces a weight vector w for each source token to ensure crucial tokens are selected:

$$
\mathbf {w} = \operatorname{LogSat} \left(D e c _ {[ \mathbf {E C H O} ]} (\mathbf {Z})\right) \in \mathbb {R} _ {\geq 0} ^ {n} \tag {7}
$$

By combining the English $\mathbf{t}^{(e)}$ and the weighted source views $\{\mathbf{s}_{i}^{(l)},\mathbf{w}_{i}\}_{i=1}^{n}$ , MILCO produces a dual-view representation $\mathbf{o}=\{\mathbf{t}^{(e)},\mathbf{s}^{(l)},\mathbf{w}\}$ that leverages cross-lingual projection to form a unified lexical view preserving crucial source-language tokens that would otherwise be lost in translation.

# 3.2 TRAINING: SPARSE ALIGNMENT AND CONTRASTIVE REFINEMENT

We propose a two-stage training recipe for MILCO: Sparse Alignment Pretraining to ground multilingual text to English lexical space, followed by Sparse Contrastive Training to refine alignment and optimize retrieval effectiveness, with sparsity enforced throughout.

Sparse Alignment Pretraining (SAP). To ensure the English view $\mathbf{t}^{(e)}$ is grounded in the English lexicon, we leverage widely available parallel (xx–en) sentences to align the English view of a non-English sentence to the representation of its corresponding English sentence. Given a pair of tokenized parallel sentences $(\mathbf{s}^{(\ell)}, \mathbf{s}^{(e)})$ in language $\ell$ and English, we employ an oracle teacher English LSR model, such as SPLADEv3 (Lassance et al., 2024), denoted as LSR\*, to produce the target English sparse representation $t^{*}$ .

We design a sparse-aware MSE (SMSE) loss, specifically to minimize the difference between two sparse vectors. Since most coordinates are zero, the learning signal should concentrate on the few active ones. Also, with the $\operatorname{LogSat}(\cdot)$ activation, negative pre-activation values yield zero gradients. Therefore, we compute the loss directly on the decoded logits, i.e. $\operatorname{Dec}(\mathbf{Z})$ , which were the input to $\operatorname{LogSat}(\cdot)$ , with max-pooling across the input tokens and restrict it to coordinates where at least one side is positive. For clarity, we denote such augmented representations as $\tilde{\mathbf{t}}^{(e)}$ and $\tilde{t}^{*}$ . Formally, the SMSE loss can be written as

$$
L _ {\mathrm{SMSE}} \left(\mathbf {t} ^ {(e)}, \mathbf {t} ^ {*}\right) = \frac {\sum_ {j = 1} ^ {| V _ {e} |} \mathbf {1} \left(\tilde {\mathbf {t}} _ {j} ^ {(e)} > 0 \vee \tilde {\mathbf {t}} _ {j} ^ {*} > 0\right) \left(\tilde {\mathbf {t}} _ {j} ^ {(e)} - \tilde {\mathbf {t}} _ {j} ^ {*}\right) ^ {2}}{\sum_ {j = 1} ^ {| V _ {e} |} \mathbf {1} \left(\tilde {\mathbf {t}} _ {j} ^ {(e)} > 0 \vee \tilde {\mathbf {t}} _ {j} ^ {*} > 0\right)}, \tag {8}
$$

where $1(\cdot)$ denotes the indicator function. This SMSE objective mitigates gradient dilution and focuses training on informative lexical coordinates, yielding more stable alignment. During training, we apply SMSE over batches flattened into single vectors.

Sparse Contrastive Training (SCT). Alignment pretraining grounds multilingual inputs in a shared English lexicon but is not directly optimized for retrieval. To improve effectiveness, we further train MILCO with a LexEcho head using a contrastive objective on retrieval datasets. Following Lassance et al. (2024), we use a KL distillation loss (details in Section A.7) to transfer knowledge from a cross-encoder to MILCO. To promote sparsity, we add $\ell_{1}$ -norm regularization on query and document representations q and p. Concretely, the training objective is $L_{contrastive} = L_{KLD} + \alpha_{q} \|q\|_{1} + \alpha_{d} \|p\|_{1}$ , where the $\ell_{1}$ -norms are implemented as means over the training batch.

# 4 EXPERIMENTAL SETTINGS

Pretraining, Training and Evaluation Data. For Sparse Alignment Pretraining, we use 594M bitext pairs from diverse domains collected with Sentence Transformers (Reimers & Gurevych, 2019), where each pair contains an English sentence and its translation. Dataset statistics are shown in Table 14. For Sparse Contrastive Training, we adopt the 1.4M multilingual queries released by Chen et al. (2024), with positive/negative documents and teacher scores obtained from bge-reranker-v2.5² reranker. More details are in Table 15.

[page 6]

Following Chen et al. (2024), we evaluate MILCO on four benchmarks: MIRACL (Zhang et al., b), a large-scale multilingual retrieval benchmark covering 18 languages with high-quality human annotations; MTEB v2 (Enevoldsen et al., 2025) for large-scale multilingual retrieval; MLDR (Chen et al., 2024), a multilingual long-document retrieval benchmark in 13 languages; and MKQA (Longpre et al., 2021), a cross-lingual benchmark with English documents and queries in 25 languages. Additional results on BEIR (Thakur et al., 2021), NeuCLIR (Lawrie et al., 2024) and LIMIT (Weller et al., 2025) are also included in the Appendix. Our evaluation spans 39 languages in total.

Table 1: Multilingual passage retrieval performance on the MIRACL dev set (measured by nDCG@10). Superscript $*$ : results obtained from Lassance (2023).

<table><tr><td>Model</td><td>Size</td><td>Avg</td><td>ar</td><td>bn</td><td>en</td><td>es</td><td>fa</td><td>fi</td><td>fr</td><td>hi</td><td>id</td><td>ja</td><td>ko</td><td>ru</td><td>sw</td><td>te</td><td>th</td><td>zh</td><td>de</td><td>yo</td></tr><tr><td colspan="21">Dense, multi-vector and hybrid baselines</td></tr><tr><td>mE5large</td><td>560M</td><td>66.6</td><td>76.0</td><td>75.9</td><td>52.9</td><td>52.9</td><td>59.0</td><td>77.8</td><td>54.5</td><td>62.0</td><td>52.9</td><td>70.6</td><td>66.5</td><td>67.4</td><td>74.9</td><td>84.6</td><td>80.2</td><td>56.0</td><td>56.4</td><td>78.3</td></tr><tr><td>E5mistral-7b</td><td>7.11B</td><td>63.4</td><td>73.3</td><td>70.3</td><td>57.3</td><td>52.2</td><td>52.1</td><td>74.7</td><td>55.2</td><td>52.1</td><td>52.7</td><td>66.8</td><td>61.8</td><td>67.7</td><td>68.4</td><td>73.9</td><td>74.0</td><td>54.0</td><td>54.1</td><td>79.7</td></tr><tr><td>M3-Dense</td><td>560M</td><td>69.2</td><td>78.4</td><td>80.0</td><td>56.9</td><td>56.1</td><td>60.9</td><td>78.6</td><td>58.3</td><td>59.5</td><td>56.1</td><td>72.8</td><td>69.9</td><td>70.1</td><td>78.7</td><td>86.2</td><td>82.6</td><td>62.7</td><td>56.7</td><td>81.8</td></tr><tr><td>M3-Multi-vec</td><td>560M</td><td>70.5</td><td>79.6</td><td>81.0</td><td>59.3</td><td>57.8</td><td>62.0</td><td>80.1</td><td>59.4</td><td>61.5</td><td>58.3</td><td>74.5</td><td>71.2</td><td>71.2</td><td>79.1</td><td>87.9</td><td>83.0</td><td>63.7</td><td>58.0</td><td>82.4</td></tr><tr><td>M3-Dense+Sparse</td><td>560M</td><td>70.4</td><td>79.6</td><td>80.7</td><td>58.8</td><td>58.1</td><td>62.3</td><td>79.7</td><td>58.0</td><td>62.9</td><td>58.3</td><td>73.9</td><td>71.2</td><td>69.8</td><td>78.5</td><td>87.2</td><td>83.1</td><td>63.5</td><td>57.7</td><td>83.3</td></tr><tr><td>M3-Dense+Sparse+Multivector</td><td>560M</td><td>71.5</td><td>80.2</td><td>81.5</td><td>59.6</td><td>59.7</td><td>63.4</td><td>80.4</td><td>61.2</td><td>63.3</td><td>59.0</td><td>75.2</td><td>72.1</td><td>71.7</td><td>79.6</td><td>88.1</td><td>83.7</td><td>64.9</td><td>59.8</td><td>83.5</td></tr><tr><td>PLAID-X (Multivector)</td><td>560M</td><td>55.5</td><td>66.0</td><td>68.0</td><td>46.4</td><td>51.4</td><td>48.3</td><td>52.5</td><td>61.9</td><td>42.8</td><td>56.8</td><td>44.6</td><td>61.2</td><td>63.4</td><td>61.2</td><td>32.9</td><td>75.6</td><td>72.0</td><td>44.5</td><td>49.1</td></tr><tr><td>Qwen3-Embed - 0.6B</td><td>596M</td><td>60.5</td><td>69.9</td><td>66.3</td><td>51.5</td><td>54.2</td><td>52.7</td><td>69.7</td><td>54.4</td><td>51.3</td><td>51.4</td><td>63.3</td><td>60.1</td><td>59.7</td><td>48.6</td><td>77.2</td><td>73.8</td><td>58.3</td><td>52.9</td><td>74.0</td></tr><tr><td>Qwen3-Embed - 8B</td><td>7.57B</td><td>69.8</td><td>78.2</td><td>78.3</td><td>59.8</td><td>59.6</td><td>60.5</td><td>79.0</td><td>61.0</td><td>63.1</td><td>56.1</td><td>74.3</td><td>67.5</td><td>73.5</td><td>72.2</td><td>84.3</td><td>81.5</td><td>63.3</td><td>60.5</td><td>84.5</td></tr><tr><td>MILCO-dense (align + distill)</td><td>560M</td><td>67.9</td><td>77.0</td><td>76.6</td><td>55.3</td><td>57.5</td><td>60.2</td><td>77.1</td><td>59.0</td><td>60.5</td><td>55.5</td><td>70.5</td><td>70.9</td><td>67.5</td><td>74.4</td><td>86.1</td><td>80.6</td><td>62.5</td><td>57.6</td><td>72.8</td></tr><tr><td>MILCO-dense (distill)</td><td>560M</td><td>70.9</td><td>79.5</td><td>80.2</td><td>56.8</td><td>60.4</td><td>63.4</td><td>78.5</td><td>62.6</td><td>62.2</td><td>58.4</td><td>74.7</td><td>70.5</td><td>72.1</td><td>79.6</td><td>87.0</td><td>82.9</td><td>64.2</td><td>59.5</td><td>83.2</td></tr><tr><td colspan="21">Sparse baselines</td></tr><tr><td>BM25</td><td>2</td><td>31.9</td><td>39.5</td><td>48.2</td><td>26.7</td><td>7.7</td><td>28.7</td><td>45.8</td><td>11.5</td><td>35.0</td><td>29.7</td><td>31.2</td><td>37.1</td><td>25.6</td><td>35.1</td><td>38.3</td><td>49.1</td><td>17.5</td><td>12.0</td><td>56.1</td></tr><tr><td>T-Splade*</td><td>3.4B</td><td>54.5</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr><tr><td>mSPLADEsTok*</td><td>-</td><td>63.9</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td><td>-</td></tr><tr><td>OpenSearch3</td><td>167M</td><td></td><td>74.0</td><td>67.0</td><td>57.5</td><td>54.2</td><td>51.4</td><td>76.7</td><td>55.8</td><td>48.6</td><td>58.2</td><td>66.9</td><td>60.7</td><td>65.8</td><td>76.8</td><td>74.0</td><td>-</td><td>56.2</td><td>-</td><td>-</td></tr><tr><td>M3-Sparse</td><td>560M</td><td>53.9</td><td>67.1</td><td>68.9</td><td>43.8</td><td>38.6</td><td>45.1</td><td>65.4</td><td>35.3</td><td>48.2</td><td>48.9</td><td>56.1</td><td>61.5</td><td>44.5</td><td>57.9</td><td>79.1</td><td>70.9</td><td>36.1</td><td>32.5</td><td>70.0</td></tr><tr><td>1 MILCO (SAP, SCTKD, LexEcho)</td><td>560M</td><td>72.3</td><td>80.4</td><td>82.6</td><td>60.4</td><td>60.9</td><td>62.3</td><td>81.2</td><td>61.7</td><td>64.4</td><td>60.9</td><td>77.2</td><td>72.1</td><td>74.6</td><td>80.3</td><td>87.9</td><td>84.2</td><td>65.5</td><td>61.4</td><td>83.6</td></tr><tr><td>2 MILCO (SAP, SCTKD, MLMen)</td><td>560M</td><td>69.4</td><td>77.3</td><td>79.5</td><td>57.6</td><td>59.7</td><td>58.5</td><td>78.8</td><td>60.6</td><td>63.4</td><td>57.7</td><td>72.8</td><td>67.7</td><td>72.6</td><td>78.1</td><td>82.3</td><td>80.4</td><td>60.6</td><td>59.7</td><td>81.2</td></tr><tr><td>3 MILCO (SAP, SCT, LexEcho)</td><td>560M</td><td>70.1</td><td>79.4</td><td>80.8</td><td>57.6</td><td>57.2</td><td>60.6</td><td>80.1</td><td>57.7</td><td>63.3</td><td>58.4</td><td>75.2</td><td>71.0</td><td>72.6</td><td>77.2</td><td>87.2</td><td>82.7</td><td>60.8</td><td>59.3</td><td>81.6</td></tr><tr><td>4 MILCO (SAP, MLMen)</td><td>560M</td><td>54.5</td><td>59.8</td><td>59.7</td><td>57.0</td><td>56.0</td><td>44.9</td><td>66.0</td><td>48.2</td><td>58.6</td><td>48.8</td><td>54.9</td><td>59.4</td><td>51.2</td><td>47.8</td><td>55.0</td><td>55.9</td><td>46.7</td><td>48.5</td><td>62.2</td></tr><tr><td>5 MILCO (SCTKD, MLMen)</td><td>560M</td><td>59.2</td><td>72.7</td><td>72.3</td><td>47.7</td><td>47.6</td><td>50.9</td><td>72.5</td><td>48.8</td><td>50.4</td><td>51.8</td><td>64.0</td><td>62.7</td><td>53.6</td><td>62.3</td><td>77.7</td><td>72.8</td><td>46.2</td><td>44.8</td><td>66.2</td></tr><tr><td>6 noMILCO (SCTKD, MLMm)</td><td>560M</td><td>50.7</td><td>65.8</td><td>62.0</td><td>39.7</td><td>39.4</td><td>42.0</td><td>67.0</td><td>38.5</td><td>36.9</td><td>44.9</td><td>56.1</td><td>52.9</td><td>47.3</td><td>58.6</td><td>71.0</td><td>67.0</td><td>41.8</td><td>34.6</td><td>46.9</td></tr></table>

Baselines. We compare MILCO against two group of baselines: Dense/Multi-vector and Sparse methods. For dense/multi-vector baselines, we include recent state-of-the-art methods, including multilingual E5 (Wang et al., 2024), BGE-M3 (Chen et al., 2024), PLAID-X (Yang et al., 2024b), Qwen3 Embeddings (Zhang et al., 2025). For sparse baselines, we include unsupervised BM25, M3-Sparse (Chen et al., 2024) and also OpenSearch (Shen et al., 2025), T-Splade (Lassance, 2023), mSplade (Lassance, 2023). Among these, T-Splade is the approach that translates text into English and encodes the translated text by the Splade model (Formal et al., 2021).

# MILCO configurations. We consider the following configurations in experiments:

① MILCO (SAP, SCT $_{KD}$ , LexEcho): Our strongest setup, which combines alignment with contrastive distillation training and the LexEcho head, producing dual-view lexical representations.
② MILCO (SAP, $\mathrm{SCT}_{\mathrm{KD}}$ , $\mathrm{MLM}_{\mathrm{en}}$ ): Similar to (1), but the source view is removed from LexEcho's output, producing only English lexical representations.
③ MILCO (SAP, SCT, LexEcho): Similar to (1), but without distillation. Instead, the InfoNCE loss (Oord et al., 2018) with in-batch negatives is used for Sparse Contrastive Training.
④ MILCO (SAP, MLM $_{en}$ ): Similar to (2), but without Sparse Contrastive Training.
⑤ MILCO (SCT $_{KD}$ , MLM $_{en}$ ): Similar to (2), but without Sparse Alignment Pre-training.
⑥ noMILCO (SCT $_{KD}$ , MLM $_{m}$ ): A baseline model trained directly with the full multilingual MLM head (without our multilingual connector).

We initialized MILCO from the bge-m3-unsupervised $^{4}$ multilingual base encoder and initialized the LexEcho head with Splade-v3's English MLM head (Lassance et al., 2024). We use Splade-v3 representations of English text for alignment pretraining. More details on hyperparameters and hardware are provided in Section A.8 of the Appendix.

#

[page 7]

5 RESULTS AND DISCUSSION

RQ1: How does MILCO perform compared to state-of-the-art baselines? Table 1 reports the performance of MILCO and baselines on the MIRACL benchmark (18 languages). Overall, the MILCO ① model, trained with our two-stage pipeline and LexEcho head, achieves the highest effectiveness with an average nDCG@10 of 72.3.

Against sparse baselines, MILCO outperforms M3-Sparse (Chen et al., 2024) by 34.1%, T-Splade (Lassance, 2023) by 32.7%, and MSpladesTok (Lassance, 2023) by 13.1%. Against dense baselines, MILCO still shows substantially higher effectiveness, though with smaller margins. Compared to models of similar size, it outperforms Qwen3 0.6B (Zhang et al., 2025) and M3-Dense (Chen et al., 2024) by 19.5% and 4.5%, respectively, on MIRACL. This advantage generalizes to 39 languages on MTEB v2 cross-lingual and multilingual retrieval (Table 3). Despite being $\sim14\times$ smaller, it outperforms E5-Mistral 7B (Wang et al., 2023) and Qwen3 8B on MIRACL, though Qwen3 8B performs better on MTEBv2 where it better leverages task-specific instructions. We additionally train two dense baselines using the same backbone and training data as MILCO. The first, MILCO-dense (align + distill), which uses dense alignment to thenlper/gte-base $^{5}$ and distillation, achieves an average nDCG@10 of 67.9 on MIRACL. A variant trained with distillation only performs better, reaching 70.9 nDCG@10 on MIRACL. However, both dense baselines still substantially underperform our best sparse MILCO $^{①}$ trained with the two-stage recipe.

Table 2: Performance on Multilingual Long Document Retrieval (nDCG@10, 13 languages). More language-specific details in Table 6.

<table><tr><td>Model</td><td>Size</td><td>Max Length</td><td>Avg</td></tr><tr><td colspan="4">Dense, multi-vector and hybrid baselines</td></tr><tr><td>mE5large</td><td>560M</td><td>512</td><td>34.2</td></tr><tr><td>E5mistral-7b</td><td>7B</td><td>8192</td><td>42.6</td></tr><tr><td>M3-Dense</td><td>560M</td><td>8192</td><td>52.5</td></tr><tr><td>M3-Multi-vector</td><td>560M</td><td>8192</td><td>57.6</td></tr><tr><td>M3-Dense+Sparse</td><td>560M</td><td>8192</td><td>64.8</td></tr><tr><td>M3-All</td><td>560M</td><td>8192</td><td>65.0</td></tr><tr><td>mGTE-TRM Dense</td><td>304M</td><td>8192</td><td>56.9</td></tr><tr><td>mGTE-TRM Dense + Sparse</td><td>304M</td><td>8192</td><td>71.3</td></tr><tr><td>PLAID-X (Multi-vector)</td><td>560M</td><td>512</td><td>74.2</td></tr><tr><td>Qwen3-Embed-0.6B</td><td>0.6B</td><td>32768</td><td>50.1</td></tr><tr><td>Qwen3-Embed-8B</td><td>8B</td><td>32678</td><td>59.1</td></tr><tr><td colspan="4">Sparse baselines</td></tr><tr><td>BM25</td><td>2</td><td>8192</td><td>53.6</td></tr><tr><td>M3-Sparse</td><td>560M</td><td>8192</td><td>62.2</td></tr><tr><td>mGTE-TRM Sparse</td><td>304M</td><td>8192</td><td>71.0</td></tr><tr><td>1MILCO (SAP, SCTKD, LexEcho)</td><td>560M</td><td>512</td><td>74.4</td></tr><tr><td>2MILCO (SAP, SCTKD, MLMen)</td><td>560M</td><td>512</td><td>69.9</td></tr></table>

Table 3: Performance on multilingual and cross-lingual retrieval tasks on Multilingual MTEBv2. (39 languages). More details in Table 7.

<table><tr><td>Model</td><td>Size</td><td>Avg</td></tr><tr><td colspan="3">Large Models (≥1B)</td></tr><tr><td>Qwen3-Embed-8B</td><td>8B</td><td>75.59</td></tr><tr><td>jina-embeddings-v4</td><td>3.8B</td><td>73.84</td></tr><tr><td>inf-retriever-v1</td><td>7.1B</td><td>71.21</td></tr><tr><td>SFR-Embedding-Mistral</td><td>7.1B</td><td>68.50</td></tr><tr><td>gte-Qwen2-7B-inst</td><td>7B</td><td>67.22</td></tr><tr><td>inf-retriever-v1-1.5b</td><td>1.5B</td><td>65.34</td></tr><tr><td>gte-Qwen2-1.5B-inst</td><td>1.5B</td><td>65.12</td></tr><tr><td>GritLM-7B</td><td>7B</td><td>62.82</td></tr><tr><td>NV-Embed-v2</td><td>7.9B</td><td>58.65</td></tr><tr><td>NV-Embed-v1</td><td>7.9B</td><td>56.64</td></tr><tr><td colspan="3">Small Models (&lt;1B)</td></tr><tr><td>gte-multilingual-base</td><td>305M</td><td>64.72</td></tr><tr><td>Qwen3-Embed-0.6B</td><td>0.6B</td><td>63.93</td></tr><tr><td>bge-m3</td><td>560M</td><td>62.02</td></tr><tr><td>granite-278m-multi</td><td>278M</td><td>55.80</td></tr><tr><td>granite-107m-multi</td><td>107M</td><td>49.88</td></tr><tr><td>1 MILCO (SAP, SCT $_{KD}$ , LexEcho)</td><td>560M</td><td>66.83</td></tr></table>

We further evaluate MILCO on the Multilingual Long Document Retrieval (MLDR) benchmark (Table 2). Because MILCO is trained with a 512-token limit, we split long documents into 512-token passages and score documents by their best passage. Under this setup, MILCO achieves an average nDCG@10 of 74.4, which is 14% higher than M3-All, the dense+sparse+multi-vector ensemble, and substantially surpasses Qwen3 0.6B and 8B with native long-context support.

In the Appendices, we report results on LIMIT Test (Weller et al., 2025) (Table 11) and BEIR (Thakur et al., 2021) (Table 10). On LIMIT, MILCO substantially outperforms all dense baselines regardless of size. On BEIR (English), it trails Qwen3 0.6B slightly, but scales better on large collections.

RQ2: What is the effect of sparse alignment and contrastive training in MILCO? We observe that Sparse Alignment Pretraining is crucial to ensure that the model's output is grounded in the English vocabulary. In Figure 2, we show two examples of MILCO's output under three training setups. Without SAP, contrastive training leads to semantic collapse, where the model produces

[page 8]

completely random and unexplainable (latent) output tokens with no clear relation to the input. We observe the same effect when we train noMILCO ⑥, a multilingual LSR model without the multilingual connector (similar to Splade training). With alignment pretraining, MILCO produces understandable and semantically equivalent English tokens as demonstrated in the figure. However, we observe that both Alignment-only and Contrastive-only result in mediocre multilingual retrieval effectiveness. On MIRACL results in Table 1, Alignment-only MILCO ④ and Contrastive-only MILCO ⑤ only achieve the average nDCG@10 of 54.5 and 59.2 respectively. Direct training without our connector (noMILCO ⑥) leads to a larger drop in performance, resulting in nDCG@10 of 50.7.

To further improve retrieval effectiveness, we finetune MILCO on retrieval data with a contrastive objective. We experiment with two contrastive losses: InfoNCE with dataset-provided labels (MILCO ③) and KL divergence for knowledge distillation (MILCO ①). With an InfoNCE loss, MILCO ③'s average nDCG@10 improves by 28.62%, from 54.5 with only alignment to 70.1, becoming competitive to BGE-M3-Dense and Multi-vector models. Adding distillation further boosts effectiveness, increasing nDCG@10 to 72.3 and making MILCO substantially outperform all baselines, including the hybrid BGE-M3 dense-sparse-multivector model and Qwen3 models.

RQ3: Does the proposed LexEcho head improve robustness? Unlike dense or multi-vector methods, the transparency of MILCO's sparse, lexicalized representations make errors traceable. When analyzing the English view, we found that representations often miss uncommon entities like Momo in Figure 3, leading to reduced retrieval accuracy. In the figure, Doc2 (score = 9.64) is ranked below Doc1 (score = 9.89), despite being more relevant.

The LexEcho head addresses this with a dual-view representation composed of an English view and a source view. When an important entity is missing from the English view, MILCO can fall back to the source view for source-token matching. In Figure 3, LexEcho seems to recognize the model's missing knowledge of Momo in English and assigns a high weight to 陌 in the Chinese view. In contrast, for Apple, the model relies primarily on English representations (assigning them the highest weights in Doc1 and Doc3) while assigning 苹果 (Apple) a low weight in the Chinese view.

On MIRACL (Table 1), MILCO ① with a LexEcho head consistently outperforms MILCO ② with only an English view across all 18 languages, achieving an average nDCG@10 of 72.3 (+4.17% over 69.4). The largest gains occur in non-Latin languages such as Chinese (zh: +8.09%), Telugu (te: +6.8%), Farsi (fa: +6.5%), Korean (ko: +6.5%), and Japanese (ja: +6.04%), where mapping entities into English is particularly difficult since entities could be named differently in English. The benefits of the LexEcho head also extend to long-document retrieval: on MLDR (Table 2), MILCO with LexEcho achieves 74.4 nDCG@10, a 6.43% improvement over MILCO with only an English view (69.5). These highlight the broader robustness of our approach.

RQ4: Can MILCO perform zero-shot cross-lingual retrieval? MILCO uses the multilingual connector to maps text across languages into a unified English lexical view. This allows MILCO to perform zero-shot cross-lingual retrieval, which is not possible with sparse models like M3-Sparse that rely on only a source view. We benchmark the cross-lingual capability of MILCO (zero-shot) and baselines on MKQA with R@100 in Table 4.

Prior sparse methods (e.g., BM25, BGE-M3-Sparse) generate source-view representations including input tokens with scalar weights. Their vocabularies are language-specific, so inputs in Chinese

<table><tr><td>Alignment Only</td><td>Alignment + Contrastive</td><td>Contrastive Only</td></tr><tr><td colspan="3">Input (de): Baltimore Maryland die großartigste Stadt in Amerika (Baltimore Maryland the greatest city in America)</td></tr><tr><td>baltimore (2.22), maryland (1.86), city (1.40), greatest (1.25), biggest (0.98), garrison (0.35), geography (0.31), tourism (0.19) ...</td><td>baltimore (1.77), city (1.52), maryland (1.23), america (1.19), greatest (0.89), usa (0.81), best (0.62), urban (0.26) ...</td><td>governing (1.17), past (1.07), match (0.95), worn (0.86), sky (0.65), gas (0.52), boot (0.34), mayor (0.31) ...</td></tr><tr><td colspan="3">Input (vi): Giá trị tài sản ròng của Tesla là bao nhiều? (What is Tesla&#x27;s net worth?)</td></tr><tr><td>tesla (3.36), worth (2.61), price (1.84), net (1.52), salary (1.14), money (0.80), mining (0.35), generation (0.33) ...</td><td>tesla (3.02), worth (1.89), price (1.47),net (1.37), wealth (0.71), asset (0.63), stock (0.42), company (0.41) ...</td><td>relative (0.97), drinks (0.75), gaelic (0.75), contaminated (0.73), sigh (0.67), webb (0.60), dust (0.46), – (1.22) ...</td></tr></table>

Figure 2: Sparse representations with different training strategies. Alignment only produces many grounded tokens (green) but also distantly relevant tokens (orange), Contrastive further prunes and refines. Contrastive-only suffers from semantic collapse, drifting toward ungrounded tokens (red).

<table><tr><td>Input</td><td>Translation</td><td>(1) LexEcho (English View)</td><td>(2) LexEcho (Source View)</td><td>Score (1)</td><td>Score (1)+(2)</td></tr><tr><td>Query:陌陌直播音乐怎么导入手机?</td><td>How to importMomoLive Music into mobile phone?</td><td>music(1.16), import(0.95), phone(0.88), step(0.80), transfer(0.72), no(0.69), songs(0.55), live(0.51), song(0.49), phones(0.46), stream(0.44) ...</td><td>陌(1.46), 手机(0.97), 导(0.68), 直播(0.67), 音乐(0.65), &lt;s&gt;(0.38), 怎么(0.38), 入(0.36), ?(0.34), _(0.19)</td><td></td><td></td></tr><tr><td>Doc1:用户可将苹果音乐歌曲下载或录音保存,再导入手机播放</td><td>Users can downloadAppleMusic songs and then import them into their phones ...</td><td>apple(1.72), music(1.58), step(1.33), songs(1.30), download(1.27), phone(1.18), is(1.18), play(1.14), song(1.09), can(1.03), save(1.03), app(0.95), ...</td><td>音乐(0.46), 用户(0.45), 歌曲(0.44), 选择(0.40), 导(0.40), 的方式(0.34), 上的(0.34), 保存(0.28), 可以(0.27), 苹果(0.23) ...</td><td>9.89Rank 1</td><td>11.66Rank 2</td></tr><tr><td>Doc2:陌陌直播的歌曲可以用保存功能转到手机.</td><td>Songs fromMomoLive can be saved to your phone using the save function.</td><td>step(1.62), songs(1.32), save(1.29), phone(1.20), song(1.15), music(1.07), storage(1.01), live(0.84), can(0.81), transfer(0.81), stream(0.79) ...</td><td>陌(1.54), 歌曲(0.72), 直播(0.71), 功能(0.67), 手机(0.64), 你可以(0.59), 保存(0.56), 用(0.54), _(0.53), 把(0.51) ...</td><td>9.64Rank 2</td><td>13.27Rank 1</td></tr></table>

[page 9]

Figure 3: The tail entity Momo is missing in the English view of the query and Doc2, reducing Doc2's score despite its higher relevance. The LexEcho head resolves this by selectively retaining missing entities from source tokens, correctly ranking Doc2 on top.

yield only Chinese tokens. This causes vocabulary mismatch and poor cross-lingual retrieval, with average R@100 scores of just 39.9 and 45.3 on MKQA. In contrast, MILCO avoids this issue with a shared English lexical space. Despite not being trained for cross-lingual retrieval, MILCO achieves strong results on MKQA, with a zero-shot R@100 of 76.6, improving 91.9% and 69.1% over BM25 and BGE-M3-Sparse, respectively.

Dense and multi-vector methods operate in a latent space, so they do not suffer from vocabulary mismatch and perform reasonably well on MKQA. BGE-Dense and multi-vector models are among the strongest baselines, with an average R@100 of around 75. While these methods outperform sparse baselines (e.g., BM25 or BGE-M3-Sparse), MILCO achieves about 1.7–1.9% higher R@100 than the BGE dense and multi-vector baselines, while also retaining the transparency that facilitate model analysis and error tracing. MILCO is about 9% and 12.8% better than E5-Mistral 7B and Qwen3 8B, respectively, despite having only 560M parameters.

# 6 EFFICIENCY

# AND EFFECTIVENESS TRADEOFFS

Table 4: Cross-lingual retrieval performance on MKQA, averaged across 25 languages. More details in Table 9.

<table><tr><td>Model</td><td>Avg (R@100)</td></tr><tr><td colspan="2">Baselines</td></tr><tr><td>E5-large</td><td>70.9</td></tr><tr><td>E5-mistral-7b</td><td>70.1</td></tr><tr><td>BGE-M3 Dense</td><td>75.1</td></tr><tr><td>BGE-M3 Multi-Vec</td><td>75.3</td></tr><tr><td>BGE-M3 Dense+Sparse</td><td>75.3</td></tr><tr><td>PLAID-X (multivector)</td><td>73.4</td></tr><tr><td>Qwen3-Embed-0.6B</td><td>54.4</td></tr><tr><td>Qwen3-Embed-8B</td><td>67.9</td></tr><tr><td>BM25</td><td>39.9</td></tr><tr><td>BGE-M3 Sparse</td><td>45.3</td></tr><tr><td>1 MILCO (SAP,  $SCT_{KD}$ , LexEcho)</td><td>76.6</td></tr></table>

# Model Size vs. Effectiveness. In Figure 4, we plot

MILCO's effectiveness against model size compared to baselines. We observe that MILCO, with 560M parameters, is the most effective model within its size range and even substantially outperforms larger models (e.g., Qwen3-8B and E5-Mistral-7B) across all 18 MIRACL languages. With the same model size, the BGE-M3-Multivector model underperforms MILCO despite producing multiple dense vectors for each query/document.

Sparsity vs. Effectiveness. Dense retrieval models like Matryoshka representations (Kusupati et al., 2022) support truncating embeddings for efficiency, but require additional Matryoshka training losses. MILCO and LSR methods naturally allow post-hoc pruning (Lei et al., 2025; Wen et al., 2025; Bruch et al., 2024), because LSR encodes queries and documents as weighted tokens that can be ranked and truncated at inference. Unlike Matryoshka, which applies the same truncation size to all inputs, LSR supports variable k (e.g., fewer tokens for shorter texts). Figure 5 compares two pruning strategies: top-k pruning and mass-based pruning, which removes the p-tail percentile of token weights, yielding variable tokens per document. Exact numbers are included in the Appendix 12. Mass-based pruning delivers a slightly more favorable trade-off than top-k pruning. At p = 95, it averages only 30 tokens/document yet already surpasses Qwen3-Embed 0.6B on nDCG@10 (62.2). It reaches 96% of full performance at p = 86 (86.4 tokens/doc) and achieves SOTA at 300 tokens, with only marginal gains beyond. With LexEcho's vocabulary of 280k terms, activating just 300 tokens (0.1%) yields representations that are 99.9% sparse, transparent, and highly effective.

Sparsity vs. Efficiency. We report index statistics and retrieval latency with MILCO under an inverted-index setting. We use Seismic (Bruch et al., 2024), an ANN method built on top of an inverted index. All results are on MIRACL (English subset, about 32M passages), with retrieval run

![](../assets/doc-005-page10-img1.jpeg)

<details>
<summary>scatter</summary>

| Model | Model Type | Model Size (Billion Parameters, log scale) | nDCG@10 |
| --- | --- | --- | --- |
| mContriever | Dense | ~0.18 | ~44 |
| mDPR | Dense | ~0.19 | ~45 |
| M3-Sparse | Sparse | ~0.55 | ~54 |
| Qwen3 0.6B | Dense | ~0.6 | ~61 |
| M3-Dense | Dense | ~0.6 | ~67 |
| M3-Multi-vec | Dense | ~0.6 | ~70 |
| MILCO LexEcho | Sparse | ~0.6 | ~72 |
| MILCO MLM_en | Dense | ~0.6 | ~70 |
| E5large | Dense | ~0.6 | ~69 |
| T-Splade* | Sparse | ~2.5 | ~55 |
| Qwen3 8B | Dense | ~8 | ~71 |
| E5mistral 7B | Dense | ~8 | ~64 |
</details>

Figure 4: Model size versus effectiveness on MIRACL. MILCO is lightweight (560M params), while being highly effective.

![](../assets/doc-005-page10-img2.jpeg)

<details>
<summary>line</summary>

| Tokens Kept | Top-K Pruning | Mass-based Pruning |
| --- | --- | --- |
| 10 | 44.5 | 39.5 |
| 20 | 54.5 | 56.0 |
| 50 | 63.5 | 67.4 |
| 100 | 68.5 | 70.6 |
| 200 | 71.0 | 72.3 |
</details>

Figure 5: Effectiveness (nDCG@10, MIRACL) of MILCO with varying sparsity levels obtained by post-hoc pruning methods.

Table 5: Retrieval Latency of MILCO sparse retrieval with Seismic and Qwen3-Embedding-0.6B dense retrieval with Faiss.

<table><tr><td>Model</td><td>Index</td><td>Avg Latency (ms)</td><td>P95 Latency (ms)</td><td>QPS</td><td>nDCG@10</td><td>Index Size</td></tr><tr><td>Qwen3-Embed-0.6B</td><td>HNSW</td><td>1.29</td><td>1.47</td><td>777</td><td>50.4</td><td>134G</td></tr><tr><td>MILCO (p=0)</td><td>Seismic</td><td>1.85</td><td>4.32</td><td>538</td><td>56.4</td><td>61G</td></tr><tr><td>MILCO (p=10)</td><td>Seismic</td><td>1.29</td><td>2.92</td><td>774</td><td>56.3</td><td>40G</td></tr><tr><td>MILCO (p=30)</td><td>Seismic</td><td>0.61</td><td>1.26</td><td>1647</td><td>54.4</td><td>25G</td></tr><tr><td>MILCO (p=50)</td><td>Seismic</td><td>0.65</td><td>1.33</td><td>1545</td><td>53.3</td><td>16G</td></tr><tr><td>MILCO (p=60)</td><td>Seismic</td><td>0.44</td><td>0.82</td><td>2265</td><td>50.3</td><td>12G</td></tr></table>

[page 10]

on a single AMD EPYC 7763 CPU core. We build several indexes of the pivot view with hyperparameters (n\_postings=15000, query\_cut=10, heap\_factor=0.9) and different amounts of post-hoc pruning. The unpruned index (p = 0) has an average posting-list length of 4636.09, resulting in a 61 GB index and an average retrieval latency of 1.85 ms/query. We then prune the lowest-weight dimensions whose cumulative weights account for $p \in \{10, 30, 50, 60\}\%$ of the total, which shrinks the inverted index and speeds up retrieval. Results are shown in Table 5.

Regarding index size, post-hoc pruning substantially shrinks the index: 40 GB at p = 10, 25 GB at p = 30, 16 GB at p = 50, and 12 GB at p = 60. Thus, at the most aggressive pruning level, we reduce index size by roughly 80% while keeping strong retrieval effectiveness. To contextualize these index sizes, we compare against Qwen3-Embedding-0.6B with a Faiss dense HNSW index (Douze et al., 2024) (M = 32, ef = 64) on the same hardware and collection. This dense baseline has an index size of 134 GB, whereas MILCO's pruned Seismic index is already smaller at p = 10 (40 GB) and becomes 5–10× smaller at higher pruning levels (25 GB at p = 30, 12 GB at p = 60).

Regarding latency, pruning also yields consistent improvements over the full representation: $p = 10$ reduces average latency from 1.85 ms to 1.29 ms ( $\sim 30\%$ speed-up) with virtually no loss in nDCG@10 (56.4 $\rightarrow$ 56.3), $p = 30$ makes queries about $3 \times$ faster (0.61 ms, nDCG@10 = 54.4), and even $p = 60$ achieves a $> 4 \times$ speed-up (0.44 ms) while remaining competitive (nDCG@10 = 50.3). For comparison, the Qwen3-Embedding-0.6B + Faiss HNSW achieves an average latency of 1.29 ms and nDCG@10 = 50.4. Seismic's ANN inverted index with pruning therefore allows MILCO to (i) match this latency at $p = 10$ while achieving substantially higher effectiveness (nDCG@10 = 56.3), and (ii) further reduce latency to $\approx 0.44$ ms at $p = 60$ , while remaining at least as effective overall.

# 7 CONCLUSION

We introduced MILCO, a novel multilingual learned sparse retriever that connects 39 languages to a shared English lexical space through a lightweight connector. Alignment pretraining enables the use of contrastive training, whereas the LexEcho preserves entities lost during cross-lingual projection. MILCO delivers strong zero-shot cross-lingual retrieval, showing competitive performance without cross-lingual retrieval training. Overall, MILCO achieves state-of-the-art multilingual retrieval results, while offering transparent representations and efficient post-hoc pruning.

#

[page 11]

REPRODUCIBILITY STATEMENT

We have taken several measures to ensure the transparency and reproducibility of our work.

Datasets. All datasets used for pretraining and training MILCO models are publicly available. Table 14 (Appendix) reports statistics on the number and sources of parallel sentences used for Sparse Alignment Pretraining, while Table 15 (Appendix) describes the datasets used for Sparse Contrastive Training. These datasets are widely adopted in prior work on dense retrieval (Wang et al., 2024; Chen et al., 2024; Li et al.). We note, however, that some recent models such as Qwen3-Embed (Zhang et al., 2025) do not disclose their training data, which makes direct comparisons not strictly fair.

Hyper-parameters and hardware. All hyper-parameters and hardware specifications used for Sparse Alignment and Sparse Contrastive Training are described in Section A.8 (Appendix). Any hyper-parameters not explicitly listed are set to the default values provided in HuggingFace's Trainer (Wolf et al., 2019), which we use to train our models. During pretraining and training, we hard-coded the random seed to 42.

Code. Our code is available at: https://github.com/thongnt99/milco.

Models and evaluation. MILCO is trained on 63 languages and evaluated on 39 languages, as detailed in Section A.9 (Appendix). Trained MILCO checkpoints are released at: https://github.com/thongnt99/milco. To illustrate the multilingual capabilities of our model, we provide example inputs and their corresponding sparse representations across multiple languages in Section A.1 (Appendix).

# ETHICS STATEMENT

We present MILCO, a multilingual learned sparse retrieval method supporting 39 languages. All datasets and models used to train MILCO are publicly available, and we do not introduce any proprietary or sensitive data. Since our work builds on public data, it may reflect biases present in those sources. We aims to broaden access to multilingual information retrieval research, especially for underrepresented languages.

# ACKNOWLEDGMENT

This research was supported by the Hybrid Intelligence Center, a 10-year program funded by the Dutch Ministry of Education, Culture and Science through the Netherlands Organisation for Scientific Research, project VI.Vidi.223.166 of the NWO Talent Programme which is (partly) financed by the Dutch Research Council (NWO). We acknowledge the Dutch Research Council for awarding this project access to the LUMI supercomputer, owned by the EuroHPC Joint Undertaking, hosted by CSC (Finland) and the LUMI consortium through project number NWO-2024.050.

# REFERENCES

Luiz Bonifacio, Vitor Jeronymo, Hugo Queiroz Abonizio, Israel Campiotti, Marzieh Fadaee, Roberto Lotufo, and Rodrigo Nogueira. mmarco: A multilingual version of the ms marco passage ranking dataset. arXiv:2108.13897, 2021.
Sebastian Bruch, Franco Maria Nardini, Cosimo Rulli, and Rossano Venturini. Efficient inverted indexes for approximate retrieval over learned sparse representations. In Proc. of SIGIR, pp. 152–162, 2024.
Daniel Campos, Alessandro Magnani, and Chengxiang Zhai. Quick dense retrievers consume KALE: Post training KullbackLeibler alignment of embeddings for asymmetrical dual encoders. In Proc. of ACL Workshop on SustaiNLP, pp. 59–77, 2023.
Jianlv Chen, Shitao Xiao, Peitian Zhang, Kun Luo, Defu Lian, and Zheng Liu. Bge m3-embedding: Multi-lingual, multi-functionality, multi-granularity text embeddings through self-knowledge distillation. arXiv:2402.03216, 2024.
Zewen Chi, Li Dong, Furu Wei, Nan Yang, Saksham Singhal, Wenhui Wang, Xia Song, Xian-Ling Mao, Heyan Huang, and Ming Zhou. InfoXLM: An information-theoretic framework for cross-lingual language model pre-training. In Proc. of NAACL-HLT.
Arman Cohan, Sergey Feldman, Iz Beltagy, Doug Downey, and Daniel S Weld. Specter: Document-level representation learning using citation-informed transformers. In Proc. of ACL, pp. 2270–2282, 2020.
Alexis Conneau, Kartikay Khandelwal, Naman Goyal, Vishrav Chaudhary, Guillaume Wenzek, Francisco Guzmán, Édouard Grave, Myle Ott, Luke Zettlemoyer, and Veselin Stoyanov. Unsupervised cross-lingual representation learning at scale. In Proc. of ACL, pp. 8440–8451, 2020.
Matthijs Douze, Alexandr Guzhva, Chengqi Deng, Jeff Johnson, Gergely Szilvasy, Pierre-Emmanuel Mazaré, Maria Lomeli, Lucas Hosseini, and Hervé Jégou. The faiss library. 2024.
Kenneth Enevoldsen, Isaac Chung, Imene Kerboua, Márton Kardos, Ashwin Mathur, David Stap, Jay Gala, Wissam Siblini, Dominik Krzemiński, Genta Indra Winata, et al. Mmteb: Massive multilingual text embedding benchmark. arXiv:2502.13595, 2025.
Angela Fan, Yacine Jernite, Ethan Perez, David Grangier, Jason Weston, and Michael Auli. Eli5: Long form question answering. In Proc. of ACL, pp. 3558–3567, 2019.
Fangxiaoyu Feng, Yinfei Yang, Daniel Cer, Naveen Arivazhagan, and Wei Wang. Language-agnostic bert sentence embedding. In Proc. of ACL (Volume 1: Long Papers), pp. 878–891, 2022.
Thibault Formal, Benjamin Piwowarski, and Stéphane Clinchant. Splade: Sparse lexical and expansion model for first stage ranking. In Proc. of SIGIR, pp. 2288–2292, 2021.
Thibault Formal, Carlos Lassance, Benjamin Piwowarski, and Stéphane Clinchant. From distillation to hard negative sampling: Making sparse neural ir models more effective. In Proc. of SIGIR, pp. 2353–2359, 2022.
Martin Gellerstam. Translationese in swedish novels translated from english. Translation studies in Scandinavia, 1:88–95, 1986.
Wei He, Kai Liu, Jing Liu, Yajuan Lyu, Shiqi Zhao, Xinyan Xiao, Yuan Liu, Yizhong Wang, Hua Wu, Qiaoqiao She, et al. Dureader: a chinese machine reading comprehension dataset from real-world applications. arXiv:1711.05073, 2017.
Mandar Joshi, Eunsol Choi, Daniel Weld, and Luke Zettlemoyer. TriviaQA: A large scale distantly supervised challenge dataset for reading comprehension. In Proc. of ACL (Volume 1: Long Papers), 2017.
Seungyeon Kim, Ankit Singh Rawat, Manzil Zaheer, Sadeep Jayasumana, Veeranjaneyulu Sadhanala, Wittawat Jitkrittum, Aditya Krishna Menon, Rob Fergus, and Sanjiv Kumar. Embeddistill: A geometric knowledge distillation for information retrieval. arXiv:2301.12005, 2023.
Aditya Kusupati, Gantavya Bhatt, Aniket Rege, Matthew Wallingford, Aditya Sinha, Vivek Ramanujan, William Howard-Snyder, Kaifeng Chen, Sham Kakade, Prateek Jain, et al. Matryoshka representation learning. Proc. of NeurIPS, 35:30233–30249, 2022.
Tom Kwiatkowski, Jennimaria Palomaki, Olivia Redfield, Michael Collins, Ankur Parikh, Chris Alberti, Danielle Epstein, Illia Polosukhin, Jacob Devlin, Kenton Lee, et al. Natural questions: a benchmark for question answering research. Transactions of the Association for Computational Linguistics, 7:453–466, 2019.
Carlos Lassance. Extending english ir methods to multi-lingual ir. arXiv:2302.14723, 2023.
Carlos Lassance, Hervé Déjean, Thibault Formal, and Stéphane Clinchant. Splade-v3: New baselines for splade. arXiv:2403.06789, 2024.
Dawn Lawrie, Sean MacAvaney, James Mayfield, Paul McNamee, Douglas W Oard, Luca Soldaini, and Eugene Yang. Overview of the trec 2023 neuclir track. 2024.
Yibin Lei, Tao Shen, Yu Cao, and Andrew Yates. Enhancing lexicon-based text embeddings with large language models. In Proc. of ACL (Volume 1: Long Papers), 2025.
Chaofan Li, Minghao Qin, Shitao Xiao, Jianlyu Chen, Kun Luo, Defu Lian, Yingxia Shao, and Zheng Liu. Making text embedders few-shot learners. In Proc. of ICLR.
Jimmy Lin and Xueguang Ma. A few brief notes on deepimpact, coil, and a conceptual framework for information retrieval techniques. arXiv:2106.14807, 2021.
Shayne Longpre, Yi Lu, and Joachim Daiber. MKQA: A linguistically diverse benchmark for multilingual open domain question answering. Trans. of ACL, 9, 2021.
Antoine Louis, Vageesh Saxena, Gijs van Dijck, and Gerasimos Spanakis. ColBERT-XM: A modular multi-vector representation model for zero-shot multilingual information retrieval. arXiv:2402.15059, 2024.
Sean MacAvaney, Franco Maria Nardini, Raffaele Perego, Nicola Tonellotto, Nazli Goharian, and Ophir Frieder. Expansion via prediction of importance with contextualization. In Proc. of SIGIR, pp. 1573–1576, 2020.
Macedo Maia, Siegfried Handschuh, André Freitas, Brian Davis, Ross McDermott, Manel Zarrouk, and Alexandra Balahur. Www'18 open challenge: financial opinion mining and question answering. In In Proc. WWW, pp. 1941–1942, 2018.
Suraj Nair, Eugene Yang, Dawn Lawrie, Kevin Duh, Paul McNamee, Kenton Murray, James Mayfield, and Douglas W Oard. Transfer learning approaches for building cross-language dense retrieval models. In In Proc. of ECIR, pp. 382–396. Springer, 2022a.
Suraj Nair, Eugene Yang, Dawn J Lawrie, James Mayfield, and Douglas W Oard. Learning a sparse representation model for neural clir. In DESIRES, pp. 53–64, 2022b.
Suraj Nair, Eugene Yang, Dawn Lawrie, James Mayfield, and Douglas W Oard. Blade: combining vocabulary pruning and intermediate pretraining for scalable neural clir. In Proc. of SIGIR, pp. 1219–1229, 2023.
Franco Maria Nardini, Thong Nguyen, Cosimo Rulli, Rossano Venturini, and Andrew Yates. Effective inference-free retrieval for learned sparse representations. In Proc. of SIGIR, pp. 2936–2940, 2025.
Thong Nguyen, Sean MacAvaney, and Andrew Yates. A unified framework for learned sparse retrieval. In In Proc. of ECIR, pp. 101–116. Springer, 2023.
Thong Nguyen, Mariya Hendriksen, Andrew Yates, and Maarten de Rijke. Multimodal learned sparse retrieval with probabilistic expansion control. In In Proc. of ECIR, pp. 448–464. Springer, 2024.
Tri Nguyen, Mir Rosenberg, Xia Song, Jianfeng Gao, Saurabh Tiwary, Rangan Majumder, and Li Deng. Ms marco: A human-generated machine reading comprehension dataset. arXiv:1611.09268, 2016.
Aaron van den Oord, Yazhe Li, and Oriol Vinyals. Representation learning with contrastive predictive coding. arXiv:1807.03748, 2018.
Pranav Rajpurkar, Jian Zhang, Konstantin Lopyrev, and Percy Liang. Squad: 100,000+ questions for machine comprehension of text. In Proc. of EMNLP, pp. 2383–2392, 2016.
Nils Reimers and Iryna Gurevych. Sentence-bert: Sentence embeddings using siamese bert-networks. In Proc. of EMNLP-IJCNLP, pp. 3982–3992, 2019.
Nils Reimers and Iryna Gurevych. Making monolingual sentence embeddings multilingual using knowledge distillation. In Proc. of EMNLP (EMNLP), pp. 4512–4525, 2020.
Parker Riley, Isaac Caswell, Markus Freitag, and David Grangier. Translationese as a language in “multilingual” NMT. In Proc. of ACL, 2020.
Lakshay Sharma, Laura Graesser, Nikita Nangia, and Utku Evci. Natural language understanding with the quora question pairs dataset. arXiv:1907.01041, 2019.
Xinjie Shen, Zhichao Geng, and Yang Yang. Exploring 10 sparsification for inference-free sparse retrievers. In Proc. of SIGIR, pp. 2572–2576, 2025.
Nandan Thakur, Nils Reimers, Andreas Rücklé, Abhishek Srivastava, and Iryna Gurevych. BEIR: A heterogeneous benchmark for zero-shot evaluation of information retrieval models. In Proc. of NeurIPS, 2021.
James Thorne, Andreas Vlachos, Christos Christodoulopoulos, and Arpit Mittal. FEVER: a large-scale dataset for fact extraction and VERification. In Proc. of NAACL-HLT (Volume 1: Long Papers), 2018.
Henning Wachsmuth, Shahbaz Syed, and Benno Stein. Retrieval of the best counterargument without prior topic knowledge. In Proc. of ACL (Volume 1: Long Papers), pp. 241–251, 2018.
Liang Wang, Nan Yang, Xiaolong Huang, Linjun Yang, Rangan Majumder, and Furu Wei. Improving text embeddings with large language models. arXiv:2401.00368, 2023.
Liang Wang, Nan Yang, Xiaolong Huang, Linjun Yang, Rangan Majumder, and Furu Wei. Multilingual e5 text embeddings: A technical report. arXiv:2402.05672, 2024.
Orion Weller, Michael Boratko, Iftekhar Naim, and Jinhyuk Lee. On the theoretical limitations of embedding-based retrieval. arXiv:2508.21038, 2025.
Tiansheng Wen, Yifei Wang, Zequn Zeng, Zhong Peng, Yudi Su, Xinyang Liu, Bo Chen, Hongwei Liu, Stefanie Jegelka, and Chenyu You. Beyond matryoshka: Revisiting sparse coding for adaptive representation. arXiv:2503.01776, 2025.
Thomas Wolf, Lysandre Debut, Victor Sanh, Julien Chaumond, Clement Delangue, Anthony Moi, Pierric Cistac, Tim Rault, Rémi Louf, Morgan Funtowicz, et al. Huggingface's transformers: State-of-the-art natural language processing. arXiv:1910.03771, 2019.
Xiaohui Xie, Qian Dong, Bingning Wang, Feiyang Lv, Ting Yao, Weinan Gan, Zhijing Wu, Xiangsheng Li, Haitao Li, Yiqun Liu, et al. T2ranking: A large-scale chinese benchmark for passage ranking. In Proc. of SIGIR, pp. 2681–2690, 2023.
Eugene Yang, Suraj Nair, Ramraj Chandradevan, Rebecca Iglesias-Flores, and Douglas W Oard. C3: Continued pretraining with contrastive weak supervision for cross language ad-hoc retrieval. In Proc. of SIGIR, pp. 2507–2512, 2022.
Eugene Yang, Dawn Lawrie, and James Mayfield. Distillation for multilingual information retrieval. In Proc. of SIGIR, pp. 2368–2373, 2024a.
Eugene Yang, Dawn Lawrie, James Mayfield, Douglas W. Oard, and Scott Miller. Translate-distill: Learning cross-language dense retrieval by translation and distillation. In Proc. of ECIR, 2024b.
Zhilin Yang, Peng Qi, Saizheng Zhang, Yoshua Bengio, William Cohen, Ruslan Salakhutdinov, and Christopher D Manning. Hotpotqa: A dataset for diverse, explainable multi-hop question answering. In Proc. of EMNLP, pp. 2369–2380, 2018.
Hamed Zamani, Mostafa Dehghani, W Bruce Croft, Erik Learned-Miller, and Jaap Kamps. From neural re-ranking to neural ranking: Learning a sparse representation for inverted indexing. In Proc. of CIKM, pp. 497–506, 2018.
Crystina Zhang, Jing Lu, Vinh Q Tran, Tal Schuster, Donald Metzler, and Jimmy Lin. Tomato, tomahto, tomate: Do multilingual language models understand based on subword-level semantic concepts? In Proc. of NAACL (Findings), a.
Xinyu Zhang, Nandan Thakur, Odunayo Ogundepo, Ehsan Kamalloo, David Alfonso-Hermelo, Xiaoguang Li, Qun Liu, Mehdi Rezagholizadeh, and Jimmy Lin. MIRACL: A multilingual retrieval dataset covering 18 diverse languages. Trans. Assoc. Comput. Linguist., b.
Xinyu Zhang, Xueguang Ma, Peng Shi, and Jimmy Lin. Mr. tydi: A multi-lingual benchmark for dense retrieval. arXiv:2108.08787, 2021.
Xinyu Zhang, Kelechi Ogueji, Xueguang Ma, and Jimmy Lin. Toward Best Practices for Training Multilingual Dense Retrieval Models. ACM Trans. Inf. Syst., 42(2):1–33, 2024.
Yanzhao Zhang, Mingxin Li, Dingkun Long, Xin Zhang, Huan Lin, Baosong Yang, Pengjun Xie, An Yang, Dayiheng Liu, Junyang Lin, et al. Qwen3 embedding: Advancing text embedding and reranking through foundation models. arXiv:2506.05176, 2025.

#

[page 16]

A APPENDIX

# A.1 DEMONSTRATION EXAMPLES

In Figure 6, we present a list of demonstration examples. The inputs are in different languages, while the outputs are bag-of-words English tokens produced by our ① MILCO (SAP, SCT $_{KD}$ , LexEcho) model. These examples illustrate that MILCO generates transparent representations, making it possible for humans to interpret, inspect, and trace potential errors or biases.

<table><tr><td>ID</td><td>Language</td><td>Input Text</td><td>Sparse Representation (English View)</td></tr><tr><td>1</td><td>en</td><td>what is tesla net worth?</td><td>{&quot;tesla&quot;: 3.4, &quot;worth&quot;: 2.72, &quot;net&quot;: 1.7, &quot;price&quot;: 1.65, &quot;salary&quot;: 0.8, &quot;nikola&quot;: 0.78, &quot;stock&quot;: 0.58, &quot;electric&quot;: 0.52, &quot;car&quot;: 0.49, &quot;generation&quot;: 0.49, &quot;money&quot;: 0.48, &quot;levi&quot;: 0.42, &quot;mining&quot;: 0.31, &quot;company&quot;: 0.27, &quot;sale&quot;: 0.2, &quot;milan&quot;: 0.12, &quot;edmund&quot;: 0.12, &quot;revenue&quot;: 0.06}</td></tr><tr><td>1</td><td>hi</td><td>টেস্লা কী কুল সংপত্তি ক্যা है?</td><td>{&quot;tesla&quot;: 3.35, &quot;worth&quot;: 2.79, &quot;net&quot;: 1.73, &quot;price&quot;: 1.56, &quot;salary&quot;: 1.03, &quot;money&quot;: 0.78, &quot;generation&quot;: 0.51, &quot;stock&quot;: 0.5, &quot;nikola&quot;: 0.49, &quot;electric&quot;: 0.4, &quot;car&quot;: 0.31, &quot;company&quot;: 0.29, &quot;mining&quot;: 0.29, &quot;levi&quot;: 0.25, &quot;wealth&quot;: 0.17, &quot;total&quot;: 0.16, &quot;sale&quot;: 0.11, &quot;milan&quot;: 0.1}</td></tr><tr><td>1</td><td>zh</td><td>特斯拉的净资产是多少?</td><td>{&quot;tesla&quot;: 3.35, &quot;worth&quot;: 2.71, &quot;price&quot;: 1.91, &quot;net&quot;: 1.76, &quot;salary&quot;: 1.35, &quot;money&quot;: 0.95, &quot;stock&quot;: 0.79, &quot;company&quot;: 0.58, &quot;electric&quot;: 0.54, &quot;nikola&quot;: 0.54, &quot;generation&quot;: 0.49, &quot;car&quot;: 0.34, &quot;mining&quot;: 0.32, &quot;levi&quot;: 0.19, &quot;motors&quot;: 0.15, &quot;total&quot;: 0.03}</td></tr><tr><td>1</td><td>de</td><td>Was ist Teslas Nettowert?</td><td>{&quot;tesla&quot;: 3.34, &quot;worth&quot;: 2.69, &quot;net&quot;: 1.94, &quot;price&quot;: 1.51, &quot;stock&quot;: 0.78, &quot;salary&quot;: 0.68, &quot;money&quot;: 0.62, &quot;electric&quot;: 0.48, &quot;nikola&quot;: 0.46, &quot;generation&quot;: 0.43, &quot;sale&quot;: 0.34, &quot;car&quot;: 0.25, &quot;levi&quot;: 0.22, &quot;company&quot;: 0.19, &quot;mining&quot;: 0.16, &quot;milan&quot;: 0.11, &quot;wealth&quot;: 0.11, &quot;edmund&quot;: 0.11, &quot;currently&quot;: 0.1, &quot;revenue&quot;: 0.1}</td></tr><tr><td>1</td><td>nl</td><td>Wat is de nettowaarde van Tesla?</td><td>{&quot;tesla&quot;: 3.36, &quot;worth&quot;: 2.75, &quot;net&quot;: 1.89, &quot;price&quot;: 1.66, &quot;salary&quot;: 0.99, &quot;stock&quot;: 0.87, &quot;money&quot;: 0.61, &quot;electric&quot;: 0.55, &quot;nikola&quot;: 0.49, &quot;company&quot;: 0.41, &quot;generation&quot;: 0.41, &quot;sale&quot;: 0.32, &quot;levi&quot;: 0.27, &quot;mining&quot;: 0.23, &quot;car&quot;: 0.22, &quot;revenue&quot;: 0.15, &quot;edmund&quot;: 0.12, &quot;currently&quot;: 0.11, &quot;wealth&quot;: 0.08, &quot;investment&quot;: 0.06}</td></tr><tr><td>1</td><td>ar</td><td>ما هي القيمة الصافية لشركة تيسلا؟</td><td>{&quot;tesla&quot;: 3.31, &quot;worth&quot;: 2.64, &quot;net&quot;: 1.81, &quot;price&quot;: 1.52, &quot;salary&quot;: 0.85, &quot;stock&quot;: 0.82, &quot;money&quot;: 0.58, &quot;company&quot;: 0.53, &quot;electric&quot;: 0.43, &quot;levi&quot;: 0.43, &quot;generation&quot;: 0.42, &quot;nikola&quot;: 0.28, &quot;mining&quot;: 0.26, &quot;revenue&quot;: 0.22, &quot;sale&quot;: 0.18, &quot;car&quot;: 0.16, &quot;total&quot;: 0.1, &quot;investment&quot;: 0.08, &quot;currently&quot;: 0.03, &quot;wealth&quot;: 0.03}</td></tr><tr><td>1</td><td>vi</td><td>Giá trị tài sản ròng của Tesla là bao nhiêu?</td><td>{&quot;tesla&quot;: 3.36, &quot;worth&quot;: 2.61, &quot;price&quot;: 1.84, &quot;net&quot;: 1.52, &quot;salary&quot;: 1.14, &quot;money&quot;: 0.8, &quot;stock&quot;: 0.7, &quot;electric&quot;: 0.52, &quot;nikola&quot;: 0.45, &quot;mining&quot;: 0.35, &quot;generation&quot;: 0.33, &quot;sale&quot;: 0.27, &quot;company&quot;: 0.25, &quot;milan&quot;: 0.21, &quot;car&quot;: 0.16, &quot;wealth&quot;: 0.16, &quot;investment&quot;: 0.14, &quot;levi&quot;: 0.09, &quot;revenue&quot;: 0.08, &quot;total&quot;: 0.05}</td></tr><tr><td>2</td><td>en</td><td>Baltimore Maryland the greatest city in America</td><td>{&quot;baltimore&quot;: 2.47, &quot;maryland&quot;: 2.07, &quot;greatest&quot;: 1.68, &quot;city&quot;: 1.59, &quot;biggest&quot;: 1.38, &quot;md&quot;: 1.26, &quot;america&quot;: 1.11, &quot;usa&quot;: 1.09, &quot;great&quot;: 0.98, &quot;cities&quot;: 0.93, &quot;town&quot;: 0.7, &quot;american&quot;: 0.47, &quot;us&quot;: 0.45, &quot;urban&quot;: 0.41, &quot;birthplace&quot;: 0.41, &quot;was&quot;: 0.34, &quot;famous&quot;: 0.29, &quot;garrison&quot;: 0.25, &quot;beautiful&quot;: 0.23, &quot;geography&quot;: 0.21}</td></tr><tr><td>2</td><td>hi</td><td>বাল্টীমোর মেরীলেড অমেরিকা কা সবসে বড়া শহর</td><td>{&quot;baltimore&quot;: 2.63, &quot;maryland&quot;: 2.08, &quot;largest&quot;: 1.7, &quot;city&quot;: 1.55, &quot;biggest&quot;: 1.5, &quot;md&quot;: 1.49, &quot;usa&quot;: 1.14, &quot;cities&quot;: 1.06, &quot;us&quot;: 0.78, &quot;town&quot;: 0.65, &quot;america&quot;: 0.65, &quot;population&quot;: 0.64, &quot;urban&quot;: 0.48, &quot;metropolitan&quot;: 0.34, &quot;census&quot;: 0.31, &quot;garrison&quot;: 0.3, &quot;geography&quot;: 0.29, &quot;size&quot;: 0.26, &quot;headquarters&quot;: 0.26, &quot;big&quot;: 0.19}</td></tr><tr><td>2</td><td>zh</td><td>马里兰州巴尔的摩是美国最伟大的城市</td><td>{&quot;baltimore&quot;: 2.66, &quot;maryland&quot;: 2.07, &quot;greatest&quot;: 1.85, &quot;city&quot;: 1.73, &quot;md&quot;: 1.65, &quot;biggest&quot;: 1.53, &quot;usa&quot;: 1.38, &quot;great&quot;: 1.29, &quot;cities&quot;: 1.26, &quot;us&quot;: 1.02, &quot;america&quot;: 0.91, &quot;town&quot;: 0.81, &quot;best&quot;: 0.66, &quot;urban&quot;: 0.61, &quot;geography&quot;: 0.57, &quot;birthplace&quot;: 0.57, &quot;beautiful&quot;: 0.55, &quot;garrison&quot;: 0.51, &quot;headquarters&quot;: 0.47, &quot;location&quot;: 0.46}</td></tr><tr><td>2</td><td>de</td><td>Baltimore Maryland die großartigste Stadt in Amerika</td><td>{&quot;baltimore&quot;: 2.22, &quot;maryland&quot;: 1.86, &quot;city&quot;: 1.4, &quot;greatest&quot;: 1.25, &quot;md&quot;: 1.16, &quot;biggest&quot;: 0.98, &quot;great&quot;: 0.96, &quot;cities&quot;: 0.95, &quot;usa&quot;: 0.94, &quot;america&quot;: 0.91, &quot;town&quot;: 0.69, &quot;beautiful&quot;: 0.57, &quot;most&quot;: 0.52, &quot;american&quot;: 0.49, &quot;us&quot;: 0.46, &quot;urban&quot;: 0.43, &quot;best&quot;: 0.37, &quot;garrison&quot;: 0.35, &quot;geography&quot;: 0.31, &quot;birthplace&quot;: 0.29}</td></tr><tr><td>2</td><td>nl</td><td>Baltimore Maryland de beste stad in Amerika</td><td>{&quot;baltimore&quot;: 2.35, &quot;maryland&quot;: 2.0, &quot;best&quot;: 1.94, &quot;city&quot;: 1.51, &quot;md&quot;: 1.27, &quot;usa&quot;: 1.17, &quot;america&quot;: 1.11, &quot;beautiful&quot;: 1.05, &quot;cities&quot;: 1.02, &quot;biggest&quot;: 0.89, &quot;town&quot;: 0.77, &quot;american&quot;: 0.61, &quot;us&quot;: 0.54, &quot;urban&quot;: 0.49, &quot;birthplace&quot;: 0.37, &quot;garrison&quot;: 0.35, &quot;popular&quot;: 0.3, &quot;tourism&quot;: 0.29, &quot;location&quot;: 0.28, &quot;headquarters&quot;: 0.27}</td></tr><tr><td>2</td><td>ar</td><td>bal“Theymorer ماريلاد agópm مديئة في أmerika</td><td>{&quot;baltimore&quot;: 2.57, &quot;maryland&quot;: 2.09, &quot;city&quot;: 1.63, &quot;greatest&quot;: 1.55, &quot;md&quot;: 1.53, &quot;biggest&quot;: 1.36, &quot;great&quot;: 1.24, &quot;usa&quot;: 1.21, &quot;cities&quot;: 1.15, &quot;america&quot;: 1.14, &quot;town&quot;: 0.72, &quot;garrison&quot;: 0.66, &quot;us&quot;: 0.61, &quot;location&quot;: 0.57, &quot;urban&quot;: 0.57, &quot;headquarters&quot;: 0.53, &quot;american&quot;: 0.52, &quot;best&quot;: 0.47, &quot;beautiful&quot;: 0.43, &quot;birthplace&quot;: 0.42}</td></tr><tr><td>2</td><td>vi</td><td>Baltimore Maryland thành phố vĩ đại nhất ở Mỹ</td><td>{&quot;baltimore&quot;: 2.45, &quot;maryland&quot;: 2.05, &quot;city&quot;: 1.47, &quot;biggest&quot;: 1.38, &quot;md&quot;: 1.28, &quot;greatest&quot;: 1.08, &quot;usa&quot;: 1.05, &quot;cities&quot;: 0.95, &quot;largest&quot;: 0.92, &quot;us&quot;: 0.71, &quot;america&quot;: 0.69, &quot;town&quot;: 0.65, &quot;great&quot;: 0.47, &quot;urban&quot;: 0.42, &quot;headquarters&quot;: 0.34, &quot;metropolitan&quot;: 0.3, &quot;garrison&quot;: 0.29, &quot;population&quot;: 0.27, &quot;metropolis&quot;: 0.22, &quot;american&quot;: 0.21}</td></tr><tr><td>3</td><td>zh</td><td>有谁知道陌陌直播的音乐怎么导入手机里</td><td>{&quot;import&quot;: 1.6, &quot;music&quot;: 1.46, &quot;live&quot;: 1.17, &quot;phone&quot;: 1.16, &quot;imported&quot;: 0.95, &quot;songs&quot;: 0.86, &quot;app&quot;: 0.84, &quot;step&quot;: 0.71, &quot;youtube&quot;: 0.68, &quot;phones&quot;: 0.65, &quot;stream&quot;: 0.63, &quot;no&quot;: 0.62, &quot;button&quot;: 0.62, &quot;download&quot;: 0.58, &quot;song&quot;: 0.48, &quot;pandora&quot;: 0.48, &quot;mp3&quot;: 0.47, &quot;player&quot;: 0.46, &quot;sync&quot;: 0.46, &quot;transfer&quot;: 0.45}</td></tr><tr><td>4</td><td>de</td><td>Alan Smithee is a pseudonym for a fictional director responsible for films in which the actual director does not want his name associated with the work. From 1968 to 2000, it was recommended by the Directors Guild of America (DGA) for such situations.</td><td>{&quot;alan&quot;: 3.02, &quot;#####&quot;: 3.0, &quot;smith&quot;: 2.95, &quot;pseudonym&quot;: 2.15, &quot;director&quot;: 2.05, &quot;directors&quot;: 1.93, &quot;fictional&quot;: 1.9, &quot;##ga&quot;: 1.86, &quot;guild&quot;: 1.85, &quot;responsible&quot;: 1.61, &quot;d&quot;: 1.58, &quot;who&quot;: 1.49, &quot;film&quot;: 1.34, &quot;alias&quot;: 1.29, &quot;directed&quot;: 1.26, &quot;##ees&quot;: 1.2, &quot;actual&quot;: 1.09, &quot;1968&quot;: 1.07, &quot;recommended&quot;: 1.05, &quot;directing&quot;: 1.04}</td></tr><tr><td>5</td><td>fr</td><td>Paul Jules Antoine Meillet, né le à Moulins (Allier) et mort le à Châteaumeillant (Cher), est le principal linguiste français des premières décennies du . Il est aussi philologue.</td><td>{&quot;mei&quot;: 2.9, &quot;##let&quot;: 2.73, &quot;jules&quot;: 2.62, &quot;paul&quot;: 2.57, &quot;antoine&quot;: 2.46, &quot;##ulin&quot;: 2.41, &quot;allie&quot;: 2.3, &quot;linguist&quot;: 2.21, &quot;french&quot;: 2.08, &quot;cher&quot;: 2.04, &quot;chateau&quot;: 1.84, &quot;france&quot;: 1.77, &quot;##mei&quot;: 1.72, &quot;mo&quot;: 1.7, &quot;who&quot;: 1.69, &quot;linguistics&quot;: 1.66, &quot;##llan&quot;: 1.6, &quot;born&quot;: 1.51, &quot;died&quot;: 1.39, &quot;##let&quot;: 1.34}</td></tr><tr><td>6</td><td>zh</td><td>金章宗完颜璟 女真名麻達葛, 金朝第6位皇帝(1189年1月20日—1208年12月29日在位),在位19年,享年41岁。章宗為金世宗完顏雍之嫡孙,其在位期間修訂國內律法,政治清明,史稱明昌之治,章宗統治下的金朝文化發展達至頂峰,但同時軍事能力卻也日益低下,蒙古帝國也於同時崛起</td><td>{&quot;dynasty&quot;: 2.19, &quot;emperor&quot;: 2.03, &quot;qing&quot;: 2.01, &quot;ming&quot;: 1.96, &quot;sima&quot;: 1.8, &quot;kim&quot;: 1.69, &quot;sixth&quot;: 1.67, &quot;mongolian&quot;: 1.64, &quot;6&quot;: 1.61, &quot;khan&quot;: 1.54, &quot;korea&quot;: 1.45, &quot;age&quot;: 1.44, ##chang&quot;: 1.44, &quot;dynasties&quot;: 1.42, &quot;date&quot;: 1.36, &quot;who&quot;: 1.33, &quot;died&quot;: 1.32, &quot;china&quot;: 1.31, &quot;reign&quot;: 1.31, &quot;empire&quot;: 1.3}</td></tr></table>

Figure 6: Examples of MILCO's output representations (English view) on different languages.

#

[page 17]

A.2 DETAILED MULTILINGUAL/CROSS-LINGUAL RETRIEVAL RESULTS

In this section, we show the detailed language-specific results of MILCO and baselines in the following multilingual and cross-lingual retrieval datasets. The result on Multilingual Long Document Retrieval (MLDR) is shown in Table 6. The result on MTEBv2 (multilingual and cross-lingual tasks) is shown in Table 7. The result on the NeuCLIR benchmark (cross-lingual retrieval) is shown in Table 8. The result on MKQA (cross-lingual retrieval) is shown in Table 9.

Table 6: Multilingual (long) document retrieval on the MLDR (measured by nDCG@10).

<table><tr><td>Model</td><td>Max Length</td><td>Avg</td><td>ar</td><td>de</td><td>en</td><td>es</td><td>fr</td><td>hi</td><td>it</td><td>ja</td><td>ko</td><td>pt</td><td>ru</td><td>th</td><td>zh</td></tr><tr><td colspan="16">Dense and multi-vector baselines</td></tr><tr><td>mE5large</td><td>512</td><td>34.2</td><td>33.0</td><td>26.9</td><td>33.0</td><td>51.1</td><td>49.5</td><td>21.0</td><td>43.1</td><td>29.9</td><td>27.1</td><td>58.7</td><td>42.4</td><td>15.9</td><td>13.2</td></tr><tr><td>E5mistral-7b</td><td>8192</td><td>42.6</td><td>29.6</td><td>40.6</td><td>43.3</td><td>70.2</td><td>60.5</td><td>23.2</td><td>55.3</td><td>41.6</td><td>32.7</td><td>69.5</td><td>52.4</td><td>18.2</td><td>16.8</td></tr><tr><td>M3-Dense</td><td>8192</td><td>52.5</td><td>47.6</td><td>46.1</td><td>48.9</td><td>74.8</td><td>73.8</td><td>40.7</td><td>62.7</td><td>50.9</td><td>42.9</td><td>74.4</td><td>59.5</td><td>33.6</td><td>26.0</td></tr><tr><td>M3-Multi-vector</td><td>8192</td><td>57.6</td><td>56.6</td><td>50.4</td><td>55.8</td><td>79.5</td><td>77.2</td><td>46.6</td><td>66.6</td><td>52.8</td><td>48.8</td><td>77.5</td><td>64.2</td><td>39.4</td><td>32.7</td></tr><tr><td>M3-Dense+Sparse</td><td>8192</td><td>64.8</td><td>63.0</td><td>56.4</td><td>64.2</td><td>88.7</td><td>84.2</td><td>52.3</td><td>75.8</td><td>58.5</td><td>53.1</td><td>86.0</td><td>75.6</td><td>42.9</td><td>42.0</td></tr><tr><td>M3-All</td><td>8192</td><td>65.0</td><td>64.7</td><td>57.9</td><td>63.8</td><td>86.8</td><td>83.9</td><td>52.2</td><td>75.5</td><td>60.1</td><td>55.7</td><td>85.4</td><td>73.8</td><td>44.7</td><td>40.0</td></tr><tr><td>PLAID-X (Multi-vector)</td><td>512</td><td>74.2</td><td>78.5</td><td>65.5</td><td>81.4</td><td>90.9</td><td>87.5</td><td>64.0</td><td>84.2</td><td>67.3</td><td>66.9</td><td>85.5</td><td>86.9</td><td>43.7</td><td>62.7</td></tr><tr><td>Qwen3-Embed - 0.6B</td><td>32768</td><td>50.1</td><td>44.7</td><td>45.0</td><td>75.5</td><td>48.4</td><td>69.7</td><td>24.8</td><td>62.6</td><td>49.7</td><td>38.3</td><td>73.2</td><td>61.2</td><td>30.7</td><td>26.9</td></tr><tr><td>Qwen3-Embed - 8B</td><td>32678</td><td>59.1</td><td>57.7</td><td>54.5</td><td>86.1</td><td>56.1</td><td>79.5</td><td>35.1</td><td>72.7</td><td>58.3</td><td>50.4</td><td>79.6</td><td>69.6</td><td>37.9</td><td>30.8</td></tr><tr><td colspan="16">Sparse baselines</td></tr><tr><td>BM25</td><td>8192</td><td>53.6</td><td>45.1</td><td>52.6</td><td>57.0</td><td>78.0</td><td>75.7</td><td>43.7</td><td>70.9</td><td>36.2</td><td>25.7</td><td>82.6</td><td>61.3</td><td>33.6</td><td>34.6</td></tr><tr><td>M3-Sparse</td><td>8192</td><td>62.2</td><td>58.7</td><td>53.0</td><td>62.1</td><td>87.4</td><td>82.7</td><td>49.6</td><td>74.7</td><td>53.9</td><td>47.9</td><td>85.2</td><td>72.9</td><td>40.3</td><td>40.5</td></tr><tr><td>1MILCO (SAP, SCTKD, LexEcho)</td><td>512</td><td>74.4</td><td>75.3</td><td>66.1</td><td>82.5</td><td>93.2</td><td>90.8</td><td>59.5</td><td>81.9</td><td>68.8</td><td>67.9</td><td>90.7</td><td>85.5</td><td>45.8</td><td>59.0</td></tr></table>

Table 7: Performance of embedding models on MTEBv2's multilingual and cross-lingual retrieval tasks (Enevoldsen et al., 2025). MILCO outperforms other models with similar sizes (e.g., Qwen3-0.6B, BGE-M3), while under-performs larger models, such as Qwen3-Embed-8B. (M = Multilingual, C = Cross-lingual). We evaluate English-only retrieval tasks separately in Section A.3.

<table><tr><td>Model</td><td>Avg.</td><td>Belebele (M)</td><td>MIRACL-HN (M)</td><td>MLQA (C)</td><td>Statcan (M)</td><td>Twitter (M)</td><td>Wiki (C)</td></tr><tr><td>gte-multilingual-base</td><td>64.72</td><td>77.60</td><td>64.17</td><td>72.19</td><td>21.74</td><td>68.92</td><td>83.69</td></tr><tr><td>bge-m3</td><td>62.02</td><td>78.16</td><td>69.59</td><td>74.81</td><td>21.86</td><td>37.82</td><td>89.87</td></tr><tr><td>granite-278m-multi</td><td>55.80</td><td>62.20</td><td>59.45</td><td>62.99</td><td>30.14</td><td>34.98</td><td>85.06</td></tr><tr><td>granite-125m-eng</td><td>26.99</td><td>33.37</td><td>16.35</td><td>22.90</td><td>30.71</td><td>5.92</td><td>52.70</td></tr><tr><td>granite-107m-multi</td><td>49.88</td><td>55.12</td><td>57.25</td><td>60.47</td><td>27.50</td><td>17.06</td><td>81.88</td></tr><tr><td>gte-Qwen2-7B-inst</td><td>67.22</td><td>77.54</td><td>51.58</td><td>78.69</td><td>37.87</td><td>68.64</td><td>88.97</td></tr><tr><td>gte-Qwen2-1.5B-inst</td><td>65.12</td><td>66.59</td><td>63.23</td><td>72.89</td><td>33.25</td><td>67.01</td><td>87.77</td></tr><tr><td>NV-Embed-v2</td><td>58.65</td><td>69.79</td><td>55.54</td><td>70.61</td><td>19.55</td><td>45.57</td><td>90.83</td></tr><tr><td>inf-retriever-v1</td><td>71.21</td><td>77.37</td><td>60.93</td><td>80.31</td><td>37.30</td><td>79.30</td><td>92.02</td></tr><tr><td>jina-embeddings-v4</td><td>73.84</td><td>74.29</td><td>62.95</td><td>74.90</td><td>58.07</td><td>84.38</td><td>88.46</td></tr><tr><td>inf-retriever-v1-1.5b</td><td>65.34</td><td>66.06</td><td>62.35</td><td>72.93</td><td>31.31</td><td>70.46</td><td>88.93</td></tr><tr><td>Qwen3-Embed-0.6B</td><td>63.93</td><td>68.74</td><td>61.23</td><td>72.79</td><td>33.63</td><td>60.04</td><td>87.13</td></tr><tr><td>Qwen3-Embed-8B</td><td>75.59</td><td>88.81</td><td>70.58</td><td>83.55</td><td>40.46</td><td>78.20</td><td>91.96</td></tr><tr><td>1 MILCO (SAP, SCTKD, LexEcho)</td><td>66.83</td><td>80.72</td><td>72.65</td><td>83.00</td><td>24.00</td><td>50.00</td><td>90.63</td></tr></table>

Table 8: Results on NeuCLIR cross-lingual benchmarks (Lawrie et al., 2024) on three languages (Chinese, Persian, and Russian). The Avg. MLIR score (nDCG@20) is the mean across the two years. Our 560M MILCO model outperforms Qwen3 0.6B, but falls behind PLAID-X and Qwen3-Embed 4B/8B. PLAID-X focuses exclusively on the test languages.

<table><tr><td>Model</td><td>2023 MLIR (C)</td><td>2024 MLIR (C)</td><td>Avg. MLIR (C)</td></tr><tr><td>SPLADE v3 (transl. docs)</td><td>0.420</td><td>0.440</td><td>0.430</td></tr><tr><td>PLAID-X</td><td>0.404</td><td>0.468</td><td>0.436</td></tr><tr><td>Qwen3-Embed 0.6B</td><td>0.317</td><td>0.311</td><td>0.314</td></tr><tr><td>Qwen3-Embed 4B</td><td>0.440</td><td>0.415</td><td>0.428</td></tr><tr><td>Qwen3-Embed 8B</td><td>0.434</td><td>0.419</td><td>0.427</td></tr><tr><td>1 MILCO (SAP, SCT $_{KD}$ , LexEcho)</td><td>0.395</td><td>0.427</td><td>0.411</td></tr></table>

Table 9: Cross-lingual retrieval performance on MKQA (Recall@100). Abbreviations: mCtr = mContriever, OA3 = OpenAI-3, PLD = PLAID-X, Q0.6 = Qwen3-0.6B, Q8 = Qwen3-8B.

<table><tr><td rowspan="2">Lang</td><td colspan="12">Dense Baselines</td><td colspan="2">Sparse Baselines</td><td rowspan="2">MILCO</td></tr><tr><td>mDPR</td><td>mCtr</td><td>E5-L</td><td>E5-M7B</td><td>OA3</td><td>M3-D</td><td>M3-MV</td><td>M3-DS</td><td>M3-All</td><td>PLD</td><td>Q0.6</td><td>Q8</td><td>BM25</td><td>M3-S</td></tr><tr><td>ar</td><td>48.2</td><td>58.2</td><td>68.7</td><td>59.6</td><td>65.6</td><td>71.1</td><td>71.4</td><td>71.1</td><td>71.5</td><td>64.2</td><td>44.8</td><td>64.75</td><td>18.9</td><td>23.5</td><td>74.9</td></tr><tr><td>da</td><td>67.4</td><td>73.9</td><td>77.4</td><td>77.8</td><td>73.6</td><td>77.2</td><td>77.5</td><td>77.4</td><td>77.6</td><td>77.0</td><td>57.9</td><td>69.89</td><td>49.3</td><td>55.4</td><td>77.9</td></tr><tr><td>de</td><td>65.8</td><td>71.7</td><td>76.9</td><td>77.0</td><td>73.6</td><td>76.2</td><td>76.3</td><td>76.4</td><td>76.3</td><td>76.0</td><td>61.6</td><td>69.69</td><td>35.4</td><td>43.3</td><td>76.6</td></tr><tr><td>es</td><td>66.8</td><td>72.6</td><td>76.6</td><td>77.4</td><td>73.9</td><td>76.4</td><td>76.6</td><td>76.7</td><td>76.9</td><td>75.7</td><td>62.5</td><td>70.75</td><td>43.4</td><td>50.6</td><td>77.7</td></tr><tr><td>fi</td><td>56.2</td><td>70.2</td><td>74.0</td><td>72.0</td><td>72.7</td><td>75.1</td><td>75.3</td><td>75.7</td><td>75.6</td><td>70.5</td><td>46.5</td><td>65.06</td><td>46.3</td><td>51.1</td><td>76.6</td></tr><tr><td>fr</td><td>68.2</td><td>73.8</td><td>76.5</td><td>77.0</td><td>76.2</td><td>76.2</td><td>76.4</td><td>76.6</td><td>76.6</td><td>76.1</td><td>61.8</td><td>70.22</td><td>45.3</td><td>53.9</td><td>77.4</td></tr><tr><td>he</td><td>49.7</td><td>63.2</td><td>69.0</td><td>67.2</td><td>58.1</td><td>72.4</td><td>72.9</td><td>72.5</td><td>73.0</td><td>70.5</td><td>39.0</td><td>62.68</td><td>26.9</td><td>31.1</td><td>74.8</td></tr><tr><td>hu</td><td>60.4</td><td>69.7</td><td>74.7</td><td>75.0</td><td>71.2</td><td>74.7</td><td>74.6</td><td>74.9</td><td>75.0</td><td>72.2</td><td>43.7</td><td>65.07</td><td>38.2</td><td>44.6</td><td>75.8</td></tr><tr><td>it</td><td>66.0</td><td>72.3</td><td>76.8</td><td>77.1</td><td>73.6</td><td>76.0</td><td>76.4</td><td>76.3</td><td>76.5</td><td>75.2</td><td>61.3</td><td>69.98</td><td>45.2</td><td>52.5</td><td>77.5</td></tr><tr><td>ja</td><td>60.3</td><td>64.8</td><td>71.5</td><td>65.1</td><td>71.9</td><td>75.0</td><td>75.1</td><td>75.0</td><td>75.2</td><td>75.2</td><td>57.2</td><td>69.45</td><td>24.5</td><td>31.3</td><td>77.2</td></tr><tr><td>km</td><td>29.5</td><td>26.8</td><td>33.4</td><td>34.3</td><td>33.9</td><td>68.6</td><td>69.1</td><td>68.8</td><td>69.2</td><td>63.7</td><td>24.6</td><td>52.76</td><td>20.6</td><td>30.1</td><td>70.4</td></tr><tr><td>ko</td><td>50.9</td><td>59.7</td><td>68.1</td><td>59.4</td><td>73.3</td><td>71.6</td><td>71.7</td><td>71.6</td><td>71.8</td><td>70.7</td><td>47.2</td><td>65.51</td><td>27.9</td><td>31.4</td><td>73.9</td></tr><tr><td>ms</td><td>65.5</td><td>74.1</td><td>76.3</td><td>77.0</td><td>73.3</td><td>77.2</td><td>77.4</td><td>77.4</td><td>77.4</td><td>75.5</td><td>59.8</td><td>70.06</td><td>55.9</td><td>62.4</td><td>78.0</td></tr><tr><td>nl</td><td>68.2</td><td>73.7</td><td>77.0</td><td>79.1</td><td>74.2</td><td>77.2</td><td>77.7</td><td>77.7</td><td>77.6</td><td>76.5</td><td>58.6</td><td>71.23</td><td>56.2</td><td>62.4</td><td>78.3</td></tr><tr><td>no</td><td>66.7</td><td>73.5</td><td>77.3</td><td>76.6</td><td>73.3</td><td>77.1</td><td>77.2</td><td>77.4</td><td>77.4</td><td>76.3</td><td>55.9</td><td>69.09</td><td>52.1</td><td>57.9</td><td>77.6</td></tr><tr><td>pl</td><td>67.0</td><td>71.5</td><td>73.0</td><td>77.1</td><td>73.3</td><td>76.3</td><td>76.5</td><td>76.3</td><td>76.4</td><td>75.1</td><td>54.7</td><td>68.86</td><td>48.0</td><td>50.5</td><td>76.9</td></tr><tr><td>pt</td><td>65.5</td><td>72.6</td><td>73.5</td><td>77.5</td><td>73.7</td><td>76.3</td><td>76.4</td><td>76.5</td><td>76.4</td><td>74.4</td><td>61.0</td><td>69.97</td><td>44.9</td><td>50.9</td><td>77.4</td></tr><tr><td>ru</td><td>62.7</td><td>69.8</td><td>76.8</td><td>75.5</td><td>72.0</td><td>76.2</td><td>76.4</td><td>76.2</td><td>76.5</td><td>76.2</td><td>58.9</td><td>69.65</td><td>33.2</td><td>36.9</td><td>77.4</td></tr><tr><td>sv</td><td>66.9</td><td>73.2</td><td>77.6</td><td>78.3</td><td>74.0</td><td>76.9</td><td>77.2</td><td>77.4</td><td>77.4</td><td>76.5</td><td>55.8</td><td>69.71</td><td>54.6</td><td>59.6</td><td>78.2</td></tr><tr><td>th</td><td>53.8</td><td>66.9</td><td>76.0</td><td>67.4</td><td>65.2</td><td>75.6</td><td>75.9</td><td>76.0</td><td>76.6</td><td>76.2</td><td>56.3</td><td>69.72</td><td>37.8</td><td>45.0</td><td>77.9</td></tr><tr><td>tr</td><td>59.1</td><td>71.1</td><td>74.3</td><td>74.9</td><td>75.2</td><td>75.6</td><td>75.9</td><td>76.0</td><td>76.0</td><td>72.0</td><td>52.1</td><td>66.57</td><td>45.8</td><td>51.8</td><td>77.6</td></tr><tr><td>vi</td><td>63.4</td><td>70.9</td><td>75.4</td><td>77.0</td><td>71.1</td><td>76.6</td><td>76.7</td><td>76.8</td><td>76.9</td><td>74.3</td><td>57.6</td><td>69.09</td><td>46.6</td><td>51.8</td><td>77.9</td></tr><tr><td>zh_cn</td><td>63.7</td><td>68.1</td><td>56.6</td><td>69.3</td><td>70.7</td><td>74.6</td><td>74.9</td><td>74.7</td><td>75.0</td><td>72.7</td><td>62.1</td><td>69.51</td><td>31.0</td><td>35.4</td><td>76.1</td></tr><tr><td>zh_hk</td><td>62.8</td><td>68.0</td><td>58.4</td><td>65.1</td><td>69.6</td><td>73.8</td><td>74.1</td><td>74.0</td><td>74.3</td><td>72.1</td><td>58.9</td><td>68.39</td><td>35.0</td><td>39.8</td><td>75.3</td></tr><tr><td>zh_tw</td><td>64.0</td><td>67.9</td><td>58.1</td><td>68.5</td><td>69.6</td><td>73.5</td><td>73.5</td><td>73.6</td><td>73.6</td><td>71.4</td><td>59.2</td><td>69.13</td><td>33.5</td><td>37.7</td><td>75.5</td></tr><tr><td>Avg</td><td>60.6</td><td>67.9</td><td>70.9</td><td>70.1</td><td>69.5</td><td>75.1</td><td>75.3</td><td>75.3</td><td>75.5</td><td>73.4</td><td>54.4</td><td>67.9</td><td>39.9</td><td>45.3</td><td>76.6</td></tr></table>

Table 10: Performance comparison on BEIR English retrieval benchmark.

<table><tr><td rowspan="2">Dataset</td><td rowspan="2">Size</td><td rowspan="2">On MTEBv2</td><td colspan="8">Large Models (≥1B params)</td><td colspan="9">Small Models (&lt;1B params)</td></tr><tr><td>Qwen3.4B</td><td>bgc-enc1</td><td>Qwen3.4B</td><td>inf-v1-1.5b</td><td>e5-large-Inst</td><td>gtc-large</td><td>LENS-dfK</td><td>inf-v1</td><td>gtc-base</td><td>bgc-large</td><td>gtc-base-v1.5</td><td>e5-large</td><td>bgc-lg-v1.5</td><td>Qwen3.0-6B</td><td>openearv-gfc</td><td>Splude-V3</td><td>MILCO</td></tr><tr><td colspan="20">Small Collections (&lt;1M documents)</td></tr><tr><td>ArguAna</td><td>8.7K</td><td>yes</td><td>76.9</td><td>83.1</td><td>75.6</td><td>81.5</td><td>58.5</td><td>57.2</td><td>77.3</td><td>84.9</td><td>57.1</td><td>62.5</td><td>63.5</td><td>54.4</td><td>64.5</td><td>71.0</td><td>52.1</td><td>50.9</td><td>61.8</td></tr><tr><td>FiQA2018</td><td>58K</td><td>yes</td><td>64.6</td><td>59.7</td><td>62.7</td><td>56.1</td><td>48.4</td><td>44.5</td><td>60.4</td><td>62.4</td><td>40.8</td><td>45.0</td><td>48.7</td><td>43.8</td><td>45.0</td><td>46.6</td><td>40.7</td><td>37.4</td><td>42.7</td></tr><tr><td>NFCorpus</td><td>3.6K</td><td>no</td><td>41.5</td><td>41.9</td><td>41.1</td><td>38.6</td><td>36.3</td><td>38.2</td><td>41.6</td><td>43.7</td><td>37.9</td><td>34.6</td><td>35.9</td><td>34.0</td><td>38.1</td><td>36.7</td><td>36.0</td><td>35.7</td><td>36.3</td></tr><tr><td>QuoraRetrieval</td><td>523K</td><td>no</td><td>88.9</td><td>91.0</td><td>88.1</td><td>89.6</td><td>89.2</td><td>88.3</td><td>90.8</td><td>90.4</td><td>88.2</td><td>89.0</td><td>88.4</td><td>89.3</td><td>89.1</td><td>87.8</td><td>87.3</td><td>81.4</td><td>88.2</td></tr><tr><td>SCIDOCS</td><td>26K</td><td>yes</td><td>32.7</td><td>25.3</td><td>31.4</td><td>26.3</td><td>19.2</td><td>23.4</td><td>27.5</td><td>30.8</td><td>23.1</td><td>22.2</td><td>21.9</td><td>17.5</td><td>22.6</td><td>24.4</td><td>16.7</td><td>15.8</td><td>16.8</td></tr><tr><td>SciFact</td><td>5.2K</td><td>no</td><td>78.5</td><td>79.1</td><td>78.3</td><td>82.8</td><td>71.6</td><td>74.3</td><td>78.4</td><td>85.4</td><td>76.2</td><td>72.4</td><td>76.8</td><td>70.2</td><td>74.6</td><td>69.7</td><td>72.5</td><td>71.0</td><td>70.1</td></tr><tr><td>TRECCOVID</td><td>171K</td><td>yes</td><td>95.0</td><td>79.1</td><td>92.9</td><td>72.4</td><td>82.5</td><td>70.2</td><td>69.7</td><td>75.1</td><td>68.8</td><td>75.4</td><td>73.1</td><td>71.2</td><td>74.7</td><td>90.5</td><td>73.3</td><td>74.8</td><td>74.0</td></tr><tr><td>Touche2020</td><td>383K</td><td>yes</td><td>35.9</td><td>30.5</td><td>35.4</td><td>21.3</td><td>27.4</td><td>25.5</td><td>25.9</td><td>24.4</td><td>22.6</td><td>26.6</td><td>25.2</td><td>23.1</td><td>24.8</td><td>33.2</td><td>39.0</td><td>29.3</td><td>28.0</td></tr><tr><td colspan="20">Large Collections (≥1M documents)</td></tr><tr><td>ClimateFEVER</td><td>5.4M</td><td>yes</td><td>47.4</td><td>45.4</td><td>47.4</td><td>41.5</td><td>29.9</td><td>28.8</td><td>44.6</td><td>41.8</td><td>28.1</td><td>38.2</td><td>40.4</td><td>25.7</td><td>36.6</td><td>42.1</td><td>31.2</td><td>23.3</td><td>30.8</td></tr><tr><td>DBPedia</td><td>4.6M</td><td>no</td><td>49.7</td><td>51.6</td><td>48.2</td><td>48.6</td><td>38.4</td><td>42.4</td><td>50.1</td><td>50.4</td><td>41.2</td><td>43.9</td><td>39.9</td><td>41.3</td><td>44.1</td><td>39.5</td><td>45.5</td><td>45.0</td><td>45.1</td></tr><tr><td>FEVER</td><td>5.4M</td><td>yes</td><td>91.9</td><td>92.8</td><td>91.6</td><td>90.9</td><td>78.0</td><td>84.5</td><td>92.4</td><td>94.2</td><td>81.5</td><td>86.7</td><td>94.8</td><td>82.8</td><td>87.2</td><td>88.2</td><td>86.1</td><td>79.6</td><td>83.4</td></tr><tr><td>HotpotQA</td><td>5.2M</td><td>yes</td><td>76.8</td><td>85.1</td><td>74.7</td><td>76.3</td><td>69.3</td><td>67.2</td><td>85.1</td><td>82.0</td><td>65.8</td><td>74.6</td><td>67.8</td><td>71.2</td><td>74.1</td><td>65.7</td><td>71.6</td><td>69.2</td><td>77.7</td></tr><tr><td>MSMARCO</td><td>8.8M</td><td>no</td><td>43.6</td><td>46.8</td><td>42.7</td><td>41.0</td><td>40.4</td><td>40.9</td><td>47.0</td><td>44.1</td><td>40.2</td><td>42.6</td><td>42.6</td><td>43.7</td><td>42.5</td><td>38.0</td><td>42.6</td><td>44.0</td><td>42.0</td></tr><tr><td>NQ</td><td>2.7M</td><td>no</td><td>65.3</td><td>73.9</td><td>63.1</td><td>64.2</td><td>57.8</td><td>54.8</td><td>73.1</td><td>69.7</td><td>52.8</td><td>53.2</td><td>53.0</td><td>64.0</td><td>55.0</td><td>53.5</td><td>58.2</td><td>58.6</td><td>64.9</td></tr><tr><td>Avg (All)</td><td></td><td></td><td>63.5</td><td>63.2</td><td>62.4</td><td>59.4</td><td>53.3</td><td>52.9</td><td>61.7</td><td>62.8</td><td>51.7</td><td>54.8</td><td>55.1</td><td>52.3</td><td>55.2</td><td>56.2</td><td>53.8</td><td>51.1</td><td>54.4</td></tr><tr><td>Avg (Large)</td><td></td><td></td><td>62.4</td><td>66.0</td><td>61.3</td><td>60.4</td><td>52.3</td><td>53.1</td><td>65.4</td><td>63.7</td><td>51.6</td><td>56.5</td><td>56.4</td><td>54.8</td><td>56.6</td><td>54.5</td><td>55.8</td><td>53.3</td><td>57.3</td></tr></table>

#

[page 18]

A.3 ENGLISH RETRIEVAL RESULTS (BEIR)

In Table 10, we report the performance of MILCO and baselines on various retrieval tasks evaluated on BEIR English benchmark (Thakur et al., 2021).

On average across BEIR benchmarks, MILCO attains 54.4, slightly behind the dense competitor Qwen3-0.6B (56.2; -1.8). This gap is expected, as Qwen3-0.6B benefits from instruction tuning, which the Qwen3 paper (Zhang et al., 2025) reports adds +1–5%, while MILCO does not use instructions. Compared to other English-only sparse baselines, MILCO is clearly stronger than Splade-V3 (+3.3) and marginally ahead of opensearch-gte (+0.6), while still trailing LENS-d4K (-7.3), a much larger sparse model. It is worth noting, however, that the comparison to Splade-V3 is not entirely fair: Splade is only trained on MSMARCO, while MILCO (and most other baselines) is trained on much larger data, including BEIR's in-domain training sets, which naturally favors transfer to the BEIR evaluation benchmark.

When focusing on the more challenging large-collection datasets ( $\geq$ 1M documents), MILCO shows its main strength. It achieves an average of 57.3, surpassing Qwen3-0.6B (54.5; +2.8), Splade-V3 (53.3; +4.0), and opensearch-gte (55.8; +1.5). MILCO's improvements are particularly pronounced on datasets such as HotpotQA (77.7 vs. 65.7; +12.0) and NQ (64.9 vs. 53.5; +11.4). Although it still falls behind LENS-d4K (65.4; -8.1), the strong performance on large collections is noteworthy because such scenarios are the most relevant to real-world search applications, where corpora often contain millions of documents.

Table 11: Performance of MILCO compared to dense baselines on the LIMIT benchmark.

<table><tr><td>Model</td><td>Dim</td><td>Recall@2</td><td>Recall@10</td><td>Recall@100</td></tr><tr><td>BM25</td><td>default</td><td>85.7</td><td>90.4</td><td>93.6</td></tr><tr><td>GTE-ModernColBERT</td><td>default</td><td>23.1</td><td>34.6</td><td>54.8</td></tr><tr><td>E5-Mistral 7B</td><td>32</td><td>0</td><td>0</td><td>0.5</td></tr><tr><td>E5-Mistral 7B</td><td>64</td><td>0</td><td>0.1</td><td>0.4</td></tr><tr><td>E5-Mistral 7B</td><td>128</td><td>0.1</td><td>0.3</td><td>1.0</td></tr><tr><td>E5-Mistral 7B</td><td>256</td><td>0.4</td><td>0.9</td><td>1.9</td></tr><tr><td>E5-Mistral 7B</td><td>512</td><td>0.7</td><td>1.3</td><td>3.8</td></tr><tr><td>E5-Mistral 7B</td><td>768</td><td>0.9</td><td>1.7</td><td>4.3</td></tr><tr><td>E5-Mistral 7B</td><td>1024</td><td>0.9</td><td>1.8</td><td>5.9</td></tr><tr><td>E5-Mistral 7B</td><td>2048</td><td>1.0</td><td>1.9</td><td>6.8</td></tr><tr><td>E5-Mistral 7B</td><td>3072</td><td>1.3</td><td>2.0</td><td>7.7</td></tr><tr><td>E5-Mistral 7B</td><td>4096</td><td>1.3</td><td>2.2</td><td>8.3</td></tr><tr><td>GritLM 7B</td><td>32</td><td>0</td><td>0</td><td>0.8</td></tr><tr><td>GritLM 7B</td><td>64</td><td>0</td><td>0.1</td><td>0.3</td></tr><tr><td>GritLM 7B</td><td>128</td><td>0.1</td><td>0.3</td><td>1.3</td></tr><tr><td>GritLM 7B</td><td>256</td><td>0.1</td><td>0.4</td><td>2.8</td></tr><tr><td>GritLM 7B</td><td>512</td><td>0.6</td><td>1.8</td><td>6.5</td></tr><tr><td>GritLM 7B</td><td>768</td><td>1.5</td><td>3.1</td><td>8.7</td></tr><tr><td>GritLM 7B</td><td>1024</td><td>1.8</td><td>3.5</td><td>10.6</td></tr><tr><td>GritLM 7B</td><td>2048</td><td>2.3</td><td>4.3</td><td>11.8</td></tr><tr><td>GritLM 7B</td><td>3072</td><td>2.0</td><td>4.3</td><td>12.9</td></tr><tr><td>GritLM 7B</td><td>4096</td><td>2.4</td><td>4.1</td><td>12.9</td></tr><tr><td>Qwen3-Embed</td><td>32</td><td>0</td><td>0.1</td><td>1.1</td></tr><tr><td>Qwen3-Embed</td><td>64</td><td>0</td><td>0.2</td><td>1.0</td></tr><tr><td>Qwen3-Embed</td><td>128</td><td>0.3</td><td>0.4</td><td>1.8</td></tr><tr><td>Qwen3-Embed</td><td>256</td><td>0.4</td><td>0.8</td><td>3.2</td></tr><tr><td>Qwen3-Embed</td><td>512</td><td>0.6</td><td>1.3</td><td>3.3</td></tr><tr><td>Qwen3-Embed</td><td>768</td><td>0.7</td><td>1.5</td><td>3.8</td></tr><tr><td>Qwen3-Embed</td><td>1024</td><td>0.7</td><td>1.6</td><td>4.6</td></tr><tr><td>Qwen3-Embed</td><td>2048</td><td>0.9</td><td>1.7</td><td>4.7</td></tr><tr><td>Qwen3-Embed</td><td>3072</td><td>0.8</td><td>1.6</td><td>4.8</td></tr><tr><td>Qwen3-Embed</td><td>4096</td><td>0.8</td><td>1.8</td><td>4.8</td></tr><tr><td>Gemini-Embed</td><td>2</td><td>0</td><td>0</td><td>0.1</td></tr><tr><td>Gemini-Embed</td><td>4</td><td>0</td><td>0</td><td>0.0</td></tr><tr><td>Gemini-Embed</td><td>8</td><td>0</td><td>0</td><td>0.0</td></tr><tr><td>Gemini-Embed</td><td>16</td><td>0</td><td>0</td><td>0.0</td></tr><tr><td>Gemini-Embed</td><td>32</td><td>0</td><td>0</td><td>0.0</td></tr><tr><td>Gemini-Embed</td><td>64</td><td>0</td><td>0</td><td>0.3</td></tr><tr><td>Gemini-Embed</td><td>128</td><td>0</td><td>0.1</td><td>0.3</td></tr><tr><td>Gemini-Embed</td><td>256</td><td>0</td><td>0.1</td><td>1.2</td></tr><tr><td>Gemini-Embed</td><td>512</td><td>0.2</td><td>1.1</td><td>3.6</td></tr><tr><td>Gemini-Embed</td><td>768</td><td>0.9</td><td>2.5</td><td>7.6</td></tr><tr><td>Gemini-Embed</td><td>1024</td><td>1.3</td><td>2.7</td><td>8.1</td></tr><tr><td>Gemini-Embed</td><td>2048</td><td>1.5</td><td>3.1</td><td>8.5</td></tr><tr><td>Gemini-Embed</td><td>3072</td><td>1.6</td><td>3.5</td><td>10.0</td></tr><tr><td>1 MILCO (SAP, SCTKD, LexEcho)</td><td>280,524</td><td>26.2</td><td>47.0</td><td>73.5</td></tr></table>

#

[page 19]

A.4 EMBEDDING LIMIT TEST

Table 11 shows the advantage of MILCO over strong state-of-the-art dense baselines on the LIMIT test (Weller et al., 2025). MILCO achieves an R@100 of 73.5, whereas dense models such as Gemini-Embed and Qwen3-Embed nearly collapse to zero.

# A.5 CORRELATION BETWEEN TEXT LENGTH AND VECTOR SPARSITY

In Figure 7, we show a strong correlation between input length and the sparsity of vectors produced by MILCO. Unlike dense retrieval methods, which always generate fixed-length vectors for all queries and documents, LSR methods, including MILCO, adaptively determine the optimal sparsity

![](../assets/doc-005-page20-img1.jpeg)

<details>
<summary>scatter</summary>

| Text length (# of characters) | Vector sparsity (number of non-zeros) |
| --- | --- |
| ~100 | ~1100 |
| ~300 | ~660 |
| ~900 | ~660 |
| ~1500 | ~480 |
| ~2100 | ~610 |
</details>

Figure 7: MILCO: Correlation between input text length and the sparsity of output vectors.

Table 12: MILCO: Effectiveness at different TopK (tokens). (nDCG@10, MIRACL)

<table><tr><td>TopK (tokens)</td><td>Avg</td><td>ar</td><td>bn</td><td>de</td><td>en</td><td>es</td><td>fa</td><td>fi</td><td>fr</td><td>hi</td><td>id</td><td>ja</td><td>ko</td><td>ru</td><td>sw</td><td>te</td><td>th</td><td>yo</td><td>zh</td></tr><tr><td>10</td><td>44.5</td><td>55.66</td><td>50.1</td><td>38.38</td><td>34.15</td><td>34.6</td><td>35.65</td><td>57.53</td><td>40.42</td><td>29.65</td><td>38.16</td><td>43.33</td><td>49.13</td><td>42.65</td><td>55.92</td><td>56.41</td><td>48.56</td><td>53.11</td><td>37.9</td></tr><tr><td>20</td><td>54.6</td><td>66.81</td><td>62.26</td><td>45.75</td><td>43.32</td><td>41.98</td><td>45.07</td><td>66.9</td><td>47.02</td><td>41.09</td><td>45.72</td><td>55.88</td><td>57.58</td><td>52.69</td><td>65.76</td><td>72.89</td><td>64.93</td><td>60.99</td><td>45.97</td></tr><tr><td>50</td><td>63.8</td><td>74.29</td><td>73.7</td><td>52.87</td><td>51.41</td><td>51.65</td><td>52.95</td><td>74.29</td><td>53.31</td><td>52.79</td><td>53.08</td><td>67.11</td><td>66.08</td><td>63.95</td><td>74.1</td><td>82.61</td><td>77.64</td><td>69.69</td><td>56.82</td></tr><tr><td>100</td><td>68.4</td><td>77.52</td><td>77.98</td><td>58.07</td><td>56.8</td><td>56.36</td><td>59.31</td><td>77.2</td><td>58.49</td><td>60.09</td><td>57.27</td><td>72.11</td><td>69.02</td><td>69.34</td><td>76.93</td><td>85.13</td><td>81.45</td><td>76.12</td><td>61.79</td></tr><tr><td>200</td><td>71.0</td><td>79.63</td><td>80.59</td><td>60.25</td><td>59.7</td><td>59.87</td><td>61.71</td><td>79.7</td><td>61.41</td><td>63.8</td><td>59.46</td><td>75.59</td><td>70.7</td><td>72.76</td><td>78.72</td><td>87.05</td><td>83.15</td><td>79.75</td><td>64.72</td></tr><tr><td>300</td><td>72.1</td><td>80.06</td><td>81.46</td><td>61.49</td><td>61.04</td><td>61.05</td><td>62.75</td><td>80.27</td><td>62.55</td><td>66.11</td><td>60.33</td><td>76.43</td><td>71.3</td><td>73.59</td><td>79.72</td><td>87.45</td><td>83.93</td><td>82.36</td><td>66.14</td></tr><tr><td>500</td><td>72.6</td><td>80.58</td><td>81.65</td><td>62.39</td><td>61.98</td><td>61.86</td><td>63.45</td><td>80.68</td><td>62.75</td><td>66.05</td><td>61.06</td><td>76.94</td><td>72.12</td><td>74.45</td><td>80.02</td><td>87.92</td><td>84.34</td><td>82.26</td><td>66.85</td></tr><tr><td>700</td><td>72.7</td><td>80.83</td><td>81.97</td><td>62.75</td><td>62.1</td><td>62.14</td><td>63.13</td><td>80.7</td><td>62.79</td><td>65.21</td><td>60.97</td><td>77.28</td><td>72.03</td><td>74.8</td><td>80.16</td><td>87.95</td><td>84.41</td><td>82.19</td><td>66.99</td></tr><tr><td>1000</td><td>72.7</td><td>80.81</td><td>82.12</td><td>62.83</td><td>62.09</td><td>62.17</td><td>63.04</td><td>80.63</td><td>62.74</td><td>65.12</td><td>60.99</td><td>77.28</td><td>71.94</td><td>74.89</td><td>80.26</td><td>87.75</td><td>84.48</td><td>82.36</td><td>66.94</td></tr></table>

Table 13: MILCO: Effectiveness at different pruning percentile P. (nDCG@10, MIRACL)

<table><tr><td>P</td><td>#Tokens</td><td>Avg</td><td>ar</td><td>bn</td><td>de</td><td>en</td><td>es</td><td>fa</td><td>fi</td><td>fr</td><td>hi</td><td>id</td><td>ja</td><td>ko</td><td>ru</td><td>sw</td><td>te</td><td>th</td><td>yo</td><td>zh</td></tr><tr><td>10</td><td>512.5</td><td>72.6</td><td>80.8</td><td>82.0</td><td>62.7</td><td>62.1</td><td>62.0</td><td>63.1</td><td>80.6</td><td>62.8</td><td>65.1</td><td>60.9</td><td>77.3</td><td>72.0</td><td>74.9</td><td>80.2</td><td>87.8</td><td>84.4</td><td>82.0</td><td>66.8</td></tr><tr><td>20</td><td>455.8</td><td>72.6</td><td>80.7</td><td>81.8</td><td>62.8</td><td>62.0</td><td>61.8</td><td>63.2</td><td>80.6</td><td>62.9</td><td>64.8</td><td>61.0</td><td>77.3</td><td>72.0</td><td>74.9</td><td>80.2</td><td>87.8</td><td>84.5</td><td>81.7</td><td>66.8</td></tr><tr><td>50</td><td>285.6</td><td>72.3</td><td>80.7</td><td>81.8</td><td>61.7</td><td>61.1</td><td>61.7</td><td>63.1</td><td>80.5</td><td>62.6</td><td>64.3</td><td>60.8</td><td>76.9</td><td>71.9</td><td>74.6</td><td>80.1</td><td>87.8</td><td>84.2</td><td>80.4</td><td>66.4</td></tr><tr><td>70</td><td>172.2</td><td>71.7</td><td>80.3</td><td>81.5</td><td>60.9</td><td>60.1</td><td>60.5</td><td>62.5</td><td>79.9</td><td>61.3</td><td>64.2</td><td>60.1</td><td>76.6</td><td>70.5</td><td>74.2</td><td>79.4</td><td>87.8</td><td>83.8</td><td>80.7</td><td>65.2</td></tr><tr><td>80</td><td>115.1</td><td>70.6</td><td>79.6</td><td>80.7</td><td>60.9</td><td>59.0</td><td>59.6</td><td>61.3</td><td>78.8</td><td>60.8</td><td>62.3</td><td>58.7</td><td>75.4</td><td>68.8</td><td>73.0</td><td>78.3</td><td>86.9</td><td>83.7</td><td>79.2</td><td>64.0</td></tr><tr><td>85</td><td>86.4</td><td>69.5</td><td>78.6</td><td>79.5</td><td>59.0</td><td>57.2</td><td>58.5</td><td>60.1</td><td>78.3</td><td>59.0</td><td>61.7</td><td>58.4</td><td>74.2</td><td>67.5</td><td>71.7</td><td>77.2</td><td>86.4</td><td>82.8</td><td>77.7</td><td>63.0</td></tr><tr><td>90</td><td>57.9</td><td>67.4</td><td>76.6</td><td>77.8</td><td>57.8</td><td>55.0</td><td>56.1</td><td>56.1</td><td>76.7</td><td>57.4</td><td>58.6</td><td>56.4</td><td>72.1</td><td>65.7</td><td>68.9</td><td>76.3</td><td>84.5</td><td>81.4</td><td>75.0</td><td>60.7</td></tr><tr><td>95</td><td>29.2</td><td>62.2</td><td>71.8</td><td>71.8</td><td>52.5</td><td>48.7</td><td>51.2</td><td>48.9</td><td>71.8</td><td>53.6</td><td>52.6</td><td>52.5</td><td>65.5</td><td>63.3</td><td>63.3</td><td>71.3</td><td>78.1</td><td>76.2</td><td>70.5</td><td>55.7</td></tr><tr><td>97</td><td>17.7</td><td>56.0</td><td>66.2</td><td>65.9</td><td>44.2</td><td>42.4</td><td>46.6</td><td>44.2</td><td>66.0</td><td>49.4</td><td>45.0</td><td>48.5</td><td>57.4</td><td>58.3</td><td>56.1</td><td>65.0</td><td>67.4</td><td>68.6</td><td>67.3</td><td>50.0</td></tr><tr><td>99</td><td>6.5</td><td>39.5</td><td>48.38</td><td>46.14</td><td>32.18</td><td>29.04</td><td>33.31</td><td>28.55</td><td>50.53</td><td>37.56</td><td>28.06</td><td>37.17</td><td>38.38</td><td>42.27</td><td>37.82</td><td>43.04</td><td>43.07</td><td>44.59</td><td>57.09</td><td>34.13</td></tr></table>

[page 20]

(i.e., the number of non-zero elements) based on the content density of the input text, as approximated by its length. This allows MILCO to allocate fewer tokens for short texts and more for longer ones, while maintaining the same average sparsity overall.

On Table 12 and Table 13, we show the results of two different post-hoc pruning methods (Top-k Pruning and Mass-based Pruning) applied on MILCO.

# A.6 ALIGNMENT AND CONTRASTIVE TRAINING DATA

The sources and statistics of the data used for our Sparse Alignment Pretraining are reported in Table 14. In total, the corpus consists of 594 million bi-text pairs, each containing one English sentence and one non-English sentence with the same semantic meaning.

The statistics of the data used for our contrastive training are shown in Table 15. This dataset contains 1.4M queries collected from 16 datasets, covering English, Chinese, and 16 additional languages from Mr.TYDI (Zhang et al., 2021) and MIRACL (Zhang et al., b). Similar to prior work (Chen et al., 2024; Li et al.; Lei et al., 2025), our training data also includes many in-domain datasets from BEIR (Thakur et al., 2021).

Table 14: Pretraining datasets: Parallel Sentences collected from OPUS by Reimers & Gurevych (2019).

<table><tr><td>Dataset Name</td><td>#Pairs</td></tr><tr><td>mmarco (passages)</td><td>115M</td></tr><tr><td>wikititles</td><td>14M</td></tr><tr><td>wikimatrix</td><td>19M</td></tr><tr><td>europarl</td><td>50M</td></tr><tr><td>opensubtitles</td><td>274M</td></tr><tr><td>talks</td><td>20M</td></tr><tr><td>tatoeba</td><td>8M</td></tr><tr><td>jw300</td><td>92M</td></tr><tr><td>news-commentary</td><td>2M</td></tr><tr><td>Total</td><td>594M</td></tr></table>

Table 15: Contrastive Training Data obtained from Chen et al. (2024).

<table><tr><td>Dataset</td><td>#Samples</td></tr><tr><td>en_msmarco (Nguyen et al., 2016)</td><td>485,823</td></tr><tr><td>en_eli5 (Fan et al., 2019)</td><td>150,000</td></tr><tr><td>zh_mmarco_zh (Bonifacio et al., 2021)</td><td>100,000</td></tr><tr><td>zh_t2ranking (Xie et al., 2023)</td><td>90,467</td></tr><tr><td>en_squad (Rajpurkar et al., 2016)</td><td>87,599</td></tr><tr><td>en_hotpotqa (Yang et al., 2018)</td><td>84,516</td></tr><tr><td>zh_dureader (He et al., 2017)</td><td>80,416</td></tr><tr><td>en_trivia (Joshi et al., 2017)</td><td>60,315</td></tr><tr><td>en_quora (Sharma et al., 2019)</td><td>60,202</td></tr><tr><td>en_nq (Kwiatkowski et al., 2019)</td><td>58,568</td></tr><tr><td>multilingual_mrtydi (Zhang et al., 2021)</td><td>48,729</td></tr><tr><td>multilingual_miracl (Zhang et al., b)</td><td>40,203</td></tr><tr><td>en_fever (Thorne et al., 2018)</td><td>29,096</td></tr><tr><td>en_fiqa (Maia et al., 2018)</td><td>5,500</td></tr><tr><td>en_arguana (Wachsmuth et al., 2018)</td><td>4,065</td></tr><tr><td>en_scidocs (Cohan et al., 2020)</td><td>884</td></tr><tr><td>Total</td><td>1,386,383</td></tr></table>

#

[page 21]

A.7 CONTRASTIVE TRAINING: DISTILLATION

For each query $q_{i}$ , we consider a document candidate set consisting of one positive $d^{+}$ and a set of negatives $D^{-}$ . The precomputed teacher scores are from the cross-encoder, denoted as $\theta_{\mathrm{CE}}(d,q)$ . The student scores $\theta_{\mathrm{milco}}(d,q)$ are estimated via the dot product of MILCO's lexical representations. These scores are converted into distributions over the candidate set with a softmax:

$$
P _ {x} (d | q) = \frac {\exp \left(\theta_ {x} (d , q)\right)}{\sum_ {d ^ {\prime} \in \{d ^ {+} , D ^ {-} \}} \exp \left(\theta_ {x} (d ^ {\prime} , q)\right)}, \tag {9}
$$

where $\theta_x(q,d)$ denotes either the teacher or student scoring function of the given query and document. The distillation objective is then defined as the KL divergence between the teacher's and the student's distributions across a batch of $B$ queries:

$$
L _ {\mathrm{KLD}} = \frac {1}{B} \sum_ {i = 1} ^ {B} \mathbf {K L} \big (P _ {\mathrm{milco}} (d | q _ {i}) | | P _ {\mathrm{CE}} (d | q _ {i}) \big). \tag {10}
$$

#

[page 22]

A.8 TRAINING CONFIGURATIONS AND HYPER-PARAMETERS

The hyperparameters for pretraining and training are reported in Table 16 and Table 17. Both training stages are conducted on 16 GPU nodes, each equipped with 8 AMD Instinct MI250X GPU dies. We instantiate the Multilingual Connector with a simple randomly-initialized MLP layer with a GELU activation function. For sparse regularization, we set the regularization weight to 1e-5 for both queries and documents during contrastive training. We train MILCO using the HuggingFace framework (Wolf et al., 2019). Hyperparameters not listed in Table 16 and Table 17 are set to the default values defined in HuggingFace's TrainingArguments.

Table 16: MILCO: Hyperparameters for Sparse Alignment Pre-training.

<table><tr><td>Hyperparameter</td><td>Value</td></tr><tr><td>training_type</td><td>alignment</td></tr><tr><td>model_type</td><td>bert</td></tr><tr><td>lsr_encoder_checkpoint</td><td>naver/splade-v3</td></tr><tr><td>multilingual_encoder_checkpoint</td><td>BAAI/bge-m3-unsupervised</td></tr><tr><td>train_datasets</td><td>mmarco, wikititles, wikimatrix, europarl, opensubtitles, talks, tatoeba, jw300, news-commentary</td></tr><tr><td>seed</td><td>42</td></tr><tr><td>max_length</td><td>256</td></tr><tr><td>per_device_train_batch_size</td><td>64</td></tr><tr><td>per_device_eval_batch_size</td><td>128</td></tr><tr><td>num_train_epochs</td><td>2</td></tr><tr><td>save_total_limit</td><td>2</td></tr><tr><td>warmup_steps</td><td>10000</td></tr><tr><td>lr_scheduler_type</td><td>cosine</td></tr><tr><td>dataloader_num_workers</td><td>8</td></tr><tr><td>learning_rate</td><td>2e-5</td></tr><tr><td>bf16</td><td>True</td></tr><tr><td>logging_steps</td><td>500</td></tr><tr><td>save_steps</td><td>20000</td></tr><tr><td>pooling</td><td>max</td></tr><tr><td>remove_unused_columns</td><td>False</td></tr><tr><td>dynamic_length</td><td>True</td></tr></table>

Table 17: MILCO: Hyperparameters for Sparse Contrastive Training.

<table><tr><td>Hyperparameter</td><td>Value</td></tr><tr><td>training_type</td><td>distillation</td></tr><tr><td>model_type</td><td>bert</td></tr><tr><td>lsr_encoder_checkpoint</td><td>naver/splade-v3</td></tr><tr><td>multilingual_encoder_checkpoint</td><td>BAAI/bge-m3-unsupervised</td></tr><tr><td>train_group_size</td><td>8</td></tr><tr><td>lambda_q</td><td>1e-3</td></tr><tr><td>lambda_d</td><td>1e-5</td></tr><tr><td>train_datasets</td><td>bge</td></tr><tr><td>seed</td><td>42</td></tr><tr><td>max_length</td><td>512</td></tr><tr><td>per_device_train_batch_size</td><td>8</td></tr><tr><td>per_device_eval_batch_size</td><td>32</td></tr><tr><td>num_train_epochs</td><td>8</td></tr><tr><td>save_total_limit</td><td>2</td></tr><tr><td>warmup_ratio</td><td>0.03</td></tr><tr><td>lr_scheduler_type</td><td>cosine</td></tr><tr><td>dataloader_num_workers</td><td>1</td></tr><tr><td>learning_rate</td><td>2e-5</td></tr><tr><td>bf16</td><td>True</td></tr><tr><td>logging_steps</td><td>500</td></tr></table>

#

[page 23]

A.9 LIST OF LANGUAGES SUPPORTED BY MILCO

Table 18: Datasets and their supported languages.

<table><tr><td>Dataset</td><td>Languages (standardized)</td><td>#languages</td></tr><tr><td>MIRACL</td><td>ar, bn, de, en, es, fa, fi, fr, hi, id, ja, ko, ru, sw, te, th, yo, zh</td><td>18</td></tr><tr><td>MLDR</td><td>ar, de, en, es, fr, hi, it, ja, ko, pt, ru, th, zh</td><td>13</td></tr><tr><td>MKQA</td><td>ar, da, de, es, fi, fr, he, hu, it, ja, km, ko, ms, nl, no, pl, pt, ru, sv, th, tr, vi, zh-cn, zh-hk, zh-tw</td><td>25</td></tr><tr><td>BelebeleRetrieval</td><td>acm, af, en</td><td>3</td></tr><tr><td>MLQARetrieval</td><td>ar, de, en, es, hi, vi</td><td>6</td></tr><tr><td>TwitterHjerneRetrieval</td><td>dan</td><td>1</td></tr><tr><td>WikipediaRetrievalMultilingual</td><td>bg, bn, cs, da, de, en, fa, fi, hi, it, nl, no, pt, ro, sr, sv</td><td>16</td></tr><tr><td>WikiMatrix</td><td>ar, bg, ca, cs, da, de, el, es, et, fa, fi, fr, gl, he, hi, hr, hu, hy, id, it, ja, ka, ko, lt, lv, mk, ms, nl, pl, pt, ro, ru, sk, sl, sq, sr, sv, th, tr, uk, ur, vi, zh-cn</td><td>41</td></tr><tr><td>parallel-sentences-opensubtitles</td><td>ar, bg, ca, cs, da, de, el, es, et, fa, fi, fr, gl, he, hi, hr, hu, id, it, ja, ka, ko, lt, mk, mr, nl, pl, pt, ro, ru, sk, sl, sq, sr, sv, tr, uk, vi, zh</td><td>38</td></tr><tr><td>parallel-sentences-tatoeba</td><td>ar, bg, ca, cs, da, de, el, es, et, fa, fi, fr, gl, gu, he, hi, hr, hu, hy, id, it, ja, ka, ko, ku, lt, lv, mk, mn, mr, ms, my, nb, nl, pl, pt, ro, ru, sk, sl, sq, sr, sv, th, tr, uk, ur, vi, zh</td><td>46</td></tr><tr><td>parallel-sentences-global-voices</td><td>ar, bg, ca, cs, da, de, el, es, fa, fr, he, hi, hu, id, it, ko, mk, my, nl, pl, pt, ro, ru, sq, sr, sv, tr, ur</td><td>27</td></tr><tr><td>parallel-sentences-europarl</td><td>bg, cs, da, de, el, es, et, fi, fr, hu, it, lt, lv, nl, pl, pt, ro, sk, sl, sv</td><td>20</td></tr><tr><td>parallel-sentences-talks</td><td>ar, bg, ca, cs, da, de, el, es, et, fa, fi, fr, fr-ca, gl, gu, he, hi, hr, hu, hy, id, it, ja, ka, ko, ku, lt, lv, mk, mn, mr, ms, my, nb, nl, pl, pt, pt-br, ro, ru, sk, sl, sq, sr, sv, th, tr, uk, ur, vi, zh-cn, zh-tw</td><td>50</td></tr><tr><td>parallel-sentences-jw300</td><td>ar, bg, cs, da, de, el, es, et, fa, fi, fr, gu, he, hi, hr, hu, hy, id, it, ja, ka, ko, lt, lv, mk, mn, mr, my, nl, pl, pt, ro, ru, sk, sl, sq, sr, sv, th, tr, uk, ur, vi</td><td>43</td></tr><tr><td>parallel-sentences-news-commentary</td><td>ar, cs, de, es, fr, it, ja, nl, pt, ru</td><td>10</td></tr><tr><td>mmarco</td><td>ar, zh, nl, en, fr, de, hi, id, it, ja, pt, ru, es, vi</td><td>14</td></tr><tr><td>All Test Datasets</td><td>acm, af, ar, bg, bn, cs, da, de, en, es, fa, fi, fr, he, hi, hu, id, it, ja, km, ko, ms, nl, no, pl, pt, ro, ru, sr, sv, sw, te, th, tr, vi, yo, zh, zh-cn, zh-hk, zh-tw</td><td>39</td></tr><tr><td>All (Pretrain/Train + Test) datasets</td><td>acm, af, ar, bg, bn, ca, cs, da, de, el, en, es, et, fa, fi, fr, fr-ca, gl, gu, he, hi, hr, hu, hy, id, it, ja, ka, km, ko, ku, lt, lv, mk, mn, mr, ms, my, nb, nl, no, pl, pt, pt-br, ro, ru, sk, sl, sq, sr, sv, sw, te, th, tr, uk, ur, vi, yo, zh, zh-cn, zh-hk, zh-tw</td><td>63</td></tr></table>

# A.10 ABLATIONS ON LEXECHO HEAD.

To provide additional insights on our LexEcho head, we perform an ablation that interpolates between the pivot (English) and source views in LexEcho. Specifically, we multiply the English view by $\alpha$ and the source view by $(1 - \alpha)$ , with $\alpha \in \{0.0, 0.2, \ldots, 1.0\}$ , and report MIRACL results in Table 19.

Table 19: MILCO performance under different pivot–source weighting schemes on the MIRACL (hard negatives) benchmark.

<table><tr><td> $\alpha$ </td><td>ar</td><td>bn</td><td>en</td><td>es</td><td>fa</td><td>fi</td><td>fr</td><td>hi</td><td>id</td><td>ja</td><td>ko</td><td>ru</td><td>sw</td><td>te</td><td>th</td><td>zh</td><td>de</td><td>yo</td><td>Avg</td></tr><tr><td>0.00</td><td>5.21</td><td>9.61</td><td>3.56</td><td>0.09</td><td>1.74</td><td>8.18</td><td>0.14</td><td>1.56</td><td>4.71</td><td>3.33</td><td>11.14</td><td>2.19</td><td>2.75</td><td>31.35</td><td>14.90</td><td>0.00</td><td>0.20</td><td>0.27</td><td>5.61</td></tr><tr><td>0.20</td><td>11.01</td><td>17.51</td><td>6.16</td><td>0.91</td><td>4.23</td><td>17.80</td><td>1.51</td><td>3.95</td><td>9.55</td><td>7.16</td><td>19.09</td><td>5.35</td><td>6.95</td><td>43.42</td><td>22.47</td><td>0.11</td><td>1.84</td><td>4.49</td><td>10.19</td></tr><tr><td>0.40</td><td>79.38</td><td>79.30</td><td>56.55</td><td>55.89</td><td>57.29</td><td>79.72</td><td>60.70</td><td>57.46</td><td>58.46</td><td>75.36</td><td>71.99</td><td>73.10</td><td>77.52</td><td>86.77</td><td>82.44</td><td>56.95</td><td>59.67</td><td>63.23</td><td>68.43</td></tr><tr><td>0.50</td><td>80.79</td><td>82.00</td><td>62.08</td><td>62.06</td><td>63.08</td><td>80.64</td><td>62.73</td><td>65.06</td><td>60.91</td><td>77.25</td><td>72.00</td><td>74.96</td><td>80.18</td><td>87.82</td><td>84.46</td><td>66.80</td><td>62.83</td><td>82.14</td><td>72.66</td></tr><tr><td>0.60</td><td>80.08</td><td>81.43</td><td>62.03</td><td>62.00</td><td>62.34</td><td>79.91</td><td>63.14</td><td>64.94</td><td>60.14</td><td>76.64</td><td>71.13</td><td>74.30</td><td>79.61</td><td>87.11</td><td>83.81</td><td>65.54</td><td>61.73</td><td>81.72</td><td>72.09</td></tr><tr><td>0.80</td><td>78.19</td><td>80.22</td><td>60.18</td><td>61.27</td><td>60.36</td><td>78.81</td><td>62.16</td><td>64.00</td><td>58.39</td><td>74.66</td><td>69.12</td><td>72.95</td><td>78.49</td><td>84.05</td><td>81.47</td><td>63.63</td><td>60.58</td><td>80.86</td><td>70.52</td></tr><tr><td>1.00</td><td>77.77</td><td>79.35</td><td>59.53</td><td>60.98</td><td>59.73</td><td>78.43</td><td>62.19</td><td>63.31</td><td>57.97</td><td>73.80</td><td>68.52</td><td>72.74</td><td>78.04</td><td>82.90</td><td>80.72</td><td>63.33</td><td>60.55</td><td>80.46</td><td>70.02</td></tr></table>

[page 24]

We find that MILCO performs very poorly with only the source view ( $\alpha = 0.0$ ; average nDCG@10 = 5.61), indicating that the English pivot is essential. With only the English view ( $\alpha = 1.0$ ), MILCO is already strong (average nDCG@10 = 70.02) but not optimal. The best result is obtained with a roughly balanced fusion ( $\alpha = 0.5$ ), reaching an average nDCG@10 of 72.66 (around 3–4% relative improvement over $\alpha = 1.0$ ). Performance for $\alpha$ between 0.5 and 0.6 is very similar, suggesting that LexEcho is not overly sensitive to the exact weighting as long as both views contribute.

# A.11 EFFECT OF LANGUAGE COVERAGE IN ALIGNMENT PRETRAINING

We now investigate how language coverage in the parallel corpus used for MILCO's sparse alignment pretraining affects the final retrieval performance across MIRACL languages. To this end, we compare MILCO (alignment + distillation) against our best-performing dense baseline (distillation only), trained with the same data and compute, and report per-language $\Delta nDCG@10$ . We then aggregate languages by their share of alignment data to analyze the relationship between coverage and effectiveness (Tables 20 and 21).

Table 20: Average $\Delta nDCG@10$ as a function of alignment coverage. Languages are grouped into well-represented ( $P \geq 1\%$ ) and under-represented ( $P < 1\%$ ) buckets based on their proportion in the parallel corpus.

<table><tr><td>Percentage category:</td><td>P ≥ 1</td><td>P &lt; 1</td></tr><tr><td>Avg. ΔnDCG@10</td><td>1.59</td><td>0.77</td></tr></table>

Table 21 lists nDCG@10 and $\Delta nDCG@10$ for all 18 MIRACL languages, together with their proportion in the parallel corpus. Aggregating by coverage (Table 20), we observe an average gain of +1.59 $\Delta nDCG@10$ for well-represented languages ( $P \geq 1\%$ ) and a smaller but still positive average gain of +0.77 for under-represented languages ( $P < 1\%$ ), including languages with 0 parallel samples (sw, te, yo, bn). The main exception is fa (-1.09), which we plan to analyze further.

These results indicate that higher coverage in the alignment corpus amplifies the gains from MILCO, but is not strictly required: even languages that are weakly covered or entirely absent from the alignment corpus still benefit on average. This behavior highlights MILCO's multilingual alignment pretraining as an effective mechanism for knowledge transfer and sharing across languages.

Table 21: MILCO effectiveness vs. alignment data distribution across languages (MIRACL Hard Negatives.). We report nDCG@10, per-language $\Delta$ nDCG@10 (MILCO vs. dense baseline), and the number and proportion of parallel corpus samples used for alignment pretraining.

<table><tr><td>Lang</td><td>nDCG@10</td><td>ΔnDCG@10</td><td>Samples</td><td>Percentage</td></tr><tr><td>ar</td><td>80.4</td><td>0.919</td><td>19002229</td><td>5.5</td></tr><tr><td>bn</td><td>82.6</td><td>2.387</td><td>0</td><td>0</td></tr><tr><td>en</td><td>60.4</td><td>3.585</td><td>-</td><td>-</td></tr><tr><td>es</td><td>60.9</td><td>0.487</td><td>28470451</td><td>8.23</td></tr><tr><td>fa</td><td>62.3</td><td>-1.09</td><td>646913</td><td>0.19</td></tr><tr><td>fi</td><td>81.2</td><td>2.676</td><td>4958793</td><td>1.43</td></tr><tr><td>fr</td><td>61.7</td><td>-0.922</td><td>22574836</td><td>6.53</td></tr><tr><td>hi</td><td>64.4</td><td>2.158</td><td>9626940</td><td>2.78</td></tr><tr><td>id</td><td>60.9</td><td>2.498</td><td>17591514</td><td>5.09</td></tr><tr><td>ja</td><td>77.2</td><td>2.524</td><td>11542221</td><td>3.34</td></tr><tr><td>ko</td><td>72.1</td><td>1.548</td><td>3648265</td><td>1.05</td></tr><tr><td>ru</td><td>74.6</td><td>2.458</td><td>16592711</td><td>4.8</td></tr><tr><td>sw</td><td>80.3</td><td>0.734</td><td>0</td><td>0</td></tr><tr><td>te</td><td>87.9</td><td>0.87</td><td>0</td><td>0</td></tr><tr><td>th</td><td>84.2</td><td>1.295</td><td>1668858</td><td>0.48</td></tr><tr><td>zh</td><td>65.5</td><td>1.328</td><td>9006690</td><td>2.6</td></tr><tr><td>de</td><td>61.4</td><td>1.823</td><td>24431450</td><td>7.07</td></tr><tr><td>yo</td><td>83.6</td><td>0.41</td><td>0</td><td>0</td></tr></table>
