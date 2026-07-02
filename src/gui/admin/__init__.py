from gui.admin.cars import AdminCarsMixin
from gui.admin.fees import AdminFeesMixin
from gui.admin.stats import AdminStatsMixin
from gui.admin.subscriptions import AdminSubscriptionsMixin
from gui.admin.tabs import AdminTabsMixin
from gui.admin.users import AdminUsersMixin


class AdminMixin(
    AdminCarsMixin,
    AdminFeesMixin,
    AdminSubscriptionsMixin,
    AdminUsersMixin,
    AdminStatsMixin,
    AdminTabsMixin,
):
    pass
