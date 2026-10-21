"""Common report application boundary; all adapters use the same implementation."""

from cil_application.research.report_service import (
    run_research as generate_report,
    verify_sealed_bundle as verify_report_bundle,
)
