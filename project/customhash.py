from django.contrib.auth.hashers import BasePasswordHasher
from collections import OrderedDict
class PlainTextPassword(BasePasswordHasher):
    algorithm = "plain"

    def salt(self):
        return ''

    def encode(self, password, salt):
        assert salt == ''
        return password

    def verify(self, password, encoded):
        return password == encoded

    def safe_summary(self, encoded):
        return OrderedDict([
            (('algorithm'), self.algorithm),
            (('hash'), encoded),
        ])