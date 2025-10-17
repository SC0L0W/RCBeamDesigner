# nscp_beam_constants.py

# Standard bar sizes (mm diameter)
STANDARD_BAR_SIZES = [10, 12, 16, 20, 25, 28, 32, 36, 40]

# Cross-sectional areas of bars (mm²)
BAR_AREAS = {
    10: 79,
    12: 113,
    16: 201,
    20: 314,
    25: 491,
    28: 616,
    32: 804,
    36: 1020,
    40: 1257
}

# Unit weights
UNIT_WEIGHT_CONCRETE = 24    # kN/m³
UNIT_WEIGHT_REBAR = 78.5     # kN/m³

# Material strength values
F_C_VALUES = {
    'low': 21,
    'medium': 28,
    'high': 35
}

FY_VALUES = {
    'default': 275,
    'standard': 415,
    'high': 500
}

# Strength reduction factors (ϕ)
STRENGTH_REDUCTION_FACTORS = {
    'flexure': 0.90,
    'axial_flexure': 0.65,  # variable to 0.90 depending on strain
    'shear': 0.75,
    'torsion': 0.75,
    'compression_spiral': 0.75,
    'compression_tied': 0.65
}

# Reinforcement ratios
MIN_FLEXURAL_REINF_RATIO = 0.002
MAX_FLEXURAL_REINF_RATIO = 0.025
MAX_TENSION_REINF_RATIO = 0.75  # % of balanced steel

# Clear cover (mm)
CLEAR_COVER = {
    'beam': 40,
    'column': 40,
    'slab': 20,
    'footing': 50,
    'exterior': 50
}

# Common stirrup bar sizes
STIRRUP_BAR_SIZES = [10, 12, 16]

# Beta1 values based on f'c (per NSCP/ACI)
BETA1_BY_FC = {
    21: 0.85,
    28: 0.85,
    35: 0.80,
    42: 0.75,
    56: 0.65
}

# Max spacing for stirrups
MAX_STIRRUP_SPACING = {
    'shear': lambda d: min(0.5 * d, 600),   # d = effective depth (mm)
    'torsion': lambda d: min(0.5 * d, 300)
}

# Simplified development length factor (approximate)
DEVELOPMENT_LENGTH_FACTOR = 1.2  # To be used in: Ld ≈ 1.2 × db × fy / (1.3 * √fc)
