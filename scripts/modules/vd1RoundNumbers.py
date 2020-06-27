import logging


_sampled_numbers = set()
_sampled_numbers.add(1.0)
for factor in range(6, 11):
    for sample in range(1, factor):
        _sampled_numbers.add(sample / float(factor))
_sampled_numbers.add(0.05)
_sampled_numbers.add(0.95)


def round_number(number):
    if number == 0.0:
        return number

    power_of_ten_undefined = -10
    power_of_ten = power_of_ten_undefined
    for power_of_ten_candidate in range(-4, 6):
        lower_range = pow(10, power_of_ten_candidate - 1)
        upper_range = pow(10, power_of_ten_candidate)
        if lower_range <= number <= upper_range:
            power_of_ten = power_of_ten_candidate
            break

    if power_of_ten == power_of_ten_undefined:
        logging.error('Number ' + str(number) + ' is out of expected range. Returning.')
        return number

    rounded_number = 0.5 * pow(10, power_of_ten)
    for sampled_number in _sampled_numbers:
        best_distance = abs(number - rounded_number)
        distance = abs(number - sampled_number)
        if distance < best_distance:
            rounded_number = sampled_number

    return rounded_number


def vd1_round_numbers(json_dict):
    found_numbers = False

    if 'generationInfos' in json_dict:
        generation_infos = json_dict['generationInfos']
        for generation_info in generation_infos:
            if generation_info['type'] == 'mazeComponent':
                generation_info_inner = generation_info['generationInfo']
                if 'weight' in generation_info_inner:
                    generation_info_inner['weight'] = round_number(generation_info_inner['weight'])
                    found_numbers = True

    if 'variableDomain' in json_dict:
        variable_domain = json_dict['variableDomain']
        if 'variables' in variable_domain:
            variables = variable_domain['variables']
            for variable in variables:
                if 'chance' in variable:
                    variable['chance'] = round_number(variable['chance'])
                    found_numbers = True

    return found_numbers, json_dict
