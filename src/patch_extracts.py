from pydriller import Commit
from src.utils import Utils


class PatchExtracts:
    @staticmethod
    def patch_sizes(commit: Commit, covered_files: list[str]) -> dict:
        code_patch_size = test_patch_size = config_patch_size = 0
        for m in commit.modified_files:
            if any(m.filename.lower() in filename.lower() for filename in covered_files):
                index = Utils.index_finder(m.filename.lower(), covered_files)
                full_filename_path = covered_files[index]
                if 'test' in full_filename_path.lower():
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
                index = Utils.index_finder(m.filename.lower(), covered_files)
                full_filename_path = covered_files[index]
                if 'test' in full_filename_path.lower():
                    test_count += 1
                else:
                    code_count += 1
        return {
            'test_files': 1 if code_count == 0 and test_count > 0 else 0,  # Test only
            'code_files': 1 if code_count > 0 and test_count == 0 else 0,  # code only
            'test_code_files': 1 if code_count > 0 and test_count > 0 else 0,  # Test and files
            'other_files': 1 if code_count == 0 and test_count == 0 else 0,  # Config Only
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
