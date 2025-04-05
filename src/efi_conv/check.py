from collections import defaultdict
import json
import logging
import pathlib
import re
import sys
from typing import List

import appdirs
from avefi_schema import model as efi
import click
from jsonasobj2 import as_dict
from jsonschema.validators import validator_for
from jsonschema.exceptions import best_match
from linkml_runtime.loaders import json_loader
from linkml_runtime.utils.formatutils import remove_empty_items
import requests

from . import avefi
from .cli import cli_main


log = logging.getLogger(__name__)
SCHEMA_SOURCE = 'https://raw.githubusercontent.com/AV-EFI/av-efi-schema/main/project/jsonschema/avefi_schema/model.schema.json'
CACHE_DIR = pathlib.Path(appdirs.user_cache_dir(
    appname=__package__))
SCHEMA_FILE = CACHE_DIR / 'avefi_schema.json'


@cli_main.command()
@click.option(
    '--remove-invalid/--no-remove-invalid', '-r', default=False,
    help='Remove invalid records modifying EFI_FILE in place.')
@click.option(
    '--update-schema', '-u', is_flag=True, default=False,
    help='Fetch latest version of the AVefi schema from upstream repo.')
@click.argument('efi_file', type=click.Path(dir_okay=False, exists=True))
def check(efi_file, *, remove_invalid=False, update_schema=False):
    """Sanity check EFI_FILE and optionally remove invalid records."""
    schema_validator = get_schema_validator(update_schema=update_schema)
    efi_records = avefi.load(efi_file)
    old_count = len(efi_records)
    if not pass_checks(efi_records, schema_validator, remove_invalid=True):
        if remove_invalid:
            avefi.dump(efi_records, efi_file)
            log.info(
                f"Successfully removed {old_count-len(efi_records)} invalid"
                f" records")
        else:
            log.error(
                f"Found {old_count-len(efi_records)} invalid records"
                f" (no action taken)")
            sys.exit(1)
    else:
        log.info(f"All {old_count} records passed the checks successfully")


def get_schema_validator(update_schema=False):
    """Load AVefi JSON schema and initialise validator."""
    if update_schema:
        r = requests.get(SCHEMA_SOURCE)
        r.raise_for_status()
        schema = r.json()
        CACHE_DIR.mkdir(exist_ok=True)
        with SCHEMA_FILE.open('w') as f:
            json.dump(schema, f, indent=2, ensure_ascii=False)
    else:
        try:
            with SCHEMA_FILE.open() as f:
                schema = json.load(f)
        except FileNotFoundError:
            return get_schema_validator(update_schema=True)

    cls = validator_for(schema)
    cls.check_schema(schema)
    validator = cls(schema)
    return validator


def pass_checks(
        efi_records: List[efi.MovingImageRecord], schema_validator,
        remove_invalid=False) -> bool:
    """Check records against schema and additional rules.

    Validate against AVefi schema and check various additional rules
    like field length limits, required identifiers, resolvable
    references, etc.

    Note that this function may have obvious side effects on
    ``efi_records`` if ``remove_invalid`` is set to True.

    Parameters
    ----------
    efi_records : List[efi.MovingImageRecord]
        List of records in the AVefi schema.
    schema_validator
        Validator instance as returned by get_schema_validator().
    remove_invalid : bool
        Remove records from the list if they violate any of the rules.

    Returns
    -------
    bool
        True if all checks have passed successfully, False otherwise.

    """
    id_lookup = {}
    dependants_by_ref = defaultdict(list)
    all_was_fine = True

    for rec in efi_records.copy():
        error = best_match(schema_validator.iter_errors(
            remove_empty_items(rec)))
        if error is not None:
            raise error

        if has_invalid_value(rec):
            if all_was_fine:
                all_was_fine = False
            if remove_invalid:
                efi_records.remove(rec)
                continue
        if not rec.has_identifier:
            raise ValueError(f"has_identifier is missing in record: {rec}")
        record_ids = []
        for identifier in rec.has_identifier:
            record_id = HashableId(**as_dict(identifier))
            if record_id in id_lookup:
                raise ValueError(f"Identifier is not unique: {record_id}")
            record_ids.append(record_id)
            id_lookup[record_id] = (rec, record_ids)
        if isinstance(rec, efi.WorkVariant):
            link_attributes = ('is_part_of', 'is_variant_of')
        elif isinstance(rec, efi.Manifestation):
            # Ignore has_item here
            link_attributes = ('is_manifestation_of', 'same_as')
        elif isinstance(rec, efi.Item):
            link_attributes = ('is_item_of', 'is_copy_of', 'is_derivative_of')
        else:
            raise ValueError(
                f"Cannot handle {type(rec)} (record={rec})")
        for attr_name in link_attributes:
            attr = getattr(rec, attr_name)
            if attr is None:
                attr = []
            elif not isinstance(attr, list):
                attr = [attr]
            for identifier in attr:
                ref = HashableId(**as_dict(identifier))
                dependants_by_ref[ref].append(record_id)

    for ref in list(dependants_by_ref.keys()):
        if ref not in id_lookup and ref.category == 'avefi:LocalResource':
            log.error(f"Unresolvable reference: {ref.id}")
            if all_was_fine:
                all_was_fine = False
            if remove_invalid:
                purge_dependant_records(
                    ref, efi_records, id_lookup, dependants_by_ref)
    for record_id in list(id_lookup.keys()):
        if dangling_record(
                record_id, efi_records, id_lookup, dependants_by_ref,
                remove_dangling=remove_invalid):
            if all_was_fine:
                all_was_fine = False
    return all_was_fine


def purge_dependant_records(ref, record_list, id_lookup, dependants_by_ref):
    for record_id in dependants_by_ref[ref]:
        try:
            rec, ids = id_lookup[record_id]
        except KeyError:
            continue
        record_list.remove(rec)
        for record_id in ids:
            del id_lookup[record_id]
            log.error(f"Reference to removed record: {record_id.id}")
            purge_dependant_records(
                record_id, record_list, id_lookup, dependants_by_ref)


def dangling_record(
        record_id, record_list, id_lookup, dependants_by_ref,
        remove_dangling=False):
    """Return True if record has neither items nor a PID yet."""
    if record_id.category == 'avefi:LocalResource' \
       and record_id not in dependants_by_ref:
        rec, ids = id_lookup[record_id]
        if rec.category != 'avefi:Item' \
           and all(
               id_.category == 'avefi:LocalResource'
               and id_ not in dependants_by_ref
               for id_ in ids):
            log.error(
                f"No items associated with {rec.category} {record_id.id}")
            if remove_dangling:
                refs = []
                for attr_name in (
                        'is_manifestation_of', 'is_variant_of', 'is_part_of'):
                    ref = getattr(rec, attr_name, None)
                    if ref:
                        if isinstance(ref, list):
                            refs.extend(HashableId(**as_dict(r)) for r in ref)
                        else:
                            refs.append(HashableId(**as_dict(ref)))
                for id_ in ids:
                    del id_lookup[id_]
                record_list.remove(rec)
                for ref in refs:
                    ref_deps = dependants_by_ref[ref]
                    for id_ in ids:
                        if id_ in ref_deps:
                            ref_deps.remove(id_)
                    if not ref_deps:
                        del dependants_by_ref[ref]
                    dangling_record(
                        ref, record_list, id_lookup, dependants_by_ref,
                        remove_dangling=remove_dangling)
            return True
    return False


class HashableId:
    def __init__(self, category, id):
        self.category = category
        self.id = id
        self.name = f"{category}.{id}"

    def __eq__(self, other):
        return other.id == self.id and other.category == self.category

    def __hash__(self):
        return hash(self.name)

    def __str__(self):
        return self.name


def has_invalid_value(efi_record):
    def any_empty_has_name(elem_generator):
        if any([not elem.has_name for elem in elem_generator]):
            log.error(
                f"Empty has_name in {efi_record.has_identifier[0].id}")
            return True
        return False

    if exceeds_field_limit(efi_record):
        return True
    for event in efi_record.has_event:
        if has_invalid_date(efi_record):
            return True
        for activity in event.has_activity:
            if any_empty_has_name(activity.has_agent):
                return True
        if any_empty_has_name(event.located_in):
            return True
    if isinstance(efi_record, efi.WorkVariant):
        if any_empty_has_name(efi_record.has_genre):
            return True
        if any_empty_has_name(efi_record.has_subject):
            return True
    return False


def exceeds_field_limit(efi_record):
    titles = [efi_record.has_primary_title]
    titles.extend(efi_record.has_alternative_title)
    for title in titles:
        if len(title.has_name) > 250:
            log.error(
                f"Record {efi_record.has_identifier[0].id} violates limit of"
                f" 250 characters on title length: {title.has_name}")
            return True
    return False


def has_invalid_date(efi_record):
    for event in efi_record.has_event:
        if event.has_date \
           and not re.search(
               r'^-?([1-9][0-9]{3,}|0[0-9]{3})(-(0[1-9]|1[0-2])(-(0[1-9]|[12][0-9]|3[01]))?)?[?~]?(/-?([1-9][0-9]{3,}|0[0-9]{3})(-(0[1-9]|1[0-2])(-(0[1-9]|[12][0-9]|3[01]))?)?[?~]?)?$',
               event.has_date):
            log.error(
                f"Record {efi_record.has_identifier[0].id} has event(s) with"
                f" invalid value in has_date: {event.has_date}")
            return True
    return False
