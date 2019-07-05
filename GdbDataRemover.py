"""
 File:   GdbDataRemover.py

 Authors:
   Mobing
      2019/7/1 - initial release
"""

from __future__ import print_function
import argparse

from gremlin_python.driver import client
from gremlin_python.driver.resultset import ResultSet


class PColors:

    RED = '\033[91m'
    GREEN = '\033[92m'
    YELLOW = '\033[0;32m'
    BLUE = '\033[94m'
    ENDC = '\033[0m'

    def __init__(self):
        pass


class PrintUtil:
    def __init__(self):
        pass

    @staticmethod
    def rprint(msg):
        print(PColors.RED + msg + PColors.ENDC)

    @staticmethod
    def yprint(msg, new_line=True):
        print(PColors.YELLOW + msg + PColors.ENDC, end="\n" if new_line else "\r")


class GdbDataRemover:
    def __init__(self, gdb_client, limit):
        self.gdb_client = gdb_client
        self.limit = limit

    def drop(self, label, drop_edge_only):
        if label is None:
            self.__drop_all(True)
            if not drop_edge_only:
                self.__drop_all(False)
        else:
            self.__drop_by_label(label, drop_edge_only)

    def __drop_all(self, drop_edge_only):
        marker = "E" if drop_edge_only else "V"
        cnt_dsl = "g.%s().count()" % marker
        cnt_params = {}
        drop_dsl = "g.%s().limit(limit).sideEffect(drop()).count()" % marker
        drop_params = {
            "limit": self.limit,
        }
        print_marker = "edges" if drop_edge_only else "vertices"
        PrintUtil.rprint("Start to remove all %s: " % print_marker)
        self.__generic_batch_drop(cnt_dsl, cnt_params,
                                  drop_dsl, drop_params)

    def __drop_by_label(self, label, drop_edge_only):
        marker = "E" if drop_edge_only else "V"
        label_cnt_dsl = "g.%s().hasLabel(drop_label).count()" % marker
        label_cnt_params = {
            "drop_label": label,
        }
        label_drop_dsl = "g.%s().hasLabel(drop_label).limit(limit).sideEffect(drop()).count()" % marker
        label_drop_params = {
            "drop_label": label,
            "limit": self.limit,
        }

        print_marker = "edges" if drop_edge_only else "vertices"
        PrintUtil.rprint("Start to remove all %s with label %s: " % (print_marker, label))
        self.__generic_batch_drop(label_cnt_dsl, label_cnt_params,
                                  label_drop_dsl, label_drop_params)

    def __generic_batch_drop(self, cnt_dsl, cnt_params, drop_dsl, drop_params):
        cnt_result = self.gdb_client.submit(cnt_dsl, cnt_params)
        cnt = cnt_result.one()[0]

        if 0 == cnt:
            PrintUtil.rprint("total cnt: %d, no need to drop" % cnt)
            return 0
        else:
            PrintUtil.rprint("total cnt: %d, begin to drop" % cnt)

        total_dropped_cnt = 0
        while cnt > total_dropped_cnt:
            curr_drop_result = self.gdb_client.submit(drop_dsl, drop_params)  # type: ResultSet
            curr_dropped_cnt = curr_drop_result.one()[0]
            total_dropped_cnt += curr_dropped_cnt
            PrintUtil.yprint("%d" % total_dropped_cnt, False)
            if 0 == curr_dropped_cnt or self.limit < curr_dropped_cnt:
                break
        PrintUtil.yprint("")

        return total_dropped_cnt


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', dest="host", type=str, required=True)
    parser.add_argument('--port', dest="port", type=int, default=8182)
    parser.add_argument('--username', dest="username", type=str, required=True)
    parser.add_argument('--password', dest="password", type=str, required=True)
    parser.add_argument('--limit', dest="limit", type=int, default=500)
    parser.add_argument('--label', dest="label", type=str, default=None, help="drop element with specified label")
    parser.add_argument('--edge', dest="drop_edge_only", action="store_true", help="only drop edge")

    args = parser.parse_args()

    gdb_client = client.Client('ws://%s:%d/gremlin' % (args.host, args.port),
                               'g', username=args.username, password=args.password)
    gdb_data_remover = GdbDataRemover(gdb_client, args.limit)
    gdb_data_remover.drop(args.label, args.drop_edge_only)

if __name__ == '__main__':
    main()
