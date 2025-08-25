#!/usr/bin/env python3
"""
Check Excel Report for Key Three Contact Information
Verify that missing units have proper contact details
"""

import pandas as pd

def check_excel_contacts():
    """Check the Excel report for Key Three contact information"""
    
    try:
        # Read the Excel report (use the newest one)
        excel_file = "data/output/reports/HNE_Council_BeAScout_Report_20250825_144233.xlsx"
        
        # Read the Quinapoxet sheet
        df_quinapoxet = pd.read_excel(excel_file, sheet_name='Quinapoxet District', skiprows=24)  # Skip header rows
        
        print("Checking Quinapoxet District units...")
        print(f"Total units in Quinapoxet sheet: {len(df_quinapoxet)}")
        
        # Check for units with missing BeAScout scores (these should be the missing units)
        missing_units = df_quinapoxet[df_quinapoxet['BeAScout Score (%)'] == 0]
        
        print(f"Units missing from web (0 scores): {len(missing_units)}")
        
        # Check if these missing units have Key Three contact information
        for index, unit in missing_units.head(5).iterrows():
            unit_type = unit.get('Unit Type', '')
            unit_number = unit.get('Unit Number', '')
            town = unit.get('Town', '')
            
            key_three_1_name = unit.get('Key Three #1 Name', '')
            key_three_1_email = unit.get('Key Three #1 Email', '')
            key_three_2_name = unit.get('Key Three #2 Name', '')
            key_three_3_name = unit.get('Key Three #3 Name', '')
            
            print(f"\n{unit_type} {unit_number} {town}:")
            if key_three_1_name and key_three_1_name != 'None':
                print(f"  ✅ Key Three #1: {key_three_1_name} - {key_three_1_email}")
                if key_three_2_name and key_three_2_name != 'None':
                    print(f"  ✅ Key Three #2: {key_three_2_name}")
                if key_three_3_name and key_three_3_name != 'None':
                    print(f"  ✅ Key Three #3: {key_three_3_name}")
            else:
                print(f"  ❌ No Key Three contacts found")
        
        # Check columns available
        print(f"\nColumns in Excel sheet: {list(df_quinapoxet.columns)}")
        
        return len(missing_units)
        
    except Exception as e:
        print(f"Error reading Excel file: {e}")
        return 0

if __name__ == '__main__':
    missing_count = check_excel_contacts()
    print(f"\n📊 Excel Report Check:")
    print(f"   Missing units found: {missing_count}")
    print(f"   Key Three contacts should be populated for commissioners to contact these units")