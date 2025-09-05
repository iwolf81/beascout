#!/usr/bin/env python3
"""
Generate Unit Improvement Emails - Version 2

Fresh implementation for generating personalized improvement emails 
for Scouting units based on their BeAScout information quality analysis.

This script generates emails from scratch using the restructured data
architecture and follows the sample email templates exactly.
"""

import json
import argparse
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Tuple, Optional
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

from src.pipeline.parsing.key_three_parser import KeyThreeParser

class UnitEmailGenerator:
    """Generate personalized improvement emails for Scouting units"""
    
    def __init__(self):
        self.council_name = "Heart of New England Council"
        self.council_email = "[council contact email]"
        self.council_phone = "[council phone number]"
        self.analysis_date = datetime.now().strftime("%B %d, %Y")
        
        # Initialize parser for unit info extraction
        self.parser = None
        
        # Quality score grade mappings
        self.grade_thresholds = {
            'A': 90.0,
            'B': 80.0, 
            'C': 70.0,
            'D': 60.0,
            'F': 0.0
        }
    
    def load_unit_data(self, units_file_path: str) -> List[Dict]:
        """Load processed unit data with quality scores"""
        with open(units_file_path, 'r') as f:
            data = json.load(f)
        return data.get('units_with_scores', [])
    
    def load_key_three_data(self, key_three_file_path: str) -> Dict:
        """Load Key Three contact information from Excel or JSON"""
        import pandas as pd
        from pathlib import Path
        
        file_path = Path(key_three_file_path)
        
        if file_path.suffix.lower() == '.xlsx':
            # Initialize parser for unit info extraction
            self.parser = KeyThreeParser(key_three_file_path)
            
            # Load directly from Excel file
            df = pd.read_excel(key_three_file_path, header=8)
            print(f"Loaded {len(df)} Key Three member records from Excel")
            
            # Convert to the expected format
            key_three_members = []
            for _, row in df.iterrows():
                member_data = {
                    'district': str(row.get('districtname', '')).strip(),
                    'unit_display': str(row.get('displayname', '')).strip(),
                    'member_name': str(row.get('fullname', '')).strip(),
                    'address': str(row.get('address', '')).strip(),
                    'citystate': str(row.get('citystate', '')).strip(),
                    'zip': str(row.get('zip', '')).strip(),
                    'email': str(row.get('email', '')).strip(),
                    'phone': str(row.get('phone', '')).strip(),
                    'position': str(row.get('position', '')).strip(),
                    'unit_org_name': str(row.get('unitcommorgname', '')).strip(),
                    'ypt_status': str(row.get('yptstatus', '')).strip()
                }
                
                # Clean up missing data
                for key, value in member_data.items():
                    if value in ['nan', 'None', '', 'NaT']:
                        member_data[key] = ''
                
                key_three_members.append(member_data)
        
        else:
            raise ValueError(f"Unsupported file format. Only Excel .xlsx files are supported. Got: {file_path.suffix}")
        
        # Index by unit_key (unit_type_unit_number_town) for precise matching
        # This uses the same unit_key format as scraped data
        key_three_index = {}
        for member in key_three_members:
            unit_org_name = member.get('unit_org_name', '')
            
            # Extract unit info from unitcommorgname using existing parser
            unit_info = self.parser.extract_unit_info_from_unitcommorgname(unit_org_name)
            
            if unit_info and unit_info.get('unit_town'):
                # Create unit_key in same format as scraped data: "Troop 7012 Leominster" (no leading zeros)
                unit_number = unit_info['unit_number'].lstrip('0') or '0'  # Remove leading zeros, but keep '0' if all zeros
                unit_key = f"{unit_info['unit_type']} {unit_number} {unit_info['unit_town']}"
                
                if unit_key not in key_three_index:
                    key_three_index[unit_key] = []
                key_three_index[unit_key].append(member)
        
        return key_three_index
    
    def find_key_three_for_unit(self, unit: Dict, key_three_index: Dict) -> List[Dict]:
        """Find Key Three members for a specific unit using unit_key"""
        unit_key = unit.get('unit_key', '')
        
        # Direct lookup using unit_key (e.g., "Troop_7012_Leominster")
        if unit_key in key_three_index:
            return key_three_index[unit_key]
        
        return []
    
    def format_email_addresses(self, key_three_members: List[Dict]) -> Tuple[str, str]:
        """Format email addresses for TO field and names for greeting"""
        if not key_three_members:
            return "", ""
        
        emails = []
        names = []
        
        for member in key_three_members:
            email = member.get('email', '').strip()
            name = member.get('member_name', '').strip()
            
            if email:
                emails.append(email)
            if name:
                names.append(name)
        
        to_field = ", ".join(emails) if emails else "[no email available]"
        names_field = ", ".join(names) if names else "[Key Three names not available]"
        
        return to_field, names_field
    
    def analyze_missing_fields(self, unit: Dict) -> Tuple[List[str], List[str]]:
        """Analyze unit data to determine missing required and recommended fields"""
        required_missing = []
        recommended_missing = []
        
        # Check required fields based on quality tags
        quality_tags = unit.get('quality_tags', [])
        
        for tag in quality_tags:
            if tag == 'REQUIRED_MISSING_LOCATION':
                required_missing.append('meeting_location')
            elif tag == 'REQUIRED_MISSING_DAY':
                required_missing.append('meeting_day')
            elif tag == 'REQUIRED_MISSING_TIME':
                required_missing.append('meeting_time')
            elif tag == 'REQUIRED_MISSING_EMAIL':
                required_missing.append('contact_email')
            elif tag == 'RECOMMENDED_MISSING_PERSON':
                recommended_missing.append('contact_person')
            elif tag == 'RECOMMENDED_MISSING_PHONE':
                recommended_missing.append('phone_number')
            elif tag == 'RECOMMENDED_MISSING_WEBSITE':
                recommended_missing.append('website')
            elif tag == 'RECOMMENDED_MISSING_DESCRIPTION':
                recommended_missing.append('description')
            elif tag == 'QUALITY_PERSONAL_EMAIL':
                recommended_missing.append('professional_email')
        
        return required_missing, recommended_missing
    
    def format_unit_type_for_email(self, unit_type: str) -> str:
        """Format unit type for email context (e.g., troop -> Troop)"""
        return unit_type.lower()
    
    def get_existing_information(self, unit: Dict) -> List[str]:
        """Get list of existing positive information about the unit"""
        existing_info = []
        
        # Check chartered organization
        chartered_org = unit.get('chartered_organization', '').strip()
        if chartered_org:
            existing_info.append(f"**Chartered Organization**: {chartered_org} *(Clear sponsoring organization)*")
        
        # Check contact email
        contact_email = unit.get('contact_email', '').strip()
        if contact_email:
            if 'QUALITY_PERSONAL_EMAIL' not in unit.get('quality_tags', []):
                existing_info.append(f"**Contact Email**: {contact_email} *(Unit-specific email - great for continuity!)*")
            else:
                existing_info.append(f"**Contact Email**: {contact_email} *(Available)*")
        
        # Check website
        website = unit.get('website', '').strip()
        if website:
            website_display = website if website.startswith('http') else f"https://{website}"
            unit_type = self.format_unit_type_for_email(unit.get('unit_type', ''))
            existing_info.append(f"**Website**: {website_display} *({unit_type.capitalize()}-specific website available)*")
        
        # Check description/program description
        description = unit.get('description', '').strip()
        if description and len(description) > 20:
            # Show entire description, clean up formatting
            full_description = description.replace('\n', ' ').replace('\r', '').strip()
            # Remove extra whitespace
            full_description = ' '.join(full_description.split())
            existing_info.append(f"**Program Description**: \"{full_description}\" *(Welcoming and informative)*")
        
        # Check meeting location
        meeting_location = unit.get('meeting_location', '').strip()
        if meeting_location:
            if 'QUALITY_POBOX_LOCATION' not in unit.get('quality_tags', []):
                existing_info.append(f"**Meeting Location**: {meeting_location} *(Complete address provided)*")
        
        return existing_info
    
    def generate_required_recommendations(self, unit: Dict, required_missing: List[str]) -> str:
        """Generate required field recommendations"""
        if not required_missing:
            return ""
        
        unit_type = self.format_unit_type_for_email(unit.get('unit_type', ''))
        recommendations = []
        
        for field in required_missing:
            if field == 'meeting_location':
                recommendations.append(f"""**1. Meeting Location** *(Missing - Required)*
- Families need to know where your {unit_type.capitalize()} meets to attend meetings and events
- **Action**: Update the Unit Meeting Address field with the full street address (e.g., "Boardwalk Campus School, 71-75 Spruce St, Acton MA 01720")""")
            
            elif field == 'meeting_day' or field == 'meeting_time':
                # Group day and time together
                if 'meeting_day' in required_missing and 'meeting_time' in required_missing:
                    if field == 'meeting_day':  # Only add once
                        recommendations.append(f"""**2. Meeting Day & Time** *(Missing - Required)*
- Families searching for Scouting need to know when your {unit_type.capitalize()} meets to plan their schedule
- **Action**: Please update the Description field with your regular meeting day and time (e.g., "Every Thursday, 7:00 PM - 8:30 PM")""")
                elif field == 'meeting_day' and 'meeting_time' not in required_missing:
                    recommendations.append(f"""**2. Meeting Day** *(Missing - Required)*
- Families searching for Scouting need to know when your {unit_type.capitalize()} meets to plan their schedule
- **Action**: Please update the Description field with your regular meeting day (e.g., "Every Thursday")""")
                elif field == 'meeting_time' and 'meeting_day' not in required_missing:
                    recommendations.append(f"""**2. Meeting Time** *(Missing - Required)*
- Families searching for Scouting need to know when your {unit_type.capitalize()} meets to plan their schedule
- **Action**: Please update the Description field with your regular meeting time (e.g., "7:00 PM - 8:30 PM")""")
            
            elif field == 'contact_email':
                unit_name = f"{unit_type}{unit.get('unit_number', '').lstrip('0')}{unit.get('unit_town', '').lower()}"
                recommendations.append(f"""**3. Contact Email** *(Missing - Required)*
- Families need a way to ask questions and get information about joining
- **Action**: Please update the Contact Information field with a {unit_type.capitalize()} email address (preferably unit-specific like {unit_name}@gmail.com)
- **Best Practice**: Use an email account that can be monitored by multiple unit leaders""")
        
        if recommendations:
            return "### 🔴 **High Priority - Missing Critical Information:**\n\n" + "\n\n".join(recommendations)
        return ""
    
    def generate_recommended_improvements(self, unit: Dict, recommended_missing: List[str]) -> str:
        """Generate recommended field improvements"""
        if not recommended_missing:
            return ""
        
        unit_type = self.format_unit_type_for_email(unit.get('unit_type', ''))
        recommendations = []
        counter = 4  # Start after required recommendations
        
        for field in recommended_missing:
            if field == 'contact_person':
                recommendations.append(f"""**{counter}. Contact Person** *(Missing - Recommended)*
- Provides families with a specific person to contact for questions
- **Action**: Consider adding the unit leader's name or designated person to the Contact Information field""")
                counter += 1
            
            elif field == 'phone_number':
                recommendations.append(f"""**{counter}. Phone Number** *(Missing - Recommended)*
- Provides families an immediate way to get questions answered
- **Action**: Consider adding a phone number to the Contact Information field
- **Best Practice**: Update BeAScout whenever the phone number needs to change (e.g., when a different leader handles inquiries)""")
                counter += 1
            
            elif field == 'website':
                recommendations.append(f"""**{counter}. Website** *(Missing - Recommended)*
- Allows families to learn more about your unit's activities and culture
- **Action**: Consider creating a simple website or social media page with unit information
- **Best Practice**: Update the Contact Information field with the unit's website""")
                counter += 1
            
            elif field == 'description':
                recommendations.append(f"""**{counter}. Program Description** *(Missing - Recommended)*
- Helps families understand what makes your {unit_type.capitalize()} special
- **Action**: Add a welcoming description of your unit's activities and culture to the Description field
- **Best Practice**: Include highlights and special characteristics of your unit""")
                counter += 1
            
            elif field == 'professional_email':
                unit_name = f"{unit_type.lower()}{unit.get('unit_number', '').lstrip('0')}{unit.get('unit_town', '').lower()}"
                recommendations.append(f"""**{counter}. Professional Email Address** *(Recommended Improvement)*
- Current email appears to be personal rather than unit-specific
- **Action**: Consider creating a {unit_type.capitalize()}-specific email address (e.g., {unit_name}@gmail.com)
- **Best Practice**: Unit-specific emails provide better continuity and can be monitored by multiple leaders""")
                counter += 1
        
        if recommendations:
            return "### 🟡 **Recommended - Additional Information:**\n\n" + "\n\n".join(recommendations)
        return ""
    
    def generate_email_content(self, unit: Dict, key_three_members: List[Dict]) -> str:
        """Generate complete email content for a unit (existing or missing)"""
        # Check if this is a missing unit (passed as unit_display string) or existing unit
        if isinstance(unit, str):
            # This is a missing unit - create a minimal unit dict
            unit_display = unit
            parts = unit_display.split()
            if len(parts) >= 2:
                unit_type = parts[0].capitalize()
                unit_number = parts[1].lstrip('0') or '0'
            else:
                unit_type = "Unit"
                unit_number = "Unknown"
            
            # Extract unit info using existing KeyThreeParser
            unit_town = ''
            if key_three_members:
                unit_org_name = key_three_members[0].get('unit_org_name', '')
                if unit_org_name:
                    # Use the existing sophisticated parser
                    parser = KeyThreeParser("")  # We don't need to load data, just use parsing logic
                    unit_info = parser.extract_unit_info_from_unitcommorgname(unit_org_name)
                    if unit_info:
                        # Override the parsed values with the more accurate results
                        unit_type = unit_info.get('unit_type', unit_type)
                        unit_number = unit_info.get('unit_number', '').lstrip('0') or '0'
                        unit_town = unit_info.get('unit_town', '')
            
            unit = {
                'unit_type': unit_type.lower(),
                'unit_number': unit_number,
                'unit_town': unit_town,
                'chartered_organization': '',
                'completeness_score': 0.0,
                'quality_tags': [],
                'is_missing_unit': True,
                'unit_display': unit_display
            }
        
        # Extract unit information
        unit_type = unit.get('unit_type', '').capitalize()
        unit_number = unit.get('unit_number', '').lstrip('0')
        unit_town = unit.get('unit_town', '')
        chartered_org = unit.get('chartered_organization', '')
        completeness_score = unit.get('completeness_score', 0.0)
        is_missing_unit = unit.get('is_missing_unit', False)
        
        # Format Key Three information
        to_emails, key_three_names = self.format_email_addresses(key_three_members)
        
        # Unit identifier - include town name for missing units too
        if is_missing_unit:
            # Use extracted town name if available, otherwise fall back to unit_display
            if unit_town:
                unit_identifier = f"{unit_type} {unit_number} {unit_town}"
            else:
                unit_identifier = unit.get('unit_display', f"{unit_type} {unit_number}")
            subject = f"{unit_identifier} - URGENT: BeAScout Setup Needed - Help Families Find Your {unit_type}"
        else:
            unit_identifier = f"{unit_type} {unit_number} {unit_town}"
            subject = f"{unit_identifier} - BeAScout Information Review - Help Families Find Your {unit_type}"
        
        # Analyze missing fields
        required_missing, recommended_missing = self.analyze_missing_fields(unit)
        
        # Get existing information
        existing_info = self.get_existing_information(unit)
        
        # Generate email sections
        required_section = self.generate_required_recommendations(unit, required_missing)
        recommended_section = self.generate_recommended_improvements(unit, recommended_missing)
        
        # Build email content
        email_parts = []
        
        # Header - different for missing vs existing units
        if is_missing_unit:
            email_parts.append(f"# {unit_identifier} - Key Three Setup Email\n")
        else:
            email_parts.append(f"# {unit_identifier} - Key Three Improvement Email\n")
        
        email_parts.append(f"**TO:** {unit_identifier} Key Three Members ({to_emails})\n")
        email_parts.append(f"**FROM:** {self.council_name}, Scouting America\n")
        email_parts.append(f"**SUBJECT:** {subject}\n")
        email_parts.append("---\n")
        
        # Greeting - different for missing vs existing units
        email_parts.append(f"Dear {unit_identifier} Key Three ({key_three_names}),\n")
        
        if is_missing_unit:
            email_parts.append(f"The {self.council_name} maintains records of all active units and their Key Three leadership. However, during our periodic review of unit information on BeAScout.org, we discovered that **{unit_identifier} does not appear to have a presence in BeAScout**.\n")
        else:
            email_parts.append(f"The {self.council_name} periodically reviews unit information on BeAScout.org to help prospective Scout families easily find complete, accurate information about local units. We've completed a review of {unit_identifier}'s presence in BeAScout and wanted to share our findings and recommendations.\n")
        
        # Current Quality Section - different title for missing units
        if is_missing_unit:
            email_parts.append(f"## Your {unit_type.capitalize()}'s Current Online Status\n")
        else:
            email_parts.append(f"## Your {unit_type.capitalize()}'s Current Information Quality\n")
        email_parts.append(f"**Overall Completeness Score: {completeness_score}%**\n")
        
        # Existing Information - conditional header based on score
        if existing_info:
            if completeness_score >= 80:
                info_header = "### ✅ **Excellent Information Available:**"
            elif completeness_score >= 12.5:
                info_header = "### ✅ **Good Information Available:**"
            elif len(existing_info) == 1 and 'Chartered Organization' in existing_info[0]:
                # Only chartered org info available - this is minimal info
                info_header = "### ✅ **Basic Information Available:**"
            else:
                info_header = "### ✅ **Information Available:**"
        else:
            # No information available at all - unit not found on BeAScout/JoinExploring
            info_header = "### ❌ **No Information Available:**"
        
        email_parts.append(info_header)
        if existing_info:
            for info in existing_info:
                email_parts.append(f"{info}")
        else:
            email_parts.append("## Recommendations for Configuring BeAScout:\n")
            email_parts.append(f"Families searching for Scouting in your area cannot find your unit online. Guidance and instructions for configuring BeAScout.org for your {unit_type.capitalize()} follow below.")
        email_parts.append("")
        
        # Recommendations, Congratulations, or Critical Setup (for missing units)
        if is_missing_unit:
            # Required Setup Information for missing units
            email_parts.append("### 🔴 **Required Setup Information:**\n")
            email_parts.append("**1. Meeting Location** *(Missing - Critical)*")
            email_parts.append(f"- Families need to know where your {unit_type.capitalize()} meets")
            email_parts.append("- **Action**: Add the complete meeting address (e.g., \"Community Center, 123 Main St, YourTown MA 01234\")\n")
            
            email_parts.append("**2. Meeting Schedule** *(Missing - Critical)*")
            email_parts.append(f"- Families need to know when your {unit_type.capitalize()} meets to plan their schedule")
            email_parts.append("- **Action**: Add meeting day and time (e.g., \"Every Tuesday, 7:00 PM - 8:30 PM\")\n")
            
            email_parts.append("**3. Contact Information** *(Missing - Critical)*")
            email_parts.append("- Families need a way to ask questions and get information about joining")
            email_parts.append(f"- **Action**: Add a {unit_type.capitalize()}-specific email address such as {unit_type.lower()}{unit_number}{unit_town.lower()}@gmail.com and an optional a phone number\n")

            # Add recommended section for missing units to achieve 100% score
            email_parts.append("### 🟡 **Recommended - Additional Information:**\n")
            email_parts.append("**4. Contact Person** *(Missing - Recommended)*")
            email_parts.append("- Provides families with a specific person to contact for questions")
            email_parts.append("- **Action**: Add the unit leader's name or designated person to the Contact Information field\n")
            
            email_parts.append("**5. Phone Number** *(Missing - Recommended)*")
            email_parts.append("- Provides families an immediate way to get questions answered")
            email_parts.append("- **Action**: Add a phone number to the Contact Information field")
            email_parts.append("- **Best Practice**: Update BeAScout whenever the phone number needs to change (e.g., when a different leader handles inquiries)\n")
            
            email_parts.append("**6. Website** *(Missing - Recommended)*")
            email_parts.append("- Allows families to learn more about your unit's activities and culture")
            email_parts.append("- **Action**: Consider creating a simple website or social media page with unit information")
            email_parts.append("- **Best Practice**: Update the Contact Information field with the unit's website\n")
            
            email_parts.append("**7. Program Description** *(Missing - Recommended)*")
            email_parts.append(f"- Helps families understand what makes your {unit_type.capitalize()} special")
            email_parts.append("- **Action**: Add a welcoming description of your unit's activities and culture to the Description field")
            email_parts.append("- **Best Practice**: Include highlights and special characteristics of your unit\n")
            
        elif required_section or recommended_section:
            email_parts.append("## Recommendations for Improvement:\n")
            
            if required_section:
                email_parts.append(required_section + "\n")
            
            if recommended_section:
                email_parts.append(recommended_section + "\n")
        else:
            # Unit has complete information - congratulate them!
            unit_type_lower = self.format_unit_type_for_email(unit.get('unit_type', ''))
            email_parts.append("## Congratulations!\n")
            email_parts.append(f"## Your {unit_type.capitalize()}'s Current Online Status\n")
            email_parts.append(f"🎉 **Excellent work!** Your {unit_type.capitalize()} has complete, family-friendly information on BeAScout.org. Families searching for Scouting in your area will easily find all the details they need to connect with {unit_identifier}.\n")

        # Guidelines section
        email_parts.append("## Guidelines for Effective BeAScout Information\n")
        email_parts.append("### **Prove a welcoming and informative description**")
        email_parts.append("- Describe the type of activities your unit does in the Description field.")
        email_parts.append("- Identify highlights and special characteristics of your unit\n")
        
        email_parts.append("### **Spell out full names for days and months:**")
        email_parts.append("- Include clearly defined meeting day, time, and frequency in the Description field:")
        email_parts.append('  - "Every Thursday, 7:00 PM - 8:30 PM, during the school year"')
        email_parts.append('  - Avoid abbreviations like "Thurs." or "Thu"\n')
        
        email_parts.append("### **Meeting Information Best Practices:**")
        email_parts.append("- Populate the Unit Meeting Address field")
        email_parts.append("- Use consistent 12-hour format with AM/PM (7:00 PM - 8:30 PM) for meeting times")
        email_parts.append('- Include frequency information: "Every Thursday" or "First and third Monday of each month"')
        email_parts.append("- Provide both start and end times when possible\n")
        
        email_parts.append("### **Contact Information Continuity:**")
        email_parts.append(f"- Use a unit-specific email address when possible")
        email_parts.append("- Ensure three unit leaders have access to the email account to ensure inquiries are promptly responded to\n")
        
        # Next Steps
        email_parts.append("## Next Steps\n")
        email_parts.append("1. **Update Missing Information**: Please provide the critical missing information identified above")
        email_parts.append("2. **How to Update BeAScout**: ")
        email_parts.append("   - Log into my.scouting.org with your ScoutBook credentials")
        email_parts.append("   - From the Menu, select your unit and then Organization Manager")
        email_parts.append("   - Follow the detailed instructions at")
        email_parts.append("     https://www.scouting.org/wp-content/uploads/2020/05/Be-A-Scout-Pin-Set-up.pdf")
        email_parts.append("3. **Review During Rechartering**: Recommend reviewing information during the annual rechartering process\n")
        
        # Contact information
        email_parts.append("## Questions or Need Help?\n")
        email_parts.append("If you need assistance updating your unit's information or have questions about these recommendations, please contact:\n")
        email_parts.append(f"**{self.council_name}**")
        email_parts.append(f"Email: {self.council_email}")
        email_parts.append(f"Phone: {self.council_phone}\n")
        
        # Motivational closing - different for low vs higher scores
        if completeness_score < 30:
            email_parts.append(f"Your unit's online presence is currently missing essential information that prevents families from finding and connecting with you. Updating these basic details will dramatically improve your ability to recruit new Scouts and help families discover the great program {unit_identifier} offers!\n")
        else:
            email_parts.append(f"Thank you for your leadership in Scouting and for helping families discover the great program {unit_identifier} offers!\n")
        
        # Sign off
        email_parts.append("Yours in Scouting,\n")
        email_parts.append(f"**{self.council_name}**")
        email_parts.append("*Unit Support Team*\n")
        email_parts.append("---\n")
        
        # Unit details
        meeting_location = unit.get('meeting_location', '').strip() or "Not specified"
        review_date = datetime.now().strftime("%B %d, %Y")
        review_id = f"{unit_type.upper()}_{unit_number}_{unit_town.upper()}_{datetime.now().strftime('%m%d%y')}"
        
        # Footer
        email_parts.append(f"**Note**: This review was generated using the Council's automated BeAScout information analysis system. Information was analyzed from BeAScout.org on {review_date}. If you've recently updated your information, please allow time for changes to be reflected in our next review.\n")
        
        email_parts.append(f"**{unit_identifier} Details Reviewed:**")
        email_parts.append(f"- Unit Type: {unit_type.capitalize()}")
        email_parts.append(f"- Charter Organization: {chartered_org}")
        email_parts.append(f"- Meeting Location: {meeting_location}")
        email_parts.append(f"- Analysis Date: {review_date}")
        email_parts.append(f"- Review ID: {review_id}")
        
        return "\n".join(email_parts)
    

def main():
    parser = argparse.ArgumentParser(
        description='Generate personalized improvement emails for Scouting units',
        epilog="""
Examples:
  python generate_unit_emails_v2.py data/raw/all_units_comprehensive_scored.json data/input/HNE_key_three.xlsx
  python generate_unit_emails_v2.py data/raw/all_units_comprehensive_scored.json "data/input/Key 3 08-22-2025.xlsx" --output-dir emails/
        """,
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument(
        'units_file',
        help='Path to processed units JSON file with quality scores'
    )
    
    parser.add_argument(
        'key_three_file', 
        help='Path to Key Three contacts file (Excel .xlsx format only)'
    )
    
    parser.add_argument(
        '--output-dir',
        default='data/output/emails',
        help='Output directory for email files (default: data/output/emails)'
    )
    
    parser.add_argument(
        '--unit-filter',
        help='Only generate emails for units matching this string (e.g., "Pack 32")'
    )
    
    parser.add_argument(
        '--max-units',
        type=int,
        help='Maximum number of emails to generate (for testing)'
    )
    
    args = parser.parse_args()
    
    # Create output directory
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Initialize email generator
    generator = UnitEmailGenerator()
    
    # Load data
    print(f"Loading unit data from {args.units_file}")
    units = generator.load_unit_data(args.units_file)
    
    print(f"Loading Key Three data from {args.key_three_file}")
    key_three_index = generator.load_key_three_data(args.key_three_file)
    
    # Filter units if requested
    if args.unit_filter:
        original_count = len(units)
        units = [u for u in units if args.unit_filter.lower() in u.get('unit_key', '').lower()]
        print(f"Filtered units from {original_count} to {len(units)} matching '{args.unit_filter}'")
    
    # Limit units if requested
    if args.max_units:
        units = units[:args.max_units]
        print(f"Limited to first {len(units)} units")
    
    print(f"\nGenerating emails for {len(units)} units...")
    
    generated_count = 0
    skipped_count = 0
    
    for unit in units:
        unit_key = unit.get('unit_key', 'Unknown_Unit')
        print(f"Processing {unit_key}...")
        
        # Find Key Three members for this unit
        key_three_members = generator.find_key_three_for_unit(unit, key_three_index)
        
        if not key_three_members:
            print(f"  Warning: No Key Three members found for {unit_key}")
            skipped_count += 1
            continue
        
        # Generate email content
        email_content = generator.generate_email_content(unit, key_three_members)
        
        # Save email to file
        safe_filename = unit_key.replace(' ', '_').replace('/', '_')
        email_file = output_dir / f"{safe_filename}_improvement_email.md"
        
        with open(email_file, 'w') as f:
            f.write(email_content)
        
        print(f"  Generated: {email_file}")
        generated_count += 1
    
    print(f"\n📧 EMAIL GENERATION COMPLETE:")
    print(f"  Generated: {generated_count} emails")
    print(f"  Skipped: {skipped_count} units (no Key Three data)")
    print(f"  Output directory: {output_dir}")

if __name__ == "__main__":
    main()