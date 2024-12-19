#!/usr/bin/env python3

# Portions of this file contributed by NIST are governed by the
# following statement:
#
# This software was developed at the National Institute of Standards
# and Technology by employees of the Federal Government in the course
# of their official duties. Pursuant to Title 17 Section 105 of the
# United States Code, this software is not subject to copyright
# protection within the United States. NIST assumes no responsibility
# whatsoever for its use by other parties, and makes no guarantees,
# expressed or implied, about its quality, reliability, or any other
# characteristic.
#
# We would appreciate acknowledgement if the software is used.

from typing import Union

# Define Python type for JSON-LD.  This is to help distinguish between
# general dictionaries and JSON-LD data.
# Note: This type is slightly more strict than a general JSON type.  In
# particular, float is intentionally not included, to prevent confusion
# in type conversions between JSON-LD and Python.
JSONLD = Union[
    None,
    bool,
    dict[str, "JSONLD"],
    int,
    list["JSONLD"],
    str,
]


def get_attribute(data: dict[str, JSONLD], property: str, default_value: JSONLD) -> JSONLD:
	"""
	This method gets the value of a property in the ``data`` object. Any JSON-LD type-variant aside from None is returned.  If the property is None, or not assigned in the ``data`` object, the thing passed as ``default_value`` is instead returned.

	>>> example0 = {"ex:foo": None}
	>>> get_attribute(example0, "ex:foo", "-")
	'-'
	>>> example1 = {"ex:foo": 0}
	>>> get_attribute(example1, "ex:foo", "-")
	0
	>>> example2 = {"ex:foo": False}
	>>> get_attribute(example2, "ex:foo", "-")
	False
	>>> example3 = {"ex:foo": [1, "a", None]}
	>>> get_attribute(example3, "ex:foo", "-")
	[1, 'a', None]
	>>> get_attribute(example3, "ex:bar", "-")
	'-'
	"""
	if property not in data:
		return default_value
	if data[property] is None:
		return default_value
	return data[property]


def get_optional_integer_attribute(data: dict[str, JSONLD], property: str, default_value: str) -> str:
	"""
	>>> example0 = {"ex:foo": 0}
	>>> get_optional_integer_attribute(example0, "ex:foo", "-")
	'0'
	>>> get_optional_integer_attribute(example0, "ex:bar", "-")
	'-'
	>>> example1 = {"ex:foo": 1}
	>>> get_optional_integer_attribute(example1, "ex:foo", "-")
	'1'
	>>> example2 = {"ex:foo": -1}
	>>> get_optional_integer_attribute(example2, "ex:foo", "-")
	'-1'
	>>> example3 = {"ex:foo": {"@type": "xsd:negativeInteger", "@value": "-1"}}
	>>> get_optional_integer_attribute(example3, "ex:foo", "-")
	'-1'
	>>> example4 = {"ex:foo": [1, 2, 3]}
	>>> get_optional_integer_attribute(example4, "ex:foo", "-")
	Traceback (most recent call last):
	...
	TypeError: Unexpected type for property 'ex:foo': <class 'list'>.
	"""
	return_value: JSONLD = get_attribute(data, property, default_value)
	if return_value is None:
		return default_value
	elif isinstance(return_value, dict):
		if "@value" not in return_value:
			raise ValueError("JSON object is not JSON-LD typed-literal dictionary: %r." % return_value)
		assert isinstance(return_value["@value"], str)
		if return_value["@value"][0] == "-":
			check_value = return_value["@value"][1:]
		else:
			check_value = return_value["@value"]
		if not check_value.isnumeric():
			raise ValueError("Typed-literal value is not numeric: %r." % return_value["@value"])
		return return_value["@value"]
	elif isinstance(return_value, int):
		return str(return_value)
	elif isinstance(return_value, str):
		return return_value
	raise TypeError("Unexpected type for property %r: %r." % (property, type(return_value)))


def get_optional_string_attribute(data: dict[str, JSONLD], property: str, default_value: str) -> str:
	return_value: JSONLD = get_attribute(data, property, default_value)
	if isinstance(return_value, str):
		return return_value
	raise TypeError("Unexpected type for property %r: %r." % (property, type(return_value)))
