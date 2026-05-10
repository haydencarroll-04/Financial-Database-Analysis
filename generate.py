"""
Synthetic data generator for the bank schema.

Streams CSV output to OUT_DIR. Tunable knobs at the top.
Default settings target ~1.3 GB total output and ~5-8 min runtime.
"""

import csv
import os
import random
import string
from datetime import date, datetime, timedelta

# ============================================================
# CONFIGURATION
# ============================================================
SEED = 42

OUT_DIR = r"C:\developer\synthetic_data\out"

N_BRANCHES        = 25
N_EMPLOYEES       = 500
N_CUSTOMERS       = 100_000

# account adoption (probability a given customer has at least one of these)
P_CHECKING        = 0.85
P_SAVINGS         = 0.60
P_CREDIT          = 0.50
P_LOAN            = 0.25
P_BROKERAGE       = 0.15
P_401K            = 0.30
P_ROTH            = 0.20

# transaction rate per account per year (mean; actual is randomized 0.5x-1.5x)
TXN_RATE = {
    "checking":  12.0,
    "savings":    3.0,
    "credit":     8.0,
    "loan":       1.0,
    "brokerage":  1.5,
    "401k":       1.0,
    "roth":       0.5,
}

# beneficiaries / cards
P_BENEFICIARY      = 0.80   # of customers have at least one beneficiary
EXTRA_BENEFICIARY  = 0.35   # of those, chance to add another (compounded for up to 3)
P_DEBIT_CARD       = 0.90   # of checking accounts get a debit card
P_CREDIT_CARD      = 0.95   # of credit accounts get a credit card
P_BROKERAGE_CARD   = 0.20
P_401K_CARD        = 0.05

# date span
START_DATE = date(2001, 5, 10)
END_DATE   = date(2026, 5, 10)

# dirty data probabilities
P_DIRTY_NAME       = 0.08    # whitespace / weird casing on names
P_DIRTY_EMAIL      = 0.10    # typos, missing @, etc
P_DIRTY_PHONE_BAD  = 0.04    # outright invalid phone format
P_NULL_OPTIONAL    = 0.04    # null an optional field
P_STATUS_VARIANT   = 0.40    # use a non-canonical casing/abbrev for status
P_FUTURE_OPENDATE  = 0.001   # impossible future open_date
P_BAD_MATURITY     = 0.005   # maturity before open
P_NEG_BALANCE_BUG  = 0.003   # negative balance on non-credit account
P_DUP_CUSTOMER     = 0.004   # duplicate customer (same person, new id)
P_ACCT_NUM_FORMAT  = 0.30    # account numbers with dashes/spaces
P_CARD_NUM_FORMAT  = 0.50

random.seed(SEED)

# ============================================================
# DATA POOLS
# ============================================================
FIRST_NAMES = [
    "James","Mary","John","Patricia","Robert","Jennifer","Michael","Linda","William","Elizabeth",
    "David","Barbara","Richard","Susan","Joseph","Jessica","Thomas","Sarah","Charles","Karen",
    "Christopher","Lisa","Daniel","Nancy","Matthew","Betty","Anthony","Sandra","Mark","Margaret",
    "Donald","Ashley","Steven","Kimberly","Paul","Emily","Andrew","Donna","Joshua","Michelle",
    "Kenneth","Carol","Kevin","Amanda","Brian","Melissa","George","Deborah","Edward","Stephanie",
    "Ronald","Rebecca","Timothy","Sharon","Jason","Laura","Jeffrey","Cynthia","Ryan","Kathleen",
    "Jacob","Amy","Gary","Shirley","Nicholas","Angela","Eric","Helen","Jonathan","Anna",
    "Stephen","Brenda","Larry","Pamela","Justin","Nicole","Scott","Samantha","Brandon","Katherine",
    "Benjamin","Christine","Samuel","Emma","Gregory","Catherine","Frank","Debra","Alexander","Virginia",
    "Raymond","Rachel","Patrick","Carolyn","Jack","Janet","Dennis","Maria","Jerry","Heather",
    "Tyler","Diane","Aaron","Julie","Jose","Joyce","Adam","Victoria","Henry","Olivia",
    "Nathan","Kelly","Douglas","Christina","Zachary","Lauren","Peter","Joan","Kyle","Evelyn",
    "Walter","Judith","Ethan","Andrea","Jeremy","Hannah","Harold","Megan","Keith","Cheryl",
    "Christian","Jacqueline","Roger","Martha","Noah","Madison","Gerald","Teresa","Carl","Gloria",
    "Terry","Sara","Sean","Janice","Austin","Ann","Arthur","Kathryn","Lawrence","Abigail",
    "Jesse","Sophia","Dylan","Frances","Bryan","Jean","Joe","Alice","Jordan","Judy",
    "Billy","Isabella","Bruce","Julia","Albert","Grace","Willie","Amber","Gabriel","Denise",
    "Logan","Danielle","Alan","Marilyn","Juan","Beverly","Wayne","Charlotte","Roy","Natalie",
    "Ralph","Theresa","Randy","Diana","Eugene","Brittany","Vincent","Doris","Russell","Kayla",
    "Louis","Alexis","Bobby","Lori","Philip","Marie","Johnny","Tiffany","Ivan","Priya",
    "Wei","Hiroshi","Fatima","Aisha","Diego","Sofia","Mateo","Camila","Liam","Aaliyah",
]

LAST_NAMES = [
    "Smith","Johnson","Williams","Brown","Jones","Garcia","Miller","Davis","Rodriguez","Martinez",
    "Hernandez","Lopez","Gonzalez","Wilson","Anderson","Thomas","Taylor","Moore","Jackson","Martin",
    "Lee","Perez","Thompson","White","Harris","Sanchez","Clark","Ramirez","Lewis","Robinson",
    "Walker","Young","Allen","King","Wright","Scott","Torres","Nguyen","Hill","Flores",
    "Green","Adams","Nelson","Baker","Hall","Rivera","Campbell","Mitchell","Carter","Roberts",
    "Gomez","Phillips","Evans","Turner","Diaz","Parker","Cruz","Edwards","Collins","Reyes",
    "Stewart","Morris","Morales","Murphy","Cook","Rogers","Gutierrez","Ortiz","Morgan","Cooper",
    "Peterson","Bailey","Reed","Kelly","Howard","Ramos","Kim","Cox","Ward","Richardson",
    "Watson","Brooks","Chavez","Wood","James","Bennett","Gray","Mendoza","Ruiz","Hughes",
    "Price","Alvarez","Castillo","Sanders","Patel","Myers","Long","Ross","Foster","Jimenez",
    "Powell","Jenkins","Perry","Russell","Sullivan","Bell","Coleman","Butler","Henderson","Barnes",
    "Gonzales","Fisher","Vasquez","Simmons","Romero","Jordan","Patterson","Alexander","Hamilton","Graham",
    "Reynolds","Griffin","Wallace","Moreno","West","Cole","Hayes","Bryant","Herrera","Gibson",
    "Ellis","Tran","Medina","Aquino","Marshall","Ferguson","McKinney","Cunningham","O'Brien","Steinberg",
    "Nakamura","Okonkwo","Petrov","Schmidt","Andersson","Müller","DeLaCruz","Van der Berg","Al-Hassan","Fitzgerald",
]

STREET_NAMES = [
    "Main","Oak","Pine","Maple","Cedar","Elm","Washington","Lake","Hill","Park",
    "Walnut","Spring","North","South","Ridge","River","Sunset","Highland","Forest","Center",
    "Church","Chestnut","Willow","Mill","Jefferson","Madison","Lincoln","Adams","Jackson","Franklin",
    "Birch","Meadow","Valley","Pleasant","Prospect","Union","Garden","Court","School","Bridge",
]
STREET_TYPES_CLEAN = ["St","Ave","Rd","Dr","Ln","Blvd","Ct","Way","Pl","Ter"]
STREET_TYPES_DIRTY = ["Street","St.","st","STREET","Avenue","Ave.","ave","AVENUE","Road","Rd.","rd","Drive","Dr.","Lane","Ln.","Blvd.","BLVD","Court","Ct."]

CITIES_BY_STATE = {
    "NY": ["New York","Buffalo","Rochester","Syracuse","Albany"],
    "CA": ["Los Angeles","San Francisco","San Diego","San Jose","Sacramento","Fresno"],
    "TX": ["Houston","Dallas","Austin","San Antonio","Fort Worth","El Paso"],
    "FL": ["Miami","Orlando","Tampa","Jacksonville","Tallahassee"],
    "IL": ["Chicago","Springfield","Peoria","Naperville"],
    "PA": ["Philadelphia","Pittsburgh","Allentown","Erie"],
    "OH": ["Columbus","Cleveland","Cincinnati","Toledo","Akron"],
    "GA": ["Atlanta","Savannah","Augusta","Macon"],
    "NC": ["Charlotte","Raleigh","Greensboro","Durham"],
    "MI": ["Detroit","Grand Rapids","Ann Arbor","Lansing"],
    "WA": ["Seattle","Spokane","Tacoma","Bellevue"],
    "AZ": ["Phoenix","Tucson","Mesa","Scottsdale"],
    "MA": ["Boston","Worcester","Springfield","Cambridge"],
    "CO": ["Denver","Colorado Springs","Boulder","Aurora"],
    "OR": ["Portland","Eugene","Salem","Bend"],
}
STATES = list(CITIES_BY_STATE.keys())

EMPLOYEE_ROLES = [
    "Teller","Senior Teller","Branch Manager","Assistant Manager","Loan Officer",
    "Personal Banker","Customer Service Rep","Financial Advisor","Operations Manager",
    "Wealth Manager","Mortgage Specialist","Compliance Officer",
]

LOAN_TYPES = ["Mortgage","Auto","Personal","Student","Home Equity","Small Business"]
BROKERAGE_TYPES = ["Individual","Joint","Trust","Custodial","Margin","Cash"]
RETIRE_TYPES_401K = ["Traditional","Roth","Safe Harbor","SIMPLE"]
RETIRE_TYPES_ROTH = ["Roth IRA","Roth Conversion","Spousal Roth"]
CARD_TYPES = ["Debit","Credit","Prepaid","Platinum","Gold","Rewards","Business"]
BANK_NAMES = ["Wells Fargo","Chase","Bank of America","Citibank","US Bank","PNC","Capital One",
              "TD Bank","HSBC","Truist","Ally","Fifth Third","Regions Bank"]
RELATIONSHIPS_CLEAN = ["Spouse","Child","Parent","Sibling","Grandchild","Friend","Trust","Estate"]
RELATIONSHIPS_DIRTY = ["spuose","Spuose","Daugther","Sun","Sone","Bro","Sis","father","MOTHER","Spouse "]

EMAIL_DOMAINS = ["gmail.com","yahoo.com","hotmail.com","outlook.com","aol.com","icloud.com",
                 "live.com","comcast.net","verizon.net","msn.com"]
EMAIL_DOMAIN_TYPOS = ["gmial.com","gmai.com","yaho.com","hotnail.com","outloook.com","gmail.con"]

TXN_TYPES_DEPOSIT = ["Deposit","Direct Deposit","Cash Deposit","Check Deposit","Wire In","ACH Credit"]
TXN_TYPES_WITHDRAW = ["Withdrawal","ATM Withdrawal","Cash Withdrawal","Wire Out","ACH Debit"]
TXN_TYPES_PAYMENT = ["Payment","Bill Pay","Online Payment","Auto Pay"]
TXN_TYPES_PURCHASE = ["Purchase","POS Purchase","Online Purchase"]
TXN_TYPES_TRANSFER = ["Transfer In","Transfer Out","Internal Transfer"]
TXN_TYPES_FEE = ["Service Fee","Overdraft Fee","Wire Fee","Maintenance Fee","ATM Fee"]
TXN_TYPES_INTEREST = ["Interest Credit","Interest Charge","Dividend"]
TXN_DESCRIPTIONS = [
    "Walmart","Target","Amazon","Costco","Whole Foods","Trader Joes","Starbucks","McDonalds",
    "Shell Gas","Exxon","Chevron","Home Depot","Lowes","Best Buy","Apple Store","Netflix",
    "Spotify","Verizon","AT&T","Comcast","Electric Co","Water Dept","Rent","Mortgage Pmt",
    "Salary","Payroll","IRS Refund","DMV","Uber","Lyft","Doordash","CVS Pharmacy","Walgreens",
    None,"","check #1234","ATM withdrawal - downtown","",
]

# ============================================================
# HELPERS - dirty data
# ============================================================
def maybe_dirty_name(name):
    if random.random() < P_DIRTY_NAME:
        r = random.random()
        if r < 0.20: return name.upper()
        if r < 0.35: return name.lower()
        if r < 0.55: return " " + name
        if r < 0.70: return name + " "
        if r < 0.85: return name + "  "
        return name.replace(name[0], name[0].lower(), 1) if name else name
    return name

def rand_email(first, last):
    f = first.strip().lower()
    l = last.strip().lower().replace(" ","").replace("'","")
    sep = random.choice(["",".","_","-",""])
    suffix = random.choice(["", str(random.randint(1,99)), str(random.randint(1970,2010))])
    domain = random.choice(EMAIL_DOMAINS)
    if random.random() < 0.03:
        domain = random.choice(EMAIL_DOMAIN_TYPOS)
    addr = f"{f}{sep}{l}{suffix}@{domain}"
    if random.random() < P_DIRTY_EMAIL:
        r = random.random()
        if r < 0.15: addr = addr.replace("@","")             # missing @
        elif r < 0.25: addr = addr.replace(".","..",1)        # double dot
        elif r < 0.45: addr = addr.upper()
        elif r < 0.55: addr = " " + addr
        elif r < 0.65: addr = addr + " "
        elif r < 0.75: addr = addr.replace("@","@@")
        elif r < 0.85: addr = addr.replace("@"," @ ")
    return addr

def rand_phone():
    a = random.randint(200,999)
    b = random.randint(200,999)
    c = random.randint(0,9999)
    if random.random() < P_DIRTY_PHONE_BAD:
        # invalid - missing digit, wrong length, garbage
        r = random.random()
        if r < 0.3: return f"{a}-{b}-{c}"  # short last
        if r < 0.6: return f"{a}{c:04d}"   # too short
        if r < 0.8: return f"{a}-{b}-{c:04d}-ext{random.randint(1,999)}"
        return "N/A"
    fmt = random.random()
    if fmt < 0.25: return f"({a}) {b}-{c:04d}"
    if fmt < 0.45: return f"{a}-{b}-{c:04d}"
    if fmt < 0.60: return f"{a}.{b}.{c:04d}"
    if fmt < 0.75: return f"{a}{b}{c:04d}"
    if fmt < 0.85: return f"+1-{a}-{b}-{c:04d}"
    if fmt < 0.93: return f"+1 ({a}) {b}-{c:04d}"
    return f"{a} {b} {c:04d}"

def rand_address():
    num = random.randint(1, 9999)
    street = random.choice(STREET_NAMES)
    if random.random() < 0.30:
        stype = random.choice(STREET_TYPES_DIRTY)
    else:
        stype = random.choice(STREET_TYPES_CLEAN)
    state = random.choice(STATES)
    city = random.choice(CITIES_BY_STATE[state])
    zip5 = random.randint(10000, 99999)
    apt = ""
    if random.random() < 0.25:
        apt = random.choice([f" Apt {random.randint(1,999)}", f" #{random.randint(1,999)}",
                             f" Unit {random.choice('ABCDE')}{random.randint(1,99)}",
                             f", Apt. {random.randint(1,999)}"])
    # occasional weird casing or trailing whitespace
    addr = f"{num} {street} {stype}{apt}, {city}, {state} {zip5}"
    r = random.random()
    if r < 0.02: addr = addr.upper()
    elif r < 0.03: addr = addr.lower()
    elif r < 0.05: addr = addr + "  "
    return addr

def rand_status(canonical):
    if random.random() >= P_STATUS_VARIANT:
        return canonical
    variants = {
        "Active":   ["ACTIVE","active","A","Open","OPEN","open","Actv"],
        "Closed":   ["CLOSED","closed","C","Cls","CLS","close"],
        "Suspended":["SUSPENDED","suspended","S","Susp","SUSP","Frozen"],
        "Pending":  ["PENDING","pending","P","Pend","PEND","new"],
        "Inactive": ["INACTIVE","inactive","I","Inact","Dormant"],
    }
    return random.choice(variants.get(canonical,[canonical]))

def rand_account_number():
    n = "".join(random.choices(string.digits, k=random.choice([10,11,12])))
    if random.random() < P_ACCT_NUM_FORMAT:
        r = random.random()
        if r < 0.5:
            return f"{n[:4]}-{n[4:8]}-{n[8:]}"
        elif r < 0.8:
            return f"{n[:4]} {n[4:8]} {n[8:]}"
        else:
            return f" {n}"  # leading space
    return n

def rand_card_number():
    n = "".join(random.choices(string.digits, k=16))
    if random.random() < P_CARD_NUM_FORMAT:
        r = random.random()
        if r < 0.4:
            return f"{n[:4]}-{n[4:8]}-{n[8:12]}-{n[12:]}"
        elif r < 0.7:
            return f"{n[:4]} {n[4:8]} {n[8:12]} {n[12:]}"
        elif r < 0.9:
            return f"****-****-****-{n[12:]}"  # masked
        else:
            return n[:4] + "X"*8 + n[12:]
    return n

def rand_routing_number():
    return "".join(random.choices(string.digits, k=9))

def rand_date_between(d1, d2):
    if d2 < d1: d1, d2 = d2, d1
    span = (d2 - d1).days
    if span <= 0: return d1
    return d1 + timedelta(days=random.randint(0, span))

def rand_dt_between(d1, d2):
    """Random timestamp between two dates."""
    if d2 < d1: d1, d2 = d2, d1
    span_days = (d2 - d1).days
    if span_days <= 0:
        base = d1
    else:
        base = d1 + timedelta(days=random.randint(0, span_days))
    return datetime.combine(base, datetime.min.time()) + timedelta(
        seconds=random.randint(0, 86399))

def maybe_null(value):
    if random.random() < P_NULL_OPTIONAL:
        return ""
    return value

# ============================================================
# WRITER HELPERS
# ============================================================
def open_writer(name, header):
    f = open(os.path.join(OUT_DIR, f"{name}.csv"), "w", newline="", encoding="utf-8")
    w = csv.writer(f, quoting=csv.QUOTE_MINIMAL)
    w.writerow(header)
    return f, w

# ============================================================
# MAIN
# ============================================================
def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    t_start = datetime.now()
    print(f"[{t_start:%H:%M:%S}] Starting generation -> {OUT_DIR}")

    # ---------- BRANCHES ----------
    branches = []
    fb, wb = open_writer("branch", ["branch_id","branch_name","routing_number","address"])
    for i in range(1, N_BRANCHES+1):
        state = random.choice(STATES)
        city = random.choice(CITIES_BY_STATE[state])
        name = f"{city} {random.choice(['Main','Downtown','North','South','East','West','Plaza','Heights'])} Branch"
        wb.writerow([i, name, rand_routing_number(), rand_address()])
        branches.append(i)
    fb.close()
    print(f"  branches: {N_BRANCHES}")

    # ---------- EMPLOYEES ----------
    employees = []  # list of (employee_id, branch_id, hire_date)
    fe, we = open_writer("employee", ["employee_id","branch_id","first_name","last_name","role","hire_date"])
    for i in range(1, N_EMPLOYEES+1):
        bid = random.choice(branches)
        fn = random.choice(FIRST_NAMES)
        ln = random.choice(LAST_NAMES)
        role = random.choice(EMPLOYEE_ROLES)
        hire = rand_date_between(START_DATE, END_DATE - timedelta(days=30))
        we.writerow([i, bid, maybe_dirty_name(fn), maybe_dirty_name(ln),
                     role if random.random() > P_NULL_OPTIONAL else "",
                     hire.isoformat()])
        employees.append((i, bid, hire))
    fe.close()
    print(f"  employees: {N_EMPLOYEES}")

    # ---------- CUSTOMERS + DEPENDENT TABLES (single streamed pass) ----------
    fc, wc       = open_writer("customer", ["customer_id","first_name","last_name","dob","email","phone","address"])
    fchk, wchk   = open_writer("checking_account", ["checking_account_id","customer_id","branch_id","account_number","open_date","status","balance"])
    fsav, wsav   = open_writer("savings_account",  ["savings_account_id","customer_id","branch_id","account_number","interest_rate","open_date","status","balance"])
    fcrd, wcrd   = open_writer("credit_account",   ["credit_account_id","customer_id","branch_id","account_number","credit_limit","apr","open_date","status","current_balance"])
    fln,  wln    = open_writer("loan_account",     ["loan_account_id","customer_id","branch_id","account_number","loan_type","principal_amount","interest_rate","open_date","maturity_date","status"])
    fbk,  wbk    = open_writer("brokerage_account",["brokerage_account_id","customer_id","branch_id","account_number","account_type","open_date","status","balance"])
    f401, w401   = open_writer("four_oh_one_k_account",["four_oh_one_k_account_id","customer_id","branch_id","account_number","company_match","account_type","open_date","status","balance"])
    frot, wrot   = open_writer("roth_ira",         ["roth_ira_id","customer_id","branch_id","account_number","account_type","open_date","status","balance"])
    fbn,  wbn    = open_writer("beneficiary",      ["beneficiary_id","customer_id","name","bank_name","beneficiary_account_number","relationship"])
    fcd,  wcd    = open_writer("card",             ["card_id","customer_id","checking_account_id","credit_account_id","brokerage_account_id","four_oh_one_k_account_id","card_type","card_number","expiration_date","status"])
    ftx,  wtx    = open_writer("transaction",      ["transaction_id","customer_id","employee_id","checking_account_id","savings_account_id","credit_account_id","loan_account_id","brokerage_account_id","four_oh_one_k_account_id","roth_ira_id","transaction_type","amount","transaction_date","description"])

    # id counters
    chk_id = sav_id = crd_id = ln_id = bk_id = k401_id = rot_id = 0
    bn_id = cd_id = tx_id = 0

    # for duplicate-customer dirty pattern, remember a few customers
    dup_pool = []

    cust_id = 0
    progress_step = max(1, N_CUSTOMERS // 20)

    for _ in range(N_CUSTOMERS):
        cust_id += 1

        # decide if this is a duplicate of an earlier customer (different id, same person)
        if dup_pool and random.random() < P_DUP_CUSTOMER:
            base = random.choice(dup_pool)
            fn, ln, dob, addr = base
            email = rand_email(fn, ln)
            phone = rand_phone()
        else:
            fn = random.choice(FIRST_NAMES)
            ln = random.choice(LAST_NAMES)
            # age 18-90
            age_years = random.randint(18, 90)
            dob = END_DATE - timedelta(days=age_years*365 + random.randint(0,364))
            addr = rand_address()
            email = rand_email(fn, ln)
            phone = rand_phone()
            if len(dup_pool) < 500 and random.random() < 0.01:
                dup_pool.append((fn, ln, dob, addr))

        wc.writerow([
            cust_id,
            maybe_dirty_name(fn),
            maybe_dirty_name(ln),
            maybe_null(dob.isoformat()),
            maybe_null(email),
            maybe_null(phone),
            maybe_null(addr),
        ])

        # customer joined the bank somewhere between start and ~6 months before end
        join = rand_date_between(START_DATE, END_DATE - timedelta(days=180))

        # accounts this customer holds; collect (kind, id, open_date) for transaction phase
        accts = []

        def acct_open_date(prob_future_ok=True):
            d = rand_date_between(join, END_DATE)
            if prob_future_ok and random.random() < P_FUTURE_OPENDATE:
                d = END_DATE + timedelta(days=random.randint(1, 365))
            return d

        if random.random() < P_CHECKING:
            chk_id += 1
            od = acct_open_date()
            bal = round(random.uniform(0, 25000), 2)
            if random.random() < P_NEG_BALANCE_BUG: bal = -abs(bal)
            wchk.writerow([chk_id, cust_id, random.choice(branches),
                           rand_account_number(), od.isoformat(),
                           rand_status("Active") if random.random() > 0.1 else rand_status("Closed"),
                           bal])
            accts.append(("checking", chk_id, od))

        if random.random() < P_SAVINGS:
            sav_id += 1
            od = acct_open_date()
            bal = round(random.uniform(0, 80000), 2)
            if random.random() < P_NEG_BALANCE_BUG: bal = -abs(bal)
            ir = round(random.uniform(0.01, 4.50), 2)
            wsav.writerow([sav_id, cust_id, random.choice(branches),
                           rand_account_number(), ir, od.isoformat(),
                           rand_status("Active") if random.random() > 0.08 else rand_status("Closed"),
                           bal])
            accts.append(("savings", sav_id, od))

        if random.random() < P_CREDIT:
            crd_id += 1
            od = acct_open_date()
            limit = random.choice([1000, 2500, 5000, 7500, 10000, 15000, 25000, 50000])
            apr = round(random.uniform(8.99, 29.99), 2)
            cur = round(random.uniform(-500, limit*1.05), 2)  # over-limit possible
            wcrd.writerow([crd_id, cust_id, random.choice(branches),
                           rand_account_number(), limit, apr, od.isoformat(),
                           rand_status("Active") if random.random() > 0.12 else rand_status("Closed"),
                           cur])
            accts.append(("credit", crd_id, od))

        if random.random() < P_LOAN:
            ln_id += 1
            od = acct_open_date()
            term_years = random.choice([3,5,7,10,15,20,30])
            mat = od + timedelta(days=term_years*365)
            if random.random() < P_BAD_MATURITY:
                mat = od - timedelta(days=random.randint(30, 1000))
            ltype = random.choice(LOAN_TYPES)
            principal = round(random.uniform(2000, 500000), 2)
            ir = round(random.uniform(2.5, 12.0), 2)
            wln.writerow([ln_id, cust_id, random.choice(branches),
                          rand_account_number(), ltype, principal, ir,
                          od.isoformat(), mat.isoformat(),
                          rand_status("Active") if random.random() > 0.15 else rand_status("Closed")])
            accts.append(("loan", ln_id, od))

        if random.random() < P_BROKERAGE:
            bk_id += 1
            od = acct_open_date()
            bal = round(random.uniform(500, 500000), 2)
            wbk.writerow([bk_id, cust_id, random.choice(branches),
                          rand_account_number(),
                          random.choice(BROKERAGE_TYPES),
                          od.isoformat(),
                          rand_status("Active") if random.random() > 0.1 else rand_status("Closed"),
                          bal])
            accts.append(("brokerage", bk_id, od))

        if random.random() < P_401K:
            k401_id += 1
            od = acct_open_date()
            bal = round(random.uniform(1000, 800000), 2)
            match = round(random.uniform(0, 6), 2)
            w401.writerow([k401_id, cust_id, random.choice(branches),
                           rand_account_number(), match,
                           random.choice(RETIRE_TYPES_401K),
                           od.isoformat(),
                           rand_status("Active") if random.random() > 0.08 else rand_status("Closed"),
                           bal])
            accts.append(("401k", k401_id, od))

        if random.random() < P_ROTH:
            rot_id += 1
            od = acct_open_date()
            bal = round(random.uniform(500, 300000), 2)
            wrot.writerow([rot_id, cust_id, random.choice(branches),
                           rand_account_number(),
                           random.choice(RETIRE_TYPES_ROTH),
                           od.isoformat(),
                           rand_status("Active") if random.random() > 0.08 else rand_status("Closed"),
                           bal])
            accts.append(("roth", rot_id, od))

        # ---------- BENEFICIARIES ----------
        if random.random() < P_BENEFICIARY:
            n_ben = 1
            while n_ben < 3 and random.random() < EXTRA_BENEFICIARY:
                n_ben += 1
            for _ in range(n_ben):
                bn_id += 1
                bfn = random.choice(FIRST_NAMES)
                bln = random.choice(LAST_NAMES)
                rel = random.choice(RELATIONSHIPS_CLEAN)
                if random.random() < 0.10:
                    rel = random.choice(RELATIONSHIPS_DIRTY)
                wbn.writerow([
                    bn_id, cust_id,
                    maybe_dirty_name(f"{bfn} {bln}"),
                    maybe_null(random.choice(BANK_NAMES)),
                    maybe_null(rand_account_number()),
                    rel
                ])

        # ---------- CARDS ----------
        # find checking & credit & brokerage & 401k account ids if present
        chk_acct = next((a for a in accts if a[0]=="checking"), None)
        crd_acct = next((a for a in accts if a[0]=="credit"), None)
        bk_acct  = next((a for a in accts if a[0]=="brokerage"), None)
        k_acct   = next((a for a in accts if a[0]=="401k"), None)

        if chk_acct and random.random() < P_DEBIT_CARD:
            cd_id += 1
            exp = END_DATE + timedelta(days=random.randint(-365, 365*5))
            wcd.writerow([cd_id, cust_id, chk_acct[1], "", "", "",
                          "Debit", rand_card_number(), exp.isoformat(),
                          rand_status("Active") if random.random() > 0.1 else rand_status("Closed")])
        if crd_acct and random.random() < P_CREDIT_CARD:
            cd_id += 1
            exp = END_DATE + timedelta(days=random.randint(-365, 365*5))
            ctype = random.choice(["Credit","Platinum","Gold","Rewards"])
            wcd.writerow([cd_id, cust_id, "", crd_acct[1], "", "",
                          ctype, rand_card_number(), exp.isoformat(),
                          rand_status("Active") if random.random() > 0.12 else rand_status("Closed")])
        if bk_acct and random.random() < P_BROKERAGE_CARD:
            cd_id += 1
            exp = END_DATE + timedelta(days=random.randint(-365, 365*5))
            wcd.writerow([cd_id, cust_id, "", "", bk_acct[1], "",
                          "Debit", rand_card_number(), exp.isoformat(),
                          rand_status("Active")])
        if k_acct and random.random() < P_401K_CARD:
            cd_id += 1
            exp = END_DATE + timedelta(days=random.randint(-365, 365*5))
            wcd.writerow([cd_id, cust_id, "", "", "", k_acct[1],
                          "Prepaid", rand_card_number(), exp.isoformat(),
                          rand_status("Active")])

        # ---------- TRANSACTIONS ----------
        # for each account, generate transactions across its tenure
        for kind, aid, od in accts:
            tenure_years = max(0.1, (END_DATE - od).days / 365.0)
            base_rate = TXN_RATE[kind]
            # randomize per-account activity
            scale = random.uniform(0.4, 1.6)
            n_tx = int(base_rate * tenure_years * scale)
            if n_tx <= 0:
                continue
            for _ in range(n_tx):
                tx_id += 1
                ts = rand_dt_between(od, END_DATE)
                # transaction type by account kind
                if kind in ("checking","savings"):
                    pool = (TXN_TYPES_DEPOSIT*2 + TXN_TYPES_WITHDRAW*2 +
                            TXN_TYPES_TRANSFER + TXN_TYPES_FEE +
                            (TXN_TYPES_INTEREST if kind=="savings" else []))
                    amt = round(random.uniform(5, 5000) * random.choice([-1,1,1,1]), 2)
                elif kind == "credit":
                    pool = TXN_TYPES_PURCHASE*3 + TXN_TYPES_PAYMENT + TXN_TYPES_FEE + ["Interest Charge"]
                    amt = round(random.uniform(5, 2500), 2)
                elif kind == "loan":
                    pool = ["Loan Disbursement","Principal Payment","Interest Payment","Late Fee"]
                    amt = round(random.uniform(50, 3000), 2)
                elif kind == "brokerage":
                    pool = ["Buy","Sell","Dividend","Fee","Transfer In","Transfer Out"]
                    amt = round(random.uniform(50, 25000), 2)
                elif kind == "401k":
                    pool = ["Contribution","Employer Match","Rollover","Distribution","Dividend"]
                    amt = round(random.uniform(50, 5000), 2)
                else:  # roth
                    pool = ["Contribution","Conversion","Distribution","Dividend"]
                    amt = round(random.uniform(50, 6500), 2)
                ttype = random.choice(pool)

                # employee picked from anywhere; a (very small) percentage with hire_date after txn = dirty
                emp = random.choice(employees)
                emp_id = emp[0]

                desc = random.choice(TXN_DESCRIPTIONS) if random.random() > 0.15 else ""
                if desc is None: desc = ""

                # account-id columns (only the matching one is filled)
                ck_v = aid if kind=="checking" else ""
                sv_v = aid if kind=="savings"  else ""
                cr_v = aid if kind=="credit"   else ""
                ln_v = aid if kind=="loan"     else ""
                bk_v = aid if kind=="brokerage" else ""
                k_v  = aid if kind=="401k"     else ""
                rt_v = aid if kind=="roth"     else ""

                wtx.writerow([tx_id, cust_id, emp_id,
                              ck_v, sv_v, cr_v, ln_v, bk_v, k_v, rt_v,
                              ttype, amt, ts.isoformat(sep=" "), desc])

        if cust_id % progress_step == 0:
            elapsed = (datetime.now()-t_start).total_seconds()
            print(f"  customers: {cust_id}/{N_CUSTOMERS}  txns: {tx_id:,}  elapsed {elapsed:.0f}s")

    for f in (fc, fchk, fsav, fcrd, fln, fbk, f401, frot, fbn, fcd, ftx):
        f.close()

    elapsed = (datetime.now()-t_start).total_seconds()
    print(f"\n[done] {elapsed:.0f}s elapsed")
    print(f"  customers:        {cust_id:,}")
    print(f"  checking:         {chk_id:,}")
    print(f"  savings:          {sav_id:,}")
    print(f"  credit:           {crd_id:,}")
    print(f"  loan:             {ln_id:,}")
    print(f"  brokerage:        {bk_id:,}")
    print(f"  401k:             {k401_id:,}")
    print(f"  roth_ira:         {rot_id:,}")
    print(f"  beneficiary:      {bn_id:,}")
    print(f"  card:             {cd_id:,}")
    print(f"  transaction:      {tx_id:,}")

if __name__ == "__main__":
    main()
