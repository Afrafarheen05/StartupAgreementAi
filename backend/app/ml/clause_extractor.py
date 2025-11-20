"""
Clause Extractor Module
Identifies and classifies different types of clauses in startup agreements
"""
import re
from typing import List, Dict
import spacy
from collections import defaultdict


class ClauseExtractor:
    """Extract and classify clauses from agreement text"""
    
    def __init__(self):
        # Load spaCy model (will download if not present)
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except:
            # Fallback to basic processing if spaCy model not available
            self.nlp = None
        
        # Define clause keywords and patterns
        self.clause_patterns = {
            "Liquidation Preference": {
                "keywords": ["liquidation", "preference", "distribution", "proceeds", "participating", "non-participating"],
                "patterns": [
                    r"liquidation\s+preference",
                    r"distribution\s+of\s+proceeds",
                    r"participating\s+preferred",
                    r"\d+x\s+preference"
                ]
            },
            "Anti-Dilution": {
                "keywords": ["anti-dilution", "dilution protection", "price adjustment", "weighted average", "full ratchet"],
                "patterns": [
                    r"anti[- ]dilution",
                    r"dilution\s+protection",
                    r"full\s+ratchet",
                    r"weighted\s+average"
                ]
            },
            "Board Control": {
                "keywords": ["board", "director", "appointment", "board seat", "board composition", "voting"],
                "patterns": [
                    r"board\s+of\s+directors",
                    r"board\s+composition",
                    r"director\s+appointment",
                    r"board\s+seat"
                ]
            },
            "Vesting": {
                "keywords": ["vesting", "cliff", "acceleration", "vesting schedule", "unvested"],
                "patterns": [
                    r"vesting\s+schedule",
                    r"\d+[- ]year\s+vesting",
                    r"cliff\s+period",
                    r"acceleration\s+clause"
                ]
            },
            "IP Assignment": {
                "keywords": ["intellectual property", "IP", "assignment", "ownership", "patents", "trademarks", "copyright"],
                "patterns": [
                    r"intellectual\s+property",
                    r"IP\s+assignment",
                    r"patent\s+rights",
                    r"ownership\s+of.*(?:IP|intellectual\s+property)"
                ]
            },
            "Drag-Along Rights": {
                "keywords": ["drag-along", "drag along", "forced sale", "tag-along"],
                "patterns": [
                    r"drag[- ]along",
                    r"forced\s+to\s+sell",
                    r"require.*sell.*shares"
                ]
            },
            "Information Rights": {
                "keywords": ["information rights", "financial statements", "reporting", "quarterly", "annual report"],
                "patterns": [
                    r"information\s+rights",
                    r"financial\s+statements",
                    r"quarterly\s+report",
                    r"annual\s+audit"
                ]
            },
            "No-Shop Clause": {
                "keywords": ["no-shop", "exclusivity", "solicitation", "competing offers"],
                "patterns": [
                    r"no[- ]shop",
                    r"exclusivity\s+period",
                    r"not\s+solicit",
                    r"competing\s+offer"
                ]
            },
            "Pro-Rata Rights": {
                "keywords": ["pro-rata", "pro rata", "participation rights", "follow-on"],
                "patterns": [
                    r"pro[- ]rata",
                    r"participation\s+right",
                    r"follow[- ]on\s+investment"
                ]
            },
            "Pay-to-Play": {
                "keywords": ["pay-to-play", "pay to play", "participation requirement"],
                "patterns": [
                    r"pay[- ]to[- ]play",
                    r"must\s+participate",
                    r"participation\s+requirement"
                ]
            },
            "Conversion Rights": {
                "keywords": ["conversion", "convert", "conversion rate", "conversion price"],
                "patterns": [
                    r"conversion\s+right",
                    r"convert.*shares",
                    r"conversion\s+ratio"
                ]
            },
            "Redemption Rights": {
                "keywords": ["redemption", "redeem", "buyback", "repurchase"],
                "patterns": [
                    r"redemption\s+right",
                    r"right\s+to\s+redeem",
                    r"buyback\s+right"
                ]
            },
            "Representations & Warranties": {
                "keywords": ["representations", "warranties", "represent and warrant", "authority"],
                "patterns": [
                    r"representations?\s+and\s+warranties",
                    r"represent\s+and\s+warrant",
                    r"company\s+represents"
                ]
            },
            "Voting Rights": {
                "keywords": ["voting", "vote", "approval", "consent", "supermajority"],
                "patterns": [
                    r"voting\s+right",
                    r"require.*approval",
                    r"supermajority",
                    r"consent\s+of.*investor"
                ]
            },
            "Exit Rights": {
                "keywords": ["exit", "sale", "acquisition", "merger", "IPO"],
                "patterns": [
                    r"exit\s+right",
                    r"sale\s+of\s+company",
                    r"merger\s+or\s+acquisition",
                    r"initial\s+public\s+offering"
                ]
            }
        }
    
    def extract_clauses(self, text: str, sections: List[Dict] = None) -> List[Dict]:
        """
        Extract and classify clauses from agreement text
        Returns list of clause dictionaries
        """
        clauses = []
        
        # Use sections if provided, otherwise create from full text
        if not sections:
            sections = self._create_basic_sections(text)
        
        for section in sections:
            section_text = section.get('text', '')
            
            # Identify clause type
            clause_type = self._identify_clause_type(section_text)
            
            # Extract entities if spaCy is available
            entities = self._extract_entities(section_text) if self.nlp else []
            
            # Extract key terms
            key_terms = self._extract_key_terms(section_text, clause_type)
            
            clause = {
                'id': len(clauses) + 1,
                'type': clause_type,
                'text': section_text[:500],  # First 500 chars
                'full_text': section_text,
                'position': section.get('position', 0),
                'entities': entities,
                'key_terms': key_terms,
                'title': section.get('title', '')
            }
            
            clauses.append(clause)
        
        return clauses
    
    def _identify_clause_type(self, text: str) -> str:
        """Identify the type of clause using keywords and patterns"""
        text_lower = text.lower()
        scores = defaultdict(int)
        
        for clause_type, config in self.clause_patterns.items():
            # Score based on keywords
            for keyword in config['keywords']:
                if keyword.lower() in text_lower:
                    scores[clause_type] += 2
            
            # Score based on regex patterns
            for pattern in config['patterns']:
                if re.search(pattern, text_lower, re.IGNORECASE):
                    scores[clause_type] += 3
        
        if scores:
            # Return highest scoring clause type
            return max(scores.items(), key=lambda x: x[1])[0]
        
        return "General Clause"
    
    def _extract_entities(self, text: str) -> List[Dict]:
        """Extract named entities using spaCy"""
        if not self.nlp:
            return []
        
        try:
            doc = self.nlp(text[:1000])  # Limit text length for performance
            entities = []
            
            for ent in doc.ents:
                if ent.label_ in ['ORG', 'PERSON', 'MONEY', 'PERCENT', 'DATE']:
                    entities.append({
                        'text': ent.text,
                        'label': ent.label_,
                        'start': ent.start_char,
                        'end': ent.end_char
                    })
            
            return entities
        except:
            return []
    
    def _extract_key_terms(self, text: str, clause_type: str) -> List[str]:
        """Extract key terms relevant to the clause type"""
        terms = []
        
        # Numbers (percentages, multiples)
        numbers = re.findall(r'\d+(?:\.\d+)?[xX%]?', text)
        terms.extend(numbers[:5])  # Limit to 5
        
        # Specific terms based on clause type
        if clause_type == "Liquidation Preference":
            terms.extend(re.findall(r'(?:participating|non-participating)', text, re.IGNORECASE))
        elif clause_type == "Anti-Dilution":
            terms.extend(re.findall(r'(?:full ratchet|weighted average)', text, re.IGNORECASE))
        elif clause_type == "Vesting":
            terms.extend(re.findall(r'\d+[- ](?:year|month)', text, re.IGNORECASE))
        
        return list(set(terms))  # Remove duplicates
    
    def _create_basic_sections(self, text: str) -> List[Dict]:
        """Create basic sections by splitting text into paragraphs"""
        paragraphs = text.split('\n\n')
        sections = []
        
        position = 0
        for i, para in enumerate(paragraphs):
            if len(para.strip()) > 50:  # Minimum length
                sections.append({
                    'title': f'Section {i+1}',
                    'text': para.strip(),
                    'position': position
                })
                position += len(para) + 2
        
        return sections
    
    def get_clause_statistics(self, clauses: List[Dict]) -> Dict:
        """Get statistics about extracted clauses"""
        stats = {
            'total_clauses': len(clauses),
            'clause_types': defaultdict(int),
            'has_entities': 0,
            'avg_length': 0
        }
        
        total_length = 0
        for clause in clauses:
            stats['clause_types'][clause['type']] += 1
            if clause.get('entities'):
                stats['has_entities'] += 1
            total_length += len(clause.get('full_text', ''))
        
        if clauses:
            stats['avg_length'] = total_length // len(clauses)
        
        stats['clause_types'] = dict(stats['clause_types'])
        return stats
