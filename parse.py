import json
import re

def parse_formatted_torque_file(file_path):
    torque_data = {}
    current_material = "ASTM_A36_Steel"  # Set based on file name or header
    torque_data[current_material] = {"fsu_ksi": 34.8, "engagements": []}

    current_eng = None

    # Regex for: Length of Thread Engagement (in) = 0.0625 = 1/16
    eng_pattern = r"Length of Thread Engagement\s*\(in\)\s*=\s*([\d\.]+)\s*=\s*([\d/]+)"

    with open(file_path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # 1. Check for new Engagement Header
        eng_match = re.search(eng_pattern, line)
        if eng_match:
            current_eng = {
                "in": float(eng_match.group(1)),
                "frac": eng_match.group(2),
                "data": []
            }
            torque_data[current_material]["engagements"].append(current_eng)
            continue

        # 2. Skip other header lines
        if "ksi" in line or "NOT TO BE USED" in line or "Fastener Size" in line:
            continue

        # 3. Parse Data Rows
        # Split from the right to get exactly 3 numeric values
        parts = line.rsplit(None, 3)
        if len(parts) == 4:
            try:
                row = {
                    "s": parts[0],             # Fastener size (everything else)
                    "p": float(parts[1]),     # Pullout Load
                    "a": float(parts[2]),     # Assembly Torque
                    "t": float(parts[3])      # 100% Torque
                }
                if current_eng is not None:
                    current_eng["data"].append(row)
            except ValueError:
                # Skips footer text like "NASA/TM—2017-219475 9"
                continue

    return torque_data

# Run and Save
result = parse_formatted_torque_file("ASTM A36 Steel.txt")
with open("torque_condensed.json", "w") as f:
    json.dump(result, f)

print("Extraction complete. JSON saved to torque_condensed.json")