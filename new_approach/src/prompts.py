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

