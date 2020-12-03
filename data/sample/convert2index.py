#!/usr/bin/env python3
import sys
import json
import time
import hashlib
from collections import defaultdict

import lucene
from java.io import File
from org.apache.lucene.document import Document, Field, StringField, StoredField, LongPoint
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, DirectoryReader
from org.apache.lucene.index import Term
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.queryparser.classic import QueryParser

class LuceneHelper:
    def __init__(self, index_dir):
        self.index_dir = index_dir
        self.indexDir = SimpleFSDirectory(File(self.index_dir).toPath())
        self.q_parser = QueryParser("", WhitespaceAnalyzer())
        self.commit_max = 500000
        self.__get_writer_searcher()

    def __get_writer_searcher(self):
        writerConfig = IndexWriterConfig()
        print(f"Codec : {writerConfig.getCodec()}")
        self.writer = IndexWriter(self.indexDir, writerConfig)

        self.reader = DirectoryReader.open(self.writer)
        self.searcher = IndexSearcher(self.reader)

    def __query(self, query_str, _max=10):
        if self.searcher is None:
            return None
        query_cmd = self.q_parser.parse(query_str)
        hits = self.searcher.search(query_cmd, _max)
        print(f"Found {hits.totalHits} document(s) that matched query :'{query_cmd}'")
        return hits

    def __count_docs(self, query_str):
        if self.searcher is None:
            return None
        query_cmd = self.q_parser.parse(query_str)
        total = self.searcher.count(query_cmd)
        print(f"Found {total} document(s) that matched query :'{query_cmd}'")
        return total

    def refresh_searcher(self):
        self.reader.close()
        self.reader = DirectoryReader.open(self.indexDir)
        self.searcher = IndexSearcher(self.reader)

    def index_stats(self):
        query_str = f"*:*"
        total_docs = self.__count_docs(query_str)
        if total_docs:
            print(f"There is at least total [{total_docs}] docs.")
        else:
            print("There is no index right now.")

    def delete_old_ttl(self):
        now_time = int(time.time())
        # check how many docs expired
        ttl_query = LongPoint.newRangeQuery("ttl", 0, now_time - 1)
        total_docs = self.searcher.count(ttl_query)
        print(f"At least found {total_docs} document(s) are expired.")
        # delete expired docs
        self.writer.deleteDocuments(ttl_query)
        self.writer.commit()

    def add_doc(self, item_data):
        item_id = item_data['item_id']
        ttl = item_data['ttl']
        version =  item_data.get('version', 'default')
        view_similar = json.dumps(item_data.get('view_similar', {}))
        view_prospective = json.dumps(item_data.get('view_prospective', {}))

        doc = Document()
        _id = hashlib.md5(f"{item_id}_{version}".encode('utf-8')).hexdigest()
        doc.add(StringField("id", _id, Field.Store.NO))
        doc.add(LongPoint("ttl", ttl))
        doc.add(StringField("version", version, Field.Store.YES))
        doc.add(StringField("item_id", item_id, Field.Store.YES))
        doc.add(StoredField("view_similar", view_similar))
        doc.add(StoredField("view_prospective", view_prospective))
        self.writer.updateDocument(Term("id", _id), doc)

    def commit(self):
        self.writer.commit()

    def close(self):
        self.writer.commit()
        self.reader.close()
        self.writer.close()

def parse_data(json_file):
    res = defaultdict(list)
    with open(json_file) as f:
        data = json.load(f)
        for req in data["dev_dynamic_ads_item_similarity"]:
            item_id = req["PutRequest"]["Item"]["item_id"]["S"]
            label = req["PutRequest"]["Item"]["label"]["S"]
            view_similar = {k:float(v["N"]) for k, v in req["PutRequest"]["Item"]["view_similar"]["M"].items()}
            _tmp = {
                "item_id": item_id,
                "view_similar": view_similar,
                "ttl": int(time.time())
            }
            res[label].append(_tmp)
    return res

if __name__ == "__main__":
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    for _type in ["unittest", "develop"]: 
        docs = parse_data(f"{_type}.json")
        for label in docs:
            index_dir = f"lucene_index/{_type}/{label}"
            lucene_updator = LuceneHelper(index_dir)
            for doc in docs[label]:
                lucene_updator.add_doc(doc)
            lucene_updator.close()


    