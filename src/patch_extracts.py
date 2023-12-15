from pydriller import Commit


class PatchExtracts:
    @staticmethod
    def patch_sizes(commit: Commit, covered_files: list[str]) -> dict:
        code_patch_size = test_patch_size = config_patch_size = 0
        for m in commit.modified_files:
            if any(m.filename.lower() in filename.lower() for filename in covered_files):
                if 'test' in m.filename.lower():
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
    def patch_files(commit: Commit, covered_files: list[str]) -> dict:
        code_count = test_count = 0
        for m in commit.modified_files:
            if any(m.filename.lower() in filename.lower() for filename in covered_files):
                if 'test' in m.filename.lower():
                    test_count += 1
                else:
                    code_count += 1
        return {
            'test_files': 1 if code_count == 0 and test_count > 0 else 0,
            'code_files': 1 if code_count > 0 and test_count == 0 else 0,
            'test_code_files': 1 if code_count > 0 and test_count > 0 else 0,
            'other_files': 1 if code_count == 0 and test_count == 0 else 0,
        }
