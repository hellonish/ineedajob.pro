"""
Engine Package - Unified Application Engine

Architecture:
- profile: Resume/LinkedIn/Portfolio Parsing & Unification.
- job: Job Intelligence (Context Engine).
- analysis: Gap Analysis & Scoring (Decision Engine).
- optimizer: Tailoring & Cover Letters (Action Engine).
- discrepancy: Validation.
"""

__all__ = []

# 1. Profile
try:
    from .profile import (
        parse_resume, parse_linkedin, parse_portfolio, 
        create_unified_profile, HybridResume
    )
    __all__.extend(['parse_resume', 'parse_linkedin', 'parse_portfolio', 'create_unified_profile', 'HybridResume'])
except ImportError:
    pass

# 2. Job 
try:
    from .job import scan_job, JobIntelligence
    __all__.extend(['scan_job', 'JobIntelligence'])
except ImportError:
    pass

# 3. Analysis
try:
    from .analysis import analyze_gaps, calculate_score, GapAnalysis, MatchScoreCard
    __all__.extend(['analyze_gaps', 'calculate_score', 'GapAnalysis', 'MatchScoreCard'])
except ImportError:
    pass

# 4. Optimizer
try:
    from .optimizer import create_optimization_plan, execute_plan, generate_cover_letter, OptimizationPlan
    __all__.extend(['create_optimization_plan', 'execute_plan', 'generate_cover_letter', 'OptimizationPlan'])
except ImportError:
    pass

# 5. Discrepancy
try:
    from .discrepancy import compare_profile_sources, format_for_table
    __all__.extend(['compare_profile_sources', 'format_for_table'])
except ImportError:
    pass

# 6. Models (Common)
try:
    from .models import get_deepseek_client
    __all__.extend(['get_deepseek_client'])
except ImportError:
    pass

