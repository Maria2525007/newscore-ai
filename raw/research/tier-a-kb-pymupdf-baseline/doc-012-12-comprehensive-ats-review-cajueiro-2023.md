---
id: doc-012
source: 12-comprehensive-ats-review-cajueiro-2023.pdf
source_type: pdf
source_sha256: 77e6ddd7682c67635827505a19b230926b49f9f8e4a7d2c404aae8e3d974a9a5
extraction_method: pymupdf4llm@unknown
extraction_date: 2026-05-26
pages: 94
headings:
  - "A comprehensive review of automatic text summarization techniques: method, data, evaluation and coding"
  - Abstract
  - Contents
  - 1 Introduction
  - 2 Classification of ATS systems
  - 3 An overview of other ATS surveys
  - 4 Datasets
  - 5 Basic topology of an ATS system
  - 6 Extractive summarization
  - 6.1 Frequency-based methods
tokens_estimated: 70956
warnings:
  - "ligatures_recovered: pymupdf4llm dropped letters from 31 word(s) with fi/ff/fl glyphs (e.g. 'Ofcial'→'Official', 'fexible'→'flexible'); fixed via the doc2kb ligature-recovery table — no manual action needed"
  - "ligature_residual: 10 suspicious word(s) with f-consonant patterns still present (sample: Dorffner, FDA, FSKD, MtfisfMTtfisf, confdence); if these are broken ligatures, extend _LIGATURE_FIXES in scripts/_common.py"
  - "dropped_pictures: pymupdf4llm omitted 26 picture(s) over 94 page(s) (0.28/page); in scientific/lab PDFs these placeholders typically hide equations, matrices, or block diagrams — body text will reference formulas that aren't in the extraction. Re-extract this PDF by reading the source file directly via the Read tool and overwrite the body with a manual transcription of the remaining figures"
---
[page 1]

# A comprehensive review of automatic text summarization techniques: method, data, evaluation and coding

Daniel O. Cajueiro[1,6,7] , Arthur G. Nery[1,7] , Igor Tavares[2] , Ma´ısa K. De Melo[3,7] , Silvia A. dos Reis[4] , Li Weigang[5] , and Victor R. R. Celestino[3,7]

> 1Department of Economics, FACE, Universidade de Bras´ılia (UnB), Campus Universit´ario Darcy Ribeiro, 70910-900, Bras´ılia, Brazil. Email: danielcajueiro@gmail.com

> 2Mechanic Engineering Department. Universidade de Bras´ılia (UnB), Campus Universit´ario Darcy Ribeiro, 70910-900, Bras´ılia, Brazil.

> 3Department of Mathematics, Instituto Federal de Minas Gerais, Campus Formiga, 35577-020, Belo Horizonte, Brazil.

> 4Business Department, FACE, Universidade de Bras´ılia (UnB), Campus Universit´ario Darcy Ribeiro, 70910-900, Bras´ılia, Brazil.

> 5Computer Science Department. Universidade de Bras´ılia (UnB), Campus Universit´ario Darcy Ribeiro, 70910-900, Bras´ılia, Brazil.

> 6Nacional Institute of Science and Technology for Complex Systems (INCT-SC). Universidade de Bras´ılia, Bras´ılia, Brazil.

> 7Machine Learning Laboratory in Finance and Organizations, FACE - Universidade de Bras´ılia (UnB), Campus Universit´ario Darcy Ribeiro, 70910-900, Bras´ılia, Brazil.

October 5, 2023

## Abstract

We provide a literature review about Automatic Text Summarization (ATS) systems. We consider a citation-based approach. We start with some popular and well-known papers that we have in hand about each topic we want to cover and we have tracked the “backward citations” (papers that are cited by the set of papers we knew beforehand) and the “forward citations” (newer papers that cite the set of papers we knew beforehand). In order to organize the different methods, we present the diverse approaches to ATS guided by the mechanisms they use to generate a summary. Besides presenting the methods, we also present an extensive review of the datasets available for summarization tasks and the methods used to evaluate the quality of the summaries. Finally, we present an empirical exploration of these methods using the CNN Corpus dataset that provides golden summaries for extractive and abstractive methods.

Keywords: Deep Learning, Machine Learning, Natural Language Processing, Summarization.

[page 2]

## Contents

|1|Introduction|||3|
|---|---|---|---|---|
|2|Classifcation of ATS systems|||4|
|3|An overview of other ATS surveys|||5|
|4|Datasets|||8|
|5|Basic topology of an ATS system|||15|
|6|Extractive summarization|||15|
||6.1<br>Frequency-based methods . . . . . . . . . .|.|. . . . . . . . . . . . . . . . . . . .|16|
||6.1.1<br>Vector-space-based methods . . . . .|.|. . . . . . . . . . . . . . . . . . . .|16|
||6.1.2<br>Matrix factorization based methods|.|. . . . . . . . . . . . . . . . . . . .|21|
||6.1.3<br>Graph based methods . . . . . . . .|.|. . . . . . . . . . . . . . . . . . . .|24|
||6.1.4<br>Topic-based methods . . . . . . . . .|.|. . . . . . . . . . . . . . . . . . . .|26|
||6.1.5<br>Neural word embedding based methods||. . . . . . . . . . . . . . . . . . .|28|
||6.2<br>Heuristic-based methods . . . . . . . . . . .|.|. . . . . . . . . . . . . . . . . . . .|32|
||6.3<br>Linguistic-based methods<br>. . . . . . . . . .|.|. . . . . . . . . . . . . . . . . . . .|34|
||6.4<br>Supervised machine learning-based methods|.|. . . . . . . . . . . . . . . . . . . .|37|
||6.5<br>Reinforcement learning based methods . . .|.|. . . . . . . . . . . . . . . . . . . .|41|
|7|Abstractive summarization|||44|
||7.1<br>Linguistic approaches<br>. . . . . . . . . . . .|.|. . . . . . . . . . . . . . . . . . . .|44|
||7.2<br>Sequence-to-sequence deep learning methods||. . . . . . . . . . . . . . . . . . . .|47|
|8|Compressive extractive approaches|||51|
|9|Evaluation methods|||55|
|10|Open libraries|||62|
|11|Empirical exercises|||66|
|12|Final remarks|||71|
|13|Acknowledgment|||72|

[page 3]

## 1 Introduction

Automatic Text Summarization (ATS) is the automatic process of transforming an original text document into a shorter piece of text, using techniques of Natural Language Processing (NLP), that highlights the most important information within it, according to a given criterion.

There is no doubt that one of the main uses of ATS systems is that they directly address the information overload problem (Edmunds and Morris, 2000). They allow a possible reader to understand the content of the document without having to read it entirely. Other ATS applications are keyphrase extraction (Hasan and Ng, 2014), document categorization (Brandow et al., 1995), information retrieval (Tombros and Sanderson, 1998) and question answering (Morris et al., 1992).

The seminal work in ATS systems field is due to Luhn (1958) that used an approach that mixes information about the frequency of words with some heuristics to summarize the text of scientific papers. There are several different approaches to designing ATS systems today. In this paper, we intend to present a comprehensive literature review on this topic. This is not an easy task (Bullers et al., 2018). First, there are thousands of papers, and we have to face the obvious question that is “Which set of the works should we include in this review?”. Second, the papers use very different approaches. Thus, the second important question is “How do we present these papers in a comprehensive way?”. We address the first question by adopting a citation-based approach. That means we start with a few popular[1] and well-known papers about each topic we want to cover and we track the “backward citations” (papers that are cited by the set of papers we knew beforehand) and the “forward citations” (newer papers that cite the set of papers we knew beforehand). One clear challenge of this approach is to avoid the popularity bias so common in recommendation systems (Park and Tuzhilin, 2008; Hervas-Drane, 2008; Fleder and Hosanagar, 2009). We deal with this challenge by trying to consider papers that cover different dimensions of the approach we are reviewing. In order to answer the second question, we have tried to present the diverse approaches to ATS guided by the mechanisms they use to generate a summary.

Our paper naturally relates to other reviews about this theme. We may classify these reviews in terms of classical such as Edmundson and Wyllys (1961) and Paice (1990), topicspecific such as Rahman and Borah (2015) (query-based summarization), Pouriyeh et al. (2018) (ontology-based summarization), Jalil et al. (2021) (extractive multi-document summarization) and Alomari et al. (2022) (deep learning approaches to summarization), and general reviews like ours such as Mridha et al. (2021) and El-Kassas et al. (2021). Although these latter works are very related to ours in terms of general content, the presentation of our work is very different. The models and mechanisms used to build such summaries drive our presentation. Thus, our focus on models and mechanisms used in automatic text summarization aims to provide practical guidance for researchers or practitioners who are developing such systems. By emphasizing these aspects of summarization, our review has the potential to offer unique insights that are not covered by other works in the field, and may help to bridge the gap between the technique used to build the model and the practical application in summarization. Furthermore, besides presenting the models used to generate the summaries, we also present the most popular datasets, a compendium of evaluation techniques, and an exploration of the public python libraries that one can use to implement the task of ATS[2] .

We organize the manuscript as follows: Section 2 presents a taxonomy used to classify ATS systems. Section 3 summarizes the content of other surveys about ATS systems. Section 4 describes the datasets used to explore ATS systems. Section 5 illustrates the basic topology of an ATS system. In Section 6, we present the approaches to extractive summarization. We

> 1The popular papers are the ones more cited in the field.

> 2The interested reader may find the complete code used to explore these libraries in the Zenodo: https://zenodo.org/record/7500273.

[page 4]

split this section into the following subsections: Subsection 6.1 presents the frequency-based methods. Subsection 6.2 presents the heuristic-based methods. Subsection 6.3 presents the linguistic-based methods. Subsection 6.4 presents the methods based on supervised machine learning models. Subsection 6.5 presents the reinforcement-learning-based approaches. Section 7 presents the approaches to abstractive summarization. We divide this section into two subsections. While Subsection 7.1 introduces the linguistic approaches, Subsection 7.2 describes the deep learning sequence-to-sequence approaches. Section 8 introduces the compressive extractive hybrid approaches. Section 9 describes the methods used to evaluate ATS systems. Section 10 presents the public libraries available in Python and Section 11 explores these libraries in the CNN Corpus dataset (Lins et al., 2019)[3] , which presents both extractive and abstractive golden summaries for every document[4] . Finally, Section 12 presents the main conclusions of this work.

## 2 Classification of ATS systems

This section presents some of the different criteria used to build a taxonomy for ATS systems (Jones, 1998; Hovy and Lim, 1999):

1. The type of output summary: We may classify a summary into extractive, abstractive and hybrid. While an extractive approach extracts from the text the most important sentences and joins them in order to form the final summary, an abstractive method extracts the main information from the text and rewrites it in new sentences to form the summary. Although humans usually summarize pieces of text in an abstractive way, this approach is more difficult for machines since it depends on a language model to rewrite the sentences. On the other hand, a hybrid approach combines ingredients of both approaches. A compressive extractive approach extracts the most relevant sentences in the first step and requires a language model in order to compress the sentences using only essential words in the second step. We begin our paper by categorizing the methods based on the type of output summary they generate. There are two important reasons for this. Firstly, these three categories represent distinct and well-established approaches to summarization, each with its own set of advantages and limitations. Secondly, datasets with golden summaries often follow a similar division into abstractive, extractive, and compressive abstractive approaches. Thus, Section 6 presents the extractive approaches, Section 7 presents the abstractive approaches and Section 8 presents the hybrid compressive extractive approaches.

2. The type of available information: We may classify a summary into indicative or informative. While the former case calls the attention of the reader to the content we may find in a text document, the objective of the latter case is to present the main findings of the text. Thus, while in the first case the summary intends to be an advertisement of the content of the text, in the second case the reader only reads the main text if he/she wants to learn more about a given result. While most approaches reviewed here and available in the literature are typically indicative, there are some examples of structured approaches that allow for retrieval of the main findings of a text. We may find an example of the informative approach in Section 7.1. For instance, Genest and Lapalme (2012) use handcrafted information extraction rules to extract the information they need to build the summary. In particular, they ask questions about the nature of the event, the time, the location and other relevant information in their context.

> 3Our rationale for selecting the CNN dataset is that it stands out as one of the few datasets that provides both extractive and abstractive reference summaries.

> 4It is common in this literature to call the reference human-made summaries as the gold-standard summaries.

[page 5]

3. The type of content: We may classify a summary into generic and query-based. While a query-based system intends to present a summary that focuses on keywords previously fed by the user, the generic summary is the opposite. Most query-based systems are minor modifications of generic ATS systems. For instance, Darling (2010), reviewed in Section 6.1.1, in a generic summarization setup, extracts the most important sentences of a document using information about the distribution of terms in the text. In order to provide a query-based approach, it adds more probability mass to the bins of the terms that arise in the query. In our work, we call the attention of the reader when the ATS intends to be a query-based system.

4. The number of input documents: We may classify the summary in terms of being a singledocument or a multi-document summary. The first case happens when the summary is built from only one document and the second case happens when the summary comes from the merging of many documents. It is worth mentioning that multi-document summarization has received growing attention due to the need to automatically summarize the exponential growth of online material that presents many documents with similar tenor. Thus, many sentences in different documents overlap with each other, increasing the need to recognize and remove redundancy.

In general, multi-document cases present a more serious problem of avoiding redundant sentences and additional difficulties in the concatenation of the sentences in the final summary. It is worth mentioning that many approaches presented in this review present an instance of the multi-document summarization task, and we call the reader’s attention when it happens.

A more recent approach to multi-document summarization is known as update summarization. The idea of update-based summarization is to generate short multi-document summaries of recent documents under the assumption that the earlier documents were previously considered. Thus, the objective of an update summary is to update the reader with new information about a particular topic and the ATS system has to decide which piece of information in the set of new documents is novel and which is redundant.

We may find another kind of multi-document summarization if we consider jointly to summarize the original document and the content generated by the users (such as comments or other online network contents) after the publication of the original document. This approach of summarization is known as social context summarization. We may find examples of social context summarization in Sections 6.1.2 and 6.4.

5. The type of method used to choose the sentences to be included in the summary: We may classify it in terms of being a supervised or an unsupervised method. This is particularly important because while in the former case we need data to train the model, in the latter case that is not necessary. Supervised methods arise in Sections 6.4, 7.2 and 8.

## 3 An overview of other ATS surveys

Table 1 presents an overview of other surveys about ATS systems. The first column presents the source document. The second column presents a summary of its content. The third column presents the date range of papers cited in the survey. The last column presents the number of papers cited in the review. The intention of the last two columns is to provide an indication of the coverage of the work.

The most complete surveys to date are the ones presented in El-Kassas et al. (2021) and Mridha et al. (2021). Like ours, they intend to cover most aspects of ATS systems. However, we may find differences among them in terms of content and presentation. Although there is no doubt that most classical papers are present in our work and also in these two works,

[page 6]

the presentation of our work is naturally model-guided. In terms of content, our work also presents additional sections that are not available elsewhere, namely Section 10 presents the main libraries available for coding ATS systems and Section 11 presents a comparison of the most popular methods of ATS systems, using a subset of the libraries presented in Section 10, and using the most popular methods to evaluate these methods presented in Section 9.

In terms of coverage, our work cites 360 references from 1958 to 2022 and it is one of the most complete surveys of the field. It is important to emphasize that the number of citations and the date range are just indicators of the coverage. Table 1 presents some very influential surveys with a much smaller number of references. We make a special reference to the amazing classical works Edmundson and Wyllys (1961), Paice (1990), Jones (1998) and the more recent works Nenkova et al. (2011) and Lloret and Palomar (2012).

[page 7]

|Source|Focus||Date range|References|
|---|---|---|---|---|
|Edmundson and Wyllys (1961)|It is an amazing survey of the early ATS systems.||1953-1960|7|
|Paice (1990)|It presents the classical extractive ATS systems.||1958-1989|52|
|Jones (1998)|It explores the context, input, purpose, and output factors necessary to develop|effective|1972-1997|26|
||approaches to ATS.||||
|Das and Martins (2007)|It presents approaches to extractive and abstractive summarization. It also presents an||1958-2007|48|
||overview of the evaluation methods.||||
|Gholamrezazadeh et al. (2009)|It reviews techniques of extractive summarization.||1989-2008|24|
|Damova and Koychev (2010)|It reviews techniques for query-based extractive summarization.||2005-2009|11|
|Gupta and Lehal (2010)|It presents a survey of extractive summarization techniques.||1958-2010|47|
|Nenkova et al. (2011)|It presents a fantastic general survey about ATS.||1958-2010|236|
|Lloret and Palomar (2012)|It presents a great overview of the theme that includes both abstractive and|also ex-|1958-2012|197|
||tractive ATS techniques. It discusses the taxonomy of ATS systems. It combines ATS||||
||systems with intelligent systems such as information retrieval systems, question-answering||||
||systems and text classifcation systems.<br>It also presents an overview of the techniques||||
||used to evaluate summaries.||||
|Kumar and Salim (2012)|It presents a survey of multi-document summarization.||1998-2012|36|
|Dalal and Malik (2013)|It presents a very short overview of the bio-inspired methods of text summarization.||1997-2011|7|
|Ferreira et al. (2013)|It presents an overview of sentence scoring techniques for extractive text summarization.||1958-2013|35|
|Munot and Govilkar (2014)|It presents the methods of extractive and abstractive summarization.||1958-2014|19|
|Mishra et al. (2014)|It reviews the works of ATS in the biomedical domain.||1969-2014|53|
|Saranyamol and Sindhu (2014)|It describes different approaches to the automatic text summarization process including||2007-2014|7|
||both extractive and abstractive methods.||||
|Rahman and Borah (2015)|It reviews techniques for query-based extractive summarization.||1994-2014|34|
|Meena and Gopalani (2015)|It presents a survey of extractive ATS systems evolutionary-based approaches.||2001-2012|16|
|Andhale and Bewoor (2016)|It presents a survey of extractive and abstractive ATS approaches.||1998-2015|66|
|Mohan et al. (2016)|It presents a survey on ontology-based abstractive summarization.||1997-2014|22|
|Moratanch and Chitrakala (2016)|It presents a survey of abstractive text summarization.||1999-2016|21|
|Jalil et al. (2021)|It presents a survey of multi-document summarization.||1989-2016|18|
|Gambhir and Gupta (2017)|It presents a very general survey of extractive and abstractive methods. It also|presents|1958-2016|186|
||a survey of evaluation methods and the results found in DUC datasets.||||
|Allahyari et al. (2017)|It presents a survey of extractive ATS approaches.||1958-2017|81|
|Bharti and Babu (2017)|It presents a very general survey of extractive and abstractive methods. It also|presents|1957-2016|132|
||a survey of available datasets used to investigate ATS systems and evaluation methods.||||
|Pouriyeh et al. (2018)|It presents an overview of the ontology-based summarization methods.||1966-2017|43|
|Dernoncourt et al. (2018)|It presents an overview of the available corpora for summarization.||1958-2018|75|
|Gupta and Gupta (2019)|It presents the methods of abstractive summarization.||2000-2018|109|
|Tandel et al. (2019)|It surveys the neural network-based abstractive text summarization approaches.||2014-2018|8|
|Klymenko et al. (2020)|It presents a general overview of summarization methods, including recent trends.||1958-2020|54|
|Awasthi et al. (2021)|It presents a general overview of summarization methods including very recent works.||2001-2021|37|
|Sheik and Nirmala (2021)|It presents an overview of deep learning for legal text summarization.||2004-2021|23|
|Mridha et al. (2021)|It presents a very general survey of extractive and full abstractive methods.|It also|1954-2021|353|
||presents a survey of available datasets used to investigate ATS systems and evaluation||||
||methods.||||
|El-Kassas et al. (2021)|It presents a very general survey of extractive and abstractive methods. It also|presents|1954-2020|225|
||a survey of available datasets used to investigate ATS systems and evaluation methods.||||
|Jalil et al. (2021)|It presents a survey of extractive multi-document summarization.||1998-2020|81|
|Alomari et al. (2022)|It presents a survey of the approaches based on deep learning, reinforcement learning and||1953-2022|205|
||transfer learning used for abstractive summarization. It also presents a survey of|datasets|||
||used in this feld, evaluation techniques and results.||||

Table 1: A representative compilation of other ATS surveys.

[page 8]

## 4 Datasets

There is today a large number of datasets that we may use to explore the task of ATS. The datasets may belong to a variaty of domains, they may be suitable to evaluate different tasks of summarization, they are in different sizes and they may present a different number of goldsummaries. For each dataset discussed in the following lines, Table 4 presents detailed information about them. This table has a total of nine columns: (1) name of the dataset; (2) language; (3) domain (e.g. news, scientific papers, reviews, etc.); (4) number of single-documents; (5) number of multi-documents; (6) number of gold-standard summaries per document in the case of single-documents; (7) number of gold-standard summaries per document in the case of multidocuments; (8) URL where we may find the dataset; and (9) the work that presents the dataset. Our primary focus is on datasets containing summaries for texts written in the English language. However, if a method referenced in this review is evaluated using a dataset with texts written in other languages, we also include this dataset in our discussion.

BIGPATENT Sharma et al. (2019) introduce the BIGPATENT dataset that provides good examples for the task of abstractive summarization. They build the dataset using Google Patents Public Datasets, where for each document there is one gold-standard summary which is the patent’s original abstract. One advantage of this dataset is that it does not present difficulties inherent to news summarization datasets, where summaries have a flattened discourse structure and the summary content arises at the beginning of the document. BillSum Kornilova and Eidelman (2019), in order to fill the gap that there is a lack of datasets that deal specifically with legislation, introduce the BillSum dataset. Their documents are bills collected from the United States Publishing Office’s Govinfo. Although the dataset focuses on the task of single-document extractive summarization, the fact that each bill is divided into multiple sections makes the problem akin to that of multi-document summarization. Each document is accompanied by a gold-standard summary and by its title.

Blog Summarization Dataset Ku et al. (2006) deal with three NLP tasks related to opinions in news and blog corpora, namely opinion extraction, tracking, and summarization. Concerning summarization, they tackle the problem from the perspective of sentiment analysis at the levels of word, sentence, and document. The authors gather blog posts that express opinions regarding the genetic cloning of the Dolly sheep and they give the task to tag the texts in each one of these levels to three annotators. A comparison of their opinions generates goldstandard words, sentences, and documents that expressed positive or negative opinions. From the categorization made by the annotators, two kinds of gold-standard summaries are generated for the set of positive/negative documents: one is simply the headline of the article with the largest amount of positive/negative sentences (brief summary) and the other is the listing of the sentences with the highest sentiment degree (detailed summary).

CAST Hasler et al. (2003) built the CAST corpus with the intention of having a more detailed dataset to be used in the task of extractive ATS. For that purpose, they provide annotations for each document signaling three types of sentences. The crucial sentences labeled as essential are those without which the text can not be fully understood. The important sentences provide important details of the text, even if they are not absolutely necessary for its understanding. The third group of sentences is comprised of the ones that are not important or essential. Another advantage of the dataset is that it also contains extra pieces of information about the essential and important sentences. It presents annotations for “removable parts” within the essential and important sentences and it indicates linked sentences, which are two sentences labeled as essential or important that need to be paired together for understanding. It is

[page 9]

worth mentioning that three graduate students (who were native English speakers and one post-graduate student – who had advanced knowledge of the English language annotation) were responsible for providing the annotations for this dataset. The number of summaries per document depends on the number of annotators for each document.

CNN Corpus Lins et al. (2019) introduce the CNN Corpus dataset, comprised of 3,000 Single-Documents with two gold-standard summaries each: one extractive and one abstractive. The encompassing of extractive gold-standard summaries is also an advantage of this particular dataset over others, which usually only contain abstractive ones.

CNN/Daily Mail Hermann et al. (2015) intend to develop a consistent method for what they called “teaching machines how to read”, i.e., making the machine able to comprehend a text via Natural Language Processing techniques. In order to perform that task, they collect around 400k news from CNN and Daily Mail and evaluate what they consider to be the key aspect in understanding a text, namely the answering of somewhat complex questions about it. Even though ATS is not the main focus of the authors, they took inspiration from it to develop their model and include the human-made summary for each news article in their dataset.

CWS Enron Email Carenini et al. (2007) finds that email ATS systems are becoming quite necessary in the current scenario: users who receive lots of emails do not have time to read them entirely, and reading emails is an especially difficult task to be done in mobile devices. The authors, then, develop an annotated version of the very large Enron Email dataset – which is described in more detail by Shetty and Adibi (2004) – in which they select 20 email conversations from the original dataset and hired 25 human summarizers (who were either undergraduate or graduate students of different fields of study) to write gold-standard summaries of them.

DUC Over et al. (2007) present an overview of the datasets provided by the Document Understanding Conferences (DUC) until 2006 and Dernoncourt et al. (2018) provides useful information concerning DUC 2007. If we take a look at Tables 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 and 15, we can note that DUC datasets are the ones most commonly used by researchers in the task of text summarization. The DUC datasets from 2001 to 2004 contain examples of both single-document and multi-document summarization with each document in each cluster having gold-standard summaries associated and each cluster having its own set of gold-standard summaries. The DUC datasets from 2005 to 2007 focus only on multi-document summarization.

Email Zhang and Tetreault (2019) note that the subject line is an important feature for going through emails in an efficient manner while surfing through received messages, and an ATS method that performs the task of generating such lines – what the authors called Subject Line Generation (SLG) – is of much help. The authors decide, therefore, to compile the dataset by annotating the existing single-document Enron dataset and providing each of its documents with three gold-standard human written summaries. Abstractive summarization fits the desired purposes, especially because of the high compression ratio required by the fact that subject lines are indeed very small.

Gigaword 5 Napoles et al. (2012) provide a useful description of the dataset – introduced for the first time by Graff et al. (2003) – which contains almost 10 million news as its singledocuments, each with its own abstractive gold-standard summary. The Gigaword Dataset is very commonly used by researchers for the purpose of training ATS neural networks due to the astronomical amount of documents it contains. However, this dataset only works for extreme summarization exercises since the summaries provided by the dataset are the headlines associated with each document.

[page 10]

GOVREPORT Huang et al. (2021), in order to study encoder-decoder attention deep-learningbased ATS systems, built the GOVREPORT dataset. This dataset contains about 19k large documents with an average of 9,000 words of government reports published by the U.S. Government Accountability Office (GAO), each accompanied by a gold-standard summary written by an expert.

Idebate Wang and Ling (2016) develop the dataset to go along with Movie Review in order to perform their desired task of multi-documents abstractive ATS of opinions. This dataset contains data retrieved from the argumentation website idebate.com. The Idebate dataset is composed of 2,259 clusters of arguments, each with its respective gold-standard summary written manually by an editor.

Multi-News Fabbri et al. (2019) decide to come up with the dataset after considering the fact that, while there are very large single-document datasets that deal with news summarization, when it comes to the task of multi-document ATS the number of documents available in the most used datasets is very scarce. Multi-News focuses on abstractive summarization and draws its data from the newser.com website, with each cluster of documents having its own humanwritten gold-standard dataset. There are about 56k clusters with varying numbers of source documents in the dataset.

NEWSROOM Grusky et al. (2018) aim at achieving the goal of producing a wide and diverse enough dataset that can be used in order to evaluate the level of extractiveness/abstractiveness of ATS summaries. The NEWSROOM dataset, then, consists of about 1.3M news articles on many topics such as day-to-day life, movies, games, and so on, and each document is accompanied by a human-written gold-standard summary extracted from its HTML metadata, besides its original title.

Opinosis Ganesan et al. (2010) introduce the Opinosis summarization framework and with it the dataset of the same name. The authors have the goal of summarization of redundant opinions about a certain topic – usually product reviews – from different users. A particular characteristic of this dataset is that it focuses on abstractive summarization and aims at generating relatively small summaries that could easily be read on mobile devices.

Reddit TIFU Kim et al. (2018) use the Today I F*** Up (TIFU) subreddit to build a singledocument-based dataset, which rules that each story must include one short summary and one long summary at the beginning and end of the post. Thus, this dataset is especially convenient for retrieving gold-standard short and long summaries.

Rotten Tomatoes Wang and Ling (2016) gather data from the RottenTomatoes.com movie review website with the goal of building a robust dataset to perform the task of multi-document opinion ATS. The main difference between the Rotten Tomatoes dataset and other multidocument opinion datasets is its focus being largely on abstractive summarization. It contains clusters of reviews for 3,731 movies and each of them is associated with a gold-standard human-written summary by an editor.

SAMSum Corpus Gliwa et al. (2019) introduce the SAMSum Corpus dataset, which consists of single-document text message-like dialogues. The documents are fabricated by linguists and encompass a wide range of levels of formality and topics of discussion. The dataset contains examples of both formal and informal dialogues in a wide range of contexts, such as a usual conversation between friends or a political discussion.

[page 11]

Scientific papers (arXiv & Pubmed) Cohan et al. (2018) use scientific papers as a source for a dataset with large documents with abstractive summaries. Thus, the authors compile a new dataset with arXiv and PubMed databases. Scientific papers are especially convenient due to their large length and the fact that each one contains an abstractive summary made by its author. The union of both the arXiv and PubMed datasets is one of the available ATS TensorFlow datasets (Abadi et al., 2015).

Scisummnet Yasunaga et al. (2019) tackle the task of scientific papers ATS because they found the existing literature lacking in a number of respects. The two major ones are the scarcity of documents contained in the most used datasets for that purpose and the fact that the generated summaries do not contain crucial information such as the paper’s impact on the field. They then built a dataset gathering the 1,000 most cited papers in the ACL Anthology Network (AAN) and each one was given a gold-standard summary written by an expert in the field. The difference between such summaries and those of other similar datasets is that they take into account the context in which the paper was cited elsewhere so that it is possible to obtain information on what exactly is its relevance in the field.

SoLSCSum Nguyen et al. (2016b) introduce this dataset for the task of social context summarization. This dataset includes articles and user comments collected from Yahoo News. Each sentence or comment has a label indicating whether the piece of text is important or not.

SummBank 1.0 Radev et al. (2003) aim at evaluating eight single and multi-document summarizers. Having the Hong Kong News Corpus (LDC[5] number LDC2000T46) as a basis, the authors build their own corpus which consists of 20 clusters of documents removed from the above-mentioned dataset, ranging from a variety of topics. For evaluation, they collect a total of 100 Million gold-standard automatic summaries at ten different lengths – generated by human-annotated sentence-relevance analysis. The authors also provide more than 10,000 human-written extractive and abstractive summaries and 200 Million automatic document and summary retrievals using 20 queries.

TAC After the DUC events ceased to happen, the Text Analysis Conference (TAC) was founded as a direct continuation of it. Its organization is similar to DUC’s and the 2008-2011 editions focused on multi-document summarization, following the later DUC editions trend. The perhaps most interesting aspect of the datasets provided by TAC 2008-2011 is that they focus on guided summarization, which aims at generating an “update summary” after a multidocument summary is already available. We may find a good overview of the contents of each of the cited TAC datasets in Dernoncourt et al. (2018).

TeM´ario The TeM´ario (Pardo and Rino, 2003) dataset contains 100 news articles – which covers a variety of topics, ranging from editorials to world politics – from the newspapers Jornal do Brasil e Folha de S˜ao Paulo, each accompanied by its own gold-standard summary written by an expert in the Brazilian Portuguese language. It is one of the datasets used by Cabral et al. (2014), who wanted to address the known problem of multilingual automatic text summarization and the fact that most summarization datasets and methods focus almost exclusively on the summarization of texts in the English language. Taking that into account, they propose a language-independent method for ATS developed using multiple datasets in languages other than English.

> 5Linguistic Data Consortium.

[page 12]

TIPSTER SUMMAC Mani et al. (1999) aims at developing a method for evaluating ATSgenerated summaries of texts. In order to do that, they apply the so-called TIPSTER Text Summarization Evaluation (SUMMAC), which was completed by the U.S. Government in May 1998. For the performance of the desired task, the authors select a range of topics in the news domain (for the most part, since there are some letters to the editor included as well) and chose 50 from the 200 most relevant articles published in that topic. For each document in the dataset, there are two gold-standard summaries: one of fixed length (S1) and one which was not limited by that parameter (S2).

2013 TREC Aslam et al. (2013), Liu et al. (2013) and Yang et al. (2013) provide useful overviews of the Temporal Summarization Track which occurred for the first time at TREC 2013. The task consists in generating an updated summarization summary of multiple timestamped documents from news and social media sources extracted from the TREC KBA 2013 Stream Corpus. Update summarization is convenient, for example, when dealing with so-called crisis events, such as hurricanes, earthquakes, shootings, etc. that require useful information to be quickly available to those involved in them. The gold-standard updates – which are called nuggets – are extracted from the event’s Wikipedia page and are timestamped according to its revision history since facts regarding the event are included as they happen. With the nuggets in hand, human experts assigned to them a relevance grade – to make possible proper evaluation – ranging from 0-3 (no importance to high importance), and an annotated dataset could be generated.

2014 TREC Zhao et al. (2014) present TREC 2014’s Temporal Summarization Track in a useful manner, highlighting the differences in comparison to the previous year’s edition. The task focused on the Sequential Updates Summarization task and participants have to perform the update summarization of multiple documents contained in the TREC-TS-2014F Corpora, which is a filtered – and therefore reduced – version of the track’s full Corpora. The data size is also reduced in comparison to the previous year’s, going from a size of 4.5 Tb to 559 Gb. An annotated dataset is produced as a byproduct of the track.

2015 TREC Aliannejadi et al. (2015) give an overview of TREC 2015’s Temporal Summarization Track and their participation in it. Participants are given two datasets, namely the TREC-TS-2015F and the TREC-TS-2015F-RelOnly which have smaller sizes when compared to the KBA 2014 corpus. TREC-TS-2015F-RelOnly is a filtered version of the TREC-TS-2015F, which contains many irrelevant documents. The assembly of the annotated dataset is similar to that of the previous years.

USAToday-CNN Nguyen et al. (2017) create this dataset for the task of social context summarization. This dataset includes events retrieved from USAToday and CNN and tweets associated with the events. Each sentence and each tweet have a label indicating whether the piece of text is important or not.

VSoLSCSum Nguyen et al. (2016a), in order to validate their models of social context summarization, create this non-English language dataset. This dataset includes news articles and their relevant comments collected from several Vietnamese web pages. Each sentence and comment have a label indicating whether the piece of text is important or not.

XSum Narayan et al. (2018b) introduce the single-document dataset, which focuses on abstractive extreme summarization, such as in (Napoles et al., 2012), that intends to answer the question “What is the document about?”. They build the dataset with BBC articles and each

[page 13]

summary is accompanied by a short gold-standard summary often written by the author of the article.

XLSum Hasan et al. (2021) aim at solving the problem of a lack of sources dealing with the problem of abstractive multi-lingual ATS. To perform that task, they build the XLSum dataset: a dataset composed of more than one million single documents in 44 different languages. The documents are news articles extracted from the BBC database, which is a convenient source since BBC produces articles in a multitude of countries – and therefore languages – with a consistent editorial style. Each document is accompanied by a small abstractive summary in every language, written by the text’s author, which is used as the gold-standard summary for the purpose of evaluation.

WikiHow Koupaee and Wang (2018) explore a common theme in the development of new datasets and ATS methods, namely that most datasets are limited by the fact that they deal entirely with the news domain. The authors, then, developed the WikiHow dataset with the desire that it would be used in a generalized manner and in a multitude of ATS applications. The dataset consists of about 200k Single-Documents extracted from the WikiHow.com website, which is a platform for posting step-by-step guides to performing day-to-day tasks. Each article from the website consists of a number of steps and each step starts with a summary in bold of its particular content. The gold-standard summary for each document is the concatenation of such bold statements.

[page 14]

||||Summarized|Summarized|Gold-standard|Gold-standard|||
|---|---|---|---|---|---|---|---|---|
||||single-|multi-|summaries per|summaries per|||
|Dataset|Language|Domain|documents|documents|document|cluster|URL|Source article|
|arXiv|English|Scientifc papers|215,000||1||https://arxiv.org/help/bulk_data|Cohan et al. (2018)|
|BIGPATENT|English|Patent documents|1,341,362||1||https://evasharma.github.io/bigpatent|Sharma et al. (2019)|
|BillSum|English|State bills|19,400||1||https://github.com/FiscalNote/BillSum|Kornilova and Eidelman|
|||||||||(2019)|
|Blog Summarization|Chinese|Opinion blog posts||1x20||4|http://cosmicvariance.com& http://blogs.msdn.com/ie|Ku et al. (2006)|
|CAST|English|News, Science texts|163||Varies||http://clg.wlv.ac.uk/projects/CAST/corpus/index.php|Hasler et al. (2003)|
|CNN Corpus|English|News|3,000||2||Available upon email request to the authors|Lins et al. (2019)|
|CNN/Daily Mail|English|News|312,085||1||https://github.com/deepmind/rc-data|Hermann et al. (2015)|
|CWS Enron Email|English|E-mails||20||5|https://github.com/deepmind/rc-data|Carenini et al. (2007)|
|DUC 2001|English|News|600|60x10|1|4|https://www-nlpir.nist.gov/projects/duc/data.html|Over et al. (2007)|
|DUC 2002|English|News|600|60x10|1|6|https://www-nlpir.nist.gov/projects/duc/data.html|Over et al. (2007)|
|DUC 2003|English|News|1,350|60x10, 30x25|1|3|https://www-nlpir.nist.gov/projects/duc/data.html|Over et al. (2007)|
|DUC 2004|English|News|1,000|100x10|1|2|https://www-nlpir.nist.gov/projects/duc/data.html|Over et al. (2007)|
|DUC 2005|English|News||50x32||1|https://www-nlpir.nist.gov/projects/duc/data.html|Over et al. (2007)|
|DUC 2006|English|News||50x25||1|https://www-nlpir.nist.gov/projects/duc/data.html|Over et al. (2007)|
|DUC 2007|English|News||25x10||1|https://www-nlpir.nist.gov/projects/duc/data.html|Dernoncourt et al. (2018)|
|Email|English|Emails|18,302||3||https://github.com/ryanzhumich/AESLC|Zhang and Tetreault (2019)|
|Gigaword 5|English|News|9,876,086||1||https://catalog.ldc.upenn.edu/LDC2011T07|Graf et al. (2003)|
|GOVREPORT|English|Documents|19,466||1||https://gov-report-data.github.io|Huang et al. (2021)|
|Idebate|English|Debate threads|Varies||1||https://web.eecs.umich.edu/~wangluxy/data.html|Wang and Ling (2016)|
|Multi-News|English|News||Varies||1|https://github.com/Alex-Fabbri/Multi-News|Fabbri et al. (2019)|
|NEWSROOM|English|News|1,321,995||1||https://github.com/lil-lab/newsroom|Grusky et al. (2018)|
|Opinosis|English|Reviews||51x100||5|http://kavita-ganesan.com/opinosis-opinion-dataset|Ganesan et al. (2010)|
|PubMed|English|Scientifc papers|133,000||1||https://pubmed.ncbi.nlm.nih.gov/download|Cohan et al. (2018)|
|Reddit TIFU|English|Blog posts|122,933||2||https://github.com/ctr4si/MMN|Kim et al. (2018)|
|Rotten Tomatoes|English|Movie reviews|Varies||1||https://web.eecs.umich.edu/~wangluxy/data.html|Wang and Ling (2016)|
|SAMSum Corpus|English|News|16,369||1||https://github.com/Alex-Fabbri/Multi-News|Gliwa et al. (2019)|
|Scisummnet|English|Scientifc papers||1,000||1|https://cs.stanford.edu/~myasu/projects/scisumm_net|Yasunaga et al. (2019)|
|SoLSCSum|English|News||157|||http://150.65.242.101:9292/yahoo-news.zip|Nguyen et al. (2016b)|
|SummBank 1.0|English,|News|400 (English)|40x10 (English)|Varies|Varies|https://catalog.ldc.upenn.edu/LDC2003T16|Radev et al. (2003)|
||Chinese||400 (Chinese)|10 (Chinese)|||||
|TAC 2008|English|News||48x20||1|https://tac.nist.gov/data/index.html|Dang et al. (2008)|
|TAC 2009|English|News||44x20||1|https://tac.nist.gov/data/index.html|Dang et al. (2009)|
|TAC 2010|English|News||46x20||1|https://tac.nist.gov/data/index.html|Dang et al. (2010)|
|TAC 2011|English|News||44x20||1|https://tac.nist.gov/data/index.html|Dang et al. (2011)|
|TeM´ario|Portuguese|News articles|100||1||https://www.linguateca.pt/Repositorio/TeMario|Pardo and Rino (2003)|
|TIPSTER SUMMAC|English|Electronic documents|1,000||2||https://www-nlpir.nist.gov/related_projects/tipster_summac|Mani et al. (1999)|
|TREC 2013|English|News/Social Media||4.5 Tb||Varies|https://trec.nist.gov/data.html|Yang et al. (2013)|
|TREC 2014|English|News/Social Media||559 Gb||Varies|https://trec.nist.gov/data.html|Zhao et al. (2014)|
|TREC 2015|English|News/Social Media||38 Gb||Varies|https://trec.nist.gov/data.html|Aliannejadi et al. (2015)|
|USAToday-CNN|English|News||121|||https://github.com/nguyenlab/SocialContextSummarization|Nguyen et al. (2017)|
|VSoLSCSum|Vietnamese|News||141|||https://github.com/nguyenlab/VSoLSCSum-Dataset|Nguyen et al. (2016a)|
|XSum|English|News|226,711||1||https://www.tensorflow.org/datasets/catalog/xsum|Narayan et al. (2018b)|
|XLSum|Varies|News|1,005,292||1||https://github.com/csebuetnlp/xl-sum|Hasan et al. (2021)|
|WikiHow|English|Instructions|204,004||1||https://github.com/mahnazkoupaee/WikiHow-Dataset|Koupaee and Wang (2018)|

Table 2: A compilation with the main kinds of information that concern the most commonly utilized summarization datasets.

[page 15]

## 5 Basic topology of an ATS system

All ATS systems depend on a basic sequence of steps: pre-processing, identification of the most important pieces of information and concatenation of the pieces of information for summary generation.

While the pre-processing step may vary from one solution to the other, it usually contains some of the steps also very common in other applications of NLP (Denny and Spirling, 2018; Gentzkow et al., 2019):

1. Sentencization: The process of splitting the text into sentences.

2. Tokenization: The process of removing undesired information from the text (such as commas, hyphens, periods, HTML tags, etc), standardizing terms (i.e. putting all words in lowercase and removing accents), and splitting the text so that it becomes a list of terms.

3. Removal of stopwords: The process of removing the most common words in any language, such as articles, prepositions, pronouns, and conjunctions, that do not add much information to the text.

4. Removal of low-frequency words: This is the process of removing rare words or misspelled words.

5. Stemming or Lemmatization: While stemming cuts off the end or beginning of the word, taking into account a list of common prefixes and suffixes that can be found in an inflected word, lemmatization takes the root of the word taking into consideration the morphological analysis of words. The idea of the application of one of these methods is to increase the word statistics.

The identification and selection of the most important pieces of information are two of the most important steps of an ATS system. The details of these steps depend on the used approach. It may depend on the attributes used to characterize the sentences (for instance, the frequency of the words), the method used to value the attributes, and the approach to avoid redundant sentences. We detail these steps in the next sections.

The concatenation step depends also on the used approach. In extractive ATS systems discussed in Section 6, this step is simply a concatenation of the chosen sentences in the last step. In abstractive ATS systems explored in Section 7, we need a language model to rewrite the sentences that arise in the summary. Finally, In hybrid systems, presented in Section 8, we usually revise the content of the extracted sentences.

## 6 Extractive summarization

Since the idea behind extractive summarization is to build a summary by joining important sentences of the original text, the two essential steps are (1) to find the important sentences and (2) to join the important sentences. In this section, we show that we can use different methods to implement these tasks. In Subsection 6.1, we present the frequency-based methods. In Subsection 6.2, we present the heuristic-based methods. In Subsection 6.3, we present the linguistic-based methods. In Subsection 6.4, we present the methods based on supervised machine learning models. Finally, in Subsection 6.5, we present the methods based on reinforcement learning approaches.

[page 16]

## 6.1 Frequency-based methods

We may use different models to implement an extractive frequency-based method. Thus, guided by the models used to implement the ATS systems, we split this section into five sections. In Subsection 6.1.1 we present vector-space-based methods. In Subsection 6.1.2, we present matrix factorization-based methods. In Subsection 6.1.3, we present the graph-based methods. In Subsection 6.1.4, we present the topic-based methods. Finally, in Section 6.1.5, we present the neural word embedding-based methods.

## 6.1.1 Vector-space-based methods

The vector space model provides a numerical representation of sentences using vectors, facilitating the measurement of semantic similarity and relevance. It is a model that represents each document of a collection of NS sentences by a vector of dimension NV , where NV is the number of words (terms) in the vocabulary. The idea here is to use the vector space model to select the most relevant sentences of the document.

In order to define precisely the vector space model, we start by defining the sentence-term matrix M . It is a NS × NV matrix that establishes a relation between a term and a sentence:

**==> picture [343 x 69] intentionally omitted <==**

where each row is a sentence and each column is a term. The weight ωj,i quantifies the importance of term i in sentence j. It depends on three factors. The first factor (local factor) relates to the term frequency and captures the significance of a term within a specific sentence. The second factor (global factor) relates to the sentence frequency and gauges the importance of a term throughout the entire document. The third factor (normalization) adjusts the weight to account for varying sentence lengths, ensuring comparability across sentences. Thus, we may write the weight as

**==> picture [259 x 27] intentionally omitted <==**

where

**==> picture [325 x 27] intentionally omitted <==**

In Eq. (2), normj is a sentence length normalization factor to compensate undesired effects of long sentences. In Eq. (3), ftf(tfi,j) is the weight associated with the term frequency and fisf(sfi) is the weight associated with the sentence frequency. Table 3 presents the most common choices for ftf, fisf and normj extracted from Baeza-Yates and Ribeiro-Neto (2008), Manning et al. (2008) and Dumais (1991). The term frequency (TF) and inverse sentence frequency (ISF) weighting scheme, called TF-ISF, are the most popular weights in information retrieval.

[page 17]

|Term frequency|ftf(tfi,j)|
|---|---|
|Binary|min{tfi,j,1}|
|Natural (raw frequency)|tfi,j|
|Augmented|0.5 + 0.5<br>tfi,j<br>maxi′tfi′,j|
|Logarithm|1 + log2(tfi,j)|
|Log average|1 + log2(tfi,j)<br>1 + log2(avgwi′∈djtfi′,j)|
|Sentence frequency|fisf(dfi)|
|None|1|
|Inverse frequency|log2<br>�NS<br>sfi<br>�|
|Entropy|1−<br>�<br>j<br>pi,jlog (pi,j)<br>log (NS)|
||pi,j =<br>tfi,j<br>�<br>j tfi,j|
|Normalization|normj|
|None|1|
|Cosine|�<br>�<br>�<br>�<br>NV<br>�<br>i<br>�ω2<br>i,j|
||NV|
|Word count|�<br>tfi,j|
||i|

Table 3: The most common variants of TF-ISF weights.

Before presenting the methods, it is worth mentioning the study presented by Nenkova et al. (2006) that stresses the roles of three different important dimensions that arise in frequencybased attempts to summarization, namely (1) word frequency, (2) composition functions for estimating sentence importance from word frequency estimates, and (3) adjustment of frequency weights based on context:

1. Word frequencies (or some variation based on TF-ISF) are the starting points to identify the keywords in any document (or clusters of documents);

2. The composition function is necessary to estimate the importance of the sentences as a function of the importance of the words that appear in the sentence.

3. The adjustment of frequency weights based on context is fundamental since the notion of importance is not static. A sentence with important keywords must be included in the summary as long as there is no other very related sentence with similar keywords in the summary.

Therefore, Eqs. (2) and (3) with Table 3 present different options to select the most important terms in the complete text. In order to identify the most relevant sentences of the text, as above-mentioned, we need to aggregate these measures of importance associated with the terms and also avoid the chosen sentences having the same terms. A simple way to aggregate

[page 18]

these measures for each term is to evaluate the average of each term in a sentence. However, in order to avoid the repetition of terms in different selected sentences, after selecting a given sentence, we may penalize the choice of sentences with terms that arise in sentences that had been previously selected.

The SumBasic method (Nenkova et al., 2005) uses the raw document frequency to identify the most important terms. The relevance of each sentence is given by the average of its terms. The idea is to select the most important sentences according to that criterion. However, in order to avoid the selection of highly correlated sentences, after selecting a given sentence, the frequencies of all the terms that arise in the selected sentence are squared and with these new values, the relevance of the sentences is re-evaluated. We may find an extension of Nenkova et al. (2005) in Nenkova et al. (2006). In this paper, using also the frequency of the terms as an input, the authors consider different possibilities for the evaluation of the score associated with each sentence such as (1) multiplication of the frequency of the sentence’s terms; (2) addition of these frequencies and the division by the number of terms in the sentence; (3) addition of these frequencies. Note that while (1) favors short sentences, (3) favors longer sentences, and (2) is a combination of both. As in SumBasic, they also consider an additional step in the algorithm to reduce redundancy. After a sentence has been selected for inclusion, the frequencies of the terms for the words in the selected sentences are reduced to 0.0001 (a number close to zero) to discourage sentences with similar information from being chosen again.

SumBasic+ due to Darling (2010) is also a direct extension of the work of Nenkova et al. (2006), in which a linear combination of the unigram and bigram frequencies is explored. They choose the parameters of the linear combination in order to maximize the ROUGE score. This work also explores query-based summarization and update-based summarization. While the setup used for update-based summarization is essentially the same, in order to attend to the task of query-based summarization, the authors suggest adding more probability mass on terms that arise in the query vector.

Using the same principle described in SumBasic (Nenkova et al., 2005), we may use any weight given by the combination of the terms in Table 3 to identify the most relevant terms and sentences and consider different methods to avoid redundancy. For instance, in order to avoid the selection of highly correlated sentences, Carbonell and Goldstein (1998) suggest that we may evaluate the relevance of each sentence by the convex combination between the relevance of the sentence given by TF-ISF terms and the maximal correlation of the sentence and the sentences already included in the summary.

An interesting way to reduce the redundancy of sentences in the final summary is to separate similar sentences into clusters. A simple way to do that is to characterize the sentences with TFISF vectors, use a clustering method to split the document into groups of similar sentences, and choose the most relevant sentence of each group as the one that is the closest to the centroid of each cluster (Zhang and Li, 2009). These sentences are the candidate sentences to be included in the summary. We select these sentences in order of relevance based on TF-ISF.

Another interesting approach called KL Sum is to choose sentences that minimize the Kullback–Leibler divergence (relative entropy) between the frequency of words in the summary and the frequency of words in the text (Haghighi and Vanderwende, 2009), where the sentences are greedily chosen.

A very interesting multi-document extractive approach is the submodular approach due to Lin and Bilmes (2011). They formulate the problem as an optimization problem using monotone nondecreasing submodular set functions. A submodular function f on a set of sentences S satisfies the following property: for any A ⊂ B ⊂S\s, we have f (A+s)−f (A) ≥ f (B+s)−f (B), where s ∈S. Note that f satisfies the so-called diminishing returns property and it captures the intuition that adding a sentence to a small set of sentences, like the summary, makes a greater contribution than adding a sentence to a larger set. The objective is then to find a summary that maximizes the diversity of the sentences and the coverage of the input text. The

[page 19]

authors formulate this problem as the problem of maximizing the objective function given by F (S) = L(S)+λR(S), where S is the summary, L(S) measures the coverage of summary set S to the document, R(S) measures (rewards) diversity in S, and λ ≥ 0 is a trade-off between coverage and diversity. The authors also call attention to the fact that L(S) should be monotonic, as coverage improves with a larger summary, and it should also be submodular since the effect of adding a new sentence to a smaller summary has a large effect. On the other hand, assuming that the sentences were previously split into clusters Pi for i = 1, · · · , K, in order to reward diversity, they set R(S) =[�][K] k=1[g][(][�] j∈Pi∩S[r][j][),][where][g][is][a][concave][function][and][r][is][the] sentence individual reward. The authors emphasize the fact that R is also submodular. With this objective, they show that an approximate greedy algorithm can be used for the task. In order to deal with a query-based task, they change the function R to be a linear combination of the reward associated with the individual sentences and a reward associated with the relevance of the sentence to the query. In this context, it is interesting to mention a value overview presented in Bilmes (2022) of the use of submodularity in machine learning and artificial intelligence.

There are many methods for ATS using the vector space model. We present a representative compilation of these methods in Table 4.

[page 20]

|Source|Main contribution|Dataset|||||Evaluation||
|---|---|---|---|---|---|---|---|---|
|Carbonell and Goldstein (1998)|It uses the TF-ISF to select the sentences and in an iterative fashion, it uses|TIPSTER topic (Miller|||et|al.,|F-scores<br>of<br>the|ex-|
||a convex combination of the TF-ISF and the correlation with the previously|1998)|||||tracted sentences.||
||chosen sentences.||||||||
|Radev et al. (2004)|In a multi-document setup, it creates clusters of documents by topics, it rep-|A corpus consisting of|||a|to-|Human experts||
||resents both sentences and topics using TF-IDF and it chooses the sentences|tal<br>of|558|sentences|in|27|||
||that should be extracted based on scores that weights the proximity of the|documents,||organized|in|6|||
||sentence to the topics using cosine similarity.|clusters|extracted<br>by||CIDR||||
|||(Radev|et al., 1999).||||||
|Nenkova et al. (2005)|It uses the raw document frequency to determine the relevance of each sen-|DUC 2004, 2005|||||ROUGE-1, ROUGE-2,||
||tence and in an iterative fashion it penalizes the sentences with words of||||||ROUGE-SU-4, manual||
||previously chosen sentences.||||||Pyramid<br>and<br>repeti-||
||||||||tion.||
|Nenkova et al. (2006)|It is an extension of Nenkova et al. (2005) that considers different options to|DUC 2004, 2005|||||ROUGE-1, ROUGE-2,||
||evaluate the score of a sentence.||||||ROUGE-SU-4, manual||
||||||||Pyramid||
|McDonald (2007)|It formulates the problem of multi-document summarization as a very gen-|DUC 2002|||||ROUGE-1|and|
||eral optimization problem where the objective is to choose parts of a text||||||ROUGE-2||
||(for instance, sentences) that maximize a given score that increases with the||||||||
||relevance of the parts of the text and decreases the redundancy.<br>It solves||||||||
||both with a greedy algorithm and a dynamic programming approach based||||||||
||on a solution to the 0-1 knapsack problem (Cormen et al., 2022).||||||||
|Gillick et al. (2008)|It evaluates the importance of the sentences in an integer programming frame-|TAC 2008|||||ROUGE-1, ROUGE-2||
||work whose objective is to build a summary that maximizes the concept cov-||||||and ROUGE-SU-4||
||erage (bigram frequency).||||||||
|Zhang and Li (2009)|It uses the TF-ISF to characterize the sentences, forms clusters of sentences|DUC 2003|||||ROUGE-1, ROUGE-2||
||using this information, and chooses the most relevant sentences of these clus-||||||and F-1 score of the ex-||
||ters.||||||tracted sentences.||
|Haghighi and Vanderwende (2009)|It chooses sentences that minimize the Kullback–Leibler divergence between|DUC 2006|||||ROUGE-1, ROUGE-2||
||the frequency of words in the summary and the frequency of words in the||||||and ROUGE-SU-4||
||text.||||||||
|Darling (2010)|It is an extension of Nenkova et al. (2006). It explores a linear combination|DUC 2004 and TAC 2010|||||ROUGE-2,<br>ROUGE-||
||of the unigram and bigram frequencies and it chooses the parameters of the||||||SU-4,<br>basic elements,||
||linear combination in order to maximize the ROUGE score. In order to attend||||||linguistic quality|and|
||to the task of query-based summarization, it adds more probability mass on||||||manual Pyramid||
||terms that arise in the query vector.||||||||
|Lin and Bilmes (2011)|It sets the problem of multi-document extractive summarization as a greedy|DUC 2003,||DUC 2004,|DUC||ROUGE-1|and|
||optimization of a submodular function that trades of between coverage and|2005,<br>DUC 2006 and|||DUC||ROUGE-2||
||diversity.|2007|||||||

Table 4: A representative compilation of the ATS methods that use vector space models.

[page 21]

## 6.1.2 Matrix factorization based methods

The idea of the matrix factorization methods of extractive summarization is to decompose the sentence-term matrix presented in Section 6.1.1 into a dense representation, where each term is represented by a feature (or concept). The point is that many different terms present very similar concepts. So, instead of dealing individually with the terms, we may deal directly with the concepts. In particular, in the case of ATS, we can select sentences that are good representations of different concepts that arise in the text.

The starting point for this kind of method is the vector space model reviewed in Section 6.1.1. Suppose that we have a text that we want to summarize with NS sentences. We may represent this text by the sentence-term matrix M[S] in Eq. (1) with NS rows and NV columns.

Using for instance, Singular Value Decomposition (SVD) (Stewart, 1993), Golub and Loan (2013) decompose this matrix in the following way:

**==> picture [265 x 16] intentionally omitted <==**

where U and V[T] are respectively orthogonal matrices of eigenvectors derived from sentencesentence and term-term covariance matrices[6] , and Σ is an r × r diagonal matrix of singular values where r = min (NS, NV ) is the rank of Mtfisf. Note that, in this representation, the rows of the matrix UΣ contain the r-dimensional representation of the NS sentences, where each column of V is a base vector where each sentence is represented. Therefore, each column of UΣ is associated with a concept. We may find a tutorial introduction to SVD in Klema and Laub (1980) and a survey of SVD for intelligent information retrieval in Berry et al. (1995).

If we want that the summary finds the most important sentences of each concept, the basic idea is to select the sentences that, for each column, have the maximal absolute entry as described in Gong and Liu (2001).

Steinberger et al. (2004) introduce an interesting modification to Gong and Liu (2001)’s method. It calls our attention that the latter presents two significant disadvantages: First, it is necessary to use the same number of dimensions as the number of sentences we want to choose for a summary. However, we know that the higher the number of dimensions of the concept space, less significant topics are introduced in the summary. Second, the sentences that have a higher entry in a given concept are chosen, but they are not necessarily the most important sentences (since some of the concepts may not be that important). Therefore, the idea here

is to extract the most relevant sentences s in terms of the weights �rk=1[u][2] sk[σ] k[2][.][In][order][to] � deal with a multi-document update summarization task, Steinberger and Jeˇzek (2009) create sets of topics for both previous documents and new documents. Sentences containing novel and significant topics may be extracted for building the update. Novelty is measured by the average of the internal product between the topics of the previously known documents and the topics of the new documents.

Other interesting approaches use the Non-Negative Matrix Factorization technique (NMF) (Paatero and Tapper, 1994; Paatero, 1997; Lee and Seung, 1999, 2000; Gillis, 2020). The idea of NMF is to decompose M[S] tfisf[in][a][product][of][other][two][matrices][W][and][H][,][where][we][may] interpret the columns of the product matrix as linear combinations of the column vectors in W using the coefficients provided by the columns of H. In general, we assume that the number of columns of W (or the number of rows of H) is lower than those of the product matrix we are decomposing. One simple algorithm to find this decomposition is based on the nonnegative least squares, where we minimize the distance using the Frobenius norm between the product matrix and the actual matrices W and H. We may find a comprehensive review of the NMF including properties and algorithms in Wang and Zhang (2012). Thus, we may extract the sentences that maximize each of the topics of the documents that are the ones that for

> 6This means that the columns of U are eigenvectors of MtfisfMTtfisf[and][the][columns][of][V][are][eigenvectors][of] M[T][M][tfisf][.]

[page 22]

each column has the maximal absolute entry as in Gong and Liu (2001). This is the algorithm considered in Lee et al. (2009).

In order to deal with a query-based task, Park et al. (2006) provide an algorithm that follows the same steps of Lee et al. (2009) and extracts the sentences that maximize the topics of the document that have higher similarity with the provided query.

There are many methods for ATS using matrix factorization representations. We present a representative compilation of these methods in Table 5. Furthermore, although we have considered here only the two common methods used in summarization, it is worth knowing that there are many other kinds of matrix factorization techniques. We may find a survey of these techniques in Lyche (2020) and Edelman and Jeong (2021).

[page 23]

|Source|Main contribution|Dataset|||||Evaluation|||
|---|---|---|---|---|---|---|---|---|---|
|Gong and Liu (2001)|It applies the SVD decomposition to the TF-ISF representation of the text|Two<br>months||of|the|CNN|Precision,|recall,|and|
||and it selects the sentences that are the best representative of each concept.|Worldview news programs|||||F1<br>score|of<br>the|ex-|
||||||||tracted sentences.|||
|Steinberger et al. (2004)|It applies the SVD decomposition to the TF-ISF representation of the text|Reuters|collection||||Cosine similarity||and|
||and it selects the sentences with large weights that jointly represent the im-||||||latent-semantic|||
||portance of the concept and the importance of the sentence as a representative|||||||||
||of that concept.|||||||||
|Park et al. (2006)|It uses NMF to select the most relevant sentences of the topics that are similar|Yahoo Korea News|||||Precision|||
||to the given query.|||||||||
|Steinberger and Jeˇzek (2009)|It uses latent semantic analysis for creating sets of topics for both previous|DUC 2007 and TAC 2008|||||Pyramid,|ROUGE-2,||
||documents and new documents and it selects sentences containing novel and||||||ROUGE-SU-4,<br>Basic|||
||significant topics.||||||elements<br>and<br>human|||
||||||||experts|||
|Lee et al. (2009)|It applies the NMF decomposition to the TF-ISF representation of the text|DUC 2006|||||ROUGE-1,|ROUGE-||
||and it selects the sentences that are the best representative of each concept.||||||L,<br>ROUGE-W||and|
||||||||ROUGE-SU-2|||
|Yogatama et al. (2015)|It provides a greedy algorithm to create a summary that maximizes the vol-|TAC 2008 and TAC|||2008||ROUGE-1||and|
||ume (coverage) of selected sentences in the semantic space, where the sen-||||||ROUGE-2|||
||tences are represented in the semantic space by the SUV decomposition of|||||||||
||the bigrams that form the sentences.|||||||||
|Nguyen et al. (2019)|This is an approach to social context summarization, wherein the mathemati-|SoLSCSum, USAToday-CNN,|||||ROUGE-1,|ROUGE-2||
||cal formulation of the NMF, the web documents, and the user’s content share|VSoLSCSum and DUC 2004|||||and ROUGE-W|||
||the same topic matrix.|||||||||
|Khurana and Bhatnagar (2022)|It employs NMF to reveal probability distributions for computing entropy of|DUC|2001,|DUC||2002,|ROUGE-1,|ROUGE-2||
||terms, topics, and sentences in latent space. It uses the classical Knapsack|CNN/DailyMail|||||and ROUGE-L|||
||optimization algorithm to select entropic highly informative sentences.|||||||||

Table 5: A representative compilation of the ATS methods that use matrix factorization methods.

[page 24]

## 6.1.3 Graph based methods

A graph (or a network) is a pair G = (V, E), where V is a set where each element is called a vertex (node) and E is a set of paired vertices, where each element is called an edge. Networks are used worldwide to model systems whose components interact with each other, such as genetic systems (gene coexpression or gene regulatory systems), protein networks, reaction networks, anatomic networks (intercellular and brain networks), ecological networks, technological networks (electric power networks) and social networks (Newman, 2003; Estrada, 2012). Over the years, several metrics were introduced to characterize the networks and also the components of these systems (Costa et al., 2007). Among them, we may cite centrality, which we use in this section, that measures the importance of each component in the network. For instance, if we consider Instagram, the social media platform, the most important individuals are the ones that have the largest number of followers.

In the graph-based methods approach, we represent the text as a network. In this network, each sentence is a node of the network. There is a link between two nodes if the sentences are similar. Although we may think in different ways to weigh the links of these networks, simple ideas are: (1) A link exists when two sentences share a word; (2) A link exists when the similarity between two sentences exceed a given threshold.

With these definitions in mind, the most relevant sentences are those with the highest centrality and are the ones that should be included in the summary. This is the basic idea of Text Rank (Mihalcea and Tarau, 2004) and Lex Rank (Erkan and Radev, 2004) that use respectively the page rank (Page et al., 1999) and the usual eigenvector approach (Bonacich, 1972; Ruhnau, 2000) to evaluate the centrality of the sentences in a multi-document setup.

In order to deal with a query-based approach, Otterbacher et al. (2005) basically uses the approach of the Lex Rank method (Erkan and Radev, 2004). However, instead of selecting the sentences with the highest centrality, they select sentences based on a mixture model that also considers the relevance of the sentences according to the provided query.

In Wan and Yang (2006), in a multi-document setup, the sentence similarities are built using the cosine similarity of the TF-IDF vectors of the sentences in an approach that differentiates sentences of the same document from sentences of different documents. These similarities are normalized to define a Markov chain in the network and, based on it, they evaluate the centrality of each sentence (node). In order to choose the sentences to be extracted, they penalize sentences that are very connected with the previously selected sentences.

There are many graph methods for ATS. We present a significant compilation of these methods in Table 6.

[page 25]

||Source|Main contribution|Dataset||||Evaluation|Evaluation|||
|---|---|---|---|---|---|---|---|---|---|---|
||Mihalcea and Tarau (2004)|It represents the document as a network, where each sentence is a node of the network and|Inspec database (Hulth,|||2003)|Precision, recall and F-||||
|||there is a link between two nodes if the sentences share a word. It weights the edges by the|||||measure.||||
|||normalized (by the length of the sentence) number of shared words. It uses the Page Rank|||||||||
|||to identify the most central sentences.|||||||||
||Erkan and Radev (2004)|It uses the same network representation of Mihalcea and Tarau (2004). It uses the eigenvalue|DUC 2003, 2004||||ROUGE-1||||
|||centrality to identify the most central sentences.|||||||||
||Mihalcea and Tarau (2005)|It uses the same network representation of Mihalcea and Tarau (2004). It weights the edges|DUC 2002 and TeM´ario||||ROUGE-1||||
|||considering three different situations: (a) a simple undirected graph; (b) a directed weighted|||||||||
|||graph with the orientation of edges set from a sentence to sentences that follow in the text|||||||||
|||(directed forward), or (c) a directed weighted graph with the orientation of edges set from a|||||||||
|||sentence to previous sentences in the text (directed backward). It uses the HITS and Page|||||||||
|||Rank algorithms to identify the most central sentences.|||||||||
||Otterbacher et al. (2005)|It is a query-based approach. It uses the Lex Rank method (Erkan and Radev, 2004) to find|A corpus of 20 multi-document||||Mean Reciprocal|||Rank|
|||out the most relevant sentences and it selects the sentences based on a mixture model that|clusters|of complex news sto-|||(MRR)|and||Total|
|||also considers the relevance of the sentences according to the provided query.|ries||||Reciprocal||Document||
||||||||Rank (TRDR)||||
||Wan and Yang (2006)|In<br>a<br>multi-document<br>approach,<br>it<br>uses<br>the<br>same<br>network<br>representation<br>of|DUC 2002 and DUC 2004||||ROUGE-1||||
|||Mihalcea and Tarau (2004).<br>It evaluates<br>the sentence<br>similarities using the cosine|||||||||
|||similarity of the TF-IDF vectors of the sentences. It normalizes the similarities to define a|||||||||
|||Markov chain and to evaluate the centrality of each sentence (node). In order to choose the|||||||||
|||sentences to be extracted, it penalizes sentences that are very connected with the previously|||||||||
|25|Lin et al. (2009)|selected sentences.<br>It uses the same network representation of Mihalcea and Tarau (2004) with edge weights|ICSI|meeting||corpus|ROUGE-1||and|F-|
|||given by the similarity between the sentences. It evaluates the similarity using the cosine|(Janin et al.,||2003)||measure.||||
|||between the TF-IDF vectors of the sentences or the ROUGE-1 (F measure) score. In order|||||||||
|||to extract the sentences, it maximizes a submodular set function defined on the graph using|||||||||
|||a greedy algorithm.|||||||||
||Thakkar et al. (2010)|It uses the same network representation of Mihalcea and Tarau (2004). It associates each|–||||–||||
|||edge with a cost that is proportional to the physical distance of the sentences and inversely|||||||||
|||proportional to the similarity between the sentences and the similarity between the sentence|||||||||
|||and the title of the document. It creates the summary by taking the shortest path that starts|||||||||
|||with the first sentence of the original text and ends with the last sentence.|||||||||
||Barrios et al. (2016)|It presents new alternatives to the similarity function for the Text Rank algorithm|DUC 2002||||ROUGE-1,||ROUGE-2||
|||(Mihalcea and Tarau, 2004)|||||and ROUGE-SU-4.||||
||Mallick et al. (2019)|It uses the same network representation of Mihalcea and Tarau (2004) with the edge weights|BBC news articles||||ROUGE-1,||ROUGE-2||
|||given by a modifed cosine similarity. It uses a modifed Page Rank algorithm to score the|||||and ROUGE-L.||||
|||sentences.|||||||||
||Van Lierde and Chow (2019)|This is a query-based approach where it represents sentences as nodes, as usual. However,|DUC 2005,||DUC 2006 and||ROUGE-2|||and|
|||it adds hyperedges between the sentences that consider the similarity of the themes of each|DUC 2007||||ROUGE-SU-4.||||
|||sentence, where the themes of the sentences are determined by a clustering algorithm. It|||||||||
|||extracts the sentences that cover all themes of the corpus.|||||||||
||U¸ckan and Karcı (2020)|This is a multi-document summarization method. It uses the same network representation|DUC 2002 and DUC 2004||||ROUGE-1,||ROUGE-||
|||of Mihalcea and Tarau (2004). It removes the maximum independent set from the original|||||2,<br>ROUGE-L|||and|
|||graph and it selects the sentences in the modifed graph as the ones with the highest eigenvalue|||||ROUGE-W.||||
|||centralities.|||||||||

Table 6: A significant compilation of the graph methods used for ATS.

[page 26]

## 6.1.4 Topic-based methods

The topic-based summarization methods rely on topic representations such as the Latent Dirichlet Allocation (LDA) (Blei et al., 2003). LDA is a generative model[7] that represents a document by a collection of topics and each topic, in its turn, by a collection of words.

In order to develop the so-called TopicSum, Haghighi and Vanderwende (2009) assume a fixed vocabulary V and propose a LDA-like generative model. For the sake of organization, although this approach was originally developed for multi-document summarization, we present here this approach in a setup for single-document summarization:

1. Draw a “background” vocabulary distribution φB from Dirichlet(V, λB) shared across the document collection representing the background distribution over vocabulary words.

2. For each document d, we draw a “content” distribution φC from Dirichlet(V, λC ) representing the significant content of d that we wish to summarize.

3. For each sentence s of each document d, draw a distribution ψT over topics (content, background) from a Dirichlet prior with pseudo-counts (nC, nB), where nC < nB reflects the intuition that most of the words in a document come from the background.

Using this generative model, the authors Haghighi and Vanderwende (2009) estimate φC for each document and select the most important sentences using the same criterion used by the KLSum discussed in Section 6.1, replacing the frequency of the words in the text, which is a unigram distribution, by φC . An extension of this model, called HIERSum and provided by the same work, considers that a document may be formed by different topics as in Chang and Chien (2009).

There are other ideas very similar to the approach proposed by Haghighi and Vanderwende (2009) that we present in Table 7.

> 7A generative model is a model that describes the distribution of the data and tells how likely a given example

is.

[page 27]

|Source|Main contribution|Dataset|Evaluation||
|---|---|---|---|---|
|Haghighi and Vanderwende (2009)|It presents an approach for multi-document summarization that chooses sen-|DUC 2006|ROUGE-1, ROUGE-2||
||tences that minimize the Kullback–Leibler divergence between the frequency||and ROUGE-SU-4||
||of words in the summary and the frequency of content estimated by an LDA-||||
||like approach. It also extends this model to consider the possibility that a||||
||document is formed by many topics.||||
|Chang and Chien (2009)|It explores two variations of the LDA-like approach for extractive summariza-|DUC 2005|ROUGE-1, ROUGE-2||
||tion.||and ROUGE-L||
|Wang et al. (2009)|In a multi-document summarization approach, it proposes a unigram model|DUC 2002 and|ROUGE-1,<br>ROUGE-||
||as a mixture of several topic unigram models and, in its turn, it assumes that|DUC 2004.|2,<br>ROUGE-L|and|
||topic unigram models are mixtures of sentences unigram models. Thus, each||ROUGE-SU-4||
||topic is represented by a set of sentences and the sentences to be extracted||||
||are the most representative of each topic.||||
|Delort and Alfonseca (2012)|It presents a variation of LDA that aims to learn to distinguish between|TAC 2008 and|ROUGE-1, ROUGE-2||
||common information and novel information.|TAC 2009|and ROUGE-SU-4||
|Belwal et al. (2021)|It mixes ingredients of topic modeling using LDA with vector space models|CNN/DailyMail|ROUGE-1,<br>ROUGE-||
||representation. It selects sentences represented by the vector space models||2,<br>ROUGE-L|and|
||that are the most similar to the topics previously selected.||ROUGE-SU-4||
|Srivastava et al. (2022)|It uses LDA for topic modeling and the K-medoids clustering method for|Wikihow,|ROUGE-1, ROUGE-2||
||summary generation.|CNN/DailyMail|and ROUGE-L||
|||and DUC 2002|||

Table 7: A representative compilation of the ATS methods that use topic-based methods.

[page 28]

## 6.1.5 Neural word embedding based methods

Word embeddings represent words as vectors in a high-dimensional space, capturing their semantic meaning (Bengio et al., 2000). While the vectors aggregating words by concepts discussed in Section 6.1.2 could be seen as a form of word embeddings, traditional definitions align more closely with representations derived from neural network models that extend classical models of language.

Numerous methods have been proposed for generating word embeddings. Among the most notable are Word2vec (Mikolov et al., 2013), GloVe (Pennington et al., 2014), and fastText (Joulin et al., 2016). A comprehensive review of these methods can be found in Guti´errez and Keith (2018). Although these models are all rooted in neural probabilistic language frameworks and are trained semi-supervised[8] , they differ in performance metrics, input/output types, and their balance between local and global word information. While some of these models use performance indexes that are variations of the likelihood functions associated with multinomial logit models (a kind of cross-correlation entropy), others use variations of the mean square error. For instance, the CBOW, presented in Figure 1, and skip-gram, presented in Figure 2, models, both introduced by Mikolov et al. (2013), approach the problem differently. Using a sentence like “You get a shiver in the dark” from the song “Sultans of Swing” by Dire Straits, CBOW tries to predict the word ”shiver” from its surrounding words, while skip-gram does the opposite. The objective of the CBOW approach, is to maximize the average log probability

**==> picture [285 x 35] intentionally omitted <==**

where wik is the central word and Cη(wik ) = [wik−η , . . . , wik−1, wik+1, . . . , wik+η ] is the training context of size η. We may define similarly the performance index associated with the skip-gram model. Another interesting approach is due to Collobert and Weston (2008) (CW) who train a neural network to differentiate between a valid n-gram and a corrupted one. Furthermore, in these examples, we may note that we are only using local information. However, as we mentioned before, we may also use global information given by, for instance, the term-document matrix (similar to the term-sentence matrix considered in Section 6.1.1) to weight the performance index. All these algorithms have some design and hyperparameter choices and we may find very different results depending on them (Levy et al., 2015; Liu et al., 2017).

In these models, the input and output layers have their sizes given by the vocabulary that arises in the collection of documents. In the CBOW model, the input layer indicates the words that arise in the context and the output layer indicates the desired output. In this model, they maximize the probability given by Eq. (5) using the representation of the words given by vectors such as the ones presented in

**==> picture [317 x 30] intentionally omitted <==**

where the vector vik arises when wik is the central word and the vector uil arises when wil belongs to the context Cη(wik ). Thus, in this model, we represent each word by two vectors. Neural word embeddings, denoted as vwi, are the average of these vectors and reside in R[N][W] , where NW represents the embedding dimension, a hyperparameter of the model. Analogous definitions can be applied to the skip-gram model. A recent extension of these models are the so-called contextualized word embeddings (Liu et al., 2020) such as CoVe (McCann et al., 2017) and ELMo (Peters et al., 2018). In these models, each token has a representation that is a function of the entire text sequence. They are trained using sequence-to-sequence models discussed in our text, for the sake of organization, in Section 7.2.

> 8This means that we build inputs and outputs for the neural networks using all the sentences and all the words in these sentences, that are available in the training documents without the need for annotated texts.

[page 29]

Figure 1: CBOW model.

**==> picture [325 x 289] intentionally omitted <==**

**----- Start of picture text -----**<br>
w(t − 2)<br>w(t − 1) SUM<br>w(t)<br>w(t + 1)<br>w(t + 2)<br>**----- End of picture text -----**<br>

There are several methods that we can use to consider the information encapsulated in word embeddings. The main motivation behind the use of word embeddings is to deal with the main drawbacks of the space vector models approach associated with the fact that similar words are treated separately: (1) Similar words may have very different rankings. Therefore, it fails to assign appropriate scores to the sentences; (2) The summary may be redundant, since the sentences of the summary may come from different words that have similar use and meaning.

One of the first ideas of using word embeddings in extractive summarization is due to K˚ageb¨ack et al. (2014). They use the setup of greedy submodular optimization due to Lin and Bilmes (2011), reviewed in Section 6.1.1, and different word embeddings (Word2Vec and CW) to extract sentences.

One of the simplest ideas is to use a kind of centroid method such as in Rossiello et al. (2017). We may review this method using the following steps: (1) Create a representation of the documents in the dataset using the vector space models; (2) For each document, identify the most relevant words, i.e., the words that have a weight (provided by the space vector model) larger than a given threshold; (3) Evaluate the centroid of each document averaging the word embeddings of each word selected in the last step; (4) Evaluate the word embedding of each sentence in a document averaging the word embeddings of each word that arises in the sentence; (5) Identify the most relevant sentences that are the sentences that are the most similar to the centroid of the document.

Mohd et al. (2020) use word embeddings to find the m most similar words to each word in a given sentence. Then each sentence is represented by a large vector of words, where each word in the original sentence is replaced by these m most similar words previously found using the word embedding representation. With this new representation of each sentence, it applies TF-ISF to this new representation of the sentences and any algorithm presented in Section 6.1.1 may be used to extract the most important sentences. In particular, they use a clustering method similar to Zhang and Li (2009).

[page 30]

Figure 2: Skip-gram model.

**==> picture [324 x 289] intentionally omitted <==**

**----- Start of picture text -----**<br>
w(t − 2)<br>w(t − 1)<br>w(t)<br>w(t + 1)<br>w(t + 2)<br>**----- End of picture text -----**<br>

The idea behind the work of Hailu et al. (2020) is to build a list of important words that they call keywords (first sentence words and high-frequency words) and to rank the sentences in the document according to the cosine similarity between the embeddings of the keywords and the embeddings of the words that form the sentences.

There are many methods for ATS that uses word embeddings. We present a significant compilation of these methods in Table 8.

[page 31]

|Source|Main contribution|Dataset|Evaluation||||
|---|---|---|---|---|---|---|
|K˚ageb¨ack et al. (2014)|It uses the approach of optimization of submodular functions (Lin and Bilmes,|Opinosis|ROUGE-1,||ROUGE-2||
||2011) and the Word2Vec and CW representations in different setups.||and ROUGE-SU-4||||
|Yin and Pei (2015)|It creates a sentence representation based on a kind of word embedding using|DUC 2002 and DUC 2004|ROUGE-1,||ROUGE-2||
||a convolutional neural network (CNN) and, in a setup close to the ones used||and ROUGE-SU-4||||
||in graph-based methods presented in Section 6.1.3, it chooses the sentences||||||
||that are nearly optimizing a function that trades of prestige (importance)||||||
||and dissimilarity.||||||
|Rossiello et al. (2017)|It creates a representation of the documents in the dataset using the vector|DUC 2004|ROUGE-1|||and|
||space model, it identifes the most relevant words using TF-IDF, and it uses||ROUGE-2||||
||the average word embedding of these words to represent the sentences and||||||
||the document. It identifes the most relevant sentences, those that are the||||||
||most similar to the centroid of the document.||||||
|Mohd et al. (2020)|Using the Word2Vec representation, it represents each sentence by a large|DUC 2007|ROUGE-1,|ROUGE-2,|||
||vector of words, where each word in the original sentence is replaced by these||ROUGE-L,||ROUGE-||
||m most similar words.<br>Thus, it applies TF-ISF to account for the most||SU-4||||
||important words and selects the most important sentences from the clusters||||||
||formed using the TF-ISF representation.||||||
|Hailu et al. (2020)|It builds a list of keywords based on first sentence words and high-frequency|NEWSROOM summarization|ROUGE-1,|ROUGE-2,|||
||words and ranks the sentences according to the cosine similarity between the|dataset|ROUGE-L,||BLEU-1,||
||embeddings of the keywords and the embeddings of the words that form the||BLEU-2,||BLEU-3,||
||sentences.||BLEU-4,||F-measure||
||||(of<br>1,|2|and|3|
||||grams), WEEM4TSw,||||
||||WEEM4TSg|||and|
||||WEEM4TSf.||||
|Barman et al. (2021)|It represents each word by GLOVE vectors and each sentence by the average of|BBC news|ROUGE-1|||and|
||the words it contains. In order to build the network, each sentence represents||ROUGE-2.||||
||a node and the weights of the edges are evaluated by the cosine similarity. In||||||
||order to rank the sentence, it uses the text ranking algorithm.||||||

Table 8: A significant compilation of ATS systems that use word embeddings.

[page 32]

## 6.2 Heuristic-based methods

As above-mentioned, the field of ATS started with the heuristic approach of Luhn (1958). As stated in this work, we should evaluate the importance of a sentence according to the frequency of the words that form it. In particular, in Luhn’s work, the significance of a word depends on the frequency within the document, according to the following rules: (1) It does not consider pronouns, prepositions, and articles[9] ; (2) It does not consider least frequent words; (3) Words lying in the frequency range above least frequent are the significant ones. However, in order to select the sentences that should be extracted, this work also considers a heuristic evaluation of the physical distance among the significant words in a sentence that is used to determine the clusters of significant words. Using these definitions, relevant sentences are the ones that have clusters with a large number of significant words. Edmundson and Wyllys (1961) make an important contribution since it is probably the first work that calls attention to the use of more informative measures of word frequency (such as the ones presented in Section 6.1.1) than the simple frequency.

It is worth citing Baxendale (1958), who compares three methods to extract the essential information of a text in order to mimic the way an average reader scans the content of a paper. The methods are based on scanning of topic sentences (the first sentence in 85% of the cases), a syntactical deleting process (stop word removal), and an automatic selection of prepositional phrases (units of expression, composed of a preposition, a noun, or pronoun, together with appropriate modifiers). It shows that the three methods provide equivalent results. Furthermore, one particular contribution of this paper is emphasizing the importance of the feature of sentence position in scanning the content of texts. However, this feature was further investigated in Lin and Hovy (1997) showing that we cannot define the position of the topic sentences a priori as in Baxendale (1958) since the discourse structure significantly varies over domains. Thus, Lin and Hovy (1997) find the optimal position of the sentences by comparing them with the keywords associated with the text. They also evaluate the quality of the method by comparing the topic sentences determined by this method with the sentences found in abstracts provided by humans.

Edmundson (1969) includes additional heuristics to evaluate the importance of a sentence. This work particularly considers four methods: (1) Cue method (the presence of cue words): It considers that the relevance of a sentence is affected by the presence of pragmatic words such as “significant”, “impossible” and “hardly”. (2) Key method (the presence of Keywords): It considers like Luhn (1958) topic words based on frequency; (3) Title method: It considers the presence of the words in specific parts of the document such as the title or the headings; (4) Location method (position of the sentences): It assumes that important sentences may arise in specific parts of the document such as the beginning or the end.

There are many methods for ATS that use heuristics. We present a significant compilation of these methods in Table 9.

> 9We refer to these words today as “stop words” and they are usually filtered out before any natural language processing analysis.

[page 33]

|Source|Main contribution|Dataset||Evaluation|
|---|---|---|---|---|
|Luhn (1958)|Seminal work. It uses the raw frequency of the words and a heuristic method|50 articles ranging from 300 to||Human experts|
||to evaluate the distance of significant words in sentences.|4,500 words each.|||
|Baxendale (1958)|It compares three heuristics (scanning of topic sentences, a syntactical delet-|6 technical articles||Comparative frequencies between the|
||ing process and selection of prepositional phrases).|||abstracts generated by the author, au-|
|||||tomatically and by human experts.|
|Edmundson (1969)|Besides the frequency of the words in the document, it also considers the|200 Technical documents with||Human experts and a kind of precision|
||position of the sentences, the presence of certain specific words, and the in-|approximate<br>lengths|ranging|and recall of the extracted sentences.|
||formation provided by the title.|from 100 to 3900 words, with|||
|||an average of 2500.|||
|White et al. (2003)|In a query-based setup, it extracts sentences based on four attributes: title,|Experiment-based task.||Human experts|
||location, sentence position and relation to the query.||||
|Yih et al. (2007)|In a multi-document setup, it introduces heuristics to evaluate the average|DUC 2004 and MSE|2005|ROUGE-1, ROUGE-2 and ROUGE-|
||position of the word in a cluster of documents and it assumes that good|||SU-4|
||summaries should favor words with low averages. It builds a score for the||||
||sentences based on the average position and the frequency of the words. It||||
||selects the best sentences using a stack decoder10 algorithm.||||

Table 9: A representative compilation of the ATS methods that use sentence heuristics.

[page 34]

## 6.3 Linguistic-based methods

There are different attempts to extract sentences to form abstracts based on linguistic methods. We may use the same classification that Saranyamol and Sindhu (2014) suggested to classify full abstractive methods to be mentioned in Section 7.1, namely structured-based and semantic based. The structured-based approach uses cognitive schema such as a set of rules, a template, a tree parser and a domain ontology. On the other hand, the semantic-based approach starts with a semantic representation of the document and uses this representation to identify the most important sentences of the document.

Rush et al. (1971) is one of the first works to include linguistic information to decide whether a sentence should belong to the summary. Although this work shares several ingredients with Edmundson (1969), it has a clear concern about making inferences about the contextual importance of the sentence in a structured-rule-based approach. Thus, it provides a set of rules to select or not select a given sentence based on the extensions of the location method and cue method introduced by Edmundson (1969), and reviewed in Section 6.2. The authors assume that the location method is based on the physical arrangement of the linguistic elements of an article. This arrangement can be described in terms of the location of a sentence in the document, the location of words, or the punctuation in a sentence. They suggest that while the location of the sentence in a document is very subjective and it depends on the authors’ choices, it is possible to get some pieces of relevant information using the location of words or punctuation in a sentence. Additionally, they claim that question marks should never be included in the summary for the following reasons: (1) they never provide a complete description of the facts; (2) if a question is selected, then the context behind the question should also be selected. It is worth mentioning that this discussion about whether a piece of text should be included provides the basic ideas for abstractive summarization discussed in Section 7. On the other hand, it defends that the cue method provides a powerful approach to sentence selection or rejection. For instance, words such as “Our work,” “This paper,” and “Present research”, which are used to state the purpose of a paper, serve to indicate that such sentences should be selected for the abstract. On the other hand, opinions, or references to figures or tables such as “obvious”, “believe”, “Fig.” “Figure 1”, and “Table IV” should not be included in an abstract. Furthermore, cue words may also indicate the presence of inter-sentence references that are fundamental to the creation of an abstract.

We may find an interesting example of a structured-ontology-based approach in Wu and Liu (2003). A domain ontology is a set of concepts and categories in a given subject area that shows their properties and the relations between them. Wu and Liu (2003) encode an ontology with a tree structure, and each node includes the concepts represented by the node’s children. When the count of any node increases, the counts associated with their ancestors also increase. They use this principle to score paragraphs. After marking the counts of the nodes in the ontology, the authors select second-level nodes that have higher counts as the main subtopics of the article. In order to implement the method, the authors only consider the top n subtopics. Their system uses the obtained subtopics to select paragraphs to form the summary. They rank the paragraphs based on their “closeness” to the selected subtopics by counting the words in common between the paragraph and each selected subtopic. Since we select n possible subtopics, there are also n scores associated with each paragraph, and these n scores represent the relevance of the n paragraphs for each selected topic. They assume that the score of each paragraph is the sum of its weighted relevance to the topics.

We may find a kind of informative semantic-graph-based approach for multi-document summarization in Canhasi and Kononenko (2011). The authors use a semantic role labeling parser to extract each argument of the sentence. Semantic role labeling assigns labels to words or phrases indicating their semantic role. It is often described as a technique to answer “Who did what to whom”. Thus, the authors calculate the composite similarity between all semantic frames based on the event-indexing model (Zwaan et al., 1995) to keep track of five indices,

[page 35]

namely temporality, spatiality, causality, and intention. Then, they generate a semantic graph where nodes are semantic frames and edges are the composite similarity values. In order to choose the most important sentences, they modify the Page Rank, used in Section 6.1.3, in order to identify the most significant edges in the graph.

Reeve et al. (2006) present an interesting semantic-lexical-chain approach that uses semantically related concepts to identify the sentences useful for extraction. A lexical chain is a sequence of semantic-related ordered words (Morris and Hirst, 1991). WordNet[11] is an excellent source to extract lexical chains. For example, this lexical chain was extracted from WordNet: “device → musical instrument → string instrument → guitar → electrical guitar”. Reeve et al. (2006) use a “part-of-speech” tagger and a comprehensive thesaurus to map words in concepts. The sentences to be extracted are the ones that present the most important concepts.

Table 10 significant compilation of ATS systems based on linguistic-extractive summarization.

> 11WordNet is a large lexical database of English. It groups nouns, verbs, adjectives, and adverbs into sets of cognitive synonyms, the so-called synsets, each expressing a distinct concept (Miller, 1995; Fellbaum, 2000; Princeton University, 2022). Although WordNet superficially resembles a thesaurus, there are two main differences: (1) WordNet interlinks specific senses of words; (2) WordNet labels the semantic relations among words, whereas the groupings of words in a thesaurus does not follow any explicit pattern other than meaning similarity.

[page 36]

||Source|Type|Main contribution|Dataset|Dataset|||||Evaluation|||
|---|---|---|---|---|---|---|---|---|---|---|---|---|
||Rush et al. (1971)|Structured-rule|Seminal work. It explores the application of the Po-|5 academic||papers||||Human experts|||
||||sition and Cue methods to make inferences about the||||||||||
||||context importance of a sentence. Its implementation||||||||||
||||is based on a word list and a set of rules implementing||||||||||
||||certain functions specifed for each word entry.||||||||||
||Wu and Liu (2003)|Structured-ontology|This work encodes the ontology with a tree structure.|Collected||articles||from|The|Precision,|Recall|and|
||||A paragraph is said to be relevant if its words arise in|New<br>York||Times||and|Wall|F-measure|of the|se-|
||||the topics more common in the piece of text.|Street Journal|||with|summaries||lected paragraphs.|||
|||||from the ProQuest database.|||||||||
||Chen and Verma (2006)|Structured-ontology|In a query-based setup, it uses an ontology to create|The|paper||Tashimo||et al.|Precision and recall of|||
||||a summary with extracted sentences that are close to|(2004).||||||extracted sentences.|||
||||the provided query.<br>It works in five steps: (1) The||||||||||
||||user provides a query; (2) The query is revised by an||||||||||
||||ontology; (3) It calculates the distance of each sentence||||||||||
||||of the document to the query; (4) It calculates the||||||||||
||||pairwise distance between the sentences in order to||||||||||
||||avoid redundancy; (5) It divides the sentences into||||||||||
||||groups and selects the highest one from each group.||||||||||
||Reeve et al. (2006)|Semantic-lexical-chain|It maps words in concepts and extracts the sentences|Drexel|University dataset||||with|Human experts|||
||||with the most important concepts.|approximately|||1,200 oncology||||||
|||||clinical|trial documents||||that||||
|36||||have been manually selected,<br>evaluated, and summarized.|||||||||
||Canhasi and Kononenko (2011)|Semantic-graph|This work builds an informative semantic-graph-based|DUC 2004||||||ROUGE-1|||
||||approach on the event-indexing model (Zwaan et al.,||||||||||
||||1995) for multi-document summarization to keep track||||||||||
||||of four dimensions, namely temporality, spatiality,||||||||||
||||causality, and intention. It uses a modifed Page Rank||||||||||
||||to select the most important sentences.||||||||||
||Saleh and Weigang (2017)|Structured-rule|It proposes a structured-rule approach that does not|DUC|2002,||TeMario,||and|ROUGE-1||and|
||||depend on specific characteristics of the language. It|French|and|Spanish||documents||ROUGE-2|||
||||extracts sentences that have higher scores that depend|collected from|||news|websites.|||||
||||on sentence shapes (for instance, the number of words||||||||||
||||with capital letters) and n-grams statistics.||||||||||
||Mohamed and Oussalah (2019)|Semantic-graph|This work presents a semantic-graph-based approach|DUC 2002||||||ROUGE-1,|ROUGE-2||
||||for single- and multi-document summarization. It uses|||||||and ROUGE-SU-4|||
||||semantic role labeling to build a semantic represen-||||||||||
||||tation of documents and it pairs matching roles for||||||||||
||||any two sentences. Then, it maps the sentences onto||||||||||
||||their corresponding concepts in Wikipedia. It builds a||||||||||
||||weighted semantic graph where each sentence is mod-||||||||||
||||eled as a multi-node vertex containing the Wikipedia||||||||||
||||concepts of its semantic arguments. It scores the sen-||||||||||
||||tences using the Page Rank algorithm.||||||||||

Table 10: A significant compilation of ATS systems based on linguistic-extractive summarization.

[page 37]

## 6.4 Supervised machine learning-based methods

The objective of using supervised machine learning methods in ATS is to explore the problem of ATS as a binary classification problem in which we use supervised methods of machine learning to select the sentences that should arise in the summary using their features.

This classical and conventional approach follows the steps:

1. Tag the sentences manually in the documents as positive ones (the ones that should be extracted to build the summary) and the negative ones (the opposite).

2. Select the features associated with each sentence that are used as inputs in the classification algorithm. These features may be word-based features and sentence-based features. The word-based features may be, for instance, weights that come from the space vector representation or the word embeddings. On the other hand, the sentence-based features may be the sentence position or the sentence length.

3. Estimate the model. These models usually have hyperparameters that have to be set before the estimation of the parameters. Since there is no way to choose these hyperparameters without data experimentation, a cross-validation[12] (Stone, 1978) procedure is necessary.

4. Apply the classification algorithm to find out the sentences that should be included in the summary.

There are several supervised machine learning classifiers in the literature and, in essence, we can use any of them. A machine learning classifier is a mathematical model that, given a set of attributes, provides a label associated with a class. The most popular are the logistic regression (Berkson, 1944, 1951) and their regularized versions LASSO-logistic, Ridge-logistic and elastic-net logistic (Friedman et al., 2010; Simon et al., 2011), maximum entropy classifier (Nigam et al., 1999), naive Bayes (Duda et al., 1973; Domingos and Pazzani, 1997), hidden Markov model (Rabiner and Juang, 1986), the Tree-based approaches such as decision tree (Breiman et al., 1984), random forest (Breiman, 2001) and gradient boosting (Friedman, 2001), the Support Vector Machine (SVM) (Cortes and Vapnik, 1995) and its rank version (Joachims, 2006), and the multilayer perceptron (Rumelhart et al., 1985). We may find a review of the supervised machine learning methods in Bishop and Nasrabadi (2006) and Izenman (2008) and a review of classical neural network models in Haykin (1994).

On ther other hand, modern approachs based on neural networks are able to replace the second and third step above by the automatical selection of a “composition” of features that are able to solve the binary classification problem of extractive summarization. There are different neural network models that we can use such as multilayer perceptron (Rumelhart et al., 1985), convolution neural networks (Zhang et al., 1988; LeCun et al., 1989; Li et al., 2021b) and sequence-to-sequence neural network models as reviewed in Section 7.2. We may find a review of the deep neural network models in Goodfellow et al. (2016).

It is worth mentioning that one difficulty that this approach faces is that human-made summaries are usually not extractive. Thus, there are few datasets available for this purpose, such as the DUC 2002 dataset (Over et al., 2007) and CNN (Lins et al., 2019). However, these datasets are small compared with other human-made datasets available (for instance, datasets formed by summaries of scientific papers). Thus, one relevant issue is how to create a dataset with a large number of documents with sentences labeled as to whether they should be extracted or not. The general approach to executing this task is to label the sentences of a document based on a human-made summary. Therefore, we have to solve the inverse problem of finding

> 12Cross-validation is a resampling method that splits the data into different sets in order to test and train a model on iterations.

[page 38]

the sentences that we have to extract to meet the human-made summary. In practice, this is done by a function that associates some statistics of the sentences of the document we need to summarize to the labels 0 or 1. We may find an example of this approach in Cheng and Lapata (2016) where they use the highlights created by editors to label the sentences of news articles. We may find another example in Nallapati et al. (2017). The authors assign the label 1 to the sentences that maximize the ROUGE score of the human-made summaries. We should note that the problem of adjusting datasets for natural language processing is not limited to the field of ATS. Several approaches, for instance, were introduced to augment datasets (Chen et al., 2021; Feng et al., 2021; Shorten et al., 2021).

The first paper that used a supervised approach to extractive summarization is Kupiec et al. (1995). This work uses several sentence features such as whether the sentences include the most frequent words of the document, whether the sentences include words presented in the title or in the list of keywords associated with the document, the position of the sentences in the document (important sentences usually arise at the beginning or the end of the document) and if the sentences contain indicator phrases such as ”This report (...)”. We may find an interesting contribution to summarization in Conroy and O’leary (2001). With the motivation to model the local dependencies between sentences, the authors use a Hidden Markov Model (HMM) that models the transitions between sentences that should or should not belong to the summary. They use only three features, namely the position of the sentence in the document, the number of terms in the sentence, and how likely sentence terms are in the document.

Osborne (2002) calls attention to the fact that the assumption of independence of features of the Naive Bayes is a strong assumption and the maximum entropy classifier outperforms this model. In particular, this work uses the following features: word pairs, which simply tells whether a particular word pair is present, sentence position, which indicates whether the sentence belongs to the beginning, the middle or the end of the document and discourse features, which informs if the sentence belongs to the introduction or conclusion or is located in the start of the paragraph.

An interesting contribution comes from Svore et al. (2007) that uses a feedforward neural network to find the most important sentences of a piece of text. The neural network is trained using the RankNet algorithm (Burges et al., 2005)[13] . For each sentence, the work considers several features such as the position of the sentence, n-grams of words in the sentence, terms common with the title and the presence of some specific words such as in Edmundson (1969). A particular innovation in this work is to use features from third-party sources such as query logs from Microsoft’s news search engine[14] and Wikipedia[15] entries.

Leskovec et al. (2005) and a sequence of papers (Leskovec et al., 2004a,b; Rusu et al., 2009) extract semantic information such as subject–object–predicate triples, co-reference resolution and anaphora resolution and use these pieces of information as additional inputs of a classifier. The other inputs are the location of the sentence within the document, the triplet location within the sentence, the frequency of the triplet element, the number of named entities in the sentence and the similarity of the sentence with the centroid (the central words of the document).

Jain et al. (2017), besides using several of these previously discussed attributes to characterize the sentences of a document, they also use the mean of word embeddings associated with each word of a sentence as an additional attribute.

In order to deal with a query-based task, AttSum (Cao et al., 2016) builds a convolutional neural network composed essentially of three major layers: (1) A convolutional neural network layer to project the sentences and queries onto the embeddings; (2) A pooling layer to combine

> 13RankNet is a pair-based gradient descent algorithm used to rank a set of inputs, in this case, the set of sentences in a given document.

> 14 http://search.live.com/news or http://www.bing.com/news

> 15http://www.wikipedia.org

[page 39]

the sentence embeddings to form the document embedding in the same latent space and to indicate the query relevance of a sentence; (3) A ranking layer that ranks sentences according to the similarity between its embedding and the embedding of the document cluster.

The sequence-to-sequence neural networks models (Nallapati et al., 2017; Zhou et al., 2018; Liu and Lapata, 2019), discussed in Section 7.2, as we mention in the beginning of the section, different from the classical and conventional approaches, are able to automatically extract features of the sentences and represent them mathematically by internal weights of the neural network that can be used to classify the sentences as the ones that should belong to the summary.

Finally, it is worth mentioning that these works use attributes that come from different models previously discussed, such as frequency metrics presented in Section 6.1.1, word embeddings presented in Section 6.1.5 and heuristic choices as in Section 6.2.

There are many supervised machine learning methods for ATS systems. We present a significant compilation of these methods in Table 11.

[page 40]

||Source|Model||||Features|Dataset|Dataset||||||Evaluation|||
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
||Kupiec et al. (1995)|Naive Bayes||||Sentence attributes: the presence of frequent or special words, the|188|document-summary||||||Precision and Recall of the|||
|||||||position and the presence of indicator phrases.|pairs,|sampled||||from||sentences|||
||||||||21<br>publications|||in|||the||||
||||||||scientifc<br>and|||technical|||||||
||||||||domains.||||||||||
||Conroy and O’leary (2001)|HMM||||Sentence attributes: the position, number of terms, and how likely|TREC Conference data||||||set|A kind of Recall of the||sen-|
|||||||sentence terms are in the document.||||||||tences|||
||Osborne (2002)|Maximum||entropy||Sentence attributes: word pairs and different measures of sentence|80|conference|||papers|||Precision,|Recall and F-||
|||classifier||||position (position in the document, if it belongs to introduction or|(Teufel, 2001)|||||||measure.|||
|||||||conclusion, position in a paragraph).|||||||||||
||Leskovec et al. (2005)|Support|||vector|Sentence attributes: subject, predicate, object triples, part of speech|DUC|2002||||||Precision,|recall<br>and|F1|
|||machine||||tags, and about 70 semantic tags (such as gender, location name,||||||||measures of the extracted|||
|||||||person name), location of the sentence in the document and the triple||||||||sentences and ROUGE-1|||
|||||||in the sentence, frequency, location of the word inside the sentence|||||||||||
|||||||and number of different senses of the word.|||||||||||
||Svore et al. (2007)|Feedforward|||neu-|Sentence attributes: position, n-grams of words, terms common with|1365|news|documents|||||ROUGE-1|and ROUGE-2||
|||ral network||||the title, the presence of some specific words, query logs from Mi-|gathered from CNN.com.||||||||||
|||||||crosoft’s news search engine and Wikipedia entries.|||||||||||
||Fattah and Ren (2009)|Linear regression,||||Sentence attributes: position, positive and negative keywords, sen-|200 Arabic articles||||about|||Precision|||
|||neural|network,|||tence centrality, Sentence resemblance to the title, sentence inclusion|politics and 150 English||||||ar-||||
|||gaussian||mixture||of name entity or numerical data and sentence relative length.|ticles|about religion|||||||||
|40||model|||||||||||||||
||Nguyen et al. (2016c)|SVM rank||||This is a social context summarization approach. It uses a lot of fea-|Solscsum and USAToday-|||||||ROUGE-1|and ROUGE-2||
|||||||tures and it splits into local features (such as sentence attributes and|CNN||||||||||
|||||||different measures of similarities) and social features (that measure|||||||||||
|||||||the similarities between a sentence and the comments associated with|||||||||||
|||||||it).|||||||||||
||Cao et al. (2016)|Convolution|||neu-|In order to deal with a query-based task, It introduces a neural net-|DUC|2005 and DUC||||2007||ROUGE-1|and ROUGE-2||
|||ral network||||work model with an additional layer that aims to learn the query|||||||||||
|||||||relevance of the sentence.|||||||||||
||Jain et al. (2017)|MLP||||Sentence attributes: mean TF-ISF, length, position, correlation with|10K|documents||||from||ROUGE-1,|ROUGE-2|and|
|||||||other sentences, correlation with the document centroid, depth of tree|CNN|news article|||corpus|||ROUGE-L|.||
|||||||in an agglomerative cluster, presence of keywords, presence of proper|having<br>90K||documents||||||||
|||||||names, presence of non-essential information and mean GLOVE word|(Hermann et al.,|||2015)|||||||
|||||||embedding.|||||||||||
||Nallapati et al. (2017)|GRU|Recurrent|||The GRU (Cho et al., 2014)is able to recover sentence characteristics|CNN/DailyMail|||||||ROUGE-1,|ROUGE-2|and|
|||Neural Network||||such as content, saliency and novelty.||||||||ROUGE-L|||
||Zhou et al. (2018)|Bidirectional||||It builds a model based on an encoder and a sentence extractor. The|CNN/Daily Mail|||||||ROUGE-1,|ROUGE-2|and|
|||GRU and RNN||||encoder uses a bidirectional GRU (Cho et al., 2014) to create a rep-||||||||ROUGE-L|||
|||||||resentation of the sentences.<br>The sentence extractor is a recurrent|||||||||||
|||||||neural network that remembers the partial output summary and pro-|||||||||||
|||||||vides a sentence extraction state that can be used to score sentences|||||||||||
|||||||with their representations.|||||||||||
||Liu and Lapata (2019)|BERT||||The modifed BERT transformer (Devlin et al., 2018) for extractive|CNN/DailyMail|||||||ROUGE-1,|ROUGE-2|and|
|||||||summarization is capable of extracting automatically the features in||||||||ROUGE-L|||
|||||||the internal layers.|||||||||||

Table 11: A significant compilation of ATS systems that use supervised machine learning.

[page 41]

## 6.5 Reinforcement learning based methods

A reinforcement learning problem explores a situation where the objective is to map states to actions in order to maximize a numerical reward signal. We usually define a reinforcement learning solution with the following ingredients (Puterman, 2014; Bertsekas, 2012; Bertsekas et al., 2011; Bertsekas and Tsitsiklis, 1996; Sutton and Barto, 2018):

1. An agent (the learner or the decision-maker) that interacts with the environment in a sequence of instants t = 0, 1, 2, · · · .

2. At each instant t, the agent faces a state st ∈S, where S is a finite set of possible states, and selects an action at ∈A(st), where A(st) is the set of admissible actions contingent to the state st.

3. At each state the agent receives a reward that is contingent to the chosen action r : St × A(st) →ℜ. We usually assume that maxs∈S maxa∈A(s) r(s, a) < ∞.

4. In each state, the agent maps states to probabilities of selecting a possible action. This map is called agent policy and it is denoted by Πt, where Πt(s, a) is the probability that at = a when st = s.

5. In each state st, the agent intends to maximize the expected value of the return given by

**==> picture [341 x 33] intentionally omitted <==**

where the return is given by Rt =[�][∞] k=0[γ][k][r][t][+][k][+1][and][E][π][ ��][∞] k=0[γ][k][r][t][+][k][+1] st = s is the � � expected value of the discounted sequence of rewards received by the agent assuming that in the beginning of the trajectory it was in state s and, from this state, it followed the policy π. A common assumption is that the rewards are bounded and the distributions of rewards and states are stationary. The discount factor 0 < γ < 1 has two functions. From the economic point of view, it makes explicit the value of money over time. On the other hand, from the mathematical point of view, it ensures that under mild regularity conditions, there is an optimal policy that maximizes the performance index presented in Eq. (7). Another important assumption here is that we may describe the transitions between the states as a Markovian process, i.e.,

**==> picture [406 x 13] intentionally omitted <==**

This assumption allows a parsimonious representation that reduces the computational complexity of the problem and simplifies the definition of the transition matrices, the reward structure and the set of admissible actions.

6. If the rewards and the transition probabilities are known and stationary, we may show that the solution of the problem is given by the Bellman equation:

**==> picture [99 x 14] intentionally omitted <==**

where Pπ = [Pss′] is the transition matrix contingent to the policy π, Rπ = [Rs] is the returns vector contingent to the policy π, Pss′ =[�] a∈A(s)[q] s[a][P] ss[ a][′][,][R][a] ss[′][=][E][[][r][t][+1][/s][t][=] s, at = a, st+1 = s[′] ] and qs[a][is][the][probability][of][using][the][action][a][in][state][s][.][In][order] to solve this problem, we need to know the value function given the policy π, which is a problem known as policy evaluation, and to improve the policy given another policy, which is a problem known as policy improvement. Note that the problem of policy evaluation is

[page 42]

equivalent to finding the solution of a linear system, i.e., given the policy and assuming that the rewards and probabilities are stationary and known, Eq. (9) is a linear system. We can prove that the operator L(v) = Rπ + γPπv is a contraction and, according to the Banach fixed point theorem, it can be solved by fixed point iterations[16] . In order to improve the policy, we use the Q-function Q[π] (s, a) = Eπ[Rt/st, at = a], that is the expected return for taking action a in state s and thereafter following an optimal policy. Thus, if Q[π] (s, a) > v[π] (s), then π can be improved if π(s) is replaced by a. There are two popular algorithms to solve this problem, namely policy iteration and improvement (Watkins, 1989) and value iteration (Puterman and Shin, 1978). While in the former approach the policy improvement and policy evaluation tasks are run in separate loops, in the latter, these are carried out in the same loop.

7. When the transition probabilities and rewards are not known, we use Monte Carlo methods to sample sequences of states, actions, and rewards (Michie and Chambers, 1968; Barto and Duff, 1993; Singh and Sutton, 1996). The policy evaluation and policy improvement steps are completed using average returns of episodic tasks.

8. Temporal difference learning methods combine Monte Carlo and dynamic programming approaches (Sutton, 1988). They learn from experience like the Monte Carlo methods and they update estimates like the dynamical programming approach. Two algorithms can be used to implement the temporal difference approach, namely SARSA (an Acronym for State-Action-Reward-[next]State-[next]Action) and Q-learning. While the Q-learning approach updates the value function using a greedy action approach (Rummery and Niranjan, 1994; Sutton, 1995), SARSA updates with the actual action used for generating experience by the agent (Watkins, 1989).

Ryang and Abekawa (2012), in order to formulate the problem of extractive summarization as a reinforcement learning problem, reduce the document to be summarized in a set of n sentences, define a score function for any subset of sentences of the document S ⊂ d, where S is one of the possible summaries and d is the document, and also define the length function that indicates the size of the summary. They use a temporal difference learning approach to find the summary that maximizes the score function that considers a trade-off between relevance and redundancy subject to the maximal summary length. Thus, in this problem, a state is a summary of a given length. In this work, the actions are deterministic and are basically the decision to include or not a given sentence. The reward is defined in such a way that the agent only receives the rewards when the summary reaches the final size. The score function specifically depends on the coverage of important words (the count of top-100 words in terms of the TF-IDF included), coverage ratio (the count of top-100 elements included), redundancy ratio (the counting of the number of elements that excessively cover the top 100 elements), length ratio (the ratio between the length of the summary and length limitation) and the sum of the inverse position of the sentences.

We may find an extension of the work of Ryang and Abekawa (2012) in Rioux et al. (2014). In a multi-document setup and also working with a query-based task, they use the SARSA algorithm, explore different types of rewards (not only delayed rewards as in the case of Ryang and Abekawa (2012)) and also use the ROUGE to evaluate the similarity between the reference summary and the automatic summary.

There are other reinforcement-based approaches for ATS systems. We present a significant compilation of these methods in Table 12.

> 16See, for instance, Puterman (2014).

[page 43]

|Source|Main contribution|Dataset|Evaluation|
|---|---|---|---|
|Ryang and Abekawa (2012)|It introduces a reinforcement learning model for ex-|DUC 2004|ROUGE-1, ROUGE-2|
||tractive summarization.||and ROUGE-3|
|Rioux et al. (2014)|In a multi-document approach, it extends the work|DUC 2004 and DUC 2006|ROUGE-1, ROUGE-2|
||of Ryang and Abekawa (2012) using the SARSA algo-||and ROUGE-L|
||rithm, considering different types of rewards and using|||
||the ROUGE as a measure of similarity.|||
|Henß et al. (2015)|In a multi-document summarization setup, it extends|DUC 2001, DUC 2002, DUC|ROUGE-2, ROUGE-2|
||the work of Ryang and Abekawa (2012) using the Q-|2004, ACL and Wikipedia|and ROUGE-L|
||learning algorithm and considering the reference sum-|||
||maries in the training phase.|||
|Moll´a (2017)|In order to deal with a query-based task, it extends|BioASQ 5b Phase B|ROUGE-L|
||the work of Ryang and Abekawa (2012) including the|||
||use of the reference summary in the evaluation of the|||
||reward.|||
|Lee and Lee (2017)|It explores the advantages of embedding features in a|DUC 2001, DUC 2002, ACL-|ROUGE-2|
||Q-learning model and also designs a deep neural net-|ARC and Wikipedia||
||work to approximate the value function.|||
|Narayan et al. (2018a)|It formulates the problem of extractive summariza-|CNN and Daily-Mail|ROUGE-1, ROUGE-2|
||tion as a sentence ranking problem using reinforcement||and ROUGE-L|
||learning and it uses a neural network model to encode|||
||the features of the sentences.|||
|Yao et al. (2018)|It develops a neural network for both encoding the fea-|CNN and Daily-Mail|ROUGE-1, ROUGE-2|
||tures of the sentences and also choosing the sentences||and ROUGE-L|
||that must be included in the summary.|||

Table 12: A significant compilation of ATS systems that use reinforcement learning techniques.

[page 44]

## 7 Abstractive summarization

Different from extractive summarization, which builds a summary from the combination of the important sentences previously extracted from the original text, in abstractive summarization, we need a language model to rewrite the summary from scratch. We split this section into two subsections. While in subsection 7.1 we present the ATS systems based on classical linguistic models, in Subsection 7.2 we present the modern methods based on sequence-to-sequence neural network models.

## 7.1 Linguistic approaches

As we have mentioned in Section 6.3, we may split the linguistic approaches to abstractive summarization into two large groups, namely structured-based and semantic-based (Saranyamol and Sindhu, 2014).

An example of the structured-based approach that uses a rule-based scheme is Genest and Lapalme (2012). In this work, in order to provide summaries in the fields of “Accidents and Natural Disasters”, “Attacks, Health and Safety”, “Endangered Resources”, and “Investigations/Trials”, the authors use handcrafted information extraction rules, content selection heuristics and generation patterns. In particular, to extract the information they need to build the summary, they ask the following questions: (1) What: what happened; (2) When: date, time, other temporal placement markers; (3) Where: physical location; (4) Perpetrators: individuals or groups responsible for the attack; (5) Why: reasons for the attack; (6) Who was affected: casualties (death, injury), or individuals otherwise negatively affected; (7) Damages: damages caused by the attack; (8) Countermeasures: countermeasures, rescue efforts, prevention efforts, other reactions. With the answers to these questions in hand, extracted using predefined extraction rules, they use previously generated patterns to build the summaries. The reader may note that this is a particular example of an informative summary defined in Section 2.

An example of the structured approach that uses a template for multi-document summarization is Harabagiu and Lacatusu (2002). In this work, the authors use templates that represent each topic of the piece of text that need to be summarized and are populated using information extraction rules. In order to generate the summaries, they use a parse tree to identify the Subject-Verb-Object structures[17] and WordNet to classify the topic of each structure. The topics with a high frequency are included in the summary.

We may find an example of the structured-approach that uses a domain ontology in Lee et al. (2005). In this work, the authors extend a domain ontology using concepts of fuzzy logic by embedding a set of membership degrees in each concept of the domain ontology. They use this fuzzy domain ontology to extract the sentences related to the text domain and to generate the abstract by concatenating concepts with relations.

We may find one of the first examples of the semantic-based approach in Genest and Lapalme (2011). This work proposes the concept of Information Items (INITs) to help to define the abstract representation, which is the smallest element of coherent information in a text or a sentence. The goal is to identify all entities in the text, their properties, the predicates between them, and the characteristics of the predicates. In that work, the implementation of INITs is constrained to dated and located subject–verb–object (SVO) triples and the summary generation as above-mentioned is carried out using parse trees. This work is another example of an ATS that generates informative summaries.

Another interesting example of the semantic based approach is the multimodal model of Greenbacker (2011). We may summarize the implementation of this model in three steps: (1) Building the semantic model: The semantic model, which should consider both images and pieces of text, is built based on a knowledge representation based on a domain ontology; (2)

> 17In linguistic, subject–verb–object (SVO) is a sentence structure where the subject comes first, the verb second, and the object third.

[page 45]

Rating the informational content: In order to rate the content, the authors propose the so-called information density metric (ID) which rates a concept’s importance based on factors such as completeness of attributes, the number of connections with other concepts and the number of expressions that put the concept in evidence; (3) Generating a summary: The work uses the concepts of TAG (Tree Adjoining Grammars) Derivation Trees[18] as in McDonald and Greenbacker (2010) to express the concepts and relationships found in previous steps.

Moawad and Aref (2012) implement the semantic-based approach using a semantic graph. The method consists of three steps: (1) The creation of the semantic graph called Rich Semantic Graph (RSG) for the original document; (2) The reduction of the generated semantic graph; (3) The generation of the final abstractive summary from the reduced semantic graph. In RSG, the verbs and nouns of the input document are represented as graph nodes along with edges corresponding to semantic and topological relations between them. The graph nodes are instances of the corresponding verb and noun classes in the domain ontology. The Rich Semantic Graph Reduction Phase aims to reduce the generated rich semantic graph of the source document to a reduced graph. A model of heuristic rules is applied to reduce the graph by replacing, deleting, or consolidating the graph nodes using the WordNet relations. Finally, the Summarized Text Generation Phase aims to generate the abstractive summary from the reduced rich semantic graph. To achieve its task, this phase accesses a domain ontology, which contains the information needed in the same domain of RSG to generate the final texts.

Table 13 presents a significant compilation of ATS systems based on linguistic abstractive summarization.

> 18A TAG is a formalism that builds grammatical representations through the composition of smaller pieces of syntactic structure (Joshi and Schabes, 1997).

[page 46]

||Source|Type|Main contribution|Dataset|Evaluation|||
|---|---|---|---|---|---|---|---|
||Harabagiu and Lacatusu (2002)|Structured-template|It presents a multi-document summarization approach|DUC 2002|Human experts|||
||||that uses a template to identify the important pieces of|||||
||||information, a tree parser to build subject-verb-object|||||
||||structures, the WordNet to identify the topics and gen-|||||
||||erates the abstract based on the high-frequency struc-|||||
||||tures.|||||
||Lee et al. (2005)|Structured-domain ontology|It extends a domain ontology using concepts of fuzzy|Chinese news of three weather||||
||||logic. It uses this domain ontology to extract the sen-|events,<br>including<br>“Typhoon||||
||||tences and to generate the abstract|event,” “Cold current event,”||||
|||||and “Rain event,” from the||||
|||||Chinatimes website in 2002,||||
|||||2003, and 2004.||||
||Genest and Lapalme (2011)|Semantic-INITs|It extracts sentences using a variety of methods and|Text<br>Analysis<br>Conference|Precision|and|Recall|
||||produces the summary with these sentences using a|(TAC) 2010|evaluated|by|human|
|46|Greenbacker (2011)|Semantic-multimodal|parse-tree.<br>It implements the model in three steps: (1) Building|An<br>article<br>from<br>the<br>May|experts<br>Human experts.|||
||||the semantic model based on a domain ontology; (2)|29, 2006 edition of Business-||||
||||Rating the information content based on completeness|week magazine entitled, “Will||||
||||of attributes, connections with other concepts and the|Medtronic’s Pulse Quicken?”.||||
||||number of expressions that put the concept in evi-|||||
||||dence; (3) Generating the summary using TAGs.|||||
||Genest and Lapalme (2012)|Structured-rule|It uses handcrafted information extraction rules, con-|Attack category of Text Anal-|Manual Pyramid|||
||||tent selection heuristics and generation patterns.|ysis Conference (TAC) 2011||||
|||||(Owczarzak and Dang, 2011)||||
||Moawad and Aref (2012)|Semantic-graph|It implements the model in three steps: (1) It cre-|A simulated case study called|Text<br>coherence||using|
||||ates the semantic graph; (2) It reduces the generated|“Graduate students”.|the original words of|||
||||semantic graph; (3) It generates the final abstractive||the sentences and using|||
||||summary from the reduced semantic graph.||the synonyms||of the|
||||||words of the sentences.|||

Table 13: A significant compilation of ATS systems based on linguistic abstractive summarization.

[page 47]

## 7.2 Sequence-to-sequence deep learning methods

Sequence-to-sequence deep learning models used for tasks of NLP are NN models in which the inputs and outputs are sequences of tokens of varying sizes. In order to explore the most recent approaches of sequence-to-sequence models we need to trace back to the first architectures of Recurrent Neural Networks (RNN) (Jordan, 1986; Elman, 1990). RNNs are sequence models that deal directly with two modeling constraints of the standard multilayer perceptrons that are essential to model sequences. First, it is assumed that the input sequences have the same length. Second, it’s an architecture that does not allow for the same token in different positions of the text to have similar features. The first ideas of RNNs arise in the seminal works of Jordan (1986) and Elman (1990). We may summarize the vanilla RNN by the set of equations:

**==> picture [297 x 14] intentionally omitted <==**

## and

**==> picture [273 x 14] intentionally omitted <==**

where x[i] is a token in a piece of text, y[i] is the token we want to predict, s[i] is the state of the RNN, Wss, Wax, Wys, bs and by are the parameters of the network that we need to learn and s[0] is a vector of zeros. Figure 3 represents this model. Like the other models of language, we try to predict the probability of the next word. Therefore, we may estimate the parameters of this model in a semi-supervised fashion using the backpropagation through time algorithm. Suppose, for instance, that your text includes the first sentence of the song Africa by the band Toto “I hear the drums echoing tonight.”. Thus, x[1] = “I”, x[2] = “hear” x[3] = “the”, x[4] = “drums”, x[5] = “echoing”, y[1] = “hear” y[2] = “the”, y[3] = “drums”, y[4] = “echoing” and y[5] = “tonight”. Thus, this algorithm tries to maximize the probability that the token “hear” arises when the token “I” is an input, to maximize the probability the token “the” happens when ”hear” is the input and s1 is the state of the system generated by “I” and so on. Unfortunately, vanilla RNNs are not good at dealing with long sequences. Problems that arise in this context are the so-called exploding and vanishing gradients (Bengio et al., 1993; Pascanu et al., 2013; Ribeiro et al., 2020). This happens naturally due to the algorithm of backpropagation, which is based on the chain rule of calculus, and the consequent multiplication of the same shared matrix of the parameters several times.

In order to overcome the difficulties of exploding and vanishing gradients, two important models of RNNs were introduced, namely Long Short-Term Memory (LSTM) (Hochreiter and Schmidhuber, 1997; Gers et al., 2000) and Gated Recurrent Units (GRU) (Cho et al., 2014) empirically explored in Chung et al. (2014). The basic idea behind these models is to replace the simple units of the vanilla RNN model with complex units which include gates that control the flow of information that passes from one unit to the other.

A natural extension of the vanilla RNNs is to consider the case where the input sequence and output sequence have different sizes. These models are called Encoder-Decoder models and they aim at mapping one sequence to another sequence (Sutskever et al., 2014; Vinyals and Le, 2015), where the encoder (decoder) is the part of the model that deals with the input (output) sequence. Figure 4 presents an example of this topology, where each unit of this model is the RNN unit (vanilla, LSTM or GRU). In this type of model, the intention is, given a sequence, to predict another sequence not necessarily of the same size. For example, consider that we want to use a sequence-to-sequence model to translate the first sentence of the song “Smoke on the Water” by the English band Deep Purple to Spanish. We may have x[1] =“We”, x[2] =“all”, x[3] =“came”, x[4] =“out”, x[5] =“to”, x[6] =“Montreux”, y[1] =“Todos”, y[2] =“salimos’”, y[3] =“a” and y[4] =“Montreux” in Figure 4, where Tx = 6 and Ty = 4.

A fundamental contribution to improving the learning process of sequence-to-sequence models is the attention mechanism (Bahdanau et al., 2014). The main idea behind this paper is to include a set of weights to inform the model about the context. For instance, consider again

[page 48]

the sentence “We all came out to Montreux”. We know that the phrasal verb “come out” has different meanings. However, in this sentence, it is obvious that the sense of this verb is “to go somewhere” and this happens because of the word “Montreux”, which is a town in Switzerland. In the work by Bahdanau et al. (2014), the authors evaluate the attention mechanisms by normalizing the output of a multilayer perceptron that depends on the state of the decoder model and the activation signal that comes from the encoder.

The most recent models of NLP are based on transformers. Transformers are networks models that comprise the idea of processing complex information in parallel[19] and an extension of the above-mentioned attention mechanism called multi-head attention (Vaswani et al., 2017). Multi-head attention is the idea of evaluating several attention models simultaneously. In a given sentence, we may use several attention mechanisms to explore several different dimensions at once. For instance, the chorus of the song “America” by Neil Diamond says “They’re coming to America today”. We may think of a multi-head mechanism as a way to help us ask and answer questions, i.e., it says where we should pay attention in a sentence to answer a given question[20] . Thus, the first question could be: “What is happening?”. Then, the answer is “They are coming somewhere.”. The second question could be “Where?”. Then, the answer is “America”. The third question could be “When?”. Then, the answer is “Today”. In the transformer network, this information is encoded in vectors called Queries (Q), Keys (K), and Values (V ). Like in the recurrent sequence-to-sequence models, the architecture of Transformer models has an encoderdecoder structure. The encoder model receives the embeddings (discussed in Section 6.1.5) of the inputs with a position encoding. The position encoding serves to inform the position of the token in the sequence, which is necessary here since this is a parallel model where the entire text is simultaneously inputted. The encoder block is formed by a stack of multi-head attention blocks connected with a feedforward network to generate the vectors Q, K and V that feed the following encoder blocks. The decoder block is a stack of an additional multi-head attention block and a block similar to the encoder block. The first block receives the output embeddings and generates the vector Q to be used together with the vectors K and V it receives from the encoder block. This model is used to generate the output sequence in a recursive fashion.

There is now a large list of transformers that have been used in successful NLP tasks such as Google’s BERT (Devlin et al., 2018), PEGASUS (Zhang et al., 2020), T5 (Raffel et al., 2019), and Switch (Fedus et al., 2021), Facebook’s BART (Lewis et al., 2019), and Open AI’s Generative Pre-Training (GPT) (Radford and Narasimhan, 2018), GPT-2 (Radford et al., 2019), and GPT-3 (Brown et al., 2020).

An extension of these models is the so-called Longformer (Beltagy et al., 2020), which is a modified Transformer architecture with a self-attention operation that scales linearly with the sequence length, making it versatile for processing long documents. Finally, it is worth mentioning that we may find a survey of pre-trained language models for text generation in Li et al. (2021a) and a survey of dynamic neural network models for natural language processing in Xu and McAuley (2022).

Table 14 presents a summary of the most popular transformers used for abstractive summarization with their main characteristics.

> 19This idea comes from the architecture of the Convolution Neural Network (CNN) that processes complex information in parallel (LeCun et al., 2015).

> 20It has the same role as the filters built automatically by NN models to identify dimensions of images in CNN.

[page 49]

**==> picture [416 x 210] intentionally omitted <==**

**----- Start of picture text -----**<br>
Figure 3: Vanilla RNN.<br>yˆ [<][1][>] yˆ [<][2][>] yˆ [<][3][>] yˆ [<T][y][>]<br>s [<][0][>] s [<][1][>] s [<][2][>] s [<T][x][−][1][>]<br>...<br>xˆ [<][1][>] xˆ [<][2][>] xˆ [<][3][>] xˆ [<T][x][>]<br>**----- End of picture text -----**<br>

**==> picture [402 x 124] intentionally omitted <==**

**----- Start of picture text -----**<br>
Figure 4: Sequence-to-sequence models.<br>yˆ [<][1][>] yˆ [<T][y][>]<br>... ...<br>xˆ [<][1][>] xˆ [<T][x][>]<br>**----- End of picture text -----**<br>

[page 50]

|Name|Source|Main characteristics|Dataset|||||Evaluation|
|---|---|---|---|---|---|---|---|---|
|BERT|Liu and Lapata (2019)|It is a bidirectional encoder model.|CNN-DailyMail,||XSUM||and|ROUGE-1, ROUGE-2|
||||NYT|||||and ROUGE-L|
|BART|Lewis et al. (2019)|It is a bidirectional encoder model with an autoregres-|CNN-DailyMail||and|XSUM||ROUGE-1, ROUGE-2|
|||sive decoder architecture.||||||and ROUGE-L|
|T5|Rafel et al. (2019)|It is essentially the original transformer model equiv-|CNN/DailyMail|||||ROUGE-2|
|||alent to Vaswani et al. (2017) with the normalization|||||||
|||layer outside the residual path, and using a different|||||||
|||position embedding scheme.|||||||
|GPT|Radford et al. (2019)|It is essentially the original transformer model equiv-|CNN/DailyMail|||||ROUGE-1, ROUGE-2|
|||alent to Vaswani et al. (2017).||||||and ROUGE-L|
|UniLM|Dong et al. (2019)|It is a transformer model shared among three different|CNN/DailyMail|||||ROUGE-1, ROUGE-2|
|||self-attention masks.||||||and ROUGE-L|
|MASS|Song et al. (2019)|It is a transformer model designed for encoder-|Gigaword|||||ROUGE-1, ROUGE-2|
|||decoder-based language generation tasks.||||||and ROUGE-L|
|UniLMv2|Bao et al. (2020b)|It is a transformer model shared among three different|CNN/DailyMail||and|XSUM||ROUGE-1, ROUGE-2|
|||self-attention masks.||||||and ROUGE-L|
|PEGASUS|Zhang et al. (2020)|It is essentially the original transformer model equiv-|XSUM,|CNN/DailyMail,||||ROUGE-1, ROUGE-2|
|||alent to Vaswani et al. (2017).|NEWSROOM,||Multi-News,|||and ROUGE-L|
||||Gigaword,|arXiv,||PubMed,|||
||||BIGPATENT,|||WikiHow,|||
||||Reddit<br>TIFU,||AESLC||and||
||||BillSum||||||
|Ernie-Gen|Xiao et al. (2020)|It is a transformer model with parameters shared|Gigaword|and CNN/DailyMail||||ROUGE-1, ROUGE-2|
|||among different tasks.||||||and ROUGE-L|
|ProphetNet|Qi et al. (2020)|It is a transformer model in the so-called future n-gram|Gigaword|and CNN/DailyMail||||ROUGE-1, ROUGE-2|
|||prediction as described in||||||and ROUGE-L|
|Longformer|Beltagy et al. (2020)|It is a modifed Transformer model with a self-|arXiv|||||ROUGE-1, ROUGE-2|
|||attention operation that scales linearly with the se-||||||and ROUGE-L|
|||quence length.|||||||

Table 14: A significant compilation of transformers used for abstractive summarization. Notes: BERT due to (Devlin et al., 2018) and trained by Liu and Lapata (2019) is the acronym for Bidirectional Encoder Representations from Transformers. GPT due to Radford and Narasimhan (2018) stands for Generative Pre-Trained model. BART due to Lewis et al. (2019) is the acronym for Bidirectional and Auto-Regressive. Pegasus due Vaswani et al. (2017) and trained by Zhang et al. (2020) is the acronym for Pre-training with extracted gap-sentences for abstractive summarization. T5 due to Raffel et al. (2019) stands for Text-to-Text Transfer Transformer. UniLM due to Dong et al. (2019) stands for Unified Language Model. MASS (Song et al., 2019) stands for MAsked Sequence-to-Sequence.

[page 51]

## 8 Compressive extractive approaches

Compressive extractive approaches usually depend on two steps: (1) We extract the sentences that should belong to the summary; (2) We compress the chosen sentences that come from the original text in order to present only essential information.

When selecting the sentences to be extracted, we usually rely on one of the methods already discussed in Section 6. On the other hand, in order to compress the sentences we need a model of language.

One advantage of the compressive extractive approaches over the pure extractive approaches is that for the case of the summaries that need to have a previously given constant length, the summaries created with the compressive approach usually contain more information than the summaries created with extractive approaches. This happens because by removing insignificant sentence components, we make room for more relevant information in the summary.

We have discussed many methods to extract sentences from the whole text in Section 6. On the other hand, sentence compression is by itself a research problem. It starts with the input which is a sentence with n words. The algorithm for sentence compression may drop any subset of these words and the words that remain with an unchanged order form a compression. Thus, the problem is not trivial since there are 2[n] possible pieces of text to be chosen (Clarke and Lapata, 2006). In order to solve this problem, we have to develop a method to determine what is the relevant piece of information in a sentence and how to present this information grammatically.

Although our focus here is on text summarization, it is worth mentioning that there are some interesting specific applications of solutions of the sentence compression (Knight and Marcu, 2000), such as the generation of TV captions that due to time and space constraints often requires only the most important parts of sentences (Zdenek, 2011) and audio scanning services for the blind (Grefenstette, 1998).

The precursors of compressive extractive summarization were the early attempts to provide text summaries in the style of newspapers headlines as in Witbrock and Mittal (1999) and Banko et al. (2000), where the summaries consist of a single sentence or even less than a sentence extracted from the text.

In order to implement the compressive step of compressive extractive summarization, we may use unsupervised, supervised methods or hybrid approaches.

The unsupervised approaches delete words based on part-of-speech tags[21] or the lexical items[22] alone. In particular, we may find a very interesting approach for unsupervised compressive summarization in Hori and Furui (2004). In order to generate a summary, their approach focuses on extracting topic words, weighting correct-word concatenations linguistically, and extracting reliable components of speech recognition acoustically as well as linguistically. A set of words maximizing a summarization score, indicating the appropriateness of a summarized sentence, is selected from those using a Dynamic Programming (DP) technique. The summarization score consists of word significance measured by the frequency of each word in the sentence, word confidence measured by the logarithm of the probability of n-grams, and the linguistic likelihood of summarized sentences.

> 21In linguistics, Part-Of-Speech (POS) tags, are tags used in a text (corpus) to associate a given word with its corresponding part of speech, based on both its definition and its context. The list of universal POS tags is: ADJ (adjective), ADP (adposition), ADV (adverb), AUX (auxiliary), CCONJ (coordinating conjunction), DET (determiner), INTJ (interjection), NOUN (noun), NUM (numeral), PART (particle), PRON (pronoun), PROPN (proper noun), PUNCT (punctuation), SCONJ (subordinating conjunction), SYM (symbol), VERB (verb) and X (other).

> 22A lexical item may be a single word, a part of a word, or a sequence of words that forms the basic elements of a language’s vocabulary. Examples of lexical items are: words (dog, table), phrasal verbs (get up, get over, get in, get on, idioms (“better late than never”, “pull yourself together”) and sayings (“An apple a day keeps the doctor away.”, “Actions speak louder than words.”).

[page 52]

Another interesting approach is the graph-based approach due to Filippova (2010) where a directed word graph is constructed. In this digraph, nodes represent words and edges represent the adjacency between words in a sentence. Thus, the authors can compress sentences by finding the k-shortest paths in the digraph.

The supervised approaches may depend on a number of resources such as an annotated corpus with the original sentences and their corresponding reduced forms written by humans for training and testing purposes, a lexicon[23] and a syntactic parser to generate a parse tree[24] .

Jing (2000) focuses specifically on the problem of sentence reduction of extracted sentences for summarization. The author assumes that the input of his system is the collection of extracted sentences that we can build using one of the methods of Section 6. On the other hand, his algorithm of sentence reduction has five steps: (1) Syntactic parsing: He parses the input sentence to produce the sentence parse tree; (2) Grammar checking: He determines which components of the sentence must not be deleted to keep the sentence grammatical. To do this, he traverses the parse tree generated in the first step in top-down order and marks, for each node in the parse tree, which of its children are grammatically obligatory; (3) Context information: The system decides which components in the sentence are most related to the main topic being discussed. To measure the importance of a phrase in the local context, the system relies on lexical links between words; (4) Corpus evidence: The program uses the annotated corpus consisting of sentences reduced by human professionals and their corresponding original sentences to compute how likely (measuring the probabilities) are humans to remove a certain phrase; (5) Final decision: The final reduction decisions are based on the results from all the earlier steps. To decide which phrases to remove, the system traverses the annotated sentence parse tree and removes a phrase when it is not grammatically obligatory, not the focus of the local context and has a reasonable probability of being removed by humans.

Another interesting approach to supervised compressive summarization explores the noisy channel framework (Knight and Marcu, 2000). In this framework, the authors consider that every sentence was originally shorter and then someone added some additional noisy text to it. Thus, the task of compressive summarization is to find the original sentence. It is worth mentioning that it is not relevant here whether or not the “original” string is real or hypothetical. In this approach, the authors split the problem of sentence compression into three sub-problems: (1) Source model: They assign to every string (sentence) s a probability P (s), which gives the chance that s is generated as an “original short string”; (2) Channel model: They assign to every pair of strings (sentences) s and t a probability P (t|s), which gives the chance that the expansion of the short string s results in the long string t; (3) Decoder: They search for the short string s that maximizes P (s|t) = P (s)P (t|s). In order to implement this, they assume that the probabilities P (s) and P (t|s) are associated with the representation of these sentences using parse trees.

In Cheng and Lapata (2016) and Zhang et al. (2018) different from the above-mentioned works deal with both the extractive and compressive steps using neural network models such as the ones presented in Section 7.2.

Although the most common compressive approaches focus on editing sentences using compressive operations, other operations are also possible. Jing and McKeown (2000), based on analysis of human written abstracts, call attention to different types of operations such as sentence combination (merging material from several sentences), syntactic transformation (for instance, to change the position of the subject or to transform a piece of text from passive voice to active voice), lexical paraphrasing (replacing phrases with their paraphrases), generalization

> 23A lexicon is the vocabulary of a language or a subject. For instance, the lexicon of computer science must present keys such as “algorithm”, “big data”, “class”, “design pattern” and so on.

> 24A syntactic parsing converts the sentence into a tree whose leaves hold POS tags, but the rest of the tree tells how exactly these words join together to make the complete sentence. For example, a linking verb and a verb may combine to be a Verb Phrase (VP) such as in “I have been studying English for years.”, where the underlined piece of text is a verb phrase.

[page 53]

or specification (replacing phrases or clauses with more general or specific descriptions) and reordering (changing the order of specific sentences). However, besides compressing, they only implement the fusion of sentences when two sentences are close to each other and share the same subject or when a person or an entity is mentioned for the first time in a summary and there is a description of this person or entity in the text. Another approach is due to Ganesan et al. (2010) that, using a graph-based approach where each word is a node in the graph, executes both compressive and fusion tasks of highly redundant sentences.

Table 15 presents a significant compilation of ATS systems based on compressive extractive summarization.

[page 54]

|Source|Type|Main contribution|Dataset||||Evaluation|||
|---|---|---|---|---|---|---|---|---|---|
|Jing and McKeown (2000)|Unsupervised|It calls attention to other types of editions besides the|305 sentences from||50 sum-||Human experts|||
|||compressive ones and it implements a limited set of|maries|||||||
|||sentence fusions.||||||||
|Jing (2000)|Supervised|It provides an algorithm based on 5 steps:<br>(1)|Free<br>daily|news|service||Percentage|of|system|
|||Synctatic parsing; (2) Grammar checking; (3) Context|“Communications-related||||decisions|that|agree|
|||information; (4) Corpus evidence; (5) Final decision.|headlines”,|provided<br>by||the|with human decisions|||
||||Benton Foundation25.|||||||
|Knight and Marcu (2000)|Supervised|It assumes that every sentence was originally shorter|The Zif-Davis corpus, which||||Human experts|||
|||and then someone added some additional noisy text to|is a collection of newspaper|||||||
|||it. It splits the problem of sentence compression into|articles announcing computer|||||||
|||three sub-problems: (1) Source model: it assigns to|products.|||||||
|||every sentence probability that it was generated as an||||||||
|||“original shorter string”; (2) Channel model: it assigns||||||||
|||to every pair of sentences the probability that one is||||||||
|||the expansion of the other; (3) Decoder: They search||||||||
|||for the short strings that maximize the product of the||||||||
|||two previous probabilities.||||||||
|Hori and Furui (2004)|Unsupervised|It uses a dynamic programming approach to maximize|Japanese news broadcasts on||||Summarization||accu-|
|||a summarization score that depends on the word sig-|TV in 1996.||||racy|||
|||nifcance, word confdence and the linguistic likelihood||||||||
|||of summarized sentences.||||||||
|Filippova (2010)|Unsupervised|It builds a directed graph where nodes represent words|News articles presented in clus-||||Human experts|||
|||and edges represent the adjacency between words in a|ters on Google News.|||||||
|||sentence and compresses the sentences finding the k-||||||||
|||shortest paths in this digraph.||||||||
|Ganesan et al. (2010)|Unsupervised|It provides a graph based algorithm based on two kinds|Reviews of|hotels,|cars|and|ROUGE-1,|ROUGE-2,||
|||of operations, namely compression and fusion.|other products collected from||||ROUGE-SU-4|||
||||Tripadvisor,|Amazon|and|Ed-||||
||||munds.|||||||
|Cheng and Lapata (2016)|Supervised|It develops neural network models (LSTMs) to extract|DUC|2002||and|ROUGE-1,|ROUGE-2||
|||sentences and words in a supervised fashion as in Sec-|CNN/Dailymail||||and ROUGE-L|||
|||tion 6.4.||||||||
|Zhang et al. (2018)|Supervised|It develops neural network models (LSTMs) to extract|CNN/Dailymail||||ROUGE-1,|ROUGE-2||
|||sentences and words in a supervised fashion as in Sec-|||||and ROUGE-L|||
|||tion 6.4. One particular contribution of this paper is||||||||
|||to use the human-generated summaries in the training||||||||
|||process.||||||||

Table 15: A significant compilation of ATS systems based on compressive summarization.

[page 55]

## 9 Evaluation methods

The literature divides the methods for evaluating the quality of the generated summaries by the so-called intrinsic and extrinsic methods (Jing et al., 1998; Steinberger et al., 2009). While intrinsic methods measure the quality of the summary, extrinsic methods measure a summary’s performance when involved in a particular task such as document categorization and question answering. We may divide the intrinsic methods into three groups: text quality evaluation, content-based evaluation and hybrid. Text quality evaluation focuses on the readability of the summary. On the other hand, content-based evaluation considers the performance of the method according to the chosen words. The hybrid methods consider both worlds. We may split the content group into three subgroups: free-reference based, co-selection and content-based. Freereference based methods evaluate the content of the summaries without the need of a humanmade reference. Co-selection evaluators pay attention to the sentences that were selected using metrics that come from the field of information retrieval. Finally, content-based evaluators focus on the selection of words. Considering the methods that need a human-made reference, content-based evaluators are much more popular than co-selection evaluators, since the former can be naturally applied to both extractive and abstractive summarization. The application of the latter makes more sense in extractive summarization.

Table 16 presents a digest of the methods used to evaluate ATS. DUC 2005 readability arises in this table as a quality-based approach. This entry refers to the DUC 2005 that partially used this technique to evaluate the summaries presented by the competitors (Dang, 2005). This method evaluates the quality of the summary using the following dimensions: grammatical (the summary should not have grammatical errors), non-redundancy (the summary should not have unnecessary repetition), referential clarity (the summary should be easy to identify who or what the pronouns and noun phrases in the summary are referring to), focus (the summary should contain only sentences with information that is related to the rest of the summary), structure and coherence (the summary should be well-structured and well-organized). Based on these dimensions, humans experts evaluate the summaries using a scale that ranges from very Poor, poor, barely acceptable, good to very good. TAC 2008 also uses a quality-based approach and it considers exactly the same dimensions and scale of DUC 2005 readability (Dang et al., 2008).

Another interesting attempt to provide a quality-based approach is due to Grusky et al. (2018). The authors select two semantic dimensions, namely informativeness and relevance, and two syntactic dimensions, namely fluency and coherence, for evaluation. They ask Amazon Mechanical Turk crowd workers to answer the following questions about these dimensions: (1) Informativeness: “How well does the summary capture the key points of the article?” ; (2) Relevance “Are the details provided by the summary consistent with details in the article? ”; (3) Fluency: “Are the individual sentences of the summary well-written and grammatical?”; (4) Coherence: “Do phrases and sentences of the summary fit together and make sense collectively?”.

The idea considered in Pitler and Nenkova (2008) is to combine lexical, syntactic, and discourse features to produce a predictive model of human readers’ judgments of text readability. In this context, Xenouleas et al. (2019) propose Sum-QE, a Quality Estimation model that adds a task-specific layer to a pre-trained BERT model, which is fine-tuned on the task of predicting scores for the five linguistic qualities assessed in DUC 2005. The model achieves a high correlation with human scores by addressing linguistic quality aspects that are only indirectly captured by recall-oriented evaluation metrics.

There is a bunch of free-reference-based methods. The most simple methods are based on the classical distribution divergences. For instance, we may evaluate the divergence between n-grams of the candidate summary and the document using the Kullback–Leibler divergence

[page 56]

given by:

**==> picture [319 x 30] intentionally omitted <==**

where P (x) is the probability of an event x (the appearance of an n-gram) in the document and Q(x) is the probability of an event in the candidate summary (Louis and Nenkova, 2013). Another option is to use the Jensen–Shannon divergence, as in FRESA (Torres-Moreno et al., 2010) or Louis and Nenkova (2013), that symmetrizes the evaluation of the KL divergence:

**==> picture [340 x 23] intentionally omitted <==**

SummTriver (Cabrera-Diego and Torres-Moreno, 2018) considers the possibility of more than one candidate summary and it uses this piece of information to evaluate the trivergence among the distribution of an event in the candidate summary, the distribution of an event in a document formed by the set of candidate summaries and the distribution of an event in the document. It may evaluate the trivergence using different compositions of the divergences between two of these given probabilities. We may also use the Hellinger distance (Pollard, 2002; Gonz´alez-Castro et al., 2013) to evaluate the distance between two distributions, given by:

**==> picture [325 x 34] intentionally omitted <==**

## where 0 ≤ H(P, Q) ≤ 1.

Furthermore, there are also other possibilities for evaluating the similarity between a candidate summary and the original text. For instance, we may evaluate the similarity by cosine of the representation of the text and candidate summaries using vector space models (Louis and Nenkova, 2013) as discussed in Section 6.1.1 or word embeddings (Sun and Nenkova, 2019) as discussed in Section 6.1.5. Louis and Nenkova (2013) also suggests splitting the text and candidate summary into topics and to evaluate the quality of the summary by the fraction of the summary composed of text topic signatures or the percentage of topic signatures from the text that also arise in the summary. The summary likelihood approach considers the candidate summary as being generated according to word distributions in the document. Louis and Nenkova (2013) suggests two different ways to evaluate the likelihood of the summaries, namely the unigram probability model and the multinomial probability model. Another approach to free-reference-based evaluation is SUPERT (SUmmarization evaluation with Pseudo references and bERT) presented in Gao et al. (2020). In this work, the authors measure the relevance of a candidate summary by comparing it with a pseudo-reference summary. Finally, Bao et al. (2020a) uses the idea of transfer learning (Zhuang et al., 2020) to train a neural network model using data from a dataset that has human-made summaries to provide a score to a summary of a document that does not have human-made summaries.

Two co-selection methods arise in Table 16. The information retrieval-based approach, which considers the measures of precision, recall and F-score (Baeza-Yates and Ribeiro-Neto, 2008) and the relative utility approach (Radev et al., 2004). In order to apply the information retrieval approach to evaluate the generated extractive summaries, we suppose that the objective of the method is to recover the sentences that are part of the human-generated summaries. Thus, we call the sentences that appear in the human-generated summaries True and the ones that do not, False. With that in mind, we are able to evaluate the precision, recall and F-metric. The precision is the ratio between the number of True sentences recovered by the ATS systems and the number total of sentences recovered by it as in Eq. (14):

> [in][humans’][summary][} ∩{][ATS][systems’][retrieved][sentences][}|] precision =[|{][sentences] . (14) |{ATS systems’ retrieved sentences}|

[page 57]

The recall is the ratio between the number of True sentences recovered by the automatic summarizer and the total number of sentences that should be recovered according to the humangenerated summary as in Eq. (15):

**==> picture [432 x 27] intentionally omitted <==**

The F -measure is the harmonic mean of precision and recall (Baeza-Yates and Ribeiro-Neto, 2008) as in:[26]

**==> picture [284 x 26] intentionally omitted <==**

The relative utility approach is an extension of the idea of using the information retrieval approach to evaluate summaries (Radev et al., 2003). The starting point of this method is to assume that the human-generated summaries present the level of confidence that a given sentence should belong to the summary. With these weights in hand, we are able to evaluate the relative utility, which is the ratio between the weighted importance of the sentences recovered by the automatic summarizer and the weighted importance of the sentences that should be recovered by the automatic summarizer. In order to define this measure mathematically, we suppose that there are N human experts, the document to be summarized has n sentences and e is the number of sentences in the extracted summary. Let δsj be the characteristic function that equals 1 when sentence j belongs to the extracted summary of the ATS system and that equals 0 otherwise. Let also ǫj be the characteristic function that equals 1 when sentence j belongs to the summary built based on the top e sentences according to the average utilities of all judges and equals 0 otherwise. Thus, we may define the relative utility as

**==> picture [283 x 35] intentionally omitted <==**

We may note this is a kind of weighted recall.

As we can see in Table 16, there are several methods to evaluate ATS using the content-based approach.

Factoid (Van Halteren and Teufel, 2003) and the Pyramid method (Nenkova and Passonneau, 2004) are the content-based manual approaches in Table 16. In both cases, the human evaluators assess whether the information available in the human-made summaries is also in the automated summaries by comparing the content units of both texts. A factoid is a pseudosemantic representation based on atomic information units that can be manually and robustly marked in the text. On the other hand, a pyramid presents the distinct units of text found in several reference summaries and the importance of these distinct units based on how many human-made summaries they occur.

The cosine similarity is a natural approach to compare the tokens generated by the ATS and the tokens of the human-made summaries when we represent the summaries using the vector space model discussed in Section 6.1.1. In this approach, we evaluate the cosine between the vectors that represent each summary.

The unit overlap approach basically evaluates the Jaccard distance (Levandowsky and Winter, 1971) between the words that occur in the human-made and computer-made summaries (Saggion et al., 2002b) as in

**==> picture [311 x 27] intentionally omitted <==**

where A = {sentences in humans’ summary} and B = {ATS systems’ retrieved sentences}.

> 26An extension of the F -measure is the Fβ = (1+β2) βprecision[2] precision+recall×recall[, where][ β][measures the relative importance] between precision and recall. If precision is as important as recall, we choose β = 1 and the recover the harmonic mean.

[page 58]

BLEU (BiLingual Evaluation Understudy) is a metric that was originally created for automatically evaluating machine-translated text. It measures the overlap of n-grams between an automatically generated summary and a reference summary (Papineni et al., 2002) in a precision fashion as in

**==> picture [333 x 27] intentionally omitted <==**

where A = {humans’ summary} and B = {ATS systems’ summary}.

The next measure is the size of the Long Common Subsequence (LCS)[27] between the strings formed by the human-made and computer-made summaries (Crochemore and Rytter, 1994). LCS is evaluated using dynamic programming (Cormen et al., 2022).

ROUGE (Recall Oriented Understudy for Gisting Evaluation) is a general approach to evaluating ATS systems. Since it comprises many different approaches, it is one of the most popular. ROUGE-n[28] measures the overlap of n-grams between an automatically generated summary and reference summary as in

**==> picture [343 x 27] intentionally omitted <==**

where A = {humans’ summary} and B = {ATS system’ summary}. Although Lin and Hovy (2003) originally created it in a recall fashion as in Eq. (20), the available softwares usually also present the precision fashion of it (which is the BLEU in Eq. (19)) and the F -measure, which is the harmonic mean between the precision and recall as shown in Eq. (16).

It is worth mentioning that there are other commonly used variations of ROUGE (Lin, 2004). ROUGE-L intends to consider the length of the LCS such as in Crochemore and Rytter (1994). In this case, the LCS is measured in precision and recall fashions

**==> picture [377 x 26] intentionally omitted <==**

**==> picture [369 x 27] intentionally omitted <==**

and the F -measure is evaluated as in Eq. (16).

Note that ROUGE-L, as the LCS, does not differentiate whether the match between the sequence and its subsequence is consecutive or not. For instance, let X = [‘a’,‘b’,‘c’,‘d’,‘e’], Y1 = [‘a’,‘b’,‘c’,‘f’,‘g’] and Y2 = [‘a’,‘f’,‘b’,‘g’,‘c’]. Both Y1 and Y2 have the same ROUGE-L score. Thus, ROUGE-W measures the WLCS (Weighted Longest Common Subsequence) that weights the LCS by the length of consecutive matches.

A skip-bigram is any pair of words in their sentence order, allowing for arbitrary gaps. ROUGE-S measures skip-bigram co-occurrence statistics between the human expert’s summary and the ATS system’s summary. A potential problem for ROUGE-S is that it scores null if the sentence does not have any word pair co-occurring with its reference. For instance, ROUGE-S gives a score of 0 for the sequences X = [‘a’,‘b’,‘c’,‘d’] and Y = [‘d’,‘c’,‘b’,‘a’]. ROUGE-SU-k counts both skip bigrams and unigrams with maximal skip distance k.

One critique that we can make of the approaches that count the number of common extracts between the computer-based summary and the human-based summary is that the use of words

> 27Let X = {x1, x2, · · · , xm} and Y = {y1, y2, · · · , yn}. We say the Y is a subsequence of X if there exists a strictly increasing sequence of indexes {i1, i2, · · · , iK } such that for all j ∈{1, 2, · · · , K} we have xij = yj. Given two sequences X and Y , the Longest Common Subsequence (LCS) of X and Y is a common subsequence with maximum length.

> 28Lin and Bilmes (2011) calls attention that one interesting property of the ROUGE-n is submodularity suggesting that if this is an important way to evaluate summaries, then optimal submodular approaches such as in their paper, Lin et al. (2009) and K˚ageb¨ack et al. (2014) are well justified.

[page 59]

with the same semantic is not considered. Thus, the next line of Table 16 presents a collection of works that extend the ROUGE methodology to consider semantically related words. Some of them use dictionaries or corpora. METEOR (Banerjee and Lavie, 2005), Ganesan (2018) and ShafieiBavani et al. (2018) use WordNet. Zhou et al. (2006) build an independent paraphrase collection. On the other hand, other works apply neural network representations, such as Ng and Abrecht (2015) (word embeddings), Zhang et al. (2019) (BERT), Zhao et al. (2019) (BERT), Hailu et al. (2020) (word embeddings) and Lee et al. (2020) (BERT), presented in Sections 6.1.5 and 7.2.

The next row considers methods based on relevance analysis that measure the quality of the candidate summary by using a relative decrease in retrieval performance when indexing summaries instead of full documents. They use a search engine to find the most related documents (from a given set) to the candidate summary and to its corresponding human-made summaries forming two lists of retrieved documents. Radev et al. (2003) and Cohan and Goharian (2016) evaluate respectively the candidate summary score using the Kendall or the Spearman correlation measures and the intersection between the truncated lists of retrieved documents.

The latent-based approach (Steinberger et al., 2009) uses singular value decomposition discussed in Section 6.1.2 to capture the main topics of the document. The computer-based summaries are ranked according to the similarity of the main topics of their summaries and their reference documents.

The semi-automated pyramid methods (Harnly et al., 2005; Passonneau et al., 2013, 2018) use respectively unigram overlap, cosine similarity of latent vector representations and a weighted set cover algorithm to score the summaries given the manual pyramids. On the other hand, the automated pyramid methods (Yang et al., 2016; Peyrard and Eckle-Kohler, 2017; Gao et al., 2018, 2019) face the herculean task of building the pyramids automatically. In order to do that, Yang et al. (2016) extract relation tuples using the Stanford Open Information Extraction (Angeli et al., 2015) and Peyrard and Eckle-Kohler (2017) use a phrase structure parse and dependency parse to convert each sentence using the Stanford CoreNLP (Manning et al., 2014). In order to find the semantic similarity, they respectively use WordNet and word embeddings. SSAS (Semantic Similarity for Abstractive Summarization) (Vadapalli et al., 2017) applies the model of Yang et al. (2016) to extract the SCUs and combine various semantic and lexical similarity measures to score the quality of the candidate summary.

The basic elements approach (Hovy et al., 2005, 2006), as in the case of BLEU, ROUGE or pyramid methods, compares the content of the reference summaries and generated summaries using small units as defined by the authors as (1) the head of a major syntactic constituent (noun, verb, adjective or adverbial phrases), expressed as a single item; or (2) a relation between a head and a single dependent, expressed as a triple (head — modifier — relation). In order to evaluate the score, the basic elements are evaluated according to lexical identity (the words must match exactly), lemma identity (the root forms of the words must match according to WordNet) and distributional similarity (words are similar according to the cosine distance on mutual information-based distributional similarity scores (Lin and Pantel, 2002)).

The SEE (Summary Evaluation Environment) (Lin, 2001; Lin and Hovy, 2003) is a hybrid approach in Table 16, in the sense that comprises ingredients of both the quality and content approaches. In this approach, the human evaluators compare the human-made summary with the automatic summary by finding the common pieces of text and specifying if the found pieces of text express all, most, some, hardly any or none of the content of the current model unit. In order to measure quality, the human evaluators rate grammar, cohesion, and coherence at those levels.

The TAC 2008 overall responsiveness (Dang et al., 2008) is also a manual hybrid approach in Table 16. It evaluates the degree to which a summary is responding to the information necessary to describe the topic state and the linguistic quality. It uses the five-point scale: (1) very poor; (2) poor; (3) barely acceptable; (4) good; (5) very good.

[page 60]

The extrinsic evaluation methods explore the quality of the summary in the completion of a specific task. The difficulty with matching a computer-made summary against an ideal summary is that the ideal summary is hard to establish. In Table 16, some tasks are considered, namely document categorization, information retrieval, question answering and masked token task (Taylor, 1953).

[page 61]

||Approach|Kind|Sub-kind|Method|Source|
|---|---|---|---|---|---|
|||||DUC 2005 readability|Dang (2005)|
|||Quality||TAC 2008 readability<br>Newsroom human evaluation|Dang et al. (2008)<br>Grusky et al. (2018)|
|||||Sum-QE|Xenouleas et al. (2019)|
|||||Distributions divergence|Torres-Moreno et al. (2010) and Cabrera-Diego and Torres-Moreno (2018)|
|||||Cosine similarity|Louis and Nenkova (2013); Sun and Nenkova (2019)|
||||Free reference based|topic|Louis and Nenkova (2013)|
|||||likelihood|Louis and Nenkova (2013)|
|||||Pseudo reference|Gao et al. (2020)|
|||||Transfer learning|Bao et al. (2020a)|
||||Co-selection|Information retrieval based<br>Relative utility|Baeza-Yates and Ribeiro-Neto (2008)<br>Radev et al. (2004)|
||Intrinsic|Content||Manual<br>Cosine similarity|Van Halteren and Teufel (2003); Nenkova and Passonneau (2004)<br>Salton (1989)|
|||||Unity overlap|Saggion et al. (2002b)|
|61||||BLEU (n-grams matching)<br>Longest Common Subsequence|Papineni et al. (2002)<br>Saggion et al. (2002a)|
||||Content-based|Extracts matching (ROUGE)|Lin and Hovy (2003); Lin (2004)|
|||||Extracts matching with semantic|Banerjee and Lavie (2005), Zhou et al. (2006), Ng and Abrecht (2015), Ganesan (2018),|
||||||ShafeiBavani et al. (2018), Zhao et al. (2019) and Hailu et al. (2020).|
|||||Search-based matching|Radev et al. (2003) and Cohan and Goharian (2016)|
|||||Latent-based|Steinberger et al. (2009)|
|||||Semi-automated pyramid|Harnly et al. (2005); Passonneau et al. (2013, 2018)|
|||||Automated pyramid|Yang et al. (2016); Peyrard and Eckle-Kohler (2017); Vadapalli et al. (2017)|
|||||Basic elements|Hovy et al. (2005) and Hovy et al. (2006)|
|||Hybrid||SEE<br>Overall responsiveness|Lin (2001); Lin and Hovy (2003)<br>(Dang et al., 2008)|
|||||Document categorization|Brandow et al. (1995); Mani and Bloedorn (1997)|
||Extrinsic|Task-based||Information retrieval|Tombros and Sanderson (1998); Radev et al. (2003)|
|||||Question answering|Morris et al. (1992), Chen et al. (2018), Scialom et al. (2019) and Eyal et al. (2019)|
|||||masked token task|(Vasilyev et al., 2020)|

Table 16: A digest of the methods used to evaluate ATS.

[page 62]

It is worth mentioning that, as we have shown in Table 16, due to the inherent complexity of evaluating ATS systems, there are different methods for this task. However, as reported in Blagec et al. (2022), BLEU and ROUGE dominate the field of evaluation in spite of their low correlation with human evaluation (Liu and Liu, 2008; Ng and Abrecht, 2015). We may find the same conclusion if we consider carefully the last column of Tables 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14 and 15.

## 10 Open libraries

There are now several libraries with implementations of the most popular methods of ATS. Table 17 presents a compendium of the extractive approaches introduced in Section 6. Table 18 presents a compendium of summarization methods based on transformer models discussed in Section 7.2. Finally, Table 19 presents a digest of open libraries with evaluation methods.

[page 63]

|Name|Source code|Method|Source|Section|
|---|---|---|---|---|
|||Random|||
|||KL-Sum|Haghighi and Vanderwende (2009)|6.1.1|
|||Luhn|Luhn (1958)|6.1.1|
|Sumy|https://github.com/miso-belica/sumy/|Edmundson<br>LSA|Edmundson (1969)<br>Steinberger et al. (2004)|6.1.1<br>6.1.2|
|||Textrank|Mihalcea and Tarau (2004)|6.1.3|
|||Lexrank|Erkan and Radev (2004)|6.1.3|
|||Reduction||6.1.3|

Table 17: A compendium of the extractive approaches presented in Section 6. The methods come from the library Sumy (Belica, 2022).

[page 64]

|Name|Source Code|Kind|Method|Source|Section|
|---|---|---|---|---|---|
||||bart-large-cnn|Lewis et al. (2019)|7.2|
||huggingface.co/||pegasus-xsum<br>pegasus-large|Zhang et al. (2020)|7.2|
|transformers<br>(SummarizationPipeline)|transformers/v3.0.2/<br>modules/<br>transformers/pipelines.html#|Abstractive|t5-small<br>t5-base|||
||SummarizationPipeline||t5-large|Rafel et al. (2019)|7.2|
||||t5-3b|||
||||t5-11b|||
||||distilroberta-base-ext-sum<br>distilbert-base-uncased-ext-sum|Sanh et al. (2019)|6.4|
|||Extractive|roberta-large-ext-sum<br>roberta-base-ext-sum|Liu et al. (2019)|6.4|
|transformerSum|https://github.com/HHousen/<br>TransformerSum||bert-base-uncased-ext-sum<br>bert-large-uncased-ext-sum<br>longformer-base-4096-ext-sum<br>mobilebert-uncased-ext-sum|Devlin et al. (2018)<br>Beltagy et al. (2020)|6.4<br>6.4|
||||led-base-16384|||
|||Abstractive|led-large-16384|Beltagy et al. (2020)|7.2|
||||distil-led-large-cnn-16384|||

Table 18: A compendium of the transformer approaches presented in Sections 6.4 and 7.2. The methods come from the Transformers (Wolf et al., 2020) and TransformerSum libraries.(Housen, 2022).

[page 65]

|Library|Source Code|Method|Source|
|---|---|---|---|
|||Cosine simlarity|Salton (1989)|
|||Precision|Baeza-Yates and Ribeiro-Neto (2008)|
|NLTK|https://www.nltk.org/|Recall<br>F-Measure|Baeza-Yates and Ribeiro-Neto (2008)<br>Baeza-Yates and Ribeiro-Neto (2008)|
|||Likelihood|Louis and Nenkova (2013)|
|||Unit overlap (Jaccard)|Saggion et al. (2002b)|
|Gensim|https://radimrehurek.com/gensim/|Kullback-Leibler<br>Unit overlap (Jaccard)|Louis and Nenkova (2013)<br>Saggion et al. (2002b)|
|||ROUGE-N|Lin (2004)|
|py-ROUGE|https://github.com/Diego999/py-rouge|ROUGE-L|Lin (2004)|
|||ROUGE-W|Lin (2004)|
|ROUGE-metric|https://github.com/li-plus/rouge-metric|ROUGE-SU|Lin (2004)|

Table 19: A compendium of the evaluation methods used in summarization and discussed in Section 9. These methods come from the NLTK (Bird et al., 2009), Gensim (Reh˚uˇrek[ˇ] and Sojka, 2010), Py-ROUGE, and ROUGE-metric libraries.

[page 66]

## 11 Empirical exercises

In this section, we present an empirical exploration of some of the free ATS libraries presented in Section 10. For this exercise, we use CNN Corpus (Lins et al., 2019) presented in Section 4. We have run all extractive approaches presented in Section 10. In order to run the Edmundson summarizer we must specify a list of bonus words, that is, words that are positively relevant, a list of stigma words, negatively relevant, and a list of null words, deemed irrelevant to the summary. While the null words were defined as the list of stopwords of the NLTK library for the english language, the lists of bonus and stigma words were obtained by calculating the document frequency of terms in a subset of 200 golden summaries and source texts from each corpus, after stopwords removal. The 10 most frequent words in the subset of golden summaries were used as bonus words for each dataset, and the 10 words with the highest ratio of term frequency in source texts to the frequency in golden summaries were defined as stigma words.

We chose to run BART, mT5 and PEGASUS as the transformer models for abstractive summarization in our experiments. Given our intention of selecting ready-to-use summarization methods, these are some of the most popular transformers on the summarization pipeline of the Huggingface package. Therefore, these models are readily available in a pre-trained state by this implementation. As for which fine-tuning for each model was chosen, we decided upon pegasusxsum, bart-large-cnn and mT5-multilingual-XLSum, trained with the XSum, CNN/Daily Mail and XL-Sum datasets, respectively.

We also present the typical summaries generated by these methods for a document from the CNN Corpus in Tables 21 and 22. This dataset has both extractive and abstractive golden summaries for each text. The ones used in our examples, as well as the source text, are presented below:

[page 67]

Source text: A fourth infant has been discovered to have been infected with a rare, sometimes fatal form of bacteria that can come from baby formula, but there is no evidence the cases are related, federal health authorities said Friday. “Based on test results to date, there is no need for a recall of infant formula and parents may continue to use powdered infant formula, following the manufacturer’s directions on the printed label”, the Centers for Disease Control and Prevention and the Food and Drug Administration said in a joint update. The latest case of Cronobacter infection occurred in Florida, the update said. After cases occurred in Missouri and Illinois, authorities looked for other cases, and found an Oklahoma case and the one in Florida. The Florida and Missouri infants died this month of their infections. The Missouri case prompted retail giant Wal-Mart to pull all cans of the same size and lot number of baby formula from its shelves. But DNA fingerprinting of the bacteria from the Missouri and Illinois cases found the bacteria differed, suggesting they were not related, the agencies said. Bacteria from the other two cases were not available for testing, they said. In the Missouri case, Cronobacter bacteria were found in an opened bottle of nursery water and prepared infant formula, but it was not clear how they became contaminated, the update said. Tests on factory-sealed containers of powdered infant formula and nursery water with the same lot numbers turned up no Cronobacter bacteria, it said, adding, “There is currently no evidence to conclude that the infant formula or nursery water was contaminated during manufacturing or shipping.” Formula maker Mead Johnson Nutrition said the agencies’ test results corroborated its own. “We’re pleased with the FDA and CDC testing, which should reassure consumers, health care professionals and retailers everywhere about the safety and quality of our products”, Tim Brown, senior vice president and general manager for North America, said in a statement. “These tests also reinforce the rigor of our quality processes throughout our operations.” Cronobacter infection typically occurs during the first days or weeks of life. In a typical year, the CDC said, it learns of four to six such cases. This year, with increased awareness of the infection, it has tallied 12 cases. The bacteria can cause severe infection or inflammation of the membranes that cover the brain. Symptoms can start with fever, poor feeding, crying or listlessness. “Any young infant with these symptoms should be in the care of a physician”, the update says. The bacteria can be found in the environment and can multiply in powdered infant formula once it is mixed with water, said the CDC, which recommends breastfeeding whenever possible. Cronobacter is fatal in nearly 40% of cases, according to the CDC. Infection survivors can be left with severe neurological problems.

Extractive golden summary: “Based on test results to date, there is no need for a recall of infant formula and parents may continue to use powdered infant formula, following the manufacturer’s directions on the printed label”, the Centers for Disease Control and Prevention and the Food and Drug Administration said in a joint update. But DNA fingerprinting of the bacteria from the Missouri and Illinois cases found the bacteria differed, suggesting they were not related, the agencies said. The bacteria can be found in the environment and can multiply in powdered infant formula once it is mixed with water, said the CDC, which recommends breastfeeding whenever possible.

Abstractive golden summary: “There is no need for a recall of infant formula”, federal health officials say. DNA fingerprinting finds the Missouri and Illinois bacteria are different, suggesting they’re not related. CDC recommends breastfeeding whenever possible.

Based on the results of Table 20, there is no consensus on the best method. However, we can see that some of the methods stand out. Among the classical extractive methods, we note the one due to Luhn (1958) and Text Rank (Mihalcea and Tarau, 2004). Among the transformers, we may cite the BART (Lewis et al., 2019). This result makes sense since the training data of BART comprises a set of news. Thus, in some sense, this exercise is an exercise of learning transference (Zhuang et al., 2020).

[page 68]

|CNN Corpus||ROUGE-1|||ROUGE-2|||ROUGE-3||ROUGE-4|ROUGE-4||
|---|---|---|---|---|---|---|---|---|---|---|---|---|
||P|R|F|P|R|F|P|R|F|P|R|F|
|SumyKL|34.20|32.59|33.37|16.95|16.28|16.61|14.12|14.09|13.89|13.08|13.09|12.88|
|SumyLexRank|38.46|43.83|40.97|23.00|26.21|24.50|21.35|23.18|21.97|20.29|22.04|20.89|
|SumyLsa|32.76|33.74|33.24|16.21|16.90|16.55|14.05|14.97|14.32|13.21|14.09|13.47|
|SumyLuhn|35.86|52.83|42.72|24.14|34.37|28.36|25.50|28.95|26.89|24.61|27.94|25.95|
|SumyEdmundson|35.99|41.39|38.50|21.36|24.64|22.89|20.33|22.44|21.07|19.43|21.48|20.15|
|SumyRandom|33.45|30.77|32.05|15.33|14.52|14.91|12.82|12.54|12.42|11.94|11.72|11.59|
|SumyReduction|33.47|49.65|39.98|21.61|30.81|25.40|22.36|25.20|23.50|21.51|24.23|22.60|
|SumySumBasic|37.72|25.50|30.43|14.72|10.53|12.28|11.51|8.78|9.62|10.30|7.93|8.65|
|SumyTextRank|33.31|50.26|40.07|21.63|31.34|25.60|22.66|25.54|23.82|21.83|24.58|22.93|
|bart-large-cnn|33.29|33.54|33.41|15.87|15.88|15.87|12.82|12.97|12.74|9.38|9.42|9.28|
|mT5-multilingual-XLSum|24.43|18.25|20.90|4.98|3.65|4.21|2.90|2.13|2.42|1.38|1.00|1.14|
|pegasus-xsum|22.24|23.24|22.73|6.26|6.62|6.43|4.38|4.68|4.46|2.60|2.76|2.63|

|CNN Corpus||ROUGE-L||ROUGE-SU4|ROUGE-SU4|ROUGE-SU4|ROUGE-W|ROUGE-W||
|---|---|---|---|---|---|---|---|---|---|
||P|R|F|P|R|F|P|R|F|
|SumyKL|25.15|24.19|24.66|19.14|18.33|18.73|21.73|8.99|12.47|
|SumyLexRank|29.65|33.85|31.61|24.70|28.24|26.36|27.54|12.41|16.83|
|SumyLsa|23.76|24.62|24.18|18.20|18.95|18.57|20.94|9.23|12.59|
|SumyLuhn|29.28|42.62|34.71|25.37|36.66|29.99|30.48|14.53|19.40|
|SumyEdmundson|27.99|32.30|29.99|23.04|26.66|24.72|26.30|12.05|16.26|
|SumyRandom|23.89|22.11|22.96|17.75|16.64|17.18|20.88|8.25|11.55|
|SumyReduction|26.93|39.42|32.00|22.97|33.31|27.19|27.85|13.21|17.66|
|SumySumBasic|25.77|17.52|20.86|17.80|12.37|14.60|22.55|6.69|10.00|
|SumyTextRank|26.86|39.99|32.13|22.97|33.84|27.36|28.11|13.34|17.83|
|bart-large-cnn|25.29|25.53|25.41|15.89|15.93|15.91|24.33|11.77|15.61|
|mT5-multilingual-XLSum|16.32|12.25|14.00|7.29|5.31|6.14|16.50|5.93|8.58|
|pegasus-xsum|15.81|16.65|16.22|7.65|8.03|7.84|15.70|7.94|10.35|

|CNN Corpus|P|R|F|H|J|K-L|C|
|---|---|---|---|---|---|---|---|
|SumyKL|31.92|28.99|30.38|0.24|0.84|0.21|0.43|
|SumyLexRank|37.89|41.34|39.54|0.23|0.81|0.19|0.49|
|SumyLsa|30.97|33.67|32.26|0.23|0.85|0.20|0.37|
|SumyLuhn|37.03|49.10|42.22|0.24|0.80|0.18|0.54|
|SumyEdmundson|35.04|38.99|36.91|0.23|0.82|0.19|0.46|
|SumyRandom|30.89|29.19|30.02|0.23|0.85|0.21|0.39|
|SumyReduction|34.14|45.55|39.03|0.24|0.81|0.18|0.54|
|SumySumBasic|34.90|25.03|29.15|0.22|0.86|0.20|0.39|
|SumyTextRank|33.95|46.11|39.11|0.24|0.81|0.18|0.54|
|bart-large-cnn|33.80|33.91|33.85|0.22|0.83|0.19|0.35|
|mT5-multilingual-XLSum|24.14|18.73|21.09|0.23|0.90|0.22|0.22|
|pegasus-xsum|25.75|22.45|23.99|0.25|0.89|0.26|0.25|

Table 20: CNN Corpus results. The evaluators used in this table are ROUGE-n (1 to 4), ROUGE-L, ROUGE-SU4, ROUGE-W, Precision (P), Recall (R), the F-measure, Hellinger (H), Jaccard distance (J), KL divergence (KL) and Cosine similarity (C).

[page 69]

||Method|Summary|
|---|---|---|
||SumyRandom|A fourth infant has been discovered to have been infected with a rare, sometimes fatal form of bacteria that can come from baby formula, but there is no evidence the|
|||cases are related, federal health authorities said Friday. In the Missouri case, Cronobacter bacteria were found in an opened bottle of nursery water and prepared infant|
|||formula, but it was not clear how they became contaminated, the update said. “We’re pleased with the FDA and CDC testing, which should reassure consumers, health|
|||care professionals and retailers everywhere about the safety and quality of our products”, Tim Brown, senior vice president and general manager for North America, said|
|||in a statement. Symptoms can start with fever, poor feeding, crying or listlessness.|
||SumyLuhn|A fourth infant has been discovered to have been infected with a rare, sometimes fatal form of bacteria that can come from baby formula, but there is no evidence the cases|
|||are related, federal health authorities said Friday. “Based on test results to date, there is no need for a recall of infant formula and parents may continue to use powdered|
|||infant formula, following the manufacturer’s directions on the printed label”, the Centers for Disease Control and Prevention and the Food and Drug Administration|
|||said in a joint update. In the Missouri case, Cronobacter bacteria were found in an opened bottle of nursery water and prepared infant formula, but it was not clear how|
|||they became contaminated, the update said. Tests on factory-sealed containers of powdered infant formula and nursery water with the same lot numbers turned up no|
|||Cronobacter bacteria, it said, adding, “There is currently no evidence to conclude that the infant formula or nursery water was contaminated during manufacturing or|
|||shipping.”|
||SumyEdmundson|A fourth infant has been discovered to have been infected with a rare, sometimes fatal form of bacteria that can come from baby formula, but there is no evidence|
|||the cases are related, federal health authorities said Friday. ”Based on test results to date, there is no need for a recall of infant formula and parents may continue|
|||to use powdered infant formula, following the manufacturer’s directions on the printed label”, the Centers for Disease Control and Prevention and the Food and Drug|
|||Administration said in a joint update. The latest case of Cronobacter infection occurred in Florida, the update said. In a typical year, the CDC said, it learns of four to|
|||six such cases.|
||SumyLsa|A fourth infant has been discovered to have been infected with a rare, sometimes fatal form of bacteria that can come from baby formula, but there is no evidence the|
|||cases are related, federal health authorities said Friday. Bacteria from the other two cases were not available for testing, they said. Tests on factory-sealed containers of|
|||powdered infant formula and nursery water with the same lot numbers turned up no Cronobacter bacteria, it said, adding, “There is currently no evidence to conclude|
|||that the infant formula or nursery water was contaminated during manufacturing or shipping.” In a typical year, the CDC said, it learns of four to six such cases.|
|69|SumyLexRank|“Based on test results to date, there is no need for a recall of infant formula and parents may continue to use powdered infant formula, following the manufacturer’s|
|||directions on the printed label”, the Centers for Disease Control and Prevention and the Food and Drug Administration said in a joint update. After cases occurred|
|||in Missouri and Illinois, authorities looked for other cases, and found an Oklahoma case and the one in Florida. Tests on factory-sealed containers of powdered infant|
|||formula and nursery water with the same lot numbers turned up no Cronobacter bacteria, it said, adding,” There is currently no evidence to conclude that the infant|
|||formula or nursery water was contaminated during manufacturing or shipping.” The bacteria can be found in the environment and can multiply in powdered infant|
|||formula once it is mixed with water, said the CDC, which recommends breastfeeding whenever possible.|
||SumyTextRank|“Based on test results to date, there is no need for a recall of infant formula and parents may continue to use powdered infant formula, following the manufacturer’s|
|||directions on the printed label”, the Centers for Disease Control and Prevention and the Food and Drug Administration said in a joint update. But DNA fngerprinting|
|||of the bacteria from the Missouri and Illinois cases found the bacteria differed, suggesting they were not related, the agencies said. Tests on factory-sealed containers of|
|||powdered infant formula and nursery water with the same lot numbers turned up no Cronobacter bacteria, it said, adding, “There is currently no evidence to conclude that|
|||the infant formula or nursery water was contaminated during manufacturing or shipping.” The bacteria can be found in the environment and can multiply in powdered|
|||infant formula once it is mixed with water, said the CDC, which recommends breastfeeding whenever possible.|
||SumySumBasic|The latest case of Cronobacter infection occurred in Florida, the update said. After cases occurred in Missouri and Illinois, authorities looked for other cases, and found|
|||an Oklahoma case and the one in Florida. Tests on factory-sealed containers of powdered infant formula and nursery water with the same lot numbers turned up no|
|||Cronobacter bacteria, it said, adding, “There is currently no evidence to conclude that the infant formula or nursery water was contaminated during manufacturing or|
|||shipping.” Infection survivors can be left with severe neurological problems.|
||SumyKL|The latest case of Cronobacter infection occurred in Florida, the update said. After cases occurred in Missouri and Illinois, authorities looked for other cases, and found|
|||an Oklahoma case and the one in Florida. But DNA fngerprinting of the bacteria from the Missouri and Illinois cases found the bacteria differed, suggesting they were|
|||not related, the agencies said. The bacteria can cause severe infection or infammation of the membranes that cover the brain.|
||SumyReduction|“Based on test results to date, there is no need for a recall of infant formula and parents may continue to use powdered infant formula, following the manufacturer’s|
|||directions on the printed label”, the Centers for Disease Control and Prevention and the Food and Drug Administration said in a joint update. But DNA fngerprinting|
|||of the bacteria from the Missouri and Illinois cases found the bacteria differed, suggesting they were not related, the agencies said. Tests on factory-sealed containers of|
|||powdered infant formula and nursery water with the same lot numbers turned up no Cronobacter bacteria, it said, adding, “There is currently no evidence to conclude that|
|||the infant formula or nursery water was contaminated during manufacturing or shipping.” The bacteria can be found in the environment and can multiply in powdered|
|||infant formula once it is mixed with water, said the CDC, which recommends breastfeeding whenever possible.|

Table 21: Examples of extractive summaries.

[page 70]

|Method|Summary|
|---|---|
|Transformers-|A fourth infant has been infected with a rare, sometimes fatal form|
|facebook/bart-|of bacteria. There is no evidence the cases are related, federal health|
|large-cnn|authorities say.<br>The latest case of Cronobacter infection occurred in|
||Florida. In a typical year, the CDC says, it learns of four to six such|
||cases.|
|Transformers-|There is no need for a recall of infant formula, US health officials say, af-|
|google/pegasus-|ter three babies died from an infection linked to the product in Missouri,|
|xsum|Florida and Illinois. Tests on factory-sealed containers of powdered in-|
||fant formula and nursery water with the same lot numbers turned up no|
||Cronobacter.|
|Transformers-|The US government has said there is no need for a recall of powdered|
|csebuetnlp/|infant formula and nursery water, following tests that show no evidence|
|mT5<br>multilingual|they were contaminated during manufacturing or shipment of the prod-|
|XLSum|uct.|

Table 22: Examples of abstractive summaries.

[page 71]

## 12 Final remarks

In this work, we have provided a literature review of ATS systems. As we have previously mentioned, this is not an easy task. Since work by Luhn (1958), thousands of papers were introduced about this subject. In order to present a comprehensive review, we have divided the contributions by the type of output summary, as described in Section 2, namely extractive, abstractive and hybrid, and the type of model used to generate the summary. Several models have been used to generate summaries including the classical frequency-based models and the state of art deep neural network sequence-to-sequence models. In general, we may see in this work that any model of language can be used to generate a summary.

Besides the presentation of the models, we also introduced the most popular datasets used in the field, the methods used to evaluate the quality of the summaries, the public libraries that can be used to generate summaries and some empirical exercises exploring how the models discussed in the paper can be applied using the public libraries reviewed in Section 10 to generate useful summaries.

Although we may surely assert that the field of ATS systems is a mature field, many difficulties still remain and these field difficulties will undoubtedly be explored in the future:

1. Text quality: The quality of a summary may strongly depend on the approach used to implement the ATS system. In extractive approaches, they still fail to provide solutions that avoid a lack of coherence between the sentences. In particular, one of the biggest difficulties is the “dangling” anaphoras, i.e., sentences in the extracted summaries referring to other sentences that are not in the summary or to the wrong previous sentence. Although there are some solutions that try to minimize this problem such as extracting entire paragraphs (Wu and Liu, 2003) or using heuristics to avoid extracting sentences that make references to other sentences (Rush et al., 1971), this is still an ongoing problem. In abstractive summarization systems, the quality of the summary is strongly related to the capacity of text generation.

2. Completeness: Most choices about what should be included in the summary are based on assumptions made about the text. A large set of models have been made available. Due to the complexity of human language, all models have their own limitations. Frequency-based models strongly depend on the frequency of the tokens. With these models, important pieces of information presented using “rare” words may not be considered. One solution to deal with this is to use semantically based approaches such as the ones presented in Section 6.1.5 based on word embeddings. Linguistic models usually depend on specific structures, rules or ontologies that may not be correctly applied in many situations. Sequence-tosequence deep learning models are also kinds of frequency-based models with the same merits and problems. Furthermore, they need to be trained with large annotated datasets. If the dataset is not available, we have to transfer the learning from one dataset to the other. This transference may work or may not work depending on the differences and similarities between the two pieces of text.

3. Size of the input text: In extractive summarization, although the size of input text usually is not directly a problem, the quality of the summary may deteriorate when we concatenate sentences that come from very different parts of the text. The size of the input text may not be a problem for the linguistic-based abstractive approaches either. However, if the size of the input text is positively correlated with the complexity of the text, this might be a problem, since the structures used for linguistic-based abstractive summarization may not be able to accommodate this richness of details. Due to the computational complexity, deep learning sequence-to-sequence models suffer directly from the size of input since most models are available to texts of moderate size.

[page 72]

4. Size of the abstract: Considering abstracts that convey the same pieces of information, abstracts generated by extractive summarization approaches are usually larger than the ones generated by abstractive methods. The point is that in the case of the extractive approaches, the relevant pieces of information are distributed in several sentences, and in many situations, irrelevant pieces of information remain in the extracted sentences.

5. Datasets: Although there are many datasets available today as we presented in Section 4, many of these datasets are related to a specific field (news or scientific papers) since in general, it is very costly to create datasets. This problem increases when we need datasets to train extractive systems, since human summaries are abstractive in nature, as we mentioned in Section 6.4.

6. Evaluation: The biggest issue with the activity of evaluating the task of ATS is that there is not a perfect summary that can be used as a model such as in other machine learning tasks. Different human experts may generate great but different summaries. Besides the fact that different human experts may choose different pieces of text to include in the summary, they may include the same pieces of text in semantically equivalent ways, making the task of comparing machine summaries to human summaries very difficult.

## 13 Acknowledgment

The authors acknowledge and thank the partial financial support from the Ministry of Science and Technology of Brazil (MCTI). DOC (grant number 302629/2019-0) and LW (309545/20218) also thank CNPQ for the partial financial support.

[page 73]

## References

- M. Abadi, A. Agarwal, P. Barham, E. Brevdo, Z. Chen, C. Citro, G. S. Corrado, A. Davis, J. Dean, M. Devin, S. Ghemawat, I. Goodfellow, A. Harp, G. Irving, M. Isard, Y. Jia, R. Jozefowicz, L. Kaiser, M. Kudlur, J. Levenberg, D. Man´e, R. Monga, S. Moore, D. Murray, C. Olah, M. Schuster, J. Shlens, B. Steiner, I. Sutskever, K. Talwar, P. Tucker, V. Vanhoucke, V. Vasudevan, F. Vi´egas, O. Vinyals, P. Warden, M. Wattenberg, M. Wicke, Y. Yu, and X. Zheng. TensorFlow: Large-scale machine learning on heterogeneous systems, 2015. URL https://www.tensorflow.org/. Software available from tensorflow.org.

- M. Aliannejadi, S. A. Bahrainian, A. Giachanou, and F. Crestani. University of lugano at trec 2015: Contextual suggestion and temporal summarization tracks. In TREC, 2015.

- M. Allahyari, S. Pouriyeh, M. Assefi, S. Safaei, E. D. Trippe, J. B. Gutierrez, and K. Kochut. Text summarization techniques: a brief survey. arXiv preprint arXiv:1707.02268, 2017.

- A. Alomari, N. Idris, A. Q. M. Sabri, and I. Alsmadi. Deep reinforcement and transfer learning for abstractive text summarization: A review. Computer Speech & Language, 71:101276, 2022.

- N. Andhale and L. Bewoor. An overview of text summarization techniques. In 2016 international conference on computing communication control and automation (ICCUBEA), pages 1–7. IEEE, 2016.

- G. Angeli, M. J. J. Premkumar, and C. D. Manning. Leveraging linguistic structure for open domain information extraction. In Proceedings of the 53rd Annual Meeting of the Association for Computational Linguistics and the 7th International Joint Conference on Natural Language Processing (Volume 1: Long Papers), pages 344–354, 2015.

- J. A. Aslam, M. Ekstrand-Abueg, V. Pavlu, F. Diaz, and T. Sakai. Trec 2013 temporal summarization. In TREC, 2013.

- I. Awasthi, K. Gupta, P. S. Bhogal, S. S. Anand, and P. K. Soni. Natural language processing (nlp) based text summarization-a survey. In 2021 6th International Conference on Inventive Computation Technologies (ICICT), pages 1310–1317. IEEE, 2021.

- R. Baeza-Yates and B. Ribeiro-Neto. Modern Information Retrieval. Addison-Wesley Publishing Company, USA, 2nd edition, 2008. ISBN 9780321416919.

- D. Bahdanau, K. Cho, and Y. Bengio. Neural machine translation by jointly learning to align and translate. arXiv preprint arXiv:1409.0473, 2014.

- S. Banerjee and A. Lavie. Meteor: An automatic metric for mt evaluation with improved correlation with human judgments. In Proceedings of the acl workshop on intrinsic and extrinsic evaluation measures for machine translation and/or summarization, pages 65–72, 2005.

- M. Banko, V. O. Mittal, and M. J. Witbrock. Headline generation based on statistical translation. In Proceedings of the 38th Annual Meeting of the Association for Computational Linguistics, pages 318–325, 2000.

- F. S. Bao, H. Li, G. Luo, C. Chen, Y. Yang, Y. He, and M. Qiu. End-to-end semanticsbased summary quality assessment for single-document summarization. arXiv preprint arXiv:2005.06377, 2020a.

[page 74]

- H. Bao, L. Dong, F. Wei, W. Wang, N. Yang, X. Liu, Y. Wang, S. Piao, J. Gao, M. Zhou, and H.W. Hon. Unilmv2: Pseudo-masked language models for unified language model pre-training. In Preprint, 2020b.

- U. Barman, V. Barman, M. Rahman, and N. K. Choudhury. Graph based extractive news articles summarization approach leveraging static word embeddings. In 2021 International Conference on Computational Performance Evaluation (ComPE), pages 008–011. IEEE, 2021.

- F. Barrios, F. L´opez, L. Argerich, and R. Wachenchauzer. Variations of the similarity function of textrank for automated summarization. arXiv preprint arXiv:1602.03606, 2016.

- A. Barto and M. Duff. Monte carlo matrix inversion and reinforcement learning. Advances in Neural Information Processing Systems, 6, 1993.

- P. B. Baxendale. Machine-made index for technical literature—an experiment. IBM Journal of research and development, 2(4):354–361, 1958.

- M. Belica. Sumy. https://github.com/miso-belica/sumy, 2022.

- I. Beltagy, M. E. Peters, and A. Cohan. Longformer: The long-document transformer. arXiv preprint arXiv:2004.05150, 2020.

- R. C. Belwal, S. Rai, and A. Gupta. Text summarization using topic-based vector space model and semantic measure. Information Processing & Management, 58(3):102536, 2021.

- Y. Bengio, P. Frasconi, and P. Simard. The problem of learning long-term dependencies in recurrent networks. In IEEE international conference on neural networks, pages 1183–1188. IEEE, 1993.

- Y. Bengio, R. Ducharme, and P. Vincent. A neural probabilistic language model. Advances in neural information processing systems, 13, 2000.

- J. Berkson. Application of the logistic function to bio-assay. Journal of the American statistical association, 39(227):357–365, 1944.

- J. Berkson. Why i prefer logits to probits. Biometrics, 7(4):327–339, 1951.

- M. W. Berry, S. T. Dumais, and G. W. O’Brien. Using linear algebra for intelligent information retrieval. SIAM review, 37(4):573–595, 1995.

- D. Bertsekas. Dynamic programming and optimal control: Volume I, volume 1. Athena scientific, 2012.

- D. P. Bertsekas and J. N. Tsitsiklis. Neuro-dynamic programming. Athena Scientific, 1996.

- D. P. Bertsekas et al. Dynamic programming and optimal control 3rd edition, volume ii. Belmont, MA: Athena Scientific, 2011.

- S. K. Bharti and K. S. Babu. Automatic keyword extraction for text summarization: A survey. arXiv preprint arXiv:1704.03242, 2017.

- J. Bilmes. Submodularity in machine learning and artificial intelligence. arXiv preprint arXiv:2202.00132, 2022.

- S. Bird, E. Klein, and E. Loper. Natural language processing with Python: analyzing text with the natural language toolkit. ” O’Reilly Media, Inc.”, 2009.

- C. M. Bishop and N. M. Nasrabadi. Pattern recognition and machine learning, volume 4. Springer, 2006.

[page 75]

- K. Blagec, G. Dorffner, M. Moradi, S. Ott, and M. Samwald. A global analysis of metrics used for measuring performance in natural language processing. arXiv preprint arXiv:2204.11574, 2022.

- D. M. Blei, A. Y. Ng, and M. I. Jordan. Latent dirichlet allocation. Journal of machine Learning research, 3(Jan):993–1022, 2003.

- P. Bonacich. Factoring and weighting approaches to status scores and clique identification. Journal of mathematical sociology, 2(1):113–120, 1972.

- R. Brandow, K. Mitze, and L. F. Rau. Automatic condensation of electronic publications by sentence selection. Information Processing & Management, 31(5):675–685, 1995.

- L. Breiman. Random forests. Machine learning, 45(1):5–32, 2001.

- L. Breiman, J. H. Friedman, R. A. Olshen, and C. J. Stone. Classification and Regression Trees. Chapman and Hall/CRC, 1984.

- T. B. Brown, B. Mann, N. Ryder, M. Subbiah, J. Kaplan, P. Dhariwal, A. Neelakantan, P. Shyam, G. Sastry, A. Askell, et al. Language models are few-shot learners. arXiv preprint arXiv:2005.14165, 2020.

- K. Bullers, A. M. Howard, A. Hanson, W. D. Kearns, J. J. Orriola, R. L. Polo, and K. A. Sakmar. It takes longer than you think: librarian time spent on systematic review tasks. Journal of the Medical Library Association: JMLA, 106(2):198, 2018.

- C. Burges, T. Shaked, E. Renshaw, A. Lazier, M. Deeds, N. Hamilton, and G. Hullender. Learning to rank using gradient descent. In Proceedings of the 22nd international conference on Machine learning, pages 89–96, 2005.

- L. d. S. Cabral, R. D. Lins, R. F. Mello, F. Freitas, B. Avila, S. Simske, and M. Riss.[´] A platform for language independent summarization. In Proceedings of the 2014 ACM symposium on Document engineering, pages 203–206, 2014.

- L. A. Cabrera-Diego and J.-M. Torres-Moreno. Summtriver: A new trivergent model to evaluate summaries automatically without human references. Data & Knowledge Engineering, 113: 184–197, 2018.

- E. Canhasi and I. Kononenko. Semantic role frames graph-based multidocument summarization. In Proc. SiKDD’11, 2011.

- Z. Cao, W. Li, S. Li, F. Wei, and Y. Li. Attsum: Joint learning of focusing and summarization with neural attention. arXiv preprint arXiv:1604.00125, 2016.

- J. Carbonell and J. Goldstein. The use of mmr, diversity-based reranking for reordering documents and producing summaries. In Proceedings of the 21st Annual International ACM SIGIR Conference on Research and Development in Information Retrieval, SIGIR ’98, page 335–336, New York, NY, USA, 1998. Association for Computing Machinery.

- G. Carenini, R. T. Ng, and X. Zhou. Summarizing email conversations with clue words. In Proceedings of the 16th international conference on World Wide Web, pages 91–100, 2007.

- Y.-L. Chang and J.-T. Chien. Latent dirichlet learning for document summarization. In 2009 IEEE international conference on acoustics, speech and signal processing, pages 1689–1692. IEEE, 2009.

- J. Chen, D. Tam, C. Raffel, M. Bansal, and D. Yang. An empirical survey of data augmentation for limited data learning in nlp. arXiv preprint arXiv:2106.07499, 2021.

[page 76]

- P. Chen and R. Verma. A query-based medical information summarization system using ontology knowledge. In 19th IEEE Symposium on Computer-Based Medical Systems (CBMS’06), pages 37–42, 2006.

- P. Chen, F. Wu, T. Wang, and W. Ding. A semantic qa-based approach for text summarization evaluation. In Proceedings of the AAAI Conference on Artificial Intelligence, volume 32, 2018.

- J. Cheng and M. Lapata. Neural summarization by extracting sentences and words. arXiv preprint arXiv:1603.07252, 2016.

- K. Cho, B. Van Merri¨enboer, C. Gulcehre, D. Bahdanau, F. Bougares, H. Schwenk, and Y. Bengio. Learning phrase representations using rnn encoder-decoder for statistical machine translation. arXiv preprint arXiv:1406.1078, 2014.

- J. Chung, C. Gulcehre, K. Cho, and Y. Bengio. Empirical evaluation of gated recurrent neural networks on sequence modeling. arXiv preprint arXiv:1412.3555, 2014.

- J. Clarke and M. Lapata. Models for sentence compression: A comparison across domains, training requirements and evaluation measures. In Proceedings of the 21st International Conference on Computational Linguistics and the 44th annual meeting of the Association for Computational Linguistics, pages 377–384, 2006.

- A. Cohan and N. Goharian. Revisiting summarization evaluation for scientific articles. arXiv preprint arXiv:1604.00400, 2016.

- A. Cohan, F. Dernoncourt, D. S. Kim, T. Bui, S. Kim, W. Chang, and N. Goharian. A discourse-aware attention model for abstractive summarization of long documents. arXiv preprint arXiv:1804.05685, 2018.

- R. Collobert and J. Weston. A unified architecture for natural language processing: Deep neural networks with multitask learning. In Proceedings of the 25th international conference on Machine learning, pages 160–167, 2008.

- J. M. Conroy and D. P. O’leary. Text summarization via hidden markov models. In Proceedings of the 24th annual international ACM SIGIR conference on Research and development in information retrieval, pages 406–407, 2001.

- T. H. Cormen, C. E. Leiserson, R. L. Rivest, and C. Stein. Introduction to algorithms. MIT press, 2022.

- C. Cortes and V. Vapnik. Support-vector networks. Machine learning, 20(3):273–297, 1995.

- L. d. F. Costa, F. A. Rodrigues, G. Travieso, and P. R. Villas Boas. Characterization of complex networks: A survey of measurements. Advances in physics, 56(1):167–242, 2007.

- M. Crochemore and W. Rytter. Text algorithms. Maxime Crochemore, 1994.

- V. Dalal and L. Malik. A survey of extractive and abstractive text summarization techniques. In 2013 6th International Conference on Emerging Trends in Engineering and Technology, pages 109–110. IEEE, 2013.

- M. Damova and I. Koychev. Query-based summarization: A survey. 2010.

- H. T. Dang. Overview of duc 2005. In Proceedings of the document understanding conference, volume 2005, pages 1–12, 2005.

[page 77]

- H. T. Dang, K. Owczarzak, et al. Overview of the tac 2008 update summarization task. In TAC, 2008.

- H. T. Dang, K. Owczarzak, et al. Overview of TAC 2009 Summarization Track, 2009. URL https://tac.nist.gov/publications/2009/presentations/TAC2009_Summ_overview.pdf.

- H. T. Dang, K. Owczarzak, et al. Overview of TAC 2010 Summarization Track, 2010. URL https://tac.nist.gov/publications/2010/presentations/TAC2010_Summ_Overview.pdf.

- H. T. Dang, K. Owczarzak, et al. Overview of TAC 2011 Summarization Track, 2011. URL

- W. M. Darling. Multi-document summarization from first principles. In TAC, 2010.

- D. Das and A. Martins. A survey on automatic text summarization (tech. rep.). Literature Survey for the Language and Statistics II course at Carnegie Mellon University, 2007.

- J.-Y. Delort and E. Alfonseca. Dualsum: a topic-model based approach for update summarization. In Proceedings of the 13th Conference of the European Chapter of the Association for Computational Linguistics, pages 214–223, 2012.

- M. J. Denny and A. Spirling. Text preprocessing for unsupervised learning: Why it matters, when it misleads, and what to do about it. Political Analysis, 26(2):168–189, 2018.

- F. Dernoncourt, M. Ghassemi, and W. Chang. A repository of corpora for summarization. In Proceedings of the Eleventh International Conference on Language Resources and Evaluation (LREC 2018), 2018.

- J. Devlin, M.-W. Chang, K. Lee, and K. Toutanova. Bert: Pre-training of deep bidirectional transformers for language understanding. arXiv preprint arXiv:1810.04805, 2018.

- P. Domingos and M. Pazzani. On the optimality of the simple bayesian classifier under zero-one loss. Machine learning, 29(2):103–130, 1997.

- L. Dong, N. Yang, W. Wang, F. Wei, X. Liu, Y. Wang, J. Gao, M. Zhou, and H.-W. Hon. Unified language model pre-training for natural language understanding and generation. In Advances in Neural Information Processing Systems. Curran Associates, Inc., 2019. URL

- R. O. Duda, P. E. Hart, et al. Pattern classification and scene analysis, volume 3. Wiley New York, 1973.

- S. T. Dumais. Improving the retrieval of information from external sources. Behavior Research Methods, Instruments, & Computers, 23(2):229–236, Jun 1991. ISSN 1532-5970. doi: 10. 3758/BF03203370. URL https://doi.org/10.3758/BF03203370.

- A. Edelman and S. Jeong. Fifty three matrix factorizations: A systematic approach. arXiv preprint arXiv:2104.08669, 2021.

- A. Edmunds and A. Morris. The problem of information overload in business organisations: a review of the literature. International journal of information management, 20(1):17–28, 2000.

- H. P. Edmundson. New methods in automatic extracting. Journal of the ACM, 16(2):264–285, apr 1969.

- H. P. Edmundson and R. E. Wyllys. Automatic abstracting and indexing—survey and recommendations. Communications of the ACM, 4(5):226–234, 1961.

[page 78]

- W. S. El-Kassas, C. R. Salama, A. A. Rafea, and H. K. Mohamed. Automatic text summarization: A comprehensive survey. Expert Systems with Applications, 165:113679, 2021. ISSN 0957-4174.

- J. L. Elman. Finding structure in time. Cognitive science, 14(2):179–211, 1990.

- G. Erkan and D. R. Radev. Lexrank: Graph-based lexical centrality as salience in text summarization. Journal Artificial Intelligence Research, 22(1):457–479, 2004. ISSN 1076-9757.

- E. Estrada. The structure of complex networks: theory and applications. Oxford University Press, 2012.

- M. Eyal, T. Baumel, and M. Elhadad. Question answering as an automatic evaluation metric for news article summarization. arXiv preprint arXiv:1906.00318, 2019.

- A. Fabbri, I. Li, T. She, S. Li, and D. Radev. Multi-news: A large-scale multi-document summarization dataset and abstractive hierarchical model. pages 1074–1084, 2019.

- M. A. Fattah and F. Ren. Ga, mr, ffnn, pnn and gmm based models for automatic text summarization. Computer Speech & Language, 23(1):126–144, 2009.

- W. Fedus, B. Zoph, and N. Shazeer. Switch transformers: Scaling to trillion parameter models with simple and efficient sparsity. arXiv preprint arXiv:2101.03961, 2021.

- C. D. Fellbaum. Wordnet : an electronic lexical database. Language, 76:706, 2000.

- S. Y. Feng, V. Gangal, J. Wei, S. Chandar, S. Vosoughi, T. Mitamura, and E. Hovy. A survey of data augmentation approaches for nlp. arXiv preprint arXiv:2105.03075, 2021.

- R. Ferreira, L. de Souza Cabral, R. D. Lins, G. P. e Silva, F. Freitas, G. D. Cavalcanti, R. Lima, S. J. Simske, and L. Favaro. Assessing sentence scoring techniques for extractive text summarization. Expert systems with applications, 40(14):5755–5764, 2013.

- K. Filippova. Multi-sentence compression: Finding shortest paths in word graphs. In Proceedings of the 23rd international conference on computational linguistics (Coling 2010), pages 322–330, 2010.

- D. Fleder and K. Hosanagar. Blockbuster culture’s next rise or fall: The impact of recommender systems on sales diversity. Management science, 55(5):697–712, 2009.

- J. Friedman, T. Hastie, and R. Tibshirani. Regularization paths for generalized linear models via coordinate descent. Journal of statistical software, 33(1):1, 2010.

- J. H. Friedman. Greedy function approximation: a gradient boosting machine. Annals of statistics, pages 1189–1232, 2001.

- M. Gambhir and V. Gupta. Recent automatic text summarization techniques: a survey. Artificial Intelligence Review, 47(1):1–66, 2017.

- K. Ganesan. Rouge 2.0: Updated and improved measures for evaluation of summarization tasks. arXiv preprint arXiv:1803.01937, 2018.

- K. Ganesan, C. Zhai, and J. Han. Opinosis: A graph based approach to abstractive summarization of highly redundant opinions. 2010.

- Y. Gao, A. Warner, and R. J. Passonneau. Pyreval: An automated method for summary content analysis. In Proceedings of the Eleventh International Conference on Language Resources and Evaluation (LREC 2018), 2018.

[page 79]

- Y. Gao, C. Sun, and R. J. Passonneau. Automated pyramid summarization evaluation. In Proceedings of the 23rd Conference on Computational Natural Language Learning (CoNLL), 2019.

- Y. Gao, W. Zhao, and S. Eger. Supert: Towards new frontiers in unsupervised evaluation metrics for multi-document summarization. arXiv preprint arXiv:2005.03724, 2020.

- P.-E. Genest and G. Lapalme. Framework for abstractive summarization using text-to-text generation. In Proceedings of the workshop on monolingual text-to-text generation, pages 64–73, 2011.

- P.-E. Genest and G. Lapalme. Fully abstractive approach to guided summarization. In Proceedings of the 50th Annual Meeting of the Association for Computational Linguistics (Volume 2: Short Papers), pages 354–358, 2012.

- M. Gentzkow, B. Kelly, and M. Taddy. Text as data. Journal of Economic Literature, 57(3): 535–74, September 2019.

- F. A. Gers, J. Schmidhuber, and F. Cummins. Learning to forget: Continual prediction with lstm. Neural computation, 12(10):2451–2471, 2000.

- S. Gholamrezazadeh, M. A. Salehi, and B. Gholamzadeh. A comprehensive survey on text summarization systems. In 2009 2nd International Conference on Computer Science and its Applications, pages 1–6, 2009.

- D. Gillick, B. Favre, and D. Hakkani-T¨ur. The icsi summarization system at tac 2008. In Tac, 2008.

- N. Gillis. Nonnegative Matrix Factorization. SIAM, 2020.

- B. Gliwa, I. Mochol, M. Biesek, and A. Wawer. Samsum corpus: A human-annotated dialogue dataset for abstractive summarization. arXiv preprint arXiv:1911.12237, 2019.

- G. H. Golub and C. F. V. Loan. Matrix Computations. Johns Hopkins University Press, 2013.

- Y. Gong and X. Liu. Generic text summarization using relevance measure and latent semantic analysis. In Proceedings of the 24th Annual International ACM SIGIR Conference on Research and Development in Information Retrieval, SIGIR ’01, page 19–25, New York, NY, USA, 2001. Association for Computing Machinery. ISBN 1581133316.

- V. Gonz´alez-Castro, R. Alaiz-Rodr´ıguez, and E. Alegre. Class distribution estimation based on the hellinger distance. Information Sciences, 218:146–164, 2013.

- I. Goodfellow, Y. Bengio, and A. Courville. Deep learning. MIT press, 2016.

- D. Graff, J. Kong, K. Chen, and K. Maeda. English gigaword. Linguistic Data Consortium, Philadelphia, 4(1):34, 2003.

- C. Greenbacker. Towards a framework for abstractive summarization of multimodal documents. In Proceedings of the ACL 2011 Student Session, pages 75–80, 2011.

- G. Grefenstette. Producing intelligent telegraphic text reduction to provide an audio scanning service for the blind. In Intelligent Text Summarization, AAAI Spring Symposium Series, pages 111–117, 1998.

- M. Grusky, M. Naaman, and Y. Artzi. Newsroom: A dataset of 1.3 million summaries with diverse extractive strategies. arXiv preprint arXiv:1804.11283, 2018.

[page 80]

- S. Gupta and S. K. Gupta. Abstractive summarization: An overview of the state of the art. Expert Systems with Applications, 121:49–65, 2019.

- V. Gupta and G. S. Lehal. A survey of text summarization extractive techniques. Journal of emerging technologies in web intelligence, 2(3):258–268, 2010.

- L. Guti´errez and B. Keith. A systematic literature review on word embeddings. In International Conference on Software Process Improvement, pages 132–141. Springer, 2018.

- A. Haghighi and L. Vanderwende. Exploring content models for multi-document summarization. In Proceedings of human language technologies: The 2009 annual conference of the North American Chapter of the Association for Computational Linguistics, pages 362–370, 2009.

- T. T. Hailu, J. Yu, and T. G. Fantaye. A framework for word embedding based automatic text summarization and evaluation. Information, 11(2):78, 2020.

- S. M. Harabagiu and F. Lacatusu. Generating single and multi-document summaries with gistexter. In Document Understanding Conferences, pages 11–12, 2002.

- A. Harnly, A. Nenkova, R. Passonneau, and O. Rambow. Automation of summary evaluation by the pyramid method. In Recent Advances in Natural Language Processing (RANLP), pages 226–232, 2005.

- K. S. Hasan and V. Ng. Automatic keyphrase extraction: A survey of the state of the art. In Proceedings of the 52nd Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pages 1262–1273, 2014.

- T. Hasan, A. Bhattacharjee, M. S. Islam, K. Samin, Y.-F. Li, Y.-B. Kang, M. S. Rahman, and R. Shahriyar. Xl-sum: Large-scale multilingual abstractive summarization for 44 languages. arXiv preprint arXiv:2106.13822, 2021.

- L. Hasler, C. Or˘asan, and R. Mitkov. Building better corpora for summarisation. In Proceedings of Corpus Linguistics 2003, pages 309 – 319, Lancaster, UK, March 2003. URL http://clg.wlv.ac.uk/papers/hasler-CL-03.pdf.

- S. Haykin. Neural networks: a comprehensive foundation. Prentice-Hall, 1994.

- S. Henß, M. Mieskes, and I. Gurevych. A reinforcement learning approach for adaptive singleand multi-document summarization. In GSCL, pages 3–12, 2015.

- K. M. Hermann, T. Kocisky, E. Grefenstette, L. Espeholt, W. Kay, M. Suleyman, and P. Blunsom. Teaching machines to read and comprehend. Advances in neural information processing systems, 28, 2015.

- A. Hervas-Drane. Word of mouth and recommender systems: A theory of the long tail. 2008.

- S. Hochreiter and J. Schmidhuber. Long short-term memory. Neural computation, 9(8):1735– 1780, 1997.

- C. Hori and S. Furui. Speech summarization: an approach through word extraction and a method for evaluation. IEICE TRANSACTIONS on Information and Systems, 87(1):15–25, 2004.

- H. Housen. Transformersum. https://github.com/HHousen/TransformerSum, 2022.

- E. Hovy and C. Y. Lim. Automated multilingual text summarization and its evaluation. Technical report, University of Southern California, 1999.

[page 81]

- E. Hovy, C.-Y. Lin, and L. Zhou. Evaluating duc 2005 using basic elements. In Proceedings of DUC, volume 2005. Citeseer, 2005.

- E. H. Hovy, C.-Y. Lin, L. Zhou, and J. Fukumoto. Automated summarization evaluation with basic elements. In LREC, volume 6, pages 604–611. Citeseer, 2006.

- L. Huang, S. Cao, N. Parulian, H. Ji, and L. Wang. Efficient attentions for long document summarization. arXiv preprint arXiv:2104.02112, 2021.

- A. Hulth. Improved automatic keyword extraction given more linguistic knowledge. In Proceedings of the 2003 conference on Empirical methods in natural language processing, pages 216–223, 2003.

- A. J. Izenman. Modern multivariate statistical techniques: Regression, classification and manifold learning. Springer, 2008.

- A. Jain, D. Bhatia, and M. K. Thakur. Extractive text summarization using word vector embedding. In 2017 International Conference on Machine Learning and Data Science (MLDS), pages 51–55, 2017. doi: 10.1109/MLDS.2017.12.

- Z. Jalil, J. A. Nasir, and M. Nasir. Extractive multi-document summarization: A review of progress in the last decade. IEEE Access, 2021.

- A. Janin, D. Baron, J. Edwards, D. Ellis, D. Gelbart, N. Morgan, B. Peskin, T. Pfau, E. Shriberg, A. Stolcke, et al. The icsi meeting corpus. In 2003 IEEE International Conference on Acoustics, Speech, and Signal Processing, 2003. Proceedings.(ICASSP’03)., volume 1, pages I–I. IEEE, 2003.

- H. Jing. Sentence reduction for automatic text summarization. In Sixth applied natural language processing conference, pages 310–315, 2000.

- H. Jing and K. McKeown. Cut and paste based text summarization. In 1st Meeting of the North American Chapter of the Association for Computational Linguistics, 2000.

- H. Jing, R. Barzilay, K. McKeown, and M. Elhadad. Summarization evaluation methods: Experiments and analysis. In AAAI symposium on intelligent summarization, pages 51–59. Palo Alto, CA, 1998.

- T. Joachims. Training linear svms in linear time. In Proceedings of the 12th ACM SIGKDD international conference on Knowledge discovery and data mining, pages 217–226, 2006.

- K. S. Jones. Automatic summarising: Factors and directions. In Advances in Automatic Text Summarization, pages 1–12. MIT Press, 1998.

- M. Jordan. Serial order: a parallel distributed processing approach. technical report, june 1985-march 1986. Technical report, California Univ., San Diego, La Jolla (USA). Inst. for Cognitive Science, 1986.

- A. K. Joshi and Y. Schabes. Tree-adjoining grammars. In Handbook of formal languages, pages 69–123. Springer, 1997.

- A. Joulin, E. Grave, P. Bojanowski, and T. Mikolov. Bag of tricks for efficient text classification. arXiv preprint arXiv:1607.01759, 2016. URL https://arxiv.org/abs/1607.01759.

- M. K˚ageb¨ack, O. Mogren, N. Tahmasebi, and D. Dubhashi. Extractive summarization using continuous vector space models. In Proceedings of the 2nd Workshop on Continuous Vector Space Models and their Compositionality (CVSC), pages 31–39, 2014.

[page 82]

- A. Khurana and V. Bhatnagar. Investigating entropy for extractive document summarization. Expert Systems with Applications, 187:115820, 2022.

- B. Kim, H. Kim, and G. Kim. Abstractive summarization of reddit posts with multi-level memory networks. arXiv preprint arXiv:1811.00783, 2018.

- V. Klema and A. Laub. The singular value decomposition: Its computation and some applications. IEEE Transactions on automatic control, 25(2):164–176, 1980.

- O. Klymenko, D. Braun, and F. Matthes. Automatic text summarization: A state-of-the-art review. ICEIS (1), pages 648–655, 2020.

- K. Knight and D. Marcu. Statistics-based summarization-step one: Sentence compression. AAAI/IAAI, 2000:703–710, 2000.

- A. Kornilova and V. Eidelman. Billsum: A corpus for automatic summarization of us legislation. arXiv preprint arXiv:1910.00523, 2019.

- M. Koupaee and W. Y. Wang. Wikihow: A large scale text summarization dataset. arXiv preprint arXiv:1810.09305, 2018.

- L.-W. Ku, Y.-T. Liang, and H.-H. Chen. Opinion extraction, summarization and tracking in news and blog corpora. In Proceedings of AAAI, pages 100–107, 2006.

- Y. J. Kumar and N. Salim. Automatic multi document summarization approaches. In KS Gayathri, Received BE degree in CSE from Madras University in 2001 and ME degree from Anna University, Chennai. She is doing Ph. D. in the area of Reasoning in Smart. Citeseer, 2012.

- J. Kupiec, J. Pedersen, and F. Chen. A trainable document summarizer. In Proceedings of the 18th Annual International ACM SIGIR Conference on Research and Development in Information Retrieval, SIGIR ’95, page 68–73, 1995.

- Y. LeCun, B. Boser, J. S. Denker, D. Henderson, R. E. Howard, W. Hubbard, and L. D. Jackel. Backpropagation applied to handwritten zip code recognition. Neural computation, 1(4): 541–551, 1989.

- Y. LeCun et al. Lenet-5, convolutional neural networks. URL: http://yann. lecun. com/exdb/lenet, 20(5):14, 2015.

- C.-S. Lee, Z.-W. Jian, and L.-K. Huang. A fuzzy ontology and its application to news summarization. IEEE Transactions on Systems, Man, and Cybernetics, Part B (Cybernetics), 35 (5):859–880, 2005.

- D. Lee and H. S. Seung. Algorithms for non-negative matrix factorization. Advances in neural information processing systems, 13, 2000.

- D. Lee, M. Shin, T. Whang, S. Cho, B. Ko, D. Lee, E. Kim, and J. Jo. Reference and document aware semantic evaluation methods for korean language summarization. arXiv preprint arXiv:2005.03510, 2020.

- D. D. Lee and H. S. Seung. Learning the parts of objects by non-negative matrix factorization. Nature, 401(6755):788–791, 1999.

- G. H. Lee and K. J. Lee. Automatic text summarization using reinforcement learning with embedding features. In Proceedings of the Eighth International Joint Conference on Natural Language Processing (Volume 2: Short Papers), pages 193–197, 2017.

[page 83]

- J.-H. Lee, S. Park, C.-M. Ahn, and D. Kim. Automatic generic document summarization based on non-negative matrix factorization. Information Processing & Management, 45(1):20–34, 2009.

- J. Leskovec, M. Grobelnik, and N. Milic-Frayling. Learning semantic graph mapping for document summarization. In Proceedings of ECML/PKDD-2004 workshop on knowledge discovery and ontologies, 2004a.

- J. Leskovec, M. Grobelnik, and N. Milic-Frayling. Learning sub-structures of document semantic graphs for document summarization. In LinkKDD Workshop, volume 133, page 138, 2004b.

- J. Leskovec, N. Milic-Frayling, and M. Grobelnik. Extracting summary sentences based on the document semantic graph. 2005.

- M. Levandowsky and D. Winter. Distance between sets. Nature, 234:34–35, 1971.

- O. Levy, Y. Goldberg, and I. Dagan. Improving distributional similarity with lessons learned from word embeddings. TACL, 3:211–225, 2015. URL

- M. Lewis, Y. Liu, N. Goyal, M. Ghazvininejad, A. Mohamed, O. Levy, V. Stoyanov, and L. Zettlemoyer. Bart: Denoising sequence-to-sequence pre-training for natural language generation, translation, and comprehension. arXiv preprint arXiv:1910.13461, 2019.

- J. Li, T. Tang, W. X. Zhao, and J.-R. Wen. Pretrained language models for text generation: A survey. arXiv preprint arXiv:2105.10311, 2021a.

- Z. Li, F. Liu, W. Yang, S. Peng, and J. Zhou. A survey of convolutional neural networks: analysis, applications, and prospects. IEEE transactions on neural networks and learning systems, 2021b.

- C.-Y. Lin. Summary evaluation environment. http://www1.cs.columbia.edu/nlp/tides/SEEManual.pdf, 2001. Accessed: 2022-05-23.

- C.-Y. Lin. Rouge: A package for automatic evaluation of summaries. In Text summarization branches out, pages 74–81, 2004.

- C.-Y. Lin and E. Hovy. Identifying topics by position. In Fifth Conference on Applied Natural Language Processing, pages 283–290, 1997.

- C.-Y. Lin and E. Hovy. Automatic evaluation of summaries using n-gram co-occurrence statistics. In Proceedings of the 2003 human language technology conference of the North American chapter of the association for computational linguistics, pages 150–157, 2003.

- D. Lin and P. Pantel. Concept discovery from text. In COLING 2002: The 19th International Conference on Computational Linguistics, 2002.

- H. Lin and J. Bilmes. A class of submodular functions for document summarization. In Proceedings of the 49th annual meeting of the association for computational linguistics: human language technologies, pages 510–520, 2011.

- H. Lin, J. Bilmes, and S. Xie. Graph-based submodular selection for extractive summarization. In 2009 IEEE Workshop on Automatic Speech Recognition & Understanding, pages 381–386. IEEE, 2009.

[page 84]

- R. D. Lins, H. Oliveira, L. Cabral, J. Batista, B. Tenorio, R. Ferreira, R. Lima, G. de Fran¸ca Pereira e Silva, and S. J. Simske. The cnn-corpus: A large textual corpus for single-document extractive summarization. In Proceedings of the ACM Symposium on Document Engineering 2019, pages 1–10, 2019.

- F. Liu and Y. Liu. Correlation between rouge and human evaluation of extractive meeting summaries. In Proceedings of ACL-08: HLT, short papers, pages 201–204, 2008.

- J. Liu, Z. Liu, and H. Chen. Revisit word embeddings with semantic lexicons for modeling lexical contrast. In 2017 IEEE International Conference on Big Knowledge (ICBK), pages 72–79, Aug 2017. doi: 10.1109/ICBK.2017.35.

- Q. Liu, Y. Liu, D. Wu, and X. Cheng. Ictnet at temporal summarization track trec 2013. In TREC, 2013.

- Q. Liu, M. J. Kusner, and P. Blunsom. A survey on contextual embeddings. arXiv preprint arXiv:2003.07278, 2020.

- Y. Liu and M. Lapata. Text summarization with pretrained encoders. arXiv preprint arXiv:1908.08345, 2019.

- Y. Liu, M. Ott, N. Goyal, J. Du, M. Joshi, D. Chen, O. Levy, M. Lewis, L. Zettlemoyer, and V. Stoyanov. Roberta: A robustly optimized bert pretraining approach. arXiv preprint arXiv:1907.11692, 2019. URL https://arxiv.org/abs/1907.11692.

- E. Lloret and M. Palomar. Text summarisation in progress: a literature review. Artificial Intelligence Review, 2012.

- A. Louis and A. Nenkova. Automatically assessing machine summary content without a gold standard. Computational Linguistics, 39(2):267–300, 2013.

- H. P. Luhn. The automatic creation of literature abstracts. IBM Journal of Research and Development, 2(2):159–165, 1958.

- T. Lyche. Numerical Linear Algebra and Matrix Factorizations. Springer, 2020.

- C. Mallick, A. K. Das, M. Dutta, A. K. Das, and A. Sarkar. Graph-based text summarization using modified textrank. In Soft computing in data analytics, pages 137–146. Springer, 2019.

- I. Mani and E. Bloedorn. Multi-document summarization by graph search and matching. arXiv preprint cmp-lg/9712004, 1997.

- I. Mani, D. House, G. Klein, L. Hirschman, T. Firmin, and B. M. Sundheim. The tipster summac text summarization evaluation. In Ninth Conference of the European Chapter of the Association for Computational Linguistics, pages 77–85, 1999.

- C. D. Manning, P. Raghavan, and H. Sch¨utze. Introduction to Information Retrieval. Cambridge University Press, New York, NY, USA, 2008. ISBN 0521865719, 9780521865715.

- C. D. Manning, M. Surdeanu, J. Bauer, J. R. Finkel, S. Bethard, and D. McClosky. The stanford corenlp natural language processing toolkit. In Proceedings of 52nd annual meeting of the association for computational linguistics: system demonstrations, pages 55–60, 2014.

- B. McCann, J. Bradbury, C. Xiong, and R. Socher. Learned in translation: Contextualized word vectors. Advances in neural information processing systems, 30, 2017.

[page 85]

- D. D. McDonald and C. Greenbacker. ‘if you’ve heard it, you can say it’-towards an account of expressibility. In Proceedings of the 6th International Natural Language Generation Conference, 2010.

- R. McDonald. A study of global inference algorithms in multi-document summarization. In European Conference on Information Retrieval, pages 557–564. Springer, 2007.

- Y. K. Meena and D. Gopalani. Evolutionary algorithms for extractive automatic text summarization. Procedia Computer Science, 48:244–249, 2015.

- D. Michie and R. A. Chambers. Boxes: An experiment in adaptive control. Machine intelligence, 2(2):137–152, 1968.

- R. Mihalcea and P. Tarau. Textrank: Bringing order into text. In Proceedings of the 2004 conference on empirical methods in natural language processing, pages 404–411, 2004.

- R. Mihalcea and P. Tarau. A language independent algorithm for single and multiple document summarization. In Companion Volume to the Proceedings of Conference including Posters/Demos and tutorial abstracts, 2005.

- T. Mikolov, I. Sutskever, K. Chen, G. Corrado, and J. Dean. Distributed representations of words and phrases and their compositionality. CoRR, abs/1310.4546, 2013.

- G. A. Miller. Wordnet: A lexical database for english. Communications of the ACM, 38(11): 39–41, nov 1995.

- S. Miller, M. Crystal, H. Fox, L. Ramshaw, R. Schwartz, R. Stone, and R. Weischedel. Algorithms that learn to extract information bbn: Tipster phase iii. In TIPSTER TEXT PROGRAM PHASE III: Proceedings of a Workshop held at Baltimore, Maryland, October 13-15, 1998, pages 75–89, 1998.

- R. Mishra, J. Bian, M. Fiszman, C. R. Weir, S. Jonnalagadda, J. Mostafa, and G. Del Fiol. Text summarization in the biomedical domain: a systematic review of recent research. Journal of biomedical informatics, 52:457–467, 2014.

- I. F. Moawad and M. Aref. Semantic graph reduction approach for abstractive text summarization. In 2012 Seventh International Conference on Computer Engineering & Systems (ICCES), pages 132–138. IEEE, 2012.

- M. Mohamed and M. Oussalah. Srl-esa-textsum: A text summarization approach based on semantic role labeling and explicit semantic analysis. Information Processing & Management, 56(4):1356–1372, 2019.

- M. J. Mohan, C. Sunitha, A. Ganesh, and A. Jaya. A study on ontology based abstractive summarization. Procedia Computer Science, 87:32–37, 2016.

- M. Mohd, R. Jan, and M. Shah. Text document summarization using word embedding. Expert Systems with Applications, 143:112958, 2020.

- D. Moll´a. Towards the use of deep reinforcement learning with global policy for query-based extractive summarisation. arXiv preprint arXiv:1711.03859, 2017.

- N. Moratanch and S. Chitrakala. A survey on abstractive text summarization. In 2016 International Conference on Circuit, power and computing technologies (ICCPCT), pages 1–7. IEEE, 2016.

[page 86]

- A. H. Morris, G. M. Kasper, and D. A. Adams. The effects and limitations of automated text condensing on reading comprehension performance. Information Systems Research, 3 (1):17–35, 1992.

- J. Morris and G. Hirst. Lexical cohesion computed by thesaural relations as an indicator of the structure of text. Computational linguistics, 17(1):21–48, 1991.

- M. F. Mridha, A. A. Lima, K. Nur, S. C. Das, M. Hasan, and M. M. Kabir. A survey of automatic text summarization: Progress, process and challenges. IEEE Access, 9:156043–156070, 2021.

- N. Munot and S. S. Govilkar. Comparative study of text summarization methods. International Journal of Computer Applications, 102(12), 2014.

- R. Nallapati, F. Zhai, and B. Zhou. Summarunner: A recurrent neural network based sequence model for extractive summarization of documents. In Thirty-first AAAI conference on artificial intelligence, 2017.

- C. Napoles, M. Gormley, and B. Van Durme. Annotated Gigaword. In Proceedings of the Joint Workshop on Automatic Knowledge Base Construction and Web-scale Knowledge Extraction (AKBC-WEKEX), pages 95–100, Montr´eal, Canada, June 2012. Association for Computational Linguistics. URL https://aclanthology.org/W12-3018.

- S. Narayan, S. B. Cohen, and M. Lapata. Ranking sentences for extractive summarization with reinforcement learning. In NAACL, 2018a.

- S. Narayan, S. B. Cohen, and M. Lapata. Don’t give me the details, just the summary! topic-aware convolutional neural networks for extreme summarization. arXiv preprint arXiv:1808.08745, 2018b.

- A. Nenkova and R. J. Passonneau. Evaluating content selection in summarization: The pyramid method. In Proceedings of the human language technology conference of the north american chapter of the association for computational linguistics: Hlt-naacl 2004, pages 145–152, 2004.

- A. Nenkova, L. Vanderwende, and L. Vanderwende. The impact of frequency on summarization. Technical report, Columbia University, 2005.

- A. Nenkova, L. Vanderwende, and K. McKeown. A compositional context sensitive multidocument summarizer: exploring the factors that influence summarization. In Proceedings of the 29th annual international ACM SIGIR conference on Research and development in information retrieval, pages 573–580, 2006.

- A. Nenkova, K. McKeown, et al. Automatic summarization. Foundations and Trends® in Information Retrieval, 5(2–3):103–233, 2011.

- M. E. Newman. The structure and function of complex networks. SIAM review, 45(2):167–256, 2003.

- J.-P. Ng and V. Abrecht. Better summarization evaluation with word embeddings for rouge. arXiv preprint arXiv:1508.06034, 2015.

- M.-T. Nguyen, D. V. Lai, P.-K. Do, D.-V. Tran, and M. Le Nguyen. Vsolscsum: Building a vietnamese sentence-comment dataset for social context summarization. In Proceedings of the 12th Workshop on Asian Language Resources (ALR12), pages 38–48, 2016a.

- M.-T. Nguyen, C.-X. Tran, D.-V. Tran, and M.-L. Nguyen. Solscsum: A linked sentencecomment dataset for social context summarization. In Proceedings of the 25th ACM International on Conference on Information and Knowledge Management, pages 2409–2412, 2016b.

[page 87]

- M.-T. Nguyen, D.-V. Tran, C.-X. Tran, and M.-L. Nguyen. Learning to summarize web documents using social information. In 2016 IEEE 28th International Conference on Tools with Artificial Intelligence (ICTAI), pages 619–626. IEEE, 2016c.

- M.-T. Nguyen, D.-V. Tran, C.-X. Tran, and M.-L. Nguyen. Exploiting user-generated content to enrich web document summarization. International Journal on Artificial Intelligence Tools, 26(05):1760017, 2017.

- M.-T. Nguyen, V. C. Tran, X. H. Nguyen, and L.-M. Nguyen. Web document summarization by exploiting social context with matrix co-factorization. Information Processing & Management, 56(3):495–515, 2019.

- K. Nigam, J. Lafferty, and A. McCallum. Using maximum entropy for text classification. In IJCAI-99 workshop on machine learning for information filtering, volume 1, pages 61–67. Stockholom, Sweden, 1999.

- M. Osborne. Using maximum entropy for sentence extraction. In Proceedings of the ACL-02 Workshop on Automatic Summarization, pages 1–8, 2002.

- J. Otterbacher, G. Erkan, and D. Radev. Using random walks for question-focused sentence retrieval. In Proceedings of human language technology conference and conference on empirical methods in natural language processing, pages 915–922, 2005.

- P. Over, H. Dang, and D. Harman. Duc in context, information processing and management. 2007.

- K. Owczarzak and H. T. Dang. Overview of the tac 2011 summarization track: Guided task and aesop task. In Proceedings of the Text Analysis Conference (TAC 2011), Gaithersburg, Maryland, USA, November, 2011.

- P. Paatero. Least squares formulation of robust non-negative factor analysis. Chemometrics and intelligent laboratory systems, 37(1):23–35, 1997.

- P. Paatero and U. Tapper. Positive matrix factorization: A non-negative factor model with optimal utilization of error estimates of data values. Environmetrics, 5(2):111–126, 1994.

- L. Page, S. Brin, R. Motwani, and T. Winograd. The pagerank citation ranking: Bringing order to the web. Technical report, Stanford InfoLab, 1999.

- C. D. Paice. Constructing literature abstracts by computer: techniques and prospects. Information Processing & Management, 26(1):171–186, 1990.

- K. Papineni, S. Roukos, T. Ward, and W.-J. Zhu. Bleu: a method for automatic evaluation of machine translation. In Proceedings of the 40th annual meeting of the Association for Computational Linguistics, pages 311–318, 2002.

- T. A. S. Pardo and L. H. M. Rino. Temario: a corpus for automatic text summarization. Technical report, NILC Tech. Report NILC-TR-03-09, 2003.

- S. Park, J.-H. Lee, C.-M. Ahn, J. S. Hong, and S.-J. Chun. Query based summarization using non-negative matrix factorization. In International Conference on Knowledge-Based and Intelligent Information and Engineering Systems, pages 84–89. Springer, 2006.

- Y.-J. Park and A. Tuzhilin. The long tail of recommender systems and how to leverage it. In Proceedings of the 2008 ACM conference on Recommender systems, pages 11–18, 2008.

- R. Pascanu, T. Mikolov, and Y. Bengio. On the difficulty of training recurrent neural networks. In International conference on machine learning, pages 1310–1318. PMLR, 2013.

[page 88]

- R. J. Passonneau, E. Chen, W. Guo, and D. Perin. Automated pyramid scoring of summaries using distributional semantics. In Proceedings of the 51st Annual Meeting of the Association for Computational Linguistics (Volume 2: Short Papers), pages 143–147, 2013.

- R. J. Passonneau, A. Poddar, G. Gite, A. Krivokapic, Q. Yang, and D. Perin. Wise crowd content assessment and educational rubrics. International Journal of Artificial Intelligence in Education, 28(1):29–55, 2018.

- J. Pennington, R. Socher, and C. Manning. GloVe: Global vectors for word representation. In Proceedings of the 2014 Conference on Empirical Methods in Natural Language Processing (EMNLP), pages 1532–1543, Doha, Qatar, Oct. 2014.

- M. E. Peters, M. Neumann, M. Iyyer, M. G. C. Clark, K. Lee, and L. Zettlemoyer. Deep contextualized word representations. arXiv preprint arXiv:1802.05365v2, 2018.

- M. Peyrard and J. Eckle-Kohler. Supervised learning of automatic pyramid for optimizationbased multi-document summarization. In Proceedings of the 55th Annual Meeting of the Association for Computational Linguistics (Volume 1: Long Papers), pages 1084–1094, 2017.

- E. Pitler and A. Nenkova. Revisiting readability: A unified framework for predicting text quality. In Proceedings of the 2008 conference on empirical methods in natural language processing, pages 186–195, 2008.

- D. Pollard. A user’s guide to measure theoretic probability. Number 8. Cambridge University Press, 2002.

- S. Pouriyeh, M. Allahyari, K. Kochut, and H. R. Arabnia. A comprehensive survey of ontology summarization: measures and methods. arXiv preprint arXiv:1801.01937, 2018.

- Princeton University. About wordnet. https://wordnet.princeton.edu/, 2022. Accessed: 2022-03-04.

- M. L. Puterman. Markov decision processes: discrete stochastic dynamic programming. John Wiley & Sons, 2014.

- M. L. Puterman and M. C. Shin. Modified policy iteration algorithms for discounted markov decision problems. Management Science, 24(11):1127–1137, 1978.

- W. Qi, Y. Yan, Y. Gong, D. Liu, N. Duan, J. Chen, R. Zhang, and M. Zhou. Prophetnet: Predicting future n-gram for sequence-to-sequence pre-training. In Proceedings of the 2020 Conference on Empirical Methods in Natural Language Processing: Findings, pages 2401– 2410, 2020.

- L. Rabiner and B. Juang. An introduction to hidden markov models. ieee assp magazine, 3(1): 4–16, 1986.

- D. Radev, S. Teufel, H. Saggion, W. Lam, J. Blitzer, H. Qi, A. Celebi, D. Liu, and E. F. Drabek. Evaluation challenges in large-scale document summarization. In Proceedings of the 41st Annual Meeting of the Association for Computational Linguistics, pages 375–382, 2003.

- D. R. Radev, K. McKeown, and V. Hatzivassiloglou. A description of the cidr system as used for tdt-2. 1999.

- D. R. Radev, H. Jing, M. Sty´s, and D. Tam. Centroid-based summarization of multiple documents. Information Processing & Management, 40(6):919–938, 2004.

- A. Radford and K. Narasimhan. Improving language understanding by generative pre-training, 2018.

[page 89]

- A. Radford, J. Wu, R. Child, D. Luan, D. Amodei, I. Sutskever, et al. Language models are unsupervised multitask learners. OpenAI blog, 1(8):9, 2019.

- C. Raffel, N. Shazeer, A. Roberts, K. Lee, S. Narang, M. Matena, Y. Zhou, W. Li, and P. J. Liu. Exploring the limits of transfer learning with a unified text-to-text transformer. arXiv preprint arXiv:1910.10683, 2019.

- N. Rahman and B. Borah. A survey on existing extractive techniques for query-based text summarization. In 2015 International Symposium on Advanced Computing and Communication (ISACC), pages 98–102. IEEE, 2015.

- L. Reeve, H. Han, and A. D. Brooks. Biochain: lexical chaining methods for biomedical text summarization. In Proceedings of the 2006 ACM symposium on Applied computing, pages 180–184, 2006.

- R. Reh˚uˇrek[ˇ] and P. Sojka. Software Framework for Topic Modelling with Large Corpora. In Proceedings of the LREC 2010 Workshop on New Challenges for NLP Frameworks, pages 45–50, Valletta, Malta, May 2010. ELRA. http://is.muni.cz/publication/884893/en.

- A. H. Ribeiro, K. Tiels, L. A. Aguirre, and T. Sch¨on. Beyond exploding and vanishing gradients: analysing rnn training using attractors and smoothness. In International Conference on Artificial Intelligence and Statistics, pages 2370–2380. PMLR, 2020.

- C. Rioux, S. A. Hasan, and Y. Chali. Fear the reaper: A system for automatic multidocument summarization with reinforcement learning. In Proceedings of the 2014 conference on empirical methods in natural language processing (EMNLP), pages 681–690, 2014.

- G. Rossiello, P. Basile, and G. Semeraro. Centroid-based text summarization through compositionality of word embeddings. In MultiLing@EACL, 2017.

- B. Ruhnau. Eigenvector-centrality — a node-centrality? Social Networks, 22(4):357–365, 2000.

- D. E. Rumelhart, G. E. Hinton, and R. J. Williams. Learning internal representations by error propagation. Technical report, California Univ San Diego La Jolla Inst for Cognitive Science, 1985.

- G. A. Rummery and M. Niranjan. On-line Q-learning using connectionist systems, volume 37. Citeseer, 1994.

- J. E. Rush, R. Salvador, and A. Zamora. Automatic abstracting and indexing. ii. production of indicative abstracts by application of contextual inference and syntactic coherence criteria. Journal of the American Society for Information Science, 22(4):260–274, 1971.

- D. Rusu, B. Fortuna, M. Grobelnik, and D. Mladeni´c. Semantic graphs derived from triplets with application in document summarization. Informatica, 33(3), 2009.

- S. Ryang and T. Abekawa. Framework of automatic text summarization using reinforcement learning. In Proceedings of the 2012 Joint Conference on Empirical Methods in Natural Language Processing and Computational Natural Language Learning, pages 256–265, 2012.

- H. Saggion, D. Radev, S. Teufel, and W. Lam. Meta-evaluation of summaries in a crosslingual environment using content-based metrics. In COLING 2002: The 19th International Conference on Computational Linguistics, 2002a.

- H. Saggion, D. R. Radev, S. Teufel, W. Lam, and S. M. Strassel. Developing infrastructure for the evaluation of single and multi-document summarization systems in a cross-lingual environment. In LREC, pages 747–754, 2002b.

[page 90]

- A. A. Saleh and L. Weigang. Language independent text summarization of western european languages using shape coding of text elements. In 2017 13th international conference on natural computation, fuzzy systems and knowledge discovery (ICNC-FSKD), pages 2221– 2228. IEEE, 2017.

- G. Salton. Automatic text processing. Reading: Addison-Wesley, 1989.

- V. Sanh, L. Debut, J. Chaumond, and T. Wolf. Distilbert, a distilled version of bert: smaller, faster, cheaper and lighter. arXiv preprint arXiv:1910.01108, 2019. URL https://arxiv.org/abs/1910.01108.

- C. Saranyamol and L. Sindhu. A survey on automatic text summarization. International Journal of Computer Science and Information Technologies, 5(6):7889–7893, 2014.

- T. Scialom, S. Lamprier, B. Piwowarski, and J. Staiano. Answers unite! unsupervised metrics for reinforced summarization models. arXiv preprint arXiv:1909.01610, 2019.

- E. ShafieiBavani, M. Ebrahimi, R. Wong, and F. Chen. A graph-theoretic summary evaluation for rouge. In Proceedings of the 2018 Conference on Empirical Methods in Natural Language Processing, pages 762–767, 2018.

- E. Sharma, C. Li, and L. Wang. Bigpatent: A large-scale dataset for abstractive and coherent summarization. arXiv preprint arXiv:1906.03741, 2019.

- R. Sheik and S. J. Nirmala. Deep learning techniques for legal text summarization. In 2021 IEEE 8th Uttar Pradesh Section International Conference on Electrical, Electronics and Computer Engineering (UPCON), pages 1–5. IEEE, 2021.

- J. Shetty and J. Adibi. The enron email dataset database schema and brief statistical report. Information sciences institute technical report, University of Southern California, 4(1):120– 128, 2004.

- C. Shorten, T. M. Khoshgoftaar, and B. Furht. Text data augmentation for deep learning. Journal of big Data, 8(1):1–34, 2021.

- N. Simon, J. Friedman, T. Hastie, and R. Tibshirani. Regularization paths for cox’s proportional hazards model via coordinate descent. Journal of statistical software, 39(5):1, 2011.

- S. P. Singh and R. S. Sutton. Reinforcement learning with replacing eligibility traces. Machine learning, 22(1):123–158, 1996.

- K. Song, X. Tan, T. Qin, J. Lu, and T.-Y. Liu. Mass: Masked sequence to sequence pre-training for language generation. In ICML, 2019.

- R. Srivastava, P. Singh, K. Rana, and V. Kumar. A topic modeled unsupervised approach to single document extractive text summarization. Knowledge-Based Systems, 246:108636, 2022.

- J. Steinberger and K. Jeˇzek. Update summarization based on novel topic distribution. In Proceedings of the 9th ACM Symposium on Document Engineering, pages 205–213, 2009.

- J. Steinberger, K. Jezek, et al. Using latent semantic analysis in text summarization and summary evaluation. Proceedings of ISIM, 4(93-100):8, 2004.

- J. Steinberger et al. Evaluation measures for text summarization. Computing and Informatics, 28(2):251–275, 2009.

[page 91]

- G. W. Stewart. On the early history of the singular value decomposition. SIAM review, 35(4): 551–566, 1993.

- M. Stone. Cross-validation: A review. Statistics: A Journal of Theoretical and Applied Statistics, 9(1):127–139, 1978.

- S. Sun and A. Nenkova. The feasibility of embedding based automatic evaluation for single document summarization. In Proceedings of the 2019 conference on empirical methods in natural language processing and the 9th international joint conference on natural language processing (EMNLP-IJCNLP), pages 1216–1221, 2019.

- I. Sutskever, O. Vinyals, and Q. V. Le. Sequence to sequence learning with neural networks. Advances in neural information processing systems, 27, 2014.

- R. S. Sutton. Learning to predict by the methods of temporal differences. Machine learning, 3 (1):9–44, 1988.

- R. S. Sutton. Generalization in reinforcement learning: Successful examples using sparse coarse coding. Advances in neural information processing systems, 8, 1995.

- R. S. Sutton and A. G. Barto. Reinforcement learning: An introduction. MIT press, 2018.

- K. Svore, L. Vanderwende, and C. Burges. Enhancing single-document summarization by combining ranknet and third-party sources. In Proceedings of the 2007 joint conference on empirical methods in natural language processing and computational natural language learning (EMNLP-CoNLL), pages 448–457, 2007.

- J. Tandel, K. Mistree, and P. Shah. A review on neural network based abstractive text summarization models. In 2019 IEEE 5th International Conference for Convergence in Technology (I2CT), pages 1–4. IEEE, 2019.

- A. Tashimo, Y. Mitamura, S. Nagai, Y. Nakamura, K. Ohtsuka, Y. Mizue, and J. Nishihira. Aqueous levels of macrophage migration inhibitory factor and monocyte chemotactic protein1 in patients with diabetic retinopathy. Diabetic Medicine, 21(12):1292–1297, 2004.

- W. L. Taylor. “cloze procedure”: A new tool for measuring readability. Journalism quarterly, 30(4):415–433, 1953.

- S. Teufel. Task-based evaluation of summary quality: Describing relationships between scientific papers. In In Workshop Automatic Summarization, NAACL. Citeseer, 2001.

- K. S. Thakkar, R. V. Dharaskar, and M. Chandak. Graph-based algorithms for text summarization. In 2010 3rd International Conference on Emerging Trends in Engineering and Technology, pages 516–519. IEEE, 2010.

- A. Tombros and M. Sanderson. Advantages of query biased summaries in information retrieval. In Proceedings of the 21st annual international ACM SIGIR conference on Research and development in information retrieval, pages 2–10, 1998.

- J.-M. Torres-Moreno, H. Saggion, I. d. Cunha, E. SanJuan, and P. Vel´azquez-Morales. Summary evaluation with and without references. Polibits, (42):13–20, 2010.

- T. U¸ckan and A. Karcı. Extractive multi-document text summarization based on graph independent sets. Egyptian Informatics Journal, 21(3):145–157, 2020.

- R. Vadapalli, L. J. Kurisinkel, M. Gupta, and V. Varma. Ssas: semantic similarity for abstractive summarization. In Proceedings of the Eighth International Joint Conference on Natural Language Processing (Volume 2: Short Papers), pages 198–203, 2017.

[page 92]

- H. Van Halteren and S. Teufel. Examining the consensus between human summaries: initial experiments with factoid analysis. In Proceedings of the HLT-NAACL 03 Text Summarization Workshop, pages 57–64, 2003.

- H. Van Lierde and T. W. Chow. Query-oriented text summarization based on hypergraph transversals. Information Processing & Management, 56(4):1317–1338, 2019.

- O. Vasilyev, V. Dharnidharka, and J. Bohannon. Fill in the blanc: Human-free quality estimation of document summaries. arXiv preprint arXiv:2002.09836, 2020.

- A. Vaswani, N. Shazeer, N. Parmar, J. Uszkoreit, L. Jones, A. N. Gomez, �L. Kaiser, and I. Polosukhin. Attention is all you need. In Advances in neural information systems, pages 5998–6008, 2017.

- O. Vinyals and Q. Le. A neural conversational model. arXiv preprint arXiv:1506.05869, 2015.

- X. Wan and J. Yang. Improved affinity graph based multi-document summarization. In Proceedings of the human language technology conference of the NAACL, Companion volume: Short papers, pages 181–184, 2006.

- D. Wang, S. Zhu, T. Li, and Y. Gong. Multi-document summarization using sentence-based topic models. In Proceedings of the ACL-IJCNLP 2009 conference short papers, pages 297– 300, 2009.

- L. Wang and W. Ling. Neural network-based abstract generation for opinions and arguments. arXiv preprint arXiv:1606.02785, 2016.

- Y.-X. Wang and Y.-J. Zhang. Nonnegative matrix factorization: A comprehensive review. IEEE Transactions on knowledge and data engineering, 25(6):1336–1353, 2012.

- C. J. C. H. Watkins. Learning from delayed rewards. PhD thesis, King’s College, Cambridge United Kingdom, 1989.

- R. W. White, J. M. Jose, and I. Ruthven. A task-oriented study on the influencing effects of query-biased summarisation in web searching. Information Processing & Management, 39(5): 707–733, 2003.

- M. J. Witbrock and V. O. Mittal. Ultra-summarization (poster abstract) a statistical approach to generating highly condensed non-extractive summaries. In Proceedings of the 22nd annual international ACM SIGIR conference on Research and development in information retrieval, pages 315–316, 1999.

- T. Wolf, L. Debut, V. Sanh, J. Chaumond, C. Delangue, A. Moi, P. Cistac, C. Ma, Y. Jernite, J. Plu, C. Xu, T. Le Scao, S. Gugger, M. Drame, Q. Lhoest, and A. M. Rush. Transformers: State-of-the-Art Natural Language Processing. pages 38–45. Association for Computational Linguistics, 10 2020. URL https://www.aclweb.org/anthology/2020.emnlp-demos.6.

- C.-W. Wu and C.-L. Liu. Ontology-based text summarization for business news articles. In CATA, pages 389–392, 2003.

- S. Xenouleas, P. Malakasiotis, M. Apidianaki, and I. Androutsopoulos. Sumqe: a bert-based summary quality estimation model. arXiv preprint arXiv:1909.00578, 2019.

- D. Xiao, H. Zhang, Y. Li, Y. Sun, H. Tian, H. Wu, and H. Wang. Ernie-gen: An enhanced multi-flow pre-training and fine-tuning framework for natural language generation. arXiv preprint arXiv:2001.11314, 2020.

[page 93]

- C. Xu and J. McAuley. A survey on dynamic neural networks for natural language processing. arXiv preprint arXiv:2202.07101, 2022.

- Q. Yang, R. J. Passonneau, and G. De Melo. Peak: Pyramid evaluation via automated knowledge extraction. In Thirtieth AAAI Conference on Artificial Intelligence, 2016.

- Z. Yang, F. Yao, H. Sun, Y. Zhao, Y. Lai, and K. Fan. Bjut at trec 2013 temporal summarization track. In TREC, 2013.

- K. Yao, L. Zhang, T. Luo, and Y. Wu. Deep reinforcement learning for extractive document summarization. Neurocomputing, 284:52–62, 2018.

- M. Yasunaga, J. Kasai, R. Zhang, A. R. Fabbri, I. Li, D. Friedman, and D. R. Radev. Scisummnet: A large annotated corpus and content-impact models for scientific paper summarization with citation networks. In Proceedings of the AAAI conference on artificial intelligence, volume 33, pages 7386–7393, 2019.

- W.-t. Yih, J. Goodman, L. Vanderwende, and H. Suzuki. Multi-document summarization by maximizing informative content-words. In IJCAI, volume 7, pages 1776–1782, 2007.

- W. Yin and Y. Pei. Optimizing sentence modeling and selection for document summarization. In Twenty-fourth international joint conference on artificial intelligence, 2015.

- D. Yogatama, F. Liu, and N. A. Smith. Extractive summarization by maximizing semantic volume. In Proceedings of the 2015 Conference on Empirical Methods in Natural Language Processing, pages 1961–1966, 2015.

- S. Zdenek. Which sounds are significant? towards a rhetoric of closed captioning. Disability Studies Quarterly, 31(3), 2011.

- J. Zhang, Y. Zhao, M. Saleh, and P. Liu. Pegasus: Pre-training with extracted gap-sentences for abstractive summarization. In International Conference on Machine Learning, pages 11328– 11339. PMLR, 2020.

- P. Y. Zhang and C. Li. Automatic text summarization based on sentences clustering and extraction. 2009 2nd IEEE International Conference on Computer Science and Information Technology, pages 167–170, 2009.

- R. Zhang and J. Tetreault. This email could save your life: Introducing the task of email subject line generation. arXiv preprint arXiv:1906.03497, 2019.

- T. Zhang, V. Kishore, F. Wu, K. Q. Weinberger, and Y. Artzi. Bertscore: Evaluating text generation with bert. arXiv preprint arXiv:1904.09675, 2019.

- W. Zhang, J. Tanida, K. Itoh, and Y. Ichioka. Shift-invariant pattern recognition neural network and its optical architecture. In Proceedings of annual conference of the Japan Society of Applied Physics, pages 2147–2151, 1988.

- X. Zhang, M. Lapata, F. Wei, and M. Zhou. Neural latent extractive document summarization. arXiv preprint arXiv:1808.07187, 2018.

- W. Zhao, M. Peyrard, F. Liu, Y. Gao, C. M. Meyer, and S. Eger. Moverscore: Text generation evaluating with contextualized embeddings and earth mover distance. arXiv preprint arXiv:1909.02622, 2019.

- Y. Zhao, F. Yao, H. Sun, and Z. Yang. Bjut at trec 2014 temporal summarization track. Technical report, BEIJING UNIVERSTIY OF TECHNOLOGY (CHINA), 2014.

[page 94]

- L. Zhou, C.-Y. Lin, D. S. Munteanu, and E. Hovy. Paraeval: Using paraphrases to evaluate summaries automatically. In Proceedings of the human language technology conference of the NAACL, main conference, pages 447–454, 2006.

- Q. Zhou, N. Yang, F. Wei, S. Huang, M. Zhou, and T. Zhao. Neural document summarization by jointly learning to score and select sentences. arXiv preprint arXiv:1807.02305, 2018.

- F. Zhuang, Z. Qi, K. Duan, D. Xi, Y. Zhu, H. Zhu, H. Xiong, and Q. He. A comprehensive survey on transfer learning. Proceedings of the IEEE, 109(1):43–76, 2020.

- R. A. Zwaan, M. C. Langston, and A. C. Graesser. The construction of situation models in narrative comprehension: An event-indexing model. Psychological science, 6(5):292–297, 1995.
