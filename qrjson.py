from dataclasses import dataclass, field
from typing import Union, Dict, List


@dataclass
class QRJson:
    width: float = 20.0
    height: float = 20.0
    margin_up: float = 0.1
    margin_down: float = 0.3
    margin_left: float = 0.2
    margin_right: float = 0.2
    text: str = "under"  # 'under' lub 'over'
    text_size: float = 0.15
    items: List[Dict[str, str]] = field(default_factory=list)

    def add_items(
        self,
        data: Union[List[str], Dict[str, str]],
        repeat: int = 1
    ):
        #pozwala na włożenie list lub dict
        if isinstance(data, list):
            pairs = {val: val for val in data}
        elif isinstance(data, dict):
            pairs = data
        else:
            raise TypeError("data musi być listą lub słownikiem")

        for label, value in pairs.items():
            for _ in range(repeat):
                self.items.append({"label": label, "value": value})


class QRJsonGenerator:
    def __init__(self):
        self.config: Dict[str, QRJson] = {}

    def add_type(
        self,
        name: str,
        items: Union[List[str], Dict[str, str]],
        repeat: int = 1,
        **overrides
    ):
        q = QRJson(**overrides)
        q.add_items(items, repeat=repeat)
        self.config[name] = q

    def generate(self) -> Dict[str, dict]:
        return {
            name: {
                "width": q.width,
                "height": q.height,
                "margin_up": q.margin_up,
                "margin_down": q.margin_down,
                "margin_left": q.margin_left,
                "margin_right": q.margin_right,
                "text": q.text,
                "text_size": q.text_size,
                "items": q.items,
            }
            for name, q in self.config.items()
        }
