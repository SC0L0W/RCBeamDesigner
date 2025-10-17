import json
import os
import csv
from typing import Dict, List, Tuple, Any, Optional
from dataclasses import dataclass
import logging

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class BeamDesignSummary:
    """Data class to store beam design summary information"""
    grp: str
    beam: str
    type: str
    size: str
    material: str
    bottom_left: str
    bottom_mid: str
    bottom_right: str
    top_left: str
    top_mid: str
    top_right: str
    shear_left: str
    shear_mid: str
    shear_right: str
    sfr: str = "-"


class StructuralDesignSummaryGenerator:
    """Professional structural design summary report generator"""

    def __init__(self, flexural_file: str, shear_file: str, torsion_file: str):
        """
        Initialize the generator with input file paths

        Args:
            flexural_file: Path to flexural design results JSON
            shear_file: Path to shear design results JSON
            torsion_file: Path to torsion design results JSON
        """
        self.flexural_file = flexural_file
        self.shear_file = shear_file
        self.torsion_file = torsion_file

        # Create output directory
        self.output_dir = os.path.join(os.path.dirname(__file__), '..', 'output_data')
        os.makedirs(self.output_dir, exist_ok=True)

        # Initialize data containers
        self.flexural_data: Optional[Dict] = None
        self.shear_data: Optional[Dict] = None
        self.torsion_data: Optional[Dict] = None

    def load_json_file(self, filepath: str) -> Dict[str, Any]:
        try:
            with open(filepath, 'r', encoding='latin-1') as file:
                data = json.load(file)
                logger.info(f"Successfully loaded {filepath}")
                return data
        except FileNotFoundError:
            logger.error(f"File not found: {filepath}")
            raise
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON format in {filepath}: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading {filepath}: {e}")
            raise

    def load_all_data(self) -> None:
        """Load all required JSON files"""
        try:
            self.flexural_data = self.load_json_file(self.flexural_file)
            self.shear_data = self.load_json_file(self.shear_file)
            self.torsion_data = self.load_json_file(self.torsion_file)
            logger.info("All data files loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load data files: {e}")
            raise

    def format_reinforcement(self, bar_data: Dict) -> str:
        """
        Format reinforcement data into readable string

        Args:
            bar_data: Dictionary containing bar information

        Returns:
            Formatted reinforcement string (e.g., "2-#16", "4-#20")
        """
        if not bar_data:
            return "-"

        num_bars = bar_data.get('num_bars', 0)
        diameter = bar_data.get('bar_diameter', 0)

        if num_bars == 0 or diameter == 0:
            return "-"

        return f"{num_bars}-#{diameter}"

    def format_shear_reinforcement(self, shear_data: Dict) -> str:
        """
        Format shear reinforcement data

        Args:
            shear_data: Dictionary containing shear reinforcement data

        Returns:
            Formatted shear reinforcement string (e.g., "2L-#10 @ 120")
        """
        if not shear_data:
            return "-"

        legs = shear_data.get('stirrup_legs', 2)
        diameter = shear_data.get('stirrup_diameter', 0)
        spacing = shear_data.get('spacing', 0)

        if diameter == 0 or spacing == 0:
            return "-"

        return f"{legs}L-#{diameter} @ {spacing}"

    def get_beam_dimensions(self, beam_data: Dict) -> str:
        """
        Extract beam dimensions from beam data

        Args:
            beam_data: Dictionary containing beam information

        Returns:
            Formatted dimension string (e.g., "300 x 550")
        """
        # Try to get dimensions from different possible locations
        dimensions = beam_data.get('dimensions')
        if not dimensions:
            # Check if dimensions are in beam_dimensions
            dimensions = beam_data.get('beam_dimensions')

        if dimensions:
            width = dimensions.get('width', dimensions.get('base', 0))
            height = dimensions.get('height', 0)
            return f"{int(width)} x {int(height)}"

        return "300 x 550"  # Default size

    def get_material_info(self, data: Dict) -> str:
        """
        Extract material information

        Args:
            data: Design data dictionary

        Returns:
            Material specification string
        """
        # Get concrete grade
        concrete_grade = "C28"  # default

        # Try different locations for concrete grade
        metadata = data.get('metadata', {})
        if 'material_properties' in metadata:
            concrete_grade = metadata['material_properties'].get('concrete_grade', 'C28')
        elif 'beam_data' in data:
            beam_data = data['beam_data']
            if 'material_properties' in beam_data:
                concrete_grade = beam_data['material_properties'].get('concrete_grade', 'C28')

        # Get steel grades
        main_steel_fy = metadata.get('material_properties', {}).get('main_steel_rebar_fy', 414)
        shear_steel_fy = metadata.get('material_properties', {}).get('shear_steel_fy', 276)

        return f"{concrete_grade};Fy{int(main_steel_fy)};Fy{int(shear_steel_fy)}"

    def process_beam_data(self) -> List[BeamDesignSummary]:
        """
        Process all beam data and create summary objects

        Returns:
            List of BeamDesignSummary objects
        """
        beam_summaries = []

        if not all([self.flexural_data, self.shear_data, self.torsion_data]):
            logger.error("Data not loaded. Call load_all_data() first.")
            return beam_summaries

        # Get material information
        material_info = self.get_material_info(self.flexural_data)

        # Process flexural data (main source of beam information)
        flexural_results = self.flexural_data.get('results', {})

        group_counter = 1

        for floor_name, floor_data in flexural_results.items():
            for group_name, group_data in floor_data.items():
                for beam_name, beam_data in group_data.items():

                    # Get beam dimensions
                    beam_size = self.get_beam_dimensions(beam_data)

                    # Determine beam type (assume "Dcl" for detailed beams)
                    beam_type = "Dcl"

                    # Get reinforcement for each section
                    sections = ['left', 'mid', 'right']
                    reinforcement = {'bottom': {}, 'top': {}}

                    for section in sections:
                        section_data = beam_data.get(section, {})

                        # Bottom reinforcement
                        bottom_data = section_data.get('bottom', {})
                        if bottom_data:
                            reinforcement['bottom'][section] = self.format_reinforcement(
                                bottom_data.get('recommended_bars', {})
                            )

                        # Top reinforcement
                        top_data = section_data.get('top', {})
                        if top_data:
                            reinforcement['top'][section] = self.format_reinforcement(
                                top_data.get('recommended_bars', {})
                            )

                    # Get shear reinforcement from shear data
                    shear_reinforcement = {}
                    if self.shear_data:
                        shear_results = self.shear_data.get('beam_designs', {})
                        floor_shear = shear_results.get(floor_name, {})
                        group_shear = floor_shear.get(group_name, {})
                        beam_shear = group_shear.get(beam_name, {})

                        for section in sections:
                            section_shear = beam_shear.get(section, {})
                            shear_reinforcement[section] = self.format_shear_reinforcement(section_shear)

                    # Create summary object
                    summary = BeamDesignSummary(
                        grp=f"G{group_counter}",
                        beam=f"B{len(beam_summaries) + 1}",
                        type=beam_type,
                        size=beam_size,
                        material=material_info,
                        bottom_left=reinforcement['bottom'].get('left', '-'),
                        bottom_mid=reinforcement['bottom'].get('mid', '-'),
                        bottom_right=reinforcement['bottom'].get('right', '-'),
                        top_left=reinforcement['top'].get('left', '-'),
                        top_mid=reinforcement['top'].get('mid', '-'),
                        top_right=reinforcement['top'].get('right', '-'),
                        shear_left=shear_reinforcement.get('left', '-'),
                        shear_mid=shear_reinforcement.get('mid', '-'),
                        shear_right=shear_reinforcement.get('right', '-'),
                        sfr="-"
                    )

                    beam_summaries.append(summary)

                group_counter += 1

        return beam_summaries

    def generate_csv_report(self, output_filename: str = 'structural_design_summary.csv') -> str:
        """
        Generate comprehensive CSV report

        Args:
            output_filename: Name of output CSV file

        Returns:
            Path to generated CSV file
        """
        try:
            # Load all data
            self.load_all_data()

            # Process beam data
            beam_summaries = self.process_beam_data()

            if not beam_summaries:
                logger.warning("No beam data found to generate report")
                return ""

            # Prepare CSV data
            headers = [
                'GRP', 'Beam', 'Type', 'Size', 'Material',
                'Bottom Left', 'Bottom Mid', 'Bottom Right',
                'Top Left', 'Top Mid', 'Top Right',
                'Shear Left', 'Shear Mid', 'Shear Right', 'SFR'
            ]

            # Generate output path
            output_path = os.path.join(self.output_dir, output_filename)

            # Write CSV file
            with open(output_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow(headers)

                for summary in beam_summaries:
                    writer.writerow([
                        summary.grp, summary.beam, summary.type, summary.size, summary.material,
                        summary.bottom_left, summary.bottom_mid, summary.bottom_right,
                        summary.top_left, summary.top_mid, summary.top_right,
                        summary.shear_left, summary.shear_mid, summary.shear_right, summary.sfr
                    ])

            logger.info(f"CSV report generated successfully: {output_path}")
            logger.info(f"Total beams processed: {len(beam_summaries)}")

            return output_path

        except Exception as e:
            logger.error(f"Error generating CSV report: {e}")
            raise

    def generate_summary_statistics(self) -> Dict[str, Any]:
        """
        Generate summary statistics from the design data

        Returns:
            Dictionary containing summary statistics
        """
        if not all([self.flexural_data, self.shear_data, self.torsion_data]):
            logger.error("Data not loaded. Call load_all_data() first.")
            return {}

        stats = {
            'total_beams': 0,
            'total_sections': 0,
            'max_moment': 0,
            'max_shear': 0,
            'max_torsion': 0,
            'design_passes': 0,
            'design_failures': 0
        }

        # Extract statistics from flexural data
        if self.flexural_data:
            metadata = self.flexural_data.get('metadata', {})
            design_summary = metadata.get('design_summary', {})

            stats['total_beams'] = design_summary.get('total_beams', 0)
            stats['total_sections'] = design_summary.get('total_sections', 0)

            # Process results for max values
            results = self.flexural_data.get('results', {})
            for floor_data in results.values():
                for group_data in floor_data.values():
                    for beam_data in group_data.values():
                        for section_data in beam_data.values():
                            if isinstance(section_data, dict):
                                for location_data in section_data.values():
                                    if isinstance(location_data, dict):
                                        moment = location_data.get('moment', 0)
                                        stats['max_moment'] = max(stats['max_moment'], moment)

                                        if location_data.get('design_status') == 'PASS':
                                            stats['design_passes'] += 1
                                        else:
                                            stats['design_failures'] += 1

        # Extract shear statistics
        if self.shear_data:
            beam_designs = self.shear_data.get('beam_designs', {})
            for floor_data in beam_designs.values():
                for group_data in floor_data.values():
                    for beam_data in group_data.values():
                        for section_data in beam_data.values():
                            if isinstance(section_data, dict):
                                shear = section_data.get('extracted_forces', {}).get('max_shear', 0)
                                stats['max_shear'] = max(stats['max_shear'], shear)

        # Extract torsion statistics
        if self.torsion_data:
            beams = self.torsion_data.get('beams', {})
            for floor_data in beams.values():
                for group_data in floor_data.values():
                    for beam_data in group_data.values():
                        sections = beam_data.get('sections', {})
                        for section_data in sections.values():
                            if isinstance(section_data, dict):
                                torsion = section_data.get('forces', {}).get('torsion_kNm', 0)
                                stats['max_torsion'] = max(stats['max_torsion'], torsion)

        return stats

    def print_summary_report(self) -> None:
        """Print a summary report to console"""
        try:
            self.load_all_data()
            stats = self.generate_summary_statistics()

            print("\n" + "=" * 60)
            print("STRUCTURAL DESIGN SUMMARY REPORT")
            print("=" * 60)
            print(f"Total Beams: {stats.get('total_beams', 'N/A')}")
            print(f"Total Sections: {stats.get('total_sections', 'N/A')}")
            print(f"Maximum Moment: {stats.get('max_moment', 0):.2f} kNm")
            print(f"Maximum Shear: {stats.get('max_shear', 0):.2f} kN")
            print(f"Maximum Torsion: {stats.get('max_torsion', 0):.2f} kNm")
            print(f"Design Passes: {stats.get('design_passes', 'N/A')}")
            print(f"Design Failures: {stats.get('design_failures', 'N/A')}")
            print("=" * 60)

        except Exception as e:
            logger.error(f"Error generating summary report: {e}")


def main():
    """Main function to demonstrate usage"""
    try:
        # Initialize generator
        generator = StructuralDesignSummaryGenerator(
            flexural_file='../raw_data/flexural_design_results.json',
            shear_file='../raw_data/shear_design_results.json',
            torsion_file='../raw_data/torsion_design_output.json'
        )

        # Generate CSV report
        output_path = generator.generate_csv_report()

        # Print summary to console
        generator.print_summary_report()

        print(f"\nDetailed CSV report generated at: {output_path}")

    except Exception as e:
        logger.error(f"Error in main execution: {e}")
        raise


if __name__ == "__main__":
    main()