from dataclasses import dataclass


@dataclass
class PDSectionElement:
    sectionId: int
    startTime: str
    endTime: str