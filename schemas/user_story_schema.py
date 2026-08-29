"""Pydantic schemas for User Story generation and revision contracts."""

from typing import List, Optional
from pydantic import BaseModel, Field


class AcceptanceCriterion(BaseModel):

  scenario_title: str = Field(
      description="Actionable title for the BDD scenario"
  )
  given: List[str] = Field(
      default_factory=list, description="Preconditions and initial state"
  )
  when: List[str] = Field(
      default_factory=list, description="Triggering action or request"
  )
  then: List[str] = Field(
      default_factory=list,
      description="Expected outcomes, HTTP statuses, and payloads",
  )


class UserStoryPayload(BaseModel):

  story_id: str = Field(description="Unique story identifier")
  title: str = Field(description="Short descriptive title of the user story")
  priority: Optional[str] = Field(
      default="Medium", description="Priority level (High, Medium, Low)"
  )
  persona: str = Field(description="Target persona (As a...)")
  action: str = Field(description="Intended action (I want to...)")
  benefit: str = Field(description="Business benefit (So that...)")
  business_context: str = Field(description="Background and strategic alignment")
  acceptance_criteria: List[AcceptanceCriterion] = Field(
      default_factory=list, description="List of BDD scenarios"
  )
  technical_constraints: List[str] = Field(
      default_factory=list,
      description="Non-functional constraints and tech stack rules",
  )
  out_of_scope: List[str] = Field(
      default_factory=list,
      description="Explicitly excluded items to prevent scope creep",
  )
  design_ui_ux: Optional[str] = Field(
      default="N/A - Backend only",
      description="Design & UI/UX notes or links if applicable",
  )
  definition_of_done: List[str] = Field(
      default_factory=list, description="Checklist for story completion"
  )
  open_questions: List[str] = Field(
      default_factory=list,
      description="Questions for human reviewers to clarify",
  )
  assumptions_made: List[str] = Field(
      default_factory=list,
      description="Technical/business assumptions made by agent",
  )
  revision_changelog: Optional[str] = Field(
      default=None, description="Summary of adjustments during PR review"
  )
  rendered_markdown: str = Field(
      description="Complete GitHub-ready Markdown string"
  )
