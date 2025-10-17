import json
import math
import os
from typing import Dict, List, Tuple, Optional
from datetime import datetime


class ShearDesigner:
    def __init__(self, beam_data_file: str = None):
        self.beam_data = None
        self.design_results = {}
        self.Es = 200000  # MPa, steel modulus
        self.phi_shear = 0.75  # shear strength reduction factor
        self.max_aggregate_size = 25
        self.standard_bar_sizes = [10, 12, 16, 20, 25, 28, 32, 36, 40]
        self.frame_type = 'ordinary'
        self.reinforcement_parameters = {}
        self.stirrup_spacing_round_off = 25  # Default value in mm

        # Default concrete strengths (MPa)
        self.concrete_strengths = {
            'C20': 20, 'C25': 25, 'C28': 28, 'C30': 30, 'C35': 35, 'C40': 40
        }

        # Load beam data from provided file or default location
        if beam_data_file:
            self.load_beam_data(beam_data_file)
        else:
            # Try to load from default location
            default_filename = os.path.join('..', 'raw_data', 'flexural_design_results.json')
            if os.path.exists(default_filename):
                self.load_beam_data(default_filename)
            else:
                self.beam_data = None

        if self.beam_data:
            self._set_parameters_from_json()

    def load_beam_data(self, filename: str = None, data_dict: dict = None) -> None:
        """Load beam data from JSON file or dictionary."""
        try:
            if data_dict:
                self.beam_data = data_dict
                print("Successfully loaded beam data from dictionary")
            elif filename:
                with open(filename, 'r') as f:
                    self.beam_data = json.load(f)
                print(f"Successfully loaded beam data from {filename}")
            else:
                print("No data source provided")
                return
        except (FileNotFoundError, json.JSONDecodeError) as e:
            print(f"Error loading beam data: {e}")
            self.beam_data = None

    def _set_parameters_from_json(self):
        """Extract parameters from loaded beam data."""
        if not self.beam_data:
            print("Warning: No beam data available for parameter extraction")
            return

        # Extract from metadata first, then from beam_data directly
        metadata = self.beam_data.get('metadata', {})
        beam_data_section = metadata.get('beam_data', {})

        # Extract general design settings
        design_settings = beam_data_section.get('design_settings', {})
        if not design_settings:
            # Try alternative location
            design_settings = self.beam_data.get('design_settings', {})

        self.frame_type = design_settings.get('frame_type', 'ordinary').lower()
        self.reduction_factor_shear = design_settings.get('reduction_factor_shear', 0.75)
        self.lightweight_factor_shear = design_settings.get('lightweight_factor_shear', 1.0)
        self.reinforcement_type = design_settings.get('reinforcement_type', 'Non-Pre-stressed')
        self.consider_bending_and_axial = design_settings.get('consider_bending_and_axial_design', True)

        # Extract stirrup spacing round-off value
        self.stirrup_spacing_round_off = design_settings.get('stirrup_spacing_round_off', 25)

        # Extract material properties
        material_props = beam_data_section.get('material_properties', {})
        if not material_props:
            material_props = self.beam_data.get('material_properties', {})

        self.concrete_grade = material_props.get('concrete_grade', 'C28')
        self.main_steel_fy = material_props.get('main_steel_rebar_fy', 414.0)
        self.shear_steel_fy = material_props.get('shear_steel_fy', 276.0)
        self.concrete_cover = material_props.get('concrete_cover', 40.0)
        self.max_aggregate_size = material_props.get('max_aggregate_size', 25.0)

        # Extract reinforcement parameters
        reinf_params = beam_data_section.get('reinforcement_parameters', {})
        if not reinf_params:
            reinf_params = self.beam_data.get('reinforcement_parameters', {})

        self.main_bar_range = reinf_params.get('main_bar_range', [16, 32])
        self.stirrup_bar_range = reinf_params.get('stirrup_bar_range', [12, 16])
        self.min_stirrup_spacing = reinf_params.get('min_stirrup_spacing', 75.0)
        self.max_stirrup_spacing = reinf_params.get('max_stirrup_spacing', 300.0)

        # Extract floor groups and beams
        self.floor_groups = beam_data_section.get('floor_groups', {})
        if not self.floor_groups:
            self.floor_groups = self.beam_data.get('floor_groups', {})

        # Extract from results section if available
        results = self.beam_data.get('results', {})
        if results and not self.floor_groups:
            self.floor_groups = results

        print(f"Frame type: {self.frame_type}")
        print(f"Concrete grade: {self.concrete_grade}")
        print(f"Spacing limits: {self.min_stirrup_spacing} - {self.max_stirrup_spacing} mm")
        print(f"Stirrup spacing round-off: {self.stirrup_spacing_round_off} mm")

    def round_spacing(self, spacing: float) -> float:
        """Round spacing to the nearest multiple of stirrup_spacing_round_off."""
        round_off = self.stirrup_spacing_round_off
        return math.floor(spacing / round_off) * round_off

    def get_concrete_strength(self, grade: str) -> float:
        """Get concrete compressive strength from grade."""
        return self.concrete_strengths.get(grade, 28)

    def calculate_effective_depth(self, height: float, cover: float, stirrup_dia: float, main_bar_dia: float) -> float:
        """Calculate effective depth of beam."""
        return height - cover - stirrup_dia - main_bar_dia / 2

    def calculate_longitudinal_reinforcement_ratio(self, As: float, b: float, d: float) -> float:
        """Calculate longitudinal reinforcement ratio."""
        return As / (b * d)

    def calculate_Vc(self, fc_prime: float, b: float, d: float,
                     rho: Optional[float] = None, Vu: Optional[float] = None,
                     Mu: Optional[float] = None, Nu: Optional[float] = None,
                     Ag: Optional[float] = None) -> float:
        """Calculate concrete shear capacity."""
        lambda_factor = self.lightweight_factor_shear

        # Basic formula: Vc = 0.29 * lambda * sqrt(fc') * b * d
        Vc_basic = 0.29 * lambda_factor * math.sqrt(fc_prime) * b * d

        # Consider axial force if present
        if Nu is not None and Ag is not None and Nu != 0:
            if Nu > 0:  # Compression
                axial_factor = 1 + Nu / (14 * Ag)
            else:  # Tension
                axial_factor = 1 + Nu / (3.5 * Ag)
            Vc_basic *= axial_factor

        # More detailed formula with moment and shear interaction
        if rho is not None and Vu is not None and Mu is not None and Mu != 0:
            Vc_detailed = (0.16 * lambda_factor * math.sqrt(fc_prime) + 17 * rho * Vu * d / Mu) * b * d
            if Nu is not None and Ag is not None and Nu != 0:
                if Nu > 0:  # Compression
                    axial_factor = 1 + Nu / (14 * Ag)
                else:  # Tension
                    axial_factor = 1 + Nu / (3.5 * Ag)
                Vc_detailed *= axial_factor
            return min(Vc_basic, Vc_detailed)

        return Vc_basic

    def calculate_required_shear_reinforcement(self, Vu: float, Vc: float) -> float:
        """Calculate required shear reinforcement."""
        phi = self.reduction_factor_shear
        Vs = Vu / phi - Vc
        return max(0, Vs)

    def calculate_stirrup_area(self, bar_diameter: float, legs: int) -> float:
        """Calculate total area of stirrup legs."""
        bar_area = math.pi * (bar_diameter / 2) ** 2
        return legs * bar_area

    def calculate_spacing(self, Av: float, f_yv: float, d: float, Vs: float) -> float:
        """Calculate stirrup spacing."""
        if Vs <= 0:
            return float('inf')
        return (Av * f_yv * d) / Vs

    def check_minimum_shear_reinforcement(self, b: float, s: float, f_yv: float, Av: float) -> bool:
        """Check if minimum shear reinforcement is provided."""
        # Minimum Av/s = 0.35 * b / f_yv
        min_av_s = 0.35 * b / f_yv
        actual_av_s = Av / s
        return actual_av_s >= min_av_s

    def get_spacing_limits(self, d: float, Vs: float, fc_prime: float, b: float) -> Tuple[float, float]:
        """Get maximum and minimum spacing limits."""
        # Maximum spacing based on code requirements
        if Vs <= 0.33 * math.sqrt(fc_prime) * b * d:
            max_s_code = min(d / 2, 600)  # mm
        else:
            max_s_code = min(d / 4, 300)  # mm

        # Consider frame type
        if self.frame_type == 'special':
            max_s_code = min(max_s_code, d / 4, 150)  # More restrictive for special frames

        # Use the minimum of code requirement and user-specified maximum
        max_s = min(max_s_code, self.max_stirrup_spacing)

        # Minimum spacing from user input
        min_s = self.min_stirrup_spacing

        return min_s, max_s

    def determine_stirrup_legs(self, b: float) -> int:
        """Determine number of stirrup legs based on beam width."""
        if b <= 300:
            return 2  # 2-leg stirrups
        elif b <= 500:
            return 4
        else:
            return 6

    def get_minimum_main_bar_diameter(self, section_data: Dict) -> float:
        """Get minimum main bar diameter from top and bottom reinforcement."""
        try:
            # Get recommended bars for top and bottom
            top_bars = section_data.get('top', {}).get('recommended_bars', {})
            bottom_bars = section_data.get('bottom', {}).get('recommended_bars', {})

            top_dia = top_bars.get('bar_diameter', 20)
            bottom_dia = bottom_bars.get('bar_diameter', 20)

            # Return minimum of top and bottom
            return min(top_dia, bottom_dia)
        except:
            return 20  # Default value

    def extract_beam_dimensions(self, beam_data: Dict) -> Dict:
        """Extract beam dimensions from beam data."""
        # Try to get dimensions from beam data
        dimensions = beam_data.get('dimensions', {})
        if dimensions:
            return dimensions

        # If not found, look in the beam data structure
        for key, value in beam_data.items():
            if isinstance(value, dict) and 'dimensions' in value:
                return value['dimensions']

        # Default dimensions
        return {'base': 300, 'height': 550, 'length': 5000}

    def extract_forces_for_section(self, section_name: str, beam_data: Dict) -> Dict:
        """Extract forces for a specific section (left, mid, right)."""
        forces = {}

        # First, try to get forces from the 'forces' key in beam_data
        if 'forces' in beam_data and section_name in beam_data['forces']:
            forces = beam_data['forces'][section_name].copy()
            print(f"Found forces in beam_data['forces']['{section_name}']: {forces}")

        # If not found, try to get from the section data directly
        elif section_name in beam_data:
            section_data = beam_data[section_name]
            # Check if forces are directly in the section data
            if any(key in section_data for key in ['max_shear', 'max_moment_top', 'max_moment_bottom', 'max_axial']):
                forces = section_data.copy()
                print(f"Found forces in beam_data['{section_name}']: {forces}")

        # If still not found, try from metadata structure
        if not forces:
            metadata = self.beam_data.get('metadata', {})
            beam_data_section = metadata.get('beam_data', {})
            floor_groups = beam_data_section.get('floor_groups', {})

            # Navigate through the structure to find forces
            for floor_name, groups in floor_groups.items():
                for group_name, beams in groups.items():
                    for beam_name, beam_info in beams.items():
                        if 'forces' in beam_info and section_name in beam_info['forces']:
                            forces = beam_info['forces'][section_name].copy()
                            print(f"Found forces in metadata structure: {forces}")
                            break
                    if forces:
                        break
                if forces:
                    break

        # Default values if nothing found
        if not forces:
            print(f"Warning: No forces found for section '{section_name}'. Using default values.")
            forces = {
                'max_shear': 0,
                'max_moment_top': 0,
                'max_moment_bottom': 0,
                'max_axial': 0,
                'max_torsion': 0
            }

        return forces

    def design_shear_for_section(self, section_name: str, section_data: Dict, beam_data: Dict,
                                 beam_dimensions: Dict) -> Dict:
        """Design shear reinforcement for a beam section."""
        try:
            # Extract beam dimensions
            b = beam_dimensions.get('base', 300)  # mm
            h = beam_dimensions.get('height', 550)  # mm
            L = beam_dimensions.get('length', 5000)  # mm

            # Extract forces for this section
            forces = self.extract_forces_for_section(section_name, beam_data)

            # Extract shear force from forces data
            Vu = forces.get('max_shear', 0) * 1000  # Convert kN to N

            # Get moment for shear-moment interaction (use max of top and bottom)
            max_moment_top = forces.get('max_moment_top', 0)
            max_moment_bottom = forces.get('max_moment_bottom', 0)
            Mu = max(abs(max_moment_top), abs(max_moment_bottom)) * 1000000  # Convert kN·m to N·mm

            # Get axial force
            Nu = forces.get('max_axial', 0) * 1000  # Convert kN to N

            # Material properties
            fc_prime = self.get_concrete_strength(self.concrete_grade)
            f_yv = self.shear_steel_fy

            # Get main bar diameter from flexural design results
            main_bar_dia = self.get_minimum_main_bar_diameter(section_data)

            # Calculate effective depth
            stirrup_dia = min(self.stirrup_bar_range)  # Use minimum stirrup diameter
            d = self.calculate_effective_depth(h, self.concrete_cover, stirrup_dia, main_bar_dia)

            # Calculate gross area
            Ag = b * h

            # Calculate longitudinal reinforcement ratio (estimate from flexural design)
            As_top = 0
            As_bottom = 0

            if 'top' in section_data and 'recommended_bars' in section_data['top']:
                As_top = section_data['top']['recommended_bars'].get('total_area', 0)
            if 'bottom' in section_data and 'recommended_bars' in section_data['bottom']:
                As_bottom = section_data['bottom']['recommended_bars'].get('total_area', 0)

            # Use average steel area for rho calculation
            As_avg = (As_top + As_bottom) / 2 if (As_top + As_bottom) > 0 else 0.015 * b * d
            rho = self.calculate_longitudinal_reinforcement_ratio(As_avg, b, d)

            # Calculate concrete shear capacity
            Vc = self.calculate_Vc(fc_prime, b, d, rho, Vu, Mu, Nu, Ag)

            # Calculate required shear reinforcement
            Vs = self.calculate_required_shear_reinforcement(Vu, Vc)

            # Determine stirrup configuration
            legs = self.determine_stirrup_legs(b)

            # Design stirrup reinforcement
            design_result = {
                'section': section_name,
                'dimensions': {
                    'width': b,
                    'height': h,
                    'effective_depth': d,
                    'main_bar_diameter': main_bar_dia
                },
                'forces': {
                    'factored_shear': Vu,
                    'factored_moment': Mu,
                    'axial_force': Nu
                },
                'extracted_forces': forces,  # Include the extracted forces for debugging
                'material_properties': {
                    'concrete_strength': fc_prime,
                    'steel_yield_strength': f_yv,
                    'rho': rho
                },
                'concrete_capacity': Vc,
                'required_steel_shear': Vs,
                'stirrup_legs': legs,
                'stirrup_diameter': stirrup_dia,
                'spacing': None,
                'shear_reinforcement_required': Vs > 0
            }

            if Vs > 0:
                # Calculate stirrup area
                Av = self.calculate_stirrup_area(stirrup_dia, legs)

                # Calculate required spacing
                s_required = self.calculate_spacing(Av, f_yv, d, Vs)

                # Check spacing limits
                min_s, max_s = self.get_spacing_limits(d, Vs, fc_prime, b)

                # Determine final spacing
                s_final = max(min_s, min(s_required, max_s))

                # Check minimum shear reinforcement
                if not self.check_minimum_shear_reinforcement(b, s_final, f_yv, Av):
                    # Adjust spacing to meet minimum requirements
                    s_min_req = (Av * f_yv) / (0.35 * b)
                    s_final = min(s_final, s_min_req)

                # Round to practical spacing using the configurable round-off value
                s_final = self.round_spacing(s_final)
                s_final = max(s_final, min_s)

                design_result.update({
                    'spacing': s_final,
                    'stirrup_area': Av,
                    'spacing_limits': {
                        'minimum': min_s,
                        'maximum': max_s
                    },
                    'spacing_required': s_required
                })
            else:
                # No shear reinforcement required, but provide minimum
                min_s, max_s = self.get_spacing_limits(d, 0, fc_prime, b)
                design_result.update({
                    'spacing': max_s,
                    'note': 'Minimum shear reinforcement provided'
                })

            return design_result

        except Exception as e:
            print(f"Error in shear design for section {section_name}: {str(e)}")
            return {
                'section': section_name,
                'error': str(e)
            }

    def design_all_beams(self) -> Dict:
        """Design shear reinforcement for all beams."""
        if not self.beam_data:
            print("No beam data available for design")
            return {}

        design_results = {
            'timestamp': datetime.now().isoformat(),
            'design_parameters': {
                'frame_type': self.frame_type,
                'concrete_grade': self.concrete_grade,
                'shear_steel_fy': self.shear_steel_fy,
                'reduction_factor': self.reduction_factor_shear,
                'stirrup_bar_range': self.stirrup_bar_range,
                'stirrup_spacing_round_off': self.stirrup_spacing_round_off,
                'spacing_limits': {
                    'minimum': self.min_stirrup_spacing,
                    'maximum': self.max_stirrup_spacing
                }
            },
            'beam_designs': {}
        }

        # Get results from the data structure
        results = self.beam_data.get('results', {})
        if not results:
            results = self.floor_groups

        for floor_name, groups in results.items():
            design_results['beam_designs'][floor_name] = {}

            for group_name, beams in groups.items():
                design_results['beam_designs'][floor_name][group_name] = {}

                for beam_name, beam_data in beams.items():
                    # Extract beam dimensions
                    dimensions = self.extract_beam_dimensions(beam_data)

                    beam_design = {}

                    # Design each section of the beam (left, mid, right)
                    for section_name in ['left', 'mid', 'right']:
                        if section_name in beam_data:
                            section_data = beam_data[section_name]

                            section_design = self.design_shear_for_section(
                                section_name, section_data, beam_data, dimensions
                            )
                            beam_design[section_name] = section_design

                    design_results['beam_designs'][floor_name][group_name][beam_name] = beam_design

                    print(f"Completed shear design for {floor_name} - {group_name} - {beam_name}")

        self.design_results = design_results
        return design_results

    def save_results(self, filename: str = None):
        if not self.design_results:
            print("No design results to save")
            return

        if filename is None:
            filename = f"shear_design_results.json"

        try:
            script_dir = os.path.dirname(os.path.abspath(__file__))
            raw_data_dir = os.path.join(script_dir, '..', 'raw_data')
            os.makedirs(raw_data_dir, exist_ok=True)
            save_path = os.path.join(raw_data_dir, filename)

            with open(save_path, 'w') as f:
                json.dump(self.design_results, f, indent=2)
            print(f"Design results saved to {filename}")
        except Exception as e:
            print(f"Error saving results: {e}")

    def print_design_summary(self):
        """Print a summary of the design results."""
        if not self.design_results:
            print("No design results available")
            return

        print("\n" + "=" * 70)
        print("SHEAR DESIGN SUMMARY")
        print("=" * 70)

        beam_designs = self.design_results.get('beam_designs', {})

        for floor_name, groups in beam_designs.items():
            print(f"\n{floor_name.upper()}:")
            for group_name, beams in groups.items():
                print(f"  {group_name}:")
                for beam_name, sections in beams.items():
                    print(f"    {beam_name}:")
                    for section_name, design in sections.items():
                        if 'error' in design:
                            print(f"      {section_name}: ERROR - {design['error']}")
                        else:
                            spacing = design.get('spacing', 'N/A')
                            legs = design.get('stirrup_legs', 'N/A')
                            diameter = design.get('stirrup_diameter', 'N/A')
                            required = design.get('shear_reinforcement_required', False)
                            shear_force = design.get('forces', {}).get('factored_shear', 0) / 1000  # Convert to kN

                            print(f"      {section_name}: Vu = {shear_force:.1f} kN")
                            print(f"        Stirrups: {diameter}mm, {legs} legs @ {spacing}mm c/c")
                            if not required:
                                print(f"        (Minimum reinforcement only)")


def main():
    """Main function to run the shear design."""
    # Initialize the designer
    shear_designer = ShearDesigner()

    if shear_designer.beam_data:
        print("Starting shear design...")

        # Design all beams
        results = shear_designer.design_all_beams()

        # Print summary
        shear_designer.print_design_summary()

        # Save results
        shear_designer.save_results()

        print("\nShear design completed successfully!")
    else:
        print("No beam data loaded. Please check the input file.")


# Example usage with provided data
def run_with_provided_data(beam_data_dict):
    """Run shear design with provided beam data dictionary."""
    shear_designer = ShearDesigner()
    shear_designer.load_beam_data(data_dict=beam_data_dict)

    if shear_designer.beam_data:
        print("Starting shear design with provided data...")
        results = shear_designer.design_all_beams()
        shear_designer.print_design_summary()
        shear_designer.save_results()
        print("\nShear design completed successfully!")
        return results
    else:
        print("Failed to load provided beam data.")
        return None


if __name__ == "__main__":
    main()