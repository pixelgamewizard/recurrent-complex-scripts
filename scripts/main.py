import argparse
import json
import logging
import os
import shutil
import zipfile

import modules


class FileFormatException(Exception):
    pass


class PathNotAcceptedException(Exception):
    pass


def load_operation_list(filepath):
    if not os.path.exists(filepath):
        raise PathNotAcceptedException('Operation list ' + str(filepath) + ' does not exist.')
    if not os.path.isfile(filepath):
        raise PathNotAcceptedException('Operation list ' + str(filepath) + ' is not a file.')
    json_file = open(filepath, mode='r')
    json_input_text = json_file.read()
    json_file.close()
    try:
        json_dict = dict(json.loads(json_input_text))
    except json.JSONDecodeError as exception:
        raise FileFormatException('File is not in JSON format; ' + str(exception))
    return json_dict


def verify_rcst_directory(directory):
    success = True
    problems = str()
    contents = os.listdir(directory)
    for content in contents:
        content_path = os.path.join(directory, content)
        if not os.path.isfile(content_path):
            problems = problems + 'Found content that was not a file: ' + str(content) + '. '
            success = False
        if not zipfile.is_zipfile(content_path):
            problems = problems + 'Found content that was not .rcst (zip) format: ' + str(content) + '. '
            success = False
    if not success:
        raise FileFormatException(problems)


def make_directory_empty(directory):
    if not isinstance(directory, str):
        raise PathNotAcceptedException('Path is not of type str.')

    if not os.path.exists(directory):
        os.mkdir(directory)

    if not os.path.isdir(directory):
        raise PathNotAcceptedException('Path is not a directory: ' + str(directory))

    contents = os.listdir(directory)
    for content in contents:
        content_path = os.path.join(directory, content)
        if os.path.isfile(content_path):
            os.remove(content_path)
        elif os.path.isdir(content_path):
            shutil.rmtree(content_path, ignore_errors=True)
        else:
            raise PathNotAcceptedException(
                'Path ' + str(directory) + ' contains something that is not a file or folder: ' + str(content))


def main():
    parser = argparse.ArgumentParser(description='Process recurrent complex files')
    parser.add_argument('--inputDir', action='store', type=str, required=True,
                        help='Directory where original files are stored')
    parser.add_argument('--tempDir', action='store', type=str, required=True,
                        help='Directory where intermediate files are stored')
    parser.add_argument('--outputDir', action='store', type=str, required=True,
                        help='Directory where processed files are stored')
    parser.add_argument('--operationList', action='store', type=str, required=True,
                        help='JSON file containing the configuration.')
    args = vars(parser.parse_args())

    # pre-processing
    input_dir = os.path.join(args['inputDir'])
    try:
        verify_rcst_directory(input_dir)
    except FileFormatException as exception:
        logging.error('Found unexpected content in input directory; ' + str(exception))
        return -1

    temp_dir = os.path.join(args['tempDir'])
    output_dir = os.path.join(args['outputDir'])
    try:
        make_directory_empty(temp_dir)
        make_directory_empty(output_dir)
    except PathNotAcceptedException as exception:
        logging.error('Failed to prepare directories; ' + str(exception))
        return -1

    try:
        operation_list = load_operation_list(os.path.join(args['operationList']))['operation_list']
    except PathNotAcceptedException or FileFormatException as exception:
        logging.error('Failed to load operation list; ' + str(exception))
        return -1

    # processing
    input_files = os.listdir(input_dir)
    for filename in input_files:
        input_filepath = os.path.join(input_dir, filename)
        input_zipfile = zipfile.ZipFile(input_filepath, 'r')
        basename, _ = os.path.splitext(filename)
        temp_path = os.path.join(temp_dir, basename)
        os.mkdir(temp_path)
        input_zipfile.extractall(temp_path)

        structure_filepath = os.path.join(temp_path, 'structure.json')
        structure_json_file = open(structure_filepath, mode='r')
        structure_json_input_text = structure_json_file.read()
        structure_json_file.close()
        structure_json = dict(json.loads(structure_json_input_text))

        for operation in operation_list:
            if 'type' not in operation:
                logging.error('missing type for operation in operation list.')
                continue
            operation_type = operation['type']
            if operation_type == 'vd1_round_numbers':
                found_numbers, structure_json = modules.vd1_round_numbers(structure_json)
                if not found_numbers:
                    logging.warning('Did not find numbers in file ' + str(filename))
            elif operation_type == 'vd1_maze_component_clone':
                old_name = operation['old_name']
                new_name = operation['new_name']
                found_component, structure_json = modules.vd1_maze_component_clone(structure_json, old_name, new_name)
                if not found_component:
                    logging.warning('Did not find maze component ' + str(old_name) + ' in file ' + str(filename) + '.')
            elif operation_type == 'vd1_maze_component_rename':
                old_name = operation['old_name']
                new_name = operation['new_name']
                found_component, structure_json = modules.vd1_maze_component_rename(structure_json, old_name, new_name)
                if not found_component:
                    logging.warning('Did not find maze component ' + str(old_name) + ' in file ' + str(filename) + '.')
            elif operation_type == 'vd1_maze_component_zero_weights':
                maze_name = operation['maze_name']
                found_component, structure_json = modules.vd1_maze_component_zero_weights(structure_json, maze_name)
                if not found_component:
                    logging.warning('Did not find maze component ' + str(maze_name) + ' in file ' + str(filename) + '.')
            else:
                logging.error('Unexpected operation ' + str(operation_type) + '. Skipping.')

        structure_json_output_text = json.dumps(structure_json)
        structure_json_file = open(structure_filepath, mode='w')
        structure_json_file.write(structure_json_output_text)
        structure_json_file.close()

        world_data_filepath = os.path.join(temp_path, 'worldData.nbt')
        output_filepath = os.path.join(output_dir, filename)
        output_zipfile = zipfile.ZipFile(output_filepath, mode='w', compression=zipfile.ZIP_DEFLATED, compresslevel=4)
        output_zipfile.write(filename=structure_filepath, arcname='structure.json')
        output_zipfile.write(filename=world_data_filepath, arcname='worldData.nbt')

    return 0


main()
