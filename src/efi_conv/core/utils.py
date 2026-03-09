from avefi_schema import model_pydantic_v2 as efi


def described_by_issuer(
        record: efi.MovingImageRecord, issuer: dict
) -> efi.DescriptionResource:
    """Return described_by entry matching ``issuer``.

    Get the DescriptionResource entry of ``record`` matching
    ``issuer`` if present and create it if not. Note that described_by
    is multivalued for WorkVariant records only. Therefore, ValueError
    will be raised for Manifestation or Item records that alreadey
    have a value for described_by that does not match ``issuer``.

    """
    if isinstance(record, efi.WorkVariant):
        for described_by in record.described_by or []:
            if described_by.has_issuer_id == issuer['has_issuer_id']:
                break
        else:
            record.described_by = [efi.DescriptionResource(**issuer)]
            described_by = record.described_by[0]
    else:
        if record.described_by:
            described_by = record.described_by
            if described_by.has_issuer_id != issuer['has_issuer_id']:
                raise ValueError(
                    f"Unexpected issuer information in record provided by"
                    f" issuer_id {issuer.has_issuer_id}: {described_by}")
        else:
            record.described_by = efi.DescriptionResource(**issuer)
            described_by = record.described_by
    return described_by
