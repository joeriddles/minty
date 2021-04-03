class Link:
    url: str
    visited: bool
    eggs: list[str]

    def __init__(self, url: str) -> None:
        self.url = url
        self.visited = False
    
    def __str__(self) -> str:
        return self.url
    
    def __eq__(self, o) -> bool:
        if not isinstance(o, Link):
            raise NotImplementedError()
        return self.url == o.url
    
    def __hash__(self) -> int:
        return self.url.__hash__()
