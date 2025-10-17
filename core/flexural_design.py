import json
import math
import os
from typing import Dict, List, Tuple

class FlexuralDesigner:

    # <editor-fold desc="INITIALIZATION & DATA MANAGEMENT">
    def __init__(self, beam_data_file: str = None):
        self.beam_data = None
        self.design_results = {}
        self.Es = 200000
        self.max_steel_ratio = 0.025
        self.max_aggregate_size = 25
        self.standard_bar_sizes = [10, 12, 16, 20, 25, 28, 32, 36, 40]
        self.frame_type = 'ordinary'
        self.reinforcement_parameters = {}

        default_filename = os.path.join('..', 'raw_data', 'beam_data.json')
        filename_to_load = beam_data_file or default_filename

        if os.path.exists(filename_to_load):
            self.load_beam_data(filename_to_load)
        else:
            self.beam_data = None

        if self.beam_data:
            self._set_parameters_from_json()
    def load_beam_data(self, filename: str) -> None:
        try:
            with open(filename, 'r') as f:
                self.beam_data = json.load(f)
        except (FileNotFoundError, json.JSONDecodeError):
            self.beam_data = None
    def _set_parameters_from_json(self) -> None:
        """
        Set design parameters from beam data JSON structure.
        Extracts material properties and reinforcement parameters.
        """
        if not self.beam_data:
            print("Warning: No beam data available for parameter extraction")
            return

        # Extract material properties
        if 'material_properties' in self.beam_data:
            material_props = self.beam_data['material_properties']

            # Extract frame type with validation
            frame_type = material_props.get('frame_type', 'ordinary')
            valid_frame_types = ['ordinary', 'special', 'intermediate']
            if isinstance(frame_type, str) and frame_type.lower() in valid_frame_types:
                self.frame_type = frame_type.lower()
            else:
                print(f"Warning: Invalid or missing frame type '{frame_type}'. Using 'ordinary' as default.")
                self.frame_type = 'ordinary'

            # Extract max aggregate size
            if 'max_aggregate_size' in material_props:
                self.max_aggregate_size = material_props['max_aggregate_size']

            # Extract other material properties if available
            if 'concrete_cover' in material_props:
                self.concrete_cover = material_props['concrete_cover']

            if 'main_steel_rebar_fy' in material_props:
                self.main_steel_fy = material_props['main_steel_rebar_fy']

            if 'shear_steel_fy' in material_props:
                self.shear_steel_fy = material_props['shear_steel_fy']

            if 'reduction_factor_shear' in material_props:
                self.phi_shear = material_props['reduction_factor_shear']

        if 'design_settings' in self.beam_data:
            design_set = self.beam_data['material_properties']
            frame_type = design_set.get('frame_type', 'ordinary')

        # Initialize reinforcement_parameters if not already set
        self.reinforcement_parameters = getattr(self, 'reinforcement_parameters', {})
        # Or explicitly set to empty dict if attribute might not exist
        if not hasattr(self, 'reinforcement_parameters'):
            self.reinforcement_parameters = {}

        # Extract reinforcement parameters
        if 'reinforcement_parameters' in self.beam_data:
            self.reinforcement_parameters = self.beam_data['reinforcement_parameters']

            # Filter bar sizes based on main_bar_range
            reinf_params = self.reinforcement_parameters

            if 'main_bar_range' in reinf_params:
                min_bar, max_bar = reinf_params['main_bar_range']

                # Filter standard bar sizes
                original_bars = self.standard_bar_sizes.copy()
                self.standard_bar_sizes = [
                    bar for bar in self.standard_bar_sizes
                    if min_bar <= bar <= max_bar
                ]

                # Fallback if no bars in range
                if not self.standard_bar_sizes:
                    print(f"Warning: No standard bars in range [{min_bar}, {max_bar}]. Using default bars.")
                    self.standard_bar_sizes = [10, 12, 16, 20, 25, 28, 32, 36, 40]
                else:
                    print(f"Filtered bar sizes: {self.standard_bar_sizes} (from range [{min_bar}, {max_bar}])")

            # Extract stirrup bar range if available
            if 'stirrup_bar_range' in reinf_params:
                self.stirrup_bar_range = reinf_params['stirrup_bar_range']

            # Extract spacing parameters
            if 'min_spacing' in reinf_params:
                self.min_spacing = reinf_params['min_spacing']

            if 'max_spacing' in reinf_params:
                self.max_spacing = reinf_params['max_spacing']
    def validate_beam_data_structure(self, beam_data: Dict) -> bool:
        try:
            required_keys = ['dimensions', 'forces']
            for key in required_keys:
                if key not in beam_data:
                    return False
            dims = beam_data['dimensions']
            if 'base' not in dims or 'height' not in dims:
                return False
            for section in ['left', 'mid', 'right']:
                if section not in beam_data['forces']:
                    return False
                for moment in ['max_moment_top', 'max_moment_bottom']:
                    if moment not in beam_data['forces'][section]:
                        return False
            return True
        except:
            return False
    def get_bars_in_range(self, bar_range: Tuple[int, int]) -> List[int]:
        """Return list of standard bar sizes within the specified range."""
        min_bar, max_bar = bar_range
        return [bar for bar in self.standard_bar_sizes if min_bar <= bar <= max_bar]
    def select_most_efficient_bar(self, bars: List[int]) -> int:
        """Select the smallest bar diameter in the list (most efficient)."""
        return min(bars) if bars else None
    # </editor-fold>
    # <editor-fold desc="MATERIAL PROPERTIES & BASIC CALCULATIONS">
    def extract_concrete_strength(self, concrete_grade: str) -> float:
        if isinstance(concrete_grade, str):
            grade_str = concrete_grade.strip().upper().replace('C', '')
            try:
                return float(grade_str)
            except ValueError:
                return 28.0
        else:
            return 28.0
    def calculate_beta(self, fc_prime: float) -> float:
        if fc_prime <= 28:
            return 0.85
        elif fc_prime <= 55:
            return max(0.65, 0.85 - 0.05 * (fc_prime - 28) / 7)
        else:
            return 0.65
    def calculate_balanced_steel_ratio(self, fc_prime: float, fy: float) -> float:
        return (0.85 * fc_prime / fy) * (600 / (600 + fy))
    def calculate_min_steel_ratio(self, fc_prime: float, fy: float, b: float, d: float) -> float:
        rho_min1 = 0.25 * math.sqrt(fc_prime) / fy
        rho_min2 = 1.4 / fy
        return max(rho_min1, rho_min2)
    def calculate_max_steel_ratio(self, rho_bal: float) -> float:
        return min(0.75 * rho_bal, self.max_steel_ratio)
    def calculate_steel_ratio_limit_state(self, Mu: float, phi: float, b: float, d: float, fc_prime: float,
                                          fy: float) -> float:
        """
        Calculate steel ratio (rho) based on limit state principles.
        """
        m = fy / (0.85 * fc_prime)
        Rn = Mu / (phi * b * d ** 2)

        argument = 1 - (2 * m * Rn) / fy
        if argument < 0:
            argument = 0  # To prevent math domain error; over-reinforced scenario

        rho = (1 / m) * (1 - math.sqrt(argument))
        # Clamp rho within min and max ratios
        rho_min = self.calculate_min_steel_ratio(fc_prime, fy, b, d)
        rho_max = self.calculate_max_steel_ratio(rho)  # assuming you pass rho_bal or define appropriately

        rho = max(rho, rho_min)
        rho = min(rho, rho_max)
        return rho
    def calculate_effective_depth(self, height: float, cover: float, stirrup_dia: float, main_bar_dia: float) -> float:
        """Calculate effective depth considering second bar layer (~25 mm gap)."""
        d1 = height - cover - stirrup_dia - main_bar_dia / 2
        d2 = d1 - self.max_aggregate_size / 2
        return max(d2, d1, 25)
    def calculate_neutral_axis_depth(self, rho: float, fc_prime: float, fy: float, d: float) -> float:
        """
        Calculate the neutral axis depth for a given steel ratio.

        Args:
            rho (float): Steel ratio
            fc_prime (float): Concrete compressive strength
            fy (float): Yield strength of reinforcement
            d (float): Effective depth of the beam section

        Returns:
            float: Depth of the neutral axis (c)
        """
        beta = self.calculate_beta(fc_prime)
        a = (rho * fy * d) / (0.85 * fc_prime)
        return a / beta
    def calc_strain_in_steel(self, d, c):
        # Assuming maximum strain at outer tension steel
        epsilon_cu = 0.003
        epsilon_s = epsilon_cu * (d - c) / c
        return epsilon_s

    # </editor-fold>
    # <editor-fold desc="REINFORCEMENT CALCULATIONS">
    def calculate_minimum_area_for_bars(self, bar_range: Tuple[int, int], min_bars: int = 2) -> float:
        bar_min, bar_max = bar_range
        available_bars = [dia for dia in self.standard_bar_sizes if bar_min <= dia <= bar_max]
        if not available_bars:
            available_bars = [min(self.standard_bar_sizes, key=lambda x: abs(x - bar_min))]
        min_bar_dia = min(available_bars)
        min_bar_area = math.pi * (min_bar_dia / 2) ** 2
        return min_bars * min_bar_area
    def calculate_bar_combinations(self, As_required: float, bar_range: Tuple[int, int], min_bars: int = 2) -> List[Dict]:
        available_bars = [dia for dia in self.standard_bar_sizes if bar_range[0] <= dia <= bar_range[1]]
        if not available_bars:
            available_bars = [min(self.standard_bar_sizes, key=lambda x: abs(x - bar_range[0]))]
        combinations = []
        for bar_dia in available_bars:
            bar_area = math.pi * (bar_dia / 2) ** 2
            num_bars_for_area = max(min_bars, math.ceil(As_required / bar_area))
            for num_bars in range(num_bars_for_area, min(num_bars_for_area + 3, 20)):
                actual_area = num_bars * bar_area
                if actual_area >= As_required:
                    excess_percentage = ((actual_area - As_required) / As_required) * 100
                    if num_bars > 12 or excess_percentage > 50:
                        continue
                    combo = {
                        'bar_diameter': bar_dia,
                        'bar_area': bar_area,
                        'num_bars': num_bars,
                        'total_area': actual_area,
                        'area_ratio': actual_area / As_required,
                        'excess_percentage': excess_percentage,
                        'meets_min_bars': num_bars >= min_bars,
                        'efficiency_score': self.calculate_efficiency_score(excess_percentage, num_bars)
                    }
                    combinations.append(combo)
        combinations.sort(key=lambda x: x['efficiency_score'], reverse=True)
        return combinations
    def calculate_efficiency_score(self, excess_percentage: float, num_bars: int) -> float:

        # Penalty for excess steel area (more excess means lower score)
        excess_penalty = excess_percentage / 2  # Adjust weight as needed

        # Penalty based on deviation from optimal number of bars (e.g., 4)
        optimal_bars = 4
        bar_penalty = abs(num_bars - optimal_bars)

        # Compute score, ensuring it stays within 0-100
        raw_score = 100 - excess_penalty - bar_penalty

        # Clamp the score between 0 and 100
        score = max(0, min(100, raw_score))

        return score
    # </editor-fold>
    # <editor-fold desc="Design Main Methods">
    def calculate_required_steel_area(self, Mu: float, phi: float, b: float, d: float, fc_prime: float, fy: float,
                                      bar_range: Tuple[int, int]) -> Tuple[float, bool, Dict]:
        """
        Calculate required steel area based on limit state rho, selecting the most efficient bar diameter.
        Returns: (As_required, is_doubly_reinforced, design_details)
        """

        # Step 1: Calculate rho via limit state approach
        rho_limit_state = self.calculate_steel_ratio_limit_state(Mu, phi, b, d, fc_prime, fy)

        # Calculate required steel area using proper formula
        As_required = rho_limit_state * b * d

        # Get candidate bar sizes within range
        candidate_bars = self.get_bars_in_range(bar_range)
        if not candidate_bars:
            # fallback to default if none
            candidate_bars = self.standard_bar_sizes

        # Initialize
        is_doubly_reinforced = False
        design_details = {}

        # Minimum number of bars
        min_bars = 2

        # Evaluate each candidate bar size
        best_candidate = None
        min_excess = float('inf')

        for bar_dia in candidate_bars:
            bar_area = math.pi * (bar_dia / 2) ** 2

            # Calculate minimum number of bars needed for this bar size
            min_bars_needed = max(min_bars, math.ceil(As_required / bar_area))
            total_area_candidate = min_bars_needed * bar_area

            # Capacity check
            capacity_check = self.verify_capacity(total_area_candidate, phi, b, d, fc_prime, fy, Mu)

            if capacity_check['passes']:
                excess = total_area_candidate - As_required
                if excess < min_excess:
                    min_excess = excess
                    best_candidate = {
                        'bar_diameter': bar_dia,
                        'num_bars': min_bars_needed,
                        'total_area': total_area_candidate,
                        'excess_percentage': (excess / As_required) * 100 if As_required > 0 else 0,
                        'capacity_check': capacity_check
                    }

        if best_candidate:
            As_required_final = best_candidate['total_area']
            is_doubly_reinforced = False
            design_details = {
                'bar_diameter': best_candidate['bar_diameter'],
                'num_bars': best_candidate['num_bars'],
                'excess_percentage': best_candidate['excess_percentage'],
                'theoretical_as_required': As_required
            }
            return As_required_final, is_doubly_reinforced, design_details
        else:
            # If no candidate passes, check if doubly reinforced is needed
            # This would require additional logic for compression reinforcement
            is_doubly_reinforced = True

            # For now, return the theoretical requirement with smallest available bar
            smallest_bar = min(candidate_bars) if candidate_bars else min(self.standard_bar_sizes)
            bar_area = math.pi * (smallest_bar / 2) ** 2
            num_bars = max(min_bars, math.ceil(As_required / bar_area))

            design_details = {
                'note': 'Section may require doubly reinforced design or larger dimensions',
                'bar_diameter': smallest_bar,
                'num_bars': num_bars,
                'theoretical_as_required': As_required,
                'total_area': num_bars * bar_area
            }

            return As_required, is_doubly_reinforced, design_details
    def design_doubly_reinforced_enhanced(
            self,
            Mu: float,
            phi: float,
            b: float,
            d: float,
            fc_prime: float,
            fy: float,
            rho_max: float,
            rho_min: float,
            bar_range: Tuple[int, int],
            cover: float,
            stirrup_dia: float
    ) -> Tuple[float, bool, Dict]:
        """Enhanced doubly reinforced design with comprehensive verification using passed values only"""

        # Initial calculations
        As1 = rho_max * b * d
        beta = self.calculate_beta(fc_prime)
        a1 = (As1 * fy) / (0.85 * fc_prime * b)
        c1 = a1 / beta
        Mn1 = As1 * fy * (d - a1 / 2)
        Mn_total = Mu / phi
        Mn2 = Mn_total - Mn1

        if Mn2 <= 0:
            # Single reinforcement sufficient
            verification_results = self.comprehensive_verification_system(
                As1, Mu, phi, b, d, fc_prime, fy, rho_max,
                self.calculate_balanced_steel_ratio(fc_prime, fy)
            )

            design_recommendations = self.final_design_recommendation_engine(
                As1, b, d, bar_range, verification_results
            )

            return As1, False, {
                'type': 'singly_reinforced',
                'As_required': As1,
                'verification_results': verification_results,
                'design_recommendations': design_recommendations,
                'note': 'Initially calculated as doubly reinforced but singly reinforced is sufficient'
            }

        # Compression steel calculations using passed cover and stirrup_dia
        d_prime = cover + stirrup_dia + bar_range[0] / 2

        # Enhanced compression steel verification
        compression_steel_verification = self.verify_compression_steel(c1, d_prime, fc_prime, fy)

        fs_prime = compression_steel_verification['fs_prime']
        As_prime_required = Mn2 / (fs_prime * (d - d_prime))
        As2 = (As_prime_required * fs_prime) / fy
        As_total = As1 + As2

        # Minimum compression steel
        As_min_bars_comp = self.calculate_minimum_area_for_bars(bar_range, min_bars=2)
        As_prime_actual = max(As_prime_required, As_min_bars_comp)

        if As_prime_actual > As_prime_required:
            As2_adjusted = (As_prime_actual * fs_prime) / fy
            As_total = As1 + As2_adjusted

        # Comprehensive verification for doubly reinforced design
        verification_results = self.comprehensive_verification_doubly_reinforced(
            As1, As_prime_actual, Mu, phi, b, d, d_prime, fc_prime, fy, compression_steel_verification
        )

        # Separate recommendations for tension and compression
        tension_recommendations = self.final_design_recommendation_engine(
            As_total, b, d, bar_range, verification_results
        )

        compression_recommendations = self.final_design_recommendation_engine(
            As_prime_actual, b, d, bar_range, verification_results
        )

        return As_total, True, {
            'type': 'doubly_reinforced',
            'As1': As1,
            'As2': As2,
            'As_total': As_total,
            'As_prime_required': As_prime_required,
            'As_prime_actual': As_prime_actual,
            'As_min_bars_comp': As_min_bars_comp,
            'Mn1': Mn1,
            'Mn2': Mn2,
            'Mn_total': Mn_total,
            'fs_prime': fs_prime,
            'd_prime': d_prime,
            'c1': c1,
            'a1': a1,
            'beta': beta,
            'compression_steel_verification': compression_steel_verification,
            'verification_results': verification_results,
            'tension_recommendations': tension_recommendations,
            'compression_recommendations': compression_recommendations
        }

    # </editor-fold>
    # <editor-fold desc="SPACING & ARRANGEMENT VERIFICATION">
    def check_bar_spacing(self, b: float, cover: float, stirrup_dia: float, bar_dia: float,
                          num_bars: int, layers: int = 1) -> Dict:


        # ACI 318 minimum spacing requirement - prioritized as requested
        min_spacing_req = max(25, bar_dia, (4 / 3) * self.max_aggregate_size)

        # Calculate available width for reinforcement
        available_width = b - 2 * cover - 2 * stirrup_dia

        # Check if beam width is sufficient
        if available_width <= 0:
            return {
                'spacing_ok': False,
                'error': 'Insufficient width for reinforcement',
                'recommendation': 'INCREASE_BEAM_WIDTH',
                'available_width': available_width,
                'min_spacing_required': min_spacing_req
            }

        if layers == 1:
            # Single layer analysis
            if num_bars == 1:
                spacing_ok = bar_dia <= available_width
                actual_spacing = available_width
            else:
                total_bar_width = num_bars * bar_dia
                if total_bar_width > available_width:
                    spacing_ok = False
                    actual_spacing = 0
                else:
                    remaining_space = available_width - total_bar_width
                    num_gaps = num_bars - 1
                    actual_spacing = remaining_space / num_gaps if num_gaps > 0 else 0
                    spacing_ok = actual_spacing >= min_spacing_req

            # Calculate maximum bars that can fit in single layer
            max_bars_single = int((available_width + min_spacing_req) / (bar_dia + min_spacing_req))

            result = {
                'spacing_ok': spacing_ok,
                'actual_spacing': actual_spacing,
                'min_spacing_required': min_spacing_req,
                'available_width': available_width,
                'max_bars_single_layer': max_bars_single,
                'requires_multiple_layers': num_bars > max_bars_single,
                'layers_required': 1 if num_bars <= max_bars_single else math.ceil(num_bars / max_bars_single),
                'recommendation': 'OK' if spacing_ok else 'USE_MULTIPLE_LAYERS'
            }

            # Check two-layer solution if single layer fails
            if not spacing_ok and num_bars > 1:
                two_layer_result = self.check_bar_spacing(b, cover, stirrup_dia, bar_dia, num_bars, 2)
                if two_layer_result['spacing_ok']:
                    result.update({
                        'recommendation': 'USE_2_LAYERS',
                        'two_layer_solution': two_layer_result
                    })
        else:
            # Multi-layer analysis
            bars_per_layer = math.ceil(num_bars / layers)

            if bars_per_layer == 1:
                spacing_ok = bar_dia <= available_width
                actual_spacing = available_width
            else:
                total_bar_width_per_layer = bars_per_layer * bar_dia
                if total_bar_width_per_layer > available_width:
                    spacing_ok = False
                    actual_spacing = 0
                else:
                    remaining_space_per_layer = available_width - total_bar_width_per_layer
                    num_gaps_per_layer = bars_per_layer - 1
                    actual_spacing = remaining_space_per_layer / num_gaps_per_layer if num_gaps_per_layer > 0 else 0
                    spacing_ok = actual_spacing >= min_spacing_req

            # Calculate maximum bars per layer
            max_bars_per_layer = int((available_width + min_spacing_req) / (bar_dia + min_spacing_req))

            result = {
                'spacing_ok': spacing_ok,
                'actual_spacing': actual_spacing,
                'min_spacing_required': min_spacing_req,
                'available_width': available_width,
                'bars_per_layer': bars_per_layer,
                'max_bars_per_layer': max_bars_per_layer,
                'layers_used': layers,
                'total_bars_distributed': bars_per_layer * layers,
                'recommendation': 'OK' if spacing_ok else 'INCREASE_LAYERS_OR_REDUCE_BARS'
            }

        return result

    def check_spacing_and_adjust_bars(self, section_result: Dict, b: float, cover: float,
                                      stirrup_dia: float, bar_range: Tuple[int, int]) -> Dict:

        if 'recommended_bars' not in section_result or not section_result['recommended_bars']:
            return section_result

        recommended = section_result['recommended_bars']
        bar_dia = recommended['bar_diameter']
        num_bars = recommended['num_bars']

        # Perform initial spacing check
        spacing_check = self.check_bar_spacing(b, cover, stirrup_dia, bar_dia, num_bars, layers=1)

        # Initialize final arrangement dict
        final_arrangement = {
            'layers': 1,
            'bars_per_layer': [num_bars],
            'bar_diameter': bar_dia,
            'spacing_ok': spacing_check['spacing_ok'],
            'actual_spacing': spacing_check['actual_spacing'],
            'arrangement_type': 'single_layer_equal_spacing'
        }

        if spacing_check['spacing_ok']:
            # Single layer solution works
            section_result['spacing_analysis'] = spacing_check
            section_result['final_arrangement'] = final_arrangement
        else:
            # Handle multi-layer or failed spacing scenarios
            if 'two_layer_solution' in spacing_check and spacing_check['two_layer_solution']['spacing_ok']:
                # Two-layer solution is viable
                two_layer = spacing_check['two_layer_solution']
                bars_in_layer = two_layer['bars_per_layer']
                layer_1_bars = bars_in_layer
                layer_2_bars = num_bars - bars_in_layer

                section_result['spacing_analysis'] = two_layer
                section_result['final_arrangement'] = {
                    'layers': 2,
                    'bars_per_layer': [layer_1_bars, layer_2_bars],
                    'bar_diameter': bar_dia,
                    'spacing_ok': True,
                    'actual_spacing': two_layer['actual_spacing'],
                    'arrangement_type': 'two_layer_equal_spacing'
                }
            else:
                # Multi-layer solution required
                required_layers = spacing_check['layers_required']
                spacing_check_multi = self.check_bar_spacing(b, cover, stirrup_dia, bar_dia, num_bars,
                                                             layers=required_layers)

                if spacing_check_multi['spacing_ok']:
                    # Distribute bars across layers
                    layer_distribution = []
                    remaining_bars = num_bars
                    bars_per_layer = spacing_check_multi['bars_per_layer']

                    for _ in range(required_layers):
                        bars_in_layer = min(bars_per_layer, remaining_bars)
                        layer_distribution.append(bars_in_layer)
                        remaining_bars -= bars_in_layer

                    section_result['spacing_analysis'] = spacing_check_multi
                    section_result['final_arrangement'] = {
                        'layers': required_layers,
                        'bars_per_layer': layer_distribution,
                        'bar_diameter': bar_dia,
                        'spacing_ok': True,
                        'actual_spacing': spacing_check_multi['actual_spacing'],
                        'arrangement_type': 'multi_layer_equal_spacing'
                    }
                else:
                    # Final fallback: spacing not achievable
                    section_result['spacing_analysis'] = spacing_check
                    section_result['final_arrangement'] = {
                        'layers': 1,
                        'bars_per_layer': [num_bars],
                        'bar_diameter': bar_dia,
                        'spacing_ok': False,
                        'needs_doubly_reinforced': True,
                        'arrangement_type': 'failed_spacing_check',
                        'recommendations': [
                            'INCREASE_BEAM_WIDTH',
                            'REDUCE_BAR_DIAMETER',
                            'CONSIDER_DOUBLY_REINFORCED_DESIGN'
                        ]
                    }

        return section_result

    def check_single_layer_feasibility(self, combo: Dict, b: float) -> bool:

        bar_diameter = combo['bar_size']
        num_bars = combo['num_bars']

        # Use prioritized spacing requirement
        min_spacing = max(25, bar_diameter, (4 / 3) * self.max_aggregate_size)
        min_cover = 40  # Standard cover assumption

        required_width = num_bars * bar_diameter + (num_bars - 1) * min_spacing + 2 * min_cover
        return required_width <= b

    def calculate_required_layers(self, combo: Dict, b: float) -> int:

        if self.check_single_layer_feasibility(combo, b):
            return 1

        bar_diameter = combo['bar_size']
        num_bars = combo['num_bars']
        min_spacing = max(25, bar_diameter, (4 / 3) * self.max_aggregate_size)
        min_cover = 40

        # Calculate available width for bars
        available_width = b - 2 * min_cover

        # Calculate maximum bars that can fit in one layer
        max_bars_per_layer = int((available_width + min_spacing) / (bar_diameter + min_spacing))
        max_bars_per_layer = max(1, max_bars_per_layer)  # Ensure at least 1 bar per layer

        # Calculate required layers
        required_layers = math.ceil(num_bars / max_bars_per_layer)

        # Practical limit check
        max_practical_layers = 4
        if required_layers > max_practical_layers:
            raise ValueError(f"Too many layers required ({required_layers}). "
                             f"Consider using larger bars or increasing section width.")

        return required_layers

    def detailed_spacing_check(self, combo: Dict, b: float, d: float) -> Dict:

        bar_diameter = combo['bar_size']
        num_bars = combo['num_bars']

        # ACI 318 requirements - prioritized spacing formula
        min_spacing = max(25, bar_diameter, (4 / 3) * self.max_aggregate_size)
        min_cover = 40  # Standard cover assumption

        # Calculate available width for bars
        available_width = b - 2 * min_cover
        required_width = num_bars * bar_diameter + (num_bars - 1) * min_spacing

        compliant = required_width <= available_width

        # Calculate actual spacing if compliant
        actual_spacing = 0
        if compliant and num_bars > 1:
            actual_spacing = (available_width - num_bars * bar_diameter) / (num_bars - 1)

        return {
            'compliant': compliant,
            'min_spacing': min_spacing,
            'available_width': available_width,
            'required_width': required_width,
            'actual_spacing': actual_spacing,
            'spacing_ratio': actual_spacing / min_spacing if min_spacing > 0 else 0,
            'max_aggregate_factor': (4 / 3) * self.max_aggregate_size,
            'governing_criteria': self._get_governing_criteria(25, bar_diameter, (4 / 3) * self.max_aggregate_size)
        }

    def _get_governing_criteria(self, min_25mm: float, bar_dia: float, aggregate_factor: float) -> str:
        """
        Determine which criteria governs the minimum spacing requirement

        Args:
            min_25mm: Minimum 25mm requirement
            bar_dia: Bar diameter
            aggregate_factor: (4/3) * max_aggregate_size

        Returns:
            str: Description of governing criteria
        """
        max_val = max(min_25mm, bar_dia, aggregate_factor)

        if max_val == aggregate_factor:
            return f"Aggregate size factor: {aggregate_factor:.1f}mm"
        elif max_val == bar_dia:
            return f"Bar diameter: {bar_dia}mm"
        else:
            return "Minimum 25mm requirement"

    def get_layer_arrangement(self, combo: Dict, b: float) -> List[int]:

        num_bars = combo['num_bars']
        required_layers = self.calculate_required_layers(combo, b)

        if required_layers == 1:
            return [num_bars]

        # Distribute bars as evenly as possible across layers
        bars_per_layer = num_bars // required_layers
        extra_bars = num_bars % required_layers

        arrangement = []
        for i in range(required_layers):
            # Add extra bars to bottom layers first for better structural performance
            layer_bars = bars_per_layer + (1 if i < extra_bars else 0)
            arrangement.append(layer_bars)

        return arrangement

    def calculate_layer_spacing(self, combo: Dict, required_layers: int) -> float:

        if required_layers <= 1:
            return 0.0

        bar_diameter = combo['bar_size']

        # Minimum clear spacing between layers
        min_clear_spacing = max(25, bar_diameter, (4 / 3) * self.max_aggregate_size)

        # Center-to-center spacing
        layer_spacing = bar_diameter + min_clear_spacing

        return layer_spacing
    # </editor-fold>
    # <editor-fold desc="VERIFICATION SYSTEMS">

    def verify_capacity(self, As_required: float, phi: float, b: float, d: float,
                        fc_prime: float, fy: float, Mu: float) -> Dict:
        """Verify if φMn ≥ Mu"""

        # Inputs must be in consistent units (mm, MPa, N)
        a = (As_required * fy) / (0.85 * fc_prime * b)  # depth of equivalent stress block
        Mn = As_required * fy * (d - a / 2)  # moment in N·mm
        Mn = Mn / 1e6  # convert to kN·m
        phi_Mn = phi * Mn  # factored moment
        Mu = Mu * 1e-3
        capacity_ratio = phi_Mn / Mu
        passes = capacity_ratio >= 1.0

        return {
            'Mn': Mn,
            'phi_Mn': phi_Mn,
            'Mu': Mu,
            'capacity_ratio': capacity_ratio,
            'passes': passes,
            'excess_capacity_percent': (capacity_ratio - 1.0) * 100
        }
    def verify_strain_compatibility(self, As_required: float, b: float, d: float,
                                    fc_prime: float, fy: float) -> Dict:
        """Verify steel yields properly and strain compatibility"""

        # Calculate neutral axis depth
        a = (As_required * fy) / (0.85 * fc_prime * b)
        beta = self.calculate_beta(fc_prime)
        c = a / beta

        # Calculate steel strain
        eps_cu = 0.003  # Ultimate concrete strain
        eps_s = eps_cu * (d - c) / c
        eps_y = fy / self.Es  # Yield strain

        # Check if steel yields
        steel_yields = eps_s >= eps_y

        # Calculate actual steel stress
        if steel_yields:
            fs = fy
        else:
            fs = eps_s * self.Es

        return {
            'c': c,
            'a': a,
            'eps_s': eps_s,
            'eps_y': eps_y,
            'fs': fs,
            'steel_yields': steel_yields,
            'passes': steel_yields,
            'strain_ratio': eps_s / eps_y if eps_y > 0 else 0
        }

    def verify_ductility_requirements(self, rho_required: float, rho_bal: float,
                                      fc_prime: float, fy: float, d: float) -> Dict:
        """Verify adequate ductility index"""

        # Calculate ductility index (curvature ductility)
        beta = self.calculate_beta(fc_prime)
        c = self.calculate_neutral_axis_depth(rho_required, fc_prime, fy, d)

        # Curvature at yield and ultimate
        eps_y = fy / self.Es
        eps_cu = 0.003

        # Approximate ductility calculations
        ductility_index = eps_cu / eps_y if eps_y > 0 else 0

        # ACI 318 ductility requirements
        rho_ratio = rho_required / rho_bal
        min_ductility_index = 3.0  # Minimum acceptable ductility

        passes = ductility_index >= min_ductility_index and rho_ratio <= 0.75

        return {
            'ductility_index': ductility_index,
            'min_ductility_index': min_ductility_index,
            'rho_ratio': rho_ratio,
            'max_rho_ratio': 0.75,
            'passes': passes,
            'ductility_adequate': ductility_index >= min_ductility_index,
            'steel_ratio_adequate': rho_ratio <= 0.75
        }

    def verify_compression_steel(self, c1: float, d_prime: float, fc_prime: float, fy: float) -> Dict:
        """Enhanced compression steel verification"""

        eps_cu = 0.003
        eps_s_prime = eps_cu * (c1 - d_prime) / c1
        eps_y = fy / self.Es

        if eps_s_prime >= eps_y:
            fs_prime = fy
            steel_yields = True
        else:
            fs_prime = eps_s_prime * self.Es
            steel_yields = False

        return {
            'eps_s_prime': eps_s_prime,
            'eps_y': eps_y,
            'fs_prime': fs_prime,
            'steel_yields': steel_yields,
            'strain_ratio': eps_s_prime / eps_y if eps_y > 0 else 0,
            'stress_ratio': fs_prime / fy if fy > 0 else 0
        }
    def comprehensive_verification_doubly_reinforced(self, As1: float, As_prime: float, Mu: float,
                                                     phi: float, b: float, d: float, d_prime: float,
                                                     fc_prime: float, fy: float,
                                                     compression_verification: Dict) -> Dict:
        """Comprehensive verification for doubly reinforced sections"""

        # Calculate total capacity
        fs_prime = compression_verification['fs_prime']
        a1 = (As1 * fy) / (0.85 * fc_prime * b)

        # Moment components
        Mn1 = As1 * fy * (d - a1 / 2)
        Mn2 = As_prime * fs_prime * (d - d_prime)
        Mn_total = Mn1 + Mn2
        phi_Mn = phi * Mn_total

        # Capacity verification
        capacity_ratio = phi_Mn / Mu
        capacity_adequate = capacity_ratio >= 1.0

        # Ductility verification for doubly reinforced
        total_tension_steel = As1 + (As_prime * fs_prime / fy)
        rho_total = total_tension_steel / (b * d)
        rho_bal = self.calculate_balanced_steel_ratio(fc_prime, fy)

        return {
            'capacity_verification': {
                'Mn_total': Mn_total,
                'phi_Mn': phi_Mn,
                'capacity_ratio': capacity_ratio,
                'adequate': capacity_adequate
            },
            'ductility_verification': {
                'rho_total': rho_total,
                'rho_bal': rho_bal,
                'rho_ratio': rho_total / rho_bal,
                'adequate': rho_total <= 0.75 * rho_bal
            },
            'compression_steel_verification': compression_verification,
            'overall_adequate': capacity_adequate and (rho_total <= 0.75 * rho_bal)
        }
    # </editor-fold>
    # <editor-fold desc="SAFETY & OPTIMIZATION">
    def calculate_safety_margins(self, capacity_check: Dict, strain_check: Dict,
                                 ductility_check: Dict) -> Dict:
        """Calculate comprehensive safety margins"""

        return {
            'capacity_safety_margin': capacity_check['excess_capacity_percent'],
            'strain_safety_margin': (strain_check['strain_ratio'] - 1.0) * 100 if strain_check[
                                                                                      'strain_ratio'] > 1.0 else 0,
            'ductility_safety_margin': (ductility_check['ductility_index'] - ductility_check['min_ductility_index']) /
                                       ductility_check['min_ductility_index'] * 100,
            'overall_safety_rating': self.calculate_overall_safety_rating(capacity_check, strain_check, ductility_check)
        }
    def calculate_overall_safety_rating(self, capacity_check: Dict, strain_check: Dict,
                                        ductility_check: Dict) -> str:
        """Calculate overall safety rating"""

        if not all([capacity_check['passes'], strain_check['passes'], ductility_check['passes']]):
            return 'INADEQUATE'

        capacity_margin = capacity_check['excess_capacity_percent']

        if capacity_margin > 20:
            return 'EXCELLENT'
        elif capacity_margin > 10:
            return 'GOOD'
        elif capacity_margin > 5:
            return 'ADEQUATE'
        else:
            return 'MINIMAL'
    def final_design_recommendation_engine(self, As_required: float, b: float, d: float,
                                           bar_range: Tuple[int, int], verification_results: Dict) -> Dict:
        """Final design recommendation engine with multiple options"""

        # 1. MULTIPLE BAR SIZE OPTIONS
        bar_combinations = self.evaluate_all_bar_combinations(As_required, bar_range)

        # 2. CONSTRUCTABILITY ANALYSIS
        constructability_analysis = self.analyze_constructability(bar_combinations, b, d)

        # 3. EXCESS STEEL OPTIMIZATION
        optimized_combinations = self.optimize_excess_steel(bar_combinations, As_required)

        # 4. SPACING VERIFICATION (ACI 318 compliance)
        spacing_verified_combinations = self.verify_spacing_compliance(optimized_combinations, b, d)

        # Select best recommendations
        best_recommendations = self.select_best_recommendations(
            spacing_verified_combinations, verification_results
        )

        return {
            'all_combinations': bar_combinations,
            'constructability_analysis': constructability_analysis,
            'optimized_combinations': optimized_combinations,
            'spacing_verified_combinations': spacing_verified_combinations,
            'best_recommendations': best_recommendations,
            'recommended_design': best_recommendations[0] if best_recommendations else None
        }

    # </editor-fold>
    # <editor-fold desc="BAR COMBINATION OPTIMIZATION">
    def calculate_best_bar_diameter(self, Mu, b, d, fc_prime, fy, bar_range):
        """
        Evaluate candidate bars in range to find the most efficient that passes capacity.
        Returns: (best_bar_diameter, details_dict)
        """
        candidate_bars = self.get_bars_in_range(bar_range)
        if not candidate_bars:
            candidate_bars = self.standard_bar_sizes

        min_excess = float('inf')
        best_bar_dia = None
        best_details = {}

        for bar_dia in candidate_bars:
            bar_area = math.pi * (bar_dia / 2) ** 2

            # Estimate minimum number of bars needed for Mu
            # Using simplified capacity check; for precise, replace with detailed capacity calculation
            min_bars = max(2, math.ceil(
                Mu / (bar_area * fy * (d - (self.calculate_beta(fc_prime) * (bar_area / (math.pi / 4)))))))

            total_area = min_bars * bar_area

            capacity = self.verify_capacity(total_area, 0.9, b, d, fc_prime, fy, Mu)
            if capacity['passes']:
                excess_percentage = (total_area - self.calculate_minimum_area_for_bars(bar_range,
                                                                                       2)) / self.calculate_minimum_area_for_bars(
                    bar_range, 2) * 100
                if excess_percentage < min_excess:
                    min_excess = excess_percentage
                    best_bar_dia = bar_dia
                    best_details = {
                        'bar_diameter': bar_dia,
                        'num_bars': min_bars,
                        'total_area': total_area,
                        'excess_percentage': excess_percentage
                    }
        return best_bar_dia, best_details
    def evaluate_all_bar_combinations(self, As_required: float, bar_range: Tuple[int, int]) -> List[Dict]:
        """Evaluate all feasible bar size combinations"""

        combinations = []

        for bar_size in range(bar_range[0], bar_range[1] + 1):
            if bar_size in self.standard_bar_sizes:
                bar_area = self.standard_bar_sizes[bar_size]
                min_bars = max(2, math.ceil(As_required / bar_area))

                for num_bars in range(min_bars, min_bars + 5):  # Check several options
                    total_area = num_bars * bar_area
                    if total_area >= As_required:
                        excess_percentage = ((total_area - As_required) / As_required) * 100

                        combinations.append({
                            'bar_size': bar_size,
                            'num_bars': num_bars,
                            'bar_area': bar_area,
                            'total_area': total_area,
                            'excess_percentage': excess_percentage,
                            'efficiency_score': self.calculate_efficiency_score(excess_percentage, num_bars)
                        })

        return sorted(combinations, key=lambda x: x['efficiency_score'], reverse=True)
    def analyze_constructability(self, combinations: List[Dict], b: float, d: float) -> Dict:
        """Analyze constructability of bar combinations"""

        constructability_scores = []

        for combo in combinations:
            # Check if single layer is possible
            single_layer_possible = self.check_single_layer_feasibility(combo, b)

            # Calculate required layers
            required_layers = self.calculate_required_layers(combo, b)

            # Constructability score (lower is better)
            constructability_score = required_layers + (0 if single_layer_possible else 1)

            constructability_scores.append({
                **combo,
                'single_layer_possible': single_layer_possible,
                'required_layers': required_layers,
                'constructability_score': constructability_score
            })

        return {
            'combinations_with_constructability': constructability_scores,
            'best_constructability': min(constructability_scores, key=lambda x: x['constructability_score'])
        }
    def optimize_excess_steel(self, combinations: List[Dict], As_required: float) -> List[Dict]:
        """Optimize combinations to minimize material waste"""

        # Filter combinations with reasonable excess (< 25%)
        reasonable_combinations = [
            combo for combo in combinations
            if combo['excess_percentage'] < 25
        ]

        if not reasonable_combinations:
            reasonable_combinations = combinations[:5]  # Take top 5 if all have high excess

        # Sort by excess percentage (ascending)
        return sorted(reasonable_combinations, key=lambda x: x['excess_percentage'])
    def verify_spacing_compliance(self, combinations: List[Dict], b: float, d: float) -> List[Dict]:
        """Verify ACI 318 spacing compliance"""

        compliant_combinations = []

        for combo in combinations:
            spacing_check = self.detailed_spacing_check(combo, b, d)

            if spacing_check['compliant']:
                compliant_combinations.append({
                    **combo,
                    'spacing_details': spacing_check
                })

        return compliant_combinations
    def select_best_recommendations(self, verified_combinations: List[Dict],
                                    verification_results: Dict) -> List[Dict]:
        """Select best design recommendations"""

        if not verified_combinations:
            return []

        # Score each combination
        scored_combinations = []

        for combo in verified_combinations:
            score = self.calculate_combination_score(combo, verification_results)
            scored_combinations.append({
                **combo,
                'overall_score': score
            })

        # Return top 3 recommendations
        return sorted(scored_combinations, key=lambda x: x['overall_score'], reverse=True)[:3]
    def calculate_combination_score(self, combo: Dict, verification_results: Dict) -> float:
        """Calculate overall score for bar combination"""

        # Scoring factors
        efficiency_weight = 0.3
        constructability_weight = 0.3
        excess_steel_weight = 0.2
        spacing_weight = 0.2

        # Normalize scores (0-1 scale)
        efficiency_score = combo['efficiency_score'] / 100  # Assuming max 100
        constructability_score = 1 / combo['constructability_score']  # Invert (lower is better)
        excess_steel_score = max(0, 1 - combo['excess_percentage'] / 25)  # Penalize high excess
        spacing_score = 1 if combo['spacing_details']['compliant'] else 0

        overall_score = (
                efficiency_weight * efficiency_score +
                constructability_weight * constructability_score +
                excess_steel_weight * excess_steel_score +
                spacing_weight * spacing_score
        )

        return overall_score
    # </editor-fold>
    # <editor-fold desc="DUCTILITY & SEISMIC REQUIREMENTS">
    def calculate_ductile_requirements(self, sections_results: Dict) -> Dict:
        try:
            all_ast_areas = []
            top_steel_areas = []
            for section in ['left', 'mid', 'right']:
                if section in sections_results:
                    for location in ['top', 'bottom']:
                        if location in sections_results[section]:
                            result = sections_results[section][location]
                            As_required = result.get('As_required', 0)
                            if As_required > 0:
                                all_ast_areas.append(As_required)
                                if location == 'top':
                                    top_steel_areas.append(As_required)
            max_ast_all_zones = max(all_ast_areas) if all_ast_areas else 0
            max_top_steel = max(top_steel_areas) if top_steel_areas else 0
            ast_25_percent = 0.25 * max_ast_all_zones
            ast_50_percent_top = 0.50 * max_top_steel
            bottom_left_right = max(ast_50_percent_top, ast_25_percent)
            top_left_right = ast_25_percent
            bottom_mid = ast_25_percent
            top_mid = ast_25_percent
            return {
                'max_ast_all_zones': max_ast_all_zones,
                'max_top_steel': max_top_steel,
                'ast_25_percent': ast_25_percent,
                'ast_50_percent_top': ast_50_percent_top,
                'bottom_left_right': bottom_left_right,
                'top_left_right': top_left_right,
                'bottom_mid': bottom_mid,
                'top_mid': top_mid
            }
        except:
            return {
                'max_ast_all_zones': 0,
                'max_top_steel': 0,
                'ast_25_percent': 0,
                'ast_50_percent_top': 0,
                'bottom_left_right': 0,
                'top_left_right': 0,
                'bottom_mid': 0,
                'top_mid': 0
            }

    def apply_ductile_requirements(
            self,
            section_result: Dict,
            section: str,
            location: str,
            ductile_req: Dict,
            bar_range: Tuple[int, int]
    ) -> Dict:
        """
        Adjusts the section result based on ductile requirements, updating bar options,
        spacing, and notes depending on the section and location.
        """
        try:
            # Determine the ductile requirement based on section and location
            ductile_requirement = 0
            if section in ['left', 'right']:
                if location == 'bottom':
                    ductile_requirement = ductile_req.get('bottom_left_right', 0)
                elif location == 'top':
                    ductile_requirement = ductile_req.get('top_left_right', 0)
            elif section == 'mid':
                if location == 'bottom':
                    ductile_requirement = ductile_req.get('bottom_mid', 0)
                elif location == 'top':
                    ductile_requirement = ductile_req.get('top_mid', 0)

            # Fetch current As_required and ensure numeric
            current_As_required = section_result.get('As_required', 0)
            if not isinstance(current_As_required, (int, float)):
                current_As_required = 0

            # Ensure ductile_requirement is numeric
            if not isinstance(ductile_requirement, (int, float)):
                ductile_requirement = 0

            # Check if ductile requirement demands more steel than current
            if ductile_requirement > current_As_required:
                # Update section with ductile control
                section_result['As_required'] = ductile_requirement
                section_result['ductile_controlling'] = True
                section_result['ductile_requirement'] = ductile_requirement

                # Generate bar options for the ductile control requirement
                new_bars = self.calculate_bar_combinations(ductile_requirement, bar_range, min_bars=2)
                section_result['bar_combinations'] = new_bars
                section_result['recommended_bars'] = new_bars[0] if new_bars else None
                section_result['note'] = f"Ductile requirement controls ({ductile_requirement:.0f} mm²)"
            else:
                # Ductile not controlling; keep current As_required
                section_result['ductile_controlling'] = False
                section_result['ductile_requirement'] = ductile_requirement

                # Recalculate bars based on current As_required
                current_bars = self.calculate_bar_combinations(current_As_required, bar_range, min_bars=2)
                section_result['recommended_bars'] = current_bars[0] if current_bars else None

                # Add note if ductile requirement exists but is satisfied
                if ductile_requirement > 0:
                    section_result['note'] = f"Ductile requirement: {ductile_requirement:.0f} mm² (satisfied)"

            return section_result

        except Exception as e:
            print(f"Error in apply_ductile_requirements: {str(e)}")
            section_result['ductile_error'] = str(e)
            return section_result

    def get_frame_type_safely(self, beam_data: Dict) -> str:
        """
        Safely extract frame type from beam data with validation.

        Args:
            beam_data (Dict): Beam data dictionary containing material properties

        Returns:
            str: Frame type ('ordinary', 'special', or 'intermediate')
        """
        try:
            design_set = beam_data.get('design_settings', {})
            frame_type = design_set.get('frame_type', 'ordinary')

            # Handle string input and normalize to lowercase
            if isinstance(frame_type, str):
                frame_type = frame_type.lower().strip()
            else:
                return 'ordinary'

            # Valid frame types according to seismic design codes
            valid_types = ['ordinary', 'special', 'intermediate']

            if frame_type in valid_types:
                return frame_type
            else:
                # Log warning for invalid frame type
                print(f"Warning: Invalid frame type '{frame_type}' found. Using 'ordinary' as default.")
                return 'ordinary'
        except Exception as e:
            print(f"Warning: Error extracting frame type: {str(e)}. Using 'ordinary' as default.")
            return 'ordinary'
    # </editor-fold>
    # <editor-fold desc="MAIN DESIGN WORKFLOW">
    def design_beam_section(self, section_forces: Dict, section_name: str, moment_type: str,
                            beam_dimensions: Dict) -> Dict:
        try:
            # Validate inputs
            if section_name not in ['left', 'mid', 'right']:
                raise ValueError(f"Invalid section_name: {section_name}")
            if moment_type not in ['max_moment_bottom', 'max_moment_top']:
                raise ValueError(f"Invalid moment_type: {moment_type}")

            # Extract beam dimensions
            b = beam_dimensions.get('base')
            h = beam_dimensions.get('height')
            L = beam_dimensions.get('length')
            if None in (b, h, L):
                raise KeyError("Incomplete beam dimensions")
            if not all(isinstance(v, (int, float)) and v > 0 for v in (b, h, L)):
                raise ValueError("Beam dimensions must be positive numbers")

            # Store geometry info in section_result for spacing verification
            section_result = {}
            section_result['base'] = b
            section_result['height'] = h
            section_result['length'] = L

            # Material properties
            material_props = self.beam_data.get('material_properties', {})
            reinforcement_params = self.beam_data.get('reinforcement_parameters', {})

            fc_prime = self.extract_concrete_strength(material_props.get('concrete_grade'))
            fy = material_props.get('main_steel_rebar_fy')
            cover = material_props.get('concrete_cover')
            if None in (fc_prime, fy, cover):
                raise ValueError("Incomplete material properties")

            # Get stirrup and main bar ranges
            stirrup_range = reinforcement_params.get('stirrup_bar_range', [13])
            stirrup_dia = stirrup_range[0] if stirrup_range else 13
            bar_range = reinforcement_params.get('main_bar_range', [16, 25])
            candidate_bars = self.get_bars_in_range(bar_range)
            if not candidate_bars:
                candidate_bars = self.standard_bar_sizes

            # Retrieve section force
            section_data = section_forces.get(section_name, {})
            Mu = section_data.get(moment_type, 0) * 1000  # convert kNm to Nmm

            # Determine optimal bar diameter
            main_bar_dia, _ = self.calculate_best_bar_diameter(Mu, b, h, fc_prime, fy, bar_range)
            if main_bar_dia is None:
                main_bar_dia = min(candidate_bars)

            # Effective depth
            d = self.calculate_effective_depth(h, cover, stirrup_dia, main_bar_dia)

            # Minimum reinforcement
            As_min_bars = self.calculate_minimum_area_for_bars(bar_range, min_bars=2)
            rho_min_code = self.calculate_min_steel_ratio(fc_prime, fy, b, d)
            As_min_code = rho_min_code * b * d
            As_min_actual = max(As_min_code, As_min_bars)

            # Design parameters
            phi = 0.9
            As_required, is_doubly_reinforced, design_details = self.calculate_required_steel_area(
                Mu, phi, b, d, fc_prime, fy, bar_range
            )


            # Capacity check
            capacity_check = self.verify_capacity(As_required, phi, b, d, fc_prime, fy, Mu)

            # Neutral axis and strain check
            rho = As_required / (b * d)
            c = self.calculate_neutral_axis_depth(rho, fc_prime, fy, d)
            eps_s = self.calc_strain_in_steel(d, c)
            eps_y = fy / self.Es
            steel_yields = eps_s >= eps_y

            # Prepare section result
            section_result = {
                'section': section_name,
                'moment': Mu / 1000,  # in kNm
                'effective_depth': d,
                'neutral_axis_depth': c,
                'strain_in_steel': eps_s,
                'steel_yields': steel_yields,
                'capacity_check': capacity_check,
                'design_status': 'PASS' if capacity_check['passes'] and steel_yields else 'REVISE',
                'As_required': As_required,
                'd': d,
                'c': c,
                'strain': eps_s
            }

            # Generate bar options
            bar_combos = self.calculate_bar_combinations(As_required, bar_range, min_bars=2)
            recommended_combo = bar_combos[0] if bar_combos else None
            section_result['bar_combinations'] = bar_combos
            section_result['recommended_bars'] = recommended_combo

            return section_result

        except KeyError as ke:
            print(f"[ERROR] Missing key during design of section '{section_name}': {str(ke)}")
            return self._create_error_result('Missing data in input', f"Missing key: {str(ke)}", section_name)
        except ValueError as ve:
            print(f"[ERROR] Invalid value during design of section '{section_name}': {str(ve)}")
            return self._create_error_result('Invalid value', str(ve), section_name)
        except Exception as e:
            print(f"[ERROR] design_beam_section exception: {str(e)}")
            return self._create_error_result('Design calculation error', 'Design calculation failed', section_name)
    def _create_error_result(self, error_type: str, note: str, section: str = "") -> Dict:
        return {
            'error': error_type,
            'design_required': False,
            'note': f"[{section}] {note}" if section else note,
            'moment': 0,
            'effective_depth': 0,
            'concrete_strength': 0,
            'steel_strength': 0,
            'is_doubly_reinforced': False,
            'As_required': 0,
            'As_minimum': 0,
            'bar_combinations': [],
            'recommended_bars': None
        }
    def design_all_beams(self) -> Dict:
        """
        Design all beams in the structure with enhanced error handling and logging.

        Returns:
            Dict: Complete design results organized by floor/group/beam hierarchy
        """
        section_errors = 0
        total_sections = 0

        if not self.beam_data:
            print("Error: No beam data available for design")
            return {}

        print("Starting beam design process...")
        design_results = {}

        # Get floor groups from beam data
        floor_groups = self.beam_data.get('floor_groups', {})
        if not floor_groups:
            print("Warning: No floor groups found in beam data")
            return {}

        # Get frame type once at the beginning (it's global for all beams)
        frame_type = self.get_frame_type_safely(self.beam_data)
        print(f"Frame type: {frame_type}")

        # Get bar range once (it's global for all beams)
        bar_range = self.beam_data.get('reinforcement_parameters', {}).get('main_bar_range', [16, 25])

        total_beams = 0
        processed_beams = 0

        # Process each floor
        for floor_name, beam_groups in floor_groups.items():
            print(f"\nProcessing floor: {floor_name}")
            design_results[floor_name] = {}

            if not isinstance(beam_groups, dict):
                print(f"Warning: Invalid beam groups structure for floor {floor_name}")
                continue

            # Process each beam group
            for beam_group_name, beams in beam_groups.items():
                print(f"  Processing group: {beam_group_name}")
                design_results[floor_name][beam_group_name] = {}

                if not isinstance(beams, dict):
                    print(f"Warning: Invalid beams structure for group {beam_group_name}")
                    continue

                # Process each individual beam
                for beam_number, individual_beam_data in beams.items():
                    total_beams += 1
                    print(f"    Processing beam: {beam_number}")

                    try:
                        # Validate individual beam data structure
                        if not self._validate_individual_beam_structure(individual_beam_data):
                            raise ValueError("Invalid individual beam data structure")

                        # Extract and validate beam dimensions once for this beam
                        beam_dimensions = self._extract_and_validate_beam_dimensions(individual_beam_data)
                        print(
                            f"      Beam dimensions: {beam_dimensions['base']}x{beam_dimensions['height']} mm (L={beam_dimensions['length']} mm)")

                        sections_results = {}

                        # Design each section (left, mid, right) for both top and bottom moments
                        for section in ['left', 'mid', 'right']:
                            print(f"      Designing section: {section}")
                            total_sections += 2  # top and bottom

                            section_forces = individual_beam_data.get("forces", {})

                            bottom_result = self.design_beam_section(
                                section_forces, section, 'max_moment_bottom', beam_dimensions
                            )

                            top_result = self.design_beam_section(
                                section_forces, section, 'max_moment_top', beam_dimensions
                            )

                            bottom_has_error = bottom_result.get('error') is not None
                            top_has_error = top_result.get('error') is not None

                            if bottom_has_error or top_has_error:
                                print(f"        ✗ Section {section} design failed")
                                section_errors += int(bottom_has_error) + int(top_has_error)
                            else:
                                print(
                                    f"        ✓ Section {section} designed (Bottom: {bottom_result.get('moment', 0):.2f} kNm, Top: {top_result.get('moment', 0):.2f} kNm)")

                            sections_results[section] = {
                                'bottom': bottom_result,
                                'top': top_result
                            }

                        # Apply frame-specific requirements
                        sections_results['frame_type'] = frame_type

                        if frame_type == 'special':
                            print(f"      Applying special frame requirements...")
                            try:
                                # Calculate ductile requirements
                                ductile_req = self.calculate_ductile_requirements(sections_results)

                                # Apply ductile requirements to each section and location
                                for section in ['left', 'mid', 'right']:
                                    for location in ['top', 'bottom']:
                                        if (section in sections_results and
                                                location in sections_results[section] and
                                                sections_results[section][location].get('design_status') != 'ERROR'):
                                            sections_results[section][location] = self.apply_ductile_requirements(
                                                sections_results[section][location],
                                                section,
                                                location,
                                                ductile_req,
                                                bar_range
                                            )

                                sections_results['ductile_requirements'] = ductile_req
                                print(f"      ✓ Special frame requirements applied successfully")

                            except Exception as e:
                                print(f"      ✗ Error applying special frame requirements: {str(e)}")
                                sections_results['ductile_requirements_error'] = str(e)

                        elif frame_type == 'intermediate':
                            print(f"      Intermediate frame - standard requirements applied")
                            # Add intermediate frame logic if needed
                            pass
                        else:
                            print(f"      Ordinary frame - standard requirements applied")
                            # Add ordinary frame logic if needed
                            pass

                        # Store results for this individual beam
                        design_results[floor_name][beam_group_name][beam_number] = sections_results
                        processed_beams += 1
                        print(f"    ✓ Beam {beam_number} designed successfully")

                    except Exception as e:
                        print(f"    ✗ Error processing beam {beam_number}: {str(e)}")
                        design_results[floor_name][beam_group_name][beam_number] = {
                            'design_status': 'ERROR',
                            'error_message': str(e),
                            'frame_type': frame_type
                        }

        print(f"\n=== Design Summary ===")
        print(f"Total beams processed: {processed_beams}/{total_beams}")
        if total_sections > 0:
            print(f"Section success rate: {(1 - section_errors / total_sections) * 100:.1f}%")
        else:
            print("No sections were processed.")

        self.design_results = design_results
        return design_results
    def _extract_and_validate_beam_dimensions(self, individual_beam_data: Dict) -> Dict:
        """
        Extract and validate beam dimensions from individual beam data.

        Args:
            individual_beam_data: Data for a single beam

        Returns:
            Dict: Validated beam dimensions

        Raises:
            KeyError: If dimensions are missing or incomplete
            ValueError: If dimension values are invalid
        """
        dimensions = individual_beam_data.get('dimensions')
        if not dimensions:
            raise KeyError("Missing 'dimensions' in beam data")

        # Check required dimension keys
        required_keys = ['base', 'height', 'length']
        for key in required_keys:
            if key not in dimensions:
                raise KeyError(f"Missing dimension '{key}' in beam data")

            value = dimensions[key]
            if not isinstance(value, (int, float)) or value <= 0:
                raise ValueError(f"Invalid dimension value for '{key}': {value}")

        return dimensions
    def _validate_individual_beam_structure(self, individual_beam_data: Dict) -> bool:
        """
        Validate the structure of individual beam data.

        Args:
            individual_beam_data: Data for a single beam

        Returns:
            bool: True if structure is valid, False otherwise
        """
        try:
            # Check required top-level keys
            required_keys = ['dimensions', 'forces']
            for key in required_keys:
                if key not in individual_beam_data:
                    print(f"[VALIDATION ERROR] Missing required key: {key}")
                    return False

            # Validate dimensions
            dimensions = individual_beam_data['dimensions']
            required_dim_keys = ['base', 'height', 'length']
            for key in required_dim_keys:
                if key not in dimensions:
                    print(f"[VALIDATION ERROR] Missing dimension key: {key}")
                    return False
                if not isinstance(dimensions[key], (int, float)) or dimensions[key] <= 0:
                    print(f"[VALIDATION ERROR] Invalid dimension value for {key}: {dimensions[key]}")
                    return False

            # Validate forces structure
            forces = individual_beam_data['forces']
            required_sections = ['left', 'mid', 'right']
            required_force_types = ['max_moment_bottom', 'max_moment_top', 'max_shear']

            for section in required_sections:
                if section not in forces:
                    print(f"[VALIDATION ERROR] Missing force section: {section}")
                    return False

                section_forces = forces[section]
                for force_type in required_force_types:
                    if force_type not in section_forces:
                        print(f"[VALIDATION ERROR] Missing force type '{force_type}' in section '{section}'")
                        return False

                    if not isinstance(section_forces[force_type], (int, float)):
                        print(
                            f"[VALIDATION ERROR] Invalid force value for {force_type} in {section}: {section_forces[force_type]}")
                        return False

            return True

        except Exception as e:
            print(f"[VALIDATION ERROR] Exception during validation: {str(e)}")
            return False
    # </editor-fold>
    # <editor-fold desc="UTILITIES & OUTPUT">
    def format_bar_description(self, section_result: Dict) -> str:
        if not section_result or not isinstance(section_result, dict):
            return "N/A"

        final_arrangement = section_result.get('final_arrangement')
        if final_arrangement:
            spacing_ok_value = final_arrangement.get('spacing_ok', False)
            if isinstance(spacing_ok_value, str):
                spacing_ok = spacing_ok_value.lower() == 'true'
            else:
                spacing_ok = bool(spacing_ok_value)

            if spacing_ok:
                layers = final_arrangement.get('layers', 1)
                bars_per_layer = final_arrangement.get('bars_per_layer', [])
                bar_dia = final_arrangement.get('bar_diameter', 0)

                # Validate bar diameter
                if not isinstance(bar_dia, (int, float)) or bar_dia <= 0:
                    return "ERROR: Invalid bar diameter"

                # Validate bars per layer
                if not bars_per_layer or not all(isinstance(b, int) for b in bars_per_layer):
                    return "ERROR: Invalid bars per layer"

                if layers == 1:
                    return f"{bars_per_layer[0]}-#{int(bar_dia)}"
                else:
                    layer_descs = []
                    for i, b in enumerate(bars_per_layer):
                        if isinstance(b, int) and b > 0:
                            layer_descs.append(f"L{i + 1}:{b}-#{int(bar_dia)}")
                    if not layer_descs:
                        return "ERROR: No bars in layers"
                    return "/".join(layer_descs)

        # Fallback: use 'design_details' if present
        design_details = section_result.get('design_details')
        if design_details:
            bar_dia = design_details.get('bar_diameter')
            num_bars = design_details.get('num_bars')
            if (isinstance(num_bars, int) and num_bars > 0 and
                    isinstance(bar_dia, (int, float)) and bar_dia > 0):
                return f"{num_bars}-#{int(bar_dia)}"

        # Fallback: use 'recommended_bars' if present
        recommended_bars = section_result.get('recommended_bars')
        if recommended_bars:
            num_bars = recommended_bars.get('num_bars', 0)
            bar_dia = recommended_bars.get('bar_diameter', 0)
            if (isinstance(num_bars, int) and num_bars > 0 and
                    isinstance(bar_dia, (int, float)) and bar_dia > 0):
                return f"{num_bars}-#{int(bar_dia)}"

        return "ERROR: Unable to format bar description"
    def _format_single_steel_group(self, steel_group: Dict, prefix: str = "") -> str:
        """
        Helper method to format a single steel group (tension or compression).

        Args:
            steel_group (Dict): Steel group information
            prefix (str): Prefix for the description (T for tension, C for compression)

        Returns:
            str: Formatted steel group description
        """
        num_bars = steel_group.get('num_bars', 0)
        bar_diameter = steel_group.get('bar_diameter', 0)

        if num_bars > 0 and bar_diameter > 0:
            base_desc = f"{num_bars}-#{bar_diameter}"
            return f"{prefix}:{base_desc}" if prefix else base_desc

        return "ERROR"
    def save_design_results(self, filename: str = None) -> bool:

        if not self.design_results:
            print("Warning: No design results to save")
            return False

        try:
            if filename is None:
                filename = f"flexural_design_results.json"

            if not filename.endswith('.json'):
                filename += '.json'

            # Create directory structure
            script_dir = os.path.dirname(os.path.abspath(__file__))
            raw_data_dir = os.path.join(script_dir, '..', 'raw_data')
            os.makedirs(raw_data_dir, exist_ok=True)
            save_path = os.path.join(raw_data_dir, filename)

            # Organize data with comprehensive structure
            data = {
                'metadata': {
                    'version': '1.0',
                    'beam_data': self.beam_data,
                    'design_parameters': {
                        'Es': getattr(self, 'Es', 200000),
                        'max_steel_ratio': getattr(self, 'max_steel_ratio', 0.75),
                        'max_aggregate_size': getattr(self, 'max_aggregate_size', 20),
                        'phi_flexure': getattr(self, 'phi_flexure', 0.9),
                        'minimum_bars': getattr(self, 'minimum_bars', 2)
                    },
                    'material_properties': self._extract_material_summary(),
                    'design_summary': self._generate_design_summary()
                },
                'results': self.design_results,
            }

            # Save to file
            with open(save_path, 'w') as f:
                json.dump(data, f, indent=4, ensure_ascii=False)

            print(f"Design results saved successfully to: {save_path}")
            return True

        except Exception as e:
            print(f"Error saving design results: {str(e)}")
            return False

    def _extract_material_summary(self) -> Dict:
        """
        Extract material properties summary from beam data.

        Returns:
            Dict: Material properties summary
        """
        if not self.beam_data:
            return {}

        # Get material properties from the top level of beam_data
        material_props = self.beam_data.get('material_properties', {})
        design_set = self.beam_data.get('design_settings', {})

        concrete_grade = material_props.get('concrete_grade', 'Unknown')
        main_steel_fy = material_props.get('main_steel_rebar_fy', 'Unknown')
        shear_steel_fy = material_props.get('shear_steel_fy', 'Unknown')

        # Count total beams in all floor groups
        total_beams = 0
        floor_groups = self.beam_data.get('floor_groups', {})
        for floor_name, floor_data in floor_groups.items():
            if isinstance(floor_data, dict):
                for group_name, group_data in floor_data.items():
                    if isinstance(group_data, dict):
                        # Count beams in this group
                        beam_count = sum(1 for key in group_data.keys()
                                         if key.lower().startswith('beam'))
                        total_beams += beam_count

        # Create material summary
        material_summary = {
            'concrete_properties': {
                'grade': concrete_grade,
                'total_beams_using': total_beams
            },
            'steel_properties': {
                'main_steel_fy': f"{main_steel_fy} MPa" if isinstance(main_steel_fy, (int, float)) else str(
                    main_steel_fy),
                'shear_steel_fy': f"{shear_steel_fy} MPa" if isinstance(shear_steel_fy, (int, float)) else str(
                    shear_steel_fy),
                'total_beams_using': total_beams
            },
            'other_properties': {
                'frame_type': design_set.get('frame_type', 'Unknown'),
                'concrete_cover': f"{material_props.get('concrete_cover', 0)} mm",
                'max_aggregate_size': f"{material_props.get('max_aggregate_size', 0)} mm",
                'reduction_factor_shear': design_set.get('reduction_factor_shear', 'Unknown'),
                'consider_bending_and_axial_design': design_set.get('consider_bending_and_axial_design', 'Unknown')
            }
        }

        return material_summary
    def _generate_design_summary(self) -> Dict:
        """
        Generate overall design summary statistics.

        Returns:
            Dict: Design summary statistics
        """
        if not self.design_results:
            return {}

        summary = {
            'total_beams': 0,
            'total_sections': 0,
            'design_types': {'singly_reinforced': 0, 'doubly_reinforced': 0},
            'spacing_issues': 0,
            'design_errors': 0,
            'sections_by_location': {'left': 0, 'mid': 0, 'right': 0}
        }

        # Count beams from the original beam_data structure
        if self.beam_data:
            floor_groups = self.beam_data.get('floor_groups', {})
            for floor_name, floor_data in floor_groups.items():
                if isinstance(floor_data, dict):
                    for group_name, group_data in floor_data.items():
                        if isinstance(group_data, dict):
                            # Count beams in this group
                            beam_count = sum(1 for key in group_data.keys()
                                             if key.startswith('beam') or 'beam' in key.lower())
                            summary['total_beams'] += beam_count

        # Analyze design results
        for beam_id, beam_results in self.design_results.items():
            if isinstance(beam_results, dict):
                for section_name, section_result in beam_results.items():
                    if isinstance(section_result, dict):
                        summary['total_sections'] += 1

                        # Count sections by location
                        section_lower = section_name.lower()
                        for location in ['left', 'mid', 'right']:
                            if location in section_lower:
                                summary['sections_by_location'][location] += 1
                                break

                        # Count design types
                        design_type = section_result.get('design_type', 'singly_reinforced')
                        if design_type in summary['design_types']:
                            summary['design_types'][design_type] += 1

                        # Count spacing issues
                        final_arrangement = section_result.get('final_arrangement', {})
                        if not final_arrangement.get('spacing_ok', True):
                            summary['spacing_issues'] += 1

                        # Count design errors
                        if section_result.get('design_status') == 'ERROR':
                            summary['design_errors'] += 1

        return summary
    # </editor-fold>

def main():
    designer = FlexuralDesigner()
    if designer.beam_data:
        designer.design_all_beams()
        designer.save_design_results()

if __name__ == "__main__":
    main()