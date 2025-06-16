# **Navigating Data Protection in 2025: GDPR Compliance for AI Agent-Based Products**

## **I. Executive Summary**

The proliferation of Artificial Intelligence (AI) agent-based products necessitates a rigorous and forward-looking approach to data protection, particularly under the General Data Protection Regulation (GDPR). As of 2025, the regulatory landscape is characterized by the established framework of the GDPR, complemented and increasingly intertwined with AI-specific legislation such as the EU AI Act. This report provides an expert analysis of best practices for ensuring GDPR compliance for AI agent-based products, emphasizing the enduring relevance of core data protection principles, the implications of recent legal and regulatory developments, and strategies for addressing the unique challenges posed by the autonomous and data-intensive nature of AI agents.

Key findings underscore that compliance is not a static achievement but an ongoing commitment, demanding robust data governance, meticulous Data Protection Impact Assessments (DPIAs), and a clear lawful basis for all processing activities. The dynamic learning capabilities of AI agents present specific challenges to principles like purpose limitation and data minimisation, requiring innovative technical and organizational measures. Recent Court of Justice of the European Union (CJEU) rulings and guidance from bodies like the European Data Protection Board (EDPB) and national Data Protection Authorities (DPAs) are shaping the interpretation of GDPR in the context of AI, particularly concerning transparency in automated decision-making, the use of legitimate interests for data processing, and the threshold for data anonymisation.

For AI agent-based products, bespoke best practices are crucial. These include implementing explainable AI (XAI) techniques, ensuring data subject rights can be effectively exercised even when data is embedded in complex models, proactively addressing potential biases and inaccuracies in AI outputs, and fortifying systems against novel AI-specific security threats. Data Protection by Design and by Default (DPbDD) must be a foundational element, supported by Privacy Enhancing Technologies (PETs) where appropriate.

Successfully navigating this complex environment requires organizations to adopt a proactive, adaptive, and risk-based compliance posture. This involves fostering a strong internal culture of data privacy and AI ethics, investing in transparency technologies, conducting thorough vendor due diligence, and maintaining comprehensive documentation. Ultimately, robust GDPR compliance is not merely a legal obligation but a cornerstone for building trust in AI and unlocking its transformative potential responsibly.

## **II. Introduction: GDPR and AI Agents in the 2025 Landscape**

The regulatory and technological environment surrounding Artificial Intelligence (AI) agents in 2025 is marked by significant evolution and increasing complexity. The General Data Protection Regulation (GDPR) remains the cornerstone of data protection in the European Union, setting a global standard for how personal data must be handled.<sup>1</sup> Concurrently, AI agent-based products are becoming increasingly prevalent, promising substantial societal and economic impacts through their capacity for autonomous action and sophisticated data processing.<sup>4</sup> This confluence necessitates a nuanced understanding of how established data protection principles apply to these advanced technologies.

A critical development is the phased entry into force of the EU AI Act, which introduces a risk-based regulatory framework for AI systems. This legislation operates in conjunction with the GDPR, creating an intricate regulatory interplay, particularly for AI systems that process personal data.<sup>7</sup> The AI Act categorizes AI systems based on risk, with "high-risk" systems subject to stringent obligations, many of which intersect with or expand upon GDPR requirements concerning data governance, transparency, security, and impact assessment.<sup>10</sup> The global momentum towards enhanced user data protection and the promotion of ethical AI further underscores the significance of GDPR compliance, with the Regulation often serving as an influential model for other jurisdictions.<sup>11</sup>

The imperative for robust data protection extends beyond mere legal compliance; it is a fundamental prerequisite for fostering user trust and enabling responsible AI innovation.<sup>11</sup> As AI technologies become more integrated into daily life and business operations, ensuring that personal data is processed lawfully, fairly, and securely is paramount. The increasing number of reported AI-related incidents and the widespread acknowledgment of Responsible AI (RAI) risks by organizations highlight the critical need for effective data protection strategies.<sup>12</sup>

The regulatory landscape for AI in 2025 is thus a complex tapestry woven from established data protection laws like GDPR and new, AI-specific regulations like the AI Act. This necessitates a holistic compliance strategy rather than a siloed approach. Organizations cannot treat these regulations in isolation; compliance efforts must be coordinated to address the full spectrum of legal obligations. For instance, the AI Act's risk-based approach will inevitably influence how GDPR's requirements, such as those for Data Protection Impact Assessments (DPIAs) and security measures, are applied to AI systems, particularly those classified as high-risk.

Furthermore, the very definition of an "AI system" under the AI Act is subject to ongoing guidance and interpretation.<sup>15</sup> This means organizations must remain vigilant in assessing whether their technologies fall within the AI Act's scope. Such a determination is crucial, as it directly impacts their GDPR obligations if personal data is processed by these systems. The dynamic nature of AI means this definition might capture an increasing number of systems over time, bringing them under the dual scrutiny of both the AI Act and GDPR.

## **III. Foundational GDPR Principles: Enduring Relevance for AI Agent-Based Products**

The core principles enshrined in Article 5 of the GDPR provide the bedrock for lawful and ethical data processing. Their relevance is not diminished but rather amplified in the context of complex AI agent-based products. Adherence to these principles is fundamental for ensuring compliance and building trust in AI technologies.

- **Lawfulness, Fairness, and Transparency:** Personal data must be processed lawfully, fairly, and in a transparent manner in relation to the data subject.<sup>1</sup>
  - **Lawfulness:** Every processing activity undertaken by an AI agent, from its training phase to its operational deployment and learning cycles, must be grounded in a valid legal basis as defined in Article 6 GDPR (and Article 9 for special categories of data).<sup>3</sup>
  - **Fairness:** Processing must not be unjustly detrimental, discriminatory, unexpected, or misleading to data subjects.<sup>1</sup> This is particularly pertinent for AI agents, whose decision-making can be opaque and potentially biased.
  - **Transparency:** Data subjects must be provided with clear, concise, and easily understandable information about how their personal data is collected, used, and processed by AI agents.<sup>11</sup> This includes information about the purposes of processing, the categories of data involved, retention periods, their rights, and, crucially for AI, meaningful information about the logic involved in automated decision-making.<sup>17</sup>
- **Purpose Limitation:** Personal data must be collected for specified, explicit, and legitimate purposes and not further processed in a manner that is incompatible with those initial purposes.<sup>1</sup> This principle faces unique challenges with AI agents that possess learning capabilities and can adapt their behavior over time, potentially leading to the processing of personal data for new purposes not originally envisaged or communicated to the data subject.<sup>4</sup>
- **Data Minimisation:** Only personal data that are adequate, relevant, and limited to what is necessary for the purposes for which they are processed should be collected and used.<sup>1</sup> AI systems, including agents, are often perceived as data-hungry. However, the data minimisation principle mandates that they be designed to collect, process, and retain only the minimum amount of personal data required for their specified functions.<sup>4</sup>
- **Accuracy:** Personal data must be accurate and, where necessary, kept up to date. Every reasonable step must be taken to ensure that personal data that are inaccurate, having regard to the purposes for which they are processed, are erased or rectified without delay.<sup>1</sup> The outputs of AI agents, which can sometimes be affected by inaccuracies or "hallucinations" (i.e., generating confident but false information), pose a direct challenge to this principle, especially if these outputs are used to make decisions about individuals.<sup>5</sup>
- **Storage Limitation:** Personal data must be kept in a form which permits identification of data subjects for no longer than is necessary for the purposes for which the personal data are processed.<sup>1</sup> This requires organizations to establish clear data retention policies for all personal data processed by AI agents, including training datasets, input data, output data, and interaction logs. Data should be deleted or anonymised once it is no longer necessary.
- **Integrity and Confidentiality (Security):** Personal data must be processed in a manner that ensures appropriate security, including protection against unauthorised or unlawful processing and against accidental loss, destruction, or damage, using appropriate technical or organisational measures.<sup>1</sup> AI agents, given their connectivity and data processing capabilities, require robust security measures to protect against traditional cyber threats as well as AI-specific vulnerabilities such as model poisoning, adversarial attacks, and data leakage through the agent itself.<sup>3</sup>
- **Accountability:** The controller is responsible for, and must be able to demonstrate compliance with, all the above principles.<sup>1</sup> This principle is paramount for AI systems. Given the potential complexity and opacity (the "black box" nature) of some AI agents <sup>7</sup>, demonstrating compliance requires comprehensive documentation, robust governance frameworks, regular audits, and the implementation of technical measures that allow for the verification of the agent's operations.<sup>2</sup>

The accountability principle, in effect, acts as a meta-principle for AI agents. It demands not just adherence to the other data protection principles but also the demonstrable proof of such compliance. The inherent complexity of AI makes this demonstration particularly challenging. Therefore, accountability for AI agents must extend beyond mere policy statements to include robust technical measures that ensure verifiability and traceability of data processing activities.

A significant tension arises between the principle of "Purpose Limitation" and the dynamic learning capabilities inherent in many AI agents. GDPR strictly defines purpose limitation based on "specified, explicit and legitimate purposes" determined at the point of data collection.<sup>1</sup> However, sophisticated AI agents, as noted in <sup>4</sup>, "could make dynamic decisions to change their behaviour over time, this could result in them processing personal data for a new purpose not originally intended." This potential for "purpose creep" creates a direct conflict with the GDPR, necessitating careful governance mechanisms. These might include re-evaluating the lawful basis for processing, obtaining new consent if the original purpose changes significantly, or designing agents with inherent limitations on purpose evolution.

Similarly, "Data Minimisation" for AI agents is not a static, one-time action but an ongoing obligation. The GDPR requires that personal data be "adequate, relevant and limited to what is necessary".<sup>17</sup> AI agents that "keep track of past interactions" (memory) and "learn from user feedback" <sup>4</sup> have the potential to accumulate vast datasets over time. Without active and continuous minimisation strategies—such as periodic reviews of data necessity, automated deletion of non-essential data, or techniques for data abstraction and aggregation—organizations risk non-compliance. The challenge lies in retaining sufficient data for the agent's effective learning and personalization capabilities while strictly adhering to the minimisation principle.

The following table summarizes the core GDPR principles and their specific implications and challenges in the context of AI agent-based products:

\\begin{table}\[h!\]

\\centering

\\caption{GDPR Principles & Specific Implications for AI Agents}

\\label{tab:gdpr_principles_ai}

\\begin{tabular}{|p{2.5cm}|p{3.5cm}|p{4.5cm}|p{4cm}|}

\\hline

\\textbf{GDPR Principle} & \\textbf{General Definition (Art. 5 GDPR)} & \\textbf{Specific Implications for AI Agents} & \\textbf{Key Challenges for AI Agents} \\

\\hline

Lawfulness, Fairness, Transparency & Processed lawfully, fairly, transparently 1 & Clear lawful basis for all AI processing stages (training, operation, learning). Fair processing, avoiding bias. Transparent information on data use, ADM logic. & Establishing lawful basis for vast training data. Ensuring fairness in algorithmic outputs. Explaining complex AI logic simply. \\

\\hline

Purpose Limitation & Collected for specified, explicit, legitimate purposes; no incompatible further processing 1 & Initial purposes must be clearly defined. Monitor for "purpose creep" as agents learn/adapt. New lawful basis/consent if purposes evolve incompatibly. & Dynamic learning leading to new, unintended data uses.4 Defining scope for general-purpose AI. \\

\\hline

Data Minimisation & Adequate, relevant, limited to necessary 17 & Collect/process only data essential for agent's defined tasks and learning. Ongoing evaluation of data necessity. & Agents' tendency to accumulate data ("memory," interaction logs 4). Balancing learning needs with minimisation. \\

\\hline

Accuracy & Accurate and kept up to date; rectify/erase inaccuracies 1 & Ensure accuracy of training data and agent outputs. Address AI "hallucinations" and output errors. & Agents generating plausible but incorrect information.5 Correcting inaccuracies within trained models. \\

\\hline

Storage Limitation & Kept identifiable no longer than necessary 1 & Define retention periods for all data categories (training, interaction, logs). Securely delete/anonymise data when no longer needed. & Managing large volumes of data with varying retention needs. Technical challenges of erasing data from trained models. \\

\\hline

Integrity and Confidentiality (Security) & Processed securely, protecting against unauthorised/unlawful processing, loss, destruction, damage 1 & Robust security for data, models, and agent interactions. Defend against AI-specific attacks (e.g., prompt injection, model inversion 5). & Novel and evolving AI attack vectors. Securing autonomous agent actions and data access. \\

\\hline

Accountability & Controller responsible for and must demonstrate compliance 1 & Comprehensive documentation of all AI data processing, decisions, DPIAs, LIAs, security measures. Ability to audit agent behaviour. & "Black box" nature of some AI.20 Demonstrating compliance for dynamic, learning systems. \\

\\hline

\\end{tabular}

\\end{table}

## **IV. Key GDPR Compliance Imperatives for 2025**

Achieving and maintaining GDPR compliance for AI agent-based products in 2025 requires a multifaceted approach, focusing on robust governance, thorough risk assessment, lawful data processing, state-of-the-art security, diligent breach management, and the integral involvement of Data Protection Officers (DPOs).

Robust Data Governance and Accountability Frameworks:

A cornerstone of GDPR compliance is the establishment of a strong data governance framework. This involves clearly defining roles and responsibilities for the development, deployment, and oversight of AI agents.2 Crucially, this includes assigning ownership for decisions made or supported by AI agents, ensuring that there is a clear line of accountability even when processes are automated.19 Comprehensive documentation of all data processing activities is mandatory under Article 30 GDPR (Records of processing activities). For AI systems, this documentation must be particularly detailed, covering data sources, the specific purposes for which data is processed at each stage of the AI lifecycle (training, testing, operation, learning), access controls, data sharing arrangements, and retention periods.2 Given the dynamic nature of AI agents that learn and adapt, this documentation must be treated as a living record, regularly updated to reflect changes in processing activities.4 Regular audits and compliance reviews are essential to verify that AI systems operate as intended and in accordance with GDPR requirements and internal policies.2

Conducting Effective Data Protection Impact Assessments (DPIAs) for AI:

The processing of personal data by AI agents, particularly those involving novel technologies, large-scale processing, systematic monitoring, or automated decision-making with significant effects, is often classified as "high-risk" under GDPR Article 35. This designation mandates the completion of a DPIA before the processing begins.1 DPIAs for AI systems must systematically identify and assess the potential risks to the rights and freedoms of data subjects. This assessment must extend beyond traditional data protection risks to include AI-specific concerns such as algorithmic bias, lack of transparency (opacity), potential for errors or "hallucinations," and unique security vulnerabilities.27 The DPIA process should not be a one-off exercise but should be integrated into the AI development lifecycle from the earliest stages, embodying the principle of "privacy by design," and should be revisited and updated as the AI system evolves or new risks emerge.27 Consultation with the DPO is a requirement during the DPIA process, and if the DPIA indicates high risks that cannot be adequately mitigated, consultation with the relevant supervisory authority may be necessary.29 The findings of a DPIA should directly inform the design and operational parameters of the AI agent, influencing decisions on data minimisation techniques, the types of security safeguards implemented, and the necessity and nature of human oversight mechanisms.

Ensuring Lawful Basis for all Processing Activities:

Under Article 6 GDPR, all processing of personal data must have a valid lawful basis. For AI agents, this requirement applies to each distinct processing activity throughout their lifecycle, from the initial collection of data for training, the training process itself, the processing of data during the agent's operation, data utilized for the agent's ongoing learning and improvement, and any data sharing undertaken by the agent.1 This granularity is critical because different stages might involve different data types, purposes, and risk profiles, potentially necessitating distinct lawful bases or renewed assessments.

- **Consent (Article 7 GDPR):** Where consent is relied upon, it must be freely given, specific, informed, and unambiguous.<sup>3</sup> Obtaining such consent can be particularly challenging for complex AI processing, where fully explaining all potential data uses and implications to data subjects in a clear and understandable manner is difficult.
- **Legitimate Interests (Article 6(1)(f) GDPR):** Reliance on legitimate interests requires a meticulously documented Legitimate Interests Assessment (LIA). This involves a three-part test: identifying the legitimate interest pursued by the controller or a third party; demonstrating the necessity of the processing for achieving that interest; and balancing this interest against the fundamental rights and freedoms of the data subject. This balancing act is especially critical for data-intensive AI model training, particularly when using publicly available or web-scraped data.<sup>21</sup> EDPB Opinion 28/2024 provides detailed criteria for conducting LIAs in the context of AI.<sup>21</sup>

Implementing State-of-the-Art Security Measures (Technical and Organisational - TOMs):

Article 32 GDPR mandates the implementation of appropriate TOMs to ensure a level of security appropriate to the risk. For AI agents, this involves protecting personal data against unauthorized access, alteration, destruction, or loss.3 Standard security measures such as encryption, pseudonymisation, robust access controls, multi-factor authentication, and regular security audits remain essential.2 However, AI agents also introduce novel security threats that require specialized defenses. These include model poisoning (corrupting training data to manipulate outcomes), adversarial attacks (crafting inputs to deceive models), prompt injection (tricking agents into unintended actions), and data leakage through the agent's interactions or memory.5 The concept of "state-of-the-art security" for AI agents is therefore a dynamic and evolving target. As AI attack vectors develop, organizations must continuously update their security measures beyond traditional cybersecurity practices to incorporate AI-specific defenses, reflecting ongoing research and adaptation of security protocols.

Data Breach Management and Notification:

Organizations must have well-defined and tested procedures in place to detect, respond to, mitigate, and report personal data breaches in accordance with GDPR Articles 33 (notification to the supervisory authority) and 34 (communication to the data subject).2 Given the potential for AI agents to process large volumes of data rapidly and operate autonomously, the ability to quickly detect a breach and initiate response protocols is of heightened importance.

The Role of the Data Protection Officer (DPO):

Where a DPO is appointed, they play a crucial advisory and oversight role. The DPO should be involved in all significant stages of AI agent development and deployment, particularly in the conduct of DPIAs, advising on compliance with GDPR, and acting as a point of contact for supervisory authorities and data subjects.1

## **V. Navigating the Evolving Legal Landscape: CJEU Rulings and Regulatory Guidance (2025 Focus)**

The legal framework governing data protection and AI is not static. By 2025, several key judgments from the Court of Justice of the European Union (CJEU) and recent guidance from regulatory bodies like the European Data Protection Board (EDPB), the EU Agency for Cybersecurity (ENISA), and national Data Protection Authorities (DPAs) will significantly shape compliance obligations, particularly for AI agent-based products.

**Key CJEU Judgments Impacting AI and Data Protection:**

Recent CJEU jurisprudence has provided critical clarifications on the application of GDPR principles in technologically advanced contexts, with direct implications for AI systems:

- **Transparency in Automated Decision-Making (ADM):** A landmark development is the CJEU's stance on transparency in ADM, exemplified by cases such as _Case C-203/22 (Dun and Bradstreet Austria)_. The Court has ruled that data controllers must provide data subjects with "meaningful information" about the logic involved in automated decisions. This goes beyond merely disclosing complex mathematical formulas or algorithms.<sup>7</sup> Instead, controllers must explain "the procedure and principles actually applied" and, where relevant, how variations in input data could have altered the decision outcome.<sup>7</sup> This ruling imposes a significant obligation on developers and deployers of AI agents that make or support decisions having legal or similarly significant effects on individuals, demanding a higher degree of explainability. The consistent emphasis by the CJEU on "meaningful transparency" is creating a strong legal expectation for "explainable AI" (XAI). This requirement pushes beyond the literal text of the GDPR and compels technological advancements, requiring AI agent developers to invest in XAI techniques and be prepared to articulate how their agents arrive at decisions. The AI Act's similar explainability requirements further solidify this trend.<sup>7</sup>
- **Balancing Transparency with Trade Secrets:** The CJEU has clarified that while trade secrets are a legitimate interest, they cannot serve as a blanket justification for withholding essential transparency information regarding ADM.<sup>7</sup> In situations where a controller believes disclosure could compromise trade secrets, they may be required to submit the relevant information to the competent supervisory authority or court. These bodies will then perform a balancing act to determine the extent of the data subject's access rights under Article 15 GDPR, weighing the data subject's right to information against the controller's commercial interests.
- **Definition of Data Controller:** In cases like _C-638/23 (Amt der Tiroler Landesregierung)_, the CJEU has affirmed that public bodies can be considered data controllers under Article 4(7) GDPR, even if they lack a distinct legal personality under national law.<sup>20</sup> The emphasis is placed on the actual exercise of control over data processing operations and the associated responsibility and accountability. This has implications for AI systems deployed by or in conjunction with public sector entities.
- **Calculation of GDPR Fines:** The ruling in _C-383/23 (ILVA A/S)_ established that the total worldwide turnover of the parent company should be considered when calculating GDPR fines for infringements by a subsidiary.<sup>20</sup> This decision aligns with EU competition law principles and underscores the concept of a single economic unit for penalty calculations, significantly increasing the potential financial repercussions for non-compliance related to AI ventures within larger corporate groups.
- **Pseudonymised Data as Personal Data:** The Advocate General's Opinion in _C-413/23 (EDPS v SRB)_, issued on February 5, 2025, suggested that pseudonymised data shared with third parties should not automatically be considered personal data if the risks of re-identification by the recipient are "non-existent or insignificant".<sup>20</sup> While an AG Opinion is not binding on the Court, it provides an influential perspective. If upheld, this could offer potential, albeit high-threshold, avenues for sharing data for AI model training or other purposes. However, it would necessitate a rigorous, case-by-case risk assessment by the data controller to demonstrate that the recipient lacks the means reasonably likely to be used for re-identification.
- **EDPB Powers in Cross-Border Enforcement:** The CJEU's decision in the joined cases _T-70/23, T-84/23, T111/23 (Data Protection Commission v European Data Protection Board)_ upheld the EDPB's authority to instruct national DPAs to broaden the scope of their investigations in cross-border GDPR enforcement cases.<sup>20</sup> This ruling reinforces the EDPB's supervisory role and its power to ensure consistent and harmonized GDPR enforcement across all EU Member States. For companies developing or deploying AI agents across multiple EU jurisdictions, this means they face potentially more stringent and coordinated scrutiny from data protection authorities.

**Analysis of Recent Regulatory Guidance on AI (Focus on 2024-2025 publications):**

- **EDPB Opinion 28/2024 on AI Models and Data Protection (December 2024):** This crucial opinion provides detailed guidance on several aspects of AI and GDPR:
  - **Anonymity of AI Models:** The EDPB maintains a high bar for claims that AI models trained on personal data can be considered anonymous. Anonymity must be assessed on a case-by-case basis, and the controller must demonstrate that the likelihood of re-identification, using all means reasonably likely to be used, is negligible.<sup>21</sup> This requires robust testing against various re-identification attacks (e.g., attribute inference, membership inference, model inversion, reconstruction attacks).<sup>21</sup>
  - **Legitimate Interests (LI) as a Lawful Basis:** The EDPB confirms that LI can be an appropriate lawful basis for processing personal data in the development and deployment of AI models. However, this is subject to stringent adherence to the three-part LIA test: identifying a clear and lawful interest, demonstrating the necessity of the processing for that interest (including an assessment of whether less intrusive means are available), and conducting a careful balancing test against the rights and freedoms of data subjects.<sup>21</sup> Comprehensive documentation (LIAs, DPIAs) is critical. The EDPB's strict stance signals that relying on these avenues to bypass certain GDPR obligations will be difficult and heavily scrutinized, placing a greater onus on robust data protection by design, data minimisation, and exploring consent where feasible.
  - **Developer vs. Deployer Responsibility:** The Opinion addresses the responsibilities of AI model developers versus deployers concerning training data that may have been unlawfully processed. Deployers have an obligation to conduct appropriate due diligence to ascertain the lawfulness of the data used to train the models they deploy.<sup>21</sup>
- **ENISA (EU Agency for Cybersecurity) Guidance:** ENISA's reports and frameworks continue to highlight the evolving cybersecurity threat landscape, with specific attention to AI-related risks. This includes the use of AI for generating fake content, deepfakes, and new methods for spreading misinformation, as well as the exploitation of vulnerabilities in AI systems themselves.<sup>33</sup> ENISA provides frameworks for good cybersecurity practices for AI, covering the entire AI lifecycle and emphasizing the need for dynamic, measurable risk assessments of both technical and social threats (e.g., bias, lack of fairness) and continuous risk management.<sup>34</sup>
- **National DPA Guidance:** National DPAs are also issuing AI-specific guidance. For instance, the French DPA (CNIL) published recommendations in February 2025 focusing on practical aspects of AI and GDPR compliance, such as informing data subjects and facilitating the exercise of their rights.<sup>35</sup> These recommendations address challenges like defining purposes for general-purpose AI, data minimisation in AI contexts, and managing data subject rights when data is embedded in AI models (e.g., by suggesting techniques like output filtering or anonymisation of training data).<sup>36</sup> Joint declarations by multiple DPAs (e.g., the February 2025 declaration by authorities from Australia, Korea, Ireland, France, and the UK) advocate for common principles such as data protection by design, robust data governance, and proactive risk management in AI.<sup>40</sup>

The increasing convergence of guidance from the EDPB, national DPAs, and the requirements stemming from the EU AI Act indicates a clear trajectory towards a more harmonized, albeit stringent, regulatory framework for AI in the EU. However, subtle nuances in national DPA interpretations and enforcement priorities <sup>37</sup> mean that organizations must maintain a vigilant awareness of developments at both the EU and Member State levels to ensure comprehensive compliance.

The following table summarizes key 2025 CJEU rulings and their impact:

\\begin{table}\[h!\]

\\centering

\\caption{Key 2025 CJEU Rulings & Their Impact on AI/GDPR Compliance}

\\label{tab:cjeu_rulings_ai}

\\resizebox{\\textwidth}{!}{%

\\begin{tabular}{|p{2.2cm}|p{1.5cm}|p{4cm}|p{4.5cm}|p{3.8cm}|p{1.5cm}|}

\\hline

\\textbf{CJEU Case Ref & Name} & \\textbf{Date of Ruling/ Opinion} & \\textbf{Key Finding(s) Relevant to AI/Data Protection} & \\textbf{Implications for AI Agent-Based Products} & \\textbf{Recommended Actions for Organizations} & \\textbf{Relevant Sources} \\

\\hline

C-203/22 (Dun and Bradstreet Austria / SCHUFA Holding) & Feb 27, 2025 (CJEU Decision) & Controllers must provide "meaningful information" on ADM logic, not just algorithms. Trade secrets not a blanket justification for opacity.7 & Increased demand for XAI. AI agents making significant decisions must be explainable. Need to balance transparency with IP. & Invest in XAI. Prepare clear explanations of ADM. Establish procedures for handling access requests involving potential trade secrets, possibly involving DPA review. & 7 \\

\\hline

C-638/23 (Amt der Tiroler Landesregierung) & Early 2025 (CJEU Ruling) & Public bodies, even without distinct legal personality, can be data controllers; emphasizes responsibility and accountability.20 & Clarifies controller status for public sector AI deployments. Public-private AI partnerships need clear responsibility allocation. & Review controller/processor status for public sector AI projects. Ensure clear accountability structures. & 20 \\

\\hline

C-383/23 (ILVA A/S) & Early 2025 (CJEU Ruling) & Total turnover of parent company considered for fining subsidiaries for GDPR violations.20 & Increased financial risk for non-compliant AI agents within larger corporate groups. Reinforces need for group-wide GDPR compliance programs. & Ensure GDPR compliance for AI is addressed at group level. Assess potential fines based on total group turnover. & 20 \\

\\hline

C-413/23 (EDPS v SRB) & Feb 5, 2025 (AG Opinion) & Pseudonymised data shared with third parties may not be personal data if re-identification risk for recipient is "non-existent or insignificant".20 & Potential (high-threshold) for using/sharing pseudonymised data for AI training if re-identification robustly prevented. Requires rigorous risk assessment. & Conduct thorough re-identification risk assessments for any pseudonymised data sharing for AI. Document safeguards. Be cautious, as AG opinion is not binding yet. & 20 \\

\\hline

Joined cases T-70/23, T-84/23, T111/23 (DPC v EDPB) & Early 2025 (CJEU Ruling) & EDPB has authority to order broader investigations in cross-border cases, ensuring consistent GDPR enforcement.20 & AI companies operating cross-border face harmonized and potentially more stringent scrutiny. Increased likelihood of EU-wide investigations. & Prepare for consistent and potentially broader DPA scrutiny across EU. Ensure AI compliance programs are robust EU-wide. & 20 \\

\\hline

\\end{tabular}%

}

\\end{table}

## **VI. AI Agent-Based Products: Amplified GDPR Challenges and Bespoke Best Practices**

AI agent-based products, characterized by their autonomy, learning capabilities, and capacity to process vast amounts of data, present amplified and often novel challenges to GDPR compliance. Addressing these requires bespoke best practices tailored to their unique operational characteristics.

**A. Transparency and Explainability in Automated Decision-Making (ADM):**

- **Challenge:** A significant hurdle with AI agents is their potential "black box" nature, making it difficult to fully understand and explain their internal decision-making processes.<sup>5</sup> This opacity is compounded by their dynamic learning capabilities, which can alter decision logic over time, making static explanations insufficient.<sup>4</sup>
- **GDPR Link:** Articles 13, 14, and 15 (right of access, which includes the right to "meaningful information about the logic involved" in ADM), and Article 22 (rights related to ADM which produces legal or similarly significant effects).
- **Best Practices:**
  - Implement Explainable AI (XAI) techniques to furnish "clear and meaningful explanations" regarding the AI agent's role in a decision-making procedure and the primary elements influencing the decision.<sup>7</sup> As per recent CJEU rulings, this must include an explanation of "the procedure and principles actually applied" and, where applicable, how variations in the input data could have led to a different outcome.<sup>7</sup>
  - Adopt a layered approach to providing information: offer concise, easily digestible summaries for general users, with clear pathways to access more detailed and technical explanations if desired.<sup>13</sup>
  - Thoroughly document the decision-making processes embedded within the AI agent and maintain records that can be used to explain specific decisions to data subjects and supervisory authorities.<sup>7</sup>
  - Acknowledge the tension between transparency and the protection of trade secrets. While trade secrets are legitimate, they cannot serve as an absolute barrier to a data subject's right to explanation. Organizations should be prepared for scenarios where they might need to submit information about their algorithms or decision-making logic to competent authorities for a balancing of interests.<sup>7</sup>
  - Ensure that the explanations provided are sufficient to enable data subjects to understand the basis of a decision and, consequently, to effectively challenge it if they believe it to be incorrect or unfair.<sup>20</sup>
  - For AI agents that interact directly with users (e.g., chatbots, virtual assistants), it is crucial to clearly disclose when the user is interacting with an AI system rather than a human operator.<sup>41</sup>
- The legal standard for "explainability" is evolving from a purely technical consideration to a practical necessity for user empowerment and regulatory oversight. The CJEU's emphasis on enabling data subjects to _challenge_ decisions <sup>20</sup> implies that explanations must be actionable and insightful, not merely informational. This has profound implications for AI system design, necessitating investment in robust XAI capabilities and potentially interactive explanatory interfaces. Furthermore, the dynamic learning nature of AI agents <sup>4</sup> means that transparency and explainability cannot be static, one-time provisions. Systems may need to be designed to provide evolving explanations as the agent learns and adapts its decision-making logic, or at least ensure that core explainable principles remain stable and transparent despite ongoing learning.

**B. Purpose Limitation and Data Minimisation in Dynamic AI Systems:**

- **Challenge:** The inherent ability of AI agents to learn, adapt, and potentially discover new applications for the data they process <sup>4</sup> can directly conflict with the GDPR principle of collecting data only for "specified, explicit and legitimate purposes".<sup>1</sup> Similarly, the principle of processing only data that is "adequate, relevant and limited to what is necessary" <sup>17</sup> is challenged by agents that may accumulate vast quantities of data through continuous interaction and learning.<sup>4</sup>
- **GDPR Link:** Article 5(1)(b) (purpose limitation), Article 5(1)(c) (data minimisation).
- **Best Practices:**
  - Clearly define and meticulously document the initial purposes for which the AI agent will process personal data. Be highly specific about the tasks the agent is designed to perform and the objectives it aims to achieve.<sup>1</sup>
  - Implement technical and organizational measures to control and define the operational parameters of the underlying AI models. This helps prevent uncontrolled "purpose creep," where the agent begins using data for purposes beyond those initially defined.<sup>4</sup>
  - Establish processes for regularly reviewing whether the personal data processed by the agent remains adequate, relevant, and limited to the defined purposes. Implement data pruning, summarization, or "forgetting" mechanisms where data is no longer necessary or relevant.<sup>17</sup>
  - If new purposes for data processing emerge through the agent's learning capabilities that are incompatible with the original purposes, a new lawful basis must be identified, or fresh, specific consent must be obtained from data subjects.<sup>4</sup>
  - For AI agents, particularly those interacting with users, focus on collecting only the data essential for their immediate functionality and stated tasks.<sup>13</sup> For example, a chatbot designed for product inquiries should not collect location data unless that information is directly relevant to fulfilling the user's query (e.g., checking local stock).<sup>13</sup>
- True adherence to purpose limitation for advanced, learning AI agents may necessitate a shift from purely technical data management to robust ethical governance frameworks. These frameworks must continuously evaluate the agent's evolving capabilities and data uses against the initial purposes and broader societal expectations. The autonomous learning capacity of AI agents <sup>4</sup> means their operational scope can expand beyond initial programming. Technical controls alone <sup>4</sup> might be insufficient if the agent's core learning algorithms lead it to discover novel, unintended data correlations and uses. This implies a need for human-in-the-loop governance to reassess purpose compatibility on an ongoing basis.
- Data minimisation in the context of AI agents extends beyond just the input data to also encompass the "memory" or interaction logs the agent retains.<sup>4</sup> Striking a delicate balance between retaining sufficient data for effective learning and personalization, and minimizing data to comply with GDPR, is a key design and operational challenge. Techniques such as data aggregation, abstraction, or implementing time-limited storage for detailed interaction logs become crucial.

**C. Lawful Basis for Data Processing Across the AI Lifecycle:**

- **Challenge:** Establishing a valid lawful basis for the often vast quantities of personal data used to train AI models—especially if this data is web-scraped or obtained from third-party sources—is a significant challenge.<sup>5</sup> Similarly, the ongoing processing of personal data by the deployed agent requires a clear lawful basis. Obtaining valid, granular consent for all facets of AI processing can be complex and may lead to "consent fatigue".<sup>13</sup>
- **GDPR Link:** Article 6 (lawful bases for processing), Article 7 (conditions for consent), Article 9 (processing of special categories of personal data).
- **Best Practices:**
  - **Consent:** For direct interactions with AI agents, obtain explicit, informed consent from users. This consent process must clearly explain what personal data will be collected, how it will be used (including for the agent's learning and improvement), and inform users of their data subject rights.<sup>3</sup> Utilize clear cookie consent banners and comprehensive, easily understandable privacy policies.<sup>2</sup>
  - **Legitimate Interests (LI):** If relying on legitimate interests as the lawful basis for training AI models or for their deployment, a thorough and documented Legitimate Interests Assessment (LIA) is mandatory.<sup>21</sup> This LIA must:
    - Clearly define the specific, lawful interest being pursued (e.g., developing an AI agent for fraud detection, improving customer service through a conversational AI).<sup>21</sup>
    - Demonstrate the necessity of processing personal data to achieve that interest. This includes assessing whether the purpose could be achieved using less intrusive means, such as anonymised or synthetic data, or without processing personal data at all.<sup>21</sup>
    - Conduct a careful balancing test, weighing the controller's legitimate interests against the fundamental rights and freedoms of the data subjects. This balancing test must consider the nature of the personal data, the context of its collection and processing, the reasonable expectations of data subjects, and the potential impact of the processing on them. Implement mitigating measures to help tip the balance in favor of the processing, such as pseudonymisation, respecting robots.txt or ai.txt protocols for web-scraped data, and implementing output filters to prevent the disclosure of sensitive information.<sup>21</sup>
  - **Data Provenance:** When using third-party data sources for training AI agents, conduct due diligence to verify the lawfulness of the data collection and ensure that its use for AI training is permissible.<sup>21</sup>
  - **Special Category Data:** Exercise extreme caution when processing special categories of personal data (as defined in Article 9 GDPR, e.g., health data, biometric data for unique identification, racial or ethnic origin). If an AI agent processes such data (either directly provided or inferred), ensure that a valid condition under Article 9(2) applies, in addition to a lawful basis under Article 6. The EU AI Act also contains specific rules and prohibitions regarding certain uses of biometric categorization systems.<sup>8</sup>
- The EDPB's detailed scrutiny of 'legitimate interests' as a lawful basis for AI processing <sup>21</sup> suggests that while this basis remains available, it will require exceptionally robust justification and comprehensive documentation. This is particularly true for large-scale training data acquisition (e.g., via web scraping) or for AI agent deployments that have a high potential impact on individuals. The EDPB's emphasis on the "necessity" prong (could the purpose be achieved with less or no personal data?) and the detailed "balancing test" (considering data subject expectations and potential impact) <sup>21</sup> makes legitimate interests a challenging basis for AI, which often thrives on vast datasets and can have unforeseen consequences. This may drive organizations towards more robust anonymisation or pseudonymisation techniques from the outset, or towards seeking more specific and granular forms of consent for AI training and operational data processing.
- For AI agents that interact extensively with users, "consent fatigue" is a tangible risk if users are repeatedly prompted for permissions as the agent's functionalities or data requirements evolve. This necessitates the design of innovative consent management mechanisms that are user-friendly, offer granular choices, and provide users with ongoing control over their data preferences, such as through easily accessible dashboards or contextual consent requests.<sup>13</sup>

**D. Upholding Data Subject Rights (DSRs) with AI Agents:**

- **Challenge:** Effectively facilitating data subject rights—such as access, rectification, erasure, portability, objection, and restriction of processing—can be highly complex when personal data is deeply embedded within trained AI models or when the agent's processing is continuous and autonomous.<sup>1</sup> For instance, truly "erasing" a specific individual's data from a complex, trained neural network can be technically challenging or even impossible without complete retraining of the model, which is often a costly and time-consuming process.<sup>44</sup>
- **GDPR Link:** Articles 12-22.
- **Best Practices:**
  - Embed DSR facilitation into the design of AI agents and their underlying systems from the very outset (Data Protection by Design).<sup>13</sup>
  - Provide clear, straightforward, and easily accessible mechanisms for users to exercise their rights. This could be through the AI agent's interface itself (e.g., a chatbot command), dedicated self-service portals, or clearly signposted contact points.<sup>2</sup>
  - **Right of Access (Article 15):** Design systems to enable users to obtain a copy of their personal data processed by the AI agent. This must include meaningful information about any automated decision-making logic involved, as discussed in section VI.A.
  - **Right to Rectification (Article 16):** Implement processes to correct inaccurate personal data. This applies not only to input datasets used for training or operation but also potentially to how the AI agent represents or utilizes that data.<sup>37</sup> If inaccuracies in training data have influenced the model, this may involve updating the training data and considering model retraining or fine-tuning if feasible. Alternatively, filtering outputs to prevent the propagation of decisions based on known inaccuracies can be a mitigating measure.
  - **Right to Erasure (Article 17, 'Right to be Forgotten'):** Develop comprehensive strategies for data removal. If direct and complete erasure of specific data points from trained AI models is technically infeasible, consider and document alternative measures. These may include anonymizing the data within the model, de-linking it from the individual, or implementing robust output filters to prevent the data from being used or displayed in future interactions.<sup>24</sup> The CNIL, for example, has suggested output filtering as a practical measure to address erasure requests without necessitating full model retraining.<sup>37</sup>
  - **Right to Data Portability (Article 20):** Where processing is based on consent or contract and is carried out by automated means, provide the data subject with their personal data in a structured, commonly used, and machine-readable format (e.g., CSV, JSON).<sup>1</sup> This typically includes data provided by the user and may extend to observed data like learned preferences if it falls within the scope of Article 20.
  - **Right to Object (Article 21):** Provide mechanisms for users to object to the processing of their personal data, particularly when processing is based on legitimate interests or for direct marketing purposes (which includes profiling by the AI agent).<sup>24</sup> Upon objection, processing must cease unless the controller demonstrates compelling legitimate grounds that override the data subject's interests, rights, and freedoms, or for the establishment, exercise, or defense of legal claims. The EDPB has suggested that in some AI contexts, controllers might consider granting unconditional rights to object or erasure.<sup>43</sup>
  - **Rights Related to Automated Individual Decision-Making, Including Profiling (Article 22):** For AI agents involved in making solely automated decisions that produce legal effects concerning data subjects or similarly significantly affect them, implement safeguards. These include the right for the data subject to obtain human intervention, to express their point of view, and to contest the decision.<sup>4</sup>
- The significant technical difficulty of implementing certain DSRs, such as the right to erasure, within already trained AI models <sup>44</sup> serves as a strong driver for investing in Privacy Enhancing Technologies (PETs) and establishing robust data governance for training data _before_ model development commences. If personal data is never directly incorporated into the model in an identifiable form, or if it is effectively anonymised (though achieving true anonymisation is a high bar according to the EDPB <sup>21</sup>), then subsequent requests for erasure become less problematic for the integrity of the model itself. This approach effectively shifts a significant part of the DSR compliance burden upstream to the data preparation and selection stages.
- Facilitating DSRs for AI agents in a user-friendly manner requires a combination of sophisticated technical solutions (e.g., APIs for data access and portability, model output filtering mechanisms) and clear, intuitive user interfaces (e.g., chatbots capable of understanding and processing DSR requests, or well-designed self-service portals <sup>13</sup>). This represents an important intersection where user experience (UX) design directly supports legal compliance. Article 12 GDPR mandates that information and modalities for exercising DSRs be provided in a "concise, transparent, intelligible and easily accessible form, using clear and plain language." For AI agents, the interactive interface is often the primary point of contact with the user; therefore, building DSR functionalities directly into the agent's conversational capabilities or clearly linking to accessible portals is key for fulfilling this requirement.

**E. Ensuring Accuracy and Addressing Bias in AI Outputs:**

- **Challenge:** AI agents, particularly those based on generative models, can "hallucinate"—producing outputs that are factually incorrect, misleading, or nonsensical, despite being presented confidently.<sup>5</sup> Furthermore, AI models can inherit and amplify biases present in their training data, leading to inaccurate, unfair, or discriminatory outcomes against certain individuals or groups.<sup>12</sup> Compounding errors can also occur in AI agents that perform multi-step tasks, where an initial small error can lead to significantly flawed final outputs.<sup>5</sup>
- **GDPR Link:** Article 5(1)(d) (accuracy principle, requiring data to be accurate and, where necessary, kept up to date, and for inaccurate data to be rectified or erased), and the fairness principle (embedded in Article 5(1)(a)), which implies avoiding discriminatory processing.
- **Best Practices:**
  - Prioritize the use of high-quality, representative, and, where feasible, bias-audited training data. The quality of training data is a critical determinant of model accuracy and fairness.<sup>12</sup>
  - Implement robust mechanisms throughout the AI lifecycle to detect, measure, and mitigate biases in algorithms and their outputs. This may involve pre-processing training data, in-processing algorithmic adjustments, or post-processing output corrections.<sup>12</sup>
  - Regularly validate and monitor the accuracy of AI agent outputs, especially for decisions or information that could have a significant impact on individuals.<sup>25</sup> Establish performance metrics for accuracy and fairness.
  - Provide users with clear and transparent information about the potential limitations in the AI agent's accuracy and the possibility of errors or biases in its outputs.
  - Consider implementing human oversight or review mechanisms for critical decisions made or significantly supported by AI agents, particularly in high-risk applications.<sup>4</sup>
  - Document all efforts undertaken to ensure accuracy and fairness as part of the overall accountability obligations under GDPR. This includes records of data quality assessments, bias audits, and validation processes.
- The GDPR's accuracy principle (Article 5(1)(d)) applies not only to the input data processed by an AI agent but also extends to the _outputs_ generated by the agent, especially if these outputs are presented as factual information or form the basis of decisions affecting individuals. This implies that organizations deploying AI agents bear a responsibility for the "truthfulness" and reliability of their agents' outputs to a certain extent. If an AI agent provides inaccurate information that is subsequently relied upon to the detriment of a data subject, it constitutes a failure of the accuracy principle by the data controller. The documented issues of "hallucinations" and "compounding errors" <sup>5</sup> necessitate the implementation of output validation mechanisms or, at a minimum, clear disclaimers regarding the reliability of the agent's outputs.
- Addressing AI bias is not merely an ethical consideration but a core GDPR compliance issue, intrinsically linked to the principles of fairness and non-discrimination. Failure to proactively identify and mitigate biases within AI systems can lead to processing that is inherently unfair or results in discriminatory effects. Such discrimination could potentially involve the processing of special categories of personal data if biases are related to protected characteristics (e.g., race, gender, religion). The observation that AI models can reinforce existing societal biases <sup>12</sup> underscores the critical need for proactive bias detection and mitigation strategies throughout the entire AI lifecycle, from data collection and preparation to model training, validation, and deployment, as advocated in responsible AI literature.<sup>12</sup>

**F. Security and Confidentiality for AI Agents:**

- **Challenge:** AI agents introduce a new landscape of security vulnerabilities. These include sophisticated attacks such as prompt injection (manipulating agent instructions via user inputs), model inversion (extracting sensitive training data from the model), data poisoning (corrupting training data to degrade performance or introduce backdoors), membership inference attacks (determining if an individual's data was part of the training set), and the exploitation of their inherent autonomy and potentially extensive access privileges within systems.<sup>5</sup>
- **GDPR Link:** Article 5(1)(f) (integrity and confidentiality), Article 32 (security of processing).
- **Best Practices:**
  - Implement robust Identity and Access Management (IAM) specifically tailored for AI agents. This includes assigning distinct, auditable identities to each agent, employing context-based entitlements based on the principles of Just-Enough-Access (JEA) and Just-in-Time (JIT) access, utilizing ephemeral credentials instead of static API keys or service accounts, and continuously verifying AI agent access using risk-based authentication mechanisms.<sup>6</sup> It is crucial to "down scope agent privileges" to the minimum necessary for their tasks.<sup>6</sup>
  - Protect training data from unauthorized access and poisoning attacks. Secure AI models themselves from theft, unauthorized copying, or reverse engineering.
  - Implement technical defenses against known adversarial attacks. This can include input sanitization and validation to counter prompt injection, techniques to enhance model robustness against perturbations, and anomaly detection for unusual query patterns.<sup>5</sup>
  - Secure all Application Programming Interfaces (APIs) used by or exposed by AI agents, ensuring proper authentication, authorization, and encryption.<sup>23</sup>
  - Encrypt sensitive personal data processed by AI agents, both when it is in transit over networks and when it is at rest in storage systems.<sup>2</sup>
  - Conduct regular security audits, vulnerability assessments, and penetration testing specifically designed to target AI systems and their unique vulnerabilities.<sup>13</sup>
  - Continuously monitor AI agent activity for anomalous behavior or indicators of compromise.<sup>19</sup>
  - Ensure human oversight is available for security-critical actions initiated or performed by AI agents.<sup>4</sup>
- The GDPR principle of "integrity and confidentiality" (Article 5(1)(f)), when applied to AI agents, extends to protecting the AI model itself if it has "absorbed" personal data from its training set <sup>21</sup> or if its inversion or reconstruction could reveal sensitive training data. This expands the scope of what needs to be secured beyond just input and output data; the model parameters and architecture can also be considered confidential information requiring protection under Article 32.
- The autonomous nature of AI agents <sup>5</sup> necessitates a "zero trust" security posture. Granting broad, standing privileges to an AI agent creates a significant security risk, as a compromised agent could act independently and rapidly to exfiltrate data, disrupt operations, or cause other harm. The advice to avoid giving an agent "keys to your entire building" and to establish "appropriate boundaries" <sup>6</sup>, along with advocacy for JIT/JEA provisioning and continuous verification <sup>19</sup>, reflects a critical shift from traditional perimeter-based security to an identity-centric security model, even for non-human entities like AI agents.

The following table provides a consolidated view of AI agent challenges and corresponding GDPR mitigation best practices:

\\begin{table}\[h!\]

\\centering

\\caption{AI Agent Challenges & GDPR Mitigation Best Practices}

\\label{tab:ai_challenges_mitigation}

\\resizebox{\\textwidth}{!}{%

\\begin{tabular}{|p{3cm}|p{4cm}|p{2.5cm}|p{5cm}|p{3.5cm}|p{1.5cm}|}

\\hline

\\textbf{Challenge Area} & \\textbf{Specific Challenge for AI Agents} & \\textbf{Relevant GDPR Articles/ Principles} & \\textbf{Best Practice/Mitigation Strategy} & \\textbf{Example Implementation for AI Agent} & \\textbf{Key Sources} \\

\\hline

Transparency in ADM & "Black box" nature, dynamic logic 4 & Art. 13-15, 22 & Implement XAI; layered info; document processes; balance with trade secrets; enable challenges. & Chatbot explains key factors in a loan pre-assessment; user can request detailed logic or human review. & 4 \\

\\hline

Purpose Limitation & Learning leads to new, unintended data uses ("purpose creep") 4 & Art. 5(1)(b) & Define initial purposes clearly; control model parameters; regular review; new lawful basis/consent for incompatible new purposes. & AI research agent's scope is initially limited to medical journals; if it starts analyzing social media for health trends, reassess purpose and basis. & 1 \\

\\hline

Data Minimisation & Agents accumulate vast interaction data/memory 4 & Art. 5(1)(c) & Design for minimal data collection; ongoing evaluation; data pruning/ "forgetting" mechanisms. & Personal assistant AI only stores meeting details for a set period, then archives or anonymizes. & 4 \\

\\hline

Lawful Basis & Justifying data for training (esp. web-scraped) and ongoing operation 5 & Art. 6, 7, 9 & Explicit consent for interactions; robust LIA for training/deployment if using LI; verify third-party data provenance. & E-commerce agent gets explicit consent for personalization; LIA conducted for using browsing history for model improvement. & 3 \\

\\hline

Data Subject Rights (DSRs) & Difficulty implementing rights (e.g., erasure from trained models) 44 & Art. 12-22 & DPbDD for DSRs; accessible mechanisms (agent interface, portals); alternatives for erasure (anonymisation, output filtering). & User tells customer service AI "delete my chat history"; AI confirms and initiates process or filters future outputs. & 13 \\

\\hline

Accuracy/Bias & Hallucinations, inherited bias, compounding errors 5 & Art. 5(1)(d), Art. 5(1)(a) (fairness) & Quality training data; bias detection/mitigation; output validation; transparency about limitations; human oversight for critical decisions. & AI hiring tool is regularly audited for demographic bias; recruiters review AI-shortlisted candidates. & 5 \\

\\hline

Security & Novel AI attacks (prompt injection, model inversion), exploitation of autonomy 5 & Art. 5(1)(f), Art. 32 & Robust IAM for agents (JEA/JIT); defenses against adversarial attacks; secure APIs; encryption; AI-specific security audits. & Financial advice AI agent has restricted access to specific APIs, uses ephemeral credentials, and its inputs are sanitized. & 5 \\

\\hline

\\end{tabular}%

}

\\end{table}

## **VII. Data Protection by Design and by Default (DPbDD) in AI Agent Development and Deployment**

Article 25 of the GDPR mandates Data Protection by Design and by Default (DPbDD), requiring controllers to implement appropriate technical and organizational measures to effectively integrate data protection principles into their processing activities from the very inception of system design and to ensure that, by default, only necessary personal data is processed.<sup>17</sup> For AI agent-based products, with their inherent complexity, data intensity, and potential for high-risk processing, DPbDD is not merely a compliance obligation but a foundational strategy for responsible development and deployment.<sup>4</sup> The factors to be considered when implementing DPbDD include the state of the art, the cost of implementation, and the nature, scope, context, and purposes of processing, as well as the risks of varying likelihood and severity for the rights and freedoms of natural persons posed by the processing.<sup>49</sup>

**Practical Implementation Strategies for AI Agents:**

- **Default Privacy Settings:** AI agents should be configured with the most privacy-protective settings enabled by default. This means that functionalities involving significant personal data collection or sharing should require active user opt-in rather than opt-out.<sup>49</sup> For example, an AI agent's capability to learn from user interactions to personalize future responses should be off by default, requiring explicit user consent to activate.
- **Data Minimisation by Design:** From the earliest design stages, AI agents must be engineered to collect and process only the personal data that is strictly necessary for their specific, clearly defined tasks and functionalities.<sup>14</sup> This involves carefully considering what data attributes are truly required for each feature and avoiding the collection of superfluous information.
- **Pseudonymisation and Anonymisation by Design:** Implement pseudonymisation techniques (such as tokenization or encryption with segregated keys) or, where feasible and the high threshold can be met, anonymisation techniques, as early as possible in the data lifecycle.<sup>2</sup> This is particularly critical for datasets used to train AI models. However, achieving true anonymisation that withstands scrutiny, especially by the EDPB, is challenging for complex AI models.<sup>21</sup>
- **Security by Design:** Integrate robust security measures into the architecture of the AI agent and its supporting infrastructure from the outset, rather than treating security as an add-on. This includes considerations for data encryption, access controls, secure coding practices, and defenses against AI-specific attacks (as detailed in Section VI.F).
- **Transparency by Design:** Design the AI agent's interfaces and communication protocols to be inherently transparent. Users should be clearly and proactively informed about the agent's data processing practices, the purposes of processing, and the logic behind its automated decisions or recommendations (as detailed in Section VI.A).
- **DSR Facilitation by Design:** Build functionalities and processes into the AI agent system that make it straightforward for data subjects to exercise their GDPR rights (e.g., access, rectification, erasure). This might involve user-friendly dashboards, API endpoints for data export, or mechanisms within the agent's interface to initiate DSR requests (as detailed in Section VI.D).

**The Role of Privacy Enhancing Technologies (PETs):**

Privacy Enhancing Technologies (PETs) are a suite of tools and techniques that can significantly aid in implementing DPbDD for AI agents by enabling data analysis, model training, and system operation with reduced privacy risks.<sup>51</sup> Examples of PETs relevant to AI include:

- **Homomorphic Encryption:** Allows computations to be performed directly on encrypted data without needing to decrypt it first, thus protecting data confidentiality even during processing.<sup>51</sup>
- **Federated Learning:** Enables AI models to be trained on decentralized datasets residing on different devices or servers. Instead of pooling raw data, local model updates are aggregated, minimizing direct exposure of sensitive data.<sup>51</sup>
- **Differential Privacy:** Involves adding carefully calibrated statistical noise to datasets or query responses to protect individual privacy while still allowing for useful aggregate analysis.<sup>51</sup>
- **Confidential Computing (Trusted Execution Environments - TEEs):** Provides hardware-based isolation to protect data and code while in use, ensuring that even cloud providers or system administrators cannot access sensitive information being processed within the TEE.<sup>51</sup>
- **Synthetic Data Generation:** Creating artificial datasets that mimic the statistical properties of real data but do not contain actual personal information, which can then be used for model training or testing.<sup>51</sup>

While PETs offer powerful capabilities, they are not a universal solution or a "panacea" for all privacy challenges.<sup>52</sup> They often involve trade-offs (e.g., between privacy protection and data utility or computational overhead) and should be considered as part of a comprehensive, multi-layered data protection strategy.

For AI agents, DPbDD is more than a legal obligation; it is a strategic imperative. Given the high potential risks and inherent complexities associated with AI, attempting to retrofit privacy safeguards late in the development cycle is typically far more costly, less effective, and can lead to significant operational disruptions or even necessitate complete system redesigns. The unique characteristics of AI agents—such as dynamic learning <sup>4</sup>, high data intensity <sup>5</sup>, and potential opacity <sup>5</sup>—mean that privacy considerations must deeply influence fundamental architectural choices, including model selection, training data strategies, and the definition of operational boundaries, from the conceptual stage onwards.

The selection and implementation of PETs <sup>51</sup> must be carefully tailored to the specific use case, risk profile, and operational context of the AI agent. There is no one-size-fits-all PET solution. The effectiveness of any chosen PET in achieving legal requirements, such as true anonymisation or adequate security, needs critical assessment and justification, typically documented within the DPIA and the broader DPbDD framework. For instance, while differential privacy can offer strong mathematical guarantees of privacy, it inherently introduces a trade-off between the level of privacy protection and the accuracy or utility of the data. Similarly, federated learning, while avoiding data centralisation, presents its own set of security and governance challenges that must be addressed.

## **VIII. The Interplay of GDPR and the EU AI Act for AI Agent Products**

The regulatory environment for AI agent-based products in the EU is characterized by the co-existence of the GDPR and the EU AI Act. Understanding their interplay is crucial for comprehensive compliance. The GDPR applies whenever personal data is processed by any system, including AI agents.<sup>7</sup> The AI Act, on the other hand, establishes a horizontal regulatory framework for AI systems based on their potential risk to health, safety, and fundamental rights, irrespective of whether personal data is processed. However, it includes specific provisions and considerations for AI systems that do process personal data.<sup>10</sup>

**Understanding Overlapping and Distinct Obligations:**

The AI Act is designed to be _lex specialis_ in relation to AI-specific risks, meaning its provisions take precedence for those specific aspects. However, it explicitly states that it does not diminish the protections afforded by the GDPR or other Union laws on data protection.<sup>8</sup> Data subjects retain all their rights under the GDPR when their personal data is processed by AI systems.<sup>10</sup> The AI Act's requirements are often complementary to GDPR obligations, sometimes reinforcing them or providing more specific rules for AI contexts.

**Implications of AI Act Risk Categorisations for GDPR Compliance:**

The AI Act's risk-based approach has direct implications for how GDPR compliance is approached for AI agents:

- **Prohibited AI Practices (AI Act Article 5):** The AI Act outright bans certain AI practices deemed to pose an unacceptable risk to Union values and fundamental rights. Many of these prohibited practices inherently involve the processing of personal data and would likely also contravene core GDPR principles such as lawfulness, fairness, purpose limitation, and the rules for processing special categories of data.<sup>8</sup> Examples include:
  - AI systems deploying subliminal techniques or purposefully manipulative or deceptive techniques to materially distort a person's behavior, causing significant harm.
  - Social scoring systems by public or private actors leading to discriminatory outcomes or detrimental treatment in unrelated contexts.
  - Certain uses of "real-time" remote biometric identification systems in publicly accessible spaces for law enforcement (with very narrow exceptions).
  - Untargeted scraping of facial images from the internet or CCTV footage to create or expand facial recognition databases.
  - Emotion recognition systems in the workplace and educational institutions (except for medical or safety reasons).
  - Biometric categorization systems based on sensitive attributes like race, political opinions, or sexual orientation (with limited exceptions). The AI Act's explicit prohibitions on these practices provide clearer "red lines" than GDPR alone might offer for those specific use cases. This can simplify compliance decisions in these narrow areas by making the practice unlawful per se under the AI Act, thereby reinforcing any existing GDPR concerns.
- **High-Risk AI Systems (AI Act Annex III):** AI systems classified as high-risk (e.g., those used in critical infrastructure, education, employment, law enforcement, or those making automated decisions that significantly affect fundamental rights) are subject to a comprehensive set of stringent requirements under the AI Act.<sup>10</sup> These obligations often align with, reinforce, or expand upon GDPR obligations:
  - **Data and Data Governance (AI Act Article 10):** High-risk AI systems must be trained, validated, and tested using high-quality datasets. This includes requirements for relevance, representativeness, freedom from errors, and completeness. Specific attention must be paid to detecting and mitigating possible biases in datasets that could lead to discrimination or affect fundamental rights.<sup>10</sup> These requirements directly support GDPR's principles of accuracy (Article 5(1)(d)) and fairness (Article 5(1)(a)).
  - **Technical Documentation and Logging (AI Act Articles 11, 19):** Providers of high-risk AI systems must draw up and maintain extensive technical documentation. These systems must also be designed to enable the automatic recording of events (logs) throughout their lifecycle.<sup>10</sup> These obligations strongly support the GDPR's accountability principle (Article 5(2) and Article 24).
  - **Transparency and Provision of Information to Deployers (AI Act Article 13):** High-risk AI systems must be designed and developed to achieve an appropriate level of transparency for their intended use, enabling deployers to understand their functioning and limitations. They must be accompanied by clear instructions for use.<sup>10</sup> This aligns with GDPR's transparency requirements (Articles 12-14) and the need for meaningful information regarding automated decision-making (Article 15, 22).
  - **Human Oversight (AI Act Article 14):** High-risk AI systems must be designed and developed to allow for effective human oversight by natural persons during the period the AI system is in use.<sup>10</sup> This is a key safeguard that also supports GDPR compliance, particularly in mitigating risks associated with automated decisions that have significant effects.
  - **Accuracy, Robustness, and Cybersecurity (AI Act Article 15):** High-risk AI systems must achieve an appropriate level of accuracy, robustness, and cybersecurity throughout their lifecycle.<sup>10</sup> These requirements directly complement GDPR's principles of accuracy (Article 5(1)(d)) and integrity and confidentiality (Article 5(1)(f), Article 32).
  - **Fundamental Rights Impact Assessment (FRIA) (AI Act Article 27):** Deployers of certain high-risk AI systems (e.g., public bodies, private entities providing public services, or those in specific sectors like banking or insurance) are required to conduct a FRIA before putting the system into use.<sup>10</sup> A FRIA assesses the potential impact of the AI system on fundamental rights more broadly than a GDPR-mandated DPIA, which focuses specifically on risks to data protection. While DPIAs focus on risks to data subjects' rights and freedoms concerning their personal data, FRIAs consider a wider range of fundamental rights, such as non-discrimination and freedom of expression, beyond purely data protection aspects. This will require organizations to develop or adopt more holistic impact assessment methodologies that can address both data protection and wider fundamental rights impacts in a coordinated manner.
- **Transparency Risk AI Systems:** For AI systems that pose a transparency risk, such as chatbots or systems generating deepfakes, the AI Act mandates specific disclosure obligations. Users must be made aware that they are interacting with an AI system or that content has been AI-generated or manipulated.<sup>10</sup> This directly supports the GDPR's transparency principle.

**Harmonizing Compliance Efforts:**

Organizations developing or deploying AI agents can harmonize their GDPR and AI Act compliance efforts. Many of the AI Act's requirements for high-risk systems effectively codify and expand upon best practices that would already be expected under a robust interpretation of GDPR for complex AI. For example, a thorough DPIA conducted under GDPR would likely address many of the risks and mitigation measures that the AI Act seeks to formalize for high-risk systems. Data governance practices established for GDPR compliance, such as data mapping, records of processing activities, and data quality checks, will provide a strong foundation for meeting the AI Act's data requirements. Similarly, security measures implemented under GDPR Article 32 will contribute to meeting the AI Act's cybersecurity demands. Organizations with mature GDPR programs for AI will therefore have a significant head start in achieving AI Act compliance.

The following table outlines key overlaps and distinctions between GDPR and the EU AI Act for AI agent data processing:

\\begin{table}\[h!\]

\\centering

\\caption{GDPR vs. EU AI Act – Key Overlaps and Distinctions for AI Agent Data Processing}

\\label{tab:gdpr_ai_act_comparison}

\\resizebox{\\textwidth}{!}{%

\\begin{tabular}{|p{2.8cm}|p{3.2cm}|p{3.7cm}|p{3.2cm}|p{3.2cm}|p{1.5cm}|}

\\hline

\\textbf{Compliance Aspect} & \\textbf{GDPR Requirement(s)} & \\textbf{EU AI Act Requirement(s) (High-Risk Focus)} & \\textbf{Key Overlap/Synergy} & \\textbf{Distinct AI Act Obligation/Expansion} & \\textbf{Key Sources} \\

\\hline

Risk Assessment & DPIA for high-risk processing (Art. 35) & Risk management system throughout lifecycle (Art. 9); FRIA for certain deployers (Art. 27) & Both mandate risk assessment for high-impact systems. DPIA informs AI Act risk management. & AI Act mandates specific risk management system for AI. FRIA has broader scope than DPIA (all fundamental rights). & 10 (Art. 9, 27), 28 \\

\\hline

Data Governance & Principles: Lawfulness, Fairness, Transparency, Purpose Limitation, Data Minimisation, Accuracy (Art. 5) & High-quality training, validation, testing data; bias mitigation; data relevance & AI Act operationalizes GDPR data principles for AI data inputs. & Specific requirements for dataset quality, representativeness, error-freeness, bias detection/correction for high-risk AI (Art. 10). & 10 (Art. 10) \\

\\hline

Transparency & Explainability & Information to data subjects (Art. 13-15); "Meaningful information" on ADM logic (Art. 22) & Transparency for deployers (Art. 13); Disclosure for chatbots/deepfakes. Explainability for ADM (CJEU interpretation). & Both require clarity on AI operation and decision-making. & AI Act has specific disclosure rules for certain AI types. High-risk AI must provide detailed info to deployers. & 7 (Art. 13) \\

\\hline

Human Oversight & Safeguards for ADM (Art. 22 - right to human intervention) & Effective human oversight for high-risk AI (Art. 14) & Both recognize need for human involvement in critical AI decisions. & AI Act mandates design for human oversight; specific enhanced oversight for some biometric systems. & 10 (Art. 14) \\

\\hline

Security & Appropriate TOMs (Art. 32); Integrity & Confidentiality (Art. 5(1)(f)) & Robustness, accuracy, cybersecurity for high-risk AI (Art. 15) & Both require strong security measures. & AI Act specifies AI-related robustness (e.g., against adversarial attacks) and accuracy levels. & 10 (Art. 15) \\

\\hline

Lawful Basis / Prohibited Uses & Lawful basis for all processing (Art. 6, 9) & Prohibition of certain unacceptable risk AI practices (Art. 5) & Prohibited AI practices often involve unlawful data processing under GDPR. & AI Act explicitly bans specific AI applications, providing clearer red lines. & 8 (Art. 5) \\

\\hline

Accountability & Controller responsibility; demonstrate compliance (Art. 5(2), 24); RoPA (Art. 30) & Technical documentation (Art. 11); Logging (Art. 19); Quality Management System (Art. 17) & Both require extensive record-keeping and demonstrable compliance. & AI Act mandates specific technical documentation for AI, activity logging, and QMS for providers. & 10 (Art. 11, 17, 19) \\

\\hline

\\end{tabular}%

}

\\end{table}

## **IX. Strategic Recommendations for Robust GDPR Compliance for AI Agents in 2025 and Beyond**

Ensuring robust GDPR compliance for AI agent-based products in the dynamic landscape of 2025 requires more than adherence to a static checklist; it demands a proactive, adaptive, and ethically grounded strategic approach. Organizations must embed data protection into their culture and operations to navigate evolving legal interpretations, technological advancements, and societal expectations.

Develop a Proactive and Adaptive Compliance Posture:

The regulatory and technological environment for AI is in constant flux. Organizations must therefore establish mechanisms for continuously monitoring legal interpretations from courts like the CJEU, new guidance from the EDPB and national DPAs, and evolving cybersecurity threat intelligence from bodies like ENISA.2 This includes staying abreast of advancements in AI capabilities and the development of new Privacy Enhancing Technologies (PETs). A critical component of an adaptive posture is the establishment of an AI governance board or committee. This body should comprise cross-functional representation from legal, compliance, technology, ethics, and business units to provide holistic oversight and strategic direction for AI development and deployment.23 Compliance should be viewed as an ongoing journey, requiring iterative refinement, particularly for self-learning AI agents whose behavior and data processing activities can change over time.

Foster a Culture of Data Privacy and AI Ethics:

Technical and procedural safeguards are essential, but they are most effective when supported by a strong organizational culture that values data privacy and AI ethics. Comprehensive and regular training programs should be implemented for all personnel involved in the design, development, deployment, and oversight of AI agents.2 This training should cover foundational GDPR principles, AI-specific risks (such as algorithmic bias, security vulnerabilities unique to AI, and the implications of automated decision-making), and broader ethical considerations relevant to the AI agent's application. Ethical guidelines should be formally developed and embedded into AI development and deployment processes, ensuring that AI systems are not only compliant but also fair, accountable, and aligned with human values.12

Prioritize Data Protection by Design and by Default (DPbDD):

DPbDD, as mandated by GDPR Article 25, must be a non-negotiable starting point for all AI agent projects.4 Given the inherent complexities and potential high risks associated with AI agents, attempting to retrofit privacy safeguards is significantly more costly, less effective, and can lead to substantial rework or even project failure. DPbDD requires integrating data protection principles and safeguards into the very architecture of the AI agent from its conceptualization. This includes making conscious design choices that minimize data collection, enhance security, promote transparency, and facilitate data subject rights. Organizations should actively invest in and explore the use of PETs that are appropriate for the AI agent's specific use case and risk profile, such as federated learning, homomorphic encryption, or differential privacy, to further embed privacy into the system's core.51

Invest in Transparency and Explainability Technologies:

Meeting the increasing legal and societal demands for transparency and explainability in AI decision-making requires investment in appropriate technologies and methodologies. Organizations should explore and implement Explainable AI (XAI) tools and techniques that can provide meaningful insights into how AI agents arrive at their decisions or recommendations, particularly when these have significant effects on individuals.7 This not only aids in fulfilling GDPR obligations (e.g., Article 15 and 22) but also helps in building user trust and identifying potential biases or errors in the AI system.

Strengthen Vendor Due Diligence and Contractual Safeguards:

Many organizations will rely on third-party vendors for AI agents, models, or underlying platforms. In such cases, conducting thorough due diligence on the vendor's GDPR compliance posture, data sourcing practices, security measures, and transparency commitments is critical.21 Robust contractual safeguards, typically in the form of Data Processing Agreements (DPAs) under Article 28 GDPR, must be in place. These agreements should clearly define the roles and responsibilities of the controller and processor, specify the scope and purpose of processing, outline security obligations, and detail procedures for handling data subject rights and data breaches.1

Maintain Comprehensive and Dynamic Documentation:

Accountability is a cornerstone of the GDPR. Organizations must maintain detailed and up-to-date records of all AI-related data processing activities. This includes DPIAs, LIAs, records of processing activities (RoPAs), documentation of security measures implemented, procedures for handling data subject requests, records of consent, AI model development and validation processes, and data breach incident reports.2 For dynamic AI agents, this documentation must be regularly reviewed and updated to reflect any changes in their processing activities or risk profile.

Effective GDPR compliance for AI agents in 2025 and beyond hinges on establishing a resilient and adaptive governance framework. The rapid evolution of AI technology and regulatory interpretations means that a static, checklist-based approach to compliance is insufficient. The repeated emphasis in legal and regulatory discourse on the dynamic nature of AI <sup>4</sup>, evolving security threats <sup>33</sup>, new judicial precedents <sup>7</sup>, and ongoing regulatory guidance from bodies like the EDPB and national DPAs underscores the necessity for agile and forward-looking compliance strategies. These strategies must be rooted in core data protection principles and a robust risk management methodology rather than an overly rigid adherence to prescriptive rules alone.

Furthermore, true "accountability" in the context of AI agents will increasingly require organizations to demonstrate not only legal compliance but also ethical stewardship of the technology. This involves a proactive consideration of the broader societal impacts and fundamental rights implications of AI, extending beyond the strict confines of data protection. The introduction of requirements like the Fundamental Rights Impact Assessment (FRIA) under the EU AI Act <sup>10</sup>, the growing focus on AI ethics in research and development <sup>12</sup>, and the concerns voiced by DPAs regarding algorithmic bias and fairness <sup>12</sup> all point towards an expanding expectation of responsible AI development and deployment. GDPR accountability serves as the foundational layer, but the emerging landscape demands a more holistic commitment to ethical AI governance.

## **X. Conclusion**

Ensuring GDPR compliance for AI agent-based products in 2025 is a complex but critical endeavor. The enduring foundational principles of the GDPR—lawfulness, fairness, transparency, purpose limitation, data minimisation, accuracy, storage limitation, integrity and confidentiality, and accountability—provide the essential framework. However, their application to the dynamic, autonomous, and data-intensive nature of AI agents requires careful consideration and bespoke strategies. The evolving legal landscape, marked by significant CJEU rulings and detailed guidance from the EDPB and national DPAs, alongside the increasing applicability of the EU AI Act, demands a proactive and adaptive approach from organizations.

Key takeaways from this analysis emphasize the necessity of robust data governance, including comprehensive DPIAs and LIAs, particularly when relying on legitimate interests for processing data for AI model training and deployment. Transparency and explainability in automated decision-making are no longer aspirational goals but increasingly concrete legal expectations, requiring investment in XAI techniques and clear communication with data subjects. Upholding data subject rights in the context of AI agents presents unique technical challenges, necessitating innovative solutions such as output filtering or advanced data management in training datasets. Addressing AI-specific risks, including algorithmic bias and novel security vulnerabilities, is paramount. Data Protection by Design and by Default, supported by appropriate PETs, must be integral to the entire AI agent lifecycle.

The future of AI regulation and data protection will likely see a continued evolution of legal frameworks and judicial interpretations as AI technology matures and its societal impact becomes more profound. Increased international cooperation among DPAs and the development of harmonized standards will be crucial for providing legal certainty and fostering responsible innovation. The future of GDPR compliance in the age of AI agents will likely place a greater emphasis on auditable AI systems, the ability to provide verifiable claims about data handling practices (such as for anonymisation or bias mitigation), and the demonstration of accountability through a combination of robust technical and organizational measures. The collective weight of CJEU rulings demanding meaningful explanations <sup>7</sup>, EDPB guidance requiring empirical proof for anonymity and legitimate interest claims <sup>21</sup>, and the AI Act's stringent documentation and logging requirements <sup>10</sup> all point towards a future where mere assertions of compliance will be insufficient. Regulators and data subjects alike will expect verifiable evidence of data protection in practice.

As AI agents become more deeply integrated into business processes and societal functions, the definition of "harm" and "risk" under the GDPR may be interpreted more broadly. This could encompass the complex societal impacts of AI, thereby expanding the scope and depth of DPIAs and, where applicable, FRIAs. The ongoing challenge for organizations will be to strike a sustainable balance between harnessing the transformative power of AI innovation and upholding the fundamental right to data protection and broader ethical considerations. A commitment to these principles will not only ensure legal compliance but also build essential trust with users and society at large, paving the way for a future where AI serves humanity responsibly.

#### Works cited

1. The GDPR in brief | Autoriteit Persoonsgegevens, accessed May 24, 2025, <https://www.autoriteitpersoonsgegevens.nl/en/themes/basic-gdpr/gdpr-basics/the-gdpr-in-brief>
2. What are the Best Practices for GDPR Compliance? | Scytale, accessed May 24, 2025, <https://scytale.ai/resources/best-practices-for-gdpr-compliance/>
3. GDPR Cybersecurity Compliance: A Definitive Guide | FireMon, accessed May 24, 2025, <https://www.firemon.com/blog/gdpr-cybersecurity-compliance/>
4. Agentic AI and EU Legal Considerations | Mason Hayes Curran, accessed May 24, 2025, <https://www.mhc.ie/latest/insights/rise-of-the-helpful-machines>
5. Minding Mindful Machines: AI Agents and Data Protection ..., accessed May 24, 2025, <https://fpf.org/blog/minding-mindful-machines-ai-agents-and-data-protection-considerations/>
6. Agentic AI's risk and reward calculus | IAPP, accessed May 24, 2025, <https://iapp.org/news/a/agentic-ai-s-risk-and-reward-calculus>
7. CJEU Clarifies GDPR Rights on Automated Decision-Making and ..., accessed May 24, 2025, <https://www.insideprivacy.com/gdpr/cjeu-clarifies-gdpr-rights-on-automated-decision-making-and-trade-secrets/>
8. The European Commission's Guidance on Prohibited AI Practices: Unraveling the AI Act, accessed May 24, 2025, <https://www.privacyworld.blog/2025/05/the-european-commissions-guidance-on-prohibited-ai-practices-unraveling-the-ai-act/>
9. EU Commission Publishes Guidelines on the Prohibited AI Practices ..., accessed May 24, 2025, <https://www.orrick.com/en/Insights/2025/04/EU-Commission-Publishes-Guidelines-on-the-Prohibited-AI-Practices-under-the-AI-Act>
10. AI Act | Shaping Europe's digital future, accessed May 24, 2025, <https://digital-strategy.ec.europa.eu/en/policies/regulatory-framework-ai>
11. Leading with Trust: How Data Privacy and Governance Shape the Future of AI Agents, accessed May 24, 2025, <https://www.outreach.io/resources/blog/data-privacy-governance-future-of-ai>
12. CHAPTER 3: Responsible AI, accessed May 24, 2025, <https://hai-production.s3.amazonaws.com/files/hai_ai-index-report-2025_chapter3_final.pdf>
13. Blog - AI Agents and Data Privacy: Navigating GDPR Compliance, accessed May 24, 2025, <https://sennalabs.com/blog/ai-agents-and-data-privacy-navigating-gdpr-compliance>
14. Data Privacy in AI: A Guide for Modern Industries | TrustArc, accessed May 24, 2025, <https://trustarc.com/resource/ai-applications-used-in-privacy-compliance/>
15. AI View: February 2025, accessed May 24, 2025, <https://www.simmons-simmons.com/en/publications/cm7al90ss006utf2kp6swxye6/ai-view-february-2025>
16. The Commission publishes guidelines on AI system definition to facilitate the first AI Act's rules application, accessed May 24, 2025, <https://digital-strategy.ec.europa.eu/en/library/commission-publishes-guidelines-ai-system-definition-facilitate-first-ai-acts-rules-application>
17. <www.dataprotection.ie>, accessed May 24, 2025, <https://www.dataprotection.ie/sites/default/files/uploads/2019-11/Guidance%20on%20the%20Principles%20of%20Data%20Protection_Oct19.pdf>
18. Data Minimization – EPIC – Electronic Privacy Information Center, accessed May 24, 2025, <https://epic.org/issues/consumer-privacy/data-minimization/>
19. AI Agents & IAM: A Digital Trust Dilemma | Ping Identity, accessed May 24, 2025, <https://www.pingidentity.com/en/resources/blog/post/digital-trust-dilemma.html>
20. 2025 data protection CJEU case round-up - Kennedys Law, accessed May 24, 2025, <https://kennedyslaw.com/en/thought-leadership/article/2025/2025-data-protection-cjeu-case-round-up/>
21. GDPR Considerations When Developing and Deploying AI Models ..., accessed May 24, 2025, <https://www.debevoisedatablog.com/2025/04/14/gdpr-considerations-when-developing-and-deploying-ai-models-the-edpbs-opinion-on-compliance/>
22. Navigating GDPR Risks in AI: Insights from the EDPB's latest ..., accessed May 24, 2025, <https://technologyquotient.freshfields.com/post/102jsr2/navigating-gdpr-risks-in-ai-insights-from-the-edpbs-latest-opinion-the-uk-ico>
23. AI and Data Privacy: Mitigating Risks and Ensuring Protection | Qualys, accessed May 24, 2025, <https://blog.qualys.com/product-tech/2025/02/07/ai-and-data-privacy-mitigating-risks-in-the-age-of-generative-ai-tools>
24. The Intersection of GDPR and AI and 6 Compliance Best Practices ..., accessed May 24, 2025, <https://www.exabeam.com/explainers/gdpr-compliance/the-intersection-of-gdpr-and-ai-and-6-compliance-best-practices/>
25. GDPR & AI: Compliance, Challenges & Best Practices | DPO ..., accessed May 24, 2025, <https://www.dpo-consulting.com/blog/gdpr-and-ai-best-practices>
26. How to Conduct a Thorough DPIA for AI Compliance \[with GDPR\], accessed May 24, 2025, <https://foundershield.com/blog/ai-compliance-through-dpia/>
27. How to Conduct a Data Protection Impact Assessment (DPIA) | 2025 ..., accessed May 24, 2025, <https://www.alation.com/blog/data-protection-impact-assessment-dpia-2025-guide/>
28. Navigating Through Human Rights in AI: Exploring the Interplay ..., accessed May 24, 2025, <https://www.mdpi.com/2624-800X/5/1/7>
29. What You Should Know About Article 35 of the GDPR - Securiti, accessed May 24, 2025, <https://securiti.ai/article-35-gdpr/>
30. AI explainability legal governance: Pulling back the curtain ..., accessed May 24, 2025, <https://www.michalsons.com/blog/ai-explainability-legal-governance/77745>
31. EDPB publishes eagerly anticipated Opinion on AI models - Matheson, accessed May 24, 2025, <https://www.matheson.com/insights/detail/edpb-publishes-eagerly-anticipated-opinion-on-ai-models>
32. EU: EDPB Opinion on AI Provides Important Guidance though Many Questions Remain, accessed May 24, 2025, <https://privacymatters.dlapiper.com/2025/01/eu-edpb-opinion-on-ai-provides-important-guidance-though-many-questions-remain/>
33. Understanding the Evolving Cybersecurity Threat Landscape in the EU: An In-Depth Analysis for Compliance, accessed May 24, 2025, <https://www.compliancehub.wiki/understanding-the-evolving-cybersecurity-threat-landscape-in-the-eu-an-in-depth-analysis-for-compliance/>
34. multilayer framework for good cybersecurity practices for ai - ENISA, accessed May 24, 2025, <https://www.enisa.europa.eu/sites/default/files/publications/Multilayer%20Framework%20for%20Good%20Cybersecurity%20Practices%20for%20AI.pdf>
35. Tag – CNIL - Hunton Andrews Kurth LLP, accessed May 24, 2025, <https://www.hunton.com/privacy-and-information-security-law/tag/cnil>
36. France: CNIL publishes recommendations on AI and GDPR | News - DataGuidance, accessed May 24, 2025, <https://www.dataguidance.com/news/france-cnil-publishes-recommendations-ai-and-gdpr>
37. New CNIL's guidelines on AI models: a practical approach amidst ..., accessed May 24, 2025, <https://www.hoganlovells.com/en/publications/new-cnils-guidelines-on-ai-models-a-practical-approach-amidst-eus-regulatory-tangles>
38. AI & GDPR: The key steps to bring your tools into compliance - Squair, accessed May 24, 2025, <https://www.squairlaw.com/en/blog/ai-gdpr-the-key-steps-to-bring-your-tools-into-compliance>
39. Gibson Dunn | Europe | Data Protection – February 2025, accessed May 24, 2025, <https://www.gibsondunn.com/gibson-dunn-europe-data-protection-february-2025/>
40. Data governance and AI: Five Data Protection Authorities Commit to Innovative and Privacy-Protecting AI | CNIL, accessed May 24, 2025, <https://www.cnil.fr/en/data-governance-and-ai-five-data-protection-authorities-commit-innovative-and-privacy-protecting-ai>
41. Privacy and AI: Navigating compliance with GDPR and the AI Act, accessed May 24, 2025, <https://techsense.lu/news/privacy-and-ai-navigating-compliance-with-gdpr-and-the-ai-act>
42. The European Data Protection Board Shares Opinion on How to ..., accessed May 24, 2025, <https://www.orrick.com/en/Insights/2025/03/The-European-Data-Protection-Board-Shares-Opinion-on-How-to-Use-AI-in-Compliance-with-GDPR>
43. Artificial Intelligence and Data Protection: The EDPB Opinion 28 ..., accessed May 24, 2025, <https://www.clydeco.com/en/insights/2025/03/artificial-intelligence-and-data-protection-the-ed>
44. AI & GDPR: Key Challenges, Fines and Practical Solutions, accessed May 24, 2025, <https://www.ddg.fr/actualite/compliance-of-ai-systems-with-the-gdpr-issues-penalties-and-prospects>
45. Data Protection and Privacy in AI-Based Learning Systems - LTEN, accessed May 24, 2025, <https://www.l-ten.org/Web/Web/News---Insights/focus-articles/Data-Protection-and-Privacy-in-AI-Based-Learning-Systems.aspx>
46. Art. 20 GDPR – Right to data portability - General Data Protection ..., accessed May 24, 2025, <https://gdpr-info.eu/art-20-gdpr/>
47. Art. 21 GDPR – Right to object - General Data Protection Regulation ..., accessed May 24, 2025, <https://gdpr-info.eu/art-21-gdpr/>
48. Summary of EDPB's Opinion 28/2024 Concerning AI Models ..., accessed May 24, 2025, <https://securiti.ai/summary-of-edpb-opinion-282024-concerning-ai-models-processing-of-personal-data/>
49. Art. 25 GDPR – Data protection by design and by default - General ..., accessed May 24, 2025, <https://gdpr-info.eu/art-25-gdpr/>
50. International: Privacy by Design and by Default in AI tools - AI series ..., accessed May 24, 2025, <https://www.dataguidance.com/opinion/international-privacy-design-and-default-ai-tools-ai>
51. Artificial Intelligence/Machine Learning & the ... - PayPal Ventures, accessed May 24, 2025, <https://paypal.vc/news/news-details/2025/Artificial-Intelligence-Machine-Learning--the-Privacy-Tech-Renaissance-by-Rachel-Zhao-Investor--Lorenzo-Ligato-Intern/default.aspx>
52. <www.informationpolicycentre.com>, accessed May 24, 2025, <https://www.informationpolicycentre.com/uploads/5/7/1/0/57104281/cipl_pets_and_ppts_in_ai_mar25.pdf>
53. Guidelines on prohibited AI practices as published by the Commission - Deloitte, accessed May 24, 2025, <https://www.deloitte.com/lu/en/Industries/technology/perspectives/guidelines-prohibited-ai-practices.html>
54. ISO 42001 Annex C: Top AI Governance Objectives And Risks, accessed May 24, 2025, <https://cyberzoni.com/standards/iso-42001/annex-c/>
55. Best AI Practices to Comply with GDPR - Seifti, accessed May 24, 2025, <https://seifti.io/best-ai-practices-to-comply-with-gdpr/>
56. AAAI-25 New Faculty Highlights Program, accessed May 24, 2025, <https://aaai.org/conference/aaai/aaai-25/new-faculty-highlights-program/>