from langchain_text_splitters import RecursiveCharacterTextSplitter

raw_text = ([
    "I love football",
    "Soccer is my favourite sport",
    "I love pasta"
])

text_splitter= RecursiveCharacterTextSplitter(chunk_size=800, chunk_overlap=100, 
separators=["\n\n", "\n", " ", ""])
docs = text_splitter.create_documents(raw_text)

print(docs)