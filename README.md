# 🏗️ RCBeamDesigner - Automated Reinforced Concrete Beam Design

<div align="center">

**Automate Your Structural Analysis Workflow**

*Developed by* **Engr. Lowrence Scott D. Gutierrez**  
[![LinkedIn](https://img.shields.io/badge/LinkedIn-Connect-blue?style=flat&logo=linkedin)](https://www.linkedin.com/in/lsdg)

---

### 📊 Repository Stats

![GitHub Views](https://komarev.com/ghpvc/?username=SC0L0W&label=Repository%20Views&color=0e75b6&style=flat)  
![GitHub Stars](https://img.shields.io/github/stars/SC0L0W/RCBeamDesigner?style=flat&color=yellow)  

---

**Transform hours of manual reinforced concrete beam design into seconds.**

</div>

---

## ✨ What Makes This Special

This intelligent Python-powered framework revolutionizes how structural engineers design reinforced concrete beams. Fully compliant with **NSCP 2015 standards**, it automatically processes complex beam designs for multiple floors and beam groups simultaneously—complete with detailed engineering reports, professional drawings, and reinforcement schedules—eliminating human error and saving valuable engineering time.

Whether you're designing residential buildings, commercial structures, or industrial facilities, this modular Python system seamlessly processes your beam data through an automated workflow, generating code-compliant designs with comprehensive verification, ductility checks for special moment frames, and professional documentation instantly.

---

## 🚀 Key Features

<table>
<tr>
<td width="50%">

### 🔄 **Multi-Level Batch Processing**
- Design multiple floors simultaneously
- Process beam groups hierarchically
- Handle dozens of beams in one execution
- Support for left, mid, and right sections

### 📋 **Intelligent Design System**
- Automatic bar size optimization
- Multi-layer reinforcement arrangement
- Spacing verification per ACI 318
- Doubly reinforced design when needed

</td>
<td width="50%">

### 🎯 **NSCP 2015 & ACI 318 Compliant**
- Ultimate strength design (USD) method
- Ductility requirements for seismic frames
- Special, intermediate, and ordinary frame types
- Comprehensive verification systems

### 🛡️ **Production-Ready Architecture**
- Modular Python OOP design
- JSON-based data persistence
- Robust error handling and validation
- Automatic fallback mechanisms

</td>
</tr>
</table>

---

## 📁 File Structure & Workflow

The system operates through a **modular 8-step processing pipeline**:

```
📂 beam_design_system/
│
├── 📥 inputs/
│   ├── user_inputs.py              #0 → Interactive data collection
│   │   └── BeamDataCollector class: Hierarchical beam input system
│   ├── material_properties.py      # Material definitions & constants
│   └── constants.py                # NSCP 2015 code factors
│
├── ⚙️ core/
│   ├── flexural_design.py          #2 → Main flexural calculations
│   │   └── FlexuralDesigner class: 2000+ lines of design logic
│   ├── shear_design.py             #3 → Shear reinforcement design
│   ├── torsion_design.py           #4 → Torsion analysis
│   └── beam_detailing.py           #5 → Reinforcement detailing
│
├── 📤 output/
│   ├── detailed_report_generator.py    #6 → PDF report generation
│   ├── summary_report_generator.py     #7 → CSV summaries
│   └── schedule_generator.py           #8 → Bar schedules
│
├── 🎯 main.py                      #1 → Main execution orchestrator
│
├── 💾 raw_data/                    # JSON processing data
│   ├── beam_data.json              (Step 0 output - User inputs)
│   ├── flexural_design_results.json    (Step 2 output - Design results)
│   ├── shear_design_results.json       (Step 3 output - Shear design)
│   └── torsion_design_results.json     (Step 4 output - Torsion)
│
└── 📊 output_data/                 # Final deliverables
    ├── detailed_drawing.dxf            (Step 5 output - CAD drawings)
    ├── professional_beam_design_report.pdf (Step 6 output - Reports)
    └── structural_design_summary.csv       (Step 7 output - Schedules)
```

---

## 🔄 Processing Pipeline

```
┌─────────────────────────────────────────────────────────────┐
│ STEP 0: Interactive Data Collection (user_inputs.py)       │
│ • Floor groups → Beam groups → Individual beams            │
│ • Dimensions, forces, materials per beam                   │
│ • Design settings (frame type, factors, preferences)       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 1: Main Execution (main.py)                           │
│ • Initialize FlexuralDesigner with beam_data.json          │
│ • Validate data structure                                  │
│ • Set material properties and design parameters            │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 2: Flexural Design (flexural_design.py)               │
│ • Design all sections (left/mid/right, top/bottom)         │
│ • Calculate required steel areas                           │
│ • Optimize bar combinations                                │
│ • Verify spacing & arrange multiple layers                 │
│ • Apply ductility requirements (special frames)            │
│ • Generate flexural_design_results.json                    │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 3: Shear Design (shear_design.py)                     │
│ • Calculate concrete shear capacity (Vc)                   │
│ • Determine required steel shear (Vs)                      │
│ • Design stirrup spacing and configuration                 │
│ • Generate shear_design_results.json                       │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 4: Torsion Design (torsion_design.py)                 │
│ • Check torsion threshold requirements                     │
│ • Calculate torsional reinforcement                        │
│ • Combine with shear reinforcement                         │
│ • Generate torsion_design_results.json                     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 5: Beam Detailing (beam_detailing.py)                 │
│ • Development length calculations                          │
│ • Generate DXF drawings with reinforcement layout          │
│ • Create detailed_drawing.dxf                              │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 6: Detailed Report (detailed_report_generator.py)     │
│ • Professional PDF with calculations                       │
│ • Charts, tables, and verification                         │
│ • Create professional_beam_design_report.pdf               │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 7: Summary Report (summary_report_generator.py)       │
│ • CSV export for spreadsheet analysis                      │
│ • Create structural_design_summary.csv                     │
└─────────────────────────────────────────────────────────────┘
                          ↓
┌─────────────────────────────────────────────────────────────┐
│ STEP 8: Schedule Generator (schedule_generator.py)         │
│ • Bar bending schedules                                    │
│ • Material quantity takeoff                                │
│ • Construction schedules                                   │
└─────────────────────────────────────────────────────────────┘
```

---

## 🔧 Prerequisites

### **System Requirements**
- ✅ **Python 3.8+** installed
- ✅ **Operating System:** Windows, macOS, or Linux

### **Required Python Libraries**
```bash
numpy>=1.21.0      # Numerical calculations
pandas>=1.3.0      # Data processing (future use)
json               # Built-in: Data serialization
math               # Built-in: Mathematical operations
typing             # Built-in: Type hints
datetime           # Built-in: Timestamps
```

### **Knowledge Prerequisites**
- ✅ Basic understanding of reinforced concrete design
- ✅ Familiarity with NSCP 2015 requirements
- ✅ Understanding of structural analysis output (moments, shears)

---

## 📖 Getting Started

### **Step 1: Clone the Repository**

```bash
# Clone via Git
git clone https://github.com/SC0L0W/RCBeamDesigner.git
cd RCBeamDesigner

# Or download as ZIP and extract
```

---

### **Step 2: Install Dependencies**

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# Install required packages
pip install numpy>=1.21.0
```

---

### **Step 3: Run Interactive Data Collection**

```bash
# Navigate to inputs folder
cd inputs

# Run the data collector
python user_inputs.py
```

#### **Interactive Input Flow:**

The system will guide you through a structured data collection process:

```
STRUCTURAL BEAM DATA COLLECTION
========================================

=== DESIGN SETTINGS ===
Frame Type Options:
1. Intermediate
2. Special
Select frame type (1-2): 2

Reduction Factor for Shear Options:
1. 0.75
2. 0.65
Select reduction factor for shear (1-2): 1

Lightweight Factor for Shear Options:
1. 1.00
2. 0.85
3. 0.75
Select lightweight factor for shear (1-3): 1

Reinforcement Type Options:
1. Pre-stressed
2. Non-Pre-stressed
Select reinforcement type (1-2): 2

Consider bending and axial in design? (yes/no): no

Enter stirrup spacing round off (default 5): 5

Consider torsion design in calculations? (yes/no): yes

=== MATERIAL PROPERTIES ===
Enter concrete grade (e.g., C28): C28
Enter main steel rebar fy (MPa): 415
Enter shear steel fy (MPa): 275
Enter concrete cover (mm): 40
Enter maximum aggregate size (mm): 25

=== REINFORCEMENT PARAMETERS ===
Enter main bar diameter range (min,max) in mm: 16,28
Enter stirrup bar diameter range (min,max) in mm: 10,12
Enter minimum spacing between bars (mm): 25
Enter maximum spacing between bars (mm): 300

=== FLOOR GROUP CONFIGURATION ===
Enter number of floor groups: 2
Enter name for floor group 1: 2F
Enter number of beam groups in floor group '2F': 1
Enter name for beam group 1 in floor group '2F': B1

Enter number of beams in beam group 'B1': 2
Enter beam number 1 in beam group 'B1': 101

--- Dimensions for Floor 2F, Beam Group B1, Beam 101 ---
Enter beam base/width (mm): 300
Enter beam height (mm): 500
Enter beam length (mm): 6000

=== BEAM FORCES - Floor 2F, Beam Group B1, Beam 101 ===

--- Forces for LEFT section (Floor 2F, Beam Group B1, Beam 101) ---
Enter maximum moment at bottom for left (kN·m): 85.5
Enter maximum moment at top for left (kN·m): 125.3
Enter maximum shear for left (kN): 95.2
Enter maximum axial force for left (kN): 0
Enter maximum torsion for left (kN·m): 0

--- Forces for MID section (Floor 2F, Beam Group B1, Beam 101) ---
Enter maximum moment at bottom for mid (kN·m): 145.8
Enter maximum moment at top for mid (kN·m): 0
Enter maximum shear for mid (kN): 0
Enter maximum axial force for mid (kN): 0
Enter maximum torsion for mid (kN·m): 0

--- Forces for RIGHT section (Floor 2F, Beam Group B1, Beam 101) ---
Enter maximum moment at bottom for right (kN·m): 88.2
Enter maximum moment at top for right (kN·m): 130.1
Enter maximum shear for right (kN): 92.8
Enter maximum axial force for right (kN): 0
Enter maximum torsion for right (kN·m): 0

[Repeat for all beams...]

================================================
DATA COLLECTION SUMMARY
================================================
Data automatically saved to ../raw_data/beam_data.json
File created successfully! Size: 4,523 bytes
```

---

### **Step 4: Run Flexural Design**

```bash
# Navigate to core folder
cd ../core

# Run flexural design
python flexural_design.py
```

#### **Expected Console Output:**

```
Starting beam design process...
Frame type: special

Processing floor: 2F
  Processing group: B1
    Processing beam: 101
      Beam dimensions: 300x500 mm (L=6000 mm)
      Designing section: left
        ✓ Section left designed (Bottom: 85.50 kNm, Top: 125.30 kNm)
      Designing section: mid
        ✓ Section mid designed (Bottom: 145.80 kNm, Top: 0.00 kNm)
      Designing section: right
        ✓ Section right designed (Bottom: 88.20 kNm, Top: 130.10 kNm)
      Applying special frame requirements...
      ✓ Special frame requirements applied successfully
    ✓ Beam 101 designed successfully

=== Design Summary ===
Total beams processed: 2/2
Section success rate: 100.0%

Design results saved successfully to: ../raw_data/flexural_design_results.json
```

---

### **Step 5: Review Generated Results**

Navigate to the `raw_data/` folder to review:

#### **📄 beam_data.json** (Input Data)
```json
{
  "timestamp": "2025-10-18T14:30:45.123456",
  "design_settings": {
    "frame_type": "special",
    "reduction_factor_shear": 0.75,
    "lightweight_factor_shear": 1.0,
    "reinforcement_type": "Non-Pre-stressed",
    "consider_bending_and_axial_design": false,
    "stirrup_spacing_round_off": 5,
    "consider_torsion_design": true
  },
  "material_properties": {
    "concrete_grade": "C28",
    "main_steel_rebar_fy": 415,
    "shear_steel_fy": 275,
    "concrete_cover": 40,
    "max_aggregate_size": 25
  },
  "reinforcement_parameters": {
    "main_bar_range": [16, 28],
    "stirrup_bar_range": [10, 12],
    "min_stirrup_spacing": 25,
    "max_stirrup_spacing": 300
  },
  "floor_groups": {
    "2F": {
      "B1": {
        "101": {
          "dimensions": {
            "base": 300,
            "height": 500,
            "length": 6000
          },
          "forces": {
            "left": {
              "max_moment_bottom": 85.5,
              "max_moment_top": 125.3,
              "max_shear": 95.2,
              "max_axial": 0,
              "max_torsion": 0
            },
            "mid": { /* ... */ },
            "right": { /* ... */ }
          }
        }
      }
    }
  }
}
```

#### **📄 flexural_design_results.json** (Design Output)
```json
{
  "metadata": {
    "version": "1.0",
    "design_parameters": {
      "Es": 200000,
      "max_steel_ratio": 0.025,
      "max_aggregate_size": 25,
      "phi_flexure": 0.9,
      "minimum_bars": 2
    },
    "material_properties": {
      "concrete_properties": {
        "grade": "C28",
        "total_beams_using": 2
      },
      "steel_properties": {
        "main_steel_fy": "415 MPa",
        "shear_steel_fy": "275 MPa"
      }
    },
    "design_summary": {
      "total_beams": 2,
      "total_sections": 12,
      "design_types": {
        "singly_reinforced": 12,
        "doubly_reinforced": 0
      },
      "spacing_issues": 0,
      "design_errors": 0
    }
  },
  "results": {
    "2F": {
      "B1": {
        "101": {
          "left": {
            "bottom": {
              "section": "left",
              "moment": 85.5,
              "effective_depth": 450,
              "neutral_axis_depth": 28.5,
              "strain_in_steel": 0.0044,
              "steel_yields": true,
              "As_required": 1245.8,
              "recommended_bars": {
                "bar_diameter": 20,
                "num_bars": 4,
                "total_area": 1256.6,
                "excess_percentage": 0.87,
                "efficiency_score": 98.5
              },
              "final_arrangement": {
                "layers": 1,
                "bars_per_layer": [4],
                "bar_diameter": 20,
                "spacing_ok": true,
                "actual_spacing": 35.5,
                "arrangement_type": "single_layer_equal_spacing"
              },
              "capacity_check": {
                "Mn": 95.2,
                "phi_Mn": 85.68,
                "capacity_ratio": 1.002,
                "passes": true
              },
              "design_status": "PASS"
            },
            "top": { /* similar structure */ }
          },
          "mid": { /* ... */ },
          "right": { /* ... */ },
          "frame_type": "special",
          "ductile_requirements": {
            "max_ast_all_zones": 1825.4,
            "ast_25_percent": 456.35,
            "bottom_left_right": 912.7,
            "top_left_right": 456.35
          }
        }
      }
    }
  }
}
```

---

## 🎓 Technical Deep Dive

### **Core Module: FlexuralDesigner Class**

The `flexural_design.py` module contains over **2000 lines** of production-ready code organized into logical sections:

#### **1. Initialization & Data Management**
```python
class FlexuralDesigner:
    def __init__(self, beam_data_file: str = None):
        self.beam_data = None
        self.design_results = {}
        self.Es = 200000  # Steel modulus (MPa)
        self.max_steel_ratio = 0.025
        self.standard_bar_sizes = [10, 12, 16, 20, 25, 28, 32, 36, 40]
```

**Key Methods:**
- `load_beam_data()` - Load JSON input data
- `_set_parameters_from_json()` - Extract material properties
- `validate_beam_data_structure()` - Validate input integrity
- `get_bars_in_range()` - Filter bar sizes by user-defined range

---

#### **2. Material Properties & Basic Calculations**

**Concrete Strength Extraction:**
```python
def extract_concrete_strength(self, concrete_grade: str) -> float:
    # Converts "C28" → 28.0 MPa
    grade_str = concrete_grade.strip().upper().replace('C', '')
    return float(grade_str)
```

**Beta Factor (Whitney Stress Block):**
```python
def calculate_beta(self, fc_prime: float) -> float:
    if fc_prime <= 28:
        return 0.85
    elif fc_prime <= 55:
        return max(0.65, 0.85 - 0.05 * (fc_prime - 28) / 7)
    else:
        return 0.65
```

**Balanced Steel Ratio:**
```python
def calculate_balanced_steel_ratio(self, fc_prime: float, fy: float) -> float:
    return (0.85 * fc_prime / fy) * (600 / (600 + fy))
```

**Minimum Steel Ratio (NSCP 2015 Section 422.3.2):**
```python
def calculate_min_steel_ratio(self, fc_prime: float, fy: float, 
                               b: float, d: float) -> float:
    rho_min1 = 0.25 * math.sqrt(fc_prime) / fy
    rho_min2 = 1.4 / fy
    return max(rho_min1, rho_min2)
```

**Effective Depth Calculation:**
```python
def calculate_effective_depth(self, height: float, cover: float, 
                               stirrup_dia: float, main_bar_dia: float) -> float:
    """Consider second bar layer with aggregate size spacing"""
    d1 = height - cover - stirrup_dia - main_bar_dia / 2
    d2 = d1 - self.max_aggregate_size / 2
    return max(d2, d1, 25)
```

---

#### **3. Reinforcement Calculations**

**Required Steel Area via Limit State:**
```python
def calculate_steel_ratio_limit_state(self, Mu: float, phi: float, 
                                       b: float, d: float, 
                                       fc_prime: float, fy: float) -> float:
    m = fy / (0.85 * fc_prime)
    Rn = Mu / (phi * b * d ** 2)
    
    argument = 1 - (2 * m * Rn) / fy
    if argument < 0:
        argument = 0  # Over-reinforced scenario
    
    rho = (1 / m) * (1 - math.sqrt(argument))
    
    # Clamp between min and max
    rho_min = self.calculate_min_steel_ratio(fc_prime, fy, b, d)
    rho_max = self.calculate_max_steel_ratio(rho_bal)
    
    return max(min(rho, rho_max), rho_min)
```

**Bar Combination Generator:**
```python
def calculate_bar_combinations(self, As_required: float, 
                                bar_range: Tuple[int, int], 
                                min_bars: int = 2) -> List[Dict]:
    """Generate all feasible bar combinations with efficiency scores"""
    
    available_bars = [dia for dia in self.standard_bar_sizes 
                      if bar_range[0] <= dia <= bar_range[1]]
    
    combinations = []
    for bar_dia in available_bars:
        bar_area = math.pi * (bar_dia / 2) ** 2
        num_bars_for_area = max(min_bars, math.ceil(As_required / bar_area))
        
        for num_bars in range(num_bars_for_area, 
                              min(num_bars_for_area + 3, 20)):
            actual_area = num_bars * bar_area
            if actual_area >= As_required:
                excess_percentage = ((actual_area - As_required) 
                                    / As_required) * 100
                
                if num_bars <= 12 and excess_percentage <= 50:
                    combinations.append({
                        'bar_diameter': bar_dia,
                        'num_bars': num_bars,
                        'total_area': actual_area,
                        'excess_percentage': excess_percentage,
                        'efficiency_score': self.calculate_efficiency_score(
                            excess_percentage, num_bars
                        )
                    })
    
    return sorted(combinations, key=lambda x: x['efficiency_score'], 
                  reverse=True)
```

**Efficiency Scoring Algorithm:**
```python
def calculate_efficiency_score(self, excess_percentage: float, 
                                num_bars: int) -> float:
    """Score combinations: higher = better (0-100 scale)"""
    
    optimal_bars = 4
    excess_penalty = excess_percentage / 2
    bar_penalty = abs(num_bars - optimal_bars)
    
    raw_score = 100 - excess_penalty - bar_penalty
    return max(0, min(100, raw_score))
```

---

#### **4. Spacing & Arrangement Verification (ACI 318)**

**Bar Spacing Checker:**
```python
def check_bar_spacing(self, b: float, cover: float, stirrup_dia: float,
                       bar_dia: float, num_bars: int, 
                       layers: int = 1) -> Dict:
    """
    ACI 318 minimum spacing requirement:
    s_min = max(25mm, bar_dia, (4/3) × max_aggregate_size)
    """
    
    min_spacing_req = max(25, bar_dia, 
                          (4/3) * self.max_aggregate_size)
    
    available_width = b - 2 * cover - 2 * stirrup_dia
    
    if layers == 1:
        if num_bars == 1:
            spacing_ok = bar_dia <= available_width
            actual_spacing = available_width
        else:
            total_bar_width = num_bars * bar_dia
            remaining_space = available_width - total_bar_width
            num_gaps = num_bars - 1
            actual_spacing = (remaining_space / num_gaps 
                             if num_gaps > 0 else 0)
            spacing_ok = actual_spacing >= min_spacing_req
        
        max_bars_single = int((available_width + min_spacing_req) / 
                              (bar_dia + min_spacing_req))
        
        return {
            'spacing_ok': spacing_ok,
            'actual_spacing': actual_spacing,
            'min_spacing_required': min_spacing_req,
            'max_bars_single_layer': max_bars_single,
            'requires_multiple_layers': num_bars > max_bars_single
        }
```

**Multi-Layer Arrangement:**
```python
def check_spacing_and_adjust_bars(self, section_result: Dict, 
                                   b: float, cover: float,
                                   stirrup_dia: float, 
                                   bar_range: Tuple[int, int]) -> Dict:
    """
    Automatically arrange bars in multiple layers if needed
    """
    
    recommended = section_result['recommended_bars']
    bar_dia = recommended['bar_diameter']
    num_bars = recommended['num_bars']
    
    spacing_check = self.check_bar_spacing(b, cover, stirrup_dia, 
                                            bar_dia, num_bars, layers=1)
    
    if spacing_check['spacing_ok']:
        # Single layer works
        section_result['final_arrangement'] = {
            'layers': 1,
            'bars_per_layer': [num_bars],
            'bar_diameter': bar_dia,
            'spacing_ok': True,
            'actual_spacing': spacing_check['actual_spacing'],
            'arrangement_type': 'single_layer_equal_spacing'
        }
    else:
        # Try two-layer solution
        if 'two_layer_solution' in spacing_check:
            two_layer = spacing_check['two_layer_solution']
            bars_in_layer = two_layer['bars_per_layer']
            
            section_result['final_arrangement'] = {
                'layers': 2,
                'bars_per_layer': [bars_in_layer, 
                                  num_bars - bars_in_layer],
                'spacing_ok': True,
                'arrangement_type': 'two_layer_equal_spacing'
            }
    
    return section_result
```

---

#### **5. Verification Systems**

**Capacity Verification:**
```python
def verify_capacity(self, As_required: float, phi: float, 
                    b: float, d: float, fc_prime: float, 
                    fy: float, Mu: float) -> Dict:
    """Verify φMn ≥ Mu"""
    
    a = (As_required * fy) / (0.85 * fc_prime * b)
    Mn = As_required * fy * (d - a / 2) / 1e6  # to kN·m
    phi_Mn = phi * Mn
    
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
```

**Strain Compatibility:**
```python
def verify_strain_compatibility(self, As_required: float, 
                                 b: float, d: float,
                                 fc_prime: float, fy: float) -> Dict:
    """Verify steel yields and strain compatibility"""
    
    a = (As_required * fy) / (0.85 * fc_prime * b)
    beta = self.calculate_beta(fc_prime)
    c = a / beta
    
    eps_cu = 0.003  # Ultimate concrete strain
    eps_s = eps_cu * (d - c) / c
    eps_y = fy / self.Es
    
    steel_yields = eps_s >= eps_y
    fs = fy if steel_yields else eps_s * self.Es
    
    return {
        'c': c,
        'eps_s': eps_s,
        'eps_y': eps_y,
        'fs': fs,
        'steel_yields': steel_yields,
        'strain_ratio': eps_s / eps_y
    }
```

**Ductility Requirements:**
```python
def verify_ductility_requirements(self, rho_required: float, 
                                   rho_bal: float,
                                   fc_prime: float, 
                                   fy: float, d: float) -> Dict:
    """ACI 318 ductility index verification"""
    
    eps_y = fy / self.Es
    eps_cu = 0.003
    ductility_index = eps_cu / eps_y
    
    rho_ratio = rho_required / rho_bal
    min_ductility_index = 3.0
    
    passes = (ductility_index >= min_ductility_index and 
              rho_ratio <= 0.75)
    
    return {
        'ductility_index': ductility_index,
        'rho_ratio': rho_ratio,
        'passes': passes
    }
```

---

#### **6. Ductility & Seismic Requirements**

**Special Moment Frame Requirements:**
```python
def calculate_ductile_requirements(self, 
                                    sections_results: Dict) -> Dict:
    """
    Calculate minimum steel requirements for special frames
    per NSCP 2015 seismic provisions
    """
    
    # Collect all steel areas
    all_ast_areas = []
    top_steel_areas = []
    
    for section in ['left', 'mid', 'right']:
        for location in ['top', 'bottom']:
            As_required = sections_results[section][location].get(
                'As_required', 0
            )
            if As_required > 0:
                all_ast_areas.append(As_required)
                if location == 'top':
                    top_steel_areas.append(As_required)
    
    max_ast_all_zones = max(all_ast_areas) if all_ast_areas else 0
    max_top_steel = max(top_steel_areas) if top_steel_areas else 0
    
    # Calculate minimum requirements
    ast_25_percent = 0.25 * max_ast_all_zones
    ast_50_percent_top = 0.50 * max_top_steel
    
    return {
        'max_ast_all_zones': max_ast_all_zones,
        'ast_25_percent': ast_25_percent,
        'bottom_left_right': max(ast_50_percent_top, ast_25_percent),
        'top_left_right': ast_25_percent,
        'bottom_mid': ast_25_percent,
        'top_mid': ast_25_percent
    }
```

**Apply Ductile Requirements:**
```python
def apply_ductile_requirements(self, section_result: Dict, 
                                section: str, location: str,
                                ductile_req: Dict, 
                                bar_range: Tuple[int, int]) -> Dict:
    """Adjust reinforcement based on ductile requirements"""
    
    # Determine requirement based on section and location
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
    
    # Check if ductile requirement controls
    current_As_required = section_result.get('As_required', 0)
    
    if ductile_requirement > current_As_required:
        # Ductile requirement controls
        section_result['As_required'] = ductile_requirement
        section_result['ductile_controlling'] = True
        section_result['note'] = f"Ductile requirement controls ({ductile_requirement:.0f} mm²)"
        
        # Regenerate bar combinations
        new_bars = self.calculate_bar_combinations(
            ductile_requirement, bar_range, min_bars=2
        )
        section_result['bar_combinations'] = new_bars
        section_result['recommended_bars'] = new_bars[0] if new_bars else None
    
    return section_result
```

---

### **Output Module: Professional Report Generator**

The `detailed_report_generator.py` module creates comprehensive PDF reports using **ReportLab** library with over **1000 lines** of advanced formatting:

#### **Key Features:**

**1. Professional Document Structure**
```python
class NumberedCanvas(canvas.Canvas):
    """Custom canvas with automatic page numbering"""
    
    def draw_page_number(self, page_num, total_pages):
        self.setFont("Helvetica", 9)
        self.drawRightString(letter[0] - 0.5 * inch, 0.5 * inch,
                             f"Page {page_num} of {total_pages}")
```

**2. Enhanced Styling System**
```python
# Custom paragraph styles
title_style = ParagraphStyle(
    'CustomTitle',
    fontSize=24,
    textColor=colors.HexColor('#1f4e79'),
    fontName='Helvetica-Bold',
    alignment=TA_CENTER
)

heading1_style = ParagraphStyle(
    'CustomHeading1',
    fontSize=18,
    textColor=colors.HexColor('#1f4e79'),
    borderWidth=1,
    borderColor=colors.HexColor('#5b9bd5'),
    backColor=colors.HexColor('#f2f2f2')
)
```

**3. Report Sections Generated:**

| Section | Description | Content |
|---------|-------------|---------|
| **Cover Page** | Professional title page | Project details, date, prepared by |
| **Executive Summary** | High-level overview | Design scope, methodology, key findings |
| **Table of Contents** | Navigation aid | Page references for all sections |
| **Design Criteria** | Standards and materials | NSCP 2015 requirements, material properties |
| **Flexural Design** | Detailed flexural analysis | Formulas, calculations, bar recommendations |
| **Shear Design** | Shear capacity verification | Concrete and steel contributions |
| **Torsion Design** | Torsional analysis | Threshold checks, reinforcement |
| **Reinforcement Summary** | Complete bar schedules | All beams with utilization ratios |
| **Design Verification** | Code compliance | Compliance checks, safety factors |
| **Performance Charts** | Visual analytics | Utilization graphs, capacity distributions |
| **Conclusions** | Design recommendations | Implementation guidelines |
| **Appendices** | Supporting information | Sample calculations, references |

**4. Advanced Table Formatting**
```python
def create_enhanced_table(data, col_widths, title=None, 
                          highlight_rows=None):
    """Professional table with alternating row colors"""
    
    table = Table(data, colWidths=col_widths, repeatRows=1)
    
    table_style = [
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#1f4e79')),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), 
         [colors.white, colors.HexColor('#f8f9fa')]),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black)
    ]
    
    table.setStyle(TableStyle(table_style))
    return table
```

**5. Performance Visualization**
```python
def create_performance_charts():
    """Generate matplotlib charts for PDF"""
    
    fig, ((ax1, ax2), (ax3, ax4)) = plt.subplots(2, 2, figsize=(12, 10))
    
    # Chart 1: Reinforcement Utilization Bar Chart
    ax1.bar(sections, utilization, color=['#1f4e79', '#5b9bd5'])
    ax1.set_title('Average Reinforcement Utilization')
    
    # Chart 2: Capacity Distribution Pie Chart
    ax2.pie(counts, labels=capacities, autopct='%1.1f%%')
    ax2.set_title('Design Capacity Distribution')
    
    # Chart 3: Moment vs Capacity Comparison
    ax3.bar(x - width/2, applied_moments, width, label='Applied')
    ax3.bar(x + width/2, capacity_moments, width, label='Capacity')
    
    # Chart 4: Shear Force Distribution Line Plot
    ax4.plot(positions, avg_shear, marker='o', linewidth=3)
    
    # Save to buffer and embed in PDF
    chart_buffer = io.BytesIO()
    plt.savefig(chart_buffer, format='png', dpi=300)
    chart_image = Image(chart_buffer, width=7*inch, height=5.5*inch)
    elements.append(chart_image)
```

**6. Formula Documentation**
```python
flexural_formulas = """
<b>Key Design Equations:</b><br/><br/>

<b>1. Minimum Reinforcement Area:</b><br/>
A<sub>s,min</sub> = max {0.25√f'<sub>c</sub> × b<sub>w</sub> × d / f<sub>y</sub>, 
                      1.4 × b<sub>w</sub> × d / f<sub>y</sub>}<br/><br/>

<b>2. Nominal Moment Capacity:</b><br/>
M<sub>n</sub> = A<sub>s</sub> × f<sub>y</sub> × (d - a/2)<br/><br/>

<b>3. Design Moment Capacity:</b><br/>
φM<sub>n</sub> ≥ M<sub>u</sub> (where φ = 0.90)
"""
elements.append(Paragraph(flexural_formulas, formula_style))
```

**7. Sample PDF Output Structure:**
```
╔══════════════════════════════════════════════════════════╗
║  STRUCTURAL DESIGN REPORT                                ║
║  Comprehensive Beam Design Analysis                      ║
║  ─────────────────────────────────────────────────────  ║
║  Project: 3 Storey Residential Building                 ║
║  Design Code: NSCP 2015                                  ║
║  Date: October 18, 2025                                  ║
╚══════════════════════════════════════════════════════════╝

═══════════════════════════════════════════════════════════
EXECUTIVE SUMMARY
═══════════════════════════════════════════════════════════

This comprehensive structural design report presents...

═══════════════════════════════════════════════════════════
FLEXURAL DESIGN ANALYSIS
═══════════════════════════════════════════════════════════

3.1 Design Methodology
─────────────────────────────────────────────────────────

3.2 Design Formulas
┌───────────────────────────────────────────────────────┐
│ Key Design Equations:                                 │
│                                                       │
│ 1. Minimum Reinforcement Area:                       │
│    As,min = max {0.25√f'c × bw × d / fy,            │
│                  1.4 × bw × d / fy}                  │
└───────────────────────────────────────────────────────┘

3.3 Design Results
─────────────────────────────────────────────────────────

Floor: 2F
Group: B1
Beam 101 - Design Summary

┌────────┬──────────┬────────────┬──────────────┬──────────┬─────────┐
│Section │ Moment   │ Required   │ Provided     │ Capacity │ Status  │
│        │ (kN⋅m)   │ As (mm²)   │ Reinforcement│  Check   │         │
├────────┼──────────┼────────────┼──────────────┼──────────┼─────────┤
│ LEFT   │ 85.50    │ 1245.8     │ 4 × ⌀20mm   │ 1.01     │ ✓ ADEQUATE│
│ (BOTTOM)                                                              │
├────────┼──────────┼────────────┼──────────────┼──────────┼─────────┤
│ LEFT   │ 125.30   │ 1825.4     │ 6 × ⌀20mm   │ 1.04     │ ✓ ADEQUATE│
│ (TOP)                                                                 │
└────────┴──────────┴────────────┴──────────────┴──────────┴─────────┘

[Performance Charts]
[Verification Tables]
[Conclusions and Recommendations]

                                                Page 15 of 25
```

**8. Report Generation Workflow:**
```python
class ReportGenerator:
    def __init__(self, output_dir, 
                 filename="professional_beam_design_report.pdf"):
        self.output_dir = output_dir
        self.filename = filename
        self.report_path = os.path.join(self.output_dir, self.filename)
        os.makedirs(self.output_dir, exist_ok=True)
    
    def generate(self):
        # Load all JSON results
        flexural_data = self.load_json('flexural_design_results.json')
        shear_data = self.load_json('shear_design_results.json')
        torsion_data = self.load_json('torsion_design_output.json')
        
        # Build report sections
        self.add_cover_page()
        self.add_executive_summary()
        self.add_flexural_design_section()
        self.add_shear_design_section()
        self.add_torsion_design_section()
        self.add_reinforcement_summary()
        self.add_design_verification()
        self.add_conclusions()
        self.add_appendices()
        
        # Generate PDF
        doc.build(elements, canvasmaker=NumberedCanvas)
```

---

## 📊 Complete Output Package

After running all modules, you receive a comprehensive set of deliverables:

### **1. JSON Data Files** (`raw_data/`)

**beam_data.json** - Complete input data
```json
{
  "timestamp": "2025-10-18T14:30:45.123456",
  "design_settings": { "frame_type": "special", ... },
  "material_properties": { "concrete_grade": "C28", ... },
  "floor_groups": { "2F": { "B1": { "101": {...} } } }
}
```

**flexural_design_results.json** - Design calculations
```json
{
  "metadata": {
    "design_parameters": { "Es": 200000, ... },
    "design_summary": { "total_beams": 12, ... }
  },
  "results": {
    "2F": {
      "B1": {
        "101": {
          "left": {
            "bottom": {
              "As_required": 1245.8,
              "recommended_bars": { "num_bars": 4, "bar_diameter": 20 },
              "capacity_check": { "passes": true, "capacity_ratio": 1.01 }
            }
          }
        }
      }
    }
  }
}
```

### **2. CAD Drawing** (`output_data/`)

**detailed_drawing.dxf** - AutoCAD compatible
- Beam elevation views
- Reinforcement details
- Section cuts
- Dimension annotations

### **3. Professional Report** (`output_data/`)

**professional_beam_design_report.pdf** - 20-30 pages
- Cover page with project details
- Executive summary
- Detailed calculations with formulas
- Professional tables and charts
- Code compliance verification
- Conclusions and recommendations
- Appendices with references

### **4. Summary Spreadsheet** (`output_data/`)

**structural_design_summary.csv** - Excel compatible
```csv
Floor,Beam,Section,Location,Moment_kNm,As_required_mm2,Provided_bars,Status
2F,B1-101,Left,Bottom,85.5,1245.8,4-⌀20mm,PASS
2F,B1-101,Left,Top,125.3,1825.4,6-⌀20mm,PASS
...
```

---

##
