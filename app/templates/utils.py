from app.authorities import to_list

VIEW_TEMPLATE = '''|<img src="http://rosetta.nli.org.il/delivery/DeliveryManagerServlet?dps_pid={}&dps_func=thumbnail"/>
|-
'''

find_ie = re.compile(r"dps_pid=(IE\d+)").search

# This function returns a thumbnail link


def generate_thumb(rosetta_links):
    ies = [find_ie(link).group(1) for link in to_list(rosetta_links) if find_ie(link)]
    if ies:
        return VIEW_TEMPLATE.format(ies[0])
    return ''

# This function extract elements in a string according to the $$ delimeter


def extract_link(links):
    return to_list(links)[0].split('$$')[1][1:]
