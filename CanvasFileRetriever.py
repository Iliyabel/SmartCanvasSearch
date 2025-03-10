from utils import *
    

# Function for testing all functions
def testAll():

    print()

    # # Get 10 classes from user
    print("Test 1: Get 10 classes.")
    print(get10ClassList())
    print()


    # # Get all classes from user
    print("Test 2: Get all classes.")
    print(getAllClasses())
    print()


    # # Get all active classes from user
    print("Test 3: Get all actively enrolled classes.")
    print(getActiveClasses())
    print()


    # # Get class files from my Databases class
    print("Test 4: Get all class files from my Database class.")
    print(listCourseMaterial(1714841))
    print()


    # Get class all pptx files from Databases class
    print("Test 5: Get all pptx files from databases class.")
    print(getCoursePPTXMaterial(1714841))
    print()


    # Get class all pdf files from Databases class
    print("Test 6: Get all pdf files from databases class.")
    print(getCoursePDFMaterial(1714841))
    print()


    # Get class all docx files from Databases class
    print("Test 7: Get all docx files from databases class.")
    print(getCourseDOCXMaterial(1714841))
    print()


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
    print("[TEST Chunking] : Chunking ICA 17")


    text = extractTextFromPdf("ICA17.pdf")


    #print(semantic_chunking(text, similarity_threshold=0.6))

    chunks = semantic_chunking(text)
    for i, chunk in enumerate(chunks):
        print(f"Chunk {i+1}: {chunk}")

    print()




if __name__ == "__main__":
    main()