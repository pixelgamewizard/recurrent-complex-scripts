import copy
import secrets


def generate_id():
    return 'mazeComponent_' + str(secrets.token_hex(4))


def vd1_maze_component_clone(json_dict, old_name, new_name):
    found_component = False
    if 'generationInfos' in json_dict:
        generation_infos = json_dict['generationInfos']
        for generation_info in generation_infos:
            if generation_info['type'] == 'mazeComponent':
                generation_info_inner = generation_info['generationInfo']
                if generation_info_inner['mazeID'] == old_name:
                    cloned_generation_info = copy.deepcopy(generation_info)
                    cloned_generation_info['generationInfo']['mazeID'] = new_name
                    cloned_generation_info['generationInfo']['id'] = generate_id()
                    generation_infos.append(cloned_generation_info)
                    found_component = True
    return found_component, json_dict
