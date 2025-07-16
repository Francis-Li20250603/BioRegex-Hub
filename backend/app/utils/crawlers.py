import httpx
from selectolax.parser import HTMLParser
import json
from datetime import datetime
from sqlmodel import Session, select
from app.database import engine
from app.models import Rule
import re
import logging
from app.config import settings

logger = logging.getLogger(__name__)

# FDA-specific regex patterns
FDA_PATTERNS = {
    "PATIENT_ID": r"\b[A-Z]{3}\d{5}\b",
    "DATE": r"\b\d{4}-\d{2}-\d{2}\b",
    "NDC": r"\b\d{4}-\d{4}-\d{2}|\d{5}-\d{3}-\d{2}\b"
}

# EMA-specific regex patterns
EMA_PATTERNS = {
    "PATIENT_ID": r"\bEU-\d{3}-\d{4}-\d{4}\b",
    "DATE": r"\b\d{2}/\d{2}/\d{4}\b",
    "PRODUCT_CODE": r"\bEMEA/\d{5}/\d{4}\b"
}

def extract_regex_from_text(text: str, region: str) -> list:
    patterns = FDA_PATTERNS if region == "FDA" else EMA_PATTERNS
    found_patterns = []
    
    for data_type, pattern in patterns.items():
        if re.search(pattern, text):
            found_patterns.append({
                "pattern": pattern,
                "data_type": data_type,
                "region": region
            })
    
    return found_patterns

def crawl_fda():
    logger.info("Starting FDA crawl")
    try:
        response = httpx.get(settings.FDA_GUIDANCE_URL, timeout=30)
        if response.status_code != 200:
            logger.error(f"FDA site returned {response.status_code}")
            return
        
        tree = HTMLParser(response.text)
        documents = []
        
        # Extract document links - example selector
        for item in tree.css('.fda-guidance-list-item'):
            title = item.css_first('h3 a').text().strip()
            link = "https://www.fda.gov" + item.css_first('h3 a').attrs['href']
            date_str = item.css_first('.date').text().strip()
            pub_date = datetime.strptime(date_str, '%B %d, %Y').date()
            documents.append({"title": title, "url": link, "date": pub_date})
        
        # Process each document
        new_rules = []
        with Session(engine) as db:
            for doc in documents[:5]:  # Limit for demo
                # Skip if already exists
                existing = db.exec(
                    select(Rule).where(Rule.reference_url == doc['url'])
                ).first()
                if existing:
                    continue
                
                # Download document content
                try:
                    doc_resp = httpx.get(doc['url'], timeout=30)
                    if doc_resp.status_code == 200:
                        doc_text = doc_resp.text[:10000]  # First 10k chars
                        patterns = extract_regex_from_text(doc_text, "FDA")
                        
                        for pattern in patterns:
                            rule = Rule(
                                pattern=pattern["pattern"],
                                description=f"Auto-generated from FDA guidance: {doc['title']}",
                                data_type=pattern["data_type"],
                                region="FDA",
                                reference_url=doc['url']
                            )
                            new_rules.append(rule)
                except Exception as e:
                    logger.error(f"Error processing FDA doc {doc['url']}: {str(e)}")
            
            # Add new rules to database
            for rule in new_rules:
                db.add(rule)
            db.commit()
            
        logger.info(f"Found {len(new_rules)} new rules from FDA")
        return new_rules
    except Exception as e:
        logger.exception("Error in FDA crawl")
        return []

def crawl_ema():
    logger.info("Starting EMA crawl")
    try:
        response = httpx.get(settings.EMA_GUIDANCE_URL, timeout=30)
        if response.status_code != 200:
            logger.error(f"EMA site returned {response.status_code}")
            return
        
        # EMA site parsing would be implemented similarly
        # Placeholder implementation
        return []
    except Exception as e:
        logger.exception("Error in EMA crawl")
        return []
