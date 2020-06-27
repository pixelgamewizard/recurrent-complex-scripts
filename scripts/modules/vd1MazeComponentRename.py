def vd1_maze_component_rename(json_dict, old_name, new_name):
    found_component = False
    if 'generationInfos' in json_dict:
        generation_infos = json_dict['generationInfos']
        for generation_info in generation_infos:
            if generation_info['type'] == 'mazeComponent':
                generation_info_inner = generation_info['generationInfo']
                if generation_info_inner['mazeID'] == old_name:
                    generation_info_inner['mazeID'] = new_name
                    found_component = True
    return found_component, json_dict
