MATERIAL_PROPERTIES = {
    'concrete': {
        'C20': {
            'grade': 'C20',
            'fc': 20.0,                       # MPa
            'unit_weight': 24.0,             # kN/m³
            'modulus_elasticity': 20000.0,   # MPa (approx. 4700√fc')
            'beta1': 0.85
        },
        'C25': {
            'grade': 'C25',
            'fc': 25.0,
            'unit_weight': 24.0,
            'modulus_elasticity': 23500.0,
            'beta1': 0.85
        },
        'C28': {
            'grade': 'C28',
            'fc': 28.0,
            'unit_weight': 24.0,
            'modulus_elasticity': 24800.0,
            'beta1': 0.85
        },
        'C30': {
            'grade': 'C30',
            'fc': 30.0,
            'unit_weight': 24.0,
            'modulus_elasticity': 25700.0,
            'beta1': 0.80
        },
        'C35': {
            'grade': 'C35',
            'fc': 35.0,
            'unit_weight': 24.0,
            'modulus_elasticity': 27800.0,
            'beta1': 0.80
        },
        'C40': {
            'grade': 'C40',
            'fc': 40.0,
            'unit_weight': 24.0,
            'modulus_elasticity': 29700.0,
            'beta1': 0.75
        },
        'C42': {
            'grade': 'C42',
            'fc': 42.0,
            'unit_weight': 24.0,
            'modulus_elasticity': 30400.0,
            'beta1': 0.75
        },
        'C56': {
            'grade': 'C56',
            'fc': 56.0,
            'unit_weight': 24.0,
            'modulus_elasticity': 35200.0,
            'beta1': 0.65
        }
    },

    'steel': {
        'Grade275': {
            'fy': 275.0,                     # MPa
            'fu': 410.0,                     # MPa
            'modulus_elasticity': 200000.0, # MPa
            'unit_weight': 78.5             # kN/m³
        },
        'Grade415': {
            'fy': 415.0,
            'fu': 550.0,
            'modulus_elasticity': 200000.0,
            'unit_weight': 78.5
        },
        'Grade500': {
            'fy': 500.0,
            'fu': 620.0,
            'modulus_elasticity': 200000.0,
            'unit_weight': 78.5
        }
    },

    'default_combinations': {
        'main_steel': 'Grade415',
        'stirrup_steel': 'Grade275',
        'concrete': 'C28'
    },

    'partial_safety_factors': {
        'phi_flexure': 0.90,
        'phi_shear': 0.75,
        'phi_torsion': 0.75,
        'phi_compression_tied': 0.65,
        'phi_compression_spiral': 0.75,
        'phi_axial_flexure_min': 0.65,
        'phi_axial_flexure_max': 0.90
    },

    'thermal': {
        'coefficient_thermal_expansion': {
            'concrete': 9.9e-6,  # per °C
            'steel': 12.0e-6     # per °C
        }
    },

    'others': {
        'poisson_ratio_concrete': 0.2,
        'poisson_ratio_steel': 0.3
    }
}
