"""Compatibility exports. Canonical implementations live in cil_* packages."""

from typing import Any as Any
from cil_application.analysis.service import (
    SERIES_SIGNATURE_FIELDS as SERIES_SIGNATURE_FIELDS,
)
from cil_application.analysis.service import _series_group_id as _series_group_id
from cil_application.analysis.service import _series_signature as _series_signature
from cil_domain.jobs.trends import aggregate_job_trends as aggregate_job_trends
from cil_application.analysis.service import (
    build_company_timeline as build_company_timeline,
)
from cil_domain.finance.analytics import (
    calculate_dynamic_wacc as calculate_dynamic_wacc,
)
from cil_application.analysis.service import (
    compare_revenue_and_hiring_trends as compare_revenue_and_hiring_trends,
)
from cil_domain.finance.analytics import dcf_scenarios as dcf_scenarios
from cil_domain.finance.analytics import (
    difference_in_differences as difference_in_differences,
)
from cil_domain.finance.analytics import (
    dynamic_macro_linked_dcf as dynamic_macro_linked_dcf,
)
from cil_application.analysis.service import (
    evaluate_ai_adoption_impact as evaluate_ai_adoption_impact,
)
from cil_application.analysis.service import evaluate_ai_event as evaluate_ai_event
from cil_application.analysis.service import evaluate_job_trends as evaluate_job_trends
from cil_application.analysis.service import (
    evaluate_valuation_scenarios as evaluate_valuation_scenarios,
)
from cil_domain.finance.analytics import event_study as event_study
from cil_application.analysis.service import job_event_boundary as job_event_boundary
from cil_application.analysis.service import job_trend_timeline as job_trend_timeline
from cil_domain.finance.analytics import (
    panel_difference_in_differences as panel_difference_in_differences,
)
from cil_domain.finance.analytics import pct_change as pct_change
from cil_application.analysis.service import (
    run_temporal_analytics_suite as run_temporal_analytics_suite,
)
from cil_domain.finance.analytics import safe_div as safe_div
from cil_application.analysis.service import (
    timeline_series_groups as timeline_series_groups,
)
from cil_application.analysis.service import (
    validate_series_signature as validate_series_signature,
)
from cil_domain.finance.analytics import (
    verify_parallel_trends as verify_parallel_trends,
)
