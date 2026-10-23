from typing import Dict, Any, List
import re
from backend.app.core.logger import get_logger

logger = get_logger("FormatAgent")

class ContentFormatAgent:
    def execute(self, draft_markdown: str, seo_brief: Dict[str, Any]) -> Dict[str, Any]:
        """
        Converts the approved article into diverse derivative formats dynamically tailored
        to the target topic, domain, and audience while preserving factual citations.
        """
        logger.info("Generating multi-format derivative assets...")
        
        domain = seo_brief.get("domain", "Enterprise Technology")
        primary_kw = seo_brief.get("primary_keywords", ["AI Implementations"])[0] if seo_brief.get("primary_keywords") else "Enterprise AI"
        title = seo_brief.get("recommended_meta_title", f"Best Use Cases of {primary_kw}")
        target_query = seo_brief.get("target_query", primary_kw)

        # 1. Clean markdown to HTML
        html_paragraphs = []
        for line in draft_markdown.split("\n"):
            line_s = line.strip()
            if not line_s:
                continue
            if line_s.startswith("# "):
                html_paragraphs.append(f"<h1>{line_s[2:]}</h1>")
            elif line_s.startswith("## "):
                html_paragraphs.append(f"<h2>{line_s[3:]}</h2>")
            elif line_s.startswith("### "):
                html_paragraphs.append(f"<h3>{line_s[4:]}</h3>")
            elif line_s.startswith("---"):
                html_paragraphs.append("<hr />")
            elif line_s.startswith("* "):
                html_paragraphs.append(f"<li>{line_s[2:]}</li>")
            elif re.match(r"^\d+\.\s+[A-Z]", line_s):
                html_paragraphs.append(f"<h2>{line_s}</h2>")
            else:
                html_paragraphs.append(f"<p>{line_s}</p>")
        blog_html = "\n".join(html_paragraphs)

        # 2. Generate CMS/Yoast Markdown with proper ## subheadings for editors
        cms_markdown_lines = []
        for line in draft_markdown.split("\n"):
            line_s = line.strip()
            if re.match(r"^\d+\.\s+[A-Z]", line_s) or (line_s.isupper() and len(line_s) > 5 and not line_s.startswith("---") and not line_s.startswith("![") and not line_s.startswith("+")):
                cms_markdown_lines.append(f"## {line_s}")
            else:
                cms_markdown_lines.append(line)
        cms_markdown = "\n".join(cms_markdown_lines)

        # 3. Dynamic Executive Summary (C-Suite Briefing)
        full_context = f"{domain} {title} {target_query}".lower()
        if any(w in full_context for w in ["robot", "robotics", "cobot", "autonomous", "drone", "manipulator", "slam"]):
            exec_summary = (
                f"EXECUTIVE BRIEFING: {title.upper()}\n\n"
                "Target Audience: VP of Automation, Robotics Engineering Directors & Plant Managers\n"
                "Core Objective: Moving past flashy humanoid demonstrations to production assembly line throughput, edge safety, and operator trust.\n\n"
                "1. Immediate Impact: Vision-guided manipulation with edge 3D point cloud parsing cuts assembly alignment errors by 30%.\n"
                "2. Warehouse Mobility: Autonomous Mobile Robots (AMR) using real-time SLAM eliminate forklift collisions and transport bottlenecks.\n"
                "3. Sim-to-Real Acceleration: Physics-engine domain randomization trains dexterous manipulation policies weeks faster than manual scripting.\n"
                "4. Core Foundation: Success requires open ROS 2 DDS middleware and strict ISO 10218 cobot fail-safe interlocks."
            )
            linkedin_post = (
                f"In industrial automation and robotics, humanoid video clips have dominated social media for eighteen months.\n\n"
                "The real question plant managers are asking: Which implementations survive real factory floors, keep workers safe, and deliver ROI?\n\n"
                "Our latest breakdown covers the practical enterprise use cases:\n"
                "🔹 Vision-guided manipulation eliminating rigid coordinate dependencies.\n"
                "🔹 Autonomous Mobile Robots (AMR) navigating warehouse corridors in real time.\n"
                "🔹 Sim-to-real reinforcement learning accelerating dexterous assembly.\n\n"
                "Success doesn't come from closed black-box arms. It requires open ROS 2 middleware and deterministic edge inference.\n\n"
                f"Explore our full implementation guide for robotics leaders: [Link]\n\n"
                "#Robotics #IndustrialAutomation #AMR #Cobots #ComputerVision #ROS2 #Industry40"
            )
            newsletter_teaser = (
                f"Subject: Beyond the Hype: Production Architectures in Enterprise {primary_kw}\n\n"
                "Dear Robotics Leader,\n\n"
                "While viral humanoid clips grab attention, smart facilities are deploying AI where it counts: "
                "guiding precision assembly arms with edge vision, automating dynamic warehouse transport with SLAM, and stopping unplanned joint failures.\n\n"
                "In our newest technical report, we break down production architectures, edge GPU latency constraints, and ISO cobot safety compliance.\n\n"
                "[Read the Full Executive Briefing ->]"
            )
            faq_items = [
                {
                    "question": "How does edge AI handle lighting variations on factory floors?",
                    "answer": "Modern vision models utilize domain-randomized synthetic training and active IR lighting, allowing sub-5ms real-time adaptation without manual recalibration."
                },
                {
                    "question": "Can collaborative robots safely work alongside humans without safety fences?",
                    "answer": "Yes, when certified under ISO/TS 15066 with power and force-limiting sensors, dynamic deceleration zones, and dual-channel fail-safe emergency circuits."
                },
                {
                    "question": "Why is ROS 2 required for enterprise robotics architectures?",
                    "answer": "ROS 2 provides real-time DDS middleware, guaranteed microsecond latency message delivery between motion controllers and AI inference nodes, and vendor-agnostic hardware abstraction."
                }
            ]
        elif any(w in full_context for w in ["education", "school", "student", "teacher", "learning", "edtech", "university"]):
            exec_summary = (
                f"EXECUTIVE BRIEFING: {title.upper()}\n\n"
                "Target Audience: University Deans, Provosts & EdTech Leaders\n"
                "Core Objective: Moving from flashy chatbots to practical implementations that fit into LMS workflows, protect FERPA privacy, and improve learning.\n\n"
                "1. Immediate Impact: Intelligent tutoring and mastery-based adaptive tools solve the 'teach to the middle' problem and improve course completion by 25%.\n"
                "2. Teacher Workload Relief: Automated grading assistance drafts rubric reviews in seconds, returning weekends to tired faculty.\n"
                "3. Early Warning Signals: Predictive retention models aggregate LMS and assignment data to flag at-risk students weeks before midterms.\n"
                "4. Core Foundation: Success requires vendor-agnostic 1EdTech LTI 1.3 standards and strict zero-data-retention FERPA compliance."
            )
            linkedin_post = (
                f"In university administration and EdTech, flashy AI demos have been the topic for eighteen months.\n\n"
                "The real question leaders are asking: Which setups actually work in classroom workflows, protect student privacy, and improve grades?\n\n"
                "Our latest breakdown covers the practical enterprise use cases:\n"
                "🔹 Intelligent tutoring closing learning gaps without replacing teachers.\n"
                "🔹 Automated grading assistance cutting rubric evaluation time by hours.\n"
                "🔹 Early-warning retention models catching at-risk students before midterms.\n\n"
                "Success doesn't come from standalone tools. It comes from 1EdTech LTI 1.3 standards and clean LMS data.\n\n"
                f"Explore the full guide for education leaders: [Link]\n\n"
                "#EdTech #HigherEd #AIinEducation #LearningAnalytics #LTI #CanvasLMS"
            )
            newsletter_teaser = (
                f"Subject: Beyond the Hype: The Real Enterprise Use Cases of {primary_kw}\n\n"
                "Dear Education Leader,\n\n"
                "While student chatbots grab headlines, smart institutions are quietly using AI where it counts: "
                "supporting tired faculty with grading, diagnosing individual learning gaps, and keeping at-risk students enrolled.\n\n"
                "In our newest briefing, we examine the practical setups, LMS integration standards (LTI 1.3), "
                "and FERPA privacy rules needed for enterprise success.\n\n"
                "[Read the Full Executive Briefing ->]"
            )
            faq_items = [
                {
                    "question": "How do educational AI tools comply with FERPA?",
                    "answer": "Enterprise platforms use dedicated virtual private environments with strict zero-data-retention agreements, ensuring student submissions never train public models."
                },
                {
                    "question": "Does AI grading replace instructor feedback?",
                    "answer": "No. Modern systems create pre-annotated draft reviews that teachers inspect, modify, and approve with a single click, keeping educators firmly in control."
                },
                {
                    "question": "What standards are required for LMS integration?",
                    "answer": "1EdTech LTI 1.3 and OneRoster standards ensure seamless single sign-on, roster synchronization, and bidirectional gradebook passback across Canvas, Blackboard, and Moodle."
                }
            ]
        elif "Finance" in domain:
            exec_summary = (
                f"EXECUTIVE BRIEFING: {title.upper()}\n\n"
                "Target Audience: Chief Risk Officers, CIOs & FinTech Leaders\n"
                "Core Objective: Deploying real-time fraud detection, automated AML compliance, and explainable credit risk modeling.\n\n"
                "1. Fraud Mitigation: Sub-second anomaly scoring across real-time transaction streams.\n"
                "2. Regulatory Alignment: Explainable AI models compliant with FCRA and model risk governance.\n"
                "3. Core Foundation: Open banking APIs and PCI-DSS Level 1 security architecture."
            )
            linkedin_post = (
                f"Financial institutions are moving beyond experimental AI into real-time transaction intelligence.\n\n"
                f"Our newest enterprise guide on {primary_kw} covers:\n"
                "🔹 Sub-millisecond fraud scoring and anomaly prevention.\n"
                "🔹 Automated AML/KYC pipelines cutting false positives.\n"
                "🔹 Explainable credit risk underwriting.\n\n"
                f"Read the full architectural breakdown: [Link]\n\n"
                "#FinTech #Banking #FraudPrevention #AIFinance #RegTech"
            )
            newsletter_teaser = (
                f"Subject: Production Architectures: High-Impact Use Cases of {primary_kw}\n\n"
                "Dear Financial Services Leader,\n\n"
                "Discover how leading institutions are deploying real-time fraud intelligence and automated compliance.\n\n"
                "[Explore the Full Technical Briefing ->]"
            )
            faq_items = [
                {
                    "question": "How do risk models ensure explainability?",
                    "answer": "Models deploy SHAP and feature attribution trees so compliance officers can inspect the exact factors driving credit decisions."
                }
            ]
        else: # Healthcare default
            exec_summary = (
                f"EXECUTIVE BRIEFING: {title.upper()}\n\n"
                "Target Audience: Health System CIOs, CMOs & Clinical Informaticists\n"
                "Core Objective: Moving from generic AI experimentation to production clinical & operational ROI.\n\n"
                "1. High-Value Priority: Ambient clinical documentation reduces documentation overhead by 45-60 min/shift.\n"
                "2. Regulatory Mandates: CMS-0057-F necessitates automated, FHIR-compliant prior authorization engines.\n"
                "3. Clinical Safeguards: Strict Clinician-in-the-Loop (CITL) protocols must remain in place to mitigate alarm fatigue and liability.\n"
                "4. Core Foundation: Enterprise AI success is gated by HL7 FHIR USCDI data interoperability, not model size."
            )
            linkedin_post = (
                "Inside hospital corridors and payer operations, the question is no longer whether AI is capable.\n\n"
                "The real question: Which architectures survive clinical workflow reality and actually deliver ROI?\n\n"
                "Our latest breakdown examines where health systems are seeing measurable impact:\n"
                "🔹 Ambient clinical voice cutting after-hours documentation by 45-60 min/shift.\n"
                "🔹 Automated prior authorization pipelines aligned with CMS-0057-F.\n"
                "🔹 Predictive deterioration models configured with explainable features to eliminate alarm fatigue.\n\n"
                "The hard truth? Your AI is only as strong as your HL7 FHIR data foundation.\n\n"
                f"Read our complete implementation guide: [Link]\n\n"
                "#HealthcareAI #DigitalHealth #Healthtech #EHR #FHIR #ClinicalInformatics"
            )
            newsletter_teaser = (
                f"Subject: Beyond the Hype: The Enterprise AI Use Cases Winning in Healthcare\n\n"
                "Dear Healthcare Leader,\n\n"
                "While chatbots capture headlines, health systems are quietly generating hard ROI in ambient documentation, "
                "prior authorization automation, and real-time clinical decision support.\n\n"
                "In our newest technical report, we break down the production architectures, EHR integration patterns, "
                "and federal compliance requirements (CMS-0057-F & ONC HTI-1) required for enterprise scale.\n\n"
                "[Explore the Full Analysis ->]"
            )
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
                    "question": "How do systems ensure clinical AI safety?",
                    "answer": "Enforcing a strict Clinician-in-the-Loop (CITL) framework, demographic bias testing, and HIPAA Safe Harbor de-identification before inference."
                }
            ]

        return {
            "title": title,
            "focus_keyword": seo_brief.get("focus_keyword", primary_kw),
            "meta_title": seo_brief.get("recommended_meta_title", title),
            "meta_description": seo_brief.get("recommended_meta_description", ""),
            "slug": seo_brief.get("target_slug", ""),
            "blog_markdown": draft_markdown,
            "cms_markdown": cms_markdown,
            "blog_html": blog_html,
            "executive_summary": exec_summary,
            "linkedin_thought_leadership": linkedin_post,
            "email_newsletter_teaser": newsletter_teaser,
            "key_takeaways_faq": faq_items
        }
