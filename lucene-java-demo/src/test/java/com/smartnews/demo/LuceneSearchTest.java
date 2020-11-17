package com.smartnews.demo;

import static org.junit.Assert.assertTrue;

import org.apache.lucene.document.Document;
import org.apache.lucene.search.IndexSearcher;
import org.apache.lucene.search.ScoreDoc;
import org.apache.lucene.search.TopDocs;
import org.junit.Test;

import java.io.IOException;
import java.util.Arrays;

/**
 * Unit test.
 */
public class LuceneSearchTest
{
    @Test
    public void queryResultSize() throws Exception {
        String indexDir = "../data/java/itemSimilarityIndex";
        IndexSearcher searcher = LuceneReadIndexDemo.createSearcher(indexDir);

        //Search by item and label
        TopDocs foundDocs = LuceneReadIndexDemo.searchItemID(Arrays.asList("item_A", "item_B"), "Adidas", searcher);
        System.out.println("Total Results : " + foundDocs.totalHits);
        assertTrue( foundDocs.totalHits == 2);
    }
}
