import re

def normalize_company_name(name):
    """
    Normalize company names by:
    1. Converting to lowercase
    2. Removing legal designations
    3. Removing punctuation
    4. Removing extra whitespace
    5. Handling special cases
    """
    # Convert to lowercase
    name = name.lower()

    # Remove legal designations and common words
    legal_words = [
        'inc', 'incorporated', 'corporation', 'corp', 'llc', 'limited', 
        'ltd', 'co', 'intl',]
        #company', 'group', 'holdings', 'international', 
        #'intl', 'technologies', 'technology', 'solutions'
    

    # Remove these words
    for word in legal_words:
        name = re.sub(rf'\b{word}\b', '', name)

    # Remove punctuation except ampersands
    name = re.sub(r'[^\w\s&]', '', name)

    # Handle specific known variations
    name_mappings = {
        'walmart': 'Walmart',
        'walmart inc': 'Walmart',
        'wal-mart': 'Walmart',
        'amazon': 'Amazon',
        'amazon.com': 'Amazon',
        'amazon web services': 'Amazon',
        'apple': 'Apple',
        'apple inc': 'Apple',
        'microsoft': 'Microsoft',
        'microsoft corporation': 'Microsoft',
        'google': 'Google',
        'google llc': 'Google',
        'facebook': 'Facebook',
        'meta': 'Meta',
        'meta inc': 'Meta',
        'netflix': 'Netflix',
        'twitter': 'Twitter',
        'tiktok': 'TikTok',
        'starbucks': 'Starbucks',
        'coca cola': 'Coca Cola',
        'cvs': 'CVS',
        'cvs health': 'CVS Health'
    }

    # Apply specific mappings
    for key, value in name_mappings.items():
        if key in name:
            return value
        
    # Strip and collapse whitespace
    name = ' '.join(name.split()).title()

    return name

def process_company_names(input_file, output_file):
    """
    Process company names from input file and write to output file
    """
    # Read the input file
    with open(input_file, 'r', encoding='utf-8') as file:
        companies = file.read().splitlines()

    # Normalize company names
    normalized_companies = [normalize_company_name(company) for company in companies]

    # Write to output file
    with open(output_file, 'w', encoding='utf-8') as file:
        for company in normalized_companies:
            file.write(f"{company}\n")

    # Print statistics
    unique_companies_count = len(set(normalized_companies))
    print(f"Original number of companies: {len(companies)}")
    print(f"Unique normalized companies: {unique_companies_count}")

    return normalized_companies