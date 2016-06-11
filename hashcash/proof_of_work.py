import hashlib
from sys import stderr
from collections import namedtuple

import unittest


class HashCash(object):
    def MINT(self, C):
        """
            Takes challenge(C) as the parameter
            Returns token(T), the solution to the challenge
        """
        raise NotImplementedError("Not implemented")

    def VALUE(self, T):
        """
            Takes token(T) as the parameter
            Returns value(V)
        """
        raise NotImplementedError("Not implemented")

    def CHAL(self, s, w):
        """
            Takes ?(s), amount-of-work(w) as parameter
            Returns challenge(C)
        """
        raise NotImplementedError("Not implemented")


Challenge = namedtuple("Challenge", ["number", "leading_zeroes"])
Token = namedtuple("Token", ["value", "leading_zeroes"])


bits = (1, 2, 4, 8, 16, 32, 64, 128)


def count_leading_zeroes(byte):
    leading_zeroes = 0
    for i in bits:
        if i & byte:
            break
        leading_zeroes += 1
    return leading_zeroes


class TestCountLeadingZeroes(unittest.TestCase):
    def test_count_leading_zeroes(self):
        self.assertEquals(count_leading_zeroes(0), 8)
        self.assertEquals(count_leading_zeroes(128), 7)
        self.assertEquals(count_leading_zeroes(64), 6)
        self.assertEquals(count_leading_zeroes(32), 5)
        self.assertEquals(count_leading_zeroes(16), 4)
        self.assertEquals(count_leading_zeroes(8), 3)
        self.assertEquals(count_leading_zeroes(4), 2)
        self.assertEquals(count_leading_zeroes(2), 1)
        self.assertEquals(count_leading_zeroes(1), 0)


class FakeHashCash(HashCash):
    def MINT(self, C):
        """
            Tries to find a hash that has n zeroes at left
        """
        i = 0
        while True:
            i += 1
            token_value = hashlib.sha256(str(C.number + i)).digest()
            token = Token(value=token_value, leading_zeroes=C.leading_zeroes)
            if self.VALUE(token):
                print "Mined token after %s tries" % i
                return token
            
    def VALUE(self, T):
        """
            Checks if token has n zeroes at left
        """

        total_leading_zeroes = 0 
        for byte in (ord(char) for char in T.value):
            leading_zeroes = count_leading_zeroes(byte)
            total_leading_zeroes += leading_zeroes
            if leading_zeroes < 8:
                break
        return total_leading_zeroes == T.leading_zeroes

    number = 0

    def CHAL(self, s, w):
        """
            w is the number of zeroes at left of the hash
        """
        # starts from one
        self.number += 1
        return Challenge(number=self.number, leading_zeroes=w)


class Server():
    def __init__(self, client):
        self.hashcash = FakeHashCash()
        self.client = client

    def run(self):
        C = self.hashcash.CHAL(None, 12)
        token = self.client.MINT(C)
        if self.hashcash.VALUE(token):
            print "The token client mined as %s is verified" % [format(ord(i), '08b') for i in token.value]
        else:
            print "Client is cheating!!!"

class Client():
    def __init__(self):
        self.hashcash = FakeHashCash()

    def MINT(self, C):
        return self.hashcash.MINT(C)

client = Client()
server = Server(client)
server.run()
