import requests
import tempfile
import os
import shutil
from jinja2 import Template
from zipfile import ZipFile
import logging
import webbrowser

# Name of src directory
SRC_DIR = 'src'

# Atmel Start home.
_URL_ATMEL_START = 'http://start.atmel.com/'
# Backend API v1
_URL_API_v1 = _URL_ATMEL_START + 'api/v1/'
# Backend API v2
_URL_API_v2 = _URL_ATMEL_START + 'api/v2/'
# Endpoint to request the conversion from YAML ("storage") to JSON ("transport")
_URL_LATEST_TRANSPORT = _URL_API_v2 + 'project_format/transport/latest'
# Endpoint to request the conversion from JSON ("transport") to YAML ("storage")
_URL_LATEST_STORAGE = _URL_API_v1 + 'project_format/storage/latest'
# Endpoint to request to generate the project code given the JSON config.
_URL_GENERATE = _URL_API_v1 + 'generate/?format=atzip&compilers=[atmel_studio,make]&file_name_base=My%20Project'


def init(project_directory, project_name):
    """
    Initializes a project.

    It creates a src/ directory, generates a CMakeLists.txt for cmake and
    :param project_directory: The directory that shall be used for the project
    :param project_name: the project name
    :return:
    """
    logger = logging.getLogger(__name__)
    # make src directory
    src_dirname = os.path.join(project_directory, SRC_DIR)
    if not os.path.isdir(src_dirname):
        logging.info('Creating src/ directory...')
        os.mkdir(src_dirname)
    else:
        logging.warn('src/ directory already exists. Ignoring.')

    # generate CMakeLists.txt if not existing
    cmakelists_filename = os.path.join(project_directory, 'CMakeLists.txt')
    if os.path.isfile(cmakelists_filename):
        logger.error('CMakeLists.txt already exists.')
        exit(-1)
    # Read, render and write template
    logging.info('Generating CMakeLists.txt...')
    with open(os.path.join(os.path.dirname(__file__), '../templates/CMakeLists.txt'), 'r') as file:
        content = file.read()
    template = Template(content)
    cmakelists = template.render(project_name=project_name)
    with open(os.path.join(cmakelists_filename), 'w') as file:
        file.write(cmakelists)
    logging.info('Successfully generated CMakeLists.txt')


def edit(atmel_start_config_filename):
    """

    :param atmel_start_config_filename:
    :return:
    """
    pass


def _request_json(atmel_start_config_filename):
    """
    Takes an atmel start config file (YAML format) and converts it into JSON. Returns as dictionary structure.

    :param atmel_start_config_filename: filename of atmel start config file
    :return: A dictionary structure representing the JSON config file.
    """
    with open(atmel_start_config_filename, 'rb') as file:
        config = file.read()
    response = requests.post(_URL_LATEST_TRANSPORT, data=config, headers={'Content-type': 'application/json'})
    if response.status_code != 200:
        raise Exception('Retrieving JSON from YAML failed. Http Status: {0}'.format(response.status_code))
    return response.json()['result']['project']


def generate(atmel_start_config_filename, file):
    """
    Generates the atmel start project.

    It takes a configuration described by a dictionary structure and returns a filename to zip file containing the
    project
    :param atmel_start_config_filename: atmel start configuration file
    :param file: open file descriptor to where the project zip file is written to
    :return:
    """
    logger = logging.getLogger(__name__)
    logger.info('Generating atmel start project from configuration file...')
    config_json = _request_json(atmel_start_config_filename)
    response = requests.post(_URL_GENERATE, json=config_json)
    if response.status_code != 200:
        raise Exception('Generation failed. Status code: {0}'.format(response.status_code))

    # Write the file contents in the response to a file specified by local_file_path
    for chunk in response.iter_content(chunk_size=128):
        file.write(chunk)


def extract_zip_file(file, directory):
    """
    Extracts all files from a zip file into the given directory.

    :param file: file descriptor to a file containing the zip archive
    :param directory: the directory to which the zip file shall be extracted
    :return:
    """
    with ZipFile(file, 'r') as f_zip:
        f_zip.extractall(directory)


def retrieve_and_replace_project(atmel_start_config_filename, atmel_start_project_directory):
    """
    Generates a project from a configuration file and extracts it into the specified project directory.

    If the project directory exists its contents will be removed first.

    :param atmel_start_config_filename: atmel start configuration file
    :param atmel_start_project_directory: atmel start project directory
    :return:
    """
    # generate project file from configuration and extract it into the atmel start project directory
    logger = logging.getLogger(__name__)
    with tempfile.TemporaryFile() as file:
        generate(atmel_start_config_filename, file)
        # remove all contents of the atmel start project directory if it exists
        logger.info('Removing old project files...')
        if os.path.isdir(atmel_start_project_directory):
            shutil.rmtree(atmel_start_project_directory)
        # extract files
        logging.info('Extracting new project files...')
        os.mkdir(atmel_start_project_directory)
        extract_zip_file(file, atmel_start_project_directory)
