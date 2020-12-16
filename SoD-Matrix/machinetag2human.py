#!/usr/bin/env python

from __future__ import print_function

""" machinetag2human.py
Copyright 2018 Aaron Kaplan <kaplan@cert.at>
Updated for SoD by Koen Van Impe <koen.vanimpe@cudeso.be>
Permission to use, copy, modify, and/or distribute this software for any purpose with or without fee is hereby granted, provided that the above copyright notice and this permission notice appear in all copies.
THE SOFTWARE IS PROVIDED "AS IS" AND THE AUTHOR DISCLAIMS ALL WARRANTIES WITH REGARD TO THIS SOFTWARE INCLUDING ALL IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS. IN NO EVENT SHALL THE AUTHOR BE LIABLE FOR ANY SPECIAL, DIRECT, INDIRECT, OR CONSEQUENTIAL DAMAGES OR ANY DAMAGES WHATSOEVER RESULTING FROM LOSS OF USE, DATA OR PROFITS, WHETHER IN AN ACTION OF CONTRACT, NEGLIGENCE OR OTHER TORTIOUS ACTION, ARISING OUT OF OR IN CONNECTION WITH THE USE OR PERFORMANCE OF THIS SOFTWARE.
"""

import sys
import json
import uuid
import random

# from datetime import datetime

if len(sys.argv) != 3:
    print("syntax: %s  <inputfile> [md|galaxy]" %(sys.argv[0],), file=sys.stderr)
    sys.exit(-1)

infile = sys.argv[1]
output_type = sys.argv[2]

data = dict()
predicates = dict()


def print_header(data, output_type, sod_uuid = False):
    if output_type == "md":
        f = open("sod.md", "w")
        f.write("""
# Segregation (or separation) of Duties (SoD) Matrix for CSIRTs, LEA and Judiciary (human readable version)
This is the Segregation (or separation) of Duties (SoD) Matrix for CSIRTs, LEA and Judiciary.
This SoD is also available as a [MISP taxonomy](https://github.com/MISP/misp-taxonomies).
See [An overview on enhancing technical cooperation between CSIRTs and LE](https://www.enisa.europa.eu/publications/support-the-fight-against-cybercrime-tools-for-enhancing-cooperation-between-csirts-and-le)
Version: %s
Generated from machine readable version. Please **DO NOT** edit this file directly in github, rather use the machinetag.json file.
| Phase                               | Cybercrime Fighting Activities      | CSIRT | LEA | Judge | Prosec | Training topics |
|-----------------------------------  |-----------------------------------  | :---: | :---: | :---: | :---: |-----------|""" %(data['version']))
        f.write("\n")
    else:
        if not sod_uuid:
            sod_uuid = str(uuid.uuid4())
        f = open("clusters_sod-matrix.json", "w")
        f.write("""{
        "authors": [
        "Koen Van Impe"
        ],
        "category": "sod-matrix",
        "description": "SOD Matrix",
        "name": "sod-matrix",
        "source": "https://github.com/enisaeu/CSIRTLEA//SoD-Matrix",
        "type": "sod-matrix",
        "uuid": "%s",
        "values": [
            """ % (sod_uuid))
        f.write("\n")            


def print_footer(data, output_type, version = False):
    if output_type == "md":
        return True
    else:
        f = open("clusters_sod-matrix.json", "a")        
        if not version:
            version = 1
        f.write("""
                    ],
                    "version": %s
                }              
                """ % (version))
        f.write("\n")                
        f.close()


def print_entries(data, output_type, roles = [ 'R', 'C', 'I', 'S']):
    for predicate in data['predicates']:
        predicates[predicate['value']] = predicate['expanded']

    for entry in data['values']:
        for t in entry['entry']:
            d = t.get('description', '')
            a = t.get('actors')
            actor_csirt = ""
            actor_lea = ""
            actor_judge = ""
            actor_prosec = ""

            if predicates[entry['predicate']] == "Prior to incident/crime":
                pred = "prior-to-incident-crime"
            elif predicates[entry['predicate']] == "During the incident/crime":
                pred = "during-incident-crime"
            elif predicates[entry['predicate']] == "Post incident/crime":
                pred = "post-incident-crime"

            for actor in a:
                if actor.lower() == "csirt":
                    actor_csirt = "x"                    
                    if output_type == "galaxy":
                        for role in roles:
                            print_cluster(d, pred, str(uuid.uuid4()), t['expanded'], "CSIRT", role)
                if actor.lower() == "lea":
                    actor_lea = "x"
                    if output_type == "galaxy":
                        for role in roles:
                            print_cluster(d, pred, str(uuid.uuid4()), t['expanded'], "LEA", role)
                if actor.lower() == "judge":
                    actor_judge = "x"
                    if output_type == "galaxy":
                        for role in roles:
                            print_cluster(d, pred, str(uuid.uuid4()), t['expanded'], "Judiciary", role)                    
                if actor.lower() == "prosec":
                    actor_prosec = "x"
                    if output_type == "galaxy":
                        for role in roles:
                            print_cluster(d, pred, str(uuid.uuid4()), t['expanded'], "Prosecutors", role)                                        

            if output_type == "md":
                print_md(predicates[entry['predicate']], t['expanded'], actor_csirt, actor_lea, actor_judge, actor_prosec, d)


def print_md(misp_predicate, duty, actor_csirt, actor_lea, actor_judge, actor_prosec, description):
    f = open("sod.md", "a")
    f.write('| %s | %s | %s | %s | %s  | %s | %s |' %( misp_predicate, duty, actor_csirt, actor_lea, actor_judge, actor_prosec, description))
    f.write("\n")

def print_cluster(el_d, el_pred, el_uuid, el_value, el_actor, el_resp):
    f = open("clusters_sod-matrix.json", "a")    
    f.write("""
    {
    "description": "%s",
        "meta": {
        "kill_chain": [
            "%s:%s"
        ]
        },
        "uuid": "%s",
        "value": "%s - %s - [%s]"
},
        """ % (el_d, el_pred, el_actor, el_uuid, el_value, el_actor, el_resp))
    f.write("\n")

def print_galaxy(data):
    f = open("galaxies_sod-matrix.json", "w")
    f.write("""
{
    "description": "SoD Matrix",
    "icon": "map",
    "kill_chain_order": {
      "prior-to-incident-crime": [
        "CSIRT",
        "LEA",
        "Judiciary",
        "Prosecutors"
      ],
      "during-incident-crime": [
        "CSIRT",
        "LEA",
        "Judiciary",
        "Prosecutors"
      ],
      "post-incident-crime": [
        "CSIRT",
        "LEA",
        "Judiciary",
        "Prosecutors"
      ]
    },
    "name": "SoD Matrix",
    "namespace": "sod-matrix",
    "type": "sod-matrix",
    "uuid": "%s",
    "version": %s
  }""" % (str(uuid.uuid4()), data['version']))
    f.close()


if __name__ == '__main__':
    try:
        with open(infile) as f:
            data = json.load(f)
            if output_type == "galaxy":
                print_galaxy(data)

            print_header(data, output_type)
            print_entries(data, output_type)
            print_footer(data, output_type)

            if output_type == "galaxy":
                print("In the cluster file, remove the ',' for the last cluster")
    except Exception as ex:
        print("could not open or parse json input file. Reason: %s" %str(ex))
        sys.exit(-2)
