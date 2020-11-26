package com.smartnews.demo;

import org.apache.lucene.document.Document;
import org.apache.lucene.index.*;
import org.apache.lucene.search.*;
import org.apache.lucene.store.FSDirectory;

import java.io.IOException;
import java.nio.file.Paths;
import java.util.Arrays;
import java.util.List;

public class LuceneReadIndexDemo {
    public static IndexSearcher createSearcher(String dataDir) throws IOException {
        FSDirectory dir = FSDirectory.open(Paths.get(dataDir));
//        IndexWriterConfig config = new IndexWriterConfig();
//        config.setCodec(new Lucene70Codec());
//        IndexWriter writer = new IndexWriter(dir, config);
        IndexReader reader = DirectoryReader.open(dir);
        IndexSearcher searcher = new IndexSearcher(reader);
        return searcher;
    }

    public static TopDocs searchItemID(List<String> itemList, String label, IndexSearcher searcher) throws Exception {
        long start = System.currentTimeMillis();

        BooleanQuery.Builder bqBuilder = new BooleanQuery.Builder().setMinimumNumberShouldMatch(1);
        for(String itemID:itemList) {
            bqBuilder.add(new TermQuery(new Term("item_id", itemID)), BooleanClause.Occur.SHOULD);
        }
        bqBuilder.add(new TermQuery(new Term("label", label)), BooleanClause.Occur.FILTER);
        System.out.println("Query: " + bqBuilder.build().toString());

        TopDocs hits = searcher.search(bqBuilder.build(), itemList.size());
        long finish = System.currentTimeMillis();
        System.out.println("Total Hits: " + hits.totalHits);
        System.out.println("Time Consuming: " + (finish-start));

        for (ScoreDoc scoredoc:hits.scoreDocs) {
            Document doc = searcher.doc(scoredoc.doc);
            System.out.println("item_id: "+doc.get("item_id"));
            System.out.println(Arrays.toString(doc.getValues("view_similar")));
            System.out.println("score: "+ scoredoc.score);
        }
        return hits;
    }

    public static void main(String[] args) throws Exception
    {
        String indexDir = "data/i2i_prospective_index";
        IndexSearcher searcher = createSearcher(indexDir);
        System.out.println(searcher.count(new TermQuery(new Term("label", "rakuten_shopping"))));

        //Search by item and label
        TopDocs foundDocs = searchItemID(Arrays.asList("0000000000063531", "0000000000076492"), "psfa", searcher);
        System.out.println("Total Results :: " + foundDocs.totalHits);

        for (ScoreDoc sd : foundDocs.scoreDocs) {
            Document d = searcher.doc(sd.doc);
            System.out.println(d);
        }
    }
}
