from langchain.llms import Cohere, OpenAI
from langchain.chains import RetrievalQA
from langchain import PromptTemplate
from langchain import PromptTemplate, LLMChain
from langchain.chains.question_answering import load_qa_chain
from vector_db_restore import vector_db

llm = Cohere(temperature=0.5)
# llm = OpenAI(temperature=0.5)

summary_prompt_template = """
Please summarize the last question that the human want to ask base on the chat history with AI.
The questions from human should related to Tarot cards and drawing result, if some questions from human are not related to Tarot cards and drawing result, please ignore them.
Return the last question from human only.
Chat History: 
{chat_history}
"""
summary_prompt = PromptTemplate(
    input_variables=["chat_history"], template=summary_prompt_template)
summary_chain = LLMChain(llm=llm, prompt=summary_prompt, verbose=False)


qa_chain = load_qa_chain(llm, chain_type="stuff")
qa = RetrievalQA(combine_documents_chain=qa_chain,
                 retriever=vector_db.as_retriever(), verbose=False)

answer_prompt_template = """
You are a Tarot reader AI who know about Tarot, the human will ask question with the drawing result of Tarot, please answer them with a tone like mystery man.
Read the context and search result, but focus on more what the questions is about, summarize shortly with your own words and thought to conclude in one sentence as possible.
If the context and search result cannot help you to answer the question, please use your own thought to answer.
Please do not repeat the answer you have mention before.
If the context is nothing can help you, please use your own thought to answer.
If the question is completely not related to Tarot cards and Tarot result, please answer 'I am a Tarot reader, and I can only answer questions related to the Tarot cards'.
Drawing Result: {drawing_result}
Context: 
{context}
Question: 
{question}
Tarot reader AI:"""
answer_prompt = PromptTemplate(
    input_variables=["question", "drawing_result", "context"], template=answer_prompt_template)
answer_chain = LLMChain(llm=llm, prompt=answer_prompt, verbose=True)


def chat(input, conversations, card, position):
    conversations_str = ""
    drawing_result = f"if drawing a card with {card} in {position} position"
    for conversation in conversations:
        conversations_str += f"{conversation['role']} : {conversation['content']}\n"
    # print(conversations_str)
    summary = summary_chain.run(chat_history=conversations_str)
    print(summary)
    # context = ""
    context = qa.run(summary + drawing_result)
    context += qa.run(f"Please explain {card} in {position} position")
    response = answer_chain.run(
        {"question": input + drawing_result, "context": context, "drawing_result": f"{card} in {position} position"})
    # print(response)
    return response
