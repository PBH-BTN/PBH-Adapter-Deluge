from dataclasses import asdict, dataclass


@dataclass
class BaseModel:
    def dist(self) -> dict:
        return asdict(self)
