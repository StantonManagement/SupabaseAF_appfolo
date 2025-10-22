import re


def clean_record(record):
    """Convert numeric strings to proper int/float, handling commas"""
    cleaned = {}
    for key, value in record.items():
        if value is None or value == "":
            cleaned[key] = value
        elif isinstance(value, str):
            # Remove commas and check if it's a number
            cleaned_value = value.replace(",", "").strip()

            # Check if it's an integer
            if re.match(r"^-?\d+$", cleaned_value):
                cleaned[key] = int(cleaned_value)
            # Check if it's a float/decimal
            elif re.match(r"^-?\d+\.\d+$", cleaned_value):
                cleaned[key] = float(cleaned_value)
            else:
                # Keep as string
                cleaned[key] = value
        else:
            # Already a number or other type
            cleaned[key] = value

    return cleaned
