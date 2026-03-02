import streamlit as st
import subprocess
import os
import tempfile
import re

st.set_page_config(page_title="Anurag's Resume Generator", page_icon="📄", layout="centered")
st.title("📄 JD → ATS Resume Generator")
st.caption("Rule-based • No API key needed • Tailored per JD type")

# ══════════════════════════════════════════════════════════════════════════════
# ROLE DETECTION
# ══════════════════════════════════════════════════════════════════════════════
ROLE_TYPES = {
    "sde": ["software engineer", "sde", "backend engineer", "software developer", "full stack",
            "frontend", "java developer", "python developer", "data structures", "algorithms",
            "system design", "microservices", "cloud", "devops", "lld", "hld", "oop",
            "object oriented", "scalable", "fault tolerant", "amazon", "google", "microsoft",
            "flipkart", "airbnb", "uber", "low level design"],
    "analytics": ["data analyst", "business analyst", "decision analytics", "analytics associate",
                  "insight", "reporting analyst", "bi analyst", "power bi", "tableau",
                  "data visualization", "zs", "consulting", "hypothesis", "exploratory data",
                  "eda", "scenario analysis", "kpi", "dashboard analyst"],
    "data_science": ["data scientist", "machine learning", "ml engineer", "ai", "deep learning",
                     "model", "classification", "regression", "nlp", "feature engineering",
                     "scikit", "tensorflow", "pytorch", "xgboost", "lgbm", "random forest",
                     "credit risk", "risk analytics", "fraud detection", "churn", "predictive",
                     "censora", "bajaj", "risk model", "logistic regression"],
    "entry": ["trainee", "apprentice", "fresher", "graduate", "associate engineer",
              "junior developer", "entry level", "campus hire", "tech support",
              "mindtree", "wipro", "infosys", "tcs", "cognizant", "capgemini", "accenture",
              "software trainee", "get program", "abap", "sap"],
    "consulting": ["consultant", "technology consultant", "it consultant", "associate consultant",
                   "ey", "deloitte", "pwc", "kpmg", "mckinsey", "bcg", "bain",
                   "servicenow", "enterprise platform", "platform consultant", "crm consultant"]
}

def detect_role(jd: str) -> str:
    jd_lower = jd.lower()
    scores = {role: 0 for role in ROLE_TYPES}
    for role, keywords in ROLE_TYPES.items():
        for kw in keywords:
            if kw in jd_lower:
                scores[role] += 1
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else "sde"

# ══════════════════════════════════════════════════════════════════════════════
# KEYWORD EXTRACTION
# ══════════════════════════════════════════════════════════════════════════════
ALL_KEYWORDS = [
    "python", "sql", "c#", ".net", "java", "javascript", "typescript", "react", "node",
    "api", "rest", "graphql", "microservices", "docker", "kubernetes", "aws", "azure", "gcp",
    "git", "ci/cd", "devops", "agile", "scrum", "backend", "frontend", "fullstack",
    "database", "mysql", "postgresql", "mongodb", "redis", "data structures", "algorithms",
    "power bi", "tableau", "excel", "machine learning", "deep learning", "ai", "oop",
    "servicenow", "salesforce", "crm", "erp", "sap", "abap", "object oriented",
    "testing", "debugging", "optimization", "automation", "integration", "migration",
    "documentation", "stakeholder", "communication", "leadership", "collaboration",
    "data validation", "data migration", "etl", "pipeline", "reporting", "dashboard",
    "system analysis", "business analysis", "enterprise", "production", "security",
    "compliance", "audit", "change management", "pandas", "numpy", "scikit", "tensorflow",
    "logistic regression", "random forest", "decision tree", "xgboost", "classification",
    "regression", "eda", "exploratory data analysis", "hypothesis testing", "statistics",
    "risk analytics", "credit risk", "fraud detection", "feature engineering", "oops",
    "data structures", "complexity", "scalable", "fault tolerant", "low latency",
    "java", "spring", "hibernate", "jdbc", "crud", "mvc", "layered architecture"
]

def extract_keywords(jd: str) -> list:
    jd_lower = jd.lower()
    found = []
    for kw in sorted(ALL_KEYWORDS, key=len, reverse=True):
        if kw in jd_lower and kw not in found:
            found.append(kw)
    words = re.findall(r'\b[A-Z][a-zA-Z]{3,}\b', jd)
    for w in words:
        if w.lower() not in [f.lower() for f in found]:
            found.append(w.lower())
    return list(dict.fromkeys(found))

# ══════════════════════════════════════════════════════════════════════════════
# EXPERIENCE TEMPLATES BY ROLE
# ══════════════════════════════════════════════════════════════════════════════

def get_experience(role: str, jd_keywords: list) -> list:
    jd_lower = " ".join(jd_keywords)

    if role == "sde":
        return [
            {
                "title": "Software Engineering Intern",
                "company": "Baker Hughes",
                "date": "Jan 2025 -- Jul 2025",
                "bullets": [
                    "Designed and optimized backend data pipelines to process large datasets efficiently in a production environment.",
                    "Refactored legacy \\textbf{SQL and Python} scripts into modular, object-oriented components improving performance.",
                    "Worked on data migration workflows with emphasis on data consistency, validation, and failure handling.",
                    "Debugged performance bottlenecks and collaborated with cross-functional teams to improve system reliability.",
                    "Authored technical documentation covering system design, data flows, and operational processes.",
                ]
            },
            {
                "title": "Research Intern",
                "company": "Pune Metro",
                "date": "Jun 2024 -- Jul 2024",
                "bullets": [
                    "Built data analysis and reporting solutions to monitor operational metrics using \\textbf{SQL and Python}.",
                    "Developed Python-based automation for data cleaning, transformation, and validation.",
                    "Performed exploratory analysis to identify trends, inefficiencies, and system-level patterns.",
                    "Presented technical insights to stakeholders using structured reports and dashboards.",
                ]
            },
            {
                "title": "Account Manager -- Technology Platforms",
                "company": "BeyondWalls",
                "date": "2025 -- Present",
                "bullets": [
                    "Supported engineering and product teams to monitor and optimize in-house \\textbf{CRM and platform workflows}.",
                    "Performed backend configuration, data validation, and system monitoring to ensure error-free execution.",
                    "Managed data flows, reporting logic, and documentation supporting business-critical systems.",
                    "Translated business requirements into actionable system tasks bridging technical and non-technical teams.",
                ]
            },
        ]

    elif role == "analytics":
        return [
            {
                "title": "Account Manager Analytics \\& Insights",
                "company": "BeyondWalls",
                "date": "2025 -- Present",
                "bullets": [
                    "Partner with internal and external stakeholders to identify business problems and analytics opportunities.",
                    "Perform data analysis and performance tracking on \\textbf{CRM and campaign datasets} to drive decision-making.",
                    "Translate analytical findings into structured insights, reports, and presentations for senior stakeholders.",
                    "Manage multiple client engagements simultaneously ensuring on-time delivery with a client-first mindset.",
                ]
            },
            {
                "title": "Data Analyst / .NET Intern",
                "company": "Baker Hughes",
                "date": "Jan 2025 -- Jul 2025",
                "bullets": [
                    "Applied analytical thinking to transform large operational datasets into structured data models for reporting.",
                    "Developed \\textbf{data processing and validation workflows} using Python and SQL to support analytics use cases.",
                    "Conducted data profiling, quality checks, and reconciliation to ensure accuracy and reliability of insights.",
                    "Documented methodologies, assumptions, and analytical logic to support transparency and reproducibility.",
                ]
            },
            {
                "title": "Research Intern Analytics",
                "company": "Pune Metro",
                "date": "Jun 2024 -- Jul 2024",
                "bullets": [
                    "Conducted exploratory data analysis on operational and power generation datasets using \\textbf{SQL and Python}.",
                    "Designed \\textbf{KPI dashboards using Power BI} to monitor system performance and efficiency.",
                    "Synthesized findings into clear insights and recommendations for technical and non-technical stakeholders.",
                ]
            },
        ]

    elif role == "data_science":
        return [
            {
                "title": "Account Manager Data \\& Risk Exposure",
                "company": "BeyondWalls",
                "date": "2025 -- Present",
                "bullets": [
                    "Analyzed customer lifecycle data including leads, conversions, and drop-offs to identify behavioral risk patterns.",
                    "Tracked campaign \\textbf{KPIs and performance metrics}, identifying early warning signals and optimization opportunities.",
                    "Prepared structured analytical reports and MOMs supporting data-driven decision-making.",
                    "Conducted secondary research to study customer segments, competitor positioning, and conversion risks.",
                ]
            },
            {
                "title": "Data / Software Engineering Intern",
                "company": "Baker Hughes",
                "date": "Jan 2025 -- Jul 2025",
                "bullets": [
                    "Worked on large-scale \\textbf{data migration and optimization} projects using SQL and Python.",
                    "Developed Python-based data preprocessing and validation pipelines using \\textbf{Pandas and NumPy}.",
                    "Applied OOP principles in C\\#/.NET to build modular and scalable data pipeline components.",
                    "Optimized SQL queries for performance, accuracy, and scalability in production environments.",
                ]
            },
            {
                "title": "Research Intern Data Analytics",
                "company": "Pune Metro Rail Corporation",
                "date": "Jun 2024 -- Jul 2024",
                "bullets": [
                    "Analyzed operational and power generation datasets using \\textbf{SQL and Python}.",
                    "Built \\textbf{Power BI dashboards} to monitor KPIs and operational performance.",
                    "Performed exploratory data analysis to identify trends and inefficiencies.",
                ]
            },
        ]

    elif role == "entry":
        return [
            {
                "title": "Account Manager Technology \\& Systems",
                "company": "BeyondWalls",
                "date": "2025 -- Present",
                "bullets": [
                    "Worked closely with internal engineering and product teams to monitor and support in-house CRM systems.",
                    "Performed data validation, reporting checks, and workflow analysis to ensure accurate system execution.",
                    "Prepared structured documentation, MOMs, and logs to support operational transparency.",
                    "Collaborated across teams strengthening communication, problem-solving, and ownership skills.",
                ]
            },
            {
                "title": "Software Engineering Intern",
                "company": "Baker Hughes",
                "date": "Jan 2025 -- Jul 2025",
                "bullets": [
                    "Assisted in developing and maintaining backend components using \\textbf{C\\#/.NET and Python}.",
                    "Applied Python scripting for data processing, validation, and automation tasks.",
                    "Wrote and optimized \\textbf{SQL queries} for data extraction, consistency checks, and reporting.",
                    "Debugged code issues and followed version control practices with structured documentation.",
                ]
            },
            {
                "title": "Research Intern Data \\& Systems Analysis",
                "company": "Pune Metro",
                "date": "Jun 2024 -- Jul 2024",
                "bullets": [
                    "Worked on operational datasets using \\textbf{SQL} and built Power BI dashboards for performance monitoring.",
                    "Performed exploratory data analysis and basic data quality checks.",
                    "Presented findings clearly to technical and non-technical stakeholders.",
                ]
            },
        ]

    else:  # consulting
        return [
            {
                "title": "Account Manager -- Technology Platforms",
                "company": "BeyondWalls",
                "date": "2025 -- Present",
                "bullets": [
                    "Worked closely with engineering, product, and operations teams to support CRM and platform workflows.",
                    "Assisted in backend configuration, data validation, and system monitoring ensuring error-free execution.",
                    "Managed data flows, reporting logic, and documentation supporting business-critical enterprise systems.",
                    "Acted as bridge between business users and technical teams translating requirements into system tasks.",
                ]
            },
            {
                "title": "Software Developer Intern (.NET)",
                "company": "Baker Hughes",
                "date": "Jan 2025 -- Jul 2025",
                "bullets": [
                    "Contributed to backend application development using \\textbf{C\\#/.NET} in an enterprise environment.",
                    "Refactored and optimized backend logic and \\textbf{SQL queries} to improve performance and reliability.",
                    "Implemented Python scripts for data processing, automation, and validation workflows.",
                    "Assisted with testing, debugging, change documentation, and production support activities.",
                ]
            },
            {
                "title": "Research Intern -- Systems \\& Data Analytics",
                "company": "Pune Metro",
                "date": "Jun 2024 -- Jul 2024",
                "bullets": [
                    "Performed systems analysis and data exploration on operational and power generation datasets.",
                    "Built structured reports and dashboards using \\textbf{SQL and Power BI}.",
                    "Documented analytical logic and findings for cross-functional consumption.",
                ]
            },
        ]

# ══════════════════════════════════════════════════════════════════════════════
# PROJECTS BY ROLE
# ══════════════════════════════════════════════════════════════════════════════
ALL_PROJECTS = {
    "sde": [
        {
            "title": "Data Migration and SQL Optimization System",
            "date": "Jan 2025 -- Apr 2025",
            "bullets": [
                "Designed a modular data migration framework using \\textbf{C\\# and Python} applying object-oriented design principles.",
                "Optimized complex SQL queries and indexing strategies reducing execution time by \\textbf{30\\%}.",
                "Implemented automated validation checks and error handling to ensure fault-tolerant data movement.",
                "Built reusable components to support scalability and future system extensions.",
            ]
        },
        {
            "title": "Credit Card Fraud Detection System",
            "date": "Nov 2024 -- Dec 2024",
            "bullets": [
                "Built an end-to-end fraud detection pipeline using \\textbf{Python} with clear separation of concerns via OOP.",
                "Applied classification algorithms on imbalanced datasets and evaluated models using precision-recall metrics.",
                "Processed large transaction datasets efficiently using optimized data structures.",
                "Visualized system outputs to support debugging, monitoring, and model evaluation.",
            ]
        },
    ],
    "analytics": [
        {
            "title": "Customer Behavior and Retention Analysis",
            "date": "",
            "bullets": [
                "Applied hypothesis-driven exploratory data analysis using \\textbf{Python (Pandas, NumPy)}.",
                "Identified key behavioral drivers and patterns impacting customer outcomes.",
                "Translated analysis into clear insights and scenario-based recommendations for stakeholders.",
            ]
        },
        {
            "title": "Data Migration and Data Quality Analytics",
            "date": "",
            "bullets": [
                "Analyzed large datasets during migration to identify inconsistencies and data quality risks.",
                "Wrote optimized \\textbf{SQL queries} for reconciliation, validation, and reporting.",
                "Automated data quality checks using \\textbf{Python} to improve reliability and efficiency.",
            ]
        },
    ],
    "data_science": [
        {
            "title": "Customer Churn Prediction -- Binary Classification",
            "date": "",
            "bullets": [
                "Built binary classification models using \\textbf{Logistic Regression, Decision Trees, and Random Forest}.",
                "Performed feature engineering, missing value treatment, and outlier handling using Python.",
                "Evaluated models using \\textbf{ROC-AUC, Precision, Recall, and KS statistics}.",
                "Interpreted model outputs to recommend actionable customer retention strategies.",
            ]
        },
        {
            "title": "Credit Card Fraud Detection",
            "date": "",
            "bullets": [
                "Developed \\textbf{machine learning models} on imbalanced datasets for fraud detection.",
                "Used Python (Scikit-learn, Pandas, NumPy) for data preprocessing and modeling.",
                "Implemented threshold tuning and model monitoring techniques.",
                "Visualized performance metrics for business interpretation.",
            ]
        },
    ],
    "entry": [
        {
            "title": "Data Migration and Validation Project",
            "date": "",
            "bullets": [
                "Assisted in migrating structured datasets using \\textbf{SQL and backend logic}.",
                "Validated data accuracy across systems using Python scripts.",
                "Maintained logs and documentation for traceability and audits.",
            ]
        },
        {
            "title": "Backend Application -- Programming Fundamentals",
            "date": "",
            "bullets": [
                "Developed backend modules using \\textbf{Java} following OOP principles.",
                "Implemented CRUD operations and basic API logic.",
                "Debugged and tested components to ensure functional correctness.",
            ]
        },
    ],
    "consulting": [
        {
            "title": "Data Migration and Backend Optimization Project",
            "date": "",
            "bullets": [
                "Migrated structured datasets across environments using \\textbf{SQL} and backend logic.",
                "Optimized queries and backend scripts to improve execution efficiency.",
                "Ensured data integrity through validation checks and reconciliation processes.",
                "Maintained technical documentation for audit and handover.",
            ]
        },
        {
            "title": "Backend Application Development Project",
            "date": "",
            "bullets": [
                "Developed backend modules using \\textbf{C\\#/.NET} following enterprise coding standards.",
                "Implemented database interactions and basic API endpoints.",
                "Performed unit testing, debugging, and documentation.",
            ]
        },
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
# SKILLS BY ROLE
# ══════════════════════════════════════════════════════════════════════════════
SKILLS_BY_ROLE = {
    "sde": [
        ("Programming Languages", "Python, C++, C\\#, Java, SQL"),
        ("Computer Science", "Data Structures, Algorithms, OOP, Complexity Analysis"),
        ("Backend \\& Databases", "MySQL, Relational Databases, Query Optimization"),
        ("Engineering Practices", "Debugging, Code Reviews, CI/CD basics, Technical Documentation"),
        ("Tools", "Git, Power BI, Pandas, NumPy"),
    ],
    "analytics": [
        ("Programming \\& Analytics", "Python, SQL, R (basic exposure)"),
        ("Statistical \\& Analytical Methods", "Exploratory Data Analysis, Hypothesis Testing, Descriptive Statistics, Scenario Analysis"),
        ("Data Visualization", "Power BI, Data Storytelling, Insight Communication"),
        ("Business \\& Decision Analytics", "Problem Structuring, Stakeholder Management, Client-Facing Analytics"),
        ("Professional Skills", "Communication, Presentation, Attention to Detail, Team Collaboration"),
    ],
    "data_science": [
        ("Programming Languages", "Python, SQL, C\\#, Java"),
        ("Machine Learning", "Logistic Regression, Decision Trees, Random Forest, Gradient Boosting (XGBoost/LightGBM)"),
        ("Libraries \\& Tools", "Scikit-learn, Pandas, NumPy, SciPy, Power BI"),
        ("Risk Analytics", "Binary Classification, Model Evaluation, Credit Risk Concepts, Portfolio Monitoring"),
        ("Data Skills", "Data Cleaning, Feature Engineering, Statistical Modeling, Reporting"),
    ],
    "entry": [
        ("Programming Languages", "C\\#, Python, Java, SQL"),
        ("Core Concepts", "Object-Oriented Programming (OOP), Programming Fundamentals"),
        ("Data \\& Reporting", "SQL Queries, Data Validation, Power BI, Dashboards"),
        ("Development Practices", "Debugging, Unit Testing (Basic), Documentation, Git"),
        ("Professional Skills", "Problem Solving, Team Collaboration, Communication, Willingness to Learn"),
    ],
    "consulting": [
        ("Backend \\& Programming", "\\textbf{C\\#/.NET, Python, SQL}"),
        ("Platform \\& Systems", "ServiceNow (Foundational), CRM Platforms, Enterprise Systems"),
        ("Data \\& Integration", "SQL Databases, API Integration, Data Validation, Data Migration"),
        ("Development Practices", "System Analysis, Backend Optimization, Debugging, Documentation"),
        ("Enterprise Practices", "Change Management, Secure Coding Awareness, Production Support"),
        ("Professional Skills", "Stakeholder Communication, Cross-Functional Collaboration, Attention to Detail"),
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
# SUMMARIES BY ROLE
# ══════════════════════════════════════════════════════════════════════════════
def build_summary(role: str, jd_keywords: list, jd_text: str) -> str:
    jd_lower = jd_text.lower()
    tech = [k for k in jd_keywords if k in ALL_KEYWORDS][:4]
    tech_str = ", ".join([t.upper() if len(t) <= 4 else t.title() for t in tech]) if tech else "C\\#/.NET, Python, SQL"

    # Detect specific company/role hints for extra personalization
    company_hint = ""
    if "amazon" in jd_lower: company_hint = " Seeking an SDE-I role at Amazon to build scalable, fault-tolerant systems that directly impact customers at scale."
    elif "zs" in jd_lower: company_hint = " Highly motivated, client-focused, and well-suited for a fast-paced analytics consulting environment."
    elif "censora" in jd_lower or "regulated" in jd_lower: company_hint = " Eager to contribute to enterprise-scale analytics initiatives in a regulated, data-driven environment."
    elif "bajaj" in jd_lower or "credit risk" in jd_lower: company_hint = " Seeking to contribute to Risk Analytics and Credit Risk Modeling in a data-driven financial environment."

    if role == "sde":
        return (f"Software Engineering graduate with strong foundations in data structures, algorithms, "
                f"object-oriented programming, and relational databases. Hands-on experience designing backend systems, "
                f"optimizing SQL workflows, and building automation pipelines using \\textbf{{Python, C++, C\\#, and SQL}}. "
                f"Demonstrated ownership across the software development lifecycle including design, implementation, debugging, and documentation."
                + company_hint)

    elif role == "analytics":
        return (f"Decision Analytics and Business Analytics professional with hands-on experience applying statistical analysis, "
                f"exploratory data analysis (EDA), and data-driven problem solving to address complex business challenges. "
                f"Strong proficiency in \\textbf{{Python and SQL}}, with experience translating raw data into actionable insights, "
                f"scenario analyses, and executive-ready recommendations. Proven ability to collaborate with cross-functional teams "
                f"and communicate insights clearly to stakeholders."
                + company_hint)

    elif role == "data_science":
        return (f"Data-driven Risk Analytics and Data Science professional with hands-on experience in \\textbf{{Python and SQL}} "
                f"for statistical modeling, binary classification, and large-scale data analysis. "
                f"Strong foundation in machine learning algorithms including Logistic Regression, Decision Trees, and Random Forest. "
                f"Experienced in model development, performance monitoring, reporting, and translating analytical insights into business decisions."
                + company_hint)

    elif role == "entry":
        return (f"Motivated Software Development Apprentice with a strong foundation in programming fundamentals, "
                f"object-oriented programming, and data handling. Hands-on experience with \\textbf{{C\\#, Python, Java, and SQL}} "
                f"through internships and real-world projects. Comfortable assisting in coding, debugging, data validation, reporting, and documentation. "
                f"Quick learner with a collaborative mindset, eager to develop skills across software development and automation."
                + company_hint)

    else:  # consulting
        return (f"Backend and Platform-focused Software Developer with hands-on experience in system analysis, "
                f"application development, data integration, and backend optimization. "
                f"Strong proficiency in \\textbf{{C\\#/.NET, Python, and SQL}}, with practical exposure to API integration, "
                f"database-driven applications, documentation, and production support. "
                f"Highly adaptable and eager to build deep expertise in enterprise platforms within a global consulting environment."
                + company_hint)

# ══════════════════════════════════════════════════════════════════════════════
# LEADERSHIP (used for SDE/big tech roles)
# ══════════════════════════════════════════════════════════════════════════════
LEADERSHIP_SECTION = r"""
\section{Leadership \& Activities}
\begin{joblong}{Production and Backstage Head -- COEP Drama and Films Club}{Apr 2023 -- May 2025}
  \item Led cross-functional teams of 20+ members and managed end-to-end production operations under tight deadlines.
  \item Strengthened leadership, coordination, and stakeholder communication skills.
\end{joblong}
\begin{joblong}{Operations and Logistics Coordinator -- Pune Startup Fest}{Oct 2022 -- Mar 2023}
  \item Coordinated logistics and communication for a large-scale 500+ attendee technical event.
  \item Managed vendor relationships, scheduling, and on-ground execution.
\end{joblong}
"""

# ══════════════════════════════════════════════════════════════════════════════
# LATEX BUILDER
# ══════════════════════════════════════════════════════════════════════════════
LATEX_PREAMBLE = r"""\documentclass[a4paper,11pt]{article}
\usepackage{parskip}
\usepackage{xcolor}
\usepackage[scale=0.92, top=0.65cm, bottom=0.65cm]{geometry}
\usepackage{tabularx}
\usepackage{enumitem}
\usepackage{titlesec}
\usepackage{hyperref}
\usepackage{fontawesome5}
\usepackage{array}

\newcolumntype{C}{>{\centering\arraybackslash}X}
\definecolor{linkcolour}{rgb}{0,0.2,0.6}
\hypersetup{colorlinks=true, urlcolor=linkcolour}
\titleformat{\section}{\Large\scshape\raggedright}{}{0em}{}[\titlerule]
\titlespacing{\section}{0pt}{3pt}{3pt}

\newenvironment{joblong}[2]{
\begin{tabularx}{\linewidth}{@{}l X r@{}}
\textbf{#1} & & #2 \\[1pt]
\end{tabularx}
\begin{itemize}[leftmargin=1em, itemsep=1pt, topsep=1pt, label=--]
}{
\end{itemize}
}
\begin{document}
\pagestyle{empty}
"""

def build_latex(role: str, jd_text: str, jd_keywords: list) -> str:
    lines = [LATEX_PREAMBLE]

    # ── Header ────────────────────────────────────────────────────────────────
    lines.append(r"""
\begin{tabularx}{\linewidth}{@{} C @{}}
{\Huge \textbf{ANURAG LOKHANDE}} \\[3pt]
\href{tel:+917709271496}{\faMobile\ +91 77092 71496} \quad | \quad
\href{mailto:lokhandeag21.elec@coeptech.ac.in}{\faEnvelope\ lokhandeag21.elec@coeptech.ac.in} \quad | \quad
\href{https://www.linkedin.com/in/anurag-lokhande-180a5a230/}{\faLinkedin\ LinkedIn}
\end{tabularx}
""")

    # ── Summary ───────────────────────────────────────────────────────────────
    lines.append(r"\section{Professional Summary}")
    lines.append(build_summary(role, jd_keywords, jd_text))
    lines.append("")

    # ── Experience ────────────────────────────────────────────────────────────
    exp_label = "Work Experience" if role == "sde" else "Professional Experience"
    lines.append(f"\\section{{{exp_label}}}")
    experience = get_experience(role, jd_keywords)
    for exp in experience:
        lines.append(f"\\begin{{joblong}}{{{exp['title']} --- {exp['company']}}}{{{exp['date']}}}")
        for b in exp["bullets"]:
            lines.append(f"  \\item {b}")
        lines.append(r"\end{joblong}")
        lines.append("")

    # ── Projects ──────────────────────────────────────────────────────────────
    proj_label = "Projects" if role in ["sde", "entry"] else "Selected Analytics Projects" if role == "analytics" else "Key Projects" if role == "data_science" else "Selected Technical Projects"
    lines.append(f"\\section{{{proj_label}}}")
    projects = ALL_PROJECTS.get(role, ALL_PROJECTS["consulting"])
    for proj in projects:
        date_str = proj.get("date", "")
        lines.append(f"\\begin{{joblong}}{{{proj['title']}}}{{{date_str}}}")
        for b in proj["bullets"]:
            lines.append(f"  \\item {b}")
        lines.append(r"\end{joblong}")
        lines.append("")

    # ── Education ─────────────────────────────────────────────────────────────
    lines.append(r"\section{Education}")
    lines.append(r"""\begin{tabularx}{\linewidth}{@{}l C r@{}}
\textbf{B.Tech in Electrical Engineering} & \textbf{COEP Technological University, Pune} & 2021 -- 2025 \\
\end{tabularx}
""")

    # ── Skills ────────────────────────────────────────────────────────────────
    skill_label = "Technical Skills" if role != "analytics" else "Skills"
    lines.append(f"\\section{{{skill_label}}}")
    lines.append(r"\begin{tabularx}{\linewidth}{@{}l X@{}}")
    skills = SKILLS_BY_ROLE.get(role, SKILLS_BY_ROLE["consulting"])

    # Inject top JD keywords into first skill row
    top_jd_tech = [k for k in jd_keywords if k in ALL_KEYWORDS][:3]
    for i, (label, val) in enumerate(skills):
        lines.append(f"\\textbf{{{label}:}} & {val} \\\\")
    lines.append(r"\end{tabularx}")
    lines.append("")

    # ── Leadership (SDE / big tech only) ─────────────────────────────────────
    if role == "sde":
        lines.append(LEADERSHIP_SECTION)

    lines.append(r"\end{document}")
    return "\n".join(lines)

# ══════════════════════════════════════════════════════════════════════════════
# PDF COMPILER
# ══════════════════════════════════════════════════════════════════════════════
def compile_to_pdf(latex: str):
    with tempfile.TemporaryDirectory() as tmpdir:
        tex_path = os.path.join(tmpdir, "resume.tex")
        pdf_path = os.path.join(tmpdir, "resume.pdf")
        with open(tex_path, "w", encoding="utf-8") as f:
            f.write(latex)
        for _ in range(2):
            result = subprocess.run(
                ["pdflatex", "-interaction=nonstopmode", "-output-directory", tmpdir, tex_path],
                capture_output=True, text=True
            )
        if os.path.exists(pdf_path):
            with open(pdf_path, "rb") as f:
                return f.read(), None
        return None, result.stdout[-3000:]

# ══════════════════════════════════════════════════════════════════════════════
# ROLE DISPLAY NAMES
# ══════════════════════════════════════════════════════════════════════════════
ROLE_DISPLAY = {
    "sde": "💻 SDE / Backend Engineer",
    "analytics": "📊 Data Analytics / BI",
    "data_science": "🤖 Data Science / Risk / ML",
    "entry": "🎓 Entry Level / Trainee",
    "consulting": "🏢 IT Consulting / Enterprise",
}

# ══════════════════════════════════════════════════════════════════════════════
# UI
# ══════════════════════════════════════════════════════════════════════════════
jd_input = st.text_area(
    "📋 Paste the Job Description here",
    height=300,
    placeholder="Paste the full job description including skills, responsibilities, and qualifications..."
)

col1, col2 = st.columns([2, 1])
with col1:
    generate_btn = st.button("✨ Generate Resume", type="primary", use_container_width=True)
with col2:
    show_latex = st.checkbox("Show LaTeX code", value=False)

if "latex" not in st.session_state:
    st.session_state.latex = None
if "pdf_bytes" not in st.session_state:
    st.session_state.pdf_bytes = None
if "role" not in st.session_state:
    st.session_state.role = None
if "keywords" not in st.session_state:
    st.session_state.keywords = []

if generate_btn:
    if not jd_input.strip():
        st.warning("⚠️ Please paste a Job Description.")
    else:
        with st.spinner("🔍 Analyzing JD..."):
            keywords = extract_keywords(jd_input)
            role = detect_role(jd_input)
            st.session_state.keywords = keywords
            st.session_state.role = role

        with st.spinner("📝 Building tailored resume..."):
            latex = build_latex(role, jd_input, keywords)
            st.session_state.latex = latex

        with st.spinner("📄 Compiling PDF..."):
            check = subprocess.run(["which", "pdflatex"], capture_output=True)
            if check.returncode != 0:
                st.session_state.pdf_bytes = None
            else:
                pdf, err = compile_to_pdf(latex)
                st.session_state.pdf_bytes = pdf
                if err:
                    st.error("LaTeX error:")
                    st.code(err)

if st.session_state.latex:
    st.success("✅ Resume generated!")

    # Show detected role
    if st.session_state.role:
        st.info(f"🎯 **Detected Role Type:** {ROLE_DISPLAY.get(st.session_state.role, st.session_state.role)}")

    # Show top keywords
    if st.session_state.keywords:
        top_kw = st.session_state.keywords[:15]
        st.caption(f"**Keywords matched:** {', '.join(top_kw)}")

    if st.session_state.pdf_bytes:
        st.download_button(
            label="⬇️ Download Resume (PDF)",
            data=st.session_state.pdf_bytes,
            file_name="Anurag_Lokhande_Resume.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )
    else:
        st.warning("⚠️ pdflatex not available on this server.")
        st.info("👉 Copy the LaTeX code below → paste at **overleaf.com** → Download PDF")

    if show_latex or not st.session_state.pdf_bytes:
        st.subheader("📝 LaTeX Source Code")
        st.code(st.session_state.latex, language="latex")
        st.download_button(
            label="⬇️ Download LaTeX (.tex)",
            data=st.session_state.latex,
            file_name="Anurag_Lokhande_Resume.tex",
            mime="text/plain",
            use_container_width=True
        )
