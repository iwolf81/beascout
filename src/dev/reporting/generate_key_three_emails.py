#!/usr/bin/env python3
"""
Key Three Email Generation System

Generates personalized improvement emails for units by cross-referencing:
1. Unit data from scored JSON files (primary_identifier)
2. Key Three member information from HNE_key_three.xlsx (unitcommorgname)

Usage:
    python scripts/generate_key_three_emails.py data/raw/all_units_01720_scored.json
    python scripts/generate_key_three_emails.py data/raw/all_units_*_scored.json --output-dir data/output/emails/
"""

import sys
from pathlib import Path

# Ensure project root is in Python path for imports
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

import json
import glob
import re
from typing import List, Dict, Any
import pandas as pd
from datetime import datetime


class KeyThreeEmailGenerator:
    def __init__(self, key_three_file: str = "data/input/Key 3 08-22-2025.xlsx"):
        """Initialize with Key Three member data"""
        self.key_three_data = self._load_key_three_data(key_three_file)
        self.hne_towns_set = self._load_hne_towns()
        
    def _load_key_three_data(self, file_path: str) -> pd.DataFrame:
        """Load Key Three member data from Excel file"""
        try:
            # Read Excel file with proper headers (row 8 contains headers)
            df = pd.read_excel(file_path, header=8)
            print(f"Loaded {len(df)} Key Three member records")
            return df
        except Exception as e:
            print(f"Error loading Key Three data: {e}", file=sys.stderr)
            return pd.DataFrame()
    
    def _load_hne_towns(self) -> set:
        """Load HNE towns data once at initialization"""
        try:
            import sys
            import os
            # Try multiple path approaches for robustness
            possible_paths = [
                os.path.join(os.path.dirname(__file__), '..', '..'),  # From src/pipeline/reporting
                'src',  # From repo root
                '.'  # Current directory (repo root)
            ]
            
            for path_to_add in possible_paths:
                if path_to_add not in sys.path:
                    sys.path.insert(0, path_to_add)
                
                try:
                    from config.hne_towns import get_hne_towns_and_zipcodes
                    hne_towns, _ = get_hne_towns_and_zipcodes()
                    return set([town.lower() for town in hne_towns])
                except ImportError:
                    continue
            
            # If all import attempts fail, this is a critical error
            raise RuntimeError(
                f"CRITICAL ERROR [{Path(__file__).name}]: Cannot load HNE towns data (TOWN_TO_DISTRICT mapping). "
                "This is required to filter units to HNE territory only. "
                "Without this data, non-HNE units could be included in reports. "
                "Pipeline must stop to prevent data integrity issues."
            )
            
        except Exception as e:
            print(f"Warning: Error loading HNE towns: {e}", file=sys.stderr)
            return set()
    
    def _normalize_unit_identifier(self, identifier: str) -> str:
        """Normalize unit identifier for matching
        
        Converts formats like:
        - "Pack 0001 Acton-The Church of The Good Shepherd" 
        - "Pack 0001 (F) - Acton-The Church of The Good Shepherd"
        
        To consistent format for matching
        """
        if not identifier:
            return ""
        
        # Remove leading zeros from unit numbers
        identifier = re.sub(r'\b0+(\d+)', r'\1', identifier)
        
        # Remove gender indicators like "(F)" or "(B)" 
        identifier = re.sub(r'\s*\([FB]\)\s*', '', identifier)
        
        # Normalize spacing - remove all extra spaces and standardize dashes
        identifier = re.sub(r'\s+', ' ', identifier)  # Multiple spaces to single space
        identifier = re.sub(r'\s*-\s*', '-', identifier)  # Standardize dashes
        
        # Convert to lowercase for case-insensitive matching
        return identifier.strip().lower()
    
    def _find_key_three_members(self, primary_identifier: str) -> List[Dict[str, str]]:
        """Find Key Three members for a given unit primary identifier
        
        ORGANIZATION MATCHING LOGIC:
        ============================
        
        Problem: Multiple units can share the same number across different organizations.
        Example: Troop 7012 exists in both Acton (Group Of Citizens) and Leominster (Our Lady Of The Lake)
        
        Solution: Two-stage matching process:
        
        STEP 1: Extract Organization Keywords
        ------------------------------------
        From "Troop 7012 Acton-Group Of Citizens, Inc":
        - Raw org part: "acton-group of citizens, inc"
        - Filter out stop words: "of", "inc" (common, non-distinctive)
        - Filter out short terms: anything ≤ 2 characters
        - Final keywords: ['acton', 'group', 'citizens']
        
        STEP 2: Two-Stage Matching Process
        -----------------------------------
        For each Key Three record:
        
        Stage 1 - Unit Pattern Match:
        - Must contain "troop 7012" ✅ (all 6 Troop 7012 records pass)
        
        Stage 2 - Organization Match:
        - Count keyword matches in unitcommorgname field
        - Threshold: At least 1 match required (minimum of max(1, keywords//2))
        
        STEP 3: Results Example
        -----------------------
        Member               | unitcommorgname                          | Keywords Found | Match?
        ---------------------|------------------------------------------|----------------|--------
        Keith Boudreau       | leominster-our lady of the lake church   | 0/3           | ❌
        Stephen Hoff         | acton-group of citizens, inc             | 3/3 ✅        | ✅
        William Garnett      | acton-group of citizens, inc             | 3/3 ✅        | ✅
        Maria Heiniluoma     | acton-group of citizens, inc             | 3/3 ✅        | ✅
        Jessie Spinelli      | leominster-our lady of the lake church   | 0/3           | ❌
        
        Key Design Decisions:
        - Stop words removed: "of", "the", "inc", "church", "club" don't help distinguish organizations
        - Flexible threshold: Requires only 1+ keyword match (not all) to handle naming variations  
        - Case-insensitive: All comparisons done in lowercase
        - Punctuation-agnostic: Handles dashes, commas, periods automatically
        
        This ensures units with duplicate numbers get correctly matched to their specific Key Three members.
        """
        if self.key_three_data.empty:
            return []
        
        # Extract unit type, number and organization from primary identifier
        parts = primary_identifier.split(' ', 2)  # Split into at most 3 parts
        if len(parts) < 3:
            return []
        
        unit_type = parts[0].lower()  # Pack, Troop, Crew, etc.
        unit_number = parts[1].lstrip('0') or '0'  # Remove leading zeros
        org_part = parts[2].lower()  # Organization part
        
        # Extract key organization identifiers for matching
        org_keywords = self._extract_org_keywords(org_part)
        
        # Find matching records using comprehensive matching
        matches = []
        expected_unit_pattern = f"{unit_type} {unit_number.zfill(4)}"  # e.g., "troop 7012"
        
        for _, row in self.key_three_data.iterrows():
            unit_comm_org = str(row.get('unitcommorgname', '')).lower()
            
            # First check: must contain the unit type and number
            if expected_unit_pattern not in unit_comm_org:
                continue
            
            # Second check: organization matching
            # For units with duplicate numbers, we need to match the organization
            if org_keywords and self._org_matches(unit_comm_org, org_keywords):
                matches.append({
                    'name': str(row.get('fullname', '')),
                    'email': str(row.get('email', '')),
                    'position': str(row.get('position', '')),
                    'phone': str(row.get('phone', '')),
                    'unitcommorgname': str(row.get('unitcommorgname', ''))
                })
        
        return matches
    
    def _extract_org_keywords(self, org_part: str) -> List[str]:
        """Extract key organization identifiers for matching"""
        org_part = org_part.lower()
        
        # Split on common separators and extract meaningful terms
        # Remove common words that don't help with matching
        stop_words = {'the', 'of', 'and', 'a', 'an', 'inc', 'church', 'club', 'association', 'society'}
        
        # Split on dashes and other separators
        terms = []
        for part in org_part.replace('-', ' ').split():
            # Remove punctuation and get meaningful terms
            clean_term = part.strip('.,()').lower()
            if clean_term and clean_term not in stop_words and len(clean_term) > 2:
                terms.append(clean_term)
        
        return terms
    
    def _org_matches(self, unit_comm_org: str, org_keywords: List[str]) -> bool:
        """Check if organization keywords match the unitcommorgname"""
        if not org_keywords:
            return True  # If no specific org keywords, match any
        
        unit_comm_org = unit_comm_org.lower()
        
        # Count how many keywords match
        matches = 0
        for keyword in org_keywords:
            if keyword in unit_comm_org:
                matches += 1
        
        # Require at least half the keywords to match (minimum 1)
        required_matches = max(1, len(org_keywords) // 2)
        return matches >= required_matches
    
    def _format_recommendations_section(self, recommendations: List[str]) -> str:
        """Format the recommendations section based on missing information"""
        missing_required = [r for r in recommendations if r.startswith('REQUIRED_MISSING_')]
        missing_recommended = [r for r in recommendations if r.startswith('RECOMMENDED_MISSING_')]
        quality_issues = [r for r in recommendations if r.startswith('QUALITY_')]
        
        sections = []
        
        # Missing Critical Information section
        if missing_required:
            sections.append("### 🔴 **Missing Critical Information for Families:**")
            
            if 'REQUIRED_MISSING_LOCATION' in recommendations:
                sections.append("- **Meeting Location**: *Not specified - families need to know where you meet*")
            if 'REQUIRED_MISSING_DAY' in recommendations:
                sections.append("- **Meeting Day**: *Not specified - families need to know when you meet*")
            if 'REQUIRED_MISSING_TIME' in recommendations:
                sections.append("- **Meeting Time**: *Not specified - families need to know what time meetings start*")
            if 'REQUIRED_MISSING_EMAIL' in recommendations:
                sections.append("- **Contact Email**: *Not specified - families have no way to reach you*")
        
        # Missing Recommended Information section  
        if missing_recommended:
            sections.append("\n### 🟡 **Recommended Additional Information:**")

            if 'RECOMMENDED_MISSING_CONTACT' in recommendations:
                sections.append("- **Contact Person**: *Helps families know who to reach out to*")
            if 'RECOMMENDED_MISSING_PHONE' in recommendations:
                sections.append("- **Phone Number**: *Provides immediate communication option for urgent questions*")
            if 'RECOMMENDED_MISSING_WEBSITE' in recommendations:
                sections.append("- **Website**: *A unit website increases visibility and provides additional information for families*")
            if 'RECOMMENDED_MISSING_DESCRIPTION' in recommendations:
                sections.append("- **Program Description**: *Informative description helps attract new Scouts by explaining unit activities and culture*")
        
        # Quality Issues section
        if quality_issues:
            sections.append("\n### 🟡 **Quality Improvements:**")
            
            if 'QUALITY_PERSONAL_EMAIL' in recommendations:
                sections.append("- **Contact Email**: *Consider using unit-specific email monitored by multiple leaders instead of a personal one*")
            if 'QUALITY_POBOX_LOCATION' in recommendations:
                sections.append("- **Meeting Location**: *Complement PO Box with physical meeting location so families can find meetings*")
            if 'QUALITY_UNIT_ADDRESS' in recommendations:
                sections.append("- **Meeting Location**: *Provide physical meeting location in Unit Meeting Address field instead of Description field*")
        
        return "\n".join(sections)
    
    def _format_excellent_section(self, unit_data: Dict[str, Any], recommendations: List[str]) -> str:
        """Format the 'Already Doing Well' section for available information"""
        excellent_items = []
        
        # Check what information is available (not in missing recommendations)
        if unit_data.get('meeting_location') and 'REQUIRED_MISSING_LOCATION' not in recommendations:
            location = unit_data['meeting_location']
            if 'QUALITY_POBOX_LOCATION' in recommendations:
                excellent_items.append(f"- **Meeting Address**: {location} *(Address provided, though actual meeting location would be more helpful)*")
            else:
                excellent_items.append(f"- **Meeting Location**: {location} *(Clear address provided)*")
        
        if unit_data.get('contact_email') and 'REQUIRED_MISSING_EMAIL' not in recommendations:
            email = unit_data['contact_email']
            if 'QUALITY_PERSONAL_EMAIL' in recommendations:
                excellent_items.append(f"- **Contact Email**: {email} *(Email provided - consider unit-specific email for continuity)*")
            else:
                excellent_items.append(f"- **Contact Email**: {email} *(Unit-specific email - great for continuity!)*")
        
        if unit_data.get('contact_person') and 'RECOMMENDED_MISSING_CONTACT' not in recommendations:
            excellent_items.append(f"- **Contact Person**: {unit_data['contact_person']} *(Designated contact provided)*")
        
        if unit_data.get('website') and 'RECOMMENDED_MISSING_WEBSITE' not in recommendations:
            website = unit_data['website']
            unit_type = unit_data.get('unit_type', 'Unit').lower()
            excellent_items.append(f"- **Website**: {website} *({unit_type.title()}-specific website available)*")
        
        if unit_data.get('description') and 'RECOMMENDED_MISSING_DESCRIPTION' not in recommendations:
            description = unit_data['description'].strip()
            # Format description with proper word wrapping and indentation  
            if len(description) > 80:
                # Break at word boundaries and indent continuation lines
                words = description.split()
                lines = []
                current_line = []
                current_length = 0
                
                for word in words:
                    if current_length + len(word) + 1 > 80 and current_line:
                        lines.append(' '.join(current_line))
                        current_line = [word]
                        current_length = len(word)
                    else:
                        current_line.append(word)
                        current_length += len(word) + (1 if current_line else 0)
                
                if current_line:
                    lines.append(' '.join(current_line))
                
                # Format with proper indentation for continuation lines
                if len(lines) > 1:
                    formatted_desc = f"\"{lines[0]}\n"
                    for line in lines[1:]:
                        formatted_desc += f"  {line}\n"
                    formatted_desc = formatted_desc.rstrip() + "\""
                    excellent_items.append(f"- **Program Description**: {formatted_desc} *(Welcoming and informative)*")
                else:
                    excellent_items.append(f"- **Program Description**: \"{description}\" *(Welcoming and informative)*")
            else:
                excellent_items.append(f"- **Program Description**: \"{description}\" *(Welcoming and informative)*")
        
        if unit_data.get('chartered_organization'):
            excellent_items.append(f"- **Chartered Organization**: {unit_data['chartered_organization']} *(Clear sponsoring organization)*")
        
        if excellent_items:
            return "### ✅ **Excellent - Information Available:**\n" + "\n".join(excellent_items)
        else:
            return ""
    
    def _format_action_items(self, recommendations: List[str], unit_data: Dict[str, Any]) -> str:
        """Format detailed action items for recommendations"""
        sections = []
        action_num = 1  # Initialize at function start
        
        # High Priority - Missing Critical Information
        missing_required = [r for r in recommendations if r.startswith('REQUIRED_MISSING_')]
        if missing_required:
            sections.append("### 🔴 **High Priority - Missing Critical Information:**")
            sections.append("")
            
            if 'REQUIRED_MISSING_LOCATION' in recommendations:
                unit_type = unit_data.get('unit_type', 'unit').lower()
                sections.extend([
                    f"**{action_num}. Meeting Location** *(Missing - Required)*",
                    f"- Families need to know where your {unit_type} meets to attend meetings and events",
                    f"- **Action**: Please provide your meeting location with full street address (e.g., \"123 Main St, Community Center, {unit_data.get('chartered_organization', 'Your Town')}\")",
                    "- **Where to Update**: Log into BeAScout.org, search for your unit, and update the meeting location field",
                    ""
                ])
                action_num += 1
            
            if 'REQUIRED_MISSING_DAY' in recommendations:
                sections.extend([
                    f"**{action_num}. Meeting Day & Time** *(Missing - Required)*" if 'REQUIRED_MISSING_TIME' in recommendations else f"**{action_num}. Meeting Day** *(Missing - Required)*",
                    f"- Families searching for Scouting need to know when your {unit_data.get('unit_type', 'unit').lower()} meets to plan their schedule",
                    "- **Action**: Please provide your regular meeting day and time (e.g., \"Every Thursday, 7:00 PM - 8:30 PM\")",
                    "- **Where to Update**: Log into BeAScout.org, search for your unit, and update the meeting time field",
                    ""
                ])
                action_num += 1
            elif 'REQUIRED_MISSING_TIME' in recommendations:
                sections.extend([
                    f"**{action_num}. Meeting Time** *(Missing - Required)*",
                    f"- Families searching for Scouting need to know what time your {unit_data.get('unit_type', 'unit').lower()} meets",
                    "- **Action**: Please provide your regular meeting time (e.g., \"7:00 PM - 8:30 PM\")",
                    "- **Where to Update**: Log into BeAScout.org, search for your unit, and update the meeting time field",
                    ""
                ])
                action_num += 1
            
            if 'REQUIRED_MISSING_EMAIL' in recommendations:
                unit_type = unit_data.get('unit_type', 'unit').lower()
                unit_num = unit_data.get('unit_number', 'XXX').lstrip('0') or 'XXX'
                town = unit_data.get('chartered_organization', '').split('-')[-1].strip() if unit_data.get('chartered_organization') else 'yourtown'
                example_email = f"{unit_type}{unit_num}{town.lower().replace(' ', '')}@gmail.com"
                
                sections.extend([
                    f"**{action_num}. Contact Email** *(Missing - Required)*",
                    "- Families need a way to ask questions and get information about joining",
                    f"- **Action**: Please provide a {unit_type} email address (preferably unit-specific like {example_email})",
                    "- **Best Practice**: Use a unit-specific email that can be monitored by multiple unit leaders",
                    "- **Where to Update**: Log into BeAScout.org, search for your unit, and update the contact email field",
                    ""
                ])
                action_num += 1
        
        # Recommended - Additional Information
        missing_recommended = [r for r in recommendations if r.startswith('RECOMMENDED_MISSING_')]
        quality_issues = [r for r in recommendations if r.startswith('QUALITY_')]
        
        if missing_recommended or quality_issues:
            sections.append("### 🟡 **Recommended - Additional Information:**")
            sections.append("")
            
            
            if 'RECOMMENDED_MISSING_CONTACT' in recommendations:
                sections.extend([
                    f"**{action_num}. Contact Person** *(Missing - Recommended)*",
                    "- Provides families with a specific person to contact for questions",
                    "- **Action**: Consider adding the unit leader's name or designated contact person",
                    ""
                ])
                action_num += 1
            
            if 'RECOMMENDED_MISSING_PHONE' in recommendations:
                sections.extend([
                    f"**{action_num}. Phone Contact** *(Missing - Recommended)*",
                    "- Provides families an immediate way to get questions answered",
                    "- **Action**: Consider adding a current unit leader's phone contact",
                    "- **Best Practice**: Update BeAScout whenever the phone number needs to change (e.g., when a different leader handles inquiries)",
                    ""
                ])
                action_num += 1
            
            if 'RECOMMENDED_MISSING_WEBSITE' in recommendations:
                sections.extend([
                    f"**{action_num}. Website** *(Missing - Recommended)*",
                    "- Allows families to learn more about your unit's activities and culture",
                    "- **Action**: Consider creating a simple website or social media page with unit information",
                    ""
                ])
                action_num += 1
            
            if 'QUALITY_PERSONAL_EMAIL' in recommendations:
                unit_type = unit_data.get('unit_type', 'unit').lower()
                sections.extend([
                    f"**{action_num}. Email Continuity** *(Quality Improvement)*",
                    f"- Current email appears to be a personal address, which may change when leadership rotates",
                    f"- **Action**: Consider transitioning to a unit-specific email address for better continuity",
                    f"- **Best Practice**: Unit-specific emails stay with the {unit_type} as leaders change",
                    ""
                ])
                action_num += 1
        
        return "\n".join(sections)
    
    def generate_email(self, unit_data: Dict[str, Any]) -> str:
        """Generate a personalized Key Three email for a unit"""
        # Support both primary_identifier and unit_key fields for compatibility
        primary_identifier = unit_data.get('primary_identifier', unit_data.get('unit_key', ''))
        unit_type = unit_data.get('unit_type', 'Unit')
        unit_number = unit_data.get('unit_number', '').lstrip('0') or 'XXX'
        
        # Use unit_town field if available, otherwise extract from primary identifier
        town = unit_data.get('unit_town', '')
        if not town:
            # Fallback to parsing primary identifier
            parts = primary_identifier.split(' ', 2) if ' ' in primary_identifier else ['', '', '']
            if len(parts) >= 3 and '-' in parts[2]:
                town = parts[2].split('-')[0].strip()  # Get part before first dash
            else:
                town = 'Town'
        recommendations = unit_data.get('recommendations', unit_data.get('quality_tags', []))
        score = unit_data.get('completeness_score', 0)
        
        # Find Key Three members
        key_three_members = self._find_key_three_members(primary_identifier)
        
        # Format Key Three member information
        if key_three_members:
            member_emails = [m['email'] for m in key_three_members if m['email']]
            member_names = [m['name'].strip() for m in key_three_members if m['name']]
            to_line = f"{unit_type} {unit_number} {town} Key Three Members ({', '.join(member_emails)})"
            dear_line = f"Dear {unit_type} {unit_number} {town} Key Three ({', '.join(member_names)}),"
        else:
            to_line = f"{unit_type} {unit_number} {town} Key Three Members (emails not found in Key Three roster)"
            dear_line = f"Dear {unit_type} {unit_number} {town} Key Three,"
        
        # Format sections
        current_info_section = self._format_recommendations_section(recommendations)
        excellent_section = self._format_excellent_section(unit_data, recommendations)
        action_items = self._format_action_items(recommendations, unit_data)
        
        # Determine if this is a critical case (missing most required information)
        critical_count = sum(1 for r in recommendations if r.startswith('REQUIRED_MISSING_'))
        is_critical = critical_count >= 3
        
        # Generate email content
        email_content = f"""# {unit_type} {unit_number} {town} - Key Three Improvement Email

**TO:** {to_line}
**FROM:** Heart of New England Council, Scouting America  
**SUBJECT:** {unit_type} {unit_number} {town} - BeAScout Information Review - Help Families Find Your {unit_type}  

---

{dear_line}

The Heart of New England Council periodically reviews unit information on BeAScout.org and JoinExploring.org to help prospective Scout families easily find complete, accurate information about local units. We've completed a review of {unit_type} {unit_number} {town}'s online presence and wanted to share our findings and recommendations.

## Your {unit_type}'s Current Information Quality

**Overall Completeness Score: {score}%**

{current_info_section}

{excellent_section}

## Recommendations for Improvement

{action_items}

{self._get_guidelines_section(unit_type)}

## Next Steps

1. **Update Missing Information**: Please provide the critical missing information identified above
2. **How to Update BeAScout**: 
   - Visit beascout.scouting.org and click "Sign In" in the top right
   - Log in using your my.scouting.org credentials (same as ScoutBook)
   - Search for your unit and click "Manage Unit Information"
   - Update the missing fields and click "Save"
   - **Detailed Instructions**: https://www.scouting.org/wp-content/uploads/2020/05/Be-A-Scout-Pin-Set-up.pdf
3. **Review During Rechartering**: Recommend reviewing information during the annual rechartering process

## Questions or Need Help?

If you need assistance updating your {unit_type.lower()}'s information or have questions about these recommendations, please contact:

**Heart of New England Council**  
Email: [council contact email]  
Phone: [council phone number]

{"Your unit's online presence is currently missing essential information that prevents families from finding and connecting with you. Updating these basic details will dramatically improve your ability to recruit new Scouts and help families discover the great program " + unit_type + " " + unit_number + " " + town + " offers!" if is_critical else "Thank you for your leadership in Scouting and for helping families discover the great program " + unit_type + " " + unit_number + " " + town + " offers!"}

Yours in Scouting,
Heart of New England Council

---

**Note**: This review was generated using the Council's automated BeAScout information analysis system. Information was analyzed from BeAScout.org on [Date]. If you've recently updated your information, please allow time for changes to be reflected in our next review.

**{unit_type} {unit_number} {town} Details Reviewed:**
- Unit Type: {unit_data.get('unit_type', 'Unknown')}
- Charter Organization: {unit_data.get('chartered_organization', 'Not specified')}  
- Meeting Location: {unit_data.get('meeting_location') or 'Not specified'}
- Analysis Date: {datetime.now().strftime('%B %d, %Y')}
- Review ID: {unit_type.upper()}_{unit_number}_{town.upper().replace(' ', '_')}_{datetime.now().strftime('%m%d%y')}"""

        return email_content
    
    def _get_guidelines_section(self, unit_type: str) -> str:
        """Get the guidelines section for the email"""
        return f"""## Guidelines for Effective BeAScout Information

### **Spell out full names for days and months:**
- Include clearly defined meeting day, time, and frequency in descriptions:
  - "Every Thursday, 7:00 PM - 8:30 PM, during the school year"
  - Avoid abbreviations like "Thurs." or "Thu"

### **Meeting Information Best Practices:**
- Use consistent 12-hour format with AM/PM (7:00 PM - 8:30 PM)
- Include frequency information: "Every Thursday" or "First and third Monday of each month"
- Provide both start and end times when possible

### **Contact Information Continuity:**
- Use {unit_type.lower()}-specific email addresses when possible
- Ensure three unit leaders have access to the email account to ensure inquiries are promptly responded to"""
    
    def _is_hne_unit(self, unit_data: Dict[str, Any]) -> bool:
        """Check if unit is within Heart of New England Council territory"""
        # Use the unit_town field if available (preferred method)
        unit_town = unit_data.get('unit_town', '')
        if unit_town:
            # Use preloaded HNE towns set
            if self.hne_towns_set:
                return unit_town.lower() in self.hne_towns_set
            else:
                # If no HNE towns loaded, include all units
                return True
        
        # Fallback to primary_identifier parsing (for backward compatibility)
        # Support both primary_identifier and unit_key fields
        primary_identifier = unit_data.get('primary_identifier', unit_data.get('unit_key', ''))
        if not primary_identifier:
            return False
            
        # Use preloaded HNE towns set for fallback parsing too
        if not self.hne_towns_set:
            return True  # If no HNE towns loaded, include all units
            
        # Extract town from primary identifier
        parts = primary_identifier.split(' ', 2)
        if len(parts) >= 3:
            org_part = parts[2]
            if '-' in org_part:
                # Format: 'Acton-Organization Name' 
                town = org_part.split('-')[0].strip()
                return town.lower() in self.hne_towns_set
            else:
                # Try to extract town from organization name
                org_part_lower = org_part.lower()
                # Check each preloaded HNE town
                for hne_town_lower in self.hne_towns_set:
                    if hne_town_lower in org_part_lower:
                        return True
                return False  # Cannot determine town
        
        return False  # Cannot parse identifier

    def generate_emails_from_file(self, json_file: str, output_dir: str = "data/output/emails/", hne_only: bool = True) -> List[str]:
        """Generate emails for all units in a scored JSON file
        
        Args:
            json_file: Path to scored JSON file
            output_dir: Output directory for generated emails  
            hne_only: If True, only generate emails for HNE Council units
        """
        try:
            with open(json_file, 'r') as f:
                data = json.load(f)
            
            units = data.get('units_with_scores', [])
            if not units:
                print(f"No units found in {json_file}")
                return []
            
            # Filter for HNE units only if requested
            if hne_only:
                hne_units = []
                non_hne_units = []
                for unit in units:
                    if self._is_hne_unit(unit):
                        hne_units.append(unit)
                    else:
                        non_hne_units.append(unit)
                
                print(f"Found {len(hne_units)} HNE Council units, {len(non_hne_units)} non-HNE units")
                print("Non-HNE units excluded from email generation:")
                for unit in non_hne_units:
                    print(f"  - {unit.get('primary_identifier', 'Unknown')}")
                
                units = hne_units
            
            # Create output directory and clean existing files
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            
            # Clean existing email files
            existing_emails = list(output_path.glob("*_email.md"))
            if existing_emails:
                print(f"Cleaning {len(existing_emails)} existing email files...")
                for email_file in existing_emails:
                    email_file.unlink()
            
            generated_files = []
            
            for unit in units:
                # Generate email content
                email_content = self.generate_email(unit)
                
                # Create filename using unit_key or primary_identifier
                primary_id = unit.get('primary_identifier', unit.get('unit_key', 'Unknown_Unit'))
                safe_filename = re.sub(r'[^\w\-_\.]', '_', primary_id)
                filename = f"{safe_filename}_email.md"
                file_path = Path(output_dir) / filename
                
                # Write email to file
                with open(file_path, 'w') as f:
                    f.write(email_content)
                
                generated_files.append(str(file_path))
                print(f"Generated: {filename}")
            
            return generated_files
            
        except Exception as e:
            print(f"Error processing {json_file}: {e}", file=sys.stderr)
            return []


def main():
    if len(sys.argv) < 2:
        print("Usage: python src/pipeline/reporting/generate_key_three_emails.py "
              "<json_file> [--key-three file] [--output-dir output/] [--include-all]", file=sys.stderr)
        print("Examples:")
        print("  python src/pipeline/reporting/generate_key_three_emails.py "
              "data/raw/all_units_comprehensive_scored.json")
        print("  python src/pipeline/reporting/generate_key_three_emails.py "
              "data/raw/all_units_comprehensive_scored.json --key-three 'data/input/Key 3 08-22-2025.xlsx'")
        print("  python src/pipeline/reporting/generate_key_three_emails.py "
              "data/raw/all_units_comprehensive_scored.json --output-dir data/output/emails/")
        print("  python src/pipeline/reporting/generate_key_three_emails.py "
              "data/raw/all_units_comprehensive_scored.json --include-all  # Include non-HNE units")
        sys.exit(1)
    
    # Parse arguments
    args = sys.argv[1:]
    output_dir = "data/output/emails/"
    hne_only = True  # Default to HNE units only
    key_three_file = "data/input/Key 3 08-22-2025.xlsx"  # Default Key Three file
    
    if "--output-dir" in args:
        output_idx = args.index("--output-dir")
        if output_idx + 1 < len(args):
            output_dir = args[output_idx + 1]
            args = args[:output_idx] + args[output_idx + 2:]  # Remove --output-dir and its value
    
    if "--key-three" in args:
        key_three_idx = args.index("--key-three")
        if key_three_idx + 1 < len(args):
            key_three_file = args[key_three_idx + 1]
            args = args[:key_three_idx] + args[key_three_idx + 2:]  # Remove --key-three and its value
    
    if "--include-all" in args:
        hne_only = False
        args.remove("--include-all")
    
    # Handle glob patterns
    all_files = []
    for pattern in args:
        if '*' in pattern or '?' in pattern:
            all_files.extend(glob.glob(pattern))
        else:
            all_files.append(pattern)
    
    if not all_files:
        print("No matching files found", file=sys.stderr)
        sys.exit(1)
    
    # Sort files for consistent output
    all_files.sort()
    
    # Initialize generator
    generator = KeyThreeEmailGenerator(key_three_file)
    
    all_generated_files = []
    for file_path in all_files:
        if not Path(file_path).exists():
            print(f"File not found: {file_path}", file=sys.stderr)
            continue
        
        print(f"\nProcessing: {file_path}")
        generated_files = generator.generate_emails_from_file(file_path, output_dir, hne_only)
        all_generated_files.extend(generated_files)
    
    print(f"\nGenerated {len(all_generated_files)} emails in {output_dir}")
    if all_generated_files:
        print("Sample files:")
        for file_path in all_generated_files[:3]:  # Show first 3
            print(f"  {file_path}")
        if len(all_generated_files) > 3:
            print(f"  ... and {len(all_generated_files) - 3} more")


if __name__ == "__main__":
    main()