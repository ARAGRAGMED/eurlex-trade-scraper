# EUR-Lex Data Scope for Trade Scraper

## Overview
This document outlines the target data categories for the EUR-Lex Trade Scraper, which uses **web scraping** to extract trade-related documents from EUR-Lex's Advanced Search interface.

## Data Collection Method
- **Approach**: Web scraping of EUR-Lex Advanced Search results
- **Why not SOAP**: SOAP API requires complex ECAS authentication that's difficult to automate
- **Result**: Same data, more reliable access method

## Target Document Categories

### Primary Focus
1. **Legal Acts**
   - Regulations
   - Decisions  
   - Directives
   - Communications

2. **Preparatory Documents**
   - Commission proposals
   - Council positions
   - European Parliament opinions

3. **EU Case-Law**
   - Court of Justice judgments
   - General Court decisions

### Document Types Specifically Sought
- **Trade Defense Measures**: Antidumping, countervailing duties, safeguards
- **Import/Export Regulations**: Tariffs, quotas, licensing requirements
- **Trade Agreements**: Implementation measures
- **Market Access**: Barriers, restrictions, facilitations

## Exclusions
- **National Legislation**: Only EU-level documents
- **Historical Documents**: Focus on current and recent documents
- **Non-Trade Documents**: Administrative, institutional, or other policy areas

## Data Fields Extracted
- **Document Number (CELEX)**: Unique identifier
- **Title**: Document title
- **Publication Date**: Official publication date
- **Document Type**: Regulation, Decision, etc.
- **Author**: Commission, Council, Parliament, etc.
- **Text Excerpt**: Relevant content snippets
- **URL**: Direct link to EUR-Lex document
- **Match Details**: Which keywords matched and why

## Keyword Matching Strategy
The scraper uses a **3-group AND logic**:
1. **Trade Measures**: Must contain trade-related terms
2. **Products**: Must mention specific products (phosphate, fertilizers, etc.)
3. **Entities**: Must reference specific companies or countries

**All groups must match** for a document to be included in results.

## Data Quality Assurance
- **Deduplication**: Based on CELEX number and title
- **Validation**: Check for required fields before inclusion
- **Filtering**: Remove documents that don't meet keyword criteria
- **Logging**: Detailed logs of matching decisions for transparency
