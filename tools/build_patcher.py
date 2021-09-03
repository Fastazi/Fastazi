'''
This file is part of an ICSE'22 submission that is currently under review.

================================================================

This script modifies build.xml or pom.xml files (for Ant and Maven)
in order to incorporate Ekstazi test case selection into the
build process.

================================================================

This is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as 
published by the Free Software Foundation, either version 3 of the 
License, or (at your option) any later version.

This software is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this source.  If not, see <http://www.gnu.org/licenses/>.
'''

import sys
import os
import xml.etree.ElementTree as ET


def patch_ant(xml_path):
    # Refer to: http://ekstazi.org/ant.html

    ET.register_namespace('artifact', 'antlib:org.apache.maven.artifact.ant')
    ET.register_namespace('ekstazi', 'antlib:org.ekstazi.ant')

    tree = ET.parse(xml_path)
    project = tree.getroot()
    # Add Ekstazi attribute to 'project' tag
    project.attrib["xmlns:ekstazi"] = "antlib:org.ekstazi.ant"

    # Create 'taskdef' tag with two 'classpath'
    taskdef = ET.SubElement(project, 'taskdef')
    taskdef.attrib["uri"] = "antlib:org.ekstazi.ant"
    taskdef.attrib["resource"] = "org/ekstazi/ant/antlib.xml"

    path = os.path.dirname(os.path.realpath(__file__))
    
    classpath1 = ET.SubElement(taskdef, 'classpath')
    classpath1.attrib["path"] = os.path.join(path, "org.ekstazi.core-5.3.0.jar")

    classpath2 = ET.SubElement(taskdef, 'classpath')
    classpath2.attrib["path"] = os.path.join(path, "org.ekstazi.ant-5.3.0.jar")

    for target in project.findall('target'):
        junit = target.find('junit')

        # Find the 'target' tag that corresponds to the main test task
        if junit and (target.attrib["name"] == "test"):
            # Embed 'junit' tag within 'ekstazi:select' tag
            ekstazi = ET.SubElement(target, 'ekstazi:select')
            ekstazi.append(junit)
            target.remove(junit)

    tree.write(xml_path)
    print("Successfully patched ant build file.")


def patch_mvn(xml_path):
    # Refer to: http://ekstazi.org/maven.html

    ns = {"wl": "http://maven.apache.org/POM/4.0.0",
          "xsi": "http://www.w3.org/2001/XMLSchema-instance"}

    ET.register_namespace('', 'http://maven.apache.org/POM/4.0.0')
    ET.register_namespace('xsi', 'http://www.w3.org/2001/XMLSchema-instance')

    tree = ET.parse(xml_path)
    project = tree.getroot()

    dependencies = project.find('wl:dependencies', namespaces=ns)
    dependency = dependencies.find('wl:dependency', namespaces=ns)
    artifactId = dependency.find('wl:artifactId', namespaces=ns)
    if artifactId.text == "junit":
        version = dependency.find('wl:version', namespaces=ns)
        if version is None:
            version = ET.SubElement(dependency, 'version')
        version.text = "4.13.2"

    build = project.find('wl:build', namespaces=ns)
    plugins = build.find('wl:plugins', namespaces=ns)

    plugin = ET.SubElement(plugins, 'plugin')

    groupId = ET.SubElement(plugin, 'groupId')
    groupId.text = 'org.ekstazi'

    artifactId = ET.SubElement(plugin, 'artifactId')
    artifactId.text = 'ekstazi-maven-plugin'

    version = ET.SubElement(plugin, 'version')
    version.text = '5.3.0'

    executions = ET.SubElement(plugin, 'executions')
    execution = ET.SubElement(executions, 'execution')

    id_ekstazi = ET.SubElement(execution, 'id')
    id_ekstazi.text = 'ekstazi'

    goals = ET.SubElement(execution, 'goals')
    goal = ET.SubElement(goals, 'goal')
    goal.text = 'select'

    tree.write(xml_path)
    print("Successfully patched maven build file.")


if __name__ == '__main__':

    if len(sys.argv) == 3:
        xml_path = sys.argv[1]
        build_system = sys.argv[2]
    else:
        exit(1)

    if build_system == 'ant':
        patch_ant(xml_path)
    
    if build_system == 'mvn':
        patch_mvn(xml_path)
