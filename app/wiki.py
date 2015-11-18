import mwclient
from app.settings import *

def get_wiki_page(page_name, site=WIKI_SITE, user=WIKI_USER, password=WIKI_PASSWORD, path=WIKI_PATH):
    site = mwclient.Site(site, path=path)
    site.login(user, password)
    page = site.Pages[page_name]
    return page

def create_wiki_page(page_name, summary, content, site=WIKI_SITE, user=WIKI_USER, password=WIKI_PASSWORD, path=WIKI_PATH):
    page = get_wiki_page(page_name=page_name, site=site, user=user, password=password, path=path)
    page.save(content, summary)
    return page

def create_redirect_wiki_page(page_name, redirect_to, summary, site=WIKI_SITE, user=WIKI_USER, password=WIKI_PASSWORD, path=WIKI_PATH):
    page = get_wiki_page(page_name=page_name, site=site, user=user, password=password, path=path)
    content = "#REDIRECT [[{}]]".format(redirect_to)
    page.save(content, "Creating redirect from {} to {}".format(page_name, redirect_to))
    return page

def delete_wiki_page(page_name, reason=None, site=WIKI_SITE, user=WIKI_USER, password=WIKI_PASSWORD, path=WIKI_PATH):
    page = get_wiki_page(page_name=page_name, site=site, user=user, password=password, path=path)
    page.delete(reason=reason)
