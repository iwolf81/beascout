#!/usr/bin/env python3
"""
BeAScout Unit Quality Scoring System

Analyzes unit information completeness and generates quality scores with 
recommendation identifiers for Key Three outreach.

Usage:
    python src/analysis/quality_scorer.py data/raw/all_units_01720.json
"""

import json
import os
import re
import datetime
from typing import Dict, List, Tuple, Any
from dataclasses import dataclass
from pathlib import Path


@dataclass
class ScoringWeights:
    """Scoring weights by unit type"""
    # Non-specialized units (Packs, Troops, Ships): 4 required fields at 17.5% each
    STANDARD_REQUIRED = {
        'meeting_location': 17.5,
        'meeting_day': 17.5,
        'meeting_time': 17.5,
        'contact_email': 17.5
    }
    
    # Specialized units (Crews, Posts, Clubs): 5 required fields at 14% each
    SPECIALIZED_REQUIRED = {
        'meeting_location': 14.0,
        'meeting_day': 14.0,
        'meeting_time': 14.0,
        'contact_email': 14.0,
        'specialty': 14.0
    }
    
    # Recommended fields (same for all unit types): 4 fields at 7.5% each
    RECOMMENDED = {
        'contact_person': 7.5,
        'phone_number': 7.5,
        'website': 7.5,
        'description': 7.5
    }


class UnitQualityScorer:
    """Scores unit information completeness and generates recommendations"""
    
    def __init__(self):
        self.weights = ScoringWeights()
        self.recommendation_map = {
            # Required field recommendations
            'REQUIRED_MISSING_LOCATION': "Add meeting location with street address",
            'REQUIRED_MISSING_DAY': "Add meeting day",
            'REQUIRED_MISSING_TIME': "Add meeting time",
            'REQUIRED_MISSING_EMAIL': "Add contact email address",
            'REQUIRED_MISSING_SPECIALTY': "Add specialty information (Crews only)",
            
            # Recommended field recommendations
            'RECOMMENDED_MISSING_CONTACT': "Add contact person name",
            'RECOMMENDED_MISSING_PHONE': "Add contact phone number",
            'RECOMMENDED_MISSING_WEBSITE': "Add unit-specific website",
            
            # Data quality recommendations
            'QUALITY_POBOX_LOCATION': "Replace PO Box with physical meeting location",
            'QUALITY_PERSONAL_EMAIL': "Use unit-specific email instead of personal email",
            'QUALITY_ADDRESS_EMPTY': "Unit address field is empty - meeting location found elsewhere",
            
            # Content quality recommendations
            'RECOMMENDED_MISSING_DESCRIPTION': "Add informative and inviting unit description that includes meeting day(s) and time(s)"
        }
    
    @classmethod
    def log_quality_debug(cls, unit: Dict[str, Any], score: float, grade: str, recommendations: List[str]):
        """Log quality scoring results for manual verification"""
        # Use a session-based timestamp (created once per execution)
        if not hasattr(cls, '_quality_debug_filename'):
            timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
            cls._quality_debug_filename = f'data/debug/quality_debug_{timestamp}.log'
            
            # Ensure debug directory exists
            os.makedirs('data/debug', exist_ok=True)
        
        with open(cls._quality_debug_filename, 'a', encoding='utf-8') as f:
            unit_type = unit.get('unit_type', 'Unknown')
            unit_number = unit.get('unit_number', 'Unknown')
            unit_town = unit.get('unit_town', 'Unknown')
            
            # Format quality flags - show all recommendations or 'None' if empty
            quality_flags = ', '.join(recommendations) if recommendations else 'None'
            
            f.write(f"  unit_type: '{unit_type}', ")
            f.write(f"  unit_number: '{unit_number}', ")
            f.write(f"  unit_town: '{unit_town}', ")
            f.write(f"  score: {score:.1f}, ")
            f.write(f"  grade: '{grade}', ")
            f.write(f"  quality_flags: '{quality_flags}'\n")
    
    def is_specialized_unit(self, unit: Dict[str, Any]) -> bool:
        """Check if unit uses specialized scoring weights: Crew, Post, or Club"""
        unit_type = unit.get('unit_type', '').lower()
        return unit_type in ['crew', 'post', 'club']
    
    def requires_specialty_field(self, unit: Dict[str, Any]) -> bool:
        """Check if unit requires specialty field: only Crews"""
        unit_type = unit.get('unit_type', '').lower()
        return unit_type == 'crew'
    
    def is_field_present(self, unit: Dict[str, Any], field: str) -> bool:
        """Check if field has meaningful content"""
        value = unit.get(field, '')
        if not isinstance(value, str):
            return False
        return bool(value.strip())
    
    def is_pobox_location(self, location: str) -> bool:
        """Check if location is a PO Box"""
        if not location:
            return False
        # Common PO Box patterns
        pobox_patterns = [
            r'\bP\.?O\.?\s*Box\b',
            r'\bPO\s*Box\b',
            r'\bPost\s*Office\s*Box\b'
        ]
        for pattern in pobox_patterns:
            if re.search(pattern, location, re.IGNORECASE):
                return True
        return False
    
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
        ]
        
        has_personal_identifier = any(re.search(pattern, local_part) 
                                    for pattern in personal_patterns)
        
        # If has clear personal identifiers, it's personal regardless of unit context
        if has_personal_identifier:
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
            
        # FOURTH: Check remaining personal patterns (for ambiguous cases)
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
        score = 0.0
        recommendations = []
        is_specialized = self.is_specialized_unit(unit)
        
        # Check for quality flags from extraction process
        quality_flags = unit.get('quality_flags', [])
        for flag in quality_flags:
            if flag in self.recommendation_map:
                recommendations.append(flag)
        
        # Get appropriate required field weights
        required_weights = self.weights.SPECIALIZED_REQUIRED if is_specialized else self.weights.STANDARD_REQUIRED
        
        # Score required fields
        for field, weight in required_weights.items():
            if field == 'specialty' and not self.requires_specialty_field(unit):
                continue  # Skip specialty for non-crew units
                
            if not self.is_field_present(unit, field):
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
                # Field is present - check quality
                if field == 'meeting_location':
                    location = unit.get(field, '')
                    if self.is_pobox_location(location):
                        score += weight * 0.5  # Half credit for PO Box
                        recommendations.append('QUALITY_POBOX_LOCATION')
                    elif 'QUALITY_ADDRESS_EMPTY' in quality_flags:
                        score += weight * 0.5  # Half credit for empty address div
                        # Note: QUALITY_ADDRESS_EMPTY already added to recommendations above
                    else:
                        score += weight  # Full credit
                elif field == 'contact_email':
                    email = unit.get(field, '')
                    if self.is_personal_email(email, unit):
                        score += weight * 0.5  # Half credit for personal email
                        recommendations.append('QUALITY_PERSONAL_EMAIL')
                    else:
                        score += weight  # Full credit
                else:
                    score += weight  # Full credit for other fields
        
        # Score recommended fields
        for field, weight in self.weights.RECOMMENDED.items():
            if not self.is_field_present(unit, field):
                if field == 'contact_person':
                    recommendations.append('RECOMMENDED_MISSING_CONTACT')
                elif field == 'phone_number':
                    recommendations.append('RECOMMENDED_MISSING_PHONE')
                elif field == 'website':
                    recommendations.append('RECOMMENDED_MISSING_WEBSITE')
                elif field == 'description':
                    recommendations.append('RECOMMENDED_MISSING_DESCRIPTION')
            else:
                score += weight  # Full credit for present recommended fields
        
        # Generate grade and log quality debug info
        grade = self.get_letter_grade(score)
        self.log_quality_debug(unit, score, grade, recommendations)
        
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