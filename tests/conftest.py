"""Shared test settings: the Hypothesis profiles of the reference module (CMP-6.9).

``HYPOTHESIS_PROFILE`` selects ``gate`` (the default), ``ci`` or ``nightly``.
"""

from nogat_formulas import register_profiles

register_profiles()
