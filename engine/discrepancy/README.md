# Discrepancy Engine (`engine/discrepancy`)

The **Discrepancy Engine** compares Resume, LinkedIn, and Portfolio profiles to find inconsistencies. It provides a granular comparison table showing the actual values from each source.

## Core Components

### 1. `models.py`
Pydantic schemas for structured output:
- `ProfileItem` - Single item with values from each source
- `DiscrepancyItem` - Detailed discrepancy with severity
- `SkillComparison` - Skills matrix (backward compatible)
- `ProfileDiscrepancy` - Complete analysis result

### 2. `analyzer.py`
`DiscrepancyAnalyzer` class for LLM-based analysis:
- Compares dates, job titles, skills, projects across sources
- Returns structured `ProfileDiscrepancy` result

### 3. `formatter.py`
`TableFormatter` class for UI-ready output:
- Comparison table with all items and values
- Filtered views: mismatches, partial presence
- Legacy skill and discrepancy tables

### 4. `checker.py`
Backward-compatible wrapper functions.

## Usage

### Modern OOP Style
```python
from engine.discrepancy import DiscrepancyAnalyzer, TableFormatter

analyzer = DiscrepancyAnalyzer()
result = analyzer.analyze(resume_data, linkedin_data, portfolio_data)

formatter = TableFormatter()
tables = formatter.format_all(result)

# Access the comparison table
for row in tables['comparison_table']['rows']:
    print(row)  # [category, field, resume_val, linkedin_val, portfolio_val, status]
```

### Backward Compatible Style
```python
from engine.discrepancy import compare_profile_sources, format_for_table

result = compare_profile_sources(resume_data, linkedin_data, portfolio_data)
tables = format_for_table(result)
```

## Output Format

### Comparison Table
| Category | Field | Resume | LinkedIn | Portfolio | Status |
|----------|-------|--------|----------|-----------|--------|
| job_title | Current Role | Senior Eng | Staff Eng | Lead Eng | ⚠️ Mismatch |
| date | Company X End | 2023-06 | 2023-08 | - | ⚠️ Mismatch |
| skill | Python | ✓ | ✓ | - | 📝 Partial |
| skill | React | ✓ | ✓ | ✓ | ✅ Match |

### Status Types
- **✅ Match**: All sources have the same value
- **⚠️ Mismatch**: Different values across sources
- **📝 Partial**: Item missing from at least one source
