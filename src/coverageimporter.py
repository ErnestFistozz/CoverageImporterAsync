import asyncio
from pydriller import Repository
from src.codecov import CodeCovCoverage
from src.coveralls import CoverallsCoverage
from src.utils import Utils
from src.patch_extracts import PatchExtracts
from src.crap_metric import CrapMetric


class CoverageImporter:
    async def checkout_and_analyse_coveralls_commit(self, build: dict, coveralls: CoverallsCoverage) -> None:
        repo_name = build['repository_name']
        git_url = 'https://github.com/{}.git'.format(repo_name)
        for commit in Repository(git_url, single=build['commit_sha']).traverse_commits():
            commit_files = await coveralls.fetch_source_files(build['commit_sha'])
            executable_lines = executed_lines = 0
            if commit_files:
                for m in commit.modified_files:
                    filename_index = Utils.index_finder(m.filename, commit_files)
                    if filename_index != -1:
                        line_coverage_array = await coveralls.source_coverage_array(commit.hash,
                                                                                    commit_files[filename_index])
                        if line_coverage_array:
                            modified_lines = [line_number[0] for line_number in m.diff_parsed['added']]
                            executable_lines += len([1 for line_number in modified_lines if
                                                     isinstance(line_coverage_array[line_number - 1], int)])
                            executed_lines += len([1 for line_number in modified_lines if
                                                   isinstance(line_coverage_array[line_number - 1], int) and
                                                   line_coverage_array[line_number - 1] > 0])
            patch_files = PatchExtracts.patch_files(commit, commit_files)
            patch_size = PatchExtracts.patch_sizes(commit, commit_files)

            build.update(patch_files)  # update the
            build.update(patch_size)

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

    async def analyze_coveralls_commits(self, coveralls: CoverallsCoverage):
        builds = await coveralls.collect_builds_data()
        modified_builds = []
        for build in builds:
            try:
                async with asyncio.Lock():
                    await self.checkout_and_analyse_coveralls_commit(build, coveralls)
                    modified_builds.append(build)
            except Exception as err:
                build_commit = build['commit_sha']
                build_repo = build['repository_name']
                print(f"Error checking out repo {build_repo} in commit-{build_commit} - error - {str(err)}")
                continue
        return modified_builds

    async def checkout_and_analyse_codecov_commit(self, build: dict, codecov: CodeCovCoverage) -> None:
        repo_name = build['repository_name']
        git_url = 'https://github.com/{}.git'.format(repo_name)
        for commit in Repository(git_url, single=build['commit_sha']).traverse_commits():
            commit_report = await codecov.commit_report(commit.hash)
            commit_files = codecov.fetch_source_file_names(commit_report)
            api_patch_coverage = codecov.api_patch_coverage(commit_report)  # retrieve patch coverage as per api status
            executed_lines = executable_lines = 0
            if commit_files:
                for m in commit.modified_files:
                    modified_source_file = Utils.index_finder(m.filename, commit_files)
                    if modified_source_file != -1:
                        coverage_array = codecov.file_line_coverage_array(commit_report,
                                                                          commit_files[modified_source_file])
                        if coverage_array:
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
            build.update(patch_files)  # update the
            build.update(patch_size)
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

            build['api_patch_coverage'] = api_patch_coverage
            build['dmm_unit_size'] = dmm_commit_size
            build['dmm_unit_complexity'] = dmm_commit_complexity
            build['dmm_unit_interface'] = dmm_commit_interface
            build['dmm'] = delta_maintainibility_model
            build['crap_metric'] = commit_crappiness

    async def analyze_codecov_commits(self, codecov: CodeCovCoverage):
        builds = await codecov.collect_build_data()
        modified_builds = []
        for build in builds:
            try:
                async with asyncio.Lock():
                    await self.checkout_and_analyse_codecov_commit(build, codecov)
                    modified_builds.append(build)
            except Exception as err:
                build_commit = build['commit_sha']
                build_repo = build['repository_name']
                print(f"Error checking out repo {build_repo} in commit-{build_commit} - error - {str(err)}")
                continue
        return modified_builds
