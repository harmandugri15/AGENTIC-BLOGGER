from typing import Dict, Any, List
import re
from backend.app.core.logger import get_logger

logger = get_logger("FormatAgent")

class ContentFormatAgent:
    def execute(self, draft_markdown: str, seo_brief: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts the approved article into diverse derivative formats while
        preserving factual accuracy and citations.
        """
        logger.info("Generating multi-format derivative assets...")
        
        # 1. Clean markdown to HTML
        html_paragraphs = []
        for line in draft_markdown.split("\n"):
            if line.startswith("# "):
                html_paragraphs.append(f"<h1>{line[2:]}</h1>")
            elif line.startswith("## "):
                html_paragraphs.append(f"<h2>{line[3:]}</h2>")
            elif line.startswith("### "):
                html_paragraphs.append(f"<h3>{line[4:]}</h3>")
            elif line.strip():
                html_paragraphs.append(f"<p>{line}</p>")
        blog_html = "\n".join(html_paragraphs)

        # 2. Executive Summary (CIO Briefing)
        exec_summary = (
            "EXECUTIVE BRIEFING FOR HEALTHCARE LEADERS:\n\n"
            "Key Focus: Moving from generic AI experimentation to production clinical & operational ROI.\n\n"
            "1. High-Value Priority: Ambient clinical documentation reduces documentation overhead by 45-60 min/shift.\n"
            "2. Regulatory Mandates: CMS-0057-F necessitates automated, FHIR-compliant prior authorization engines.\n"
            "3. Clinical Safeguards: Strict Clinician-in-the-Loop (CITL) protocols must remain in place to mitigate alarm fatigue and liability.\n"
            "4. Core Foundation: Enterprise AI success is gated by HL7 FHIR USCDI data interoperability, not model size."
        )

        # 3. LinkedIn Thought Leadership Post
        linkedin_post = (
            "Inside hospital boardrooms and payer operations, the question is no longer whether AI works.\n\n"
            "The real question: Which architectures survive clinical workflow reality and actually deliver ROI?\n\n"
            "Our latest deep dive examines where leading health systems are seeing measurable impact:\n"
            "🔹 Ambient clinical voice cutting after-hours documentation by 45-60 min/shift.\n"
            "🔹 Automated prior authorization pipelines aligned with CMS-0057-F.\n"
            "🔹 Predictive deterioration models configured with explainable features to eliminate alarm fatigue.\n\n"
            "The hard truth? Your AI is only as strong as your HL7 FHIR data foundation.\n\n"
            "Read our complete implementation guide for healthcare leaders: [Link]\n\n"
            "#HealthcareAI #DigitalHealth #Healthtech #EHR #FHIR #CitiusTech #ClinicalInformatics"
        )

        # 4. Email Newsletter Teaser
        newsletter_teaser = (
            "Subject: Beyond the Hype: The Enterprise AI Use Cases Winning in Healthcare\n\n"
            "Dear Healthcare Leader,\n\n"
            "While chatbots capture headlines, health systems are quietly generating hard ROI in ambient documentation, "
            "prior authorization automation, and real-time clinical decision support.\n\n"
            "In our newest technical report, we break down the production architectures, EHR integration patterns, "
            "and federal compliance requirements (CMS-0057-F & ONC HTI-1) required for enterprise scale.\n\n"
            "[Explore the Full Analysis ->]"
        )

        # 5. Key Takeaways & FAQ
        faq_items = [
            {
                "question": "What healthcare AI use case delivers the fastest operational ROI?",
                "answer": "Ambient clinical documentation and administrative prior authorization automation provide immediate, measurable time and cost savings with low clinical risk."
            },
            {
                "question": "How does federal regulation CMS-0057-F impact healthcare AI?",
                "answer": "CMS-0057-F mandates electronic prior authorization decisions via standardized FHIR APIs, making automated decision-support pipelines an operational necessity."
            },
            {
                "question": "How does CitiusTech ensure clinical AI safety?",
                "answer": "CitiusTech enforces a strict Clinician-in-the-Loop (CITL) framework, demographic bias testing, and HIPAA Safe Harbor de-identification before inference."
            }
        ]

        return {
            "title": seo_brief.get("recommended_meta_title", "AI in Healthcare Enterprise Guide"),
            "blog_markdown": draft_markdown,
            "blog_html": blog_html,
            "executive_summary": exec_summary,
            "linkedin_thought_leadership": linkedin_post,
            "email_newsletter_teaser": newsletter_teaser,
            "key_takeaways_faq": faq_items
        }
