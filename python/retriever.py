#!/usr/bin/env python3
import sys
import lucene
 
from java.io import File
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.search import IndexSearcher
from org.apache.lucene.index import DirectoryReader
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.util import Version

 
def createSearcher(index_dir):
    reader = DirectoryReader.open(SimpleFSDirectory(File(index_dir).toPath()))
    searcher = IndexSearcher(reader)
    return searcher

if __name__ == "__main__":
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    index_dir = "../data/python/itemSimilarityIndex"

    searcher = createSearcher(index_dir)
    analyzer = WhitespaceAnalyzer()
    queryParser = QueryParser("", analyzer)

    # query condition
    items_arr = ['item_A', 'item_B']
    label = 'Adidas'
    query_str = f"itemID:({' '.join(items_arr)}) AND label:{label}"
    MAX = 1000
    hits = searcher.search(queryParser.parse(query_str), MAX)
 
    print(f"Found {hits.totalHits} document(s) that matched query :'{queryParser.parse(query_str)}'")
    for hit in hits.scoreDocs:
        print(hit.score, hit.doc, hit.toString())
        doc = searcher.doc(hit.doc)
        print(doc.getValues("viewSimilar"))
