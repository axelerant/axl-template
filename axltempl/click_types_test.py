"""
Test ComposerPackage click type
"""
import unittest

from axltempl.click_types import ComposerPackage


class ClickTypesTest(unittest.TestCase):
    def test_valid_package_without_version(self):
        cp = ComposerPackage()
        views = cp("drupal/views")[0]
        self.assertEqual(views.get_name(), "drupal/views")
        self.assertEqual(views.get_package_vendor(), "drupal")
        self.assertEqual(views.get_package_name(), "views")
        self.assertEqual(views.get_version(), "")

    def test_valid_package_with_version(self):
        cp = ComposerPackage()
        views = cp("drupal/views:^3.0")[0]
        self.assertEqual(views.get_name(), "drupal/views")
        self.assertEqual(views.get_package_vendor(), "drupal")
        self.assertEqual(views.get_package_name(), "views")
        self.assertEqual(views.get_version(), "^3.0")

    def test_valid_package_with_complex_version(self):
        cp = ComposerPackage()
        views = cp('drupal/views:"^3.0 || ^4.0"')[0]
        self.assertEqual(views.get_version(), "^3.0 || ^4.0")
