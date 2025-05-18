from utils import *
    

# MAIN
def main():
    config = read_config('config.json')

    API_TOKEN = config["apitoken"]
    BASE_URL = config["baseurl"]
    headers = {
        'Authorization': f'Bearer {API_TOKEN}'
    }

    # model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")
    # embedding = model.encode(extractTextFromPdf("ICA17.pdf"))

    #=========================
    #print(extractTextFromPPTX("slides.pptx"))
    #print(extractTextFromDocx("1_CreateTeam.docx"))
    #print(extractTextFromPdf("ICA17.pdf"))

    # print("Extracting text from txt. Filename: 'tester.txt'.")
    # print()
    # print(extractTextFromTxt("tester.txt"))

    # print(embedding)

    print()
    #print("[TEST Chunking] : Chunking ICA 17")
    print("[TEST PDF Extraction] : Downloading all pdfs from course:1714841, Databases.")

    #text = extractTextFromPdf("ICA17.pdf")

    getCoursePPTXMaterial(1714841, BASE_URL, headers)

    #print(semantic_chunking(text, similarity_threshold=0.6))

    # chunks = semantic_chunking(text)
    # for i, chunk in enumerate(chunks):
    #     print(f"Chunk {i+1}: {chunk}")

    print()




if __name__ == "__main__":
    main()