import asyncio
from pydriller import Repository
from src.codecov import CodeCovCoverage
from src.coveralls import CoverallsCoverage
from utils import Utils
from patch_extracts import PatchExtracts
from crap_metric import CrapMetric


class CoverageImporter:
    async def checkout_and_analyse_coveralls_commit(self, build: dict, coveralls: CoverallsCoverage) -> None:
        repo_name = build['repository_name']
        git_url = 'https://github.com/{}.git'.format(repo_name)
        for commit in Repository(git_url, single=build['commit_sha']).traverse_commits():
            commit_files = await coveralls.fetch_source_files(build['commit_sha'])
            executable_lines = executed_lines = 0
            patch_extracts = PatchExtracts()
            if commit_files:
                for m in commit.modified_files:
                    filename_index = Utils.index_finder(m.filename, commit_files)
                    if filename_index != -1:
                        coverage_array = await coveralls.source_coverage_array(commit.hash,
                                                                               commit_files[filename_index])
                        if coverage_array:
                            modified_lines = [line_number[0] for line_number in m.diff_parsed['added']]
                            executable_lines += len([1 for line_number in modified_lines if
                                                     isinstance(coverage_array[line_number - 1], int)])
                            executed_lines += len([1 for line_number in modified_lines if
                                                   isinstance(coverage_array[line_number - 1], int) and
                                                   coverage_array[line_number - 1] > 0])
            patch_files = patch_extracts.patch_files(commit, commit_files)
            patch_size = patch_extracts.patch_sizes(commit, commit_files)

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
            build['dmm_unit_size'] = dmm_commit_size
            build['dmm_unit_complexity'] = dmm_commit_complexity
            build['dmm_unit_interface'] = dmm_commit_interface
            build['dmm'] = delta_maintainibility_model
            build['crap_metric'] = commit_crappiness

    async def analyze_commits(self, coveralls: CoverallsCoverage):
        builds = await coveralls.collect_builds_data()
        modified_builds = []
        for build in builds:
            try:
                async with asyncio.Lock():
                    await self.checkout_and_analyse_coveralls_commit(build, build['commit_sha'])
                    modified_builds.append(build)
            except Exception as err:
                build_commit = build['commit_sha']
                build_repo = build['repository_name']
                print(f"Error checking out repo {build_repo} in commit-{build_commit} - error - {str(err)}")
                continue
        return modified_builds