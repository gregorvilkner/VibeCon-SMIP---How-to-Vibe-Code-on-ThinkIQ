"""SMIP_IO model package — project-specific business object classes.

This package is for the things the project is actually modeling on top of
SMIP — domain entities like `Reactor`, `Boiler`, `ProcessUnit`,
`SpectrometerSample`, etc. — not for the generic SMIP primitives
themselves (object, type, enumeration, attribute). Those primitives are
the substrate the internal methods in `smip_methods.py` already speak;
re-typing them here would add ceremony without insight.

A business class here typically:
  * pins itself to a SMIP type (by displayName or id) so callers don't
    have to repeat that knowledge,
  * declares the attribute slots it cares about and their expected
    dataType (STRING / ENUMERATION / ...),
  * uses the internal methods (`get_type_by_display_name`,
    `create_object`, `update_attribute`, ...) underneath to read or
    persist itself,
  * exposes `from_dict` / `from_object_id` constructors that turn a
    generic SMIP record into a typed instance.

Empty until a project gives it a domain to model. Re-export public
classes from this `__init__` so callers can do
`from SMIP_IO.model import <Class>`.
"""

__all__: list[str] = []
