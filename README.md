# Explainable Machine Learning Tutorial

## Book Structure

This book discusses four topics:

1. XML basics
2. Explainability in Language Models
3. Explainable Reinforcement Learning
4. Explainabile Multi-Agent Systems

Each topic follows the same file structure:

- **File 1: Introduction.** This includes motivation and one running example or theme (e.g., "toxicity in LLMs" for the topic "Explainability in Language Models"); explainability methods explained later will be applied to this example to showcase their specific goals and strenghts.
- **File 2: Taxonomy.** This should include one high-level figure, giving the reader a mental model of the landscape of explainability methods in this topic.
- **Files 3, 4, ...: Methods.** This is the place for intuition-building (e.g., 1 adapted figure per method) and presenting key formulas and ideas of concrete methods. The file structure here is flexible to make each topic as accessible as possible. For example, if we discuss only 3 distinct methods in a topic, we might give each of them a separate `.qmd` file; alternatively, relevant methods can be grouped together according to the introduced taxonomy.
- **File n-1: Applications.** This takes a step back again after the nitty-gritty method explanations and gives room to discuss the effectiveness of applying the methods to real-world applications.
- **File n: Conclusion.** Any last words; this can be brief.

## Setup

Install Quarto and compile with `quarto preview` for a quick view on how things look.

## Acronyms

We use the Quarto extension `rchaput/acronyms` to manage acronyms, similar to `\gls` in LaTeX. The first occurence *on each Quarto page* will be spelled out in its long form.

**Defining Acronyms:**
Add new acronyms to the `acronyms.yml` file at the root of the project.

**Usage in Text:**
Use the following Quarto shortcodes in your .qmd files instead of standard LaTeX commands. Here are some examples:

* Standard: `\acr{rl}` $\rightarrow$ reinforcement learning (RL)
* Sentence case: `\acr[case=sentence]{rl}` $\rightarrow$ Reinforcement learning (RL)
* Plural: `\acr[plural=true]{llm}` $\rightarrow$ large language models (LLMs)
* Sentence case plural: `\acr[case=sentence, plural=true]{llm}` $\rightarrow$ Large language models (LLMs)
