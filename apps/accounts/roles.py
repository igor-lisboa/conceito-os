from apps.core.enums import LabeledEnum


class Role(LabeledEnum):
    OWNER = ("owner", "Owner / admin")
    ACCOUNT_MANAGER = ("account_manager", "Account manager")
    CREATIVE = ("creative", "Creative / collaborator")
    FREELANCER = ("freelancer", "Invited freelancer")
    CLIENT = ("client", "End client")
