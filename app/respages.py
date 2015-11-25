from app import primo_comm, pages
for result, _ in zip(primo_comm.Results("בן גוריון", 5), range(5)):
    try:
        pages.create_page_from_dictionary(result)
    except Exception as e:
        print(e)