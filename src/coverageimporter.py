import asyncio
from pydriller import Repository
from abc import ABC, abstractmethod

from src.codecov import CodeCovCoverage
from src.coveralls import CoverallsCoverage
from src.utils import Utils
from src.patch_extracts import PatchExtracts
from src.crap_metric import CrapMetric


class CoverageImporter(ABC):
    @abstractmethod
    async def checkout_and_analyze_commit(self, build: dict) -> None:
        pass

    @abstractmethod
    async def analyze_commits(self):
        pass


class CodecovCoverageImporter(CoverageImporter):
    def __init__(self, initCodecov: CodeCovCoverage) -> None:
        self.codecov = initCodecov

    async def checkout_and_analyze_commit(self, build: dict) -> None:
        repo_name = build['repository_name']
        git_url = 'https://github.com/{}.git'.format(repo_name)
        for commit in Repository(git_url, single=build['commit_sha']).traverse_commits():
            commit_report = await self.codecov.commit_report(
                commit.hash)  # Get commit report -> which has all the files present in the commit
            commit_files = self.codecov.fetch_source_file_names(
                commit_report)  # From the commit report extract the list of source files
            api_patch_coverage = self.codecov.api_patch_coverage(
                commit_report)  # From the commit report retrieve patch coverage as per api status
            executed_lines = executable_lines = 0
            if commit_files:  # if the commit report contains source files
                for m in commit.modified_files:
                    modified_source_file = Utils.index_finder(m.filename,
                                                              commit_files)  # check if the modified files is a source file and is contained in the commit report
                    if modified_source_file != -1:
                        coverage_array = self.codecov.file_line_coverage_array(commit_report,
                                                                               commit_files[
                                                                                   modified_source_file])  # For the modified source file -> get the coverage array
                        if coverage_array:  # check if the coverage array is not empty
                            modified_lines = [line_number[0] for line_number in m.diff_parsed['added']]
                            for line in modified_lines:
                                for line_coverage_arr in coverage_array:
                                    if line == line_coverage_arr[0]:
                                        if line_coverage_arr[1] == 0:
                                            executed_lines += 1
                                        if line_coverage_arr[1] == 0 or line_coverage_arr[1] == 1 or \
                                                line_coverage_arr[1] == 2:
                                            executable_lines += 1
            patch_files = PatchExtracts.patch_files(commit, commit_files)
            patch_size = PatchExtracts.patch_sizes(commit, commit_files)
            patch_number_of_files = PatchExtracts.patch_number_of_files(commit, commit_files)
            build.update(patch_files)  # update the
            build.update(patch_size)
            build.update(patch_number_of_files)
            dmm_commit_size = commit.dmm_unit_size if not isinstance(commit.dmm_unit_size, type(None)) else 0
            dmm_commit_complexity = commit.dmm_unit_complexity if not isinstance(commit.dmm_unit_complexity,
                                                                                 type(None)) else 0
            dmm_commit_interface = commit.dmm_unit_interfacing if not isinstance(commit.dmm_unit_interfacing,
                                                                                 type(None)) else 0
            delta_maintainibility_model = round((dmm_commit_size + dmm_commit_complexity + dmm_commit_interface) / 3, 3)
            if executable_lines == 0:
                commit_crappiness = CrapMetric.commit_dmm_crap_metric(dmm_commit_complexity, 0)
                build['patch_coverage'] = 0
            else:
                commit_crappiness = CrapMetric.commit_dmm_crap_metric(dmm_commit_complexity, (
                        executed_lines / executable_lines) * 100)
                build['patch_coverage'] = round((executed_lines / executable_lines) * 100, 3)

            build['api_patch_coverage'] = round(api_patch_coverage, 3)
            build['dmm_unit_size'] = round(dmm_commit_size, 3)
            build['dmm_unit_complexity'] = round(dmm_commit_complexity, 3)
            build['dmm_unit_interface'] = round(dmm_commit_interface, 3)
            build['dmm'] = round(delta_maintainibility_model, 3)
            build['crap_metric'] = round(commit_crappiness, 3)

    async def analyze_commits(self):
        builds = await self.codecov.collect_build_data()
        modified_builds = []
        if len(builds) != 0:
            for build in builds:
                try:
                    async with asyncio.Lock():
                        await self.checkout_and_analyze_commit(build)
                        modified_builds.append(build)
                except Exception as err:
                    commit_hash = build['commit_sha']
                    self.codecov.logger.coverage_logger_configuration('FinalCodeCovCheckoutErrors')
                    self.codecov.logger.error(f"Codecov: Error checking out commit:{commit_hash} in repo {self.codecov.organisation}/{self.codecov.repository}. error - {str(err)}")
                    continue
        return modified_builds


class CoverallsCoverageImporter(CoverageImporter):
    def __init__(self, initCoveralls: CoverallsCoverage) -> None:
        self.coveralls = initCoveralls

    async def checkout_and_analyze_commit(self, build: dict) -> None:
        repo_name = build['repository_name']
        git_url = 'https://github.com/{}.git'.format(repo_name)
        for commit in Repository(git_url, single=build['commit_sha']).traverse_commits():
            commit_files = await self.coveralls.fetch_source_files(build['commit_sha'])  # source files in that commit
            executable_lines = executed_lines = 0
            if commit_files:  # check if the list of source files in that commit is empty or not
                for m in commit.modified_files:
                    filename_index = Utils.index_finder(m.filename,
                                                        commit_files)  # check if modified file is a source file
                    if filename_index != -1:  # if the file is indeed a source file
                        line_coverage_array = await self.coveralls.source_coverage_array(commit.hash,
                                                                                         commit_files[
                                                                                             filename_index])  # Get the coverage array of modified file
                        if line_coverage_array:  # if the coverage array is not empty
                            modified_lines = [line_number[0] for line_number in m.diff_parsed['added']]
                            executable_lines += len([1 for line_number in modified_lines if
                                                     isinstance(line_coverage_array[line_number - 1], int)])
                            executed_lines += len([1 for line_number in modified_lines if
                                                   isinstance(line_coverage_array[line_number - 1], int) and
                                                   line_coverage_array[line_number - 1] > 0])
            patch_files = PatchExtracts.patch_files(commit, commit_files)
            patch_size = PatchExtracts.patch_sizes(commit, commit_files)
            patch_number_of_files = PatchExtracts.patch_number_of_files(commit, commit_files)
            build.update(patch_files)  # update the
            build.update(patch_size)
            build.update(patch_number_of_files)

            dmm_commit_size = commit.dmm_unit_size if not isinstance(commit.dmm_unit_size, type(None)) else 0
            dmm_commit_complexity = commit.dmm_unit_complexity if not isinstance(commit.dmm_unit_complexity,
                                                                                 type(None)) else 0
            dmm_commit_interface = commit.dmm_unit_interfacing if not isinstance(commit.dmm_unit_interfacing,
                                                                                 type(None)) else 0
            delta_maintainibility_model = round((dmm_commit_size + dmm_commit_complexity + dmm_commit_interface) / 3, 3)
            if executable_lines == 0:
                build['patch_coverage'] = 0
                commit_crappiness = CrapMetric.commit_dmm_crap_metric(dmm_commit_complexity, 0)
            else:
                commit_crappiness = CrapMetric.commit_dmm_crap_metric(dmm_commit_complexity, (
                        executed_lines / executable_lines) * 100)
                build['patch_coverage'] = round((executed_lines / executable_lines) * 100, 3)
            build['dmm_unit_size'] = round(dmm_commit_size, 3)
            build['dmm_unit_complexity'] = round(dmm_commit_complexity, 3)
            build['dmm_unit_interface'] = round(dmm_commit_interface, 3)
            build['dmm'] = round(delta_maintainibility_model, 3)
            build['crap_metric'] = round(commit_crappiness, 3)

    async def analyze_commits(self):
        builds = await self.coveralls.collect_builds_data()
        modified_builds = []
        if len(builds) != 0:
            for build in builds:
                try:
                    async with asyncio.Lock():
                        await self.checkout_and_analyze_commit(build)
                        modified_builds.append(build)
                except Exception as err:
                    commit_hash = build['commit_sha']
                    self.coveralls.logger.coverage_logger_configuration('FinalCoverallsCheckoutErrors')
                    self.coveralls.logger.error(
                        f"Coveralls: Error checking out commit:{commit_hash} in repo {self.coveralls.organisation}/{self.coveralls.repository}. error - {str(err)}")
                    continue
        return modified_builds
