class FileOperator:
    @staticmethod
    def read_file(file_path: str) -> str:
        """Read file content"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        except Exception as e:
            return f"Error reading file: {str(e)}"

    @staticmethod
    def write_file(file_path: str, content: str) -> bool:
        """Write content to file"""
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            return True
        except Exception as e:
            print(f"Error writing file: {str(e)}")
            return False