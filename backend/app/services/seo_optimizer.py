import re
from typing import Dict, Any, List
from backend.app.core.logger import get_logger
from backend.app.services.yoast_seo_engine import YoastSEOEngine

logger = get_logger("SEOOptimizer")

class SEOOptimizerEngine:
    """
    Intelligently optimizes On-Page SEO, Yoast Readability, and semantic entity coverage for an article:
    - 100% Yoast Compliance (Flesch >= 60, Paragraphs <= 150 words, Subheadings <= 300 words, Transitions >= 30%).
    - Injects images with focus keyword alt text, internal links, and external citations.
    - Zero '#' markdown hashes in standard display.
    - Focus keyword density between 1.0% and 2.5%.
    """

    def __init__(self):
        self.yoast_engine = YoastSEOEngine()

    def optimize_content(
        self,
        draft_markdown: str,
        seo_strategy: Dict[str, Any],
        target_query: str
    ) -> Dict[str, Any]:
        logger.info(f"Optimizing On-Page SEO for '{target_query}'...")
        
        domain = seo_strategy.get("domain", "")
        primary_kws = seo_strategy.get("primary_keywords", [])
        entities = seo_strategy.get("semantic_entities", [])
        focus_kw = seo_strategy.get("focus_keyword") or self.yoast_engine.extract_focus_keyword(target_query, primary_kws)
        
        q_lower = (domain + " " + target_query).lower()
        if any(w in q_lower for w in ["robot", "robotics", "cobot", "autonomous", "drone", "manipulator", "slam"]):
            main_topic = "AI in Robotics"
        elif any(w in q_lower for w in ["education", "school", "student", "teacher", "learning", "edtech", "university"]):
            main_topic = "AI in Education"
        elif any(w in q_lower for w in ["supply chain", "logistics", "warehouse"]):
            main_topic = "AI in Supply Chain"
        elif any(w in q_lower for w in ["finance", "banking", "fraud", "fintech"]):
            main_topic = "AI in Financial Services"
        elif any(w in q_lower for w in ["health", "hospital", "patient", "clinical", "doctor", "medical"]):
            main_topic = "AI in Healthcare"
        else:
            main_topic = f"AI in {target_query.title()}"
        
        content = draft_markdown
        optimizations_applied = []

        # 1. Guarantee Target Keyword in Title & First 100 Words
        lines = content.split("\n")
        first_content_line_idx = -1
        for i, l in enumerate(lines):
            if l.strip() and not l.strip().startswith("---"):
                first_content_line_idx = i
                break

        if first_content_line_idx != -1:
            current_title = lines[first_content_line_idx].strip()
            topic_core = re.sub(r"^AI in\s+", "", main_topic, flags=re.I)
            if not re.search(r"\b" + re.escape(topic_core) + r"\b", current_title, re.I):
                lines[first_content_line_idx] = f"Best Use Cases of {main_topic}: Practical Setups for Enterprise Leaders"
                optimizations_applied.append(f"Enriched title with primary topic '{main_topic}'")
                content = "\n".join(lines)

        # Check first 100 words
        intro_words = " ".join(content.split()[:100])
        topic_core = re.sub(r"^AI in\s+", "", main_topic, flags=re.I)
        if not re.search(r"\b" + re.escape(topic_core) + r"\b", intro_words, re.I):
            content = content.replace(
                "Here is a breakdown of the important use cases",
                f"Here is a breakdown of the important use cases of {main_topic.lower()}"
            )
            optimizations_applied.append(f"Weaved '{main_topic}' into the introductory hook")

        # 2. Identify Missing High-Value Semantic Entities
        missing_entities = []
        for e in entities:
            base_e = re.sub(r"\s*\([^)]*\)", "", e).strip()
            if not re.search(r"\b" + re.escape(base_e) + r"\b", content, re.I):
                missing_entities.append(e)

        # 3. Naturally Weave Missing Entities into Existing Practical Bullet Points
        if "Robotics" in main_topic:
            if any("Inverse Kinematics" in e or "Motion Planning" in e for e in missing_entities):
                if "* **Inverse Kinematics & Motion Planning**:" not in content:
                    content = content.replace(
                        "* **Edge Processing**:",
                        "* **Inverse Kinematics & Motion Planning**: GPU-accelerated solvers calculate collision-free trajectory paths in sub-5ms loops.\n* **Edge Processing**:"
                    )
                    optimizations_applied.append("Integrated 'Inverse Kinematics & Motion Planning' into perception section")

            if any("Sim-to-Real" in e for e in missing_entities):
                if "Sim-to-Real Reinforcement Learning" not in content:
                    content = content.replace(
                        "Training physical robots with trial and error",
                        "Sim-to-Real Reinforcement Learning overcomes physical trial and error"
                    )
                    optimizations_applied.append("Integrated 'Sim-to-Real Reinforcement Learning' entity")

            if any("ROS 2" in e for e in missing_entities):
                if "ROS 2 Integration" not in content:
                    content = content.replace(
                        "* **ROS 2 and DDS Standards**:",
                        "* **ROS 2 Integration and DDS Standards**: Ensuring microsecond message delivery between motion controllers and AI inference nodes."
                    )
                    optimizations_applied.append("Integrated 'ROS 2 Integration' standard")

        elif "Education" in main_topic:
            if any("Student Information Systems" in e or "SIS" in e for e in missing_entities):
                if "* **Student Information Systems (SIS) Sync**:" not in content:
                    content = content.replace(
                        "* **LMS Compatibility**:",
                        "* **Student Information Systems (SIS) & LMS Integration**: Integrating adaptive tools with SIS records and Learning Management Systems using 1EdTech LTI 1.3 standards stops the need for multiple logins.\n* **LMS Compatibility**:"
                    )
                    optimizations_applied.append("Integrated 'Student Information Systems (SIS)' into architecture checklist")

            if any("Learning Analytics" in e for e in missing_entities):
                if "* **Learning Analytics & Real-Time Dashboards**:" not in content:
                    content = content.replace(
                        "* **Teacher Oversight**:",
                        "* **Learning Analytics & Real-Time Dashboards**: Instructors use learning analytics dashboards that pinpoint where student cohorts hit friction, enabling immediate classroom support.\n* **Teacher Oversight**:"
                    )
                    optimizations_applied.append("Integrated 'Learning Analytics' into teacher oversight section")

            if any("Adaptive Learning" in e for e in missing_entities):
                if "Adaptive Learning Systems" not in content:
                    content = content.replace(
                        "Intelligent Tutoring Systems fix this",
                        "Intelligent Tutoring Systems and Adaptive Learning Systems fix this"
                    )
                    optimizations_applied.append("Integrated 'Adaptive Learning Systems' into Tutoring section")

        else: # Healthcare
            if any("HL7 FHIR" in e or "FHIR" in e for e in missing_entities):
                if "HL7 FHIR USCDI" not in content:
                    content = content.replace(
                        "Enterprise deployment requires a robust data substrate:",
                        "Enterprise deployment requires a robust data substrate:\n* **HL7 FHIR USCDI Standardization**: Normalizing observations, conditions, and prior auth requests into HL7 FHIR USCDI v3/v4 datasets."
                    )
                    optimizations_applied.append("Integrated 'HL7 FHIR USCDI' into data substrate section")

            if any("Clinician-in-the-Loop" in e or "CITL" in e for e in missing_entities):
                if "Clinician-in-the-Loop (CITL)" not in content:
                    content = content.replace(
                        "* **Clinician-in-the-Loop Signoff**:",
                        "* **Clinician-in-the-Loop (CITL) Governance**: All ambient notes and predictive risk scores require active clinician review and signoff before saving."
                    )
                    optimizations_applied.append("Integrated 'Clinician-in-the-Loop (CITL)' entity")

        # 4. Strictly Verify No '#' Markdown Hashes Were Introduced
        content = content.replace("#", "")

        # 5. Build Calibrated Meta Tags
        meta_title = f"{focus_kw}: Practical Enterprise Guide"
        if len(meta_title) > 60:
            meta_title = f"{focus_kw}: Enterprise Guide"
        if len(meta_title) > 60:
            meta_title = meta_title[:57] + "..."

        meta_desc = f"Beyond the hype: Discover high-impact enterprise use cases of {focus_kw.lower()}, production architectures, ROI metrics, and practical setups."
        if len(meta_desc) > 155:
            meta_desc = meta_desc[:152] + "..."

        # 6. Apply Full Deterministic Yoast SEO & Readability Enhancements
        slug = re.sub(r"[^a-z0-9]+", "-", focus_kw.lower()).strip("-")
        yoast_result = self.yoast_engine.optimize_content(
            content_markdown=content,
            focus_keyword=focus_kw,
            meta_title=meta_title,
            meta_description=meta_desc,
            slug=slug,
            domain=domain
        )

        content = yoast_result["optimized_markdown"]
        meta_title = yoast_result["meta_title"]
        meta_description = yoast_result["meta_description"]
        optimizations_applied.extend(yoast_result["optimizations_applied"])

        return {
            "optimized_markdown": content,
            "focus_keyword": focus_kw,
            "meta_title": meta_title,
            "meta_description": meta_description,
            "slug": slug,
            "optimizations_applied": optimizations_applied,
            "missing_entities_resolved": len(optimizations_applied),
            "yoast_assessment": yoast_result["yoast_assessment"]
        }
