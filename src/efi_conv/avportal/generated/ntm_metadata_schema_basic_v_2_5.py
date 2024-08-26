"""This file was generated by xsdata, v24.7, on 2024-08-04 10:08:57

Generator: DataclassGenerator
See: https://xsdata.readthedocs.io/
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import List, Optional

__NAMESPACE__ = (
    "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd"
)


class AdditionalMaterialType(Enum):
    FILE = "File"
    URL = "URL"


@dataclass
class AlternateIdentifierDataAlternateIdentifier:
    class Meta:
        global_type = False

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    alternate_identifier_type: Optional[str] = field(
        default=None,
        metadata={
            "name": "alternateIdentifierType",
            "type": "Attribute",
            "required": True,
        },
    )


class DescriptionType(Enum):
    ABSTRACT = "Abstract"
    TECHNICAL_REMARKS = "TechnicalRemarks"


class GenreType(Enum):
    CONFERENCE_TALK = "Conference/Talk"
    DOCUMENTATION_REPORT = "Documentation/Report"
    EXPERIMENT_MODEL_TEST = "Experiment/Model Test"
    EXPLANATORY_VIDEO = "Explanatory Video"
    INTERVIEW = "Interview"
    LECTURE = "Lecture"
    RESEARCH_DATA = "Research Data"
    VIDEO_ABSTRACT = "Video Abstract"
    WEBINAR_TUTORIAL = "Webinar/Tutorial"
    WORKSHOP_INTERACTIVE_FORMAT = "Workshop/Interactive Format"
    OTHER_VIDEO = "Other Video"


@dataclass
class KeywordsTypeKeyword:
    class Meta:
        global_type = False

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    language: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"[a-z]{3}",
        },
    )


@dataclass
class NameIdentifier:
    class Meta:
        name = "nameIdentifier"
        namespace = "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    name_identifier_scheme: Optional[str] = field(
        default=None,
        metadata={
            "name": "nameIdentifierScheme",
            "type": "Attribute",
            "required": True,
        },
    )
    scheme_uri: Optional[str] = field(
        default=None,
        metadata={
            "name": "schemeURI",
            "type": "Attribute",
        },
    )


class RelatedIdentifierType(Enum):
    ARK = "ARK"
    AR_XIV = "arXiv"
    BIBCODE = "bibcode"
    DOI = "DOI"
    EAN13 = "EAN13"
    EIDR = "EIDR"
    EISSN = "EISSN"
    HANDLE = "Handle"
    ISBN = "ISBN"
    ISSN = "ISSN"
    ISTC = "ISTC"
    LISSN = "LISSN"
    LSID = "LSID"
    PMID = "PMID"
    PROBADO = "PROBADO"
    PURL = "PURL"
    URL = "URL"
    URN = "URN"


class RelationType(Enum):
    CITES = "cites"
    IS_CITED_BY = "isCitedBy"
    IS_SUPPLEMENTED_BY = "isSupplementedBy"
    IS_SUPPLEMENT_TO = "isSupplementTo"


class ResourceTypeData(Enum):
    AUDIO = "Audio"
    AUDIOVISUAL = "Audiovisual"


@dataclass
class RightsType:
    class Meta:
        name = "rightsType"

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    rights_uri: Optional[str] = field(
        default=None,
        metadata={
            "name": "rightsURI",
            "type": "Attribute",
            "required": True,
        },
    )


@dataclass
class SeriesTypeSeriesDescription:
    class Meta:
        global_type = False

    content: List[object] = field(
        default_factory=list,
        metadata={
            "type": "Wildcard",
            "namespace": "##any",
            "mixed": True,
            "choices": (
                {
                    "name": "br",
                    "type": str,
                    "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
                    "length": 0,
                },
            ),
        },
    )


class SubjectAreaType(Enum):
    ARCHITECTURE = "Architecture"
    ARTS_AND_MEDIA = "Arts and Media"
    HORTICULTURE = "Horticulture"
    CHEMISTRY = "Chemistry"
    COMPUTER_SCIENCE = "Computer Science"
    EARTH_SCIENCES = "Earth Sciences"
    ECONOMICS_SOCIAL_SCIENCES = "Economics/Social Sciences"
    EDUCATIONAL_SCIENCE = "Educational Science"
    ENGINEERING = "Engineering"
    ENVIRONMENTAL_SCIENCES_ECOLOGY = "Environmental Sciences/Ecology"
    ETHNOLOGY = "Ethnology"
    HISTORY = "History"
    INFORMATION_SCIENCE = "Information Science"
    INFORMATION_TECHNOLOGY = "Information Technology"
    LAW = "Law"
    LINGUISTICS = "Linguistics"
    LIFE_SCIENCES = "Life Sciences"
    LITERATURE_STUDIES = "Literature Studies"
    MATHEMATICS = "Mathematics"
    MEDICINE = "Medicine"
    PHILOSOPHY = "Philosophy"
    PHYSICS = "Physics"
    PSYCHOLOGY = "Psychology"
    SPORTS_SCIENCE = "Sports Science"
    STUDY_OF_RELIGIONS = "Study of Religions"
    OTHER = "Other"


@dataclass
class SubjectsDataSubject:
    class Meta:
        global_type = False

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    subject_scheme: Optional[str] = field(
        default=None,
        metadata={
            "name": "subjectScheme",
            "type": "Attribute",
            "required": True,
        },
    )


class TitleType(Enum):
    SUBTITLE = "Subtitle"
    ALTERNATIVE_TITLE = "AlternativeTitle"


@dataclass
class AdditionalMaterialsDataAdditionalMaterial:
    class Meta:
        global_type = False

    value: str = field(
        default="",
        metadata={
            "required": True,
        },
    )
    additional_material_type: Optional[AdditionalMaterialType] = field(
        default=None,
        metadata={
            "name": "additionalMaterialType",
            "type": "Attribute",
            "required": True,
        },
    )
    additional_material_title: Optional[str] = field(
        default=None,
        metadata={
            "name": "additionalMaterialTitle",
            "type": "Attribute",
        },
    )
    related_identifier: Optional[object] = field(
        default=None,
        metadata={
            "name": "relatedIdentifier",
            "type": "Attribute",
        },
    )
    related_identifier_type: Optional[RelatedIdentifierType] = field(
        default=None,
        metadata={
            "name": "relatedIdentifierType",
            "type": "Attribute",
        },
    )
    relation_type: Optional[RelationType] = field(
        default=None,
        metadata={
            "name": "relationType",
            "type": "Attribute",
        },
    )


@dataclass
class AlternateIdentifierData:
    class Meta:
        name = "alternateIdentifierData"

    alternate_identifier: List[AlternateIdentifierDataAlternateIdentifier] = (
        field(
            default_factory=list,
            metadata={
                "name": "alternateIdentifier",
                "type": "Element",
                "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
                "min_occurs": 1,
            },
        )
    )


@dataclass
class ContributorsTypeContributor:
    class Meta:
        global_type = False

    contributor_name: Optional[object] = field(
        default=None,
        metadata={
            "name": "contributorName",
            "type": "Element",
            "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
        },
    )
    name_identifier: List[NameIdentifier] = field(
        default_factory=list,
        metadata={
            "name": "nameIdentifier",
            "type": "Element",
            "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
        },
    )


@dataclass
class CreatorsTypeCreator:
    class Meta:
        global_type = False

    creator_name: Optional[object] = field(
        default=None,
        metadata={
            "name": "creatorName",
            "type": "Element",
            "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
        },
    )
    name_identifier: List[NameIdentifier] = field(
        default_factory=list,
        metadata={
            "name": "nameIdentifier",
            "type": "Element",
            "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
        },
    )


@dataclass
class DescriptionsDataDescription:
    class Meta:
        global_type = False

    description_type: Optional[DescriptionType] = field(
        default=None,
        metadata={
            "name": "descriptionType",
            "type": "Attribute",
            "required": True,
        },
    )
    language: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"[a-z]{3}",
        },
    )
    content: List[object] = field(
        default_factory=list,
        metadata={
            "type": "Wildcard",
            "namespace": "##any",
            "mixed": True,
            "choices": (
                {
                    "name": "br",
                    "type": str,
                    "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
                    "length": 0,
                },
            ),
        },
    )


@dataclass
class KeywordsType:
    class Meta:
        name = "keywordsType"

    keyword: List[KeywordsTypeKeyword] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
            "min_occurs": 1,
        },
    )


@dataclass
class ProducersTypeProducer:
    class Meta:
        global_type = False

    producer_name: Optional[object] = field(
        default=None,
        metadata={
            "name": "producerName",
            "type": "Element",
            "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
        },
    )
    name_identifier: List[NameIdentifier] = field(
        default_factory=list,
        metadata={
            "name": "nameIdentifier",
            "type": "Element",
            "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
        },
    )


@dataclass
class PublishersTypePublisher:
    class Meta:
        global_type = False

    publisher_name: Optional[object] = field(
        default=None,
        metadata={
            "name": "publisherName",
            "type": "Element",
            "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
        },
    )
    name_identifier: List[NameIdentifier] = field(
        default_factory=list,
        metadata={
            "name": "nameIdentifier",
            "type": "Element",
            "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
        },
    )


@dataclass
class SeriesType:
    """
    Parameters
    ----------
    series_title
        A name or title by which the series is known.
    series_publisher
        The publisher of the resource may be an institutional/corporate or
        personal name.
    total_part_no
    part_no
    series_mam
    series_description
    """

    class Meta:
        name = "seriesType"

    series_title: Optional[str] = field(
        default=None,
        metadata={
            "name": "seriesTitle",
            "type": "Element",
            "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
            "required": True,
        },
    )
    series_publisher: Optional[str] = field(
        default=None,
        metadata={
            "name": "seriesPublisher",
            "type": "Element",
            "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
        },
    )
    total_part_no: Optional[int] = field(
        default=None,
        metadata={
            "name": "totalPartNo",
            "type": "Element",
            "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
        },
    )
    part_no: Optional[int] = field(
        default=None,
        metadata={
            "name": "partNo",
            "type": "Element",
            "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
        },
    )
    series_mam: Optional[int] = field(
        default=None,
        metadata={
            "name": "seriesMAM",
            "type": "Element",
            "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
        },
    )
    series_description: List[SeriesTypeSeriesDescription] = field(
        default_factory=list,
        metadata={
            "name": "seriesDescription",
            "type": "Element",
            "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
        },
    )


@dataclass
class SubjectAreasType:
    class Meta:
        name = "subjectAreasType"

    subject_area: List[SubjectAreaType] = field(
        default_factory=list,
        metadata={
            "name": "subjectArea",
            "type": "Element",
            "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
            "min_occurs": 1,
        },
    )


@dataclass
class SubjectsData:
    class Meta:
        name = "subjectsData"

    subject: List[SubjectsDataSubject] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
            "min_occurs": 1,
        },
    )


@dataclass
class TitlesDataTitle:
    class Meta:
        global_type = False

    value: str = field(
        default="",
        metadata={
            "required": True,
            "min_length": 1,
        },
    )
    title_type: Optional[TitleType] = field(
        default=None,
        metadata={
            "name": "titleType",
            "type": "Attribute",
        },
    )
    language: Optional[str] = field(
        default=None,
        metadata={
            "type": "Attribute",
            "pattern": r"[a-z]{3}",
        },
    )


@dataclass
class AdditionalMaterialsData:
    class Meta:
        name = "additionalMaterialsData"

    additional_material: List[AdditionalMaterialsDataAdditionalMaterial] = (
        field(
            default_factory=list,
            metadata={
                "name": "additionalMaterial",
                "type": "Element",
                "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
            },
        )
    )


@dataclass
class ContributorsType:
    class Meta:
        name = "contributorsType"

    contributor: List[ContributorsTypeContributor] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
            "min_occurs": 1,
        },
    )


@dataclass
class CreatorsType:
    class Meta:
        name = "creatorsType"

    creator: List[CreatorsTypeCreator] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
            "min_occurs": 1,
        },
    )


@dataclass
class DescriptionsData:
    class Meta:
        name = "descriptionsData"

    description: List[DescriptionsDataDescription] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
        },
    )


@dataclass
class ProducersType:
    class Meta:
        name = "producersType"

    producer: List[ProducersTypeProducer] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
            "min_occurs": 1,
        },
    )


@dataclass
class PublishersType:
    class Meta:
        name = "publishersType"

    publisher: List[PublishersTypePublisher] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
            "min_occurs": 1,
        },
    )


@dataclass
class TitlesData:
    """
    Parameters
    ----------
    title
        A name or title by which a resource is known.
    """

    class Meta:
        name = "titlesData"

    title: List[TitlesDataTitle] = field(
        default_factory=list,
        metadata={
            "type": "Element",
            "namespace": "http://www.tib.eu/fileadmin/extern/knm/NTM-Metadata-Schema_v_2.5.xsd",
            "min_occurs": 1,
        },
    )