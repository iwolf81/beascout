#!/usr/bin/env python3
"""
Name and contact generation utilities for anonymizing Key Three data.
Generates realistic but fake names, emails, and phone numbers for testing.
"""

import random
from typing import Tuple, List

# Common first names for realistic generation
FIRST_NAMES = [
    "James", "Mary", "John", "Patricia", "Robert", "Jennifer", "Michael", "Linda",
    "William", "Elizabeth", "David", "Barbara", "Richard", "Susan", "Joseph", "Jessica",
    "Thomas", "Sarah", "Christopher", "Karen", "Charles", "Nancy", "Daniel", "Lisa",
    "Matthew", "Betty", "Anthony", "Helen", "Mark", "Sandra", "Donald", "Donna",
    "Steven", "Carol", "Paul", "Ruth", "Andrew", "Sharon", "Joshua", "Michelle",
    "Kenneth", "Laura", "Kevin", "Sarah", "Brian", "Kimberly", "George", "Deborah",
    "Timothy", "Dorothy", "Ronald", "Lisa", "Jason", "Nancy", "Edward", "Karen",
    "Jeffrey", "Betty", "Ryan", "Helen", "Jacob", "Sandra", "Gary", "Donna",
    "Nicholas", "Carol", "Eric", "Ruth", "Jonathan", "Sharon", "Stephen", "Michelle",
    "Larry", "Laura", "Justin", "Sarah", "Scott", "Kimberly", "Brandon", "Deborah",
    "Benjamin", "Dorothy", "Samuel", "Amy", "Gregory", "Angela", "Alexander", "Ashley",
    "Patrick", "Brenda", "Frank", "Emma", "Raymond", "Olivia", "Jack", "Cynthia",
    "Dennis", "Marie", "Jerry", "Janet", "Tyler", "Catherine", "Aaron", "Frances",
    "Jose", "Christine", "Henry", "Samantha", "Adam", "Debra", "Douglas", "Rachel"
]

LAST_NAMES = [
    "Smith", "Johnson", "Williams", "Brown", "Jones", "Garcia", "Miller", "Davis",
    "Rodriguez", "Martinez", "Hernandez", "Lopez", "Gonzalez", "Wilson", "Anderson", "Thomas",
    "Taylor", "Moore", "Jackson", "Martin", "Lee", "Perez", "Thompson", "White",
    "Harris", "Sanchez", "Clark", "Ramirez", "Lewis", "Robinson", "Walker", "Young",
    "Allen", "King", "Wright", "Scott", "Torres", "Nguyen", "Hill", "Flores",
    "Green", "Adams", "Nelson", "Baker", "Hall", "Rivera", "Campbell", "Mitchell",
    "Carter", "Roberts", "Gomez", "Phillips", "Evans", "Turner", "Diaz", "Parker",
    "Cruz", "Edwards", "Collins", "Reyes", "Stewart", "Morris", "Morales", "Murphy",
    "Cook", "Rogers", "Gutierrez", "Ortiz", "Morgan", "Cooper", "Peterson", "Bailey",
    "Reed", "Kelly", "Howard", "Ramos", "Kim", "Cox", "Ward", "Richardson",
    "Watson", "Brooks", "Chavez", "Wood", "James", "Bennett", "Gray", "Mendoza",
    "Ruiz", "Hughes", "Price", "Alvarez", "Castillo", "Sanders", "Patel", "Myers",
    "Long", "Ross", "Foster", "Jimenez", "Powell", "Jenkins", "Perry", "Russell"
]

# Email domains for realistic fake emails
EMAIL_DOMAINS = [
    "gmail.com", "yahoo.com", "outlook.com", "hotmail.com", "icloud.com", 
    "comcast.net", "verizon.net", "aol.com", "msn.com", "live.com"
]

# Massachusetts area codes for phone numbers
MA_AREA_CODES = ["617", "978", "508", "413", "781", "339", "857", "774", "351"]


def generate_name() -> Tuple[str, str]:
    """Generate a random first and last name combination."""
    first_name = random.choice(FIRST_NAMES)
    last_name = random.choice(LAST_NAMES)
    return first_name, last_name


def generate_full_name() -> str:
    """Generate a full name with middle initial (sometimes)."""
    first_name, last_name = generate_name()
    
    # 30% chance of middle initial
    if random.random() < 0.3:
        middle_initial = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        return f"{first_name} {middle_initial} {last_name}"
    else:
        return f"{first_name} {last_name}"


def generate_email(first_name: str = None, last_name: str = None) -> str:
    """Generate a realistic fake email address."""
    if not first_name or not last_name:
        first_name, last_name = generate_name()
    
    domain = random.choice(EMAIL_DOMAINS)
    
    # Various email patterns
    patterns = [
        f"{first_name.lower()}.{last_name.lower()}@{domain}",
        f"{first_name.lower()}{last_name.lower()}@{domain}",
        f"{first_name[0].lower()}{last_name.lower()}@{domain}",
        f"{first_name.lower()}{random.randint(1, 999)}@{domain}",
        f"{first_name.lower()}.{last_name.lower()}{random.randint(1, 99)}@{domain}"
    ]
    
    return random.choice(patterns)


def generate_ma_phone() -> str:
    """Generate a Massachusetts phone number with 555 exchange."""
    area_code = random.choice(MA_AREA_CODES)
    # Always use 555 exchange as specified in requirements
    exchange = "555"
    # Last 4 digits
    last_four = f"{random.randint(0, 9999):04d}"
    
    # Format as (XXX) 555-XXXX
    return f"({area_code}) {exchange}-{last_four}"


def generate_anonymous_contact() -> dict:
    """Generate a complete set of anonymous contact information."""
    first_name, last_name = generate_name()
    full_name = f"{first_name} {last_name}"
    
    # 30% chance of middle initial
    if random.random() < 0.3:
        middle_initial = random.choice("ABCDEFGHIJKLMNOPQRSTUVWXYZ")
        full_name = f"{first_name} {middle_initial} {last_name}"
    
    email = generate_email(first_name, last_name)
    phone = generate_ma_phone()
    
    return {
        "name": full_name,
        "email": email, 
        "phone": phone,
        "first_name": first_name,
        "last_name": last_name
    }


def generate_contact_batch(count: int) -> List[dict]:
    """Generate a batch of unique anonymous contacts."""
    contacts = []
    used_names = set()
    used_emails = set()
    
    attempts = 0
    while len(contacts) < count and attempts < count * 3:  # Prevent infinite loop
        contact = generate_anonymous_contact()
        
        # Ensure uniqueness
        if contact["name"] not in used_names and contact["email"] not in used_emails:
            contacts.append(contact)
            used_names.add(contact["name"])
            used_emails.add(contact["email"])
        
        attempts += 1
    
    return contacts


if __name__ == "__main__":
    # Test the generators
    print("Testing name generation:")
    for _ in range(5):
        print(f"  {generate_full_name()}")
    
    print("\nTesting email generation:")
    for _ in range(5):
        print(f"  {generate_email()}")
    
    print("\nTesting phone generation:")
    for _ in range(5):
        print(f"  {generate_ma_phone()}")
    
    print("\nTesting complete contact generation:")
    for contact in generate_contact_batch(3):
        print(f"  {contact['name']} | {contact['email']} | {contact['phone']}")