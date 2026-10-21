"""Compatibility exports. Canonical implementations live in cil_* packages."""

from cil_contracts.facts import AnalysisEligibility as AnalysisEligibility
from cil_application.providers.capabilities import (
    BASELINE_API_CATALOG as BASELINE_API_CATALOG,
)
from cil_domain.companies.classification import CAPABILITY_AXES as CAPABILITY_AXES
from cil_contracts.jobs import CanonicalJobRecord as CanonicalJobRecord
from cil_domain.clusters.signature import ClusterSignature as ClusterSignature
from cil_contracts.facts import CompanyClassification as CompanyClassification
from cil_contracts.attributes import (
    DynamicAttributeDefinition as DynamicAttributeDefinition,
)
from cil_contracts.reports import DynamicColumnSpec as DynamicColumnSpec
from cil_domain.attributes.registry import (
    DynamicJobSchemaRegistry as DynamicJobSchemaRegistry,
)
from cil_reporting.schema.compiler import (
    DynamicReportSchemaCompiler as DynamicReportSchemaCompiler,
)
from collections.abc import Iterable as Iterable
from cil_integrations.providers.job_schema import JobSchemaContract as JobSchemaContract
from cil_contracts.attributes import KeyAlignmentError as KeyAlignmentError
from cil_domain.companies.classification import TAXONOMY_AXES as TAXONOMY_AXES
from cil_contracts.facts import TaxonomyFact as TaxonomyFact
from cil_domain.companies.classification import classify_company as classify_company
from cil_domain.companies.classification import (
    classify_taxonomy_axes as classify_taxonomy_axes,
)
from dataclasses import dataclass as dataclass
from cil_domain.companies.classification import (
    evaluate_analysis_eligibility as evaluate_analysis_eligibility,
)
from dataclasses import field as field
from cil_integrations.providers.job_records import from_cz_ares as from_cz_ares
from cil_integrations.providers.job_records import from_cz_mpsv as from_cz_mpsv
from cil_integrations.providers.job_records import (
    from_cz_mpsv_job_record as from_cz_mpsv_job_record,
)
from cil_integrations.providers.job_records import from_kr_opendart as from_kr_opendart
from cil_integrations.providers.job_records import (
    from_kr_public_job as from_kr_public_job,
)
from cil_integrations.providers.job_records import (
    from_kr_public_job_record as from_kr_public_job_record,
)
from cil_integrations.providers.job_records import from_kr_worknet as from_kr_worknet
from cil_integrations.providers.job_records import (
    from_sk_upsvar_record as from_sk_upsvar_record,
)
from cil_integrations.providers.job_records import (
    from_us_sec_or_usaspending as from_us_sec_or_usaspending,
)
from cil_integrations.providers.job_records import (
    from_us_usajobs_record as from_us_usajobs_record,
)
from cil_application.providers.capabilities import (
    get_cluster_baseline_spec_text as get_cluster_baseline_spec_text,
)
from cil_domain.companies.classification import (
    identity_eligibility as identity_eligibility,
)
from cil_domain.companies.classification import (
    legacy_company_type as legacy_company_type,
)
from cil_domain.companies.classification import public_sector_axes as public_sector_axes
from cil_application.providers.capabilities import (
    resolve_active_providers as resolve_active_providers,
)
