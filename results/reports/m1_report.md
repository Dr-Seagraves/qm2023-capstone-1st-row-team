# Milestone 1 Report: Data Preparation
**QM 2023 Capstone Project**  
**February 24, 2026**

---

## Research Question

We're investigating whether hurricanes in Florida affect real estate investment trust (REIT) returns. Specifically, we want to know if years with more hurricane activity lead to lower returns for residential and retail REITs that own properties in Florida.

---

## Datasets We Collected

**1. Zillow Housing Market Data**
- Monthly housing data 
- Includes Florida metro areas like Miami, Tampa, Orlando, and Jacksonville
- Tracks home values, rental prices, inventory, and sales

**2. NOAA Hurricane Data**
- Historical hurricane records from the National Hurricane Center
- Information on storm names, dates, wind speeds, and locations
- Filtered to include only storms that came within 60 miles of Florida

**3. NOAA Economic Impact Data**
- Cost estimates for hurricane damage (billions of dollars)
- Casualty counts and event dates
- Covers Florida landfalls from 1980-2024

---

## How We Cleaned and Merged the Data

**Step 1: Cleaning**
- We imported all the raw data files and standardized the column names so they matched
- Removed missing values and corrected data types
- Filtered everything down to just Florida data

**Step 2: Merging**
- Combined the hurricane storm data with economic damage costs by matching storm names and dates
- Merged all the different Zillow housing metrics into one file organized by month and metro area
- Created a master dataset that brings together hurricane activity and housing market data

**Step 3: Final Output**
- Built our final analysis file located at `data/final/master_dataset.csv`
- Created a data dictionary that explains what each column means

---

## What's in Our Final Dataset

Our final dataset combines information about Florida hurricanes and housing markets:

**Hurricane Information:**
- Storm dates and names
- Wind speeds and categories
- Economic damage costs
- Summary of storms within 60 miles of Florida

**Housing Market Information:**
- Home values and rental prices by metro area
- Monthly data for Florida cities
- Sales counts and inventory levels

The data is saved in `data/final/master_dataset.csv` and includes a data dictionary at `data/final/data_dictionary.json` that explains each variable.