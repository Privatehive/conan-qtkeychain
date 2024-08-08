#!/usr/bin/env python
# -*- coding: utf-8 -*-

from conan import ConanFile
from conan.errors import ConanInvalidConfiguration
from conan.tools.cmake import CMake, CMakeToolchain
from conan.tools.files import patch, get
from conan.tools.env import VirtualBuildEnv
import json

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
    requires = ["qt/[>=6.5.0]@%s/stable" % user]
    tool_requires = ["cmake/[>=3.21.7]", "ninja/[>=1.11.1]"]
    # ---Sources---
    exports = ["info.json"]
    exports_sources = ["patches/*"]
    # ---Binary model---
    settings = "os", "compiler", "build_type", "arch"
    options = {"shared": [True, False], "fPIC": [True, False]}
    default_options = {"shared": True,
                       "fPIC": True,
                       "qt/*:qtbase": True,
                       "qt/*:dbus": True,
                       "qt/*:qttools": True,
                       "qt/*:qtdbus": True,
                       "qt/*:qttranslations": True}

    def validate(self):
        valid_os = ["Windows", "Linux", "Android"]
        if str(self.settings.os) not in valid_os:
            raise ConanInvalidConfiguration(f"{self.name} {self.version} is only supported for the following operating systems: {valid_os}")
        valid_arch = ["x86_64", "x86", "armv7", "armv8"]
        if str(self.settings.arch) not in valid_arch:
            raise ConanInvalidConfiguration(f"{self.name} {self.version} is only supported for the following architectures on {self.settings.os}: {valid_arch}")

    def source(self):
        #git = Git(self)
        #git.run("clone https://github.com/frankosterfeld/qtkeychain.git --branch=%s --depth 1 --single-branch --no-tags --recurse-submodules --shallow-submodules --progress --jobs %u keychain" % (self.version, build_jobs(self)))
        get(self, "https://github.com/frankosterfeld/qtkeychain/archive/refs/tags/%s.tar.gz" % self.version, destination="keychain", strip_root=True)
        patch(self, base_path="keychain", patch_file="patches/android_so_names.patch")

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
