from pydantic import BaseModel, Field, ValidationError, field_validator
from typing import List, Optional, Dict, Any

class GoogleAdsConfig(BaseModel):
    mcc_id: Optional[str] = None
    customer_id: str

    @field_validator("customer_id")
    @classmethod
    def customer_id_digits_only(cls, v: str) -> str:
        v2 = "".join(ch for ch in v if ch.isdigit())
        if not v2:
            raise ValueError("google_ads.customer_id must contain digits")
        return v2

class Targets(BaseModel):
    target_roas: Optional[float] = None
    target_cpa: Optional[float] = None

class ConversionSources(BaseModel):
    include: List[str] = Field(default_factory=list)
    exclude: List[str] = Field(default_factory=list)

class SpendCaps(BaseModel):
    daily: Optional[float] = None
    monthly: Optional[float] = None

class ProtectedEntities(BaseModel):
    brand_is_protected: bool = False
    entities: List[Dict[str, Any]] = Field(default_factory=list)

class Exclusions(BaseModel):
    campaign_types_ignore: List[str] = Field(default_factory=list)

class ClientConfig(BaseModel):
    client_name: str
    client_type: str
    primary_kpi: str

    google_ads: GoogleAdsConfig

    targets: Targets = Targets()
    conversion_sources: ConversionSources = ConversionSources()

    currency: str = "USD"
    timezone: str = "UTC"
    automation_mode: str = "insights"
    risk_tolerance: str = "conservative"

    spend_caps: SpendCaps = SpendCaps()
    protected_entities: ProtectedEntities = ProtectedEntities()
    exclusions: Exclusions = Exclusions()

def parse_client_config(data: dict) -> ClientConfig:
    # Raises ValidationError if invalid (used for config-gating)
    return ClientConfig.model_validate(data)
