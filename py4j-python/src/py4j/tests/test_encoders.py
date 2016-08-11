from decimal import Decimal

from py4j import binary_protocol as bprotocol
from py4j import compat

import sys

VERSION_INFO = sys.version_info
IS_PYTHON_2 = VERSION_INFO[0] == 2
IS_PYTHON_3 = VERSION_INFO[0] == 3


def test_none_encoder():
    encoder = bprotocol.NoneEncoder()

    value = None
    encoded = encoder.encode(value, type(value))
    assert encoded.type == bprotocol.NULL_TYPE
    assert encoded.size is None
    assert encoded.value is None


def test_int_encoder():
    encoder = bprotocol.IntEncoder()
    value = "Hello"

    assert encoder.encode(value, type(value)) == bprotocol.CANNOT_ENCODE

    value = 1
    encoded = encoder.encode(value, type(value))

    assert encoded.type == bprotocol.INTEGER_TYPE
    assert encoded.size is None
    assert len(encoded.value) == 4

    value = -3000000000000
    encoded = encoder.encode_specific(value, type(value))
    assert encoded.type == bprotocol.LONG_TYPE
    assert encoded.size is None
    assert len(encoded.value) == 8


def test_decimal_encoder():
    encoder = bprotocol.DecimalEncoder()
    value = Decimal("34.56")
    value_str = compat.unicode("34.56").encode("utf-8")

    encoded = encoder.encode(value, type(value))
    assert encoded.type == bprotocol.DECIMAL_TYPE
    assert encoded.size == len(value_str)
    assert len(encoded.value) == len(value_str)


def test_bool_encoder():
    encoder = bprotocol.BoolEncoder()

    value = True
    encoded = encoder.encode(value, type(value))
    assert encoded.type == bprotocol.BOOLEAN_TRUE_TYPE
    assert encoded.size is None
    assert encoded.value is None

    value = False
    encoded = encoder.encode(value, type(value))
    assert encoded.type == bprotocol.BOOLEAN_FALSE_TYPE
    assert encoded.size is None
    assert encoded.value is None


def test_double_encoder():
    encoder = bprotocol.DoubleEncoder()

    def assert_float(value):
        encoded = encoder.encode(value, type(value))
        assert encoded.type == bprotocol.DOUBLE_TYPE
        assert encoded.size is None
        assert len(encoded.value) == 8

    assert_float(2.3)
    assert_float(float("nan"))
    assert_float(float("+inf"))
    assert_float(float("-inf"))


def test_bytes_encoder():
    encoder = bprotocol.BytesEncoder()

    def assert_bytes(value):
        encoded = encoder.encode(value, type(value))
        assert encoded.type == bprotocol.BYTES_TYPE
        assert encoded.size == len(value)
        assert len(encoded.value) == len(value)

    assert_bytes(bytearray([1, 2, 3]))

    value_bytestr = compat.tobytestr("hello")
    if IS_PYTHON_3:
        assert_bytes(value_bytestr)
    else:
        assert encoder.encode(value_bytestr, type(value_bytestr)) ==\
            bprotocol.CANNOT_ENCODE


def test_string_encoder():
    encoder = bprotocol.StringEncoder()

    def assert_string(value):
        bin_string = bprotocol.get_encoded_string(value, "utf-8")
        encoded = encoder.encode(value, type(value))
        assert encoded.type == bprotocol.STRING_TYPE
        assert encoded.size == len(bin_string)
        assert len(encoded.value) == len(bin_string)

    assert_string(compat.unicode("testing\ntesting"))

    value_bytestr = compat.tobytestr("testing\ntesting")
    if IS_PYTHON_2:
        assert_string(value_bytestr)
    else:
        assert encoder.encode(value_bytestr, type(value_bytestr)) ==\
            bprotocol.CANNOT_ENCODE