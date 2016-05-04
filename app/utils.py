import re
from app.authorities import to_list

find_ie = re.compile(r"dps_pid=(IE\d+)").search


def generate_thumb_link(rosetta_links):
    """
    This function returns a thumbnail link
    :param rosetta_links: links that contain IE PID in them
    :return: the IE PID
    """
    ies = [find_ie(link).group(1) for link in to_list(rosetta_links) if find_ie(link)]
    if ies:
        return ies
    return ''


def extract_link(links):
    """
    This function extract elements in a string according to the $$ delimiter
    :param links: Links to extract data from
    :return: list of strings
    """
    return to_list(links)[0].split('$$')[1][1:]
