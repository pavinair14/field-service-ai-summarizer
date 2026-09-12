from datetime import datetime
from pydantic import BaseModel, Field


class FieldServiceReport(BaseModel):
    report_id: str = Field(..., description="Unique identifier for the report")
    asset: str = Field(..., description="Asset associated with the report")
    technician_id: str = Field(..., description="Identifier for the technician")
    arrived_at: datetime = Field(..., description="Timestamp when the technician arrived")
    departed_at: datetime = Field(..., description="Timestamp when the technician departed")
    stated_duration_hours: float = Field(..., description="Stated duration of the service in hours")
    parts_used: list[str] = Field(..., description="List of parts used during the service")
    resolution: str = Field(..., description="Description of the resolution provided")
    technician_notes: str = Field(default="", description="Additional notes from the technician")


class InvalidReport(BaseModel):
    """A record-level parsing failure that must not stop batch processing."""

    report_id: str = "unknown"
    asset: str = "Unknown asset"
    reason: str