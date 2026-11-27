"""Data pieces every page uses: links, action buttons, messages and save conflicts."""

from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True)
class Link:
    label: str
    url: str


@dataclass(frozen=True)
class Action:
    """A button that does something. post: a form posting to url; otherwise a link."""

    label: str
    url: str
    post: bool = False
    kind: str = "primary"  # primary, secondary or quiet (see components/button.html)


@dataclass(frozen=True)
class Message:
    text: str
    kind: str = "success"  # success or error


@dataclass(frozen=True)
class Conflict:
    """Someone else saved the record while this form was open."""

    changed_by: str
    changed_at: datetime  # UTC
    reload_url: str  # the form again, with the newly saved values
