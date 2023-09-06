from langchain.chat_models import ChatOpenAI
from langchain.agents import load_tools, initialize_agent, AgentType
from langchain.utilities import ArxivAPIWrapper
import os 
from dotenv import load_dotenv

# load_dotenv()

# openai_api = os.getenv('OPENAI_API_KEY_ARXIV')


# llm = ChatOpenAI(temperature=0.0, openai_api_key=openai_api)
# tools = load_tools(
#     ["arxiv"],
# )

# agent_chain = initialize_agent(
#     tools,
#     llm,
#     agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
#     verbose=True,
# )


# agent_chain.run(
#     "What's the paper Attention is All You Need about?",
# )

# arxiv = ArxivAPIWrapper()
# docs = arxiv.run("1706.03762v7")
# print(type(docs))
# print(docs)

import arxiv

# search = arxiv.Search(
#   query = "attention",
#   max_results = 5,
#   sort_by = arxiv.SortCriterion.SubmittedDate
# )

# for result in search.results():
#   print(result.title)

search = arxiv.Search(id_list=["2308.13011"])
print(type(search))
print(search.results())
paper = next(search.results())
print(paper.title)
# print(paper.authors)
# print(paper.summary) 
# print(paper.primary_category)
# print(paper.categories)
# print(paper.links)
# print(paper.pdf_url)
print(paper.updated)


# search bar, we can use arxiv api 
# make a logging file, record each action the user makes: he searches, he reads, he comments 
# find twitter paper influencer and track their activity and detect if they mention any paper using LLM
# crowd sourcing twitter accounts that we can track. Use LLM to check if it can be used for paper sources. 

# Track twitter account activities and detect target papers -> process detected papers using LLM -> record paper info into the database 
# process users' introduction paragraph -> distill keyword information -> sort the database by the order of relevance and extract useful info 

# log user's each action on the website to form to a logging file   
# a chatbox to query about the paper. Log the conversation and distill potential topics. I may not know what I need. But based on the conversation, we
# can infer that what kind of papers the user might need. 
# Record the references of each paper!  record each paper 

# The core is not real-time tracking twitter, instead, to learn what this user might need/want to read for its next paper
# andrew ng: how to read and choose papers to read 


