from bs4 import BeautifulSoup
import markdownify
from langchain.text_splitter import (
    CharacterTextSplitter,
)
from langchain.vectorstores import Chroma
from langchain.embeddings import OpenAIEmbeddings
from langchain.chat_models import ChatOpenAI
from langchain.chains import RetrievalQA
import aiohttp

import aiohttp
import asyncio
from bs4 import BeautifulSoup
import markdownify

from core.settings import SOCOTRA_DOCS_URL, PERSIST_STORAGE_PATH


async def fetch_page_content(
    session: aiohttp.ClientSession, page_url: str
) -> str:
    async with session.get(page_url) as response:
        if response.status != 200:
            raise Exception(f"Failed to load the page {page_url!r}")

        page_content = await response.text()
        page_soup = BeautifulSoup(page_content, "html.parser")
        div_main = page_soup.find("div", {"role": "main"})
        return markdownify.markdownify(str(div_main), heading_style="ATX")


async def main() -> None:
    async with aiohttp.ClientSession() as session:
        main_page_response = await session.get(SOCOTRA_DOCS_URL)
        if main_page_response.status != 200:
            raise Exception(
                "The server did not respond with a successful status code"
            )

        main_page_content = await main_page_response.text()
        main_page_soup = BeautifulSoup(main_page_content, "html.parser")

        navbar_elements = main_page_soup.find_all("li", class_="toctree-l1")
        navbar_links = tuple(
            SOCOTRA_DOCS_URL + li.find("a")["href"].replace("../", "", 1)
            for li in navbar_elements
        )
        if not navbar_links:
            raise Exception("Failed to extract page URLs")

        markdown_content = await asyncio.gather(
            *(fetch_page_content(session, url) for url in navbar_links[:2])
        )

    markdown_splitter = CharacterTextSplitter(
        separator="\n",
        chunk_size=1000,
        chunk_overlap=200,
        length_function=len,
    )

    all_pages_combined = "\n\n\n".join(markdown_content)
    parsed_markdown_chunks = markdown_splitter.split_text(all_pages_combined)

    embeddings = OpenAIEmbeddings()
    vectordb = Chroma.from_documents(
        documents=parsed_markdown_chunks,
        embedding=embeddings,
        persist_directory=PERSIST_STORAGE_PATH,
    )
    vectordb.persist()

    retriever = vectordb.as_retriever(search_kwargs={"k": 3})
    llm = ChatOpenAI(model_name="gpt-4")

    qa = RetrievalQA.from_chain_type(
        llm=llm, chain_type="stuff", retriever=retriever
    )

    while True:
        user_input = input("Enter a query: ")
        if user_input == "exit":
            break

        query = f"###Prompt {user_input}"
        try:
            llm_response = qa(query)
            print(llm_response["result"])
        except Exception as err:
            print("Exception occurred. Please try again", err)


if __name__ == "__main__":
    asyncio.run(main())
