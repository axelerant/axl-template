import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="axl-template",  # Replace with your own username
    version="0.2.0",
    author="hussainweb",
    author_email="hussainweb@gmail.com",
    description="Scaffold a Drupal site template",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/axelerant/axl-template",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3",
    ],
    keywords="drupal",
    include_package_data=True,
    install_requires=["Click",],
    entry_points={
        "console_scripts": [
            "init-drupal = axltempl.drupal:main",
            "init-lando = axltempl.lando:main",
            "init-renovate = gitlabrenovate.main:scaffold",
        ]
    },
    python_requires=">=3.6",
)
