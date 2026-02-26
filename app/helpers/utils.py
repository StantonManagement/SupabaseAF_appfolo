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


def transform_property_to_building(record):
    """
    Transform property_group_directory data to AF_Buildings schema.
    Maps AppFolio property fields to the AF_Buildings table structure.
    """
    return {
        # Property fields from property_group_directory
        "PropertyName": record.get("property_name"),
        "PropertyAddress": record.get("property_address"),
        "PropertyCity": record.get("property_city"),
        "PropertyState": record.get("property_state"),
        "PropertyId": record.get("property_id"),
        "PropertyStreet1": record.get("property_street"),
        "PropertyStreet2": record.get("property_street2"),
        "PropertyZip": record.get("property_zip"),
        "PropertyCounty": record.get("property_county"),
        "PropertyLegacyStreet1": record.get("property_legacy_street1"),
        "Property": record.get("property"),
        # Portfolio/Group fields
        "PropertyGroupName": record.get("property_group_name"),
        "PropertyGroupId": record.get("property_group_id"),
        "Portfolio": record.get("portfolio_id"),  # Portfolio ID is an integer
        "PortfolioId": record.get("portfolio_id"),  # Same as Portfolio
        # Building fields - set to None since property_group_directory doesn't have these
        "BuildingName": None,
        "BuildingId": None,
        "BuildingAddress": None,
        "BuildingStreet1": None,
        "BuildingStreet2": None,
        "BuildingCity": None,
        "BuildingState": None,
        "BuildingZip": None,
        "Building": None,
        # Additional fields - set to None
        "Units": None,
        "SqFt": None,
        "YearBuilt": None,
        "PropertyType": None,
        "BuildingType": None,
        "Amenities": None,
        "Description": None,
        "MarketRent": None,
        "ManagementFeePercent": None,
        "ManagementFlatFee": None,
        "MinimumFee": None,
        "MaximumFee": None,
        "PropertyCreatedOn": None,
        "PropertyCreatedBy": None,
        # Metadata
        "appfolio_collection": "property_group_directory",
    }
