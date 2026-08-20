import streamlit as st
import streamlit.components.v1 as components
import re
from io import BytesIO
from xml.sax.saxutils import escape
from PyPDF2 import PdfReader

# =========================================================
# OPTIONAL PDF REPORT LIBRARY
# =========================================================
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.lib.enums import TA_CENTER
    from reportlab.platypus import (
        SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
    )
    REPORTLAB_AVAILABLE = True
except ImportError:
    REPORTLAB_AVAILABLE = False

# =========================================================
# PAGE CONFIG
# =========================================================
st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide",
    initial_sidebar_state="expanded",
)

# =========================================================
# PROFESSIONAL UI
# =========================================================
st.markdown("""
<style>
.stApp {
    background:
        radial-gradient(circle at 88% 4%, rgba(37,99,235,.20), transparent 25%),
        radial-gradient(circle at 8% 35%, rgba(14,165,233,.08), transparent 23%),
        linear-gradient(145deg,#040914 0%,#071226 48%,#06101f 100%);
    color:#e5e7eb;
}
.block-container {
    max-width:1420px;
    padding-top:1.35rem;
    padding-bottom:2.5rem;
}
[data-testid="stSidebar"] {
    background:linear-gradient(180deg,#071123 0%,#0a1730 100%);
    border-right:1px solid rgba(96,165,250,.22);
}
[data-testid="stSidebar"] * { color:#e5e7eb !important; }
h1,h2,h3,h4 { color:#f8fafc !important; letter-spacing:-.025em; }
p,label { color:#cbd5e1 !important; }

.hero {
    position:relative;
    padding:34px 36px;
    border-radius:24px;
    background:
        linear-gradient(135deg,rgba(12,22,43,.98),rgba(14,42,88,.97) 58%,rgba(5,78,112,.92));
    border:1px solid rgba(96,165,250,.34);
    box-shadow:0 22px 70px rgba(0,0,0,.30);
    margin-bottom:24px;
    overflow:hidden;
}
.hero:before {
    content:"";
    position:absolute;
    width:300px;height:300px;
    right:-130px;top:-145px;
    border-radius:50%;
    background:rgba(34,211,238,.10);
    box-shadow:0 0 100px rgba(34,211,238,.10);
}
.hero h1 {
    margin:0 0 9px 0;
    color:#fff !important;
    font-size:2.25rem;
    position:relative;
}
.hero p {
    margin:0;
    font-size:15px;
    color:#bdd0e8 !important;
    max-width:820px;
    line-height:1.65;
    position:relative;
}

.section-title {
    padding:17px 21px;
    border-radius:17px;
    background:linear-gradient(135deg,rgba(11,29,64,.96),rgba(8,54,98,.82));
    border:1px solid rgba(56,189,248,.34);
    box-shadow:0 10px 28px rgba(0,0,0,.15);
    margin:27px 0 15px;
}
.section-title h2 { margin:0; font-size:1.22rem; }
.section-title p {
    margin:5px 0 0;
    color:#9fb7d5 !important;
    font-size:13px;
}

[data-testid="stFileUploaderDropzone"] {
    background:linear-gradient(145deg,#0a162a,#101f38) !important;
    border:1px dashed #3b82f6 !important;
    border-radius:15px !important;
}
[data-testid="stFileUploaderDropzone"]:hover {
    border-color:#22d3ee !important;
}
.stTextArea textarea,.stTextInput input {
    background:#091427 !important;
    color:#f8fafc !important;
    border:1px solid #334d73 !important;
    border-radius:12px !important;
}
.stTextArea textarea:focus,.stTextInput input:focus {
    border-color:#38bdf8 !important;
    box-shadow:0 0 0 2px rgba(56,189,248,.12) !important;
}
.stButton button,.stDownloadButton button {
    border-radius:11px !important;
    font-weight:750 !important;
    border:1px solid #41658e !important;
    background:linear-gradient(135deg,#132644,#0d1c33) !important;
    color:#f8fafc !important;
    min-height:42px;
    transition:.18s ease !important;
}
.stButton button:hover,.stDownloadButton button:hover {
    border-color:#38bdf8 !important;
    transform:translateY(-1px);
    box-shadow:0 8px 22px rgba(14,165,233,.12);
}

.metric-card {
    background:linear-gradient(145deg,rgba(14,27,49,.98),rgba(8,19,36,.98));
    border:1px solid rgba(71,101,145,.70);
    border-radius:17px;
    padding:19px 12px;
    text-align:center;
    min-height:112px;
    box-shadow:0 10px 28px rgba(0,0,0,.15);
}
.metric-value {
    font-size:31px;
    font-weight:850;
    color:#f8fafc !important;
}
.metric-label {
    color:#8fa7c5 !important;
    font-size:11px;
    text-transform:uppercase;
    letter-spacing:.09em;
    margin-top:4px;
}

.good,.warn,.bad,.info {
    padding:13px 16px;
    border-radius:12px;
    margin:10px 0;
    line-height:1.55;
}
.good { background:rgba(5,46,27,.65); border:1px solid #16a34a; color:#bbf7d0 !important; }
.warn { background:rgba(66,32,6,.65); border:1px solid #f59e0b; color:#fde68a !important; }
.bad  { background:rgba(69,10,10,.65); border:1px solid #ef4444; color:#fecaca !important; }
.info { background:rgba(8,47,73,.65); border:1px solid #0ea5e9; color:#bae6fd !important; }

.skill {
    display:inline-block;
    padding:7px 12px;
    margin:4px;
    border-radius:999px;
    background:#111f35;
    border:1px solid #385170;
    color:#e2e8f0 !important;
    font-size:12px;
    font-weight:650;
}
.skill.match {
    border-color:#10b981;
    background:rgba(6,56,43,.78);
    color:#a7f3d0 !important;
}
.skill.missing {
    border-color:#ef4444;
    background:rgba(61,10,18,.78);
    color:#fecaca !important;
}

.section-card {
    background:linear-gradient(145deg,rgba(13,28,52,.98),rgba(8,20,40,.98));
    border:1px solid #315b9b;
    border-radius:16px;
    padding:17px 18px;
    min-height:145px;
    margin-bottom:12px;
    box-shadow:0 10px 25px rgba(0,0,0,.14);
}
.section-card .name {
    font-size:14px;
    font-weight:750;
    color:#f8fafc;
}
.section-card .score {
    font-size:29px;
    font-weight:850;
    margin:9px 0 2px;
}
.section-card .status {
    font-size:12px;
    font-weight:650;
}

.job-card {
    position:relative;
    background:linear-gradient(145deg,rgba(13,29,55,.99),rgba(7,18,36,.99));
    border:1px solid rgba(66,111,170,.72);
    border-radius:18px;
    padding:20px 21px;
    margin:12px 0;
    box-shadow:0 13px 32px rgba(0,0,0,.18);
    transition:transform .18s ease,border-color .18s ease,box-shadow .18s ease;
}
.job-card:hover {
    transform:translateY(-2px);
    border-color:#38bdf8;
    box-shadow:0 18px 38px rgba(0,0,0,.24);
}
.job-top {
    display:flex;
    justify-content:space-between;
    align-items:center;
    gap:13px;
}
.job-rank {
    display:inline-flex;
    align-items:center;
    justify-content:center;
    width:32px;height:32px;
    flex:0 0 32px;
    border-radius:9px;
    background:rgba(37,99,235,.20);
    border:1px solid rgba(96,165,250,.38);
    color:#93c5fd;
    font-size:12px;
    font-weight:800;
}
.job-name {
    font-size:17px;
    font-weight:800;
    color:#f8fafc;
    flex:1;
}
.job-fit {
    font-size:25px;
    font-weight:850;
    color:#38d6ff;
    white-space:nowrap;
}
.job-note {
    color:#8199b8 !important;
    font-size:10px;
    text-transform:uppercase;
    letter-spacing:.09em;
    margin:3px 0 0 45px;
}
.bar {
    height:9px;
    border-radius:999px;
    background:#17263d;
    overflow:hidden;
    margin:13px 0 15px;
    border:1px solid rgba(71,101,145,.28);
}
.bar-fill {
    height:100%;
    border-radius:999px;
    background:linear-gradient(90deg,#22d3ee,#3b82f6);
    box-shadow:0 0 12px rgba(34,211,238,.22);
}
.skill-grid {
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:10px;
}
.skill-box {
    background:rgba(7,18,34,.62);
    border:1px solid rgba(71,101,145,.32);
    border-radius:12px;
    padding:10px 12px;
}
.skill-box-title {
    font-size:10px;
    text-transform:uppercase;
    letter-spacing:.08em;
    margin-bottom:5px;
}
.match-title { color:#6ee7b7; }
.missing-title { color:#fda4af; }
.skill-box-text {
    font-size:12px;
    line-height:1.55;
    color:#dbeafe;
}
.empty-state {
    text-align:center;
    padding:26px 18px;
    border:1px dashed rgba(96,165,250,.35);
    border-radius:15px;
    background:rgba(8,20,40,.45);
    color:#9fb7d5;
}

.report-panel {
    background:linear-gradient(135deg,rgba(11,37,83,.96),rgba(7,72,128,.88));
    border:1px solid rgba(56,189,248,.42);
    border-radius:18px;
    padding:20px;
    margin:13px 0 8px;
    box-shadow:0 15px 35px rgba(0,0,0,.18);
}
.report-panel h3 { margin:0 0 5px; font-size:18px; }
.report-panel p { margin:0; color:#b8cde5 !important; font-size:13px; }

.sidebar-brand { padding:14px 3px 13px; }
.sidebar-brand .title { font-size:18px; font-weight:850; color:#fff; }
.sidebar-brand .sub {
    font-size:12px;
    color:#8fa7c5 !important;
    line-height:1.5;
    margin-top:6px;
}
.sidebar-feature {
    padding:7px 0;
    color:#dbeafe !important;
    font-size:13px;
}

[data-testid="stProgress"] > div > div { border-radius:999px !important; }

.footer {
    text-align:center;
    padding:18px 0 4px;
    color:#7186a4 !important;
    font-size:11px;
}

@media (max-width: 900px) {
    .hero h1 { font-size:1.75rem; }
    .block-container { padding-left:1rem; padding-right:1rem; }
    .job-fit { font-size:22px; }
    .skill-grid { grid-template-columns:1fr; }
}
</style>
""", unsafe_allow_html=True)

# =========================================================
# DATABASES
# =========================================================
SKILLS = [
    "Python","Java","C++","C","JavaScript","TypeScript","HTML","CSS","React",
    "Node.js","Express","SQL","MySQL","PostgreSQL","MongoDB","Git","GitHub",
    "Django","Flask","Streamlit","Machine Learning","Deep Learning","Data Science",
    "Pandas","NumPy","Scikit-learn","TensorFlow","PyTorch","Spring Boot",
    "REST API","AWS","Azure","Docker","Kubernetes","Excel","Power BI","Tableau",
    "Artificial Intelligence","NLP","Natural Language Processing","Data Analysis",
    "Matplotlib","Seaborn","Linux","Figma","Jira","Agile","OOP","DSA"
]

JOB_ROLES = {
    "Python Developer":["Python","SQL","Git","Django","Flask","REST API"],
    "Data Analyst":["Python","SQL","Excel","Power BI","Tableau","Data Analysis"],
    "Data Scientist":["Python","Pandas","NumPy","Scikit-learn","Machine Learning","SQL"],
    "Machine Learning Engineer":["Python","Machine Learning","Scikit-learn","TensorFlow","PyTorch","SQL"],
    "Full Stack Developer":["HTML","CSS","JavaScript","React","Node.js","SQL","Git"],
    "Backend Developer":["Python","Java","SQL","REST API","Django","Spring Boot","Git"],
    "Frontend Developer":["HTML","CSS","JavaScript","React","Git"],
    "AI/ML Engineer":["Python","Artificial Intelligence","Machine Learning","Deep Learning","NLP"],
}

SECTION_ALIASES = {
    "Summary / Objective":[r"summary",r"professional summary",r"objective",r"profile",r"about me"],
    "Education":[r"education",r"academic background",r"qualification",r"academic qualification"],
    "Skills":[r"skills",r"technical skills",r"technical expertise",r"technologies"],
    "Experience":[r"experience",r"work experience",r"professional experience",r"employment",r"internship"],
    "Projects":[r"projects",r"academic projects",r"personal projects",r"key projects"],
    "Certifications":[r"certifications",r"certificates",r"courses",r"training"],
    "Achievements":[r"achievements",r"awards",r"honors",r"accomplishments"],
}

SECTION_CONTENT = {
    "Summary / Objective":[r"seeking",r"career",r"professional",r"developer",r"engineer",r"experience"],
    "Education":[r"\b(b\.?tech|bca|bsc|mca|m\.?tech|bachelor|master|degree|university|college)\b"],
    "Skills":[r"\b(" + "|".join(re.escape(s.lower()) for s in SKILLS) + r")\b"],
    "Experience":[r"\b(developed|worked|intern|internship|company|responsible|employment|experience)\b",r"\b20\d{2}\b"],
    "Projects":[r"\b(project|developed|built|created|implemented|github|application|system)\b"],
    "Certifications":[r"\b(certified|certificate|certification|course|training|udemy|coursera)\b"],
    "Achievements":[r"\b(achievement|award|winner|won|hackathon|recognition|accomplishment)\b"],
}

ACTION_WORDS = [
    "developed","built","created","implemented","designed","improved","optimized",
    "managed","automated","led","analyzed","deployed","reduced","increased",
    "integrated","tested","maintained","delivered"
]

# =========================================================
# HELPERS
# =========================================================
def normalize_text(text):
    return re.sub(r"[ \t]+", " ", text or "").strip()

def detect_skills(text):
    found = []
    low = (text or "").lower()
    for skill in SKILLS:
        if re.search(r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)", low):
            found.append(skill)
    return found

def extract_pdf_text(uploaded_file):
    reader = PdfReader(uploaded_file)
    parts = []
    for page in reader.pages:
        txt = page.extract_text() or ""
        if txt.strip():
            parts.append(txt)
    return "\n".join(parts)

def is_section_header(line, patterns):
    clean = re.sub(r"[^a-zA-Z /&-]", "", line).strip().lower()
    if not clean or len(clean) > 55:
        return False
    return any(re.fullmatch(p, clean) for p in patterns)

def find_section_block(text, section):
    lines = [normalize_text(x) for x in (text or "").splitlines()]
    patterns = SECTION_ALIASES.get(section, [])
    start = None

    for i, line in enumerate(lines):
        if is_section_header(line, patterns):
            start = i
            break

    if start is None:
        return "", False

    end = len(lines)
    all_patterns = []
    for vals in SECTION_ALIASES.values():
        all_patterns.extend(vals)

    for j in range(start + 1, len(lines)):
        if is_section_header(lines[j], all_patterns):
            end = j
            break

    block = "\n".join(x for x in lines[start + 1:end] if x)
    return block, True

def section_score(text, section):
    if not text.strip():
        return 0

    if section == "Contact":
        email = bool(re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text))
        phone = bool(re.search(r"(?:\+91[-\s]?)?[6-9]\d{9}", text))
        linkedin = bool(re.search(r"linkedin\.com|github\.com", text.lower()))

        score = 0
        if email: score += 40
        if phone: score += 35
        if linkedin: score += 25
        return min(100, score)

    block, header_found = find_section_block(text, section)
    if not header_found:
        return 0

    words = len(block.split())
    content_match = any(
        re.search(p, block.lower())
        for p in SECTION_CONTENT.get(section, [])
    )

    # Avoid making every well-formed section automatically 100%.
    score = 0
    if words >= 3:
        score += 25
    if words >= 8:
        score += 25
    if words >= 18:
        score += 15
    if content_match:
        score += 25
    if len(block.splitlines()) >= 2:
        score += 10

    return min(100, score)

def action_score(text):
    low = text.lower()
    count = sum(
        len(re.findall(r"\b" + re.escape(w) + r"\b", low))
        for w in ACTION_WORDS
    )
    return min(100, round(count / 6 * 100))

def content_quality_score(text, resume_skills):
    skill_part = min(100, len(resume_skills) / 10 * 100)
    action_part = action_score(text)
    return round((skill_part * 0.55) + (action_part * 0.45))

def calculate_ats(text, required, resume_skills, section_scores):
    required = set(required)
    matched = set(resume_skills).intersection(required)

    skill_match = (len(matched) / len(required) * 100) if required else 0
    section_avg = sum(section_scores.values()) / len(section_scores)
    quality = content_quality_score(text, resume_skills)

    score = (skill_match * 0.65) + (section_avg * 0.20) + (quality * 0.15)
    return round(min(100, score), 1)

def job_recommendations(resume_skills):
    user = set(resume_skills)
    results = []

    for role, required in JOB_ROLES.items():
        matched = sorted(user.intersection(required))
        missing = sorted(set(required) - user)
        fit = round(len(matched) / len(required) * 100, 1)
        results.append((role, fit, matched, missing))

    return sorted(results, key=lambda x: (-x[1], x[0]))

def make_suggestions(text, resume_skills, required, missing, sections):
    suggestions = []
    word_count = len(text.split())

    if word_count < 180:
        suggestions.append(
            "Add more useful detail. Include project impact, responsibilities and measurable results instead of keeping the resume too short."
        )

    if sections["Summary / Objective"] < 100:
        suggestions.append(
            "Add a focused 2–3 line professional summary tailored to the target role."
        )

    if sections["Projects"] < 100:
        suggestions.append(
            "Strengthen the Projects section with technologies used, your contribution and measurable outcomes."
        )

    if sections["Experience"] < 100:
        suggestions.append(
            "Add internship/work experience when applicable and describe responsibilities with action verbs and results."
        )

    if sections["Education"] < 100:
        suggestions.append(
            "Make Education clear with degree, college/university and graduation year."
        )

    if sections["Skills"] < 100:
        suggestions.append(
            "Create a dedicated Technical Skills section and keep it focused on skills you genuinely know."
        )

    if sections["Certifications"] == 0:
        suggestions.append(
            "Add relevant certifications or courses if you have completed any."
        )

    if sections["Achievements"] == 0:
        suggestions.append(
            "Consider adding achievements, awards, hackathons or strong academic/project accomplishments when relevant."
        )

    if not re.search(r"[\w.+-]+@[\w-]+\.[\w.-]+", text):
        suggestions.append("Add a professional email address.")

    if not re.search(r"(?:\+91[-\s]?)?[6-9]\d{9}", text):
        suggestions.append("Add a contact phone number.")

    if action_score(text) < 50:
        suggestions.append(
            "Use stronger action verbs such as Developed, Built, Implemented, Optimized, Automated and Deployed."
        )

    if missing:
        suggestions.append(
            "Prioritize missing target-job skills before applying. Only add skills you genuinely know or are actively learning."
        )

    if not suggestions:
        suggestions.append(
            "Your resume structure is strong. Keep tailoring keywords and achievements for each individual job description."
        )

    return suggestions

def status_for(score):
    if score >= 80:
        return "Strong", "🟢"
    if score >= 50:
        return "Needs Improvement", "🟡"
    return "Missing", "🔴"

def build_pdf(data):
    if not REPORTLAB_AVAILABLE:
        return None

    buffer = BytesIO()
    doc = SimpleDocTemplate(
        buffer, pagesize=A4,
        rightMargin=36, leftMargin=36,
        topMargin=36, bottomMargin=36
    )
    styles = getSampleStyleSheet()

    title = ParagraphStyle(
        "title", parent=styles["Title"],
        alignment=TA_CENTER, fontSize=20, spaceAfter=14
    )
    heading = ParagraphStyle(
        "heading", parent=styles["Heading2"],
        fontSize=14, spaceBefore=12, spaceAfter=7
    )
    body = styles["BodyText"]

    story = [
        Paragraph("AI Resume Analyzer — ATS Report", title),
        Paragraph(f"<b>ATS Score:</b> {data['ats']}%", body),
        Spacer(1, 10),
        Paragraph("Target Job Skill Match", heading),
        Paragraph(f"Matched skills: {len(data['matched'])}", body),
        Paragraph(f"Missing skills: {len(data['missing'])}", body),
        Paragraph(
            "Matched: " + escape(", ".join(sorted(data["matched"])) or "None"),
            body
        ),
        Paragraph(
            "Missing: " + escape(", ".join(sorted(data["missing"])) or "None"),
            body
        ),
        Paragraph("Section Analysis", heading),
    ]

    table_data = [["Section", "Score"]]
    for name, score in data["sections"].items():
        table_data.append([name, f"{score}%"])

    table = Table(table_data, colWidths=[300, 100])
    table.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,0),colors.HexColor("#1f2937")),
        ("TEXTCOLOR",(0,0),(-1,0),colors.white),
        ("GRID",(0,0),(-1,-1),0.5,colors.grey),
        ("PADDING",(0,0),(-1,-1),6),
    ]))
    story.append(table)

    story.append(Paragraph("Job Recommendations", heading))
    for role, fit, matched, missing in data["jobs"][:5]:
        story.append(
            Paragraph(
                f"<b>{escape(role)}</b>: {fit}% skill fit | "
                f"Matched: {escape(', '.join(matched) or 'None')} | "
                f"Improve: {escape(', '.join(missing) or 'None')}",
                body
            )
        )

    story.append(Paragraph("Improvement Suggestions", heading))
    for suggestion in data["suggestions"]:
        story.append(Paragraph("• " + escape(suggestion), body))

    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()

# =========================================================
# SIDEBAR
# =========================================================
with st.sidebar:
    st.markdown("""
    <div class="sidebar-brand">
        <div class="title">📄 AI Resume Analyzer</div>
        <div class="sub">Smart resume intelligence for ATS alignment, skills and job-fit analysis.</div>
    </div>
    """, unsafe_allow_html=True)

    st.divider()
    st.markdown("### FEATURES")

    for item in [
        "📊 ATS Dashboard",
        "📄 Section Analysis",
        "🧠 Smart Suggestions",
        "🎯 Job Recommendations",
        "🛠️ Skill Gap Analysis",
        "📥 Professional PDF Report",
        "✨ Professional UI",
    ]:
        st.markdown(
            f'<div class="sidebar-feature">{item}</div>',
            unsafe_allow_html=True
        )

    st.divider()
    st.caption("Major Project • Resume Intelligence")

# =========================================================
# HEADER
# =========================================================
st.markdown("""
<div class="hero">
    <h1>📄 AI Resume Analyzer</h1>
    <p>
        Analyze your resume against a target job, identify ATS gaps,
        improve resume content and discover suitable job roles.
    </p>
</div>
""", unsafe_allow_html=True)

# =========================================================
# INPUT
# =========================================================
left, right = st.columns(2, gap="large")

with left:
    st.subheader("📤 Upload Resume")
    uploaded_file = st.file_uploader(
        "Choose a PDF resume",
        type=["pdf"],
        help="Upload a text-based PDF resume for best results."
    )

with right:
    st.subheader("🎯 Target Job Description")
    job_description = st.text_area(
        "Paste the job description",
        height=190,
        placeholder=(
            "Example: Python Developer with Python, SQL, Django, "
            "REST API, Git and AWS..."
        )
    )

resume_text = ""

if uploaded_file:
    try:
        resume_text = extract_pdf_text(uploaded_file)
        st.success("Resume uploaded and text extracted successfully! ✅")
    except Exception as e:
        st.error(f"Could not read this PDF: {e}")

if uploaded_file and not resume_text.strip():
    st.warning(
        "This PDF does not contain extractable text. Please upload a text-based PDF."
    )

if resume_text.strip():
    with st.expander("📃 View Extracted Resume Text"):
        st.text(resume_text[:20000])

    st.download_button(
        "📥 Download Extracted Resume Text",
        data=resume_text,
        file_name="extracted_resume.txt",
        mime="text/plain",
    )

# =========================================================
# ANALYSIS
# =========================================================
if resume_text.strip() and job_description.strip():
    resume_skills = detect_skills(resume_text)
    required_skills = set(detect_skills(job_description))

    matched_skills = set(resume_skills).intersection(required_skills)
    missing_skills = required_skills - set(resume_skills)

    section_names = [
        "Contact",
        "Summary / Objective",
        "Education",
        "Skills",
        "Experience",
        "Projects",
        "Certifications",
        "Achievements",
    ]

    section_scores = {
        name: section_score(resume_text, name)
        for name in section_names
    }

    ats_score = calculate_ats(
        resume_text,
        required_skills,
        resume_skills,
        section_scores
    )

    suggestions = make_suggestions(
        resume_text,
        resume_skills,
        required_skills,
        missing_skills,
        section_scores
    )

    jobs = job_recommendations(resume_skills)

    # =====================================================
    # ATS DASHBOARD
    # =====================================================
    st.markdown("""
    <div class="section-title">
        <h2>📊 ATS Dashboard</h2>
        <p>Overall compatibility of your resume with the target job.</p>
    </div>
    """, unsafe_allow_html=True)

    m1, m2, m3, m4 = st.columns(4, gap="medium")

    metrics = [
        (f"{ats_score}%", "ATS Score"),
        (str(len(matched_skills)), "Matched Skills"),
        (str(len(missing_skills)), "Missing Skills"),
        (str(len(resume_skills)), "Resume Skills"),
    ]

    for col, (value, label) in zip([m1, m2, m3, m4], metrics):
        with col:
            st.markdown(
                f"""
                <div class="metric-card">
                    <div class="metric-value">{value}</div>
                    <div class="metric-label">{label}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    st.progress(
        min(100, int(ats_score)),
        text=f"Overall ATS Score: {ats_score}%"
    )

    if ats_score >= 80:
        st.markdown(
            '<div class="good">🟢 <b>Excellent ATS readiness.</b> '
            'Your resume is strongly aligned with the target job.</div>',
            unsafe_allow_html=True
        )
    elif ats_score >= 60:
        st.markdown(
            '<div class="warn">🟡 <b>Good starting point.</b> '
            'Improve missing skills and weaker resume sections.</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="bad">🔴 <b>Low ATS alignment.</b> '
            'Focus on target-job skills and resume structure.</div>',
            unsafe_allow_html=True
        )

    # =====================================================
    # SKILL GAP
    # =====================================================
    st.markdown("""
    <div class="section-title">
        <h2>🛠️ Skill Gap Analysis</h2>
        <p>Compare skills detected in your resume with the target job description.</p>
    </div>
    """, unsafe_allow_html=True)

    c1, c2 = st.columns(2, gap="large")

    with c1:
        st.markdown(f"### 🟢 Matched Skills ({len(matched_skills)})")
        if matched_skills:
            st.markdown(
                "".join(
                    f'<span class="skill match">✓ {escape(s)}</span>'
                    for s in sorted(matched_skills)
                ),
                unsafe_allow_html=True
            )
        else:
            st.info("No target-job skills matched.")

    with c2:
        st.markdown(f"### 🔴 Missing Skills ({len(missing_skills)})")
        if missing_skills:
            st.markdown(
                "".join(
                    f'<span class="skill missing">✗ {escape(s)}</span>'
                    for s in sorted(missing_skills)
                ),
                unsafe_allow_html=True
            )
        else:
            st.success("No missing target-job skills detected! 🎉")

    # =====================================================
    # SECTION ANALYSIS
    # =====================================================
    st.markdown("""
    <div class="section-title">
        <h2>📄 Resume Section Analysis</h2>
        <p>
            Scores consider section headings and meaningful content,
            instead of giving 100% simply because a heading exists.
        </p>
    </div>
    """, unsafe_allow_html=True)

    cols = st.columns(3, gap="medium")

    for i, (name, score) in enumerate(section_scores.items()):
        status, icon = status_for(score)

        score_color = (
            "#34d399" if score >= 80
            else "#fbbf24" if score >= 50
            else "#fb7185"
        )

        with cols[i % 3]:
            st.markdown(
                f"""
                <div class="section-card">
                    <div class="name">{icon} {escape(name)}</div>
                    <div class="score" style="color:{score_color};">{score}%</div>
                    <div class="status" style="color:{score_color};">{status}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # =====================================================
    # SUGGESTIONS
    # =====================================================
    st.markdown("""
    <div class="section-title">
        <h2>🧠 Resume Improvement Suggestions</h2>
        <p>Practical recommendations generated from your resume analysis.</p>
    </div>
    """, unsafe_allow_html=True)

    for i, suggestion in enumerate(suggestions, 1):
        st.markdown(
            f'<div class="info">💡 <b>{i}.</b> {escape(suggestion)}</div>',
            unsafe_allow_html=True
        )

    # =====================================================
    # JOB RECOMMENDATIONS
    # =====================================================
    st.markdown("""
    <div class="section-title">
        <h2>🎯 Job Recommendations</h2>
        <p>
            Ranked by role-specific skill coverage. Matching skills are shown
            separately from skills you can improve.
        </p>
    </div>
    """, unsafe_allow_html=True)

    top_jobs = jobs[:5]

    for rank, (role, fit, role_matched, role_missing) in enumerate(
        top_jobs, 1
    ):
        matched_text = (
            ", ".join(role_matched)
            if role_matched
            else "No matching skills yet"
        )

        missing_text = (
            ", ".join(role_missing)
            if role_missing
            else "No major skill gap detected"
        )

        # Render the recommendation card inside a small HTML component.
        # This avoids Streamlit versions that display raw HTML tags as text.
        matched_html = escape(matched_text)
        missing_html = escape(missing_text)
        role_html = escape(role)

        job_html = f"""
<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<style>
* {{ box-sizing:border-box; }}
html, body {{
    margin:0;
    padding:0;
    background:transparent;
    font-family:Arial, Helvetica, sans-serif;
}}
.card {{
    width:100%;
    padding:20px;
    border-radius:18px;
    background:linear-gradient(145deg,#0d1d37,#071326);
    border:1px solid #426fae;
    box-shadow:0 12px 30px rgba(0,0,0,.22);
    color:#e5e7eb;
}}
.top {{
    display:flex;
    align-items:center;
    gap:12px;
}}
.rank {{
    width:32px;
    height:32px;
    min-width:32px;
    border-radius:9px;
    display:flex;
    align-items:center;
    justify-content:center;
    background:#152d62;
    border:1px solid #4b78bd;
    color:#bfdbfe;
    font-size:12px;
    font-weight:800;
}}
.role {{
    flex:1;
    font-size:17px;
    font-weight:800;
    color:#f8fafc;
}}
.fit {{
    font-size:25px;
    font-weight:850;
    color:#38d6ff;
    white-space:nowrap;
}}
.note {{
    margin:5px 0 0 44px;
    color:#8199b8;
    font-size:10px;
    text-transform:uppercase;
    letter-spacing:1px;
}}
.track {{
    width:100%;
    height:9px;
    margin:13px 0 16px;
    border-radius:999px;
    overflow:hidden;
    background:#17263d;
    border:1px solid #293e5d;
}}
.fill {{
    width:{fit}%;
    height:100%;
    border-radius:999px;
    background:linear-gradient(90deg,#22d3ee,#3b82f6);
}}
.grid {{
    display:grid;
    grid-template-columns:1fr 1fr;
    gap:10px;
}}
.box {{
    min-height:72px;
    padding:10px 12px;
    border-radius:12px;
    background:rgba(5,15,30,.70);
    border:1px solid #263d5c;
}}
.title {{
    margin-bottom:6px;
    font-size:10px;
    font-weight:800;
    text-transform:uppercase;
    letter-spacing:.7px;
}}
.match {{ color:#6ee7b7; }}
.missing {{ color:#fda4af; }}
.text {{
    color:#dbeafe;
    font-size:12px;
    line-height:1.55;
}}
@media(max-width:700px) {{
    .grid {{ grid-template-columns:1fr; }}
}}
</style>
</head>
<body>
<div class="card">
    <div class="top">
        <div class="rank">#{rank}</div>
        <div class="role">{role_html}</div>
        <div class="fit">{fit}%</div>
    </div>

    <div class="note">Role skill fit</div>

    <div class="track">
        <div class="fill"></div>
    </div>

    <div class="grid">
        <div class="box">
            <div class="title match">🟢 Matching Skills</div>
            <div class="text">{matched_html}</div>
        </div>

        <div class="box">
            <div class="title missing">🔴 Skills to Improve</div>
            <div class="text">{missing_html}</div>
        </div>
    </div>
</div>
</body>
</html>
"""

        components.html(
            job_html,
            height=205 if role_missing else 185,
            scrolling=False,
        )

    # =====================================================
    # REPORT
    # =====================================================
    st.markdown("""
    <div class="report-panel">
        <h3>📥 Download Analysis Report</h3>
        <p>
            Save your complete ATS analysis as a text report or professional PDF.
        </p>
    </div>
    """, unsafe_allow_html=True)

    job_report_lines = []
    for role, fit, matched, missing in jobs[:5]:
        job_report_lines.append(
            f"- {role}: {fit}% | "
            f"Matched: {', '.join(matched) or 'None'} | "
            f"Improve: {', '.join(missing) or 'None'}"
        )

    report_text = f"""AI RESUME ANALYZER
========================================
ATS SCORE: {ats_score}%

MATCHED TARGET-JOB SKILLS:
{chr(10).join("- " + x for x in sorted(matched_skills)) or "- None"}

MISSING TARGET-JOB SKILLS:
{chr(10).join("- " + x for x in sorted(missing_skills)) or "- None"}

SECTION ANALYSIS:
{chr(10).join(f"- {name}: {score}%" for name, score in section_scores.items())}

JOB RECOMMENDATIONS:
{chr(10).join(job_report_lines)}

IMPROVEMENT SUGGESTIONS:
{chr(10).join("- " + s for s in suggestions)}

========================================
Generated by AI Resume Analyzer
"""

    r1, r2 = st.columns(2, gap="medium")

    with r1:
        st.download_button(
            "📄 Download TXT Report",
            data=report_text,
            file_name="AI_Resume_Analysis.txt",
            mime="text/plain",
        )

    with r2:
        pdf_data = build_pdf({
            "ats": ats_score,
            "matched": matched_skills,
            "missing": missing_skills,
            "sections": section_scores,
            "jobs": jobs,
            "suggestions": suggestions,
        })

        if pdf_data:
            st.download_button(
                "📥 Download Professional PDF Report",
                data=pdf_data,
                file_name="AI_Resume_Analysis.pdf",
                mime="application/pdf",
            )
        else:
            st.warning(
                "PDF report ke liye ReportLab install karein: pip install reportlab"
            )

else:
    st.markdown("""
    <div class="empty-state">
        <h3>🚀 Ready to Analyze</h3>
        <p>
            Upload a PDF resume and paste a target job description above
            to generate your complete resume intelligence report.
        </p>
        <p>
            📊 ATS Dashboard &nbsp; • &nbsp;
            📄 Section Analysis &nbsp; • &nbsp;
            🧠 Smart Suggestions &nbsp; • &nbsp;
            🎯 Job Recommendations &nbsp; • &nbsp;
            🛠️ Skill Gap &nbsp; • &nbsp;
            📥 PDF Report
        </p>
    </div>
    """, unsafe_allow_html=True)

st.divider()

st.markdown(
    '<div class="footer">🤖 AI Resume Analyzer | '
    'Analyze → ATS Score → Skill Gap → Suggestions → '
    'Job Recommendations → PDF Report</div>',
    unsafe_allow_html=True
)
