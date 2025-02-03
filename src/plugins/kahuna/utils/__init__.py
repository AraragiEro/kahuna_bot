import math

class KahunaException(Exception):
    def __init__(self, message):
        super(KahunaException, self).__init__(message)
        self.message = message

def roundup(x, base):
    return base * math.ceil(x / base)