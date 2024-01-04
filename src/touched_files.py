from pydriller import Commit, Repository
from src.utils import Utils
from src.codecov import CodeCovCoverage
from src.coveralls import CoverallsCoverage
from src.coverageimporter import CodecovCoverageImporter, CoverallsCoverageImporter


class ModifiedPatchData:
    @staticmethod
    def patch_size(commit: Commit, covered_files: list[str]) -> dict:
        """how many lines is a typical patch"""
        code_patch_size = test_patch_size = config_patch_size = 0
        for m in commit.modified_files:
            if any(m.filename.lower() in filename.lower() for filename in covered_files):
                index = Utils.index_finder(m.filename.lower(), covered_files)
                full_filename_path = covered_files[index]
                if 'test' in full_filename_path:
                    test_patch_size += m.added_lines + m.deleted_lines
                else:
                    code_patch_size += m.added_lines + m.deleted_lines
            else:
                config_patch_size += m.added_lines + m.deleted_lines
        return {
            'code_patch_size': code_patch_size,
            'test_patch_size': test_patch_size,
            'config_patch_size': config_patch_size
        }

    @staticmethod
    def patch_number_of_files(commit: Commit, covered_files: list[str]) -> dict:
        """ how many files are touched by commit """
        code_files = config_files = 0
        for m in commit.modified_files:
            if any(m.filename.lower() in filename.lower() for filename in covered_files):
                code_files += 1
            else:
                config_files += 1
        return {
            'number_of_source_code_files': code_files,
            'number_of_config': config_files
        }

    @staticmethod
    def patch_file_type(commit: Commit, covered_files: list[str]) -> dict:
        """ does a patch co-evolve test and production code?"""
        code_files = test_files = 0
        for m in commit.modified_files:
            if any(m.filename.lower() in filename.lower() for filename in covered_files):
                index = Utils.index_finder(m.filename.lower(), covered_files)
                full_filename_path = covered_files[index]
                if 'test' in full_filename_path:
                    test_files += 1
                else:
                    code_files += 1
        return {
            'touched_source_files_only': True if code_files > 0 and test_files == 0 else False,
            'touched_test_files_only': True if test_files > 0 and code_files == 0 else False,
            'touched_both_test_source_files': True if code_files > 0 and test_files > 0 else False,
            'touched_config_files': True if code_files == 0 and code_files == 0 else False
        }


class CodeCovDQsData(CodecovCoverageImporter):
    def __init__(self, initCodecov: CodeCovCoverage) -> None:
        super().__init__(initCodecov)

    async def checkout_and_analyze_commit(self, build: dict) -> None:
        repo_name = build['repository_name']
        git_url = 'https://github.com/{}.git'.format(repo_name)
        for commit in Repository(git_url, single=build['commit_sha']).traverse_commits():
            commit_report = await self.codecov.commit_report(commit.hash)
            patch_files_kind = ModifiedPatchData.patch_file_type(commit, commit_report)
            patch_files_count = ModifiedPatchData.patch_number_of_files(commit, commit_report)
            modified_files_size = ModifiedPatchData.patch_size(commit, commit_report)
            # fill the build with the update results
            build.update(patch_files_kind)
            build.update(patch_files_count)
            build.update(modified_files_size)

    async def analyze_commits(self):
        await super().analyze_commits()


class CoverallsDQsData(CoverallsCoverageImporter):
    def __init__(self, initCoveralls: CoverallsCoverage) -> None:
        super().__init__(initCoveralls)

    async def checkout_and_analyze_commit(self, build: dict) -> None:
        repo_name = build['repository_name']
        git_url = 'https://github.com/{}.git'.format(repo_name)
        for commit in Repository(git_url, single=build['commit_sha']).traverse_commits():
            commit_report = await self.coveralls.fetch_source_files(commit.hash)
            patch_files_kind = ModifiedPatchData.patch_file_type(commit, commit_report)
            patch_files_count = ModifiedPatchData.patch_number_of_files(commit, commit_report)
            modified_files_size = ModifiedPatchData.patch_size(commit, commit_report)
            # fill the build with the update results
            build.update(patch_files_kind)
            build.update(patch_files_count)
            build.update(modified_files_size)

    async def analyze_commits(self):
        await super().analyze_commits()