class CrapMetric:

    @staticmethod
    def commit_dmm_crap_metric(commit_dmm_complexity: float, patch_coverage: float) -> float:
        dmm_crap = pow(commit_dmm_complexity, 2) * pow(1 - (patch_coverage / 100), 3) + commit_dmm_complexity
        return round(dmm_crap, 3)


if __name__ == '__main__':
    print(__name__)
