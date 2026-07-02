from gui.user.debug import UserDebugMixin
from gui.user.display import UserDisplayMixin
from gui.user.entry import UserEntryMixin
from gui.user.exit import UserExitMixin
from gui.user.payment import UserPaymentMixin
from gui.user.qr_scanner import UserQRScannerMixin


class UserLogicMixin(
    UserEntryMixin,
    UserDebugMixin,
    UserQRScannerMixin,
    UserPaymentMixin,
    UserExitMixin,
    UserDisplayMixin,
):
    pass
