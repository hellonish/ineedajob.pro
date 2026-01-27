"""
Unified Profile Manager.

Aggregates data from multiple sources (Resume, LinkedIn, Portfolio) into a single master profile.
"""

from typing import Dict, Any, List, Set, Optional

def create_unified_profile(sources: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """
    Merge multiple profile sources into a Unified Profile.

    Args:
        sources: Dictionary mapping source type ('resume', 'linkedin', 'portfolio') 
                 to the parsed profile data (dict).

    Returns:
        Unified profile dictionary matching HybridResume schema.
    """
    # 1. Initialize with primary source or fallback
    base_data = sources.get('resume') or sources.get('linkedin') or sources.get('portfolio')
    if not base_data:
        return {} 

    # Start with a deep copy of structure to avoid mutating original
    import copy
    unified = copy.deepcopy(base_data)
    
    # 2. Merge Basics (Resume > LinkedIn > Portfolio)
    _merge_basics(unified, sources)

    # 3. Merge Skills (Union)
    unified['skills'] = _merge_skills(sources)

    # 4. Merge Work Experience (Aggregate & Sort)
    unified['work_experience'] = _merge_work_experience(sources)

    # 5. Merge Education (Aggregate & Sort)
    unified['education'] = _merge_education(sources)

    # 6. Merge Dynamic Sections
    unified['dynamic_sections'] = _merge_dynamic_sections(sources)

    return unified


def _merge_basics(unified: Dict[str, Any], sources: Dict[str, Dict[str, Any]]):
    """Enrich basics with missing fields from other sources."""
    # Priority: Resume (already in unified) > LinkedIn > Portfolio
    
    # Ensure structure exists
    if 'basics' not in unified: unified['basics'] = {}
    if 'contact_info' not in unified['basics']: unified['basics']['contact_info'] = {}

    main_contact = unified['basics']['contact_info']
    
    for source_type in ['resume', 'linkedin', 'portfolio']:
        data = sources.get(source_type)
        if not data: continue
        
        contact = data.get('basics', {}).get('contact_info', {})
        
        # Fill missing fields
        if not main_contact.get('email') and contact.get('email'):
            main_contact['email'] = contact.get('email')
        if not main_contact.get('phone') and contact.get('phone'):
            main_contact['phone'] = contact.get('phone')
        if not main_contact.get('linkedin_url') and contact.get('linkedin_url'):
            main_contact['linkedin_url'] = contact.get('linkedin_url')
        if not main_contact.get('portfolio_url') and contact.get('portfolio_url'):
            main_contact['portfolio_url'] = contact.get('portfolio_url')


def _merge_skills(sources: Dict[str, Dict[str, Any]]) -> List[str]:
    """Union of all skills."""
    all_skills: Set[str] = set()
    for data in sources.values():
        skills = data.get('skills', [])
        # Add all skills
        for skill in skills:
            if isinstance(skill, str):
                all_skills.add(skill)
    return list(all_skills)


def _merge_work_experience(sources: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Aggregate all work items and sort by date."""
    all_items = []
    seen = set()
    
    # Order: Resume -> LinkedIn -> Portfolio
    for source_type in ['resume', 'linkedin', 'portfolio']:
        data = sources.get(source_type)
        if not data: continue
        
        for item in data.get('work_experience', []):
            # Sig: Company + Title (normalized)
            comp = str(item.get('company_name', '')).strip().lower()
            title = str(item.get('job_title', '')).strip().lower()
            sig = (comp, title)
            
            # Deduplicate: If same position appears in lower priority source, skip it.
            # This favors the description/dates from Resume over LinkedIn
            if sig in seen and sig != ('', ''):
                continue
                
            seen.add(sig)
            all_items.append(item)
            
    # Sort by start_date descending (Recent first)
    # Assumes YYYY-MM format.
    all_items.sort(key=lambda x: str(x.get('start_date', '')), reverse=True)
    return all_items


def _merge_education(sources: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Aggregate education items."""
    all_items = []
    seen = set()
    
    for source_type in ['resume', 'linkedin', 'portfolio']:
        data = sources.get(source_type)
        if not data: continue
        
        for item in data.get('education', []):
            inst = str(item.get('institution', '')).strip().lower()
            deg = str(item.get('degree', '')).strip().lower()
            sig = (inst, deg)
            
            if sig in seen and sig != ('', ''):
                continue
            seen.add(sig)
            all_items.append(item)
            
    return all_items


def _merge_dynamic_sections(sources: Dict[str, Dict[str, Any]]) -> Dict[str, Any]:
    """Merge dynamic sections."""
    merged = {}
    
    # Priority: Resume -> LinkedIn -> Portfolio
    for source_type in ['resume', 'linkedin', 'portfolio']:
        data = sources.get(source_type)
        if not data: continue
        
        dynamic = data.get('dynamic_sections', {})
        for key, value in dynamic.items():
            if key not in merged:
                # New section, just add it
                merged[key] = value
            else:
                # Key collision logic
                # If both are lists, merge unique items
                if isinstance(merged[key], list) and isinstance(value, list):
                    current_set = set(str(x) for x in merged[key])
                    for v in value:
                        if str(v) not in current_set:
                            merged[key].append(v)
                
                # If not lists (e.g. strings), Resume (first processed) wins, so do nothing.
                
    return merged
