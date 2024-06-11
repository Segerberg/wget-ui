import os
from jinja2 import Environment, FileSystemLoader
import hashlib
from datetime import datetime, timezone
import uuid
import tarfile

def create_uuid():
    id = uuid.uuid4()
    return str(id)

def get_file_stats(file_path):
    stat = os.stat(file_path)
    try:
        creation_time = stat.st_birthtime
    except AttributeError:
        creation_time = stat.st_ctime

    creation_datetime = datetime.fromtimestamp(creation_time, tz=timezone.utc)
    creation_datetime = creation_datetime.astimezone()  # Convert to local timezone
    creation_date_str = creation_datetime.isoformat()
    return creation_date_str


def create_tar(folder_path, tar_name):
    """
    Create a TAR file from all files in the specified folder.

    Parameters:
    folder_path (str): The path to the folder containing the files to be archived.
    tar_name (str): The name of the output TAR file.
    """
    # Create a tar file
    with tarfile.open(tar_name, "w") as tar:
        # Walk through all files in the folder
        for root, dirs, files in os.walk(folder_path):
            for file in files:
                file_path = os.path.join(root, file)
                # Add each file to the tar file
                tar.add(file_path, arcname=os.path.relpath(file_path, folder_path))


def calculate_md5(file_path, chunk_size=4096):
    """
    Calculate the MD5 checksum of a file.

    :param file_path: Path to the file.
    :param chunk_size: Size of chunks to read the file in bytes. Default is 4096.
    :return: MD5 checksum as a string.
    """
    md5 = hashlib.md5()

    try:
        with open(file_path, 'rb') as file:
            for chunk in iter(lambda: file.read(chunk_size), b''):
                md5.update(chunk)
    except FileNotFoundError:
        return f"Error: The file {file_path} does not exist."
    except Exception as e:
        return f"Error: An unexpected error occurred: {e}"

    return md5.hexdigest()


def create_xml(target, data, template_path):
    file_loader = FileSystemLoader('./app')
    env = Environment(loader=file_loader)
    template = env.get_template(template_path)
    output = template.render(data=data, target=target, uuid=uuid)
    return output


def bytes_to_human_readable(byte_value: int) -> str:
    """
    Convert bytes to a human-readable format (KB, MB, GB, TB).

    Args:
        byte_value (int): The byte value to convert.

    Returns:
        str: The human-readable string representation of the byte value.
    """
    if byte_value < 1024:
        return f"{byte_value} B"
    elif byte_value < 1024 ** 2:
        return f"{byte_value // 1024} KB"
    elif byte_value < 1024 ** 3:
        return f"{byte_value // (1024 ** 2)} MB"
    elif byte_value < 1024 ** 4:
        return f"{byte_value // (1024 ** 3)} GB"
    elif byte_value < 1024 ** 5:
        return f"{byte_value // (1024 ** 4)} TB"
    else:
        return f"{byte_value // (1024 ** 5)} PB"