import copy
import logging
import os
import re
from typing import List

from avefi_schema import model as efi
from xsdata.formats.dataclass.parsers import XmlParser

from .generated import ntm_metadata_schema_basic_v_2_5 as ntm
from .generated import ntm_metadata_schema_v_2_5


ROOT_CLASS = ntm_metadata_schema_v_2_5.Resource
log = logging.getLogger(__name__)
parser = XmlParser()


def efi_import(input_file) -> List[efi.MovingImageRecord]:
    efi_records = []
    input = parser.parse(input_file, ROOT_CLASS)
    # Use input.identifier once we have complete iwf schema
    source_key = re.search(
        r'clip(\d+)\.xml', os.path.basename(input_file)).groups()[0]

    # work
    titles = input.titles.title
    primary_title = None
    alternative_titles = []
    for title in titles:
        if title.title_type is None:
            if primary_title:
                raise RuntimeError(f"Cannot determine primary title: {titles}")
            primary_title = make_title(
                title, efi.TitleTypeEnum('PreferredTitle'))
        elif title.title_type == ntm.TitleType.ALTERNATIVE_TITLE:
            alternative_titles.append(
                make_title(title, efi.TitleTypeEnum('AlternativeTitle')))
        else:
            raise RuntimeError(f"No mapping specified for title type: {title}")
    work = efi.WorkVariant(
        type=efi.WorkVariantTypeEnum('Monographic'),
        has_primary_title=primary_title,
        has_alternative_title=alternative_titles)
    production_year = input.production_year
    # Todo: Use iwf_production_year when we have the complete schema
    # if not production_year:
    #     raise RuntimeError(f"No production year")
    event = efi.ProductionEvent(has_date=production_year)
    work.has_event.append(event)
    producers = []
    for c in input.creators.creator:
        if not c.creator_name:
            raise ValueError(f"Missing creator_name for {c}")
        agent = efi.Agent(
            type=efi.AgentTypeEnum('Person'), has_name=c.creator_name)
        if c.name_identifier:
            raise RuntimeError(f"Cannot handle name_identifier for {c}")
        producers.append(agent)
    if producers:
        event.has_activity.append(
            efi.ProducingActivity(
                type=efi.ProducingActivityTypeEnum('Producer'),
                has_agent=producers))
    production_companies = []
    for p in input.producers.producer:
        if not p.producer_name:
            raise ValueError(f"Missing producer_name for {p}")
        agent = efi.Agent(
            type=efi.AgentTypeEnum('CorporateBody'), has_name=p.producer_name)
        if p.name_identifier:
            raise RuntimeError(f"Cannot handle name_identifier for {p}")
        production_companies.append(agent)
    if production_companies:
        event.has_activity.append(
            efi.ProducingActivity(
                type=efi.ProducingActivityTypeEnum('ProductionCompany'),
                has_agent=production_companies))
    if input.genre.value:
        work.has_genre.append(efi.Genre(has_name=input.genre.value))
    # SubjectAreaTYpes
    # contributors
    if input.doi:
        work.same_as.append(efi.DOIResource(id=input.doi))
    identifiers = input.alternate_identifiers
    if identifiers:
        for id in identifiers.alternate_identifier:
            if id.alternate_identifier_type != "EIDR":
                raise RuntimeError(f"Cannot handle identifier_type: {id}")
            work.same_as.append(efi.EIDRResource(id=id.value))
    for subject_area in input.subject_areas.subject_area:
        if subject_area.value == "Arts and Media":
            keywords = ["Arts", "Media"]
        else:
            keywords = subject_area.value.split("/")
        for k in keywords:
            work.has_subject.append(
                efi.Subject(
                    has_name=k,
                    same_as=[
                        efi.GNDResource(
                            id=subject_area_to_gnd_mapping[k])
                    ]))
    for k in input.keywords.keyword:
        work.has_subject.append(efi.Subject(has_name=k.value))
    work_id = efi.LocalResource(id=f"{source_key}_work")
    work.has_identifier.append(work_id)
    work.has_source_key.append(source_key)
    efi_records.append(work)

    # manifestation
    manifestation_title = copy.deepcopy(work.has_primary_title)
    manifestation_title.type = efi.TitleTypeEnum('TitleProper')
    manifestation = efi.Manifestation(
        is_manifestation_of=[work_id],
        has_primary_title=manifestation_title)
    if (
            manifestation.has_primary_title.type
            == efi.TitleTypeEnum('PreferredTitle')):
        manifestation.has_primary_title.type = efi.TitleTypeEnum('TitleProper')
    for description in input.descriptions.description:
        # Recon with <br/> elements accepted by the NTM schema
        manifestation.has_note.append(
            "\n".join(
                [
                    text
                    for text in description.content
                    if isinstance(text, str)
                ]))
    if input.publication_year or input.publishers.publisher:
        publication = efi.PublicationEvent(
            type=efi.PublicationEventTypeEnum('ReleaseEvent'))
        manifestation.has_event.append(publication)
        publishers = []
        for p in input.publishers.publisher:
            agent = efi.Agent(
                type=efi.AgentTypeEnum('CorporateBody'),
                has_name=p.publisher_name)
            if p.name_identifier:
                raise RuntimeError(f"What to do about identifier: {p}")
            publishers.append(agent)
        if publishers:
            publication.has_activity.append(
                efi.ManifestationActivity(
                    type=efi.ManifestationActivityTypeEnum('Publisher'),
                    has_agent=publishers))
        if input.publication_year:
            publication.has_date = str(input.publication_year)
    if input.language:
        if input.language == "qot":
            manifestation.has_sound_type = efi.SoundTypeEnum('Sound')
            # Todo: should in_language.usage == NoDialogue?
        elif input.language == "qno":
            manifestation.has_sound_type = efi.SoundTypeEnum('Silent')
        else:
            manifestation.in_language = efi.Language(
                code=input.language,
                usage=efi.LanguageUsageEnum.SpokenLanguage)
    # Todo: format
    if input.size:
        match = re.search(r"^(\d+) *(\w+)$", input.size)
        if match is None:
            raise RuntimeError(f"No idea how to parse size={input.size}")
        value, unit = match.groups()
        manifestation.has_extent = efi.Extent(
            has_value=value, has_unit=size_mapping[unit])
    if input.duration:
        duration_value = re.sub(
            r"^(\d\d):(\d\d):(\d\d):\d\d$", 'PT\1H\2M\3S', input.duration)
        match = re.search(r"^(\d\d):(\d\d):(\d\d):\d\d$", input.duration)
        if match is None:
            raise RuntimeError(
                f"No idea how to parse duration={input.duration}")
        duration_str = ''
        for val, suffix in zip(match.groups(), ('H', 'M', 'S')):
            i = int(val)
            if i or (not duration_str and suffix == 'S'):
                duration_str += f"{str(i)}{suffix}"
        duration_str = f"PT{duration_str}"
        manifestation.has_duration = efi.Duration(
            has_value=duration_str)
    manifestation_id = efi.LocalResource(id=f"{source_key}_manifestation")
    manifestation.has_identifier.append(manifestation_id)
    manifestation.has_source_key.append(source_key)
    efi_records.append(manifestation)

    # item
    item = efi.Item(
        is_item_of=manifestation_id,
        has_primary_title=copy.deepcopy(manifestation.has_primary_title))
    item_id = efi.LocalResource(id=f"{source_key}_item")
    item.has_identifier.append(item_id)
    item.has_source_key.append(source_key)
    efi_records.append(item)
    return efi_records


def make_title(input_title, title_type: efi.TitleTypeEnum) -> efi.Title:
    display_title = input_title.value.strip()
    result = efi.Title(type=title_type, has_name=display_title)
    first, rest = display_title.split(maxsplit=1)
    if first.lower() in articles[input_title.language]:
        result.has_ordering_name = rest
        log.warning(
            f"Dropped {first} in ordering name for title: {display_title}")
    return result


articles = {
    'eng': ['a', 'an', 'the'],
    'ger': ['das', 'der', 'die', 'ein', 'eine']
}


size_mapping = {
    "GB": efi.UnitEnum.GigaByte,
    "MB": efi.UnitEnum.MegaByte,
}


subject_area_to_gnd_mapping = {
    "Architecture": "4002851-3",
    "Arts": "4114333-4",
    # Arts und Media sind im NTM-Schema zusammengefasst
    "Media": "4169187-8",
    "Chemistry": "4009816-3",
    "Computer Science": "4026894-9",
    "Earth Sciences": "4020288-4",
    "Economics": "4066399-1",
    # Economics und Social Sciences sind im NTM-Schema zusammengefasst
    "Social Sciences": "4055916-6",
    "Educational Science": "4044302-4",
    "Engineering": "4137304-2",
    "Environmental Sciences": "4137364-9",
    # Environmental Sciences und Ecology sind im NTM-Schema zusammengefasst
    "Ecology": "4043207-5",
    "Ethnology": "4078931-7",
    "History": "4020517-4",
    "Horticulture": "4019294-5",
    "Information Science": "4128313-2",
    "Law": "4048737-4",
    "Life Sciences": "4129772-6",
    "Linguistics": "4074250-7",
    "Literature Studies": "4036034-9",
    "Mathematics": "4037944-9",
    "Medicine": "4038243-6",
    "Philosophy": "4045791-6",
    "Physics": "4045956-1",
    "Psychology": "4047704-6",
    "Sports Science": "4056442-3",
    "Study of Religions": "4049426-3",
}
