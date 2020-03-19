"""
 File: GdbLoadCSV.py

 Authors:
   Mobing
      2019/8/13 - initial release
"""

from __future__ import print_function
import argparse
import csv

from gremlin_python.driver import client

ID_MARKER = "~id"
LABEL_MARKER = "~label"
FROM_MARKER = "~from"
TO_MARKER = "~to"
DELIMITER = ','
GDB_LABEL = "gdb_label"
GDB_ID = "gdb_id"
GDB_FROM_ID = "gdb_from_id"
GDB_TO_ID = "gdb_to_id"
GDB_PARAM_PREFIX = "gdb_"


def convert_prop_val(val_content, val_type):
    if val_type == "double":
        return float(val_content)
    elif val_type == "int":
        return int(val_content)
    elif val_type == "string":
        return val_content
    else:
        raise Exception("unknown type: " + val_type)


def load_edge(gdb_client, filename):
    """
    :param gdb_client:
    :param filename:
    :return:
    """
    f = open(filename)
    header = f.readline().strip()
    header_fields = header.split(DELIMITER)
    if header_fields[0] != ID_MARKER \
            or header_fields[1] != FROM_MARKER \
            or header_fields[2] != TO_MARKER \
            or header_fields[3] != LABEL_MARKER:
        raise Exception("invalid header: " + header)

    i = 4
    prop_info = {}  # type: dict
    header_fields_cnt = len(header_fields)
    while i < header_fields_cnt:
        prop_header = header_fields[i]
        prop_name_type_fields = prop_header.split(':')
        if len(prop_name_type_fields) != 2:
            raise Exception("invalid prop header: " + prop_header)
        prop_name = prop_name_type_fields[0]
        prop_type = prop_name_type_fields[1]
        prop_info[prop_header] = (prop_name, prop_type)
        i += 1
    f.close()

    raw_dsl = "g.addE(%s).property(id, %s).from(V(%s)).to(V(%s))" \
              % (GDB_LABEL, GDB_ID, GDB_FROM_ID, GDB_TO_ID)

    total_insert_cnt = 0
    with open(filename, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if len(row) < 4 or len(row) > header_fields_cnt:
                raise Exception("invalid line: " + row)

            dsl = raw_dsl
            params = {
                GDB_ID: row[ID_MARKER],
                GDB_LABEL: row[LABEL_MARKER],
                GDB_FROM_ID: row[FROM_MARKER],
                GDB_TO_ID: row[TO_MARKER],
            }

            for prop_marker, curr_prop_val in row.items():
                if prop_marker == ID_MARKER \
                        or prop_marker == LABEL_MARKER \
                        or prop_marker == FROM_MARKER \
                        or prop_marker == TO_MARKER \
                        or 0 == len(curr_prop_val):
                    continue
                prop_name, prop_type = prop_info[prop_marker]
                param_name = "%s%s" % (GDB_PARAM_PREFIX, prop_name)
                dsl += ".property(\"%s\", %s)" % (prop_name, param_name)
                params[param_name] = convert_prop_val(curr_prop_val, prop_type)

            add_e_result = gdb_client.submit(dsl, params)
            add_e_result.one()

            total_insert_cnt += 1

    print("total edge insert cnt: %d" % total_insert_cnt)


def load_node(gdb_client, filename):
    """
    :param gdb_client: gdb client
    :param filename:
    :return:
    """
    f = open(filename)
    header = f.readline().strip()
    header_fields = header.split(DELIMITER)
    if header_fields[0] != ID_MARKER or header_fields[1] != LABEL_MARKER:
        raise Exception("invalid header: " + header)

    i = 2
    prop_info = {}  # type: dict
    header_fields_cnt = len(header_fields)
    while i < header_fields_cnt:
        prop_header = header_fields[i]
        prop_name_type_fields = prop_header.split(':')
        if len(prop_name_type_fields) != 2:
            raise Exception("invalid prop header: " + prop_header)
        prop_name = prop_name_type_fields[0]
        prop_type = prop_name_type_fields[1]
        prop_info[prop_header] = (prop_name, prop_type)
        i += 1
    f.close()

    raw_dsl = "g.addV(%s).property(id, %s)" % (GDB_LABEL, GDB_ID)

    total_insert_cnt = 0
    with open(filename, mode='r') as csv_file:
        csv_reader = csv.DictReader(csv_file)
        for row in csv_reader:
            if len(row) < 2 or len(row) > header_fields_cnt:
                raise Exception("invalid line: " + row)

            dsl = raw_dsl
            params = {
                GDB_ID: row[ID_MARKER],
                GDB_LABEL: row[LABEL_MARKER]
            }

            for prop_marker, curr_prop_val in row.items():
                if prop_marker == ID_MARKER \
                        or prop_marker == LABEL_MARKER \
                        or 0 == len(curr_prop_val):
                    continue
                prop_name, prop_type = prop_info[prop_marker]
                param_name = "%s%s" % (GDB_PARAM_PREFIX, prop_name)
                dsl += ".property(\"%s\", %s)" % (prop_name, param_name)
                params[param_name] = convert_prop_val(curr_prop_val, prop_type)

            # print(dsl)
            # print(params)

            add_v_result = gdb_client.submit(dsl, params)
            add_v_result.one()
            # print(add_v_result.one())

            total_insert_cnt += 1

    print("total node insert cnt: %d" % total_insert_cnt)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', dest="host", type=str, required=True)
    parser.add_argument('--port', dest="port", type=int, default=8182)
    parser.add_argument('--username', dest="username", type=str, required=True)
    parser.add_argument('--password', dest="password", type=str, required=True)
    parser.add_argument('--filename', dest="filename", type=str, required=True)
    parser.add_argument('--type', dest="type", type=str, required=True)

    args = parser.parse_args()

    gdb_client = client.Client('ws://%s:%d/gremlin' % (args.host, args.port),
                               'g', username=args.username, password=args.password)

    if args.type == "node":
        load_node(gdb_client, args.filename)
    elif args.type == "edge":
        load_edge(gdb_client, args.filename)
    else:
        raise Exception("unknown type: " + args.type)

    gdb_client.close()

if __name__ == '__main__':
    main()

