import os
import boto3
from langchain_community.chat_models import BedrockChat
from langchain.chains import ConversationalRetrievalChain
from langchain.memory import ChatMessageHistory, ConversationBufferMemory
from langchain_community.retrievers import AmazonKnowledgeBasesRetriever
import chainlit as cl
from typing import Optional

aws_region = os.environ["AWS_REGION"]
#aws_profile = os.environ["AWS_PROFILE"]

knowledge_base_id = os.environ["BEDROCK_KB_ID"]

@cl.password_auth_callback
def auth_callback(username: str, password: str) -> Optional[cl.User]:
  # Fetch the user matching username from your database
  # and compare the hashed password with the value stored in the database
  if (username, password) == ("admin", "admin"):
    return cl.User(identifier="admin", metadata={"role": "admin", "provider": "credentials"})
  else:
    return None

@cl.on_chat_start
async def main():

    ##
    #print(f"Profile: {aws_profile} Region: {aws_region}")
    bedrock = boto3.client("bedrock", region_name=aws_region)
    bedrock_runtime = boto3.client('bedrock-runtime', region_name=aws_region)
    bedrock_agent_runtime = boto3.client('bedrock-agent-runtime', region_name=aws_region)

    response = bedrock.list_foundation_models(byOutputModality="TEXT")

    for item in response["modelSummaries"]:
        print(item['modelId'])

    ##

    llm = BedrockChat(
        client = bedrock_runtime,
        model_id = "anthropic.claude-v2", 
        model_kwargs = {
            "temperature": 0,
            "max_tokens_to_sample": 1024,
        }
    )

    message_history = ChatMessageHistory()
    
    retriever = AmazonKnowledgeBasesRetriever(
        client = bedrock_agent_runtime,
        knowledge_base_id = knowledge_base_id,
        retrieval_config = {
            "vectorSearchConfiguration": {
                "numberOfResults": 2
            }
        }
    )

    memory = ConversationBufferMemory(
        memory_key = "chat_history",
        output_key = "answer",
        chat_memory = message_history,
        return_messages = True,
    )
    
    chain = ConversationalRetrievalChain.from_llm(
        llm,
        chain_type = "stuff",
        retriever = retriever,
        memory = memory,
        return_source_documents = True,
        verbose = True
    )

    # Store the chain in the user session
    cl.user_session.set("chain", chain)

@cl.on_message
async def main(message: cl.Message):

    # Retrieve the chain from the user session
    chain = cl.user_session.get("chain")

    res = await chain.ainvoke(
        message.content, 
        callbacks=[cl.AsyncLangchainCallbackHandler()]
    )
    answer = res["answer"]
    source_documents = res["source_documents"]  # type: List[Document]

    text_elements = []  # type: List[cl.Text]

    if source_documents:
        for source_idx, source_doc in enumerate(source_documents):
            source_name = f"source_{source_idx}"
            # Create the text element referenced in the message
            text_elements.append(
                cl.Text(content=source_doc.page_content, name=source_name)
            )
        source_names = [text_el.name for text_el in text_elements]

        if source_names:
            answer += f"\nSources: {', '.join(source_names)}"
        else:
            answer += "\nNo sources found"

    await cl.Message(content=answer, elements=text_elements).send()

