from app.pages import simple_person_name, comma_and, trim, is_hebrew

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

    def test_trim(self):
        non_trimmed = "abc ... (def) ..."
        trimmed = "abc ... (def)"
        self.assertEqual(trimmed, trim(non_trimmed))
        non_trimmed = 'abc "def" ..#$'
        trimmed = 'abc "def"'
        self.assertEqual(trimmed, trim(non_trimmed))

    def test_is_hebrew(self):
        self.assertTrue(is_hebrew("שי"))
        self.assertTrue(is_hebrew("Moshe משה"))
        self.assertFalse(is_hebrew("Shai"))


if __name__ == '__main__':
    unittest.main()
