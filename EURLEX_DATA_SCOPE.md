# 🇪🇺 EUR-Lex Data Scope for Trade Scraper

## 🎯 **Target Data Categories**

### **Primary Sources (High Priority)**

#### **1. Legal Acts** ⭐⭐⭐
- **Regulations (REG)** - Main EU trade defense measures
  - Council Regulation imposing antidumping duties
  - Commission Regulation on countervailing duties
  - Safeguard measures regulations

- **Decisions (DEC)** - Commission trade decisions
  - Initiation of antidumping investigations
  - Provisional duty decisions
  - Definitive duty decisions
  - Review decisions (sunset, interim, circumvention)

- **Directives (DIR)** - Trade policy directives
  - Trade defense instruments directive
  - Implementation directives

#### **2. Preparatory Documents** ⭐⭐
- **Communications (COM)** - Commission proposals
  - Proposals for new trade measures
  - Policy communications on trade defense

- **Staff Working Documents (SWD)** - Technical analysis
  - Impact assessments for trade measures
  - Economic analysis of dumping/subsidies
  - Market analysis documents

- **Joint Communications (JOIN)** - Inter-institutional documents
  - Joint proposals on trade policy

### **Secondary Sources (Medium Priority)**

#### **3. EU Case-Law** ⭐
- **Court of Justice cases** - Appeals of trade measures
- **General Court decisions** - First instance trade cases
- **Advocate General opinions** - Legal analysis

### **Excluded Categories** ❌

- **Treaties** - Too high-level for specific cases
- **Consolidated texts** - Historical compilations
- **International agreements** - Unless trade-specific
- **EFTA documents** - Different legal framework
- **National law** - We want EU-level measures
- **Summaries** - We want original documents

## 📊 **Metadata Fields Collected**

| Field | Description | Example |
|-------|-------------|---------|
| **DN** | Document Number | 32024R0123 |
| **TI** | Title | Council Regulation imposing antidumping duties on phosphate imports |
| **DD** | Document Date | 2024-03-15 |
| **AU** | Author | European Commission |
| **OJ** | Official Journal | L 123/45 |
| **FM** | Form | REG, DEC, DIR, COM, SWD |
| **SU** | Subject | Trade defense, antidumping, phosphate |
| **TX** | Text Content | Full document text |
| **TE** | Text Excerpt | Summary excerpt |
| **RJ** | Legal Basis | Treaty articles |
| **LB** | Legal Basis Detail | Article 108 TFEU |
| **DF** | Date of Effect | 2024-04-01 |
| **DG** | Directorate General | DG Trade |
| **DT** | Document Type | Regulation |

## 🔍 **Search Strategy**

### **Keyword Matching (3-Group AND Logic)**

1. **Trade Measures** (Group A)
   - antidumping, countervailing duty, CVD, safeguard
   - review, sunset review, circumvention
   - trade defense, dumping, subsidy

2. **Products** (Group B)  
   - phosphate, phosphate rock, phosphoric acid
   - fertilizer, DAP, MAP, TSP, SSP
   - HS codes: 25*, 31*, 3103, 3105

3. **Entities** (Group C)
   - Countries: Morocco, Jordan
   - Companies: OCP, Mosaic, Nutrien, Yara, ICL, etc.

### **Document Type Priority**

1. **REG** - Regulations (highest priority)
2. **DEC** - Decisions (high priority)
3. **COM** - Communications (medium priority)
4. **SWD** - Working documents (medium priority)
5. **DIR** - Directives (low priority)

### **Authority Focus**

- European Commission (main authority)
- DG Trade (Directorate-General for Trade)
- Council of the European Union (for regulations)

## 📈 **Expected Results**

Based on this scope, you should find:

- **10-50 documents per year** matching all criteria
- **Main document types**: Regulations, Decisions, Communications
- **Key areas**: Antidumping duties, countervailing duties, reviews
- **Geographic focus**: Morocco, Jordan, other phosphate producers
- **Company mentions**: OCP, major fertilizer companies

## 🔄 **Query Optimization**

The scraper is configured to:
1. **Search efficiently** - Focus on relevant document types
2. **Filter precisely** - 3-group AND logic for relevance
3. **Capture metadata** - All important fields for analysis
4. **Sort chronologically** - Latest documents first
5. **Handle pagination** - Process large result sets

This targeted approach ensures you get **high-quality, relevant trade regulation data** while avoiding noise from unrelated EU documents.
