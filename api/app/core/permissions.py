"""Role-based permission helpers."""

from app.db.models import MembershipRole

ROLE_RANK = {
    MembershipRole.crew: 1,
    MembershipRole.manager: 2,
    MembershipRole.owner: 3,
}


def role_at_least(role: MembershipRole, minimum: MembershipRole) -> bool:
    return ROLE_RANK[role] >= ROLE_RANK[minimum]


def can_manage_team(role: MembershipRole) -> bool:
    return role == MembershipRole.owner


def can_approve_and_publish(role: MembershipRole) -> bool:
    return role_at_least(role, MembershipRole.manager)


def can_create_jobs(role: MembershipRole) -> bool:
    return role_at_least(role, MembershipRole.crew)
