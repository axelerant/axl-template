"""
Test ComposerPackage click type
"""
import unittest

from axltempl.click_types import ComposerPackage, ComposerPackages


class ComposerPackagesTest(unittest.TestCase):
    def test_valid_package_without_version(self):
        cp = ComposerPackages()
        cplist = cp("drupal/views drupal/ctools")
        self.assertEqual(len(cplist), 2)
        self.assertEqual(cplist[0].get_name(), "drupal/views")
        self.assertEqual(cplist[1].get_name(), "drupal/ctools")

    def test_valid_package_with_version(self):
        cp = ComposerPackages()
        cplist = cp("drupal/views:^3.0 drupal/ctools")
        self.assertEqual(len(cplist), 2)
        self.assertEqual(cplist[0].get_version(), "^3.0")
        self.assertEqual(cplist[1].get_version(), "")

    def test_valid_package_with_complex_version(self):
        cp = ComposerPackages()
        cplist = cp(
            'drupal/views:"^3.0 || ^4.0" drupal/ctool:">1.0 <1.5" drupal/pathauto:"^1.0||^2.0"'
        )
        self.assertEqual(cplist[0].get_version(), '"^3.0 || ^4.0"')
        self.assertEqual(cplist[1].get_version(), '">1.0 <1.5"')
        self.assertEqual(cplist[2].get_version(), "^1.0||^2.0")


class ComposerPackageTest(unittest.TestCase):
    def test_valid_package_without_version(self):
        cp = ComposerPackage()
        views = cp("drupal/views")
        self.assertEqual(views.get_name(), "drupal/views")
        self.assertEqual(views.get_package_vendor(), "drupal")
        self.assertEqual(views.get_package_name(), "views")
        self.assertEqual(views.get_version(), "")

    def test_valid_package_with_version(self):
        cp = ComposerPackage()
        views = cp("drupal/views:^3.0")
        self.assertEqual(views.get_name(), "drupal/views")
        self.assertEqual(views.get_package_vendor(), "drupal")
        self.assertEqual(views.get_package_name(), "views")
        self.assertEqual(views.get_version(), "^3.0")

    def test_valid_package_with_complex_version(self):
        cp = ComposerPackage()
        views = cp('drupal/views:"^3.0 || ^4.0"')
        self.assertEqual(views.get_version(), '"^3.0 || ^4.0"')
