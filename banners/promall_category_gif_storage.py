from django.core.files.storage import FileSystemStorage


class PromallCategoryGIFStorage(FileSystemStorage):
    """
    Storage dedicated to PROMALLSHOP Category GIFs.
    Uses fixed filenames such as 18.gif.
    """

    def get_available_name(self, name, max_length=None):
        # Category GIF filenames are controlled by the model.
        return name

    def _save(self, name, content):
        # FileSystemStorage normally avoids overwriting existing files.
        # Replace the existing file through a temporary file instead.
        import os
        import tempfile

        full_path = self.path(name)
        directory = os.path.dirname(full_path)
        os.makedirs(directory, exist_ok=True)

        temporary_path = None

        try:
            with tempfile.NamedTemporaryFile(
                mode="wb",
                dir=directory,
                prefix=".promall_gif_",
                suffix=".tmp",
                delete=False,
            ) as temporary_file:
                temporary_path = temporary_file.name

                for chunk in content.chunks():
                    temporary_file.write(chunk)

            os.replace(temporary_path, full_path)
            temporary_path = None

        finally:
            if temporary_path and os.path.exists(temporary_path):
                os.unlink(temporary_path)

        return name
