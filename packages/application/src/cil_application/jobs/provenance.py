"""Combine pure deadline policy with explicitly configured IO and presentation."""

from cil_contracts.jobs import CanonicalJobRecord
from cil_domain.jobs.freshness import FreshnessPolicy
from cil_application.ports import probe_job_url, render_job_hyperlink


class JobProvenanceVerifier(FreshnessPolicy):
    generate_clickable_hyperlink = staticmethod(render_job_hyperlink)
    verify_url_live = staticmethod(probe_job_url)

    @classmethod
    def verify_record(
        cls,
        record: CanonicalJobRecord,
        verify_live=False,
        reference_date=None,
        row_idx=2,
        target_url_col="O",
    ):
        valid = cls.validate_url_syntax(record.job_url)
        return {
            "url_valid": valid,
            "freshness": cls.compute_freshness(record.deadline, reference_date),
            "hyperlink_formula": cls.generate_clickable_hyperlink(
                target_url_col, row_idx
            ),
            "live_status": cls.verify_url_live(record.job_url)
            if verify_live and valid
            else None,
            "parsed_deadline": str(
                cls.parse_deadline(record.deadline) or record.deadline or ""
            ),
        }
