from collections import defaultdict
import copy
import logging
import re

from avefi_schema import model_pydantic_v2 as efi
from xsdata.formats.dataclass.parsers import XmlParser

from ..core.settings import settings
from ..core.utils import described_by_issuer
from .generated.ntm_4_avefi import ntm_4_av_efi as ntm
from .generated.ntm_4_avefi import ntm_4_av_efi_schema as ntm_main

ROOT_CLASS = ntm_main.Resource
log = logging.getLogger(__name__)
parser = XmlParser()
ISSUER_INFO = {
    "has_issuer_id": "https://w3id.org/isil/DE-89",
    "has_issuer_name": "Technische Informationsbibliothek (TIB)",
}
CORPORATE_BODY_FLAG_WORDS = ["gesellschaft", "gmbh", "institut", "trickstudio"]


def efi_import(input_file) -> list[efi.MovingImageRecord]:
    input = read_input(input_file)
    return map_to_efi(input)


def read_input(input_file) -> ROOT_CLASS:
    return parser.parse(input_file, ROOT_CLASS)


def map_to_efi(input: ROOT_CLASS) -> list[efi.MovingImageRecord]:
    efi_records = []
    source_key = str(input.identifier)

    # work
    titles = input.titles.title
    primary_title, alternative_titles = process_titles(titles)
    work = efi.WorkVariant(
        type=efi.WorkVariantTypeEnum("Monographic"),
        has_primary_title=primary_title,
        has_alternative_title=alternative_titles,
    )
    production_year = get_iso_date(
        str(input.production_year), str(input.iwf_production_year)
    )
    if production_year:
        if (
            input.production_year
            and input.iwf_production_year
            and input.production_year not in input.iwf_production_year
        ):
            log.warning(
                f"Contradicting values:"
                f" productionYear={input.production_year},"
                f" iwfProductionYear={input.iwf_production_year}"
            )
    else:
        log.warning("No production year")
    event = efi.ProductionEvent(has_date=production_year)
    work.has_event.append(event)
    producers = []
    for c in input.creators.creator if input.creators else []:
        if not c.creator_name:
            continue
        agent = efi.Agent(
            type=efi.AgentTypeEnum("Person"), has_name=c.creator_name
        )
        if c.name_identifier:
            raise RuntimeError(f"Cannot handle name_identifier for {c}")
        producers.append(agent)
    if producers:
        event.has_activity.append(
            efi.ProducingActivity(
                type=efi.ProducingActivityTypeEnum("Producer"),
                has_agent=producers,
            )
        )
    production_companies = []
    for p in input.producers.producer if input.producers else []:
        if not p.producer_name:
            continue
        agent = efi.Agent(
            type=efi.AgentTypeEnum("CorporateBody"), has_name=p.producer_name
        )
        if p.name_identifier:
            raise RuntimeError(f"Cannot handle name_identifier for {p}")
        production_companies.append(agent)
    if production_companies:
        event.has_activity.append(
            efi.ProducingActivity(
                type=efi.ProducingActivityTypeEnum("ProductionCompany"),
                has_agent=production_companies,
            )
        )
    contrib_dict = defaultdict(list)
    if input.contributors:
        for contributor in input.contributors.contributor:
            if not contributor.contributor_name:
                continue
            for unit in contributor.contributor_name.split(";"):
                match = re.search(r"^([^(]*) \(([^()]*).", unit)
                if match:
                    name, roles = match.groups()
                else:
                    name = unit
                    roles = "Unknown"
                name = name.strip()
                if not any(
                    expr in name.lower() for expr in CORPORATE_BODY_FLAG_WORDS
                ):
                    name_components = name.split(",")
                    if len(name_components) == 1:
                        name_components = name.rsplit(maxsplit=1)
                        orig_name = name
                        name = ", ".join(reversed(name_components))
                        log.warning(
                            f"Please check if correct: Replaced name"
                            f" '{orig_name}' by '{name}'"
                        )
                    elif len(name_components) != 2:
                        raise ValueError(
                            f"Name probably not in correct format"
                            f" (family_name, given_name): {name}"
                        )
                for match in re.finditer(
                    r"([^,/]+)(, +|/|$)",
                    re.sub(r" +und ", ", ", roles),
                ):
                    role = match.groups()[0].strip()
                    contrib_dict[role].append(name)
        for role, names in contrib_dict.items():
            if role == "Unknown":
                # Handled on manifestation level below
                continue
            activity_type = role_mapping[role]
            if activity_type is None:
                continue
            # drop TypeEnum suffix to get the required class name
            activity_class_name = activity_type.__class__.__name__[:-8]
            activity = getattr(efi, activity_class_name)(
                type=activity_type,
                has_agent=[
                    efi.Agent(type=efi.AgentTypeEnum("Person"), has_name=name)
                    for name in names
                ],
            )
            event.has_activity.append(activity)
    if input.genre and input.genre.value:
        work.has_genre.append(efi.Genre(has_name=input.genre.value))
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
                        efi.GNDResource(id=subject_area_to_gnd_mapping[k])
                    ],
                )
            )
    for k in input.keywords.keyword:
        work.has_subject.append(efi.Subject(has_name=k.value))
    identifiers = input.alternate_identifiers
    if identifiers:
        for id in identifiers.alternate_identifier:
            if not (id.value.startswith("10.5240/")):
                raise RuntimeError(f"Cannot handle identifier_type: {id}")
            work.same_as.append(efi.EIDRResource(id=id.value))
    work_id = efi.LocalResource(id=f"{source_key}_work")
    work.has_identifier.append(work_id)
    described_by = described_by_issuer(work, ISSUER_INFO)
    if source_key not in described_by.has_source_key:
        described_by.has_source_key.append(source_key)
    efi_records.append(work)

    # manifestation
    manifestation_title = copy.deepcopy(work.has_primary_title)
    manifestation_title.type = efi.TitleTypeEnum("TitleProper")
    manifestation = efi.Manifestation(
        is_manifestation_of=[work_id], has_primary_title=manifestation_title
    )
    if manifestation.has_primary_title.type == efi.TitleTypeEnum(
        "PreferredTitle"
    ):
        manifestation.has_primary_title.type = efi.TitleTypeEnum("TitleProper")
    for description in input.descriptions.description:
        # Recon with <br/> elements accepted by the NTM schema
        manifestation.has_note.append(
            "\n".join(
                [text for text in description.content if isinstance(text, str)]
            )
        )
    publication_year = get_iso_date(
        str(input.publication_year), str(input.iwf_publication_year)
    )
    if (
        publication_year
        or input.publishers.publisher
        or contrib_dict.get("Unknown")
    ):
        publication = efi.PublicationEvent(
            type=efi.PublicationEventTypeEnum("ReleaseEvent")
        )
        manifestation.has_event.append(publication)
        publishers = []
        for p in input.publishers.publisher:
            agent = efi.Agent(
                type=efi.AgentTypeEnum("CorporateBody"),
                has_name=p.publisher_name,
            )
            if p.name_identifier:
                raise RuntimeError(f"What to do about identifier: {p}")
            publishers.append(agent)
        if publishers:
            publication.has_activity.append(
                efi.ManifestationActivity(
                    type=efi.ManifestationActivityTypeEnum("Publisher"),
                    has_agent=publishers,
                )
            )
        if contrib_dict["Unknown"]:
            publication.has_activity.append(
                efi.ManifestationActivity(
                    type=efi.ManifestationActivityTypeEnum("UnknownActivity"),
                    has_agent=[
                        efi.Agent(
                            type=efi.AgentTypeEnum("Person"), has_name=name
                        )
                        for name in contrib_dict["Unknown"]
                    ],
                )
            )
        if publication_year:
            publication.has_date = publication_year
    manifestation_id = efi.LocalResource(id=f"{source_key}_manifestation")
    manifestation.has_identifier.append(manifestation_id)
    described_by = described_by_issuer(manifestation, ISSUER_INFO)
    if source_key not in described_by.has_source_key:
        described_by.has_source_key.append(source_key)
    efi_records.append(manifestation)

    # item
    item = efi.Item(
        is_item_of=manifestation_id,
        has_primary_title=copy.deepcopy(manifestation.has_primary_title),
    )

    if input.language:
        if input.language == "qot":
            item.has_sound_type = efi.SoundTypeEnum("Sound")
            item.in_language.append(
                efi.Language(usage=[efi.LanguageUsageEnum("NoDialogue")])
            )
        elif input.language == "qno":
            item.has_sound_type = efi.SoundTypeEnum("Silent")
        else:
            item.in_language.append(
                efi.Language(
                    code=input.language,
                    usage=[efi.LanguageUsageEnum("SpokenLanguage")],
                )
            )
    # Todo: format
    if input.size:
        match = re.search(r"^([\d,]+) *(\w+)$", input.size)
        if match is None:
            raise RuntimeError(f"No idea how to parse size={input.size}")
        value, unit = match.groups()
        value = value.replace(",", ".")
        item.has_extent = efi.Extent(
            has_value=value, has_unit=size_mapping[unit]
        )
    if input.duration:
        match = re.search(r"^(\d\d):(\d\d):(\d\d):\d\d$", input.duration)
        if match is None:
            raise RuntimeError(
                f"No idea how to parse duration={input.duration}"
            )
        duration_str = ""
        for val, suffix in zip(match.groups(), ("H", "M", "S"), strict=True):
            i = int(val)
            if i or (not duration_str and suffix == "S"):
                duration_str += f"{str(i)}{suffix}"
        duration_str = f"PT{duration_str}"
        item.has_duration = efi.Duration(has_value=duration_str)

    # External identifiers
    if input.doi:
        item.same_as.append(efi.DOIResource(id=input.doi))

    # links
    if input.links:
        for link in input.links.link:
            if link.link_type == ntm.LinkType.AV_PORTAL:
                item.has_webresource.append(link.value)

    item_id = efi.LocalResource(id=f"{source_key}_item")
    item.has_identifier.append(item_id)
    described_by = described_by_issuer(item, ISSUER_INFO)
    described_by.has_source_key.append(source_key)
    efi_records.append(item)
    return efi_records


def get_iso_date(year: str, iwf_year: str) -> str | None:
    """Extract a year or period in keeping with ISO 8601.

    iwf_production_year and iwf_publication_year in the NTM schema
    seem to provide more extensive information than their counterparts
    without the iwf_ prefix. Try to make sense of that information if
    present and resort to the simpler fields when that does not work
    out.

    Parameters
    ----------
    year : str
        Input from production_year or publication_year.
    iwf_year : str
        Input from iwf_production_year or iwf_publication.

    """
    for iso_date in (iwf_year, year):
        if not iso_date:
            continue
        if "-" in iso_date:
            iso_date = iso_date.replace("-", "/")
        if is_iso_date(iso_date):
            break
    else:
        if year or iwf_year:
            log.warning(
                f"Expected date or interval according to ISO 8601,"
                f" got: {year or iwf_year}"
            )
        return None
    return iso_date


def is_iso_date(date_str):
    return bool(
        re.search(
            r"^-?([1-9][0-9]{3,}|0[0-9]{3})(-(0[1-9]|1[0-2])"
            "(-(0[1-9]|[12][0-9]|3[01]))?)?[?~]?(/-?([1-9][0-9]{3,}|0[0-9]{3})"
            "(-(0[1-9]|1[0-2])(-(0[1-9]|[12][0-9]|3[01]))?)?[?~]?)?$",
            date_str,
        )
    )


def process_titles(
    titles: list[ntm.TitleType],
) -> tuple[efi.Title | list[efi.Title]]:
    """Return primary and a list of alternative titles.

    Identify preferred title, append the subtitle if present, and
    return it as primary title. Also, return a (possibly empty) list
    of alternative titles.

    Parameters
    ----------
    titles : list(ntm.TitleType)
        List of titles according to NTM schema.

    Returns
    -------
    tuple(efi.Title, list(efi.Title))
        Primary and list of alternative titles.

    """
    input_primary_title = input_subtitle = None
    alternative_titles = []
    for title in titles:
        if not (title.value.strip()):
            continue
        if title.title_type is None:
            if input_primary_title:
                raise RuntimeError(f"Cannot determine primary title: {titles}")
            input_primary_title = title
        elif title.title_type == ntm.TitleType.SUBTITLE:
            if input_subtitle:
                raise RuntimeError(
                    f"Cannot associate subtitle to primary title: {titles}"
                )
            input_subtitle = title
        elif title.title_type == ntm.TitleType.ALTERNATIVE_TITLE:
            alternative_titles.append(
                make_title(title, efi.TitleTypeEnum("AlternativeTitle"))
            )
        else:
            raise RuntimeError(f"No mapping specified for title type: {title}")
    if input_subtitle and input_subtitle.value.strip() not in [
        t.has_name for t in alternative_titles
    ]:
        if input_subtitle.language != input_primary_title.language:
            raise RuntimeError(
                f"Languages do not match for primary and subtitle: {titles}"
            )
        input_primary_title.value = " - ".join(
            [input_primary_title.value, input_subtitle.value]
        )
    primary_title = make_title(
        input_primary_title, efi.TitleTypeEnum("PreferredTitle")
    )
    return primary_title, alternative_titles


def make_title(input_title, title_type: efi.TitleTypeEnum) -> efi.Title:
    display_title = re.sub(r"\s+", " ", input_title.value.strip())
    result = efi.Title(type=title_type, has_name=display_title)
    split_title = display_title.split(maxsplit=1)
    if (
        len(split_title) > 1
        and split_title[0].lower() in articles[input_title.language]
    ):
        first, rest = split_title
        result.has_ordering_name = f"{rest}, {first}"
        log.warning(
            f"Pushing article to back of ordering name for title:"
            f" {result.has_ordering_name}"
        )
    if len(display_title) > settings.line_limit:
        result.has_name = f"{display_title[: settings.line_limit - 3]}..."
        if result.has_ordering_name:
            result.has_ordering_name = result.has_ordering_name[
                : settings.line_limit
            ]
        log.warning(
            f"Shortening title that exceeded line limit of"
            f" {settings.line_limit} characters: {result.has_name}"
        )
    return result


articles = {
    "eng": ["a", "an", "the"],
    "ger": ["das", "der", "die", "ein", "eine"],
}


role_mapping = {
    "3D-Animation": efi.SpecialEffectsActivityTypeEnum("VisualEffects"),
    "Animation": efi.AnimationActivityTypeEnum("Animation"),
    "Anthropologe": None,
    "Assistenz": None,
    "ausführender Produzent": efi.ProducingActivityTypeEnum(
        "ExecutiveProducer"
    ),
    "Bearb.": efi.WritingActivityTypeEnum("Adaptation"),
    "Bearbeitung": efi.WritingActivityTypeEnum("Adaptation"),
    "Berater": efi.ProducingActivityTypeEnum("Advisor"),
    "Beratung": efi.ProducingActivityTypeEnum("Advisor"),
    "Bildmischung": None,
    "Buch": efi.WritingActivityTypeEnum("Writer"),
    "Bühnenbild": efi.ProductionDesignActivityTypeEnum("SetDesigner"),
    "Chorleitung": None,
    "Computeranimation": efi.AnimationActivityTypeEnum("ComputerAnimation"),
    "Computergraphik": efi.SpecialEffectsActivityTypeEnum("CGIArtist"),
    "Datenkonvertierung": None,
    "Design": None,
    "Dramaturgie": None,
    "Dramaturgische Beratung": efi.ProducingActivityTypeEnum("Advisor"),
    "Drehbuch": efi.WritingActivityTypeEnum("Writer"),
    "DVD-Authoring": None,
    "DVD-Redaktion": None,
    "elektronische Aufzeichnung": None,
    "Ethnologie": None,
    "Ethnographie": None,
    "Fachreferat": None,
    "Filmabtastung": None,
    "Fotografie": efi.CinematographyActivityTypeEnum("StillPhotographer"),
    "Fotorecherche": efi.WritingActivityTypeEnum("Research"),
    "Gestaltung": None,
    "Grafik": None,
    "Graphik": efi.AnimationActivityTypeEnum("Animator"),
    "Inszenierung": efi.WritingActivityTypeEnum("Stagedby"),
    "Interview": efi.CastActivityTypeEnum("Interviewer"),
    "Kamera": efi.CinematographyActivityTypeEnum("Cinematographer"),
    "kamera": efi.CinematographyActivityTypeEnum("Cinematographer"),
    "Kameraassistenz": efi.CinematographyActivityTypeEnum("CameraAssistant"),
    "Kommentar": efi.WritingActivityTypeEnum("NarrationWriter"),
    "Kommentartext": efi.WritingActivityTypeEnum("NarrationWriter"),
    "Komposition": efi.MusicActivityTypeEnum("Composer"),
    "Kostüme": efi.ProductionDesignActivityTypeEnum("CostumeDesigner"),
    "Libretto": None,
    "Licht": efi.CinematographyActivityTypeEnum("GafferLighting"),
    "Lichtbestimmung": efi.LaboratoryActivityTypeEnum("Colorist"),
    "MAZ-Schnitt": None,
    "MAZ-Technik": None,
    "Maz-Technik": None,
    "Mikrokinematographie": efi.CinematographyActivityTypeEnum(
        "Cinematographer"
    ),
    "Mikrokinematographie-Assistenz": efi.CinematographyActivityTypeEnum(
        "CameraAssistant"
    ),
    "Musik": efi.MusicActivityTypeEnum("MusicSupervisor"),
    "musikalische Leitung": efi.MusicActivityTypeEnum("MusicSupervisor"),
    "Orchester": efi.MusicActivityTypeEnum("MusicPerformer"),
    "Postproduktion": efi.ProducingActivityTypeEnum(
        "PostProductionSupervisor"
    ),
    "Präparation": None,
    "Produktion": efi.ProducingActivityTypeEnum("Producer"),
    "Produktionsleitung": efi.ProducingActivityTypeEnum("Producer"),
    "Projektkoordination": efi.ProducingActivityTypeEnum(
        "ProductionCoordinator"
    ),
    "Projektleitung": efi.WritingActivityTypeEnum("Editor"),
    "Psychiater": None,
    "Red.": efi.WritingActivityTypeEnum("Editor"),
    "Redaktion": efi.WritingActivityTypeEnum("Editor"),
    "Redaktionsassistenz": efi.WritingActivityTypeEnum("AssistantEditor"),
    "Regie": efi.DirectingActivityTypeEnum("Director"),
    "Regieassistenz": efi.DirectingActivityTypeEnum("AssistantDirector"),
    "Sachbearbeiter": None,
    "Schnitt": efi.EditingActivityTypeEnum("FilmEditor"),
    "Sprecher": efi.CastActivityTypeEnum("Narrator"),
    "Sprecherin": efi.CastActivityTypeEnum("Narrator"),
    "technische Assistenz": None,
    "technische Leitung": None,
    "Text": efi.WritingActivityTypeEnum("SourceMaterial"),
    "Ton": efi.SoundActivityTypeEnum("SoundRecorderMixer"),
    "Tonmischung": efi.SoundActivityTypeEnum("SoundRecorderMixer"),
    "Trick": efi.AnimationActivityTypeEnum("Animator"),
    "Typografie": None,
    "Übersetzung": None,
    "Untertitel": None,
    "Videobearbeitung": efi.CinematographyActivityTypeEnum("VideoAssist"),
    "Videotechnik": efi.CinematographyActivityTypeEnum("VideoAssist"),
    "wissenschaftl. Betreuung": efi.ProducingActivityTypeEnum("Advisor"),
    "wissenschaftliche Beratung": efi.ProducingActivityTypeEnum("Advisor"),
    "wissenschaftliche Mitarbeit": efi.ProducingActivityTypeEnum("Advisor"),
}


size_mapping = {
    "GB": efi.UnitEnum("GigaByte"),
    "MB": efi.UnitEnum("MegaByte"),
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
