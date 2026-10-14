
from flask import Flask, render_template, request, jsonify
from rapidfuzz import fuzz, process
import re

app = Flask(__name__)

# ==========================================================
# VCET LINKS
# ==========================================================

LINKS = {
    "website": "https://vcetputtur.ac.in/",
    "academics": "https://vcetputtur.ac.in/academics/",
    "faculty": "https://vcetputtur.ac.in/faculty/",
    "admissions": "https://vcetputtur.ac.in/admissions/",
    "contact": "https://vcetputtur.ac.in/",
    "placements": "https://vcetputtur.ac.in/",
    "library": "https://vcetputtur.ac.in/facilities/library/",
}

COLLEGE = {
    "name": "Vivekananda College of Engineering & Technology",
    "short_name": "VCET",
    "address": "Nehru Nagar, Puttur - 574203, Karnataka, India",
    "phone": "+91 8251 235955",
    "email": "principal@vcetputtur.ac.in",
    "principal": "Dr. Mahesh Prasanna K.",
    "kea_code": "E121",
    "comedk_code": "E148",
}

# This name appears in an older Basic Science activity report.
# Confirm the current designation with VCET.
BASIC_SCIENCE_HOD = "Prof. M. Ramananda Kamath"

BASIC_SCIENCE_HOD_NOTE = (
    "Prof. M. Ramananda Kamath was named as HOD of Basic Science "
    "in an older VCET activity report. Please confirm the current "
    "designation with the college."
)

# ==========================================================
# DEPARTMENTS
#
# Mathematics, Physics, Chemistry and Humanities/English
# all come under ONE overall Basic Science HOD.
#
# Department pages are used as faculty links when a separate
# faculty page has not been verified.
# ==========================================================

DEPARTMENTS = {
    "cse": {
        "name": "Computer Science & Engineering (CSE)",
        "aliases": [
            "cse", "computer science",
            "computer science engineering",
            "computer science and engineering",
            "computer engineering",
        ],
        "hod": "Mr. Pradeep Kumar K. G.",
        "page": "https://vcetputtur.ac.in/academics/ug-programs/computer-science-engineering/",
        "faculty": "https://vcetputtur.ac.in/academics/ug-programs/computer-science-engineering/",
    },

    "ds": {
        "name": "Computer Science Engineering (Data Science)",
        "aliases": [
            "ds", "cd", "c d", "cse ds", "cse cd",
            "cs ds", "cs cd", "data science", "data sciences",
            "computer data science", "computer science data science",
            "computer science and data science",
            "computer science engineering data science",
            "computer science engineering data sciences",
            "cse data science", "data science engineering",
            "data science department", "data science branch",
        ],
        "hod": "Prof. Roopa G. K.",
        "page": "https://vcetputtur.ac.in/academics/ug-programs/computer-science-engineering-data-science/",
        "faculty": "https://vcetputtur.ac.in/academics/ug-programs/computer-science-engineering-data-science/",
    },

    "aiml": {
        "name": "Artificial Intelligence & Machine Learning (AIML)",
        "aliases": [
            "aiml", "ai ml", "ai and ml",
            "artificial intelligence",
            "artificial intelligence and machine learning",
            "machine learning",
        ],
        "hod": "Dr. Radhika Shetty D. S.",
        "page": "https://vcetputtur.ac.in/academics/ug-programs/artificial-intelligence-machine-learning/",
        "faculty": "https://vcetputtur.ac.in/academics/ug-programs/artificial-intelligence-machine-learning/",
    },

    "ece": {
        "name": "Electronics & Communication Engineering (ECE)",
        "aliases": [
            "ece", "ec", "electronics",
            "electronics and communication",
            "electronics communication engineering",
            "electronics and communication engineering",
        ],
        "hod": "Dr. Shrikanth Rao S. K.",
        "page": "https://vcetputtur.ac.in/academics/ug-programs/electronics-communication-engineering/",
        "faculty": "https://vcetputtur.ac.in/academics/ug-programs/electronics-communication-engineering/",
    },

    "civil": {
        "name": "Civil Engineering",
        "aliases": [
            "civil", "cv", "civil engineering", "civil department",
        ],
        "hod": None,
        "page": "https://vcetputtur.ac.in/academics/ug-programs/civil-engineering/",
        "faculty": "https://vcetputtur.ac.in/academics/ug-programs/civil-engineering/",
    },

    "mech": {
        "name": "Mechanical Engineering",
        "aliases": [
            "mech", "mechanical", "mechanical engineering",
            "mechanical department",
        ],
        "hod": None,
        "page": "https://vcetputtur.ac.in/academics/ug-programs/mechanical-engineering/",
        "faculty": "https://vcetputtur.ac.in/academics/ug-programs/mechanical-engineering/",
    },

    "mca": {
        "name": "Master of Computer Applications (MCA)",
        "aliases": [
            "mca", "computer applications",
            "master of computer applications",
            "mca department", "mca course",
        ],
        "hod": None,
        "page": "https://vcetputtur.ac.in/academics/",
        "faculty": "https://vcetputtur.ac.in/faculty/",
    },

    "mba": {
        "name": "Master of Business Administration (MBA)",
        "aliases": [
            "mba", "business administration",
            "master of business administration",
            "management department", "mba department", "mba course",
        ],
        "hod": None,
        "page": "https://vcetputtur.ac.in/academics/pg-programs/department-of-business-administration/",
        "faculty": "https://vcetputtur.ac.in/academics/pg-programs/department-of-business-administration/",
    },

    "msc": {
        "name": "M.Sc. (Master of Science)",
        "aliases": [
            "msc", "m sc", "master of science",
            "masters in science", "msc course",
        ],
        "hod": None,
        "page": "https://vcetputtur.ac.in/academics/",
        "faculty": "https://vcetputtur.ac.in/faculty/",
    },

    # Basic Science subjects all share the overall HOD.

    "maths": {
        "name": "Basic Science — Mathematics",
        "aliases": [
            "maths", "math", "mathematics",
            "maths department", "mathematics department",
            "math faculty", "maths faculty", "mathematics faculty",
            "math hod", "maths hod", "mathematics hod",
            "engineering mathematics", "calculus",
        ],
        "hod": BASIC_SCIENCE_HOD,
        "page": "https://vcetputtur.ac.in/academics/basic-science/department-of-mathematics/",
        "faculty": "https://vcetputtur.ac.in/academics/basic-science/department-of-mathematics/",
    },

    "physics": {
        "name": "Basic Science — Physics",
        "aliases": [
            "physics", "phy", "physics department",
            "physics faculty", "physics hod",
            "engineering physics", "physics teacher",
        ],
        "hod": BASIC_SCIENCE_HOD,
        "page": "https://vcetputtur.ac.in/academics/basic-science/department-of-physics/",
        "faculty": "https://vcetputtur.ac.in/academics/basic-science/department-of-physics/",
    },

    "chemistry": {
        "name": "Basic Science — Chemistry",
        "aliases": [
            "chemistry", "chem", "chemistry department",
            "chemistry faculty", "chemistry hod",
            "engineering chemistry", "chemistry teacher",
        ],
        "hod": BASIC_SCIENCE_HOD,
        "page": "https://vcetputtur.ac.in/academics/basic-science/department-of-chemistry/",
        "faculty": "https://vcetputtur.ac.in/academics/basic-science/department-of-chemistry/",
    },

    "humanities": {
        "name": "Basic Science — Humanities / English",
        "aliases": [
            "english", "english department", "english faculty",
            "english hod", "humanities", "humanities department",
            "humanities faculty", "communication skills",
            "professional english", "language department",
        ],
        "hod": BASIC_SCIENCE_HOD,
        "page": "https://vcetputtur.ac.in/academics/basic-science/department-of-humanities/",
        "faculty": "https://vcetputtur.ac.in/academics/basic-science/department-of-humanities/",
    },

    "pe": {
        "name": "Department of Physical Education",
        "aliases": [
            "pe", "physical education",
            "physical education department",
            "sports department", "sports faculty",
        ],
        "hod": None,
        "page": "https://vcetputtur.ac.in/academics/",
        "faculty": "https://vcetputtur.ac.in/faculty/",
    },
}

BASIC_SUBJECTS = {"maths", "physics", "chemistry", "humanities"}

BASIC_SCIENCE_LINKS = {
    "Mathematics": DEPARTMENTS["maths"]["page"],
    "Physics": DEPARTMENTS["physics"]["page"],
    "Chemistry": DEPARTMENTS["chemistry"]["page"],
    "Humanities / English": DEPARTMENTS["humanities"]["page"],
    "General faculty directory": LINKS["faculty"],
    "Academics overview": LINKS["academics"],
}

# ==========================================================
# SHORTHAND AND COMMON MISSPELLINGS
# ==========================================================

ALIASES = {
    # Greetings
    "gm": "good morning",
    "gud mrng": "good morning",
    "good mrng": "good morning",
    "gn": "good night",
    "gud nyt": "good night",
    "gud night": "good night",
    "hii": "hi",
    "hiii": "hi",
    "heyy": "hey",
    "heyyy": "hey",
    "wassup": "what is up",
    "wsp": "what is up",

    # Chat words
    "thx": "thanks",
    "tnq": "thank you",
    "tq": "thank you",
    "ty": "thank you",
    "plz": "please",
    "pls": "please",
    "okk": "okay",
    "okie": "okay",
    "tc": "take care",

    # Questions and college words
    "abt": "about",
    "whr": "where",
    "wher": "where",
    "wht": "what",
    "hw": "how",
    "ur": "your",
    "clg": "college",
    "collg": "college",
    "collage": "college",
    "admsn": "admission",
    "admisson": "admission",
    "admision": "admission",
    "placmnt": "placement",
    "plcemnt": "placement",
    "fac": "faculty",
    "facilty": "facilities",
    "facilties": "facilities",
    "staf": "staff",
    "stafs": "staff",
    "addr": "address",
    "adress": "address",
    "loc": "location",
    "phn": "phone",
    "phne": "phone",
    "eml": "email",
    "dept": "department",
    "depts": "departments",
    "cource": "course",
    "crs": "course",
    "hostl": "hostel",
    "schlrship": "scholarship",
    "engg": "engineering",
    "mnglr": "mangaluru",
    "mangalore": "mangaluru",
    "dk": "dakshina kannada",
    "cse-ds": "cse ds",
}

VOCABULARY = set("""
hi hello hey good morning afternoon evening night goodbye bye
thanks thank you please okay welcome take care
college vcet puttur karnataka india location address district state
admission admissions eligibility application apply
course courses branch branches department departments
computer science engineering artificial intelligence machine learning
data science electronics communication mechanical civil
faculty staff hod head principal professor teacher lecturer
fees fee scholarship hostel facilities library transport
placement placements company companies training recruitment
contact phone number email website campus laboratory labs
student students exam exams syllabus timetable calendar
where what when which who how why tell explain give
available offered information details about near located
mangaluru dakshina kannada nehru nagar cse aiml ece mca mba msc
maths math mathematics physics chemistry humanities english
data sciences computer applications management basic science
physical education sports
""".split())

for department in DEPARTMENTS.values():
    VOCABULARY.update(department["name"].lower().split())
    for alias in department["aliases"]:
        VOCABULARY.update(alias.lower().split())

VOCABULARY.update(ALIASES.keys())

# ==========================================================
# NORMALIZATION AND SPELLING CORRECTION
# ==========================================================

def normalize(text):
    text = str(text).lower().strip()
    text = text.replace("&", " and ").replace("/", " ")
    text = re.sub(r"[^\w\s-]", " ", text)
    text = re.sub(r"\s+", " ", text).strip()

    for short, full in sorted(
        ALIASES.items(), key=lambda item: len(item[0]), reverse=True
    ):
        text = re.sub(
            r"\b" + re.escape(short) + r"\b",
            full,
            text,
        )

    return re.sub(r"\s+", " ", text).strip()


def correct_spelling(message):
    words = normalize(message).split()
    corrected = []

    for word in words:
        if len(word) < 4 or word.isdigit() or word in VOCABULARY:
            corrected.append(word)
            continue

        match = process.extractOne(
            word,
            list(VOCABULARY),
            scorer=fuzz.ratio,
            score_cutoff=86 if len(word) <= 6 else 82,
        )
        corrected.append(match[0] if match else word)

    return " ".join(corrected)


def phrase_in_text(phrase, text):
    phrase = normalize(phrase)
    return bool(re.search(
        r"(?<!\w)" + re.escape(phrase) + r"(?!\w)", text
    ))


# ==========================================================
# DEPARTMENT DETECTION
# ==========================================================

def basic_science_subject_from_question(question):
    """Detect only Basic Science subjects, not engineering branches."""
    q = normalize(question)

    subject_aliases = {
        "maths": [
            "maths", "math", "mathematics",
            "engineering mathematics", "calculus",
        ],
        "physics": ["physics", "phy", "engineering physics"],
        "chemistry": ["chemistry", "chem", "engineering chemistry"],
        "humanities": [
            "english", "english department", "humanities",
            "communication skills", "professional english",
        ],
    }

    matches = []
    for code, aliases in subject_aliases.items():
        for alias in aliases:
            if phrase_in_text(alias, q):
                matches.append((len(normalize(alias)), code))

    if matches:
        matches.sort(reverse=True)
        return matches[0][1]

    return None


def department_from_question(question):
    q = normalize(question)
    tokens = q.split()

    # Exact department codes. CD and DS both mean Data Science.
    code_aliases = {
        "cse": "cse",
        "cs": "cse",
        "ds": "ds",
        "cd": "ds",
        "aiml": "aiml",
        "ece": "ece",
        "ec": "ece",
        "civil": "civil",
        "mech": "mech",
        "mca": "mca",
        "mba": "mba",
        "msc": "msc",
        "math": "maths",
        "maths": "maths",
        "physics": "physics",
        "chemistry": "chemistry",
        "english": "humanities",
        "humanities": "humanities",
        "pe": "pe",
    }

    # A specific Basic Science subject should not be confused with
    # the general Basic Science department.
    subject = basic_science_subject_from_question(q)
    if subject:
        return subject

    for token in tokens:
        if token in code_aliases:
            return code_aliases[token]

    # Match complete aliases, preferring the longest match.
    matches = []

    for code, info in DEPARTMENTS.items():
        for alias in info["aliases"]:
            alias_text = normalize(alias)
            if alias_text and phrase_in_text(alias_text, q):
                matches.append((len(alias_text), code))

    if matches:
        matches.sort(reverse=True)
        return matches[0][1]

    # Fuzzy match common misspellings.
    alias_to_code = {}
    all_aliases = []

    for code, info in DEPARTMENTS.items():
        for alias in info["aliases"]:
            alias = normalize(alias)
            all_aliases.append(alias)
            alias_to_code[alias] = code

    candidates = [q] + tokens

    for size in (2, 3, 4, 5):
        for i in range(len(tokens) - size + 1):
            candidates.append(" ".join(tokens[i:i + size]))

    best_code = None
    best_score = 0

    for candidate in candidates:
        if len(candidate) < 4:
            continue

        result = process.extractOne(
            candidate,
            all_aliases,
            scorer=fuzz.ratio,
            score_cutoff=84,
        )

        if result and result[1] > best_score:
            best_score = result[1]
            best_code = alias_to_code[result[0]]

    return best_code


# ==========================================================
# DEPARTMENT ANSWERS
# ==========================================================

def asks_hod(question):
    q = normalize(question)
    tokens = set(q.split())

    return (
        bool(tokens.intersection({"hod", "head", "director", "leader"}))
        or "head of department" in q
        or "who is the head" in q
    )


def asks_faculty(question):
    tokens = set(normalize(question).split())

    return bool(tokens.intersection({
        "faculty", "staff", "teacher", "teachers",
        "professor", "lecturer", "lecturers", "faculties",
    }))


def department_answer(code, question):
    info = DEPARTMENTS[code]
    q = normalize(question)
    response = [info["name"]]

    # One overall HOD for all Basic Science subjects.
    if code in BASIC_SUBJECTS:
        response.append(
            "This subject comes under the Department of Basic Science."
        )
        response.append(f"Overall Basic Science HOD: {BASIC_SCIENCE_HOD}")
        response.append(BASIC_SCIENCE_HOD_NOTE)
        response.append(f"Specific subject page: {info['page']}")
        response.append(f"Subject faculty/details: {info['faculty']}")
        response.append(
            f"Basic Science overview: {LINKS['academics']}"
        )
        return "\n".join(response)

    if asks_hod(q):
        if info["hod"]:
            response.append(f"HOD / Head: {info['hod']}")
        else:
            response.append(
                "I don't have a verified current HOD name for this "
                "department. Please check the official department page."
            )

    if asks_faculty(q):
        response.append("Faculty and department details are available here.")

    response.append(f"Department page: {info['page']}")
    response.append(f"Faculty information: {info['faculty']}")

    return "\n".join(response)


def basic_science_overview():
    lines = [
        "Department of Basic Science — VCET Puttur",
        f"Overall Basic Science HOD: {BASIC_SCIENCE_HOD}",
        BASIC_SCIENCE_HOD_NOTE,
        "",
        "Subjects and their specific links:",
    ]

    for subject, url in BASIC_SCIENCE_LINKS.items():
        lines.append(f"{subject}: {url}")

    return "\n".join(lines)


# ==========================================================
# GREETINGS, GENERAL QUESTIONS AND COLLEGE FAQs
# ==========================================================

FAQS = [
    {
        "questions": [
            "what is vcet",
            "what does vcet stand for",
            "tell me about vivekananda college",
            "about vcet college",
        ],
        "answer": (
            f"{COLLEGE['name']} ({COLLEGE['short_name']}) is located at "
            f"{COLLEGE['address']}.\n"
            f"Website: {LINKS['website']}\n"
            f"Academics: {LINKS['academics']}"
        ),
    },
    {
        "questions": [
            "how can i contact the college",
            "college phone number",
            "what is the college email",
        ],
        "answer": (
            f"Phone: {COLLEGE['phone']}\n"
            f"Email: {COLLEGE['email']}\n"
            f"Website: {LINKS['website']}"
        ),
    },
]


def quick_answer(message):
    q = normalize(message)
    tokens = set(q.split())

    # Greetings
    if q in {
        "hi", "hello", "hey", "good morning",
        "good afternoon", "good evening", "good night",
        "what is up",
    }:
        if q == "good morning":
            return (
                "Good morning! Welcome to Chbotly. "
                "How can I help you with VCET?"
            )
        if q == "good afternoon":
            return "Good afternoon! What would you like to know about VCET?"
        if q == "good evening":
            return (
                "Good evening! Ask me about VCET courses, departments, "
                "admissions, or campus facilities."
            )
        if q == "good night":
            return "Good night! Take care. Come back whenever you need VCET information."
        if q == "what is up":
            return (
                "I'm here to help with VCET information! Ask about "
                "departments, HODs, faculty, admissions, or placements."
            )
        return (
            "Hello! Welcome to Chbotly, the VCET Puttur college assistant. "
            "What would you like to know?"
        )

    if q in {"thanks", "thank you", "thank you very much"}:
        return "You're welcome! Feel free to ask me anything about VCET."

    if q in {"bye", "goodbye", "take care"}:
        return "Goodbye! Take care and have a great day."

    if q in {"okay", "ok", "fine", "alright"}:
        return "Okay! What would you like to know about VCET?"

    # Basic Science overview versus a specific subject.
    if "basic science" in q or "basic sciences" in q:
        subject = basic_science_subject_from_question(q)
        if subject:
            return department_answer(subject, q)
        return basic_science_overview()

    # College name
    if q in {"name", "college name", "name of college"}:
        return (
            f"{COLLEGE['name']} ({COLLEGE['short_name']}).\n"
            f"Website: {LINKS['website']}"
        )

    # Puttur location
    if "puttur" in q and tokens.intersection({
        "where", "location", "located", "district", "state", "place",
    }):
        return (
            "Puttur is a town in Dakshina Kannada district, Karnataka, India, "
            "in coastal Karnataka, southeast of Mangaluru.\n"
            f"VCET address: {COLLEGE['address']}\n"
            f"Official website: {LINKS['website']}"
        )

    if q in {"puttur", "where is puttur", "puttur location"}:
        return (
            "Puttur is a town in Dakshina Kannada district, Karnataka, India.\n"
            f"VCET address: {COLLEGE['address']}\n"
            f"Website: {LINKS['website']}"
        )

    # Address
    if (
        q == "address"
        or "college address" in q
        or "vcet address" in q
    ):
        return (
            f"VCET address: {COLLEGE['address']}\n"
            f"Official website: {LINKS['website']}"
        )

    # Contact
    if tokens.intersection({"phone", "contact", "email"}):
        return (
            f"Phone: {COLLEGE['phone']}\n"
            f"Email: {COLLEGE['email']}\n"
            f"Official website: {LINKS['website']}"
        )

    if q in {"website", "college website", "vcet website", "college link"}:
        return f"Official VCET website: {LINKS['website']}"

    if "principal" in tokens:
        return (
            f"Principal: {COLLEGE['principal']}\n"
            f"Official website: {LINKS['website']}"
        )

    # Admissions
    if tokens.intersection({
        "admission", "admissions", "eligibility", "apply", "application",
    }):
        return (
            "For current admission rules, course intake, fee notifications, "
            "eligibility and required documents, check the official page.\n"
            f"Admissions: {LINKS['admissions']}\n"
            f"KEA code: {COLLEGE['kea_code']}\n"
            f"COMEDK code: {COLLEGE['comedk_code']}"
        )

    if "kea" in tokens:
        return (
            f"VCET KEA code: {COLLEGE['kea_code']}.\n"
            f"Admissions: {LINKS['admissions']}"
        )

    if "comedk" in tokens:
        return (
            f"VCET COMEDK code: {COLLEGE['comedk_code']}.\n"
            f"Admissions: {LINKS['admissions']}"
        )

    # Fees and scholarships
    if tokens.intersection({"fee", "fees", "scholarship", "scholarships"}):
        return (
            "Fees depend on the programme and admission category. "
            "Check the official admissions page for the latest details.\n"
            f"Admissions and fees: {LINKS['admissions']}"
        )

    # Placements
    if tokens.intersection({
        "placement", "placements", "recruitment",
        "company", "companies", "training",
    }):
        return (
            "For current placement and recruitment information, visit "
            "the official VCET website.\n"
            f"Website: {LINKS['placements']}"
        )

    # Courses
    if tokens.intersection({
        "course", "courses", "branch", "branches",
        "programmes", "programs", "departments",
    }):
        return (
            "VCET programmes include CSE, CSE (Data Science), AIML, ECE, "
            "Civil, Mechanical Engineering, MCA and MBA. Basic Science "
            "includes Mathematics, Physics, Chemistry and Humanities/English.\n"
            f"Academics: {LINKS['academics']}"
        )

    # General faculty directory
    if tokens.intersection({"faculty", "staff", "teachers", "lecturers"}):
        return f"Official VCET faculty directory: {LINKS['faculty']}"

    # Campus facilities
    if tokens.intersection({
        "library", "facilities", "hostel",
        "transport", "canteen", "sports",
    }):
        return (
            "For campus facilities and student services, visit the official website.\n"
            f"Website: {LINKS['website']}\n"
            f"Library: {LINKS['library']}"
        )

    if "about" in tokens and tokens.intersection({"college", "vcet"}):
        return (
            f"{COLLEGE['name']} is located at {COLLEGE['address']}.\n"
            f"Website: {LINKS['website']}\n"
            f"Academics: {LINKS['academics']}"
        )

    return None


# ==========================================================
# MAIN RESPONSE FUNCTION
# ==========================================================

def get_response(message):
    if not message or not str(message).strip():
        return "Please type a question about VCET, and I'll try to help."

    question = normalize(correct_spelling(message))

    # General Basic Science question:
    # list all subjects, links and the shared HOD.
    # Specific subject questions route to that subject instead.
    if "basic science" in question or "basic sciences" in question:
        subject = basic_science_subject_from_question(question)
        if subject:
            return department_answer(subject, question)
        return basic_science_overview()

    # Department detection first.
    # Examples: CD HOD, DS faculty, Maths faculty, Physics HOD.
    department = department_from_question(question)
    if department:
        return department_answer(department, question)

    # General college FAQs
    answer = quick_answer(question)
    if answer:
        return answer

    # Fuzzy FAQ matching
    best_answer = None
    best_score = 0

    for item in FAQS:
        for example in item["questions"]:
            score = max(
                fuzz.WRatio(question, normalize(example)),
                fuzz.token_set_ratio(question, normalize(example)),
            )

            if score > best_score:
                best_score = score
                best_answer = item["answer"]

    if best_answer and best_score >= 76:
        return best_answer

    return (
        "I'm not completely sure about that question yet. You can ask about "
        "departments, HODs, faculty, admissions, courses, fees, placements, "
        "facilities, college address, Basic Science subjects, or Puttur's location.\n"
        f"Website: {LINKS['website']}\n"
        f"Academics: {LINKS['academics']}\n"
        f"Faculty: {LINKS['faculty']}"
    )


# ==========================================================
# FLASK ROUTES
# ==========================================================

@app.route("/")
def home():
    return render_template("index.html")


@app.route("/chat", methods=["POST"])
def chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")
    return jsonify({"reply": get_response(message)})


if __name__ == "__main__":
    app.run(debug=True)
