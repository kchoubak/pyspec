from configparser import ConfigParser


def config(filename: str, section: str):
    """
    load configuration properties
    :param filename:
    :param section:
    :return:
    """
    # create a parser
    parser = ConfigParser()
    # read config file
    parser.read(filename)

    # get section, default to postgresql
    db = {}
    if parser.has_section(section):
        params = parser.items(section)
        for param in params:
            db[param[0]] = param[1]
    else:
        raise Exception('Section {0} not found in the {1} file, sections are {2}'.format(section, filename, parser.sections()))

    return db
