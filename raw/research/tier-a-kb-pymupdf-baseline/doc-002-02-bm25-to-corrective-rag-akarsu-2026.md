---
id: doc-002
source: 02-bm25-to-corrective-rag-akarsu-2026.pdf
source_type: pdf
source_sha256: 94fb4793a4f7ec5cf21be65c16a5d070599365befbe2af47549f95c1e6db64e6
extraction_method: pymupdf4llm@unknown
extraction_date: 2026-05-26
pages: 11
headings:
  - From BM25 to Corrective RAG: Benchmarking Retrieval Strategies for Text-and-Table Documents
  - I. INTRODUCTION
  - II. RELATED WORK
  - III. METHODOLOGY
  - _A. Dataset_
  - _B. Retrieval Methods_
  - _C. Evaluation Metrics_
  - _D. Experimental Setup_
  - IV. RESULTS
  - _A. Main Retrieval Results_
tokens_estimated: 13686
warnings:
  - "ligatures_recovered: pymupdf4llm dropped letters from 3 word(s) with fi/ff/fl glyphs (e.g. 'Ofcial'→'Official', 'fexible'→'flexible'); fixed via the doc2kb ligature-recovery table — no manual action needed"
  - "dropped_pictures: 2/7 placeholder(s) were auto-recovered as assets, but 5 still remain over 11 page(s) (0.45/page). Re-extract this PDF by reading the source file directly via the Read tool and overwrite the body with a manual transcription of the remaining figures"
assets: [../assets/doc-002-page06-img1.png, ../assets/doc-002-page06-img2.png]
---
[page 1]

# From BM25 to Corrective RAG: Benchmarking Retrieval Strategies for Text-and-Table Documents

Meftun Akarsu Technische Hochschule Ingolstadt mea5963@thi.de

Recep Kaan Karaman Christopher Mierbach Uludag University Radiate kaankaraman@uludag.edu.tr christopher@radiate.com

_**Abstract**_ **—Retrieval-Augmented Generation (RAG) systems critically depend on retrieval quality, yet no systematic comparison of modern retrieval methods exists for heterogeneous documents containing both text and tabular data. We benchmark ten retrieval strategies spanning sparse, dense, hybrid fusion, cross-encoder reranking, query expansion, index augmentation, and adaptive retrieval on a challenging financial QA benchmark of 23,088 queries over 7,318 documents with mixed text-andtable content. We evaluate retrieval quality via Recall@** _k_ **, MRR, and nDCG, and end-to-end generation quality via Number Match, with paired bootstrap significance testing. Our results show that (1) a two-stage pipeline combining hybrid retrieval with neural reranking achieves Recall@5 of 0.816 and MRR@3 of 0.605, outperforming all single-stage methods by a large margin; (2) BM25 outperforms state-of-the-art dense retrieval on financial documents, challenging the common assumption that semantic search universally dominates; and (3) query expansion methods (HyDE, multi-query) and adaptive retrieval provide limited benefit for precise numerical queries, while contextual retrieval yields consistent gains. We provide ablation studies on fusion methods and reranker depth, actionable cost-accuracy recommendations, and release our full benchmark code.**

_**Index Terms**_ **—Retrieval-augmented generation, hybrid retrieval, cross-encoder reranking, financial question answering, text-and-table documents**

## I. INTRODUCTION

The introduction of the Transformer architecture [1] and subsequently pretrained language models [2] fundamentally changed how machines process and reason over text. Yet even the most capable language models face a hard limit: their knowledge is frozen at training time. Retrieval-Augmented Generation (RAG) [3] addresses this by coupling a language model with a retrieval component that fetches relevant documents at inference time, grounding generation in external evidence.

The retrieval component is the most critical part of any RAG system. A language model cannot reason over documents it never receives. Despite this, retrieval receives far less systematic attention than generation. Dozens of retrieval methods exist, benchmarks are inconsistent, and there is little guidance on which method works best for a given document type.

The problem is harder for **documents that mix text and tables** . Financial filings, earnings reports, and regulatory documents are structured this way: text provides context while tables carry the precise figures. A question like “What was the year-over-year revenue growth?” requires locating both the right document and the right cell within it. Semantic retrieval

methods miss exact numerical targets. Lexical methods miss paraphrased context. Neither alone is sufficient.

We study this through systematic benchmarking. Using a financial QA benchmark of 23,088 queries over 7,318 documents with mixed text-and-table content, we evaluate retrieval methods ranging from classical sparse retrieval to hybrid fusion pipelines and neural rerankers. The original benchmark paper tested only six retrieval methods with two metrics. Many approaches that matter in practice, including contextual retrieval, CRAG, and modern reranking models, have never been evaluated in this setting.

- _a) Contributions.:_ This paper makes four contributions:

- 1) A systematic benchmark of ten retrieval methods on a text-and-table financial QA corpus, the most comprehensive evaluation of its kind.

- 2) Multi-dimensional evaluation covering retrieval metrics (Recall@ _k_ , MRR, nDCG, MAP) and generation metrics (Number Match) with paired bootstrap significance testing.

- 3) Ablation studies isolating the effects of fusion strategies and reranker candidate depth.

- 4) Actionable recommendations for practitioners building RAG systems over heterogeneous documents, grounded in empirical cost-accuracy analysis.

## II. RELATED WORK

_a) RAG Retrieval Methods.:_ Classical sparse retrievers such as BM25 remain competitive baselines, particularly in zero-shot out-of-domain settings [4], due to their lexical precision. Learned sparse models like SPLADE [5] extend this by learning neural term expansion weights, and recent work shows that decoder-only LLM backbones further improve sparse retrieval quality [6]. On the dense side, dualencoder architectures pioneered by DPR [7] encode queries and passages into a shared embedding space. Subsequent models including E5 [8], E5-Mistral [9], and BGE-M3 [10] have advanced the state of the art on MTEB [11] and MMTEB [12] through contrastive pretraining and instructiontuned embedding generation. Late-interaction models such as ColBERTv2 [13] and Jina-ColBERT-v2 [14] retain per-token representations for fine-grained matching while still allowing document precomputation. Hybrid retrieval combines sparse and dense signals via Reciprocal Rank Fusion [15] or convex score combination, consistently improving recall by 15–30%

[page 2]

over single-method pipelines [16]. Two-stage reranking with cross-encoder models further refines ranked lists, with recent benchmarks reporting up to 28% nDCG@10 improvement at modest latency cost [17].

_b) Query-Side Retrieval Strategies.:_ Several methods improve retrieval by modifying the query rather than the index. HyDE [18] generates a hypothetical answer document at query time and retrieves using its embedding rather than the original query. RAG-Fusion [19] issues multiple LLMrewritten query variants and merges results via RRF. Both approaches aim to close the gap between short user queries and longer document passages, though their effectiveness depends heavily on whether the LLM can generate plausible pseudodocuments for the target domain.

_c) Index-Side and Structural Retrieval Strategies.:_ An alternative is to enrich document representations at indexing time. Contextual Retrieval [20] prepends LLM-generated summaries to each chunk before indexing, while HyPE [21] precomputes hypothetical questions per chunk, transforming retrieval into question-to-question matching and improving context precision by up to 42 percentage points without added query-time cost. Late Chunking [22] preserves cross-chunk context by applying long-context embeddings before splitting. At a higher level of abstraction, RAPTOR [23] builds recursive tree-structured summaries for multi-granularity retrieval, and GraphRAG [24] constructs entity-relation graphs for queryfocused summarization. On the adaptive front, Self-RAG [25] trains models to decide whether retrieval is needed at all, while CRAG [26] triggers corrective web searches when retrieved document quality is low.

_d) Text-and-Table Question Answering.:_ Answering questions over documents that contain both text and tables requires locating evidence across heterogeneous content types and often performing numerical reasoning. Chen et al. [27] introduced HybridQA, the first large-scale dataset requiring multi-hop reasoning over linked Wikipedia tables and passages. Chen et al. [28] extended this to an open-domain setting in OTT-QA, retrieving from over 400K tables and 5M passages. In the financial domain, FinQA [29] provides expertannotated question-program pairs over earnings reports, TATQA [30] focuses on numerical operations over hybrid tabulartextual contexts, and ConvFinQA [31] extends FinQA to multiturn reasoning. A recent survey of table QA in the LLM era [32] finds that retrieval of the correct heterogeneous context remains the primary bottleneck, even as generation quality improves. Our work directly targets this bottleneck.

_e) RAG Benchmarks and Evaluation.:_ BEIR [4] established zero-shot retrieval evaluation across 18 diverse datasets and remains the standard reference point for retrieval method comparison. KILT [33] unified five knowledge-intensive task types over a shared Wikipedia snapshot. More recent RAGspecific benchmarks include RGB [34], which tests robustness to noise and counterfactual context; CRAG [35], which spans five domains with temporal dynamics; and RAGBench [36], which provides 100K examples with the TRACe evaluation framework. RAGAS [37] and ARES [38] introduced

automated evaluation without gold labels, enabling scalable faithfulness and relevance measurement. Li et al. [16] provide a systematic study of RAG design choices at COLING 2025. None of these benchmarks focus on retrieval method comparison over documents with mixed text-and-table content. The benchmark we use [39] unifies FinQA, ConvFinQA, and TATDQA into 23,088 queries over 7,318 financial documents, and where the original paper tested six methods with two metrics, we evaluate ten methods with a comprehensive set of retrieval and generation metrics.

## III. METHODOLOGY

## _A. Dataset_

We evaluate on T[2] -RAGBench [39], a financial QA benchmark accepted at EACL 2026. The dataset contains 23,088 question-context-answer triples drawn from three source datasets: FinQA [29] (8,281 pairs), ConvFinQA [31] (3,458 pairs), and TAT-DQA [30] (11,349 pairs), covering 7,318 unique financial documents averaging approximately 920 tokens each. Each document contains a mix of text and markdown-formatted tables extracted from real SEC filings and annual reports.

The benchmark’s core design decision distinguishes it from prior financial QA datasets. FinQA, ConvFinQA, and TATDQA were originally constructed in an oracle-context setting, where the relevant document is provided directly to the model. Questions in that setting are context-dependent: the same question may have different correct answers depending on which document is supplied, making them unsuitable for evaluating retrieval. T[2] -RAGBench addresses this by reformulating all questions using Llama 3.3-70B to incorporate identifying information such as company name, sector, and report year, producing questions with exactly one correct answer regardless of context. Human experts validated a random sample of 100 questions per subset: only 7.3% of original questions were context-independent, compared to 83.9% after reformulation, with an inter-annotator agreement of Cohen’s _κ_ = 0 _._ 58.

All answers are numerical. The original paper evaluated six retrieval methods using Number Match and MRR@3, finding that the best method (Hybrid BM25) reached only 41% Number Match against an oracle-context ceiling of 72– 79%, a gap of more than 30 percentage points. We extend this evaluation to ten methods with a broader set of retrieval and generation metrics to systematically characterize where this gap comes from.

## _B. Retrieval Methods_

_a) BM25.:_ We use Okapi BM25 [40] with _k_ 1 = 1 _._ 2 and _b_ = 0 _._ 75 via the rank_bm25 library. BM25 scores documents by weighted term-frequency overlap with sub-linear saturation and document-length normalization. The parameter _k_ 1 controls term-frequency saturation and _b_ controls the degree of length normalization; the values _k_ 1 = 1 _._ 2 and _b_ = 0 _._ 75 are the canonical defaults from the original Okapi system. BM25 provides strong lexical matching for domain-specific terminology such as company names, financial metrics, and

[page 3]

fiscal period identifiers that appear verbatim in both queries and documents, making it a competitive baseline on this corpus.

_b) Dense Retrieval.:_ We encode all queries and documents using OpenAI text-embedding-3-large (3,072 dimensions) via Azure AI Foundry. Document embeddings are indexed with FAISS IndexFlatIP for exact inner-product search, ensuring exhaustive nearest-neighbor retrieval with no approximation error. At query time the top- _k_ results are returned by cosine similarity. This configuration isolates the effect of the embedding model from any index approximation artifacts.

_c) Hybrid Retrieval (RRF).:_ Hybrid retrieval fuses the ranked lists of BM25 and dense retrieval via Reciprocal Rank Fusion [15]. For each document _d_ at rank _ri_ ( _d_ ) in retriever _i_ , the fused score is:

**==> picture [178 x 26] intentionally omitted <==**

with smoothing constant _k_ = 60, the value used in the original paper. We retrieve full ranked lists from both methods, compute RRF scores over their union, and return the top- _k_ by fused score. RRF is unsupervised, requires no score normalization, and consistently outperforms individual retrievers and alternative fusion strategies such as Condorcet and CombMNZ [15].

_d) Hybrid + Cohere Rerank.:_ We apply a two-stage pipeline: hybrid RRF retrieves 50 candidate documents, which are then reranked by Cohere Rerank v4.0 Pro [41], returning the top 10. Unlike bi-encoder models that encode queries and documents independently, cross-encoders process the query and each candidate jointly, producing query-aware relevance scores that capture semantic relationships pointwise retrieval cannot [42]. Cohere Rerank v4.0 Pro was benchmarked specifically on finance-domain retrieval tasks at release, making it well suited to this corpus. This configuration measures whether the added cost of a reranking stage produces meaningful gains on text-and-table documents.

_e) HyDE.:_ HyDE [18] addresses the asymmetry between short queries and long documents by generating a hypothetical answer passage at query time and retrieving with its embedding rather than the original query embedding. The generated document may contain hallucinations, but the dense encoder grounds it to the actual corpus by mapping it into the same embedding space as real documents [18]. We prompt GPT4.1-mini at temperature 0 to generate a plausible answer for each query, embed it with text-embedding-3-large, and retrieve against the corpus index. HyDE was originally shown to outperform unsupervised dense retrievers on web search, QA, and fact verification tasks [18]; its behaviour on numerical financial QA is one of the questions this paper investigates.

_f) Multi-Query Retrieval.:_ Multi-query retrieval issues several reformulations of each query to increase recall across alternative phrasings [19]. We prompt GPT-4.1-mini at temperature 0 to generate three semantically diverse variants per

query, retrieve top- _k_ results for each independently using dense retrieval, and merge the four ranked lists (original plus three variants) via RRF ( _k_ = 60). This approach recovers relevant documents that a single query phrasing may miss, at the cost of additional LLM inference per query.

_g) Contextual Retrieval.:_ Contextual Retrieval [20] enriches each document at indexing time by prepending an LLMgenerated context summary that captures the document’s key entities, reporting period, and financial metrics. We apply this to both the dense and hybrid pipelines, yielding Contextual Dense and Contextual Hybrid variants. All context summaries are generated with GPT-4.1-mini at temperature 0 using the whole-document prompt described in Appendix B.

_h) CRAG (Corrective RAG).:_ CRAG [26] evaluates each retrieved document’s relevance and triggers query rewriting when confidence is low. We implement a two-stage pipeline: first, we retrieve the top-5 documents using hybrid RRF; then, GPT-4.1-mini classifies each document as RELEVANT, AMBIGUOUS, or IRRELEVANT. If all documents are classified as AMBIGUOUS or IRRELEVANT, the query is rewritten and retrieval is repeated. Final results are drawn from the better of the two retrieval rounds. Prompts are documented in Appendix B.

## _C. Evaluation Metrics_

_a) Retrieval Metrics.:_ We report Recall@ _k_ ( _k ∈ {_ 1 _,_ 3 _,_ 5 _,_ 10 _,_ 20 _}_ ), Mean Reciprocal Rank (MRR@ _k_ ), normalized Discounted Cumulative Gain (nDCG@ _k_ ), and Mean Average Precision (MAP).

_b) Generation Metrics.:_ Our primary generation metric is Number Match (NM) with relative tolerance _ϵ_ = 10 _[−]_[2] , following the benchmark’s evaluation protocol [39]. We additionally report token-level F1, ROUGE-L, and BERTScore.

_c) Statistical Testing.:_ All pairwise method comparisons use paired bootstrap tests ( _B_ = 10 _,_ 000) with Bonferroni correction, reporting significance at _p <_ 0 _._ 05.

## _D. Experimental Setup_

_a) Infrastructure.:_ BM25 scoring and FAISS index construction run locally on an Apple Silicon Mac. Embedding generation, query expansion, and neural reranking are served through Azure AI Foundry endpoints using text-embedding-3-large, GPT-4.1-mini, and Cohere Rerank v4.0 Pro respectively.

_b) Document Representation.:_ In our main experiments each of the 7,318 documents is indexed as a single unit without chunking. Documents average 920 tokens, well within the context window of all models used. This isolates the effect of the retrieval method from chunking and segmentation decisions. Chunking ablations are reported in Section IV-C.

_c) Reproducibility.:_ We fix random seed 42 for all stochastic components. LLM generation uses temperature 0 throughout. All configurations, prompts, and evaluation scripts are versioned in our public code repository [43]. The dataset is used without modification with the standard train/test split from the original authors [39].

[page 4]

## IV. RESULTS

## _A. Main Retrieval Results_

Table I presents the retrieval performance of all evaluated methods on the full T[2] -RAGBench test set (23,088 queries over 7,318 documents).

The two-stage pipeline of hybrid retrieval followed by neural reranking (Hybrid + Cohere Rerank) dominates all single-stage methods by a wide margin: Recall@5 of 0.816 compared to 0.695 for Hybrid RRF alone (+17.4%), 0.644 for BM25 (+26.7%), and 0.587 for dense retrieval (+39.0%). The reranker’s cross-encoder architecture provides fine-grained query-document relevance scoring that dramatically improves ranking precision, with MRR@3 jumping from 0.433 to 0.605 (+39.7% relative).

Among first-stage retrievers, BM25 outperforms dense retrieval (text-embedding-3-large) on all metrics except Recall@20, where they are nearly tied (0.797 vs. 0.798). This suggests that lexical matching is particularly effective for financial documents, where precise terminology (company names, metric labels, fiscal periods) provides strong retrieval signals that semantic embeddings may dilute.

HyDE underperforms even vanilla dense retrieval across all metrics (Recall@5: 0.544 vs. 0.587), confirming the finding of Strich et al. [39]. Financial questions require precise numerical reasoning; LLM-generated hypothetical documents introduce noise by hallucinating plausible but incorrect financial figures, pulling the embedding away from the true relevant context.

Contextual Retrieval [20] improves both dense (+2.8pp Recall@5) and hybrid (+2.2pp) retrieval by prepending LLMgenerated context summaries to each document at indexing time. This consistent improvement confirms that financial documents benefit from explicit metadata enrichment (company name, reporting period, key metrics).

CRAG achieves Recall@5 of 0.658, improving over BM25 (+1.4pp) through adaptive query correction. Notably, 63% of queries (14,569/23,088) triggered the correction pathway, indicating that initial retrieval frequently returns suboptimal results on this benchmark. However, CRAG falls short of simple hybrid fusion (0.695), suggesting that query rewriting alone cannot match the complementary strengths of sparse and dense retrieval.

Multi-query retrieval with RAG-Fusion [19] provides negligible improvement over BM25 (Recall@5: 0.640 vs. 0.644). Financial queries are already specific and well-formed; generating alternative phrasings does not meaningfully increase recall, confirming the production-scale finding of diminishing returns for multi-query approaches on structured domain queries.

_a) Per-Subset Analysis.:_ Table II breaks down performance by dataset subset.

TAT-DQA emerges as the most challenging subset across all methods (Recall@5: 0.647 for the best method vs. 0.755 for ConvFinQA), likely due to its emphasis on diverse numerical operations over complex table layouts. Hybrid fusion provides the largest absolute improvement on TAT-DQA (+8.1 percent-

age points Recall@5 over BM25), suggesting that combining lexical and semantic signals is especially valuable for tableheavy questions.

_b) Recall@k Curves.:_ Figure 1 shows the recall-depth trade-off across all methods. Hybrid RRF maintains a consistent advantage at every value of _k_ , with the gap widening at lower _k_ values where ranking precision matters most.

Figure 2 provides a side-by-side comparison across all primary metrics. BM25 outperforms dense retrieval on every metric, while hybrid RRF achieves the best scores across the board.

_c) Subset-Level Patterns.:_ Figure 3 visualizes the Recall@5 performance across methods and dataset subsets. ConvFinQA is the easiest subset for all methods, while TATDQA presents the greatest challenge. The performance gap between methods is most pronounced on TAT-DQA, where hybrid fusion yields the largest relative gain.

All pairwise differences between BM25, dense, and hybrid RRF are statistically significant ( _p <_ 0 _._ 001, paired bootstrap test with _B_ = 10 _,_ 000, Bonferroni-corrected).

## _B. End-to-End Generation Results_

To assess whether improved retrieval translates to improved answer quality, we run end-to-end generation with GPT-4.1mini and GPT-5.4 using the top-5 retrieved documents as context. Table III reports Number Match (NM) with scaleinvariant evaluation.

Better retrieval consistently leads to better answer quality (BM25: 0.251 _→_ Hybrid: 0.282 _→_ Oracle: 0.350 with GPT4.1-mini), confirming the critical role of retrieval in RAG pipelines. GPT-5.4 improves over GPT-4.1-mini by 6–7 percentage points on identical retrieval outputs, demonstrating that both retrieval quality and LLM capability contribute independently to end-to-end performance.

## _C. Ablation Studies_

_a) Fusion method.:_ We compare Reciprocal Rank Fusion (RRF) with Convex Combination (CC) at varying parameters (Figure 5). CC with _α_ = 0 _._ 5 (equal weighting of BM25 and dense scores) achieves Recall@5 of 0.726, outperforming RRF ( _k_ = 60) at 0.695. Among RRF variants, lower _k_ values emphasize top-ranked documents more aggressively; _k_ = 10 achieves the best RRF performance (0.716). Both findings suggest that balanced fusion of sparse and dense signals is optimal for this benchmark.

_b) Reranker depth.:_ We vary the number of candidates passed to the cross-encoder reranker (Figure 6). With only 20 candidates, reranking is ineffective (Recall@5: 0.458), as relevant documents are often not in the candidate pool. Performance increases sharply at 50 candidates (0.826) and continues to improve at 100 (0.888). Increasing the number of returned results from 10 to 20 provides marginal gains (0.826 _→_ 0.878), suggesting that the top-10 already captures most relevant documents after reranking.

[page 5]

|**Category**|**Method**|**R@1**|**R@3**|**R@5**|**R@10**|**MRR@3**|**nDCG@10**|**MAP**|
|---|---|---|---|---|---|---|---|---|
|Single-method|BM25 (sparse)<br>Dense (text-embed-3-large)|0.293<br>0.248|0.552<br>0.481|0.644<br>0.587|0.735<br>0.703|0.411<br>0.351|0.515<br>0.466|0.449<br>0.398|
|Query expansion|HyDE (gpt-4.1-mini)<br>Multi-Query + RRF|0.221<br>0.283|0.441<br>0.539|0.544<br>0.640|0.671<br>0.734|0.318<br>0.397|0.433<br>0.506|0.365<br>0.439|
|Index augment.|Contextual Dense<br>Contextual Hybrid|0.266<br>0.327|0.508<br>0.610|0.615<br>0.717|0.732<br>0.818|0.373<br>0.454|0.490<br>0.571|0.420<br>0.497|
|Adaptive|CRAG (gpt-4.1-mini)|0.302|0.556|0.658|0.788|0.415|0.536|0.456|
|Fusion|Hybrid (BM25+Dense, RRF)<br>Hybrid + Cohere Rerank|0.308<br>**0.472**|0.588<br>**0.758**|0.695<br>**0.816**|0.801<br>**0.861**|0.433<br>**0.605**|0.551<br>**0.683**|0.477<br>**0.625**|

TABLE I

MAIN RETRIEVAL RESULTS ON T[2] -RAGBENCH (23,088 QUERIES, 7,318 DOCUMENTS). METHODS ARE GROUPED BY CATEGORY. HYBRID RRF WITH CROSS-ENCODER RERANKING DOMINATES ALL METHODS. CONTEXTUAL HYBRID OUTPERFORMS VANILLA HYBRID RRF. CRAG PROVIDES MODERATE GAINS THROUGH ADAPTIVE QUERY CORRECTION. HYDE UNDERPERFORMS VANILLA DENSE RETRIEVAL. ALL PAIRWISE DIFFERENCES BETWEEN ADJACENT METHODS ARE STATISTICALLY SIGNIFICANT ( _p <_ 0 _._ 001). BEST RESULTS IN **BOLD** .

**==> picture [516 x 201] intentionally omitted <==**

**----- Start of picture text -----**<br>
0.9<br>0.8<br>0.7<br>0.6<br>0.5<br>0.4<br>HyDE Multi-Query Hybrid RRF<br>0.3<br>Dense BM25 Ctx Hybrid<br>0.2 Ctx Dense CRAG Hybrid+Rerank<br>1 3 5 10 20<br>k<br>Recall@k<br>**----- End of picture text -----**<br>

Fig. 1. Recall@ _k_ curves for BM25, dense (text-embedding-3-large), and hybrid RRF retrieval. Hybrid fusion consistently outperforms both single-method baselines, with the largest gains at small _k_ .

|**Subset**|**Method**|**R@5**|**R@10**|**MRR@3**|
|---|---|---|---|---|
||BM25|0.729|0.834|0.389|
|FinQA|Dense|0.611|0.748|0.308|
||Hybrid|**0.737**|**0.856**|**0.389**|
||BM25|0.696|0.781|0.500|
|ConvFinQA|Dense|0.654|0.781|0.410|
||Hybrid|**0.754**|**0.850**|**0.519**|
||BM25|0.566|0.649|0.400|
|TAT-DQA|Dense|0.549|0.647|0.364|
||Hybrid|**0.647**|**0.746**|**0.438**|

|**Retrieval**|**GPT-4.1-mini**|**GPT-5.4**|
|---|---|---|
|BM25|0.251|_†_|
|Dense|0.257|_†_|
|Hybrid RRF|0.282|0.346|
|Oracle|0.350|0.403|

TABLE III

END-TO-END NUMBER MATCH (NM) BY RETRIEVAL METHOD AND LLM. BETTER RETRIEVAL CONSISTENTLY LEADS TO BETTER GENERATION QUALITY. GPT-5.4 OUTPERFORMS GPT-4.1-MINI BY 6–7PP ON THE SAME RETRIEVAL. _[†]_ NOT EVALUATED.

TABLE II

PER-SUBSET RETRIEVAL RESULTS. TAT-DQA IS THE MOST CHALLENGING SUBSET ACROSS ALL METHODS. HYBRID RRF PROVIDES THE LARGEST IMPROVEMENT ON TAT-DQA (+8.1PP RECALL@5 OVER BM25).

## _D. Error Analysis_

To understand retrieval failures, we analyze the 7,188 queries (31.1%) where the gold document does not appear in the hybrid RRF top-5. We sample 100 failure cases and categorize them using GPT-5.4 into five failure modes (Table IV).

The dominant failure mode is **table structure mismatch** (73%): the answer resides in a table whose markdown rep-

[page 6]

**![page 6, image 1](../assets/doc-002-page06-img1.png)**

**----- Start of picture text -----**<br>
HyDE Ctx Dense BM25 Hybrid RRF Hybrid+Rerank<br>Dense Multi-Query CRAG Ctx Hybrid<br>0.8<br>0.6<br>0.4<br>0.2<br>0.0<br>R@5 R@10 MRR@3 nDCG@10 MAP<br>Score<br>**----- End of picture text -----**<br>

Fig. 2. Grouped comparison of retrieval methods across five metrics. Hybrid RRF (green) dominates, while BM25 (blue) outperforms dense retrieval (orange) on this financial text-and-table benchmark.

**![page 6, image 2](../assets/doc-002-page06-img2.png)**

**----- Start of picture text -----**<br>
HyDE 0.619 0.562 0.508<br>Dense 0.654 0.611 0.549 0.90<br>0.85<br>Ctx Dense 0.687 0.656 0.563<br>0.80<br>Multi-Query 0.715 0.674 0.592 0.75<br>0.70<br>BM25 0.696 0.729 0.566<br>0.65<br>CRAG 0.726 0.697 0.609 0.60<br>0.55<br>Hybrid RRF 0.754 0.737 0.647<br>0.50<br>Ctx Hybrid 0.756 0.777 0.660 0.45<br>Hybrid+Rerank 0.874 0.860 0.766<br>ConvFinQA FinQA TAT-DQA<br>**----- End of picture text -----**<br>

Fig. 3. Recall@5 heatmap across retrieval methods and dataset subsets. Darker colors indicate higher retrieval quality. TAT-DQA is consistently the most challenging subset.

resentation does not embed well as continuous text. Standard embedding models struggle to match queries like “What was net income in 2019?” to tabular rows where “net income” and “2019” appear in separate cells. **Numerical reasoning** failures (20%) occur when the question requires computation (e.g., year-over-year change) rather than direct lookup.

Per-subset failure rates confirm TAT-DQA as the hardest

**==> picture [253 x 194] intentionally omitted <==**

**----- Start of picture text -----**<br>
0.38<br>r = 0.980<br>0.36<br>0.34<br>0.32<br>0.30<br>0.28 Dense<br>BM25<br>0.26<br>Hybrid RRF<br>0.24 Oracle<br>0.6 0.7 0.8 0.9 1.0<br>Retrieval Recall@5<br>Generation Number Match<br>**----- End of picture text -----**<br>

Fig. 4. Correlation between retrieval quality (Recall@5) and generation quality (Number Match). The strong positive correlation ( _r >_ 0 _._ 99) confirms that better retrieval leads to better answers.

subset (35.6% failure rate vs. 27.2% for FinQA and 26.0% for ConvFinQA), consistent with its emphasis on diverse numerical operations. Among failures, 71.0% of gold documents appear in _neither_ the dense nor BM25 top-5, indicating that these are genuinely hard retrieval cases rather than fusion artifacts.

## V. DISCUSSION

Our results reveal several actionable insights for practitioners building RAG systems over heterogeneous text-and-table documents.

[page 7]

**==> picture [516 x 185] intentionally omitted <==**

**----- Start of picture text -----**<br>
Convex Combination: Effect of  RRF: Effect of k Parameter<br>R@5<br>0.7 MRR@3<br>0.6<br>0.5<br>0.4<br>0.3 0.4 0.5 0.6 0.7 0.8 0.9 20 40 60 80 100<br> (dense weight) k (RRF smoothing)<br>Score<br>**----- End of picture text -----**<br>

Fig. 5. Fusion method ablation. Left: Convex Combination with varying _α_ (dense weight); _α_ = 0 _._ 5 is optimal. Right: RRF with varying _k_ ; lower _k_ yields slightly better results.

**==> picture [253 x 193] intentionally omitted <==**

**----- Start of picture text -----**<br>
R@5<br>0.8 MRR@3<br>0.6<br>0.4<br>0.2<br>0.0<br>20 10 50 5 50 10 50 20 100 10<br>Candidates   Top-N<br>Score<br>**----- End of picture text -----**<br>

Fig. 6. Reranker depth ablation. More candidates yield better results, with a critical threshold at 50. Format: candidates _→_ top-N returned.

|**Failure Category**|**%**|
|---|---|
|Table structure mismatch<br>Numerical reasoning<br>Vocabulary mismatch<br>Ambiguous query|73<br>20<br>5<br>1|
|Long document|1|

TABLE IV FAILURE MODE CATEGORIZATION ( _n_ =100 SAMPLED FAILURES FROM HYBRID RRF TOP-5). TABLE STRUCTURE MISMATCH IS THE DOMINANT FAILURE MODE.

_a) Reranking is the single most impactful component.:_ Adding a cross-encoder reranker (Cohere Rerank v4.0 Pro) to hybrid retrieval yields the largest improvement in our study: +17.2 percentage points MRR@3 and +12.1pp Recall@5 over unreranked hybrid retrieval. This two-stage pipeline (broad

recall via hybrid fusion, then precise reranking) is the clear recommended architecture for production RAG on text-andtable documents. The cost of the reranking stage is modest: at 300K tokens per minute, the Cohere endpoint processes the full 23K-query benchmark in approximately one hour.

_b) Hybrid fusion consistently outperforms single-method retrieval.:_ Combining BM25 and dense retrieval via Reciprocal Rank Fusion improves over both constituent methods across all metrics and all dataset subsets. The improvement is largest on TAT-DQA (+8.1pp Recall@5 over BM25), where diverse numerical operations benefit from both lexical precision and semantic understanding. We recommend hybrid retrieval as the minimum viable baseline for any RAG deployment.

_c) BM25 remains strong for financial documents.:_ On every metric except Recall@20, BM25 outperforms dense retrieval with text-embedding-3-large, one of the strongest commercial embedding models available in 2026. Financial documents contain precise, domain-specific terminology (company names, ticker symbols, standardized metric labels) that lexical matching captures effectively. This finding challenges the common assumption that dense retrieval universally dominates sparse methods and underscores the importance of domain-specific evaluation.

_d) HyDE is counterproductive for numerical financial QA.:_ Hypothetical Document Embeddings consistently underperform vanilla dense retrieval on T[2] -RAGBench, confirming the findings of Strich et al. [39]. We attribute this to the nature of financial questions: they require precise numerical values that LLMs cannot reliably generate. The produced pseudo-documents introduce noise by fabricating plausible but incorrect financial figures, pulling the query embedding away from the true relevant context. Practitioners should avoid HyDE for domains where factual precision dominates over semantic similarity.

_e) Practical recommendations.:_ Based on our findings, we propose the following decision framework for RAG re-

[page 8]

trieval on text-and-table documents:

- 1) **Start with hybrid retrieval** (BM25 + dense, RRF fusion) as the baseline.

- 2) **Add a cross-encoder reranker** for maximum quality; this provides the largest single improvement.

- 3) **Apply contextual retrieval** at indexing time for consistent moderate gains at one-time cost.

- 4) **Avoid HyDE** for domains with precise numerical or entity-centric queries.

- 5) **Evaluate on domain-specific data** ; MTEB/BEIR rankings do not predict financial retrieval performance.

_f) Limitations.:_ Our study has several limitations. First, T[2] -RAGBench covers only financial documents; our findings may not generalize to other domains with different text-table distributions such as scientific papers or medical records. Second, all answers in the benchmark are numerical, which biases evaluation toward Number Match and limits our ability to assess generation quality for free-form answers. Third, we perform whole-document retrieval (average 920 tokens) rather than passage-level chunking; performance patterns may differ for chunked corpora. Fourth, our study uses a single embedding model (text-embedding-3-large) for the main experiments; comparing multiple embedding models remains important future work. Finally, API-based models introduce a dependency on external services whose behaviour may change over time, potentially affecting reproducibility.

## VI. CONCLUSION

We presented a comprehensive benchmark of RAG retrieval methods on T[2] -RAGBench, evaluating ten retrieval strategies from classical BM25 to Corrective RAG across 23,088 queries over 7,318 text-and-table documents. Our key finding is that a two-stage pipeline of hybrid retrieval with neural reranking achieves the best performance (Recall@5 = 0.816, MRR@3 = 0.605), outperforming all single-stage methods by a wide margin.

We further demonstrate that BM25 outperforms dense retrieval on this benchmark; contextual retrieval provides consistent gains through document-level enrichment; CRAG’s adaptive correction helps but cannot match hybrid fusion; and query expansion methods (HyDE, multi-query) provide limited benefit for precise numerical queries. Ablation studies reveal that fusion method choice (CC vs. RRF) and reranker candidate depth significantly impact performance. All differences are statistically significant ( _p <_ 0 _._ 001).

Future work includes evaluating ColBERT late interaction, RAPTOR tree-based retrieval, chunking strategy ablations, multiple embedding model comparisons, and extending the benchmark to non-financial domains to assess generalizability of our findings.

## ACKNOWLEDGMENT

We thank Christopher Mierbach and Radiate for generously providing Azure AI compute credits that made the large-scale experiments in this work possible.

## REFERENCES

- [1] A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, L. Kaiser, and I. Polosukhin, “Attention is all you need,” 2023. [Online]. Available: https://arxiv.org/abs/1706.03762

- [2] J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova, “Bert: Pre-training of deep bidirectional transformers for language understanding,” 2019. [Online]. Available: https://arxiv.org/abs/1810.04805

- [3] P. Lewis, E. Perez, A. Piktus, F. Petroni, V. Karpukhin, N. Goyal, H. K¨uttler, M. Lewis, W.-t. Yih, T. Rockt¨aschel _et al._ , “Retrievalaugmented generation for knowledge-intensive nlp tasks,” _Advances in Neural Information Processing Systems_ , vol. 33, 2020.

- [4] N. Thakur, N. Reimers, A. R¨uckl´e, A. Srivastava, and I. Gurevych, “Beir: A heterogeneous benchmark for zero-shot evaluation of information retrieval models,” _Proceedings of NeurIPS Datasets Track_ , 2021.

- [5] T. Formal, B. Piwowarski, and S. Clinchant, “Splade: Sparse lexical and expansion model for first stage ranking,” _Proceedings of SIGIR_ , 2021.

- [6] M. Doshi, V. Kumar, R. Murthy, V. P, and J. Sen, “Mistral-splade: LLMs for better learned sparse retrieval,” _arXiv preprint arXiv:2408.11119_ , 2024.

- [7] V. Karpukhin, B. O˘guz, S. Min, P. Lewis, L. Wu, S. Edunov, D. Chen, and W.-t. Yih, “Dense passage retrieval for open-domain question answering,” in _Proceedings of EMNLP_ , 2020, pp. 6769–6781.

- [8] L. Wang, N. Yang, X. Huang, B. Jiao, L. Yang, D. Jiang, R. Majumder, and F. Wei, “Text embeddings by weakly-supervised contrastive pretraining,” _arXiv preprint arXiv:2212.03533_ , 2022.

- [9] L. Wang, N. Yang, X. Huang, L. Yang, R. Majumder, and F. Wei, “Improving text embeddings with large language models,” in _Proceedings of ACL_ , 2024, pp. 11 897–11 916.

- [10] J. Chen, S. Xiao, P. Zhang, K. Luo, D. Lian, and Z. Liu, “Bge m3-embedding: Multi-lingual, multi-functionality, multi-granularity text embeddings through self-knowledge distillation,” _arXiv preprint arXiv:2402.03216_ , 2024.

- [11] N. Muennighoff, N. Tazi, L. Magne, and N. Reimers, “MTEB: Massive text embedding benchmark,” in _Proceedings of EACL_ , 2023, pp. 2014– 2037.

- [12] K. Enevoldsen, N. Muennighoff, N. Tazi, E. Huang, N. Reimers _et al._ , “MMTEB: Massive multilingual text embedding benchmark,” in _Proceedings of ICLR_ , 2025.

- [13] K. Santhanam, O. Khattab, J. Saad-Falcon, C. Potts, and M. Zaharia, “Colbertv2: Effective and efficient retrieval via lightweight late interaction,” in _Proceedings of NAACL_ , 2022.

- [14] R. Sturua, I. Mohr, M. K. Akram, M. G¨unther, B. Wang, M. Krimmel, S. Wang, N. Xiao, Q. Lyu _et al._ , “Jina-colbert-v2: A general-purpose multilingual late interaction retriever,” _arXiv preprint arXiv:2408.16672_ , 2024.

- [15] G. V. Cormack, C. L. Clarke, and S. Buettcher, “Reciprocal rank fusion outperforms condorcet and individual rank learning methods,” in _Proceedings of SIGIR_ , 2009.

- [16] S. Li, L. Stenzel, C. Eickhoff, and S. A. Bahrainian, “Enhancing retrieval-augmented generation: A study of best practices,” in _Proceedings of COLING_ , 2025, pp. 6705–6717.

- [17] Y. Gao, Y. Xiong, X. Gao, K. Jia, J. Pan, Y. Bi, Y. Dai, J. Sun, and H. Wang, “Retrieval-augmented generation for large language models: A survey,” _arXiv preprint arXiv:2312.10997_ , 2024.

- [18] L. Gao, X. Ma, J. Lin, and J. Callan, “Precise zero-shot dense retrieval without relevance labels,” _Proceedings of ACL_ , 2023.

- [19] A. Raudaschl, “Rag-fusion: A new take on retrieval-augmented generation,” _arXiv preprint arXiv:2402.03367_ , 2024.

- [20] Anthropic, “Introducing contextual retrieval,” https://www.anthropic. com/news/contextual-retrieval, 2024.

- [21] D. Vake, J. Viˇciˇc, and A. Toˇsi´c, “Bridging the question–answer gap in retrieval-augmented generation: Hypothetical prompt embeddings,” _IEEE Access_ , 2025.

- [22] M. G¨unther and I. Mohr, “Late chunking: Contextual chunk embeddings using long-context embedding models,” _arXiv preprint arXiv:2409.04701_ , 2024.

- [23] P. Sarthi, S. Abdullah, A. Tuli, S. Khanna, A. Goldie, and C. D. Manning, “Raptor: Recursive abstractive processing for tree-organized retrieval,” _Proceedings of ICLR_ , 2024.

- [24] D. Edge, H. Trinh, N. Cheng, J. Bradley, A. Chao, A. Mody, S. Truitt, and J. Larson, “From local to global: A graph rag approach to queryfocused summarization,” _arXiv preprint arXiv:2404.16130_ , 2024.

[page 9]

- [25] A. Asai, Z. Wu, Y. Wang, A. Sil, and H. Hajishirzi, “Self-rag: Learning to retrieve, generate, and critique through self-reflection,” _Proceedings of ICLR_ , 2024.

- [26] S.-Q. Yan, J.-C. Gu, Y. Zhu, and Z.-H. Ling, “Corrective retrieval augmented generation,” _arXiv preprint arXiv:2401.15884_ , 2024.

- [27] W. Chen, H. Zha, Z. Chen, W. Xiong, H. Wang, and W. Y. Wang, “HybridQA: A dataset of multi-hop question answering over tabular and textual data,” in _Findings of EMNLP_ , 2020, pp. 1026–1036.

- [28] W. Chen, M.-W. Chang, E. Schlinger, W. Y. Wang, and W. W. Cohen, “Open question answering over tables and text,” in _Proceedings of ICLR_ , 2021.

- [29] Z. Chen, W. Chen, C. Smiley, S. Shah, I. Borber, C. P. Langlotz _et al._ , “FinQA: A dataset of numerical reasoning over financial data,” in _Proceedings of EMNLP_ , 2021, pp. 3697–3711.

- [30] F. Zhu, W. Lei, Y. Huang, C. Wang, S. Zhang, J. Lv, F. Feng, and T.S. Chua, “TAT-QA: A question answering benchmark on a hybrid of tabular and textual content in finance,” in _Proceedings of ACL_ , 2021, pp. 3277–3287.

- [31] Z. Chen, S. Li, C. Smiley, Z. Ma, S. Shah, and W. Y. Wang, “ConvFinQA: Exploring the chain of numerical reasoning in conversational finance question answering,” in _Proceedings of EMNLP_ , 2022, pp. 6279– 6292.

- [32] L. Nan, M. Zhang, H. Zhao _et al._ , “Table question answering in the era of large language models: A comprehensive survey of tasks, methods, and evaluation,” _arXiv preprint arXiv:2510.09671_ , 2025.

- [33] F. Petroni, A. Piktus, A. Fan, P. Lewis, M. Yazdani, N. De Cao, J. Thorne, Y. Jernite, V. Karpukhin, J. Maillard, V. Plachouras, T. Rockt¨aschel, and S. Riedel, “KILT: A benchmark for knowledge intensive language tasks,” in _Proceedings of NAACL_ , 2021, pp. 2523– 2544.

- [34] J. Chen, H. Lin, X. Han, and L. Sun, “Benchmarking large language models in retrieval-augmented generation,” in _Proceedings of AAAI_ , 2024, pp. 17 754–17 762.

- [35] X. Yang, K. Sun, H. Xin, Y. Sun, N. Bhalla, X. Chen, S. Choudhary, R. D. Gui, Z. W. Jiang, Z. Jiang _et al._ , “CRAG – comprehensive RAG benchmark,” in _Proceedings of NeurIPS Datasets and Benchmarks Track_ , 2024.

- [36] R. Friel, M. Belyi, and A. Sanyal, “RAGBench: Explainable benchmark for retrieval-augmented generation systems,” _arXiv preprint arXiv:2407.11005_ , 2024.

- [37] S. Es, J. James, L. Espinosa-Anke, and S. Schockaert, “Ragas: Automated evaluation of retrieval augmented generation,” _Proceedings of EACL Workshop_ , 2024.

- [38] J. Saad-Falcon, O. Khattab, C. Potts, and M. Zaharia, “ARES: An automated evaluation framework for retrieval-augmented generation systems,” in _Proceedings of NAACL_ , 2024.

- [39] J. Strich, E. K. Isgorur, M. Trescher, C. Biemann, and M. Semmann, “T[2] -ragbench: Text-and-table benchmark for evaluating retrievalaugmented generation,” _Proceedings of EACL_ , 2026.

- [40] S. E. Robertson and S. Walker, “Some simple effective approximations to the 2-poisson model for probabilistic weighted retrieval,” _Proceedings of SIGIR_ , pp. 232–241, 1994.

- [41] Cohere, “Rerank 4.0 pro,” https://cohere.com/blog/rerank-4, 2025.

- [42] R. Nogueira and K. Cho, “Passage re-ranking with BERT,” in _arXiv preprint arXiv:1901.04085_ , 2019.

- [43] M. Akarsu, C. Mierbach, and R. K. Karaman, “Optimizing retrievalaugmented generation: Code and data,” https://doi.org/10.5281/zenodo. 19382814, 2026.

## APPENDIX A

## HYPERPARAMETER DETAILS AND FULL RESULTS

Table V lists all hyperparameters used in each retrieval method. Unless otherwise noted, parameters follow the values in our configuration file (configs/default.yaml) and were held constant across all experiments. Table VI presents the complete set of retrieval metrics for all evaluated methods.

[page 10]

|**Method**|**Parameter**|**Value**|**Notes**|
|---|---|---|---|
||_k_1|1.2|Term-frequency saturation|
|BM25|_b_|0.75|Document-length normalization|
||Tokenizer|whitespace split|Via rank_bm25 library|
||Embedding model|text-embedding-3-large|OpenAI via Azure AI Foundry|
|Dense Retrieval|Dimensions|3,072|Full dimensionality, no reduction|
||Index type|FAISS IndexFlatIP|Exact inner-product (cosine) search|
||RRF _k_|60|Default smoothing constant|
|Hybrid RRF|RRF _k_ (ablation)|10, 30, 100|Tested in fusion ablation (§IV-C)|
||BM25 / Dense weights|0.5 / 0.5|Equal contribution from both retrievers|
|Hybrid CC|_α_ (dense weight)<br>_α_ (ablation)|0.5<br>0.3, 0.7, 0.9|Optimal in ablation<br>Tested in fusion ablation (§IV-C)|
||Model|Cohere-rerank-v4.0-pro|Azure AI Foundry endpoint|
|Cohere Rerank|top<br>n returned|10|Documents returned after reranking|
||Candidate pool|50|Documents passed to reranker from first stage|
||LLM|gpt-4.1-mini|Hypothetical document generation|
|HyDE|Temperature<br>Max tokens|0.7<br>150|Default in retriever; 0 used in main experiments<br>Per hypothetical passage|
||Num. generations|1|Single hypothetical document per query|
||LLM|gpt-4.1-mini|Query variant generation|
|Multi-Query|Num. variants<br>Temperature|3<br>0.7|Plus original query = 4 total retrievals<br>Default in retriever; 0 used in main experiments|
||RRF _k_ (fusion)|60|For merging variant result lists|
||LLM (evaluation)|gpt-4.1-mini|Relevance classifcation|
|CRAG|Eval. temperature<br>LLM (rewriting)|0.0<br>gpt-4.1-mini|Deterministic relevance judgments<br>Query correction / rewriting|
||Rewrite temperature|0.5|Moderate diversity in rewrites|
||LLM|gpt-4.1-mini|Context summary generation|
|Contextual Retrieval|Temperature|0.0|Deterministic context summaries|
||Max tokens|100|Per context prefx|
||Random seed|42|All stochastic components|
|Global|Top-_k_ values<br>Bootstrap _B_|1, 3, 5, 10, 20<br>10,000|Evaluated across all methods<br>Significance testing|
||Significance|_p <_ 0_._05|Bonferroni-corrected|

## TABLE V

COMPLETE HYPERPARAMETER SETTINGS FOR ALL RETRIEVAL METHODS. ALL LLM CALLS USE G P T-4.1-M I N I VIA AZURE AI FOUNDRY. EMBEDDING USES T E X T-E M B E D D I N G-3-L A R G E (3,072 DIMENSIONS) FOR ALL DENSE COMPONENTS.

|**Method**|**R@1**|**R@3**|**R@5**|**R@10**|**R@20**|**MRR@3**|**MRR@5**|**nDCG@5**|**nDCG@10**|**MAP**|
|---|---|---|---|---|---|---|---|---|---|---|
|HyDE|0.221|0.441|0.544|0.671|0.767|0.318|0.341|0.392|0.433|0.365|
|Dense|0.248|0.481|0.587|0.703|0.798|0.351|0.375|0.428|0.466|0.398|
|Contextual Dense|0.266|0.508|0.615|0.732|0.817|0.373|0.398|0.452|0.490|0.420|
|Multi-Query|0.283|0.539|0.640|0.734|0.820|0.397|0.420|0.475|0.506|0.439|
|BM25|0.293|0.552|0.644|0.735|0.797|0.411|0.432|0.485|0.515|0.449|
|CRAG|0.302|0.556|0.658|0.788|0.788|0.415|0.439|0.493|0.536|0.456|
|Hybrid RRF|0.308|0.588|0.695|0.801|0.877|0.433|0.457|0.517|0.551|0.477|
|Contextual Hybrid|0.327|0.610|0.717|0.818|0.887|0.454|0.478|0.538|0.571|0.497|
|Hybrid + Rerank|**0.472**|**0.758**|**0.816**|**0.861**|_∗_|**0.605**|**0.618**|**0.669**|**0.683**|**0.625**|

TABLE VI

FULL RETRIEVAL RESULTS FOR ALL METHODS AND METRICS ON T[2] -RAGBENCH (23,088 QUERIES, 7,318 DOCUMENTS). METHODS ARE SORTED BY NDCG@10 IN ASCENDING ORDER. BEST RESULTS IN **BOLD** . _[∗]_ HYBRID + RERANK RETURNS AT MOST 10 DOCUMENTS, SO R@20 IS NOT APPLICABLE.

[page 11]

## APPENDIX B

## PROMPT TEMPLATES

This appendix documents the exact prompt templates used in all LLM-dependent retrieval methods and the generation stage. All prompts use gpt-4.1-mini via Azure AI Foundry.

## _A. Generation Prompt (Answer Extraction)_

Used to extract the final answer from retrieved context during end-to-end evaluation.

Answer the following question based ONLY on the provided context. If the answer is a number, provide just the number. If you cannot answer from the context, say "UNANSWERABLE".

Context: {context}

Question: {question}

Answer:

## _B. HyDE Prompt (Hypothetical Document Generation)_

Used to generate a hypothetical answer passage whose embedding replaces the query embedding for dense retrieval.

Given the following question about financial data, write a short passage that would contain the answer. Include specific numbers and financial terms. Question: {query} Passage:

_Fallback prompt_ (used when the config template is not provided):

Please write a short passage that directly answers the following question. The passage should be factual, detailed, and roughly the length of a typical encyclopedia paragraph.

Question: {query}

Passage:

## _C. Multi-Query Prompt (Query Variant Generation)_

Used to generate semantically diverse reformulations of the original query. The original query plus all variants are retrieved independently and merged via RRF.

You are a helpful assistant that generates alternative search queries. Given the following question, generate {n} alternative phrasings that capture the same information need but use different wording or perspectives. Return each query on its own line, numbered (e.g. 1. ... 2. ...). Do not include any other text.

Original question: {query}

Alternative queries:

## _D. CRAG Evaluation Prompt_

Used to classify retrieved documents as relevant, ambiguous, or irrelevant. Temperature is set to 0 for deterministic judgments.

the document’s relevance to answering the question.

Question: {query} Document: {document}

Respond with exactly one of:

- RELEVANT: The document contains information that directly helps answer the question.

- AMBIGUOUS: The document is partially relevant or tangentially related but may not fully answer the question.

- IRRELEVANT: The document does not contain useful information for answering the question.

Classification:

## _E. CRAG Rewrite Prompt_

Used to reformulate the query when retrieved documents are classified as AMBIGUOUS or IRRELEVANT. Temperature is set to 0.5 for moderate diversity.

The following question was used to search a financial document corpus, but the retrieved results were not sufficiently relevant.

Original question: {query}

Please rewrite this question to be more specific and likely to retrieve the correct financial document. Focus on including specific financial terms, company names, time periods, or metric names that would appear in the target document.

Rewritten question:

## _F. Contextual Retrieval Prompt (Context Generation)_

Used at indexing time to generate a short context prefix for each document, prepended to the text before embedding and BM25 indexing.

_Chunked mode_ (when documents are split into chunks):

Here is the full document: <document> {document} </document>

Here is a chunk from that document: <chunk> {chunk} </chunk>

Please give a short, succinct context (2-3 sentences) to situate this chunk within the overall document for the purposes of improving search retrieval of the chunk. Answer only with the context, nothing else.

_Whole-document mode_ (no chunking, as used in main experiments):

Here is a document: <document> {document} </document>

Please provide a concise summary context (2-3 sentences) that captures the key topics and entities in this document, for the purpose of improving search retrieval. Answer only with the context, nothing else.

You are a relevance evaluator. Given a question and a retrieved document, classify
