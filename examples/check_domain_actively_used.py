"""
    Check if a domain is actively used.
    A domain is actively used if it contains other records than:
    - The standard default record:
        - Mail hardening record (SPF/DKIM/DMARC/Null MX)
        - Apex NS records
    - Cloudfloor redirection
"""
