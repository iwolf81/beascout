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
    """Scoring weights by unit type"""
    # Non-Crew units (Packs, Troops, Ships): 4 required fields at 17.5% each
    NON_CREW_REQUIRED = {
        'meeting_location': 17.5,
        'meeting_day': 17.5,
        'meeting_time': 17.5,
        'contact_email': 17.5
    }
    
    # Crew units: 5 required fields at 14% each
    CREW_REQUIRED = {
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
            'REQUIRED_MISSING_SPECIALTY': "Add specialty information for Venturing Crew",
            
            # Recommended field recommendations
            'RECOMMENDED_MISSING_CONTACT': "Add contact person name",
            'RECOMMENDED_MISSING_PHONE': "Add contact phone number",
            'RECOMMENDED_MISSING_WEBSITE': "Add unit-specific website",
            
            # Data quality recommendations
            'QUALITY_POBOX_LOCATION': "Replace PO Box with physical meeting location",
            'QUALITY_PERSONAL_EMAIL': "Use unit-specific email instead of personal email",
            
            # Content quality recommendations
            'CONTENT_MISSING_DESCRIPTION': "Add informative and inviting unit description that includes meeting day(s) and time(s)"
        }
    
    def is_crew_unit(self, unit: Dict[str, Any]) -> bool:
        """Check if unit is a Venturing Crew"""
        return unit.get('unit_type', '').lower() == 'crew'
    
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
    
    def is_personal_email(self, email: str) -> bool:
        """Check if email appears to be personal rather than unit-specific"""
        if not email:
            return False
        
        # Extract the local part (before @) for analysis
        local_part = email.split('@')[0].lower()
        
        # FIRST: Check for unit-specific patterns that should override personal detection
        unit_role_patterns = [
            r'^scoutmaster',
            r'^cubmaster', 
            r'^committee',
            r'^beascout',  # Platform-specific email
        ]
        
        is_unit_role = any(re.search(pattern, local_part) 
                          for pattern in unit_role_patterns)
        
        if is_unit_role:
            return False  # Unit role emails are not personal
            
        # SECOND: Check for personal identifier patterns  
        personal_patterns = [
            r'[a-z]+\.[a-z]+',             # first.last format anywhere
            r'^[a-z]{2,3}[a-z]{4,8}$',     # initials + name (2-3 chars + 4-8 chars, excludes single words like "scoutmaster")
            r'^[a-z]{3}$',                 # 3-letter initials (like DRD)
            r'[a-z]+[0-9]{2,4}$',          # ends with name + year/numbers
            r'[a-z]+[0-9]{1,3}$',          # ends with name + small numbers  
            r'[a-z]+\.[a-z]+\.[a-z]+',     # first.middle.last anywhere
        ]
        
        has_personal_identifier = any(re.search(pattern, local_part) 
                                    for pattern in personal_patterns)
        
        # If has personal identifiers, it's personal regardless of unit context (for continuity)
        if has_personal_identifier:
            return True
            
        # SECOND: Check for unit-specific patterns (only if no personal identifiers)
        unit_patterns = [
            r'pack\d+',
            r'troop\d+', 
            r'crew\d+',
            r'ship\d+',
            r'scouts?',
            r'cubmaster',
            r'scoutmaster',
            r'committee',
            r'sudbury',
            r'westford',
            r'harvard',
            r'concord'
        ]
        has_unit_identifier = any(re.search(pattern, local_part) 
                                for pattern in unit_patterns)
        
        if has_unit_identifier:
            return False  # Unit-specific email without personal identifiers
        
        # THIRD: For emails without unit or personal identifiers, check personal domains
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
        is_crew = self.is_crew_unit(unit)
        
        # Get appropriate required field weights
        required_weights = self.weights.CREW_REQUIRED if is_crew else self.weights.NON_CREW_REQUIRED
        
        # Score required fields
        for field, weight in required_weights.items():
            if field == 'specialty' and not is_crew:
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
                    else:
                        score += weight  # Full credit
                elif field == 'contact_email':
                    email = unit.get(field, '')
                    if self.is_personal_email(email):
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
                    recommendations.append('CONTENT_MISSING_DESCRIPTION')
            else:
                score += weight  # Full credit for present recommended fields
        
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