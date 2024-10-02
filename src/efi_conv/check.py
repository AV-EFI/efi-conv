from collections import defaultdict
import logging
import re
from typing import List

from avefi_schema import model as efi
from jsonasobj2 import as_dict
from linkml_runtime.loaders import json_loader


log = logging.getLogger(__name__)


def pass_checks(
        efi_records: List[efi.MovingImageRecord],
        remove_invalid=False) -> bool:
    id_lookup = {}
    dependants_by_ref = defaultdict(list)
    all_was_fine = True

    for rec in efi_records.copy():
        if exceeds_field_limit(rec) or has_invalid_date(rec):
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
