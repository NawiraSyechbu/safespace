from pydantic import BaseModel, Field


class RegisterIn(BaseModel):
    username: str
    email: str
    password: str


class LoginIn(BaseModel):
    email: str
    password: str


class UsernameIn(BaseModel):
    username: str


class CommunityIn(BaseModel):
    name: str
    description: str | None = None


class PostIn(BaseModel):
    community_id: int
    title: str = Field(max_length=200)
    content: str = Field(max_length=5000)


class CommentIn(BaseModel):
    content: str = Field(max_length=2000)
    parent_comment_id: int | None = None


class ReportIn(BaseModel):
    content_type: str
    content_id: int
    reason: str = Field(max_length=1000)


class AppealIn(BaseModel):
    content_type: str
    content_id: int
    reason: str = Field(max_length=1000)


class ReviewIn(BaseModel):
    content_type: str
    content_id: int
    new_status: str
    notes: str | None = None


class ResolveReportIn(BaseModel):
    action: str  # "dismiss" atau "block"
    notes: str | None = None


class AppealDecisionIn(BaseModel):
    decision: str  # "accepted" atau "rejected"


class RoleIn(BaseModel):
    role: str
