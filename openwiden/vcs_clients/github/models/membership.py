from enum import Enum


class MembershipType(str, Enum):
    ADMIN = "admin"
    MEMBER = "member"
    NOT_A_MEMBER = "not_a_member"
