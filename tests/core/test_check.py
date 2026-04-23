from efi_conv.core import avefi, check


def test_analytic_work(input_path):
    schema_validator = check.get_schema_validator()
    sample_file = input_path("data_analytic_works.json")
    efi_records = avefi.load(sample_file)
    assert check.pass_checks(efi_records, schema_validator), (
        f"Failed to validate {sample_file}"
    )


def test_invalid_period(input_path):
    """Test that period expressions with invalid year order are caught."""
    schema_validator = check.get_schema_validator()

    # Load the existing test data and modify it to create an invalid period
    sample_file = input_path("data_analytic_works.json")
    efi_records = avefi.load(sample_file)

    # Modify the first record to have an invalid period
    if efi_records:
        original_record = efi_records[0]
        # Create a copy and modify the date to be invalid
        import copy

        invalid_record = copy.deepcopy(original_record)

        # Find the first event and change its date to an invalid period
        if invalid_record.has_event:
            invalid_record.has_event[0].has_date = "1976/1975"

        # Test that the invalid period is caught
        result = check.pass_checks(
            [invalid_record], schema_validator, remove_invalid=False
        )
        assert not result, "Expected validation to fail for invalid period"


def test_valid_period(input_path):
    """Test that valid period expressions pass validation."""
    schema_validator = check.get_schema_validator()

    # Load the existing test data which has valid periods like "1975/1976"
    sample_file = input_path("data_analytic_works.json")
    efi_records = avefi.load(sample_file)

    # Test that valid periods pass validation
    result = check.pass_checks(efi_records, schema_validator)
    assert result, "Expected validation to pass for valid period expressions"


def test_equal_period(input_path):
    """Test that period expressions with equal years are valid."""
    schema_validator = check.get_schema_validator()

    # Load the existing test data and modify it to create an equal period
    sample_file = input_path("data_analytic_works.json")
    efi_records = avefi.load(sample_file)

    # Modify the first record to have an equal period
    if efi_records:
        original_record = efi_records[0]
        # Create a copy and modify the date to be equal
        import copy

        equal_record = copy.deepcopy(original_record)

        # Find the first event and change its date to an equal period
        if equal_record.has_event:
            equal_record.has_event[0].has_date = "1975/1975"

        # Test that the equal period is valid
        result = check.pass_checks(
            [equal_record], schema_validator, remove_invalid=False
        )
        assert result, "Expected validation to pass for equal period"
