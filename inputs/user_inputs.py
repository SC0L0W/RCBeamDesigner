#!/usr/bin/env python3
"""
user_input.py - Structural Beam Data Collection System
Collects and stores comprehensive beam design data including geometry,
materials, reinforcement parameters, forces, and design settings.
"""

from typing import Dict, Any, Tuple
import json
import os
from datetime import datetime


class BeamDataCollector:
    def __init__(self):
        self.beam_data = {}

    def get_float_input(self, prompt: str) -> float:
        """Get float input with validation"""
        while True:
            try:
                return float(input(prompt))
            except ValueError:
                print("Please enter a valid number.")

    def get_int_input(self, prompt: str) -> int:
        """Get integer input with validation"""
        while True:
            try:
                return int(input(prompt))
            except ValueError:
                print("Please enter a valid integer.")

    def get_tuple_input(self, prompt: str) -> Tuple[int, int]:
        """Get tuple input for ranges"""
        while True:
            try:
                values = input(prompt).split(',')
                if len(values) != 2:
                    raise ValueError
                return (int(values[0].strip()), int(values[1].strip()))
            except ValueError:
                print("Please enter two integers separated by comma (e.g., 12,25)")

    def collect_design_settings(self) -> Dict[str, Any]:
        """Collect design settings"""

        # Frame type selection
        print("\nFrame Type Options:")
        print("1. Intermediate")
        print("2. Special")
        frame_choice = self.get_int_input("Select frame type (1-2): ")
        frame_type = "intermediate" if frame_choice == 1 else "special"

        # Shear reduction factor
        print("\nReduction Factor for Shear Options:")
        print("1. 0.75")
        print("2. 0.65")
        reduction_factor_shear_choice = self.get_int_input("Select reduction factor for shear (1-2): ")
        reduction_factor_shear = 0.75 if reduction_factor_shear_choice == 1 else 0.65

        # Lightweight factor for shear
        print("\nLightweight Factor for Shear Options:")
        print("1. 1.00")
        print("2. 0.85")
        print("3. 0.75")
        lightweight_factor_shear_choice = self.get_int_input("Select lightweight factor for shear (1-3): ")
        if lightweight_factor_shear_choice == 1:
            lightweight_factor_shear = 1.00
        elif lightweight_factor_shear_choice == 2:
            lightweight_factor_shear = 0.85
        else:
            lightweight_factor_shear = 0.75

        # Reinforcement type
        print("\nReinforcement Type Options:")
        print("1. Pre-stressed")
        print("2. Non-Pre-stressed")
        reinforcement_type_choice = self.get_int_input("Select reinforcement type (1-2): ")
        reinforcement_type = "Pre-stressed" if reinforcement_type_choice == 1 else "Non-Pre-stressed"

        # Axial + bending
        consider_bending_and_axial_design = input(
            "Consider bending and axial in design? (yes/no): ").strip().lower() == 'yes'

        # Stirrup spacing round off
        stirrup_spacing_input = input(
            "Enter stirrup spacing round off (default 5): ").strip()
        if stirrup_spacing_input == '':
            stirrup_spacing_round_off = 5
        else:
            try:
                stirrup_spacing_round_off = int(stirrup_spacing_input)
            except ValueError:
                print("Invalid input. Defaulting stirrup spacing round off to 5.")
                stirrup_spacing_round_off = 5

        # Torsion design options
        print("\nTorsion Design Options:")
        consider_torsion_design = input(
            "Consider torsion design in calculations? (yes/no): ").strip().lower() == 'yes'


        # Build dictionary
        design_settings = {
            'frame_type': frame_type,
            'reduction_factor_shear': reduction_factor_shear,
            'lightweight_factor_shear': lightweight_factor_shear,
            'reinforcement_type': reinforcement_type,
            'consider_bending_and_axial_design': consider_bending_and_axial_design,
            'stirrup_spacing_round_off': stirrup_spacing_round_off,
            'consider_torsion_design': consider_torsion_design,
        }

        return design_settings

    def collect_material_properties(self) -> Dict[str, Any]:
        """Collect material and structural properties"""
        print("\n=== MATERIAL PROPERTIES ===")

        # Concrete grade
        concrete_grade = input("Enter concrete grade (e.g., C28): ").upper()

        material_props = {
            'concrete_grade': concrete_grade,
            'main_steel_rebar_fy': self.get_float_input("Enter main steel rebar fy (MPa): "),
            'shear_steel_fy': self.get_float_input("Enter shear steel fy (MPa): "),
            'concrete_cover': self.get_float_input("Enter concrete cover (mm): "),
            'max_aggregate_size': self.get_float_input("Enter maximum aggregate size (mm): ")
        }
        return material_props

    def collect_reinforcement_parameters(self) -> Dict[str, Any]:
        """Collect reinforcement bar parameters"""
        print("\n=== REINFORCEMENT PARAMETERS ===")

        reinforcement = {
            'main_bar_range': self.get_tuple_input("Enter main bar diameter range (min,max) in mm: "),
            'stirrup_bar_range': self.get_tuple_input("Enter stirrup bar diameter range (min,max) in mm: "),
            'min_stirrup_spacing': self.get_float_input("Enter minimum spacing between bars (mm): "),
            'max_stirrup_spacing': self.get_float_input("Enter maximum spacing between bars (mm): ")
        }

        return reinforcement

    def collect_beam_dimensions(self, floor_group: str, beam_group: str, beam_number: str) -> Dict[str, float]:
        """Collect dimensions for a specific beam"""
        print(f"\n--- Dimensions for Floor {floor_group}, Beam Group {beam_group}, Beam {beam_number} ---")

        dimensions = {
            'base': self.get_float_input("Enter beam base/width (mm): "),
            'height': self.get_float_input("Enter beam height (mm): "),
            'length': self.get_float_input("Enter beam length (mm): ")
        }

        return dimensions

    def collect_forces_for_section(self, section_name: str, floor_group: str, beam_group: str, beam_number: str) -> \
    Dict[str, float]:
        """Collect force values for a specific beam section, including axial and torsion forces"""
        print(
            f"\n--- Forces for {section_name.upper()} section (Floor {floor_group}, Beam Group {beam_group}, Beam {beam_number}) ---")

        forces = {
            'max_moment_bottom': self.get_float_input(f"Enter maximum moment at bottom for {section_name} (kN·m): "),
            'max_moment_top': self.get_float_input(f"Enter maximum moment at top for {section_name} (kN·m): "),
            'max_shear': self.get_float_input(f"Enter maximum shear for {section_name} (kN): "),
            'max_axial': self.get_float_input(f"Enter maximum axial force for {section_name} (kN): "),
            'max_torsion': self.get_float_input(f"Enter maximum torsion for {section_name} (kN·m): ")
        }

        return forces

    def collect_beam_forces(self, floor_group: str, beam_group: str, beam_number: str) -> Dict[str, Dict[str, float]]:
        """Collect forces for all sections of a specific beam"""
        print(f"\n=== BEAM FORCES - Floor {floor_group}, Beam Group {beam_group}, Beam {beam_number} ===")

        forces = {
            'left': self.collect_forces_for_section('left', floor_group, beam_group, beam_number),
            'mid': self.collect_forces_for_section('mid', floor_group, beam_group, beam_number),
            'right': self.collect_forces_for_section('right', floor_group, beam_group, beam_number)
        }

        return forces

    def collect_floor_group_info(self) -> Dict[str, Any]:
        """Collect information about floor groups and their beam groups"""
        print("\n=== FLOOR GROUP CONFIGURATION ===")

        num_floor_groups = self.get_int_input("Enter number of floor groups: ")

        floor_groups = {}

        for i in range(num_floor_groups):
            floor_group_name = input(f"Enter name for floor group {i + 1}: ")
            num_beam_groups = self.get_int_input(f"Enter number of beam groups in floor group '{floor_group_name}': ")

            beam_groups = {}

            for j in range(num_beam_groups):
                beam_group_name = input(f"Enter name for beam group {j + 1} in floor group '{floor_group_name}': ")
                num_beams = self.get_int_input(f"Enter number of beams in beam group '{beam_group_name}': ")

                beams = {}

                for k in range(num_beams):
                    beam_number = input(f"Enter beam number {k + 1} in beam group '{beam_group_name}': ")

                    # Collect dimensions for this beam
                    dimensions = self.collect_beam_dimensions(floor_group_name, beam_group_name, beam_number)

                    # Collect forces for this beam
                    forces = self.collect_beam_forces(floor_group_name, beam_group_name, beam_number)

                    beams[beam_number] = {
                        'dimensions': dimensions,
                        'forces': forces
                    }

                beam_groups[beam_group_name] = beams

            floor_groups[floor_group_name] = beam_groups

        return floor_groups

    def collect_all_data(self) -> Dict[str, Any]:
        """Collect all beam data"""
        print("STRUCTURAL BEAM DATA COLLECTION")
        print("=" * 40)

        # Collect global properties first
        design_settings = self.collect_design_settings()
        material_props = self.collect_material_properties()
        reinforcement = self.collect_reinforcement_parameters()
        floor_groups = self.collect_floor_group_info()

        # Combine all data
        beam_data = {
            'timestamp': datetime.now().isoformat(),
            'design_settings': design_settings,
            'material_properties': material_props,
            'reinforcement_parameters': reinforcement,
            'floor_groups': floor_groups
        }

        return beam_data

    def display_summary(self, data: Dict[str, Any]) -> None:
        """Display a summary of collected data"""
        print("\n" + "=" * 50)
        print("DATA COLLECTION SUMMARY")
        print("=" * 50)

        # Display design settings
        ds = data['design_settings']
        print(f"\nDESIGN SETTINGS:")
        print(f"  Frame Type: {ds['frame_type'].title()}")
        print(f"  Reduction Factor Shear: {ds['reduction_factor_shear']}")
        print(f"  Lightweight Factor Shear: {ds['lightweight_factor_shear']}")
        print(f"  Consider Bending and Axial Design: {ds['consider_bending_and_axial_design']}")


        materials = data['material_properties']
        reinforcement = data['reinforcement_parameters']
        floor_groups = data['floor_groups']

        # Display global properties
        print(f"\nGLOBAL PROPERTIES:")
        print(f"Concrete Grade: {materials['concrete_grade']}")
        print(f"Main Steel fy: {materials['main_steel_rebar_fy']} MPa")
        print(f"Shear Steel fy: {materials['shear_steel_fy']} MPa")
        print(f"Concrete Cover: {materials['concrete_cover']} mm")

        print(f"\nReinforcement Ranges:")
        print(f"  Main bars: {reinforcement['main_bar_range'][0]}-{reinforcement['main_bar_range'][1]} mm")
        print(f"  Stirrups: {reinforcement['stirrup_bar_range'][0]}-{reinforcement['stirrup_bar_range'][1]} mm")
        print(f"  Spacing: {reinforcement['min_stirrup_spacing']}-{reinforcement['max_stirrup_spacing']} mm")

        # Display floor group summary
        print(f"\nFLOOR GROUPS SUMMARY:")
        for floor_group, beam_groups in floor_groups.items():
            print(f"\n  Floor Group: {floor_group}")
            for beam_group, beams in beam_groups.items():
                print(f"    Beam Group: {beam_group}")
                for beam_number, beam_data in beams.items():
                    dimensions = beam_data['dimensions']
                    forces = beam_data['forces']
                    print(
                        f"      Beam {beam_number}: {dimensions['base']}×{dimensions['height']}×{dimensions['length']} mm")
                    print(
                        f"        Forces -")
                    for section, forces_dict in forces.items():
                        print(f"          {section.title()}:")
                        print(f"            M_bottom={forces_dict['max_moment_bottom']} kN·m")
                        print(f"            M_top={forces_dict['max_moment_top']} kN·m")
                        print(f"            Shear={forces_dict['max_shear']} kN")
                        print(f"            Axial={forces_dict['max_axial']} kN")
                        print(f"            Torsion={forces_dict['max_torsion']} kN·m")

    def save_to_file(self, data: dict) -> str:
        """Automatically save JSON data into raw_data folder"""
        # Get the directory where the script is located (inputs folder)
        script_dir = os.path.dirname(os.path.abspath(__file__))

        # Go up one level to beam_design_system folder, then into raw_data
        project_root = os.path.dirname(script_dir)
        raw_data_dir = os.path.join(project_root, 'raw_data')

        # Create raw_data directory if it doesn't exist
        os.makedirs(raw_data_dir, exist_ok=True)

        filename = os.path.join(raw_data_dir, 'beam_data.json')

        try:
            with open(filename, 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Data automatically saved to {filename}")

            # Also print the absolute path for clarity
            abs_path = os.path.abspath(filename)
            print(f"Absolute path: {abs_path}")

            # Verify the file was created
            if os.path.exists(filename):
                file_size = os.path.getsize(filename)
                print(f"File created successfully! Size: {file_size} bytes")
            else:
                print("Warning: File was not created!")

        except Exception as e:
            print(f"Error saving file: {e}")
            # Try saving to current directory as fallback
            fallback_filename = 'beam_data.json'
            try:
                with open(fallback_filename, 'w') as f:
                    json.dump(data, f, indent=2)
                print(f"Fallback: Data saved to {os.path.abspath(fallback_filename)}")
                return fallback_filename
            except Exception as e2:
                print(f"Fallback also failed: {e2}")
                raise

        return filename

    def run(self) -> None:
        """Main execution method"""
        try:
            # Collect all data
            beam_data = self.collect_all_data()
            self.beam_data = beam_data  # Save before displaying

            # Display summary
            self.display_summary(beam_data)

            # Automatically save data
            filename = self.save_to_file(beam_data)
            print(f"Saved data to: {filename}")

        except KeyboardInterrupt:
            print("\nData collection interrupted by user.")
            if self.beam_data:
                self.save_to_file(self.beam_data)
                print("Partial data saved.")

        except Exception as e:
            print(f"\nAn error occurred: {e}")


def main():
    """Main function to run the data collection"""
    collector = BeamDataCollector()
    collector.run()


if __name__ == "__main__":
    main()