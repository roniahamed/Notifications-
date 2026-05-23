from rest_framework.throttling import AnonRateThrottle, UserRateThrottle


class OTPThrottle(AnonRateThrottle):
    rate = "5/hour"


class LoginThrottle(AnonRateThrottle):
    rate = "10/hour"
