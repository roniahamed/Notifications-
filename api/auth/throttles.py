from rest_framework.throttling import SimpleRateThrottle

class OTPThrottle(SimpleRateThrottle):
    scope = "otp"
    rate = "5/hour"

    def get_cache_key(self, request, view):
        email = request.data.get("email")
        if email:
            ident = email
        else:
            ident = self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}


class LoginThrottle(SimpleRateThrottle):
    scope = "login"
    rate = "10/hour"

    def get_cache_key(self, request, view):
        email = request.data.get("email")
        if email:
            ident = email
        else:
            ident = self.get_ident(request)
        return self.cache_format % {"scope": self.scope, "ident": ident}
