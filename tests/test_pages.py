from app.pages import simple_person_name, comma_and

import unittest


class MyTestCase(unittest.TestCase):
    def test__simple_person_name(self):
        primo_person_name = "חלפי, אברהם, 1904-1980"
        result = "אברהם חלפי"
        self.assertEqual(result, simple_person_name(primo_person_name))

    def test_comma_and(self):
        comma_separated = "משה, אילנה, ברוך"
        result = "משה, אילנה וברוך"
        self.assertEqual(result, comma_and(comma_separated))
        no_commas = "מלכת שבא"
        self.assertEqual(no_commas, comma_and(no_commas))

if __name__ == '__main__':
    unittest.main()
