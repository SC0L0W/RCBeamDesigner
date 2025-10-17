import json
import math
import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class FrameType(Enum):
    ORDINARY = "ordinary"
    INTERMEDIATE = "intermediate"
    SPECIAL = "special"


@dataclass
class BeamDimensions:
    """Data class for beam dimensions with validation."""
    width: float
    height: float
    length: float
    cover: float = 40.0

    def __post_init__(self):
        """Validate dimensions after initialization."""
        if self.width <= 0 or self.height <= 0 or self.length <= 0:
            raise ValueError("Beam dimensions must be positive values")
        if self.cover < 0:
            raise ValueError("Concrete cover cannot be negative")

    @property
    def effective_depth(self) -> float:
        """Calculate effective depth assuming 10mm stirrup diameter."""
        return self.height - self.cover - 10


@dataclass
class Forces:
    """Data class for forces acting on beam section."""
    torsion: float = 0.0  # kN⋅m
    axial: float = 0.0  # kN

    def to_design_units(self) -> 'Forces':
        """Convert forces to design units (N⋅mm for torsion, N for axial)."""
        return Forces(
            torsion=self.torsion * 1e6,  # kN⋅m to N⋅mm
            axial=self.axial * 1e3  # kN to N
        )


@dataclass
class TorsionReinforcementResult:
    """Result of torsion reinforcement design."""
    reinforcement_required: bool
    stirrup_diameter: float
    spacing: Optional[float]
    area_required: float
    capacity_ratio: float
    side_face_reinforcement: Dict[str, Any]


class TorsionDesign:
    """
    Improved torsion design class following NSCP 2015 provisions.

    Enhancements:
    - Better error handling and validation
    - Type hints for better code documentation
    - More comprehensive torsion calculations
    - Improved logging and debugging
    - Better separation of concerns
    - More robust file handling
    """

    # Class constants
    STEEL_MODULUS = 200000  # MPa
    DEFAULT_PHI_TORSION = 0.75
    DEFAULT_MAX_AGGREGATE_SIZE = 25
    MIN_STIRRUP_SPACING = 50  # mm
    MAX_STIRRUP_SPACING = 300  # mm
    SFA_HEIGHT_THRESHOLD = 750  # mm
    SFA_MIN_RATIO = 0.0010  # minimum area ratio for side face reinforcement

    CONCRETE_STRENGTHS = {
        'C20': 20, 'C25': 25, 'C28': 28, 'C30': 30, 'C35': 35, 'C40': 40
    }

    def __init__(self, input_filename: str = 'flexural_design_results.json',
                 output_filename: str = 'torsion_design_output.json'):
        """
        Initialize torsion design with input and output file specifications.

        Args:
            input_filename: Name of input JSON file
            output_filename: Name of output JSON file
        """
        self.input_filename = input_filename
        self.output_filename = output_filename
        self.beam_data: Optional[Dict[str, Any]] = None
        self.design_results: Dict[str, Any] = {}

        # Design parameters (will be set from input data)
        self.frame_type = FrameType.ORDINARY
        self.phi_torsion = self.DEFAULT_PHI_TORSION
        self.concrete_grade = 'C28'
        self.steel_fy = 414  # MPa
        self.concrete_cover = 40  # mm
        self.perform_torsion_design = False
        self.floor_groups: Dict[str, Any] = {}

        # Load and validate input data
        self._load_and_validate_input()

        if self.beam_data:
            self._extract_parameters_from_input()

    def _load_and_validate_input(self) -> None:
        """Load input data with robust error handling and encoding detection."""
        try:
            # Try multiple possible paths for input file
            possible_paths = [
                self.input_filename,
                os.path.join('..', 'raw_data', self.input_filename),
                os.path.join('raw_data', self.input_filename)
            ]

            for path in possible_paths:
                if os.path.exists(path):
                    logger.info(f"Loading input data from: {path}")

                    # Try different encodings in order of preference
                    encodings_to_try = ['utf-8', 'utf-8-sig', 'latin-1', 'cp1252', 'iso-8859-1']

                    for encoding in encodings_to_try:
                        try:
                            with open(path, 'r', encoding=encoding) as f:
                                self.beam_data = json.load(f)
                            logger.info(f"Successfully loaded file using {encoding} encoding")
                            self._validate_input_data()
                            return
                        except UnicodeDecodeError:
                            logger.debug(f"Failed to decode with {encoding} encoding, trying next...")
                            continue
                        except json.JSONDecodeError as e:
                            logger.error(f"Invalid JSON in input file with {encoding} encoding: {e}")
                            # If JSON is invalid, don't try other encodings
                            raise

                    # If all encodings fail, try to detect encoding automatically
                    try:
                        import chardet
                        with open(path, 'rb') as f:
                            raw_data = f.read()
                        detected = chardet.detect(raw_data)
                        detected_encoding = detected['encoding']
                        confidence = detected['confidence']

                        logger.info(f"Detected encoding: {detected_encoding} (confidence: {confidence:.2f})")

                        if confidence > 0.7:  # Only use if confidence is high enough
                            with open(path, 'r', encoding=detected_encoding) as f:
                                self.beam_data = json.load(f)
                            logger.info(f"Successfully loaded file using detected encoding: {detected_encoding}")
                            self._validate_input_data()
                            return
                    except ImportError:
                        logger.warning("chardet not installed. Install with: pip install chardet")
                    except Exception as e:
                        logger.debug(f"Encoding detection failed: {e}")

                    # Last resort: try reading as binary and cleaning
                    try:
                        logger.warning("Attempting to clean file and remove invalid characters...")
                        with open(path, 'rb') as f:
                            raw_data = f.read()

                        # Try to decode with error handling
                        cleaned_text = raw_data.decode('utf-8', errors='replace')
                        # Remove replacement characters
                        cleaned_text = cleaned_text.replace('\ufffd', '')

                        self.beam_data = json.loads(cleaned_text)
                        logger.warning("File loaded with character replacement - some data may be corrupted")
                        self._validate_input_data()
                        return

                    except Exception as e:
                        logger.error(f"Failed to load file even with character cleaning: {e}")
                        raise UnicodeDecodeError(f"Could not decode file {path} with any supported encoding")

            raise FileNotFoundError(f"Input file not found in any of the expected locations: {possible_paths}")

        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in input file: {e}")
            raise
        except Exception as e:
            logger.error(f"Error loading input data: {e}")
            raise

    def _validate_input_data(self) -> None:
        """Validate the structure of input data."""
        if not isinstance(self.beam_data, dict):
            raise ValueError("Input data must be a dictionary")

        required_keys = ['metadata']
        missing_keys = [key for key in required_keys if key not in self.beam_data]
        if missing_keys:
            logger.warning(f"Missing recommended keys in input data: {missing_keys}")

    def _extract_parameters_from_input(self) -> None:
        """Extract design parameters from input data with validation."""
        try:
            data = self.beam_data
            metadata = data.get('metadata', {})
            beam_section = metadata.get('beam_data', {})

            # Extract design settings
            design_settings = beam_section.get('design_settings', {})

            # Torsion design consideration
            consider_torsion = design_settings.get('consider_torsion_design', True)
            self.perform_torsion_design = consider_torsion

            # Frame type with validation
            frame_type_str = design_settings.get('frame_type', 'ordinary').lower()
            try:
                self.frame_type = FrameType(frame_type_str)
            except ValueError:
                logger.warning(f"Invalid frame type '{frame_type_str}', using 'ordinary'")
                self.frame_type = FrameType.ORDINARY

            # Reduction factor
            self.phi_torsion = design_settings.get('reduction_factor_torsion',
                                                   design_settings.get('reduction_factor_shear',
                                                                       self.DEFAULT_PHI_TORSION))
            if not (0.1 <= self.phi_torsion <= 1.0):
                logger.warning(f"Invalid reduction factor {self.phi_torsion}, using default")
                self.phi_torsion = self.DEFAULT_PHI_TORSION

            # Material properties
            material_props = beam_section.get('material_properties', {})
            self.concrete_grade = material_props.get('concrete_grade', 'C28')
            self.steel_fy = material_props.get('main_steel_rebar_fy', 414)
            self.concrete_cover = material_props.get('concrete_cover', 40)

            # Floor groups
            self.floor_groups = beam_section.get('floor_groups', {})

            logger.info(f"Design parameters extracted: Grade={self.concrete_grade}, "
                        f"fy={self.steel_fy}, Cover={self.concrete_cover}")

        except Exception as e:
            logger.error(f"Error extracting parameters: {e}")
            raise

    def get_concrete_strength(self, grade: str) -> float:
        """Get concrete compressive strength with validation."""
        strength = self.CONCRETE_STRENGTHS.get(grade, 28)
        if grade not in self.CONCRETE_STRENGTHS:
            logger.warning(f"Unknown concrete grade '{grade}', using 28 MPa")
        return strength

    def _extract_forces_for_section(self, section_name: str, beam_data: Dict[str, Any]) -> Forces:
        """Extract forces for a specific section with multiple fallback strategies."""
        try:
            # Strategy 1: Look in forces dictionary
            if 'forces' in beam_data and section_name in beam_data['forces']:
                forces_dict = beam_data['forces'][section_name]
                return Forces(
                    torsion=forces_dict.get('max_torsion', 0),
                    axial=forces_dict.get('max_axial', 0)
                )

            # Strategy 2: Look directly in section data
            if section_name in beam_data:
                section_data = beam_data[section_name]
                return Forces(
                    torsion=section_data.get('max_torsion', 0),
                    axial=section_data.get('max_axial', 0)
                )

            # Strategy 3: Default values
            logger.warning(f"No forces found for section '{section_name}', using zeros")
            return Forces()

        except Exception as e:
            logger.error(f"Error extracting forces for {section_name}: {e}")
            return Forces()

    def _calculate_torsion_capacity(self, dimensions: BeamDimensions, fc_prime: float) -> float:
        """
        Calculate torsion capacity based on NSCP 2015 provisions.

        Args:
            dimensions: Beam dimensions
            fc_prime: Concrete compressive strength

        Returns:
            Torsion capacity in N⋅mm
        """
        # For solid rectangular sections, the torsion capacity is:
        # T_c = 0.33 * sqrt(f'c) * x^2 * y (in N⋅mm units)
        # where x and y are the shorter and longer dimensions

        x = min(dimensions.width, dimensions.height)
        y = max(dimensions.width, dimensions.height)

        # Convert to appropriate units and apply factor
        T_c = 0.33 * math.sqrt(fc_prime) * (x ** 2) * y

        return T_c

    def _calculate_required_stirrup_area(self, Tu: float, dimensions: BeamDimensions,
                                         fyv: float) -> Tuple[float, float]:
        """
        Calculate required stirrup area and spacing for torsion.

        Args:
            Tu: Ultimate torsion moment (N⋅mm)
            dimensions: Beam dimensions
            fyv: Yield strength of stirrups

        Returns:
            Tuple of (required area per unit length, recommended spacing)
        """
        # Simplified calculation for closed stirrups
        # Av/s = Tu / (fyv * d * alpha * beta)
        # where alpha and beta are factors dependent on section geometry

        d = dimensions.effective_depth

        # For rectangular sections, use simplified approach
        alpha = 0.85  # effectiveness factor
        beta = 0.85  # geometric factor

        # Required area per unit length
        Av_over_s = abs(Tu) / (fyv * d * alpha * beta)

        # Calculate spacing for given stirrup diameter (assume 10mm)
        stirrup_area = math.pi * (10 / 2) ** 2  # mm²
        spacing = stirrup_area / Av_over_s if Av_over_s > 0 else float('inf')

        # Apply practical limits
        spacing = max(self.MIN_STIRRUP_SPACING, min(spacing, self.MAX_STIRRUP_SPACING))

        return Av_over_s, spacing

    def _check_side_face_reinforcement(self, dimensions: BeamDimensions,
                                       Tu: float) -> Dict[str, Any]:
        """
        Check requirements for side face reinforcement.

        Args:
            dimensions: Beam dimensions
            Tu: Ultimate torsion moment

        Returns:
            Dictionary with SFA requirements
        """
        sfa_required = False
        min_area_per_face = 0

        if dimensions.height > self.SFA_HEIGHT_THRESHOLD:
            # Assume web is in tension if torsion is positive
            if Tu > 0:
                sfa_required = True
                min_area_per_face = self.SFA_MIN_RATIO * dimensions.width * dimensions.height

        return {
            'required': sfa_required,
            'min_area_per_face': min_area_per_face,
            'max_spacing': self.MAX_STIRRUP_SPACING,
            'height_threshold': self.SFA_HEIGHT_THRESHOLD,
            'justification': f"Height {dimensions.height}mm {'>' if dimensions.height > self.SFA_HEIGHT_THRESHOLD else '<='} {self.SFA_HEIGHT_THRESHOLD}mm"
        }

    def design_torsion_for_section(self, section_name: str, section_data: Dict[str, Any],
                                   beam_data: Dict[str, Any],
                                   dimensions: BeamDimensions) -> Dict[str, Any]:
        """
        Design torsion reinforcement for a specific section.

        Args:
            section_name: Name of the section (left, mid, right)
            section_data: Section-specific data
            beam_data: Complete beam data
            dimensions: Beam dimensions

        Returns:
            Dictionary with design results
        """
        try:
            # Extract forces
            forces = self._extract_forces_for_section(section_name, beam_data)
            forces_design = forces.to_design_units()

            # Material properties
            fc_prime = self.get_concrete_strength(self.concrete_grade)
            fyv = self.steel_fy

            # Calculate torsion capacity
            T_capacity = self._calculate_torsion_capacity(dimensions, fc_prime)
            T_factored = self.phi_torsion * T_capacity

            # Calculate capacity ratio
            capacity_ratio = abs(forces_design.torsion) / T_factored if T_factored > 0 else 0

            # Determine if reinforcement is required
            reinforcement_required = capacity_ratio > 1.0

            if reinforcement_required:
                # Calculate required reinforcement
                Av_over_s, spacing = self._calculate_required_stirrup_area(
                    forces_design.torsion, dimensions, fyv
                )
                stirrup_diameter = 10  # mm
                area_required = Av_over_s * spacing
            else:
                # Minimum reinforcement
                stirrup_diameter = 10
                spacing = self.MAX_STIRRUP_SPACING
                area_required = 0
                Av_over_s = 0

            # Check side face reinforcement
            sfa_info = self._check_side_face_reinforcement(dimensions, forces_design.torsion)

            # Prepare comprehensive results
            result = {
                'section': section_name,
                'dimensions': {
                    'width': dimensions.width,
                    'height': dimensions.height,
                    'length': dimensions.length,
                    'effective_depth': dimensions.effective_depth,
                    'cover': dimensions.cover
                },
                'forces': {
                    'torsion_kNm': forces.torsion,
                    'axial_kN': forces.axial,
                    'torsion_Nmm': forces_design.torsion,
                    'axial_N': forces_design.axial
                },
                'capacity': {
                    'concrete_torsion_capacity': T_capacity,
                    'factored_capacity': T_factored,
                    'capacity_ratio': capacity_ratio,
                    'reinforcement_required': reinforcement_required
                },
                'reinforcement': {
                    'stirrup_diameter': stirrup_diameter,
                    'spacing': spacing,
                    'area_required': area_required,
                    'area_per_unit_length': Av_over_s,
                    'side_face_reinforcement': sfa_info
                },
                'material_properties': {
                    'concrete_grade': self.concrete_grade,
                    'fc_prime': fc_prime,
                    'steel_fy': fyv,
                    'reduction_factor': self.phi_torsion
                }
            }

            logger.debug(f"Torsion design completed for {section_name}: "
                         f"Required={reinforcement_required}, Ratio={capacity_ratio:.2f}")

            return result

        except Exception as e:
            logger.error(f"Error in torsion design for {section_name}: {e}")
            return {
                'section': section_name,
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }

    def _extract_beam_dimensions(self, beam_data: Dict[str, Any]) -> BeamDimensions:
        """Extract beam dimensions with validation."""
        try:
            # Handle the actual data structure from your JSON
            dimensions_data = beam_data.get('dimensions', {})

            return BeamDimensions(
                width=dimensions_data.get('base', 300),  # 'base' is width in your data
                height=dimensions_data.get('height', 550),
                length=dimensions_data.get('length', 5000),
                cover=self.concrete_cover
            )
        except ValueError as e:
            logger.error(f"Invalid beam dimensions: {e}")
            # Return default dimensions
            return BeamDimensions(300, 550, 5000, self.concrete_cover)

    def design_all_beams(self) -> Dict[str, Any]:
        """
        Main function to perform torsion design for all beams.

        Returns:
            Dictionary with complete design results
        """
        if not self.beam_data:
            logger.error("No beam data available for design")
            return {}

        # Initialize results structure
        results = {
            'timestamp': datetime.now().isoformat(),
            'design_info': {
                'code': 'NSCP 2015',
                'software': 'STAADX ELEMENTS',
                'version': '1.0'
            },
            'parameters': {
                'frame_type': self.frame_type.value,
                'concrete_grade': self.concrete_grade,
                'steel_fy': self.steel_fy,
                'reduction_factor': self.phi_torsion,
                'concrete_cover': self.concrete_cover,
                'consider_torsion': self.perform_torsion_design
            },
            'summary': {
                'total_beams': 0,
                'beams_requiring_torsion_reinforcement': 0,
                'beams_with_side_face_reinforcement': 0
            },
            'beams': {}
        }

        if not self.perform_torsion_design:
            logger.info("Torsion design skipped as per configuration")
            results['summary']['skip_reason'] = 'Torsion design disabled in configuration'
            self.design_results = results
            return results

        logger.info("Starting torsion design for all beams")

        # Counters for summary
        total_beams = 0
        beams_with_torsion_reinforcement = 0
        beams_with_sfa = 0

        # Process each floor and beam group
        for floor_name, groups in self.floor_groups.items():
            results['beams'][floor_name] = {}

            for group_name, beams in groups.items():
                results['beams'][floor_name][group_name] = {}

                for beam_name, beam_data in beams.items():
                    total_beams += 1

                    try:
                        # Extract dimensions
                        dimensions = self._extract_beam_dimensions(beam_data)

                        # Design each section
                        sections_results = {}
                        beam_needs_torsion = False
                        beam_needs_sfa = False

                        # Process sections based on your data structure
                        for section in ['left', 'mid', 'right']:
                            # Create section data from forces
                            section_data = {}
                            if 'forces' in beam_data and section in beam_data['forces']:
                                section_data = beam_data['forces'][section]

                            design_result = self.design_torsion_for_section(
                                section, section_data, beam_data, dimensions
                            )
                            sections_results[section] = design_result

                            # Update counters
                            if (design_result.get('capacity', {}).get('reinforcement_required', False)):
                                beam_needs_torsion = True

                            if (design_result.get('reinforcement', {})
                                    .get('side_face_reinforcement', {}).get('required', False)):
                                beam_needs_sfa = True

                        # Update summary counters
                        if beam_needs_torsion:
                            beams_with_torsion_reinforcement += 1
                        if beam_needs_sfa:
                            beams_with_sfa += 1

                        results['beams'][floor_name][group_name][beam_name] = {
                            'beam_dimensions': {
                                'width': dimensions.width,
                                'height': dimensions.height,
                                'length': dimensions.length
                            },
                            'sections': sections_results,
                            'summary': {
                                'torsion_reinforcement_required': beam_needs_torsion,
                                'side_face_reinforcement_required': beam_needs_sfa
                            }
                        }

                    except Exception as e:
                        logger.error(f"Error processing beam {beam_name}: {e}")
                        results['beams'][floor_name][group_name][beam_name] = {
                            'error': str(e),
                            'timestamp': datetime.now().isoformat()
                        }

        # Update summary
        results['summary'].update({
            'total_beams': total_beams,
            'beams_requiring_torsion_reinforcement': beams_with_torsion_reinforcement,
            'beams_with_side_face_reinforcement': beams_with_sfa
        })

        self.design_results = results

        logger.info(f"Torsion design completed: {total_beams} beams processed, "
                    f"{beams_with_torsion_reinforcement} require torsion reinforcement, "
                    f"{beams_with_sfa} require side face reinforcement")

        return results

    def save_results(self) -> None:
        """Save design results to JSON file with robust error handling."""
        if not self.design_results:
            logger.warning("No design results to save")
            return

        try:
            # Determine save path
            script_dir = os.path.dirname(os.path.abspath(__file__))
            raw_data_dir = os.path.join(script_dir, '..', 'raw_data')

            # Create directory if it doesn't exist
            os.makedirs(raw_data_dir, exist_ok=True)

            save_path = os.path.join(raw_data_dir, self.output_filename)

            # Save with pretty formatting
            with open(save_path, 'w', encoding='utf-8') as f:
                json.dump(self.design_results, f, indent=2, ensure_ascii=False)

            logger.info(f"Results saved successfully to: {save_path}")

            # Log summary information
            summary = self.design_results.get('summary', {})
            logger.info(f"Design summary: {summary}")

        except Exception as e:
            logger.error(f"Error saving results: {e}")
            raise

    def print_summary(self) -> None:
        """Print a comprehensive summary of design results."""
        if not self.design_results:
            print("No design results available")
            return

        print("\n" + "=" * 80)
        print("TORSION DESIGN SUMMARY")
        print("=" * 80)

        # Parameters
        params = self.design_results.get('parameters', {})
        print(f"Design Code: NSCP 2015")
        print(f"Frame Type: {params.get('frame_type', 'N/A')}")
        print(f"Concrete Grade: {params.get('concrete_grade', 'N/A')}")
        print(f"Steel fy: {params.get('steel_fy', 'N/A')} MPa")
        print(f"Reduction Factor: {params.get('reduction_factor', 'N/A')}")
        print(f"Torsion Design: {'Enabled' if params.get('consider_torsion', False) else 'Disabled'}")

        # Summary statistics
        summary = self.design_results.get('summary', {})
        print(f"\nTotal Beams Analyzed: {summary.get('total_beams', 0)}")
        print(f"Beams Requiring Torsion Reinforcement: {summary.get('beams_requiring_torsion_reinforcement', 0)}")
        print(f"Beams Requiring Side Face Reinforcement: {summary.get('beams_with_side_face_reinforcement', 0)}")

        print("\n" + "=" * 80)


def main():
    """Main execution function with comprehensive error handling."""
    try:
        logger.info("Starting torsion design analysis")

        # Initialize designer
        designer = TorsionDesign()

        # Perform design
        results = designer.design_all_beams()

        # Print summary
        designer.print_summary()

        # Save results
        designer.save_results()

        logger.info("Torsion design analysis completed successfully")

    except Exception as e:
        logger.error(f"Fatal error in torsion design: {e}")
        raise


if __name__ == "__main__":
    main()