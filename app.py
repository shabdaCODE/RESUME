import streamlit as st
import subprocess
import os
import tempfile
import re
import requests

st.set_page_config(page_title="Anurag's Resume Generator", page_icon="📄", layout="centered")
st.title("📄 JD → ATS Resume Generator")
st.caption("Rule-based • No API key needed • ATS-optimized")

# ══════════════════════════════════════════════════════════════════════════════
# ROLE DETECTION
# ══════════════════════════════════════════════════════════════════════════════
ROLE_TYPES = {
    "sde": ["software engineer", "sde", "backend engineer", "software developer", "full stack",
            "frontend", "java developer", "python developer", "data structures", "algorithms",
            "system design", "microservices", "cloud", "devops", "lld", "hld", "oop",
            "object oriented", "scalable", "fault tolerant", "amazon", "google", "microsoft",
            "flipkart", "airbnb", "uber", "low level design", "spring", "react", "angular",
            "kubernetes", "docker", "rest api", "restful"],
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
    "python", "sql", "c#", ".net", "java", "javascript", "typescript", "react", "angular",
    "node", "spring", "hibernate", "jdbc", "api", "rest", "restful", "graphql",
    "microservices", "docker", "kubernetes", "aws", "azure", "gcp", "cloud",
    "git", "github", "ci/cd", "jenkins", "github actions", "gitlab", "devops",
    "agile", "scrum", "backend", "frontend", "fullstack", "database", "mysql",
    "postgresql", "mongodb", "redis", "data structures", "algorithms", "oop",
    "object oriented", "power bi", "tableau", "excel", "machine learning", "deep learning",
    "ai", "artificial intelligence", "servicenow", "salesforce", "crm", "erp", "sap", "abap",
    "testing", "unit testing", "debugging", "optimization", "automation", "integration",
    "migration", "documentation", "stakeholder", "communication", "leadership", "collaboration",
    "teamwork", "reliable", "ownership", "accountability", "data validation", "data migration",
    "etl", "pipeline", "reporting", "dashboard", "system analysis", "business analysis",
    "enterprise", "production", "security", "compliance", "audit", "change management",
    "pandas", "numpy", "scikit", "tensorflow", "logistic regression", "random forest",
    "decision tree", "xgboost", "classification", "regression", "eda",
    "exploratory data analysis", "hypothesis testing", "statistics", "risk analytics",
    "credit risk", "fraud detection", "feature engineering", "scalable", "fault tolerant",
    "low latency", "high availability", "crud", "mvc", "layered architecture",
    "html", "css", "linux", "bash", "shell", "nosql", "spark", "hadoop", "kafka"
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

def extract_exact_tech(jd: str) -> dict:
    """Extract exact tech stack from JD — used to inject ATS keywords into skills."""
    jd_lower = jd.lower()
    detected = {"languages": [], "frameworks": [], "devops": [], "cloud": [], "databases": [], "soft": []}

    lang_map  = {"java":"Java","kotlin":"Kotlin","python":"Python","c#":"C#","c++":"C++",
                 "javascript":"JavaScript","typescript":"TypeScript","go":"Go","scala":"Scala",
                 "sql":"SQL","shell":"Shell/Bash","bash":"Shell/Bash","php":"PHP","ruby":"Ruby"}
    fw_map    = {"spring boot":"Spring Boot","spring":"Spring",".net":".NET","react":"React",
                 "angular":"Angular","vue":"Vue.js","django":"Django","flask":"Flask",
                 "fastapi":"FastAPI","node":"Node.js","hibernate":"Hibernate","pandas":"Pandas",
                 "numpy":"NumPy","scikit":"Scikit-learn","tensorflow":"TensorFlow",
                 "pytorch":"PyTorch","xgboost":"XGBoost","tekton":"Tekton"}
    devops_map= {"kubernetes":"Kubernetes","k8s":"Kubernetes","docker":"Docker",
                 "jenkins":"Jenkins","github actions":"GitHub Actions","gitlab ci":"GitLab CI",
                 "ci/cd":"CI/CD","terraform":"Terraform","helm":"Helm","git":"Git",
                 "linux":"Linux","devops":"DevOps","agile":"Agile","scrum":"Scrum",
                 "dora":"DORA Metrics"}
    cloud_map = {"aws":"AWS","amazon web services":"AWS","azure":"Azure","gcp":"GCP",
                 "google cloud":"GCP","s3":"AWS S3","lambda":"AWS Lambda","ec2":"AWS EC2"}
    db_map    = {"mysql":"MySQL","postgresql":"PostgreSQL","postgres":"PostgreSQL",
                 "mongodb":"MongoDB","redis":"Redis","elasticsearch":"Elasticsearch",
                 "cassandra":"Cassandra","dynamodb":"DynamoDB","sql server":"SQL Server",
                 "nosql":"NoSQL","oracle":"Oracle DB"}
    soft_map  = {"collaboration":"Collaboration","teamwork":"Teamwork",
                 "communication":"Communication","leadership":"Leadership",
                 "ownership":"Ownership","accountability":"Accountability",
                 "cross-functional":"Cross-Functional Collaboration",
                 "stakeholder":"Stakeholder Management","problem.solv":"Problem Solving"}

    for k, v in lang_map.items():
        if k in jd_lower and v not in detected["languages"]: detected["languages"].append(v)
    for k, v in fw_map.items():
        if k in jd_lower and v not in detected["frameworks"]: detected["frameworks"].append(v)
    for k, v in devops_map.items():
        if k in jd_lower and v not in detected["devops"]: detected["devops"].append(v)
    for k, v in cloud_map.items():
        if k in jd_lower and v not in detected["cloud"]: detected["cloud"].append(v)
    for k, v in db_map.items():
        if k in jd_lower and v not in detected["databases"]: detected["databases"].append(v)
    for k, v in soft_map.items():
        if re.search(k, jd_lower) and v not in detected["soft"]: detected["soft"].append(v)
    return detected

def build_dynamic_skills(role: str, jd_text: str, jd_keywords: list) -> list:
    """Always put JD-exact keywords first row for ATS, then role skills below."""
    base  = get_skills(role, jd_text, jd_keywords)
    tech  = extract_exact_tech(jd_text)

    # Build one combined JD tech string grouped by category
    jd_parts = []
    if tech["languages"]:  jd_parts.append(", ".join(tech["languages"][:6]))
    if tech["frameworks"]: jd_parts.append(", ".join(tech["frameworks"][:4]))
    if tech["devops"]:     jd_parts.append(", ".join(tech["devops"][:4]))
    if tech["cloud"]:      jd_parts.append(", ".join(tech["cloud"][:3]))
    if tech["databases"]:  jd_parts.append(", ".join(tech["databases"][:3]))

    # Soft skills row — blend JD soft skills with defaults
    soft_jd  = tech.get("soft", [])
    soft_str = ", ".join(soft_jd[:4]) if soft_jd else "Collaboration, Teamwork, Ownership"
    soft_str += ", Communication, Attention to Detail, Problem Solving"

    # Assemble: JD row first, then base rows, replace Professional Skills at end
    final = []
    if jd_parts:
        final.append(("JD-Matched Tech Stack", " $|$ ".join(jd_parts)))
    for label, val in base:
        if "Professional" not in label and "Soft" not in label:
            final.append((label, val))
    final.append(("Professional Skills", soft_str))
    return final[:8]  # max 8 rows to stay on 1 page

# ══════════════════════════════════════════════════════════════════════════════
# EXPERIENCE TEMPLATES BY ROLE
# (Improvements: quantifiable achievements, active voice, specific tools)
# ══════════════════════════════════════════════════════════════════════════════
def get_experience(role: str, jd_keywords: list, jd_text: str) -> list:
    jd_lower = jd_text.lower()

    # Detect specific tools from JD to inject
    has_aws     = any(k in jd_lower for k in ["aws", "amazon web services"])
    has_azure   = any(k in jd_lower for k in ["azure", "microsoft azure"])
    has_docker  = "docker" in jd_lower
    has_k8s     = any(k in jd_lower for k in ["kubernetes", "k8s"])
    has_react   = "react" in jd_lower
    has_git     = "git" in jd_lower
    has_java    = "java" in jd_lower
    has_rest    = any(k in jd_lower for k in ["rest", "api", "restful"])
    has_cicd    = any(k in jd_lower for k in ["ci/cd", "jenkins", "github actions", "gitlab"])
    has_collab  = any(k in jd_lower for k in ["collaboration", "teamwork", "cross-functional"])
    has_agile   = any(k in jd_lower for k in ["agile", "scrum", "sprint"])

    cloud_str = "AWS" if has_aws else ("Azure" if has_azure else "cloud platforms")
    cicd_str  = "Jenkins/GitHub Actions" if has_cicd else "CI/CD pipelines"

    if role == "sde":
        bh_bullets = [
            "Designed and optimized backend data pipelines processing \\textbf{50K+ records/day} in a production environment.",
            "Refactored legacy \\textbf{SQL and Python} scripts into modular, object-oriented components, reducing execution time by \\textbf{30\\%}.",
            "Worked on data migration workflows ensuring \\textbf{100\\% data consistency} through validation and failure handling.",
            "Debugged performance bottlenecks, improving system reliability and reducing error rate by \\textbf{40\\%}.",
            "Collaborated with cross-functional teams to ship \\textbf{3 production features} on schedule.",
            f"Followed \\textbf{{{'Git' if has_git else 'version control'} and {cicd_str}}} workflows maintaining clean, reviewable code.",
        ]
        if has_rest:
            bh_bullets.append("Developed and integrated \\textbf{REST API} endpoints for internal data services.")
        if has_java:
            bh_bullets.append("Wrote clean, maintainable backend modules using \\textbf{Java} applying OOP and SOLID principles.")

        metro_bullets = [
            "Built \\textbf{Python-based automation} for data cleaning and transformation, reducing manual effort by \\textbf{60\\%}.",
            "Developed SQL-driven reporting solutions monitoring operational metrics across \\textbf{5+ metro stations}.",
            "Performed exploratory analysis identifying \\textbf{3 key inefficiencies}, leading to process improvements.",
            "Presented structured insights to stakeholders, improving report clarity and decision turnaround.",
        ]

        bw_bullets = [
            "Supported engineering and product teams to monitor CRM workflows, reducing resolution time by \\textbf{25\\%}.",
            "Performed data validation and system monitoring ensuring \\textbf{99\\%+ error-free execution}.",
            "Managed reporting logic and documentation for \\textbf{5+ business-critical systems}.",
            "Translated business requirements into actionable system tasks bridging technical and non-technical teams.",
        ]
        if has_agile:
            bw_bullets.append("Participated in \\textbf{Agile/Scrum} ceremonies, contributing to sprint planning and retrospectives.")

        return [
            {"title": "Software Engineering Intern", "company": "Baker Hughes",
             "date": "Jan 2025 -- Jul 2025", "bullets": bh_bullets[:5]},
            {"title": "Research Intern", "company": "Pune Metro",
             "date": "Jun 2024 -- Jul 2024", "bullets": metro_bullets[:4]},
            {"title": "Account Manager -- Technology Platforms", "company": "BeyondWalls",
             "date": "2025 -- Present", "bullets": bw_bullets[:4]},
        ]

    elif role == "analytics":
        return [
            {
                "title": "Account Manager Analytics \\& Insights", "company": "BeyondWalls",
                "date": "2025 -- Present",
                "bullets": [
                    "Analyzed \\textbf{CRM and campaign datasets} across \\textbf{10+ client accounts} to surface actionable business insights.",
                    "Translated analytical findings into structured reports and executive-ready presentations for senior stakeholders.",
                    "Tracked \\textbf{20+ KPIs} monthly, identifying performance gaps and optimization opportunities.",
                    "Managed multiple client engagements simultaneously, ensuring \\textbf{100\\% on-time delivery}.",
                    "Applied a client-first mindset to balance competing priorities in a fast-moving consulting environment.",
                ]
            },
            {
                "title": "Data Analyst / .NET Intern", "company": "Baker Hughes",
                "date": "Jan 2025 -- Jul 2025",
                "bullets": [
                    "Transformed \\textbf{100K+ row operational datasets} into structured data models for reporting and analysis.",
                    "Built \\textbf{Python and SQL} validation workflows reducing data quality issues by \\textbf{35\\%}.",
                    "Conducted data profiling and reconciliation ensuring \\textbf{98\\%+ data accuracy} across systems.",
                    "Documented analytical methodologies and assumptions supporting transparency and reproducibility.",
                ]
            },
            {
                "title": "Research Intern Analytics", "company": "Pune Metro",
                "date": "Jun 2024 -- Jul 2024",
                "bullets": [
                    "Designed \\textbf{KPI dashboards in Power BI} monitoring system performance across \\textbf{5 stations}.",
                    "Conducted EDA on \\textbf{operational datasets} identifying \\textbf{3 key inefficiencies} in power consumption.",
                    "Synthesized findings into clear recommendations adopted by the management team.",
                ]
            },
        ]

    elif role == "data_science":
        return [
            {
                "title": "Account Manager Data \\& Risk Analytics", "company": "BeyondWalls",
                "date": "2025 -- Present",
                "bullets": [
                    "Analyzed customer lifecycle data across \\textbf{10K+ leads} to identify behavioral risk patterns and conversion risks.",
                    "Tracked \\textbf{campaign KPIs and performance metrics} identifying early warning signals for \\textbf{3 at-risk segments}.",
                    "Prepared structured analytical reports and risk summaries supporting data-driven decisions.",
                    "Conducted secondary research on \\textbf{5+ competitor segments} to support strategic positioning.",
                ]
            },
            {
                "title": "Data / Software Engineering Intern", "company": "Baker Hughes",
                "date": "Jan 2025 -- Jul 2025",
                "bullets": [
                    "Built \\textbf{Python data pipelines} (Pandas, NumPy) processing \\textbf{100K+ records} for ML-ready datasets.",
                    "Optimized \\textbf{SQL queries} reducing data extraction time by \\textbf{40\\%} in production environments.",
                    "Applied \\textbf{OOP principles in C\\#/.NET} to build modular, scalable data pipeline components.",
                    "Collaborated with cross-functional teams delivering \\textbf{3 deployment-ready analytical solutions}.",
                ]
            },
            {
                "title": "Research Intern Data Analytics", "company": "Pune Metro Rail Corporation",
                "date": "Jun 2024 -- Jul 2024",
                "bullets": [
                    "Performed EDA on \\textbf{operational datasets} identifying trends impacting \\textbf{15\\%} operational efficiency.",
                    "Built \\textbf{Power BI dashboards} monitoring \\textbf{10+ KPIs} for management-level decision making.",
                    "Automated data validation checks reducing manual QA effort by \\textbf{50\\%}.",
                ]
            },
        ]

    elif role == "entry":
        return [
            {
                "title": "Account Manager Technology \\& Systems", "company": "BeyondWalls",
                "date": "2025 -- Present",
                "bullets": [
                    "Supported engineering and product teams monitoring \\textbf{5+ CRM workflows} ensuring accurate execution.",
                    "Performed data validation and reporting checks achieving \\textbf{99\\%+ system accuracy}.",
                    "Prepared structured documentation and MOMs supporting operational transparency.",
                    "Collaborated across \\textbf{3 cross-functional teams} strengthening communication and problem-solving skills.",
                ]
            },
            {
                "title": "Software Engineering Intern", "company": "Baker Hughes",
                "date": "Jan 2025 -- Jul 2025",
                "bullets": [
                    "Developed and maintained backend components using \\textbf{C\\#/.NET and Python}.",
                    "Wrote and optimized \\textbf{SQL queries} reducing report generation time by \\textbf{25\\%}.",
                    "Applied \\textbf{Python scripting} for data processing and automation, eliminating \\textbf{5+ manual tasks}.",
                    "Debugged code issues and followed \\textbf{Git-based version control} with structured documentation.",
                ]
            },
            {
                "title": "Research Intern Data \\& Systems Analysis", "company": "Pune Metro",
                "date": "Jun 2024 -- Jul 2024",
                "bullets": [
                    "Built \\textbf{Power BI dashboards} monitoring performance metrics across \\textbf{5 operational stations}.",
                    "Performed data quality checks reducing reporting errors by \\textbf{30\\%}.",
                    "Presented findings clearly to both technical and non-technical stakeholders.",
                ]
            },
        ]

    else:  # consulting
        return [
            {
                "title": "Account Manager -- Technology Platforms", "company": "BeyondWalls",
                "date": "2025 -- Present",
                "bullets": [
                    "Supported \\textbf{CRM and enterprise platform workflows} across engineering, product, and operations teams.",
                    "Performed backend configuration and data validation ensuring \\textbf{99\\%+ error-free execution}.",
                    "Managed data flows and reporting logic for \\textbf{5+ business-critical systems}.",
                    "Acted as bridge between business users and technical teams, translating \\textbf{20+ requirements} into system tasks.",
                    "Prepared detailed MOMs and operational documentation aligned with \\textbf{enterprise standards}.",
                ]
            },
            {
                "title": "Software Developer Intern (.NET)", "company": "Baker Hughes",
                "date": "Jan 2025 -- Jul 2025",
                "bullets": [
                    "Developed backend modules using \\textbf{C\\#/.NET} reducing system processing time by \\textbf{30\\%}.",
                    "Refactored and optimized \\textbf{SQL queries} improving query performance by \\textbf{40\\%}.",
                    "Implemented \\textbf{Python automation scripts} eliminating \\textbf{5+ recurring manual tasks}.",
                    "Supported integration of \\textbf{3 data sources} ensuring consistency across enterprise systems.",
                ]
            },
            {
                "title": "Research Intern -- Systems \\& Data Analytics", "company": "Pune Metro",
                "date": "Jun 2024 -- Jul 2024",
                "bullets": [
                    "Built \\textbf{SQL and Power BI} dashboards monitoring \\textbf{10+ operational KPIs}.",
                    "Performed systems analysis identifying \\textbf{3 data inconsistencies} improving reporting accuracy.",
                    "Documented analytical logic and findings for cross-functional consumption.",
                ]
            },
        ]

# ══════════════════════════════════════════════════════════════════════════════
# PROJECTS BY ROLE (with quantifiable metrics)
# ══════════════════════════════════════════════════════════════════════════════
ALL_PROJECTS = {
    "sde": [
        {
            "title": "Data Migration and SQL Optimization System",
            "date": "Jan 2025 -- Apr 2025",
            "bullets": [
                "Designed a modular data migration framework using \\textbf{C\\# and Python} applying OOP and SOLID principles.",
                "Optimized complex \\textbf{SQL queries and indexing strategies}, reducing execution time by \\textbf{30\\%}.",
                "Implemented automated validation checks and error handling ensuring \\textbf{100\\% fault-tolerant data movement}.",
                "Built reusable components supporting scalability and adopted by \\textbf{2 additional teams}.",
            ]
        },
        {
            "title": "Credit Card Fraud Detection System",
            "date": "Nov 2024 -- Dec 2024",
            "bullets": [
                "Built end-to-end fraud detection pipeline using \\textbf{Python} achieving \\textbf{92\\% precision} on test data.",
                "Applied classification algorithms on imbalanced datasets evaluated using \\textbf{precision-recall and ROC-AUC}.",
                "Processed \\textbf{100K+ transaction records} efficiently using optimized data structures.",
                "Visualized system outputs to support debugging, monitoring, and model evaluation.",
            ]
        },
    ],
    "analytics": [
        {
            "title": "Customer Behavior and Retention Analysis",
            "date": "",
            "bullets": [
                "Applied hypothesis-driven EDA using \\textbf{Python (Pandas, NumPy)} on \\textbf{50K+ customer records}.",
                "Identified \\textbf{4 key behavioral drivers} impacting customer retention rates.",
                "Translated analysis into scenario-based recommendations adopted by the business team.",
            ]
        },
        {
            "title": "Data Quality and Migration Analytics",
            "date": "",
            "bullets": [
                "Analyzed \\textbf{100K+ row datasets} during migration identifying \\textbf{15\\%} data quality risks.",
                "Wrote optimized \\textbf{SQL queries} for reconciliation, validation, and reporting.",
                "Automated \\textbf{10+ data quality checks} using Python, reducing manual QA effort by \\textbf{50\\%}.",
            ]
        },
    ],
    "data_science": [
        {
            "title": "Customer Churn Prediction -- Binary Classification",
            "date": "",
            "bullets": [
                "Built classification models (\\textbf{Logistic Regression, Decision Trees, Random Forest}) achieving \\textbf{88\\% ROC-AUC}.",
                "Performed feature engineering and outlier handling on \\textbf{50K+ customer records} using Python.",
                "Evaluated models using \\textbf{ROC-AUC, Precision, Recall, and KS statistics}.",
                "Interpreted model outputs recommending retention strategies reducing predicted churn by \\textbf{18\\%}.",
            ]
        },
        {
            "title": "Credit Card Fraud Detection",
            "date": "",
            "bullets": [
                "Developed ML models on \\textbf{imbalanced datasets} achieving \\textbf{92\\% precision} for fraud detection.",
                "Used \\textbf{Python (Scikit-learn, Pandas, NumPy)} for preprocessing, modeling, and evaluation.",
                "Implemented threshold tuning and monitoring improving \\textbf{false positive rate by 20\\%}.",
            ]
        },
    ],
    "entry": [
        {
            "title": "Data Migration and Validation Project",
            "date": "",
            "bullets": [
                "Migrated \\textbf{50K+ records} across environments using SQL and backend logic with \\textbf{100\\% accuracy}.",
                "Automated \\textbf{8 validation checks} using Python scripts reducing manual effort by \\textbf{40\\%}.",
                "Maintained traceability logs and documentation for audit purposes.",
            ]
        },
        {
            "title": "Java-Based Backend Application",
            "date": "",
            "bullets": [
                "Developed backend application using \\textbf{Java} with layered architecture (Controller, Service, DAO).",
                "Implemented \\textbf{CRUD operations} using SQL and relational database concepts.",
                "Applied \\textbf{OOP principles} (encapsulation, inheritance, abstraction) ensuring maintainable code.",
            ]
        },
    ],
    "consulting": [
        {
            "title": "Data Migration and Backend Optimization Project",
            "date": "",
            "bullets": [
                "Migrated \\textbf{100K+ records} across enterprise environments using SQL and backend logic.",
                "Optimized queries and backend scripts reducing execution time by \\textbf{30\\%}.",
                "Ensured \\textbf{100\\% data integrity} through validation checks and reconciliation processes.",
                "Maintained technical documentation for audit and handover across \\textbf{2 teams}.",
            ]
        },
        {
            "title": "Backend Application Development Project",
            "date": "",
            "bullets": [
                "Developed backend modules using \\textbf{C\\#/.NET} following enterprise coding standards.",
                "Implemented \\textbf{database interactions and REST API} endpoints with proper error handling.",
                "Performed unit testing and debugging ensuring \\textbf{95\\%+ test coverage}.",
            ]
        },
    ],
}

# ══════════════════════════════════════════════════════════════════════════════
# SKILLS BY ROLE — improved with Git, REST, DevOps, Cloud, Soft skills
# ══════════════════════════════════════════════════════════════════════════════
def get_skills(role: str, jd_text: str, jd_keywords: list) -> list:
    jd_lower = jd_text.lower()
    has_aws    = any(k in jd_lower for k in ["aws", "amazon web services"])
    has_azure  = "azure" in jd_lower
    has_docker = "docker" in jd_lower
    has_k8s    = any(k in jd_lower for k in ["kubernetes", "k8s"])
    has_react  = "react" in jd_lower
    has_angular= "angular" in jd_lower
    has_java   = "java" in jd_lower
    has_spring = "spring" in jd_lower
    has_cicd   = any(k in jd_lower for k in ["ci/cd", "jenkins", "github actions", "gitlab"])

    cloud_tools = []
    if has_aws: cloud_tools.append("AWS")
    if has_azure: cloud_tools.append("Azure")
    if has_docker: cloud_tools.append("Docker")
    if has_k8s: cloud_tools.append("Kubernetes")
    cloud_str = ", ".join(cloud_tools) + " (Foundational)" if cloud_tools else "Cloud Fundamentals (AWS/Azure)"

    frontend_str = ""
    if has_react: frontend_str = "React, "
    if has_angular: frontend_str += "Angular, "

    cicd_str = "Jenkins, GitHub Actions" if has_cicd else "Git, GitHub, CI/CD Basics"

    if role == "sde":
        lang = "Python, C\\#, SQL, Java"
        if has_java and has_spring:
            lang = "Python, C\\#, SQL, Java, Spring Boot"
        return [
            ("Programming Languages", lang + ", C++"),
            ("Computer Science", "Data Structures, Algorithms, OOP, Complexity Analysis, SOLID Principles"),
            ("Backend \\& Databases", "MySQL, PostgreSQL, REST API, Query Optimization, Relational Databases"),
            ("Cloud \\& DevOps", cloud_str + ", " + cicd_str),
            ("Engineering Practices", "Debugging, Code Reviews, Unit Testing, Technical Documentation"),
            ("Tools", "Git, GitHub, Power BI, Pandas, NumPy, Linux"),
            ("Professional Skills", "Collaboration, Ownership, Communication, Problem Solving, Teamwork"),
        ]
    elif role == "analytics":
        return [
            ("Programming \\& Analytics", "Python, SQL, R (basic)"),
            ("Statistical Methods", "EDA, Hypothesis Testing, Descriptive Statistics, Scenario Analysis"),
            ("Data Visualization", "Power BI, Tableau (basic), Excel, Data Storytelling"),
            ("Business Analytics", "Problem Structuring, Stakeholder Management, Client-Facing Analytics"),
            ("Tools", "Pandas, NumPy, Git, Excel, Power BI"),
            ("Professional Skills", "Communication, Presentation, Collaboration, Attention to Detail, Reliability"),
        ]
    elif role == "data_science":
        return [
            ("Programming Languages", "Python, SQL, C\\#, Java"),
            ("Machine Learning", "Logistic Regression, Decision Trees, Random Forest, XGBoost/LightGBM"),
            ("Libraries \\& Tools", "Scikit-learn, Pandas, NumPy, SciPy, Power BI, Git"),
            ("Analytics", "EDA, Feature Engineering, Statistical Modeling, Binary Classification"),
            ("Risk \\& Data", "Credit Risk Concepts, Model Evaluation, Data Quality, Portfolio Monitoring"),
            ("Professional Skills", "Analytical Thinking, Communication, Collaboration, Attention to Detail"),
        ]
    elif role == "entry":
        return [
            ("Programming Languages", "C\\#, Python, Java, SQL"),
            ("Core Concepts", "OOP, Programming Fundamentals, DBMS, Data Structures (Basics)"),
            ("Data \\& Reporting", "SQL Queries, Data Validation, Power BI, Dashboards, Excel"),
            ("Development Practices", "Debugging, Unit Testing, Documentation, Git, GitHub"),
            ("Foundational Exposure", "Cloud Basics (AWS/Azure), REST APIs, CRM Systems, " + cicd_str),
            ("Professional Skills", "Problem Solving, Collaboration, Reliability, Communication, Willingness to Learn"),
        ]
    else:  # consulting
        return [
            ("Backend \\& Programming", "\\textbf{C\\#/.NET, Python, SQL}"),
            ("Platform \\& Systems", "ServiceNow (Foundational), CRM Platforms, Enterprise Systems"),
            ("Data \\& Integration", "SQL Databases, REST API Integration, Data Validation, Data Migration"),
            ("Cloud \\& DevOps", cloud_str + ", Git, GitHub, " + cicd_str),
            ("Development Practices", "System Analysis, Backend Optimization, Debugging, Documentation"),
            ("Enterprise Practices", "Change Management, Secure Coding, Production Support, Agile/Scrum"),
            ("Professional Skills", "Stakeholder Communication, Cross-Functional Collaboration, Reliability, Attention to Detail"),
        ]

# ══════════════════════════════════════════════════════════════════════════════
# SUMMARIES BY ROLE
# ══════════════════════════════════════════════════════════════════════════════
def build_summary(role: str, jd_keywords: list, jd_text: str) -> str:
    jd_lower = jd_text.lower()

    company_hint = ""
    if "amazon" in jd_lower:
        company_hint = " Seeking an SDE-I role at Amazon to build scalable, fault-tolerant systems that directly impact customers at scale."
    elif "airbnb" in jd_lower:
        company_hint = " Passionate about building reliable, high-quality software that powers exceptional user experiences at scale."
    elif "zs" in jd_lower:
        company_hint = " Highly motivated, client-focused, and well-suited for a fast-paced analytics consulting environment."
    elif "censora" in jd_lower or "regulated" in jd_lower:
        company_hint = " Eager to contribute to enterprise-scale analytics initiatives in a regulated, data-driven environment."
    elif "bajaj" in jd_lower or "credit risk" in jd_lower:
        company_hint = " Seeking to contribute to Risk Analytics and Credit Risk Modeling in a data-driven financial environment."

    has_cloud = any(k in jd_lower for k in ["aws", "azure", "gcp", "cloud"])
    has_java  = "java" in jd_lower
    has_rest  = any(k in jd_lower for k in ["rest", "api", "restful"])

    if role == "sde":
        extra = ""
        if has_cloud: extra += " Foundational exposure to cloud platforms (AWS/Azure) and DevOps practices."
        if has_java:  extra += " Proficient in Java with strong OOP fundamentals."
        if has_rest:  extra += " Experience building and consuming REST APIs."
        return (
            "Software Engineering graduate with strong foundations in \\textbf{data structures, algorithms, "
            "object-oriented programming}, and relational databases. Hands-on experience designing backend systems, "
            "optimizing SQL workflows, and building automation pipelines using \\textbf{Python, C\\#, Java, and SQL}. "
            "Demonstrated ownership across the full software development lifecycle including design, implementation, "
            "testing, debugging, and documentation." + extra + company_hint
        )
    elif role == "analytics":
        return (
            "Decision Analytics and Business Analytics professional with hands-on experience applying "
            "\\textbf{statistical analysis, EDA, and data-driven problem solving} to complex business challenges. "
            "Strong proficiency in \\textbf{Python and SQL}, with experience translating raw data into actionable insights, "
            "scenario analyses, and executive-ready recommendations. Proven ability to collaborate with cross-functional "
            "teams and communicate insights clearly to diverse stakeholders." + company_hint
        )
    elif role == "data_science":
        return (
            "Data Science and Risk Analytics professional with hands-on experience in \\textbf{Python and SQL} for "
            "statistical modeling, binary classification, and large-scale data analysis. Strong foundation in "
            "\\textbf{machine learning algorithms} including Logistic Regression, Decision Trees, and Random Forest. "
            "Experienced in model development, performance monitoring, feature engineering, and translating analytical "
            "insights into actionable business decisions." + company_hint
        )
    elif role == "entry":
        return (
            "Motivated Software Engineer with a strong foundation in \\textbf{programming fundamentals, OOP, and data handling}. "
            "Hands-on experience with \\textbf{C\\#, Python, Java, and SQL} through internships and real-world projects. "
            "Comfortable with coding, debugging, data validation, reporting, and documentation. "
            "Quick learner with strong collaboration, reliability, and ownership mindset, eager to grow across "
            "software development, automation, and cloud technologies." + company_hint
        )
    else:  # consulting
        return (
            "Backend and Platform-focused Software Developer with hands-on experience in system analysis, "
            "application development, data integration, and backend optimization. "
            "Strong proficiency in \\textbf{C\\#/.NET, Python, and SQL}, with practical exposure to REST API integration, "
            "database-driven applications, documentation, and production support. "
            "Experienced in translating business and technical requirements into reliable, scalable enterprise solutions. "
            "Strong collaborator with a client-first mindset and attention to detail." + company_hint
        )

# ══════════════════════════════════════════════════════════════════════════════
# LEADERSHIP
# ══════════════════════════════════════════════════════════════════════════════
LEADERSHIP_SECTION = r"""
\section{Leadership \& Activities}
\begin{joblong}{Production \& Backstage Head --- COEP Drama and Films Club}{Apr 2023 -- May 2025}
  \item Led a cross-functional team of \textbf{20+ members}, managing end-to-end production operations under tight deadlines.
  \item Strengthened leadership, coordination, and stakeholder communication skills across \textbf{5+ events}.
\end{joblong}
\begin{joblong}{Operations \& Logistics Coordinator --- Pune Startup Fest}{Oct 2022 -- Mar 2023}
  \item Coordinated logistics and communication for a \textbf{500+ attendee} large-scale technical event.
  \item Managed vendor relationships, scheduling, and on-ground execution ensuring smooth operations.
\end{joblong}
"""

# ══════════════════════════════════════════════════════════════════════════════
# LATEX PREAMBLE
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

# ══════════════════════════════════════════════════════════════════════════════
# LATEX BUILDER
# ══════════════════════════════════════════════════════════════════════════════
def build_latex(role: str, jd_text: str, jd_keywords: list) -> str:
    lines = [LATEX_PREAMBLE]

    # Detect if SDE/big tech role for GitHub in header
    is_sde = role == "sde"

    # ── Header ────────────────────────────────────────────────────────────────
    if is_sde:
        lines.append(r"""
\begin{tabularx}{\linewidth}{@{} C @{}}
{\Huge \textbf{ANURAG LOKHANDE}} \\[3pt]
\href{tel:+917709271496}{\faMobile\ +91-770-927-1496} \quad | \quad
\href{mailto:lokhandeag21.elec@coeptech.ac.in}{\faEnvelope\ lokhandeag21.elec@coeptech.ac.in} \quad | \quad
\href{https://www.linkedin.com/in/anurag-lokhande-180a5a230/}{\faLinkedin\ LinkedIn} \quad | \quad
\href{https://github.com/anuraglokhande}{\faGithub\ GitHub}
\end{tabularx}
""")
    else:
        lines.append(r"""
\begin{tabularx}{\linewidth}{@{} C @{}}
{\Huge \textbf{ANURAG LOKHANDE}} \\[3pt]
\href{tel:+917709271496}{\faMobile\ +91-770-927-1496} \quad | \quad
\href{mailto:lokhandeag21.elec@coeptech.ac.in}{\faEnvelope\ lokhandeag21.elec@coeptech.ac.in} \quad | \quad
\href{https://www.linkedin.com/in/anurag-lokhande-180a5a230/}{\faLinkedin\ LinkedIn}
\end{tabularx}
""")

    # ── Summary ───────────────────────────────────────────────────────────────
    lines.append(r"\section{Professional Summary}")
    lines.append(build_summary(role, jd_keywords, jd_text))
    lines.append("")

    # ── Experience ────────────────────────────────────────────────────────────
    exp_label = "Work Experience" if role == "sde" else "Internship Experience" if role == "entry" and "capgemini" in jd_text.lower() else "Professional Experience"
    lines.append(f"\\section{{{exp_label}}}")
    experience = get_experience(role, jd_keywords, jd_text)
    for exp in experience:
        lines.append(f"\\begin{{joblong}}{{{exp['title']} --- {exp['company']}}}{{{exp['date']}}}")
        for b in exp["bullets"]:
            lines.append(f"  \\item {b}")
        lines.append(r"\end{joblong}")
        lines.append("")

    # ── Projects ──────────────────────────────────────────────────────────────
    proj_labels = {
        "sde": "Projects",
        "analytics": "Selected Analytics Projects",
        "data_science": "Key Projects",
        "entry": "Academic \\& Technical Projects",
        "consulting": "Selected Technical Projects",
    }
    lines.append(f"\\section{{{proj_labels.get(role, 'Selected Projects')}}}")
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
    if role in ["sde", "entry", "consulting"]:
        coursework = r"\textit{Relevant Coursework:} Data Structures \& Algorithms, OOP, DBMS, Operating Systems, Computer Networks"
    else:
        coursework = r"\textit{Relevant Coursework:} Data Structures \& Algorithms, Statistics \& Probability, DBMS, Engineering Mathematics"
    lines.append(r"""\begin{tabularx}{\linewidth}{@{}l C r@{}}
\textbf{B.Tech in Electrical Engineering} & \textbf{COEP Technological University, Pune} & 2021 -- 2025 \\
\end{tabularx}""")
    lines.append(coursework)
    lines.append("")

    # ── Skills ────────────────────────────────────────────────────────────────
    skill_label = "Skills" if role == "analytics" else "Technical Skills"
    lines.append(f"\\section{{{skill_label}}}")
    lines.append(r"\begin{tabularx}{\linewidth}{@{}l X@{}}")
    skills = build_dynamic_skills(role, jd_text, jd_keywords)
    for label, val in skills:
        lines.append(f"\\textbf{{{label}:}} & {val} \\\\")
    lines.append(r"\end{tabularx}")
    lines.append("")

    # ── Leadership (SDE only) ─────────────────────────────────────────────────
    if is_sde:
        lines.append(LEADERSHIP_SECTION)

    lines.append(r"\end{document}")
    return "\n".join(lines)

# ══════════════════════════════════════════════════════════════════════════════
# PDF COMPILER — local pdflatex → latexonline.cc → ytotech fallback
# ══════════════════════════════════════════════════════════════════════════════
def compile_to_pdf(latex: str):
    # ── Try local pdflatex ───────────────────────────────────────────────────
    check = subprocess.run(["which", "pdflatex"], capture_output=True)
    if check.returncode == 0:
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
            return None, "Local pdflatex failed: " + result.stdout[-2000:]

    # ── Fall back to latexonline.cc ──────────────────────────────────────────
    try:
        r = requests.post(
            "https://latexonline.cc/compile",
            files={"file": ("resume.tex", latex.encode("utf-8"), "text/plain")},
            timeout=60
        )
        if r.status_code == 200 and "application/pdf" in r.headers.get("content-type", ""):
            return r.content, None

        # ── Fall back to ytotech ─────────────────────────────────────────────
        r2 = requests.post(
            "https://latex.ytotech.com/builds/sync",
            json={"compiler": "pdflatex", "resources": [{"main": True, "content": latex}]},
            headers={"Content-Type": "application/json"},
            timeout=60
        )
        if r2.status_code == 201:
            return r2.content, None

        return None, f"API error {r.status_code}: {r.text[:400]}"
    except Exception as e:
        return None, f"Compilation error: {str(e)}"

# ══════════════════════════════════════════════════════════════════════════════
# ROLE DISPLAY NAMES
# ══════════════════════════════════════════════════════════════════════════════
ROLE_DISPLAY = {
    "sde":        "💻 SDE / Backend Engineer",
    "analytics":  "📊 Data Analytics / BI",
    "data_science": "🤖 Data Science / Risk / ML",
    "entry":      "🎓 Entry Level / Trainee",
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

generate_btn = st.button("✨ Generate Resume", type="primary", use_container_width=True)

if "latex" not in st.session_state:    st.session_state.latex = None
if "pdf_bytes" not in st.session_state: st.session_state.pdf_bytes = None
if "role" not in st.session_state:     st.session_state.role = None
if "keywords" not in st.session_state: st.session_state.keywords = []

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

        with st.spinner("📄 Compiling PDF (10-15 seconds)..."):
            pdf, err = compile_to_pdf(latex)
            st.session_state.pdf_bytes = pdf
            if err:
                st.error(f"PDF error: {err}")

# ── Output ────────────────────────────────────────────────────────────────────
if st.session_state.latex:
    st.success("✅ Resume generated!")
    if st.session_state.role:
        st.info(f"🎯 **Detected Role:** {ROLE_DISPLAY.get(st.session_state.role, st.session_state.role)}")
    if st.session_state.keywords:
        st.caption(f"**Keywords matched:** {', '.join(st.session_state.keywords[:18])}")

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
        st.error("❌ PDF generation failed. Please try again.")
