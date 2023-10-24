import os

def get_config_dict(config_file):
    res_dict = {}
    with open(config_file, 'r') as file:
        for line in file:
            line = line.strip()
            if line.startswith('#') or line.startswith('[') or line == '':
                continue

            key, value = line.split('=')
            key = key.strip()
            value = value.strip()
            res_dict[key] = value
    
    return res_dict


if __name__ == '__main__':
    config_dict = get_config_dict('mysql_template.cnf.bak')
    print(config_dict)