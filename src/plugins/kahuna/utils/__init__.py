import math

class KahunaException(Exception):
    def __init__(self, message):
        super(KahunaException, self).__init__(message)
        self.message = message

def roundup(x, base):
    return base * math.ceil(x / base)

def chunks(lst, n):
    """Yield successive n-sized chunks from lst."""
    for i in range(0, len(lst), n):
        yield lst[i:i + n]