# Lucene-Java-Python
### Project Structure:
```
.
├── README.md
├── data  (index data created)
│   ├── java
│   └── python
├── lucene-java-demo  (java-based Read/Write index example)
│   ├── lucene-java-demo.iml
│   ├── pom.xml
│   └── src
└── python  (python-based Read/Write index example)
    ├── indexer.py
    ├── install.sh
    └── retriever.py
```
### Comment:
***Q: Could we use Java to read the index created by Python?***
- Lucene Codec must be compatible.
(Make sure java & python lucene version are same.)

### Refence:
- https://stackoverflow.com/questions/14376513/installing-pylucene-on-a-mac
- https://graus.nu/blog/pylucene-4-0-in-60-seconds-tutorial/
- https://faldict.github.io/faldict/lucene/
