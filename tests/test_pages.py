from app.pages import person_name

import unittest


class MyTestCase(unittest.TestCase):
    def test_person_name(self):
        primo_person_name = "חלפי, אברהם, 1904-1980"
        result = "אברהם חלפי"
        self.assertEqual(result, person_name(primo_person_name))

if __name__ == '__main__':
    unittest.main()
