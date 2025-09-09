from __future__ import annotations

from typing import List, Literal, Optional
from pydantic import BaseModel, Field


EditOpType = Literal["write_file", "replace_text", "delete_file"]


class EditOperation(BaseModel):
    op: EditOpType = Field(..., description="Operation type")
    path: str = Field(..., description="Relative file path")
    content: Optional[str] = Field(None, description="File content for write_file")
    find: Optional[str] = Field(None, description="Substring to find for replace_text")
    replace: Optional[str] = Field(None, description="Replacement text for replace_text")


class EditPlan(BaseModel):
    description: str = Field("", description="High-level summary of the change")
    operations: List[EditOperation] = Field(default_factory=list)


