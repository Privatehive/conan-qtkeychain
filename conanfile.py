#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json, os
from conan import ConanFile
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import patch, copy, download
from conan.tools.build import cross_building, build_jobs
from conan.tools.env import VirtualBuildEnv
from conan.tools.scm import Git

required_conan_version = ">=2.0"


class QtKeychainConan(ConanFile):
    jsonInfo = json.load(open("info.json", 'r'))
    # ---Package reference---
    name = jsonInfo["projectName"]
    version = jsonInfo["version"]
    user = jsonInfo["domain"]
    channel = "stable"
    # ---Metadata---
    description = jsonInfo["projectDescription"]
    license = jsonInfo["license"]
    author = jsonInfo["vendor"]
    topics = jsonInfo["topics"]
    homepage = jsonInfo["homepage"]
    url = jsonInfo["repository"]
    # ---Requirements---
    requires = ["qt/[~6.5]@%s/stable" % user]
    tool_requires = ["cmake/3.21.7", "ninja/1.11.1"]
    # ---Sources---
    exports = ["info.json"]
    exports_sources = ["android_so_names.patch"]
    # ---Binary model---
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True,
                       "fPIC": True,
                       "qt/*:qtbase": True,
                       "qt/*:qttranslations": True}

    def source(self):
        git = Git(self)
        git.run("clone https://github.com/frankosterfeld/qtkeychain.git --branch=%s --depth 1 --single-branch --no-tags --recurse-submodules --shallow-submodules --progress --jobs %u keychain" % (self.version, build_jobs(self)))
        patch(self, base_path="keychain", patch_file="android_so_names.patch")


    def generate(self):
        ms = VirtualBuildEnv(self)
        tc = CMakeToolchain(self, generator="Ninja")
        tc.variables["BUILD_WITH_QT6"] = True
        tc.variables["BUILD_SHARED_LIBS"] = self.options.shared
        tc.generate()
        ms.generate()

    def build(self):
        cmake = CMake(self)
        cmake.configure(build_script_folder="keychain")
        cmake.build()

    def package(self):
        cmake = CMake(self)
        cmake.install()

    def package_info(self):
        self.cpp_info.builddirs = ["lib/cmake"]
