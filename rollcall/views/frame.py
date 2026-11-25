"""Data for the frame around every page."""

from dataclasses import dataclass


@dataclass(frozen=True)
class SignedInStaff:
    """The staff member shown in the header, with the address that signs them out."""

    name: str
    is_admin: bool
    sign_out_url: str
