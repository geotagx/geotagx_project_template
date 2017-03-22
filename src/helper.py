# -*- coding: utf-8 -*-
#
# This module is part of the GeoTag-X project build tool.
# It contains miscellaneous helper functions.
#
# Author: Jeremy Othieno (j.othieno@gmail.com)
#
# Copyright (c) 2016-2017 UNITAR/UNOSAT
#
# The MIT License (MIT)
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
# EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
# MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
# IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM,
# DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR
# OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE
# OR OTHER DEALINGS IN THE SOFTWARE.
from geotagx_validator.helper import check_arg_type

def get_formatted_configuration_set(path, enable_logging=False):
    """Returns a set of formatted configurations for the GeoTag-X project
    located at the specified path.

    Args:
        path (str): A path to a directory containing a GeoTag-X project.
        enable_logging (bool): If set to True, the function will log most of its operations.

    Returns:
        dict|None: A dictionary containing a set of formatted configurations if the specified
            path contains a valid GeoTag-X project, None otherwise.

    Raises:
        TypeError: If the path argument is not a string or enable_logging is not a boolean.
        IOError: If the specified path is inaccessible or not a directory, or if a required
            configuration in the directory at the specified path is inaccessible.
    """
    check_arg_type(get_formatted_configuration_set, "path", path, basestring)
    check_arg_type(get_formatted_configuration_set, "enable_logging", enable_logging, bool)

    from geotagx_validator.helper import deserialize_configuration_set
    from geotagx_formatter.core import format_configuration_set

    return format_configuration_set(deserialize_configuration_set(path), enable_logging)


def generate_html(configuration_set, path, overwrite=False, compress=False):
    """Generates the template.html, tutorial.html and results.html files from the
    specified configuration set, and writes them to the directory at the given path.

    Args:
        configuration_set (dict): A set of project configurations used to generate the
            HTML files.
        path (str): A path to a directory where the generated files will be written to.
        overwrite (bool): If set to True, any previously generated HTML files located at
            the specified path will be overwritten.
        compress (bool): If set to True, the generated HTML will be compressed.

    Raises:
        TypeError: If the configuration_set argument is not a dictionary, path is not a
            string, overwrite is not a boolean, or compress is not a boolean.
        IOError: If the specified path is inaccessible or not a writable directory, or if a
            required configuration in the directory at the specified path is inaccessible.
        ValueError: If the specified configuration set is not valid.
    """
    check_arg_type(generate_html, "configuration_set", configuration_set, dict)
    check_arg_type(generate_html, "path", path, basestring)
    check_arg_type(generate_html, "overwrite", overwrite, bool)
    check_arg_type(generate_html, "compress", compress, bool)

    from geotagx_validator.core import is_configuration_set
    from geotagx_validator.helper import is_directory
    from geotagx_formatter.helper import to_json_string
    from collections import OrderedDict
    import os

    valid, message = is_configuration_set(configuration_set)
    if not valid:
        raise ValueError(message)
    elif not is_directory(path, check_writable=True):
        raise IOError("The path '{}' is not a writable directory. Please make sure you have the appropriate access permissions.".format(path))

    output = {
        "task_presenter": os.path.join(path, "template.html"),
        "tutorial": os.path.join(path, "tutorial.html"),
        "results": os.path.join(path, "results.html"),
    }
    if not overwrite and any(os.path.isfile(f) for f in output.values()):
        raise IOError("The directory '{}' already contains a task presenter (template.html) and/or a tutorial (tutorial.html). To overwrite either, set the '-f' or '--force' flag.".format(path))

    # Remove redundant configuration fields before they are written to the HTML files.
    # Note that if need be, these fields can be retrieved from a PyBossa project instance.
    project_configuration = configuration_set["project"]
    old_project_configuration = OrderedDict(project_configuration)
    for key in ["name", "short_name", "description"]:
        project_configuration.pop(key, None)

    # Write a dummy results.html page. While the results.html page is not currently
    # used by GeoTag-X projects, it is still required by PyBossa's 'pbs'
    # command-line tool.
    open(output["results"], "w").close()

    # Write the project's tutorial. Note that if no tutorial configuration exists,
    # an empty 'tutorial.html' file is still created because (just like results.html)
    # it is required by PyBossa's 'pbs' command-line tool.
    with open(output["tutorial"], "w") as file:
        if "tutorial" in configuration_set:
            file.write(to_json_string(configuration_set))
            # Remove the tutorial configuration so it's not written to the
            # template.html file created below.
            configuration_set.pop("tutorial", None)

    # Write the task presenter.
    with open(output["task_presenter"], "w") as file:
        file.write(to_json_string(configuration_set))

    # Restore the deleted configuration fields.
    configuration_set["project"] = old_project_configuration
