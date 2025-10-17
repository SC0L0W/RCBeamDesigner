import os
from core.flexural_design import FlexuralDesigner


def run_user_inputs():
    """Run user_inputs.py to generate JSON data in raw_data/ folder."""
    try:
        import inputs.user_inputs as user_inputs_module
        user_inputs_module.main()
        return True
    except ImportError:
        print("Failed to import inputs.user_inputs. Ensure the file exists and is importable.")
        return False
    except AttributeError:
        print("The 'main()' function was not found in inputs.user_inputs.")
        return False
    except Exception as e:
        print(f"Error running user_inputs.py: {e}")
        return False

def get_latest_data_file():
    raw_data_dir = "raw_data"
    files = [f for f in os.listdir(raw_data_dir) if f.endswith('.json')]
    if not files:
        print("No JSON files found in 'raw_data/'.")
        return None
    files.sort(reverse=True)
    return os.path.join(raw_data_dir, files[0])

def main():
    print("Starting user input collection...")
    success = run_user_inputs()
    if not success:
        print("User input collection failed. Exiting.")
        return

    filename = get_latest_data_file()
    if not filename:
        print("No data file found after user input.")
        return
    print(f"Loading data from: {filename}")

    # Load JSON data into FlexuralDesigner
    designer = FlexuralDesigner()
    try:
        designer.load_beam_data(filename)
    except Exception as e:
        print(f"Error loading JSON data: {e}")
        return

    # Run the flexural design
    print("Running the flexural design process...")
    designer.design_all_beams()
    designer.save_design_results()


if __name__ == "__main__":
    main()