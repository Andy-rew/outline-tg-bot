from outline_vpn.outline_vpn import OutlineVPN

from code.config import IS_MOCK_OUTLINE, API_URL, CERT_SHA256
from code.mock_service import OutlineMockService

if IS_MOCK_OUTLINE:
    client = OutlineMockService()
else:
    client = OutlineVPN(api_url=API_URL, cert_sha256=CERT_SHA256)


def get_outline_client() -> OutlineVPN:
    """
    Get outline client
    :return: OutlineVPN client
    """
    return client
