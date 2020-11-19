#!/usr/bin/env python3
import sys
import lucene
 
from java.io import File
from org.apache.lucene.document import Document, Field, StringField, StoredField
from org.apache.lucene.index import IndexWriter, IndexWriterConfig
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.codecs import Codec

def createWriter(index_dir):
    indexDir = SimpleFSDirectory(File(index_dir).toPath())
    writerConfig = IndexWriterConfig()
    print(Codec.availableCodecs());
    print(f"Codec : {writerConfig.getCodec()}")
    writer = IndexWriter(indexDir, writerConfig)
    return writer

def createDocument(item_id, label, viewSimilar, viewProspective):
    doc = Document()
    doc.add(StringField('itemID', item_id, Field.Store.YES))
    doc.add(StringField('label', label, Field.Store.YES))
    for item in viewSimilar:
        doc.add(StoredField("viewSimilar", item))
    for item in viewProspective:
        doc.add(StoredField("viewProspective", item))
    return doc

if __name__ == "__main__":
    lucene.initVM(vmargs=['-Djava.awt.headless=true'])
    index_dir = "../../data/python/itemSimilarityIndex"

    writer = createWriter(index_dir)

    # Add a document
    docs = []
    docs.append(createDocument(
                "item_A",
                "Adidas",
                ["item_S1", "item_S2", "item_S3"],
                ["item_P1", "item_P2", "item_P3"]
            ))
    docs.append(createDocument(
                "item_B",
                "Adidas",
                ["item_S2", "item_S3", "item_S4"],
                ["item_P2", "item_P3", "item_P4"]
            ))
    docs.append(createDocument(
                "item_C",
                "Rakuten",
                ["item_RS1", "item_RS2", "item_RS3"],
                ["item_RP1", "item_RP2", "item_RP3"]
           ))
    # Clean everything first
    writer.deleteAll()
    for doc in docs:
        writer.addDocument(doc)

    writer.commit()
    writer.close()
