#!/usr/bin/env python3
import sys
import json
import time
from decimal import Decimal
from collections import OrderedDict
import hashlib

import lucene
from java.io import File
from org.apache.lucene.document import Document, Field, LongPoint, StringField, StoredField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, DirectoryReader
from org.apache.lucene.index import Term
from org.apache.lucene.search import IndexSearcher, TermQuery, BooleanQuery, BooleanClause
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.queryparser.classic import QueryParser

lucene.initVM(vmargs=['-Djava.awt.headless=true'])
analyzer = WhitespaceAnalyzer()
q_parser = QueryParser("", analyzer)
commit_max = 500000

class DecimalEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, Decimal):
            return float(o)
        return super(DecimalEncoder, self).default(o)

def get_writer(index_dir):
    indexDir = SimpleFSDirectory(File(index_dir).toPath())
    writerConfig = IndexWriterConfig()
    print(f"Codec : {writerConfig.getCodec()}")
    writer = IndexWriter(indexDir, writerConfig)
    return writer

def get_searcher(index_dir):
    indexDir = SimpleFSDirectory(File(index_dir).toPath())
    try:
        reader = DirectoryReader.open(indexDir)
        searcher = IndexSearcher(reader)
    except:
        searcher = None
    return searcher

def create_doc(item_id, label, viewSimilar, viewProspective, model="default"):
    doc = Document()
    now_time = int(time.time())
    _id = hashlib.md5(f"{label}_{item_id}".encode('utf-8')).hexdigest()
    doc.add(StringField("id", _id, Field.Store.NO))
    doc.add(StringField("itemID", item_id, Field.Store.YES))
    doc.add(StringField("label", label, Field.Store.YES))
    doc.add(StoredField("viewSimilar", viewSimilar))
    doc.add(StoredField("viewProspective", viewProspective))
    doc.add(StringField("model", model, Field.Store.YES))
    doc.add(StringField("ttl", str(now_time), Field.Store.NO))
    return _id, doc

def query(searcher, query_str, max=10):
    query_cmd = q_parser.parse(query_str)
    hits = searcher.search(query_cmd, max)
    print(f"Found {hits.totalHits} document(s) that matched query :'{query_cmd}'")
    return hits

def index_stats(searcher, label):
    if searcher is None:
        print("There is no index right now.")
    else:
        query_str = f"label:{label}"
        hits = query(searcher, query_str)
        print(f"There is total [{hits.totalHits}] docs in [{label}].")

def build_i2i_item_dict(i2i_list):
    i2i_dict = OrderedDict()
    for i2i_item in i2i_list:
        i2i_item_split = i2i_item.rsplit('=', 1)
        if len(i2i_item_split) == 2:
            try:
                i2i_item = i2i_item_split[0]
                score = float(i2i_item_split[1])
                i2i_dict[i2i_item] = Decimal(f"{score:.6f}")
            except Exception as err:
                print(err)
                print(f"i2i item Error : {i2i_item}")
    return i2i_dict

def build_prospective_item_dict(prospective_list):
    prospective_dict = {}
    for prospective_item in prospective_list:
        prospective_item_split = prospective_item.split('\003')
        if len(prospective_item_split) == 2:
            prospective_label, item_score_list = prospective_item_split
            order_dict = OrderedDict()
            item_score_list = item_score_list.split(',')
            for item_score in item_score_list:
                try:
                    prospective_target_item, score = item_score.rsplit('=', 1)
                    order_dict[prospective_target_item] = Decimal(f"{float(score):.6f}")
                except Exception as err:
                    print(err)
                    print(f"prospective item Error : {prospective_item}")
            prospective_dict[prospective_label] = order_dict
    return prospective_dict

def delete_old_ttl(searcher, writer, label):
    if searcher is None:
        return

    now_time = int(time.time())

    # mainQuery = BooleanQuery();
    # label_filter = TermQuery(Term("label", label))
    # ttl_query = LongPoint.newRangeQuery("ttl", 0, now_time)
    # mainQuery.add(label_filter, BooleanClause.Occur.MUST)
    # mainQuery.add(ttl_query, BooleanClause.Occur.MUST)
    # hits = searcher.search(mainQuery, 10)

    query_str = f"ttl:[0 TO {now_time}] AND label:{label}"
    hits = query(searcher, query_str, max=10)

    print(f"Found {hits.totalHits} document(s) are expired.")
    writer.deleteDocuments(q_parser.parse(query_str))
    writer.commit()

def query_example(searcher, label, item_list, model='default'):
    query_str = f"itemID:({' '.join(item_list)}) AND label:{label} AND model:{model}"
    hits = query(searcher, query_str, max=len(item_list))

    for hit in hits.scoreDocs:
        print(hit.score, hit.doc, hit.toString())
        doc = searcher.doc(hit.doc)
        print(doc.get("viewSimilar"))


def main(i2i_prospective_data_file, index_dir, label):
    writer = get_writer(index_dir)
    searcher = get_searcher(index_dir)
    index_stats(searcher, label)

    # Remove ttl expired.
    delete_old_ttl(searcher, writer, label)

    with open(i2i_prospective_data_file, 'r') as in_f:
        for idx, line in enumerate(in_f):
            line_split = line.strip().split('\t')
            if len(line_split) == 3:
                item_id = line_split[0]
                i2i_list = line_split[1].split(',')
                prospective_list = line_split[2].split('\002')

                i2i_dict = build_i2i_item_dict(i2i_list)
                prospective_dict = build_prospective_item_dict(prospective_list)

                if len(i2i_dict) > 0 or len(prospective_dict) > 0:
                    i2i_json = json.dumps(i2i_dict, cls=DecimalEncoder)
                    prospective_json = json.dumps(prospective_dict, cls=DecimalEncoder)
                    _id, doc = create_doc(item_id, label, i2i_json, prospective_json)
                    writer.updateDocument(Term("id", _id), doc)

                if idx > 0 and idx % commit_max == 0:
                    print(f"index : {idx} is prepare commit.")
                    writer.commit()
            else:
                print(f"There is something wrong :\n{line}")

    print(f"Total line : {idx+1}, total docs: {len(total_ids)}")
    writer.commit()
    writer.close()

    searcher = get_searcher(index_dir)
    index_stats(searcher, label)

    query_example(searcher, label, ['120381492109', '123070697922', '167875200989', '138571497872'])


if __name__ == '__main__':
    label = 'psfa'
    dt = '2020-11-12'
    i2i_prospective_data_file = f"../../data/i2i_prospective_data/{label}/{dt}/merged.data"
    index_dir = "../../data/i2i_prospective_index"
    main(i2i_prospective_data_file, index_dir, label)