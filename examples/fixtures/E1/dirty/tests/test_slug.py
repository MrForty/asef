import unittest

from slug import slugify


class SlugTest(unittest.TestCase):
    def test_spaces(self):
        self.assertEqual(slugify("Hello World"), "hello-world")

    def test_accents(self):
        self.assertEqual(slugify("Caffè Perché"), "caffe-perche")


if __name__ == "__main__":
    unittest.main()
