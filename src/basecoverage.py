class BaseCoverage:
    def __init__(self, organisation: str, repository: str) -> None:
        self.organisation = organisation
        self.repository = repository

    def org(self) -> str:
        return self.organisation

    def repo(self) -> str:
        return self.repository


if __name__ == '__main__':
    print(__name__)
