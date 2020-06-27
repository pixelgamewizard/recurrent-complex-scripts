def vd1_maze_component_zero_weights(json_dict, maze_name):
    found_component = False
    if 'generationInfos' in json_dict:
        generation_infos = json_dict['generationInfos']
        for generation_info in generation_infos:
            if generation_info['type'] == 'mazeComponent':
                generation_info_inner = generation_info['generationInfo']
                if generation_info_inner['mazeID'] == maze_name:
                    generation_info_inner['weight'] = 0.0
                    found_component = True
    return found_component, json_dict
