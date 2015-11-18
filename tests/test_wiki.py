__author__ = 'shaih'
import unittest
from uuid import uuid4 # used to generate some random sequences
from app.wiki import get_wiki_page, delete_wiki_page, create_wiki_page, create_redirect_wiki_page

class WikiTestCase(unittest.TestCase):
    def _delete_page(self, page_name):
        try:
            delete_wiki_page(page_name)
        except:
            # page didn't exist in the first place
            pass

    def test_page_creation_deletion(self):
        # test creation & get
        content = "Some content {}".format(uuid4())
        page_name = "New page {}".format(uuid4())
        self._delete_page(page_name) # make sure it doesn't exist
        page = create_wiki_page(page_name=page_name, content=content, summary="Unit test")
        print("Created page", page)
        page = get_wiki_page(page_name)
        self.assertEqual(content, page.text())
        # test deletion - if page doesn't exist then an execption would be thrown
        page.delete(reason="Unit test finished")
        print("Deleted page", page)
        non_existing_page = get_wiki_page(page_name)
        self.assertFalse(non_existing_page.text())

    def test_redirect(self):
        redirect_to_name = "Redirect here {}".format(uuid4())
        redirect_from_name = "Redirect from {}".format(uuid4())
        content = "Some content {}".format(uuid4())
        create_wiki_page(page_name=redirect_to_name, content=content, summary="Unit test")
        create_redirect_wiki_page(page_name=redirect_from_name, redirect_to=redirect_to_name, summary="Unit test")
        redirect_from = get_wiki_page(page_name=redirect_from_name)
        redirect_to = get_wiki_page(page_name=redirect_to_name)
        self.assertEqual(redirect_from.redirects_to().text(), redirect_to.text())
        # cleanup
        redirect_from.delete(reason="Unit test finished")
        redirect_to.delete(reason="Unit test finished")

if __name__ == '__main__':
    unittest.main()
