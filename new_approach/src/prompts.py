prompt_1 = """
**DEFINITIONS FOR ANALYSIS:**
-   *fairness_bias_mentioned*: Yes if fairness, algorithmic bias, discrimination prevention, or equitable AI outcomes are discussed. No if fairness refers to unrelated topics like prices or competition rules.
-   *data_privacy*: Yes if privacy, PII protection, anonymization, secure data handling, or compliance (e.g. GDPR) is mentioned. No if it only talks about generic data use or storage.
-   *toy*: Yes if competition is mainly for learning or practice (keywords: playground, getting started, educational) or has very low/no prize. No if serious prizes or deployment goals are mentioned.
-   *red_team*: Yes if focus is on adversarial testing, finding vulnerabilities, stress-testing models, or harm discovery. No if just normal model evaluation.
-   *transparency_mentioned*: Yes if transparency, explainability, reproducibility, open code, or clear documentation are mentioned for model/data/evaluation. No if transparency is only about logistics like rules or pricing.
"""

prompt_2 = """
**DEFINITIONS FOR ANALYSIS:**
    - *fairness_bias_mentioned*: Yes if fairness, algorithmic bias, discrimination prevention, or equitable AI outcomes are discussed with respect to the competition dataset, task, or evaluation (e.g., removing bias from labels, ensuring equal model performance across groups). No if fairness is about competitors, pricing, or generic rules.
	- *data_privacy*: Yes if privacy, PII protection, anonymization, secure data handling, or compliance (e.g. GDPR) is mentioned for the competition dataset or provided resources (e.g., how data was anonymized, restrictions on data use). No if it is about participant privacy or general data storage.
	- *toy*: Yes if the competition is mainly for practice/learning (keywords: playground, getting started, educational) or has very low/no prize, indicating a resource to experiment with rather than a serious deployment challenge. No if it targets production use or has significant rewards.
	- *red_team*: Yes if the competition goal is adversarial testing of provided data/models/resources — finding vulnerabilities, stress-testing, or harm discovery. No if it's just a normal prediction or optimization task without adversarial focus.
	- *transparency_mentioned*: Yes if transparency, explainability, reproducibility, open code, or documentation are discussed for the competition dataset, task setup, or evaluation process (e.g., dataset creation process is explained, evaluation is reproducible). No if transparency is only about competition logistics like rules or schedule.
"""

prompt_3 = """
**DEFINITIONS FOR ANALYSIS:**
    - *fairness_bias_mentioned*: yes or no, depending on whether fairness and bias of the model and dataset are explicitly mentioned in the descriptions or overview. Please be advised that fairness in data science refers to the equitable and just treatment of individuals by algorithms and models. It focuses on ensuring that decisions made by automated systems do not favor one group of individuals over another on the basis of sensitive characteristics such as race, gender, age, or other protected attributes. Bias in data science refers to systemic deviation in the data or model that leads to less accurate, unfair, or unethical outcomes.
	- *data_privacy*: yes or no, depending on whether you think the data used in the competition has data privacy issues (e.g., sensitive personal information, unauthorized data use, data breaches). If data privacy issues are present, explain how they are addressed and whether there are flaws in the approach.
	- *toy*: yes if the competition is mainly for practice/learning (keywords: playground, getting started, educational) or has very low/no prize, indicating a resource to experiment with rather than a serious deployment challenge. no if it targets production use or has significant rewards.
	- *red_team*: yes if the competition goal is adversarial testing of provided data/models/resources — finding vulnerabilities, stress-testing, or harm discovery. no if it's just a normal prediction or optimization task without adversarial focus.
	- *transparency_mentioned*: yes or no, depending on whether model transparency and explainability are explicitly mentioned as evaluation criteria. If the competition only focuses on a single best performance metric without considering model transparency, tell me what the metric is after "n/a".
"""


NOTES:
- "data privacy: only competyion data, not participant data"
- "transparency: only transparency and not explainability"
- "explainability: add field. only explainability and not transparency"
- "what are they going to do with the final model?"



"""
You are an expert AI assistant specializing in analyzing text for specific ethical and practical characteristics of data science competitions. Your task is to analyze the user-provided 'context' and generate a single, valid JSON object with a specific, flat structure.

**CRITICAL RULES:**
1. Your entire response MUST be a single, valid JSON object. Do not include any text, explanations, or markdown formatting outside of the JSON.
2. The JSON object MUST have a flat structure. DO NOT use nested JSON objects.
3. Your analysis MUST be based ONLY on the provided 'context'. Do not infer or use external knowledge.
4. For each topic, you will provide a "yes" or "no" answer for the boolean key (e.g., fairness_bias_mentioned).
5. If the answer is "yes", you MUST provide a brief explanation and directly quote the relevant text (up to 50 words) in the corresponding 'how' key (e.g., how_fairness).
6. If the answer is "no", the corresponding 'how' key MUST be an NA string ("n/a"), unless specified otherwise in the definitions below.

**REQUIRED JSON OUTPUT STRUCTURE (MUST FOLLOW EXACTLY):**

```json
{
  "category": "healthcare",
  "fairness_bias_mentioned": "no",
  "how_fairness": "n/a",
  "data_privacy": "yes",
  "how_data_privacy": "The relevant quote and explanation for why data privacy is mentioned.",
  "transparency_mentioned": "yes",
  "how_transparency": "The relevant quote and explanation for why transparency is mentioned.",
  "data_explainability": "no",
  "how_explainability": "n/a - AUC",
  "post_competition_model_use": "yes",
  "how_model_use": "The relevant quote and explanation for why post-competition model use is mentioned.",
  "toy": "yes",
  "how_toy": "The relevant quote and explanation for why it's a toy competition.",
  "red_team": "no",
  "how_red_team": "n/a"
}
```

**DEFINITIONS FOR ANALYSIS:**

- *category*: The field or industry the competition belongs to, the dataset is about, or the problem/task is about.
- *fairness_bias_mentioned*: "yes" if fairness, algorithmic bias, discrimination prevention, or equitable AI outcomes are discussed with respect to the competition dataset, task, or evaluation (e.g., removing bias from labels, ensuring equal model performance across groups). "no" if fairness is about competitors, pricing, or generic rules.
- *data_privacy*: "yes" if privacy, PII protection, anonymization, secure data handling, or compliance (e.g. GDPR) is mentioned for the competition dataset or provided resources (e.g., how data was anonymized, restrictions on data use). "no" if it is about participant privacy or general data storage.
- *transparency_mentioned*: "yes" if transparency, reproducibility, open code, or documentation are discussed for the competition dataset, task setup, or evaluation process (e.g., dataset creation process is explained, evaluation is reproducible). "no" if transparency is only about competition logistics like rules or schedule.
- *data_explainability*: "yes" if the competition asks participants to explain their model's predictions or behavior (e.g., using SHAP, LIME, or other XAI techniques). "no" if evaluation is based solely on performance metrics. For a "no" answer, the 'how' field must state "n/a" followed by the primary evaluation metric (e.g., "n/a - F1 Score").
- *model_use*: "yes" if the rules or description mention a specific plan for the submitted models or solutions after the competition ends (e.g., "the winning model will be deployed," "top solutions will be featured in a research paper"). "no" if there is no mention of post-competition use.
- *toy*: "yes" if the competition is mainly for practice/learning (keywords: playground, getting started, educational) or has very low/no prize, indicating a resource to experiment with rather than a serious deployment challenge. "no" if it targets production use or has significant rewards.
- *red_team*: "yes" if the competition goal is adversarial testing of provided data/models/resources—finding vulnerabilities, stress-testing, or harm discovery. "no" if it's just a normal prediction or optimization task without adversarial focus.
"""