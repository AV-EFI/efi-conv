from efi_conv.core import avefi, check


def test_analytic_work(input_path):
    schema_validator = check.get_schema_validator()
    sample_file = input_path("data_analytic_works.json")
    efi_records = avefi.load(sample_file)
    assert check.pass_checks(efi_records, schema_validator), (
        f"Failed to validate {sample_file}"
    )
