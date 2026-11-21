"""Pydantic v2 data models matching the FAIR JSON schemas."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field, field_validator

CelestialBody = Literal["lunar", "martian", "both", "unspecified"]
RegolithSimulant = Literal[
    "LHS-1",
    "LHS-1D",
    "LMS-1",
    "LMS-1D",
    "JSC-1A",
    "MGS-1",
    "MGS-1S",
    "MMS-1",
    "MMS-2",
    "exolith_unspecified",
    "other",
    "unspecified",
]
CropGuild = Literal[
    "leafy_green",
    "root",
    "legume",
    "fruiting",
    "grain",
    "herb",
    "fungi",
    "microgreen",
    "mixed",
    "other",
    "unspecified",
]
DataAvailability = Literal[
    "raw_table",
    "summary_means",
    "charts_only",
    "qualitative_only",
    "unknown",
]
BottleneckTag = Literal[
    "alkaline_ph",
    "compaction_crusting",
    "hydrophobicity_water_retention",
    "nutrient_deficiency",
    "heavy_metals_or_salinity",
    "microbial_contamination",
    "germination_failure",
    "light_or_temperature_stress",
    "root_restriction",
    "other",
]
AmendmentCategory = Literal[
    "none_control",
    "earth_soil_control",
    "organic_compost_manure",
    "vermicompost_aquaculture",
    "microbial_mycorrhizal",
    "hydrogel_alginate_polymer",
    "synthetic_fertilizer_hydroponic",
    "biochar_carbon",
    "nano_fertilizer_mineral",
    "plant_extract_waste",
    "light_spectrum_env",
    "coir_peat_perlite_substrate",
    "multi_amendment",
    "other",
]
OutcomeDirection = Literal["improved", "neutral", "reduced", "not_reported"]


class ManifestRecord(BaseModel):
    """Provenance and metadata entry for a scraped award/report."""

    report_id: str = Field(..., min_length=3)
    season: str
    season_slug: str
    season_order: int = Field(..., ge=1)
    year: int = Field(..., ge=2021)
    term: Literal["Spring", "Summer", "Fall"]
    track: Literal["main", "junior"]
    division: str = "Unspecified"
    award_tier: str
    award_category: str | None = None
    award_badges: list[str] = Field(default_factory=list)
    team_name: str = Field(..., min_length=1)
    project_title: str | None = None
    location_raw: str | None = None
    location_city: str | None = None
    location_state: str | None = None
    pdf_url: str | None = None
    thumbnail_url: str | None = None
    source_page_url: str
    has_pdf: bool = False
    local_pdf_path: str | None = None
    sha256: str | None = Field(default=None, pattern=r"^[a-f0-9]{64}$")
    byte_size: int | None = Field(default=None, ge=0)
    page_count: int | None = Field(default=None, ge=1)
    http_status: int | None = None
    fetched_at_utc: str | None = None


class TrialArm(BaseModel):
    """One experimental treatment or control arm extracted from a student report."""

    arm_id: str
    arm_label: str | None = None
    is_control: bool = False
    control_type: Literal["earth_soil", "unamended_regolith", "none"] | None = None
    regolith_pct: float | None = Field(default=None, ge=0.0, le=100.0)
    amendment_category: AmendmentCategory = "other"
    amendment_detail: str | None = None
    amendment_dose: str | None = None
    germination_rate_pct: float | None = Field(default=None, ge=0.0, le=100.0)
    survival_rate_pct: float | None = Field(default=None, ge=0.0, le=100.0)
    mean_shoot_height_cm: float | None = Field(default=None, ge=0.0)
    mean_root_length_cm: float | None = Field(default=None, ge=0.0)
    mean_fresh_biomass_g: float | None = Field(default=None, ge=0.0)
    mean_dry_biomass_g: float | None = Field(default=None, ge=0.0)
    substrate_ph: float | None = Field(default=None, ge=0.0, le=14.0)
    outcome_vs_regolith_control: OutcomeDirection = "not_reported"
    reported_effect_pct: float | None = None
    evidence_quote: str | None = None
    page_number: int | None = Field(default=None, ge=1)

    @field_validator("evidence_quote")
    @classmethod
    def _clean_quote(cls, v: str | None) -> str | None:
        if v is None:
            return None
        stripped = " ".join(v.split())
        return stripped[:600] if stripped else None


class ReportExtraction(BaseModel):
    """Structured scientific extraction for a single Plant the Moon PDF report."""

    report_id: str = Field(..., min_length=3)
    extraction_method: Literal["gemini_structured", "heuristic"]
    model_name: str | None = None
    celestial_body: CelestialBody = "unspecified"
    regolith_simulant: RegolithSimulant = "unspecified"
    regolith_simulant_raw: str | None = None
    crop_common_name: str = "unspecified"
    crop_scientific_name: str | None = None
    crop_guild: CropGuild = "unspecified"
    experimental_duration_days: float | None = Field(default=None, ge=0.0)
    total_plants_or_pots: int | None = Field(default=None, ge=1)
    replicates_per_treatment: int | None = Field(default=None, ge=1)
    has_earth_soil_control: bool = False
    has_unamended_regolith_control: bool = False
    statistical_tests_reported: list[str] = Field(default_factory=list)
    data_availability: DataAvailability = "unknown"
    primary_bottlenecks: list[BottleneckTag] = Field(default_factory=list)
    innovation_tags: list[str] = Field(default_factory=list)
    key_hypothesis: str | None = None
    summary_findings: str = ""
    arms: list[TrialArm] = Field(default_factory=list)
