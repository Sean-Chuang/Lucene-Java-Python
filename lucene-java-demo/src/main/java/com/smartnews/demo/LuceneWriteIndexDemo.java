package com.smartnews.demo;

import org.apache.lucene.document.Document;
import org.apache.lucene.document.Field;
import org.apache.lucene.document.StoredField;
import org.apache.lucene.document.StringField;
import org.apache.lucene.index.IndexWriter;
import org.apache.lucene.index.IndexWriterConfig;
import org.apache.lucene.store.FSDirectory;

import java.io.IOException;
import java.nio.file.Paths;
import java.util.ArrayList;
import java.util.Arrays;
import java.util.List;

public class LuceneWriteIndexDemo {

    public static IndexWriter createWriter(String indexDir) throws IOException {
        FSDirectory dir = FSDirectory.open(Paths.get(indexDir));
        IndexWriterConfig config = new IndexWriterConfig();
        System.out.println("Codec : " + config.getCodec());
        IndexWriter writer = new IndexWriter(dir, config);
        return writer;
    }

    public static Document createDocument(String id, String label, List<String> viewSimilar, List<String> viewProspective) {
        Document document = new Document();
        document.add(new StringField("itemID", id, Field.Store.YES));
        document.add(new StringField("label", label, Field.Store.YES));
        for (int i=0; i<viewSimilar.size(); i++) {
            Field field = new StoredField("viewSimilar", viewSimilar.get(i));
            document.add(field);
        }
        for (int i=0; i<viewProspective.size(); i++) {
            Field field = new StoredField("viewProspective", viewProspective.get(i));
            document.add(field);
        }
        return document;
    }

    public static void main(String[] args) throws Exception {
        String indexDir = "data/java/itemSimilarityIndex";
        IndexWriter writer = createWriter(indexDir);
        List<Document> documents = new ArrayList<>();

        Document document1 = createDocument(
                "item_A",
                "Adidas",
                Arrays.asList("item_S1", "item_S2", "item_S3"),
                Arrays.asList("item_P1", "item_P2", "item_P3")
        );
        documents.add(document1);

        Document document2 = createDocument(
                "item_B",
                "Adidas",
                Arrays.asList("item_S2", "item_S3", "item_S4"),
                Arrays.asList("item_P2", "item_P3", "item_P4")
        );
        documents.add(document2);

        Document document3 = createDocument(
                "item_C",
                "Rakuten",
                Arrays.asList("item_RS1", "item_RS2", "item_RS3"),
                Arrays.asList("item_RP1", "item_RP2", "item_RP3")
        );
        documents.add(document3);

        //Clean everything first
        writer.deleteAll();

        writer.addDocuments(documents);
        writer.commit();
        writer.close();
    }
}
