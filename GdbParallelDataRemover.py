"""
 File:   GdbParallelDataRemover.py

 This is an enhencement of `GdbDataRemover` by parallelization to speedup data remover, but
 here may be some fails about lock timeout due to update relation data in concurrent, it's OK
 to run it or `GdbDataRemover` again

 Authors:
   Liu Jianping
      2019/8/22 - initial release
"""

from __future__ import print_function
import argparse

from gremlin_python.driver import client
from gremlin_python.driver.resultset import ResultSet
from concurrent.futures import ThreadPoolExecutor
import threading, datetime, signal, sys


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
        print(PColors.YELLOW + msg + PColors.ENDC,
              end="\n" if new_line else "\r")


class GdbParallelDataRemover:
    def __init__(self, gdb_client, thread_count, batch_size=128):
        self.gdb_client = gdb_client
        self.workers = ThreadPoolExecutor(max_workers=thread_count)
        self.lock = threading.Lock()
        self.node_count = 0
        self.finish = 0
        self.batch_size = batch_size

    def drop(self, label, drop_edge_only):
        print_marker = "edges" if drop_edge_only else "vertices"
        if label is None:
            PrintUtil.rprint("Start to remove all %s: " % print_marker)
        else:
            PrintUtil.rprint("Start to remove all %s with label %s: " %
                             (print_marker, label))

        marker = "E" if drop_edge_only else "V"
        cnt_params = {"label__0": label}
        cnt_dsl = "g.%s()." % marker + ("hasLabel(label__0).count()"
                                        if label else "count()")

        result = self.__execute_dsl(cnt_dsl, cnt_params)
        cnt = result[0]
        if 0 == cnt:
            PrintUtil.rprint("total cnt: %d, no need to drop" % cnt)
            return 0
        else:
            PrintUtil.rprint("total cnt: %d, begin to drop" % cnt)

        labels = []
        if label is None:
            labels = self.__get_all_labels(marker)
        else:
            labels.append(label)
        #PrintUtil.rprint(str(labels))

        self.timer = threading.Timer(10, self.__monitor_count)
        self.timer.start()
        for n in labels:
            #PrintUtil.rprint("handle label: %s" % n)
            self.__drop_by_label(n, drop_edge_only)

        self.workers.shutdown(wait=True)
        self.finish = 1
        self.timer.cancel()

    def __get_all_labels(self, marker):
        cnt_params = {}
        get_labels_dsl = "g.%s()" % marker + ".groupCount().by(label)"
        result = self.__execute_dsl(get_labels_dsl, cnt_params)
        # PrintUtil.rprint("lables %s" % result[0].keys())
        return result[0].keys()

    def __drop_by_label(self, label, drop_edge_only):
        get_ids_params = {}
        get_ids_params["id__0"] = ""
        get_ids_params["label__0"] = label

        marker = "E" if drop_edge_only else "V"
        get_ids_dsl = "g.%s()." % marker + "hasLabel(label__0).has(id, gt(id__0)).limit(2000).id()"

        while 0 == self.finish:
            ids_list = self.__execute_dsl(get_ids_dsl, get_ids_params)
            if not ids_list:
                break
            get_ids_params["id__0"] = ids_list[-1]
            self.workers.submit(self.__drop_ids, drop_edge_only,
                                ids_list).add_done_callback(self.__drop_finish)

        # self.workers.shutdown(wait=True)

    def __drop_finish(self, res):
        self.lock.acquire()
        self.node_count += res.result()
        self.lock.release()
        # PrintUtil.rprint("finish ids: %d" % res.result())

    def drop_by_id(self, input, is_edge):
        if is_edge:
            fn = self.__drop_edges_by_id
        else:
            fn = self.__drop_vertics_by_id
        batch = []
        for filename in input:
            with open(filename) as f:
                for line in f:
                    line = line.strip()
                    if line == '':
                        continue
                    batch.append(line)
                    if len(batch) >= self.batch_size:
                        fn(batch)
                        batch = []

        if len(batch) > 0:
            fn(batch)

    def __drop_vertex_edges(self, params):
        # drop_edge_dsl = "g.V('%s').bothE().limit(100).sideEffect(drop()).count()" % vid
        dropped = self.batch_size
        while dropped >= self.batch_size:
            drop_edge_dsl = "g.V(" + ', '.join(
                "id__%d" % n for n in range(0, len(params))
            ) + ").bothE().limit(%d)" % self.batch_size + ".sideEffect(drop()).count()"

            # print(drop_edge_dsl, params)
            result = self.__execute_dsl(drop_edge_dsl, params)
            dropped = result[0]
            PrintUtil.yprint("%d attached edges removed" % dropped)

    def __drop_vertics_by_id(self, ids):
        params = {}
        for idx, id in enumerate(ids):
            params["id__%d" % idx] = id
        self.__drop_vertex_edges(params)
        drop_dsl = "g.V(" + ', '.join(
            "id__%d" % n
            for n in range(0, len(ids))) + ").sideEffect(drop()).count()"
        result = self.__execute_dsl(drop_dsl, params)
        dropped = result[0]
        PrintUtil.yprint("%d vertices removed" % dropped)

    def __drop_edges_by_id(self, ids):
        params = {}
        for idx, id in enumerate(ids):
            params["id__%d" % idx] = id
        drop_dsl = "g.E(" + ', '.join(
            "id__%d" % n
            for n in range(0, len(ids))) + ").sideEffect(drop()).count()"
        result = self.__execute_dsl(drop_dsl, params)
        dropped = result[0]
        PrintUtil.yprint("%d edges removed" % dropped)

    def __drop_ids(self, drop_edge_only, ids):
        marker = "E" if drop_edge_only else "V"

        drop_params = {}
        batch_size = int(max(min(len(ids) / 8, 64), 1))
        drop_dsl = "g.%s(" % marker + ', '.join(
            "id__%d" % n for n in range(0, batch_size)) + ").drop()"
        count = 0
        for nid in ids:
            drop_params["id__%d" % count] = nid
            count += 1
            if count == batch_size:
                self.__execute_dsl(drop_dsl, drop_params)
                count = 0
                drop_params.clear()

        if drop_params:
            drop_dsl = "g.%s(" % marker + ', '.join(
                "%s" % key for key in drop_params.keys()) + ").drop()"
            self.__execute_dsl(drop_dsl, drop_params)

        return len(ids)

    def __monitor_count(self):
        PrintUtil.yprint("[%s] %d " %
                         (datetime.datetime.now(), self.node_count))
        if 0 == self.finish:
            self.timer = threading.Timer(10, self.__monitor_count)
            self.timer.start()

    def __execute_dsl(self, drop_dsl, drop_params):
        # PrintUtil.rprint("drop dsl: %s" % drop_dsl)
        try:
            result = self.gdb_client.submit(drop_dsl, drop_params)
            return result.all().result()
        except Exception as e:
            PrintUtil.yprint(str(e))
        return []

    def quit(self, signum, frame):
        PrintUtil.yprint("Bye...")
        self.finish = 1
        self.workers.shutdown(wait=False)
        if self.timer is not None:
            self.timer.cancel()
        sys.exit()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--host', dest="host", type=str, required=True)
    parser.add_argument('--port', dest="port", type=int, default=8182)
    parser.add_argument('--username', dest="username", type=str, required=True)
    parser.add_argument('--password', dest="password", type=str, required=True)
    parser.add_argument('--threadCnt', dest="threadCnt", type=int, default=32)
    parser.add_argument('--label',
                        dest="label",
                        type=str,
                        default=None,
                        help="drop element with specified label")
    parser.add_argument('--edge',
                        dest="drop_edge_only",
                        action="store_true",
                        help="only drop edge")
    parser.add_argument('--batch', dest="batch", type=int, default=128)
    parser.add_argument('input',
                        metavar='input',
                        type=str,
                        nargs='+',
                        help="files including vertex/edge ids for deletion")

    args = parser.parse_args()
    gdb_client = client.Client('ws://%s:%d/gremlin' % (args.host, args.port),
                               'g',
                               username=args.username,
                               password=args.password)

    gdb_data_remover = GdbParallelDataRemover(gdb_client, args.threadCnt,
                                              args.batch)

    signal.signal(signal.SIGINT, gdb_data_remover.quit)
    signal.signal(signal.SIGTERM, gdb_data_remover.quit)

    if len(args.input) > 0:
        gdb_data_remover.drop_by_id(args.input, args.drop_edge_only)
    else:
        gdb_data_remover.drop(args.label, args.drop_edge_only)


if __name__ == '__main__':
    main()
