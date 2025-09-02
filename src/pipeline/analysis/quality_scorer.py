#!/usr/bin/env python3
"""
BeAScout Unit Quality Scoring System

Analyzes unit information completeness and generates quality scores with 
recommendation identifiers for Key Three outreach.

Usage:
    python src/analysis/quality_scorer.py data/raw/all_units_01720.json
"""

import json
import re
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ScoringWeights:
    """Scoring weights by unit type - 100% from required fields only"""
    # Standard units (Packs, Troops, Ships, Posts, Clubs): 4 required fields at 25% each
    STANDARD_REQUIRED = {
        'meeting_location': 25.0,
        'meeting_day': 25.0,
        'meeting_time': 25.0,
        'contact_email': 25.0
    }
    
    # Specialized units (Crews only): 5 required fields at 20% each
    SPECIALIZED_REQUIRED = {
        'meeting_location': 20.0,
        'meeting_day': 20.0,
        'meeting_time': 20.0,
        'contact_email': 20.0,
        'specialty': 20.0
    }
    
    # Recommended fields are now informational only (no scoring impact)
    RECOMMENDED = {
        'contact_person': 0.0,
        'phone_number': 0.0,
        'website': 0.0,
        'description': 0.0
    }


class UnitQualityScorer:
    """Scores unit information completeness and generates recommendations"""
    
    def __init__(self):
        self.weights = ScoringWeights()
        self.recommendation_map = {
            # Required field recommendations
            'REQUIRED_MISSING_LOCATION': "Add meeting location with street address.",
            'REQUIRED_MISSING_DAY': "Add meeting day(s) to description.",
            'REQUIRED_MISSING_TIME': "Add meeting time(s) to description.",
            'REQUIRED_MISSING_EMAIL': "Add contact email address.",
            'REQUIRED_MISSING_SPECIALTY': "Add specialty information for Venturing Crew.",
            
            # Recommended field recommendations
            'RECOMMENDED_MISSING_CONTACT': "Add contact person name.",
            'RECOMMENDED_MISSING_PHONE': "Add contact phone number.",
            'RECOMMENDED_MISSING_WEBSITE': "Add unit-specific website.",
            
            # Data quality recommendations
            'QUALITY_POBOX_LOCATION': "Replace PO Box with physical meeting location.",
            'QUALITY_PERSONAL_EMAIL': "Use unit-specific email instead of personal email.",
            'QUALITY_UNIT_ADDRESS': "Meeting location should be in address field, not description.",
            
            # Content quality recommendations
            'CONTENT_MISSING_DESCRIPTION': "Add informative and inviting unit description."
        }
    
    def is_specialized_unit(self, unit: Dict[str, Any]) -> bool:
        """Check if unit is specialized (requires specialty field): Crew only"""
        unit_type = unit.get('unit_type', '').lower()
        return unit_type == 'crew'
    
    def is_field_present(self, unit: Dict[str, Any], field: str) -> bool:
        """Check if field has meaningful content"""
        value = unit.get(field, '')
        if not isinstance(value, str):
            return False
        return bool(value.strip())
    
    def is_pobox_location(self, location: str) -> bool:
        """Check if location is ONLY a PO Box (no street address)"""
        if not location:
            return False
        
        # Common PO Box patterns
        pobox_patterns = [
            r'\bP\.?O\.?\s*Box\b',
            r'\bPO\s*Box\b',
            r'\bPost\s*Office\s*Box\b'
        ]
        
        has_pobox = any(re.search(pattern, location, re.IGNORECASE) for pattern in pobox_patterns)
        
        if not has_pobox:
            return False  # No PO Box found
        
        # Check if there's also a street address (number + street name)
        street_patterns = [
            r'\d+\s+[A-Za-z\s]+(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Boulevard|Blvd|Way|Circle|Cir)',
            r'\d+\s+[A-Za-z\s]+(?:Street|St|Road|Rd|Avenue|Ave|Lane|Ln|Drive|Dr|Boulevard|Blvd|Way|Circle|Cir)\b'
        ]
        
        has_street_address = any(re.search(pattern, location, re.IGNORECASE) for pattern in street_patterns)
        
        # Only flag as PO Box location if there's NO street address
        return not has_street_address
    
    def is_personal_email(self, email: str, unit_data: Dict[str, Any] = None) -> bool:
        """Check if email appears to be personal rather than unit-specific"""
        if not email:
            return False
        
        # Extract the local part (before @) for analysis
        local_part = email.split('@')[0].lower()
        
        # Extract unit number for comparison if available
        unit_number = None
        if unit_data:
            unit_num_str = unit_data.get('unit_number', '')
            if unit_num_str:
                # Remove leading zeros and convert to int for matching
                try:
                    unit_number = int(unit_num_str.lstrip('0') or '0')
                except ValueError:
                    unit_number = None
        
        # FIRST: Check for unit-specific patterns that should override personal detection
        unit_role_patterns = [
            r'^scoutmaster',
            r'^cubmaster', 
            r'^committee',
            r'^beascout',  # Platform-specific email
            r'^secretary',
            r'^info',
            r'^admin',
            r'bsa[\.\w]*troop',      # BSA.TROOP patterns
            r'pack\d+',              # pack + number patterns
            r'troop\d+',             # troop + number patterns  
            r'crew\d+',              # crew + number patterns
            r'ship\d+',              # ship + number patterns
            r'den\.leader',          # den.leader patterns
            r'gardnerscouting',      # specific unit patterns like GardnerScouting
            r'\w*troop\d+\w*',       # general troop + number patterns
            r'\w*pack\d+\w*',        # general pack + number patterns
        ]
        
        is_unit_role = any(re.search(pattern, local_part) 
                          for pattern in unit_role_patterns)
        
        if is_unit_role:
            return False  # Unit role emails are not personal
        
        # SECOND: Check for personal identifier patterns FIRST (they override unit patterns)
        personal_patterns = [
            r'[a-z]+\.[a-z]+',             # first.last format anywhere (overrides unit context)
            r'[a-z]+\.[a-z]+\.[a-z]+',     # first.middle.last anywhere  
            r'^[a-z]{3}$',                 # 3-letter initials (like DRD)
            r'[a-z]+[a-z]+rose',           # compound personal names like "carlsuzannerose"
        ]
        
        has_personal_identifier = any(re.search(pattern, local_part) 
                                    for pattern in personal_patterns)
        
        # Also check for obvious personal/family domain names
        full_email_lower = email.lower()
        personal_domain_patterns = [
            r'@.*family\.com$',            # @grindleyfamily.com 
            r'@.*currier\.us$',            # @currier.us
            r'@.*boutwellowens\.com$',     # @boutwellowens.com
            r'@.*micro-monkey\.com$',      # @micro-monkey.com
        ]
        
        has_personal_domain = any(re.search(pattern, full_email_lower) 
                                for pattern in personal_domain_patterns)
        
        # If has clear personal identifiers or personal domains, it's personal regardless of unit context
        if has_personal_identifier or has_personal_domain:
            return True
        
        # THIRD: Check for unit-only identifiers (no personal names mixed in)
        # These are clearly unit emails with numbers or other patterns
        unit_only_patterns = [
            r'^[a-z]*pack\d+[a-z]*$',           # pack62, westfordpack100, etc.
            r'^[a-z]*troop\d+[a-z]*$',          # troop100, etc.
            r'^[a-z]*crew\d+[a-z]*$',           # crew100, etc.
            r'^[a-z]*ship\d+[a-z]*$',           # ship100, etc.
            r'^[a-z]*scouts?[a-z]*$',           # scouts, ayerscouts, etc.
            r'^cubscout[a-z]*pack\d+[a-z]*$',   # cubscoutchelmsfordpack81, etc.
            r'^[a-z]*scoutmaster\d*[a-z]*$',    # scoutmaster1gstow, etc.
        ]
        
        has_unit_only_identifier = any(re.search(pattern, local_part) 
                                     for pattern in unit_only_patterns)
        
        if has_unit_only_identifier:
            return False  # Clear unit-only identifier - not personal
            
        # FOURTH: Check for unit context (unit numbers and town names) to avoid false positives
        # First check for unit numbers in the email to avoid false positives
        if unit_number:
            # Look for unit number anywhere in email (with or without leading zeros)
            unit_patterns = [
                rf'\b0*{unit_number}\b',  # unit number with optional leading zeros
                rf'^{unit_number}[a-z]',  # unit number at start followed by letters (130scoutmaster)
                rf'[a-z]{unit_number}[a-z]', # unit number embedded in letters (troop195scoutmaster)
            ]
            
            has_unit_number = any(re.search(pattern, local_part) for pattern in unit_patterns)
            if has_unit_number:
                return False  # Contains unit number - not personal
        
        # Check for unit town name in email to avoid false positives
        if unit_data:
            unit_town = unit_data.get('unit_town', '').lower()
            if unit_town and len(unit_town) >= 4:  # Only check meaningful town names
                # Look for town name in email local part
                town_pattern = rf'\b{re.escape(unit_town)}\b'
                if re.search(town_pattern, local_part):
                    return False  # Contains unit town name - likely unit-specific
        
        ambiguous_personal_patterns = [
            r'^[a-z]{2,3}[a-z]{4,8}$',     # initials + name (2-3 chars + 4-8 chars)
            r'[a-z]+[0-9]{2,4}$',          # ends with name + year/numbers (but check unit number first)
            r'[a-z]+[0-9]{1,3}$',          # ends with name + small numbers (but check unit number first)
        ]
        
        has_ambiguous_personal = any(re.search(pattern, local_part) 
                                   for pattern in ambiguous_personal_patterns)
        
        # If has ambiguous personal patterns, it's personal
        if has_ambiguous_personal:
            return True
        
        # FOURTH: For emails without unit or personal identifiers, check personal domains
        personal_domains = [
            r'@gmail\.com$',
            r'@yahoo\.com$', 
            r'@hotmail\.com$',
            r'@aol\.com$',
            r'@comcast\.net$'
        ]
        
        is_personal_domain = any(re.search(pattern, email, re.IGNORECASE) 
                                for pattern in personal_domains)
        
        # If on personal domain with no unit identifiers, it's personal
        return is_personal_domain
    
    def score_unit(self, unit: Dict[str, Any]) -> Tuple[float, List[str]]:
        """Score a single unit and return score and recommendations"""
        recommendations = []
        is_specialized = self.is_specialized_unit(unit)
        
        # Get appropriate required field weights
        required_weights = self.weights.SPECIALIZED_REQUIRED if is_specialized else self.weights.STANDARD_REQUIRED
        
        # Start with 100% base score (sum of all required field weights)
        base_score = sum(required_weights.values())
        score = base_score
        
        # Process required fields - deduct for missing fields
        for field, weight in required_weights.items():
            if field == 'specialty' and not is_specialized:
                continue  # Skip specialty for non-crew units
                
            if not self.is_field_present(unit, field):
                # Missing required field - deduct full weight
                score -= weight
                if field == 'meeting_location':
                    recommendations.append('REQUIRED_MISSING_LOCATION')
                elif field == 'meeting_day':
                    recommendations.append('REQUIRED_MISSING_DAY')
                elif field == 'meeting_time':
                    recommendations.append('REQUIRED_MISSING_TIME')
                elif field == 'contact_email':
                    recommendations.append('REQUIRED_MISSING_EMAIL')
                elif field == 'specialty':
                    recommendations.append('REQUIRED_MISSING_SPECIALTY')
            else:
                # Field is present - check for quality issues that deduct 50%
                quality_deduction = 0
                
                if field == 'meeting_location':
                    location = unit.get(field, '')
                    if self.is_pobox_location(location):
                        quality_deduction = weight * 0.5  # Deduct 50% for PO Box
                        recommendations.append('QUALITY_POBOX_LOCATION')
                    elif unit.get('_quality_unit_address', False):
                        quality_deduction = weight * 0.5  # Deduct 50% for location in description
                        recommendations.append('QUALITY_UNIT_ADDRESS')
                        
                elif field == 'contact_email':
                    email = unit.get(field, '')
                    if self.is_personal_email(email, unit):
                        quality_deduction = weight * 0.5  # Deduct 50% for personal email
                        recommendations.append('QUALITY_PERSONAL_EMAIL')
                
                # Apply quality deduction
                score -= quality_deduction
        
        # Add recommended field issues (informational only - no scoring impact)
        for field in self.weights.RECOMMENDED.keys():
            if not self.is_field_present(unit, field):
                if field == 'contact_person':
                    recommendations.append('RECOMMENDED_MISSING_CONTACT')
                elif field == 'phone_number':
                    recommendations.append('RECOMMENDED_MISSING_PHONE')
                elif field == 'website':
                    recommendations.append('RECOMMENDED_MISSING_WEBSITE')
                elif field == 'description':
                    recommendations.append('CONTENT_MISSING_DESCRIPTION')
        
        # Ensure score doesn't go below 0
        score = max(0.0, score)
        
        return score, recommendations
    
    def get_letter_grade(self, score: float) -> str:
        """Convert numeric score to letter grade"""
        if score >= 90:
            return 'A'
        elif score >= 80:
            return 'B'
        elif score >= 70:
            return 'C'
        elif score >= 60:
            return 'D'
        else:
            return 'F'
    
    def get_recommendation_descriptions(self, recommendation_ids: List[str]) -> List[str]:
        """Get human-readable descriptions for recommendation identifiers"""
        return [self.recommendation_map.get(rec_id, rec_id) for rec_id in recommendation_ids]
    
    def score_all_units(self, units_data: Dict[str, Any]) -> Dict[str, Any]:
        """Score all units and return results with recommendations"""
        results = {
            'total_units': units_data.get('total_units', 0),
            'scoring_summary': {
                'A': 0, 'B': 0, 'C': 0, 'D': 0, 'F': 0
            },
            'average_score': 0.0,
            'units_with_scores': []
        }
        
        total_score = 0.0
        units = units_data.get('all_units', [])
        
        for unit in units:
            score, recommendations = self.score_unit(unit)
            letter_grade = self.get_letter_grade(score)
            
            # Add scoring information to unit
            unit_with_score = unit.copy()
            unit_with_score.update({
                'completeness_score': round(score, 1),
                'completeness_grade': letter_grade,
                'recommendations': recommendations
            })
            
            results['units_with_scores'].append(unit_with_score)
            results['scoring_summary'][letter_grade] += 1
            total_score += score
        
        if len(units) > 0:
            results['average_score'] = round(total_score / len(units), 1)
        
        return results


def main():
    """Main function for command-line usage"""
    import sys
    
    if len(sys.argv) != 2:
        print("Usage: python src/analysis/quality_scorer.py <input_json_file>")
        sys.exit(1)
    
    input_file = Path(sys.argv[1])
    if not input_file.exists():
        print(f"Error: Input file {input_file} not found")
        sys.exit(1)
    
    # Load unit data
    with open(input_file, 'r') as f:
        units_data = json.load(f)
    
    # Score units
    scorer = UnitQualityScorer()
    results = scorer.score_all_units(units_data)
    
    # Generate output filename
    output_file = input_file.parent / f"{input_file.stem}_scored.json"
    
    # Save results
    with open(output_file, 'w') as f:
        json.dump(results, f, indent=2, ensure_ascii=False)
    
    # Print summary
    print(f"Quality Scoring Results for {results['total_units']} units:")
    print(f"Average Score: {results['average_score']}")
    print("Grade Distribution:")
    for grade in ['A', 'B', 'C', 'D', 'F']:
        count = results['scoring_summary'][grade]
        percentage = (count / results['total_units'] * 100) if results['total_units'] > 0 else 0
        print(f"  {grade}: {count} units ({percentage:.1f}%)")
    print(f"\nDetailed results saved to: {output_file}")


if __name__ == '__main__':
    main()