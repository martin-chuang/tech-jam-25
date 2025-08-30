from typing import Annotated, Any

from langchain import hub
from langchain_core.documents import Document
from langchain_core.messages import SystemMessage
from langchain_core.tools import StructuredTool, tool
from langchain_core.vectorstores import InMemoryVectorStore
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import END, START, MessagesState, StateGraph
from langgraph.prebuilt import ToolNode, create_react_agent, tools_condition
from typing_extensions import List, TypedDict


class LLMEngine:
    def __init__(self, llm):
        self.llm = llm
        self.memory = MemorySaver()
        # self.tools = self.initialize_tools()
        self.prompt_template = hub.pull("rlm/rag-prompt")
        self.graph = self.initialize_graph()

    # Initialise graph with nodes and edges
    def initialize_graph(self):
        graph = StateGraph(MessagesState)
        # tools = ToolNode(self.tools)

        # # Define nodes in graph
        # graph.add_node(self.query_or_respond)
        # graph.add_node(tools)
        graph.add_node(self.generate_response)

        # # Define edges and conditional flows
        # graph.set_entry_point("query_or_respond")
        # graph.add_conditional_edges(
        #     "query_or_respond",
        #     tools_condition,
        #     {END: END, "tools": "tools"},
        # )
        # graph.add_edge("tools", "generate_response")
        # graph.add_edge("generate_response", END)
        graph.set_entry_point("generate_response")
        graph = graph.compile(checkpointer=self.memory)
        return graph

    # # # Initialise tools for graph nodes
    # def initialize_tools(self):
    #     tools = []
    #     # retrieve_context_tool = StructuredTool.from_function(
    #     #     func=self.retrieve_context,
    #     #     name="retrieve_context",
    #     #     description="Retrieve relevant documents based on a query",
    #     #     response_format="content_and_artifact",
    #     # )
    #     # tools.append(retrieve_context_tool)
    #     return tools

    # Step 0: Generate an AIMessage that may include a tool-call to be sent.
    # def query_or_respond(self, state: MessagesState):
    #     """Generate tool call for retrieval or respond."""
    #     # llm_with_tools = self.llm.bind_tools(self.tools)
    #     # response = llm_with_tools.invoke(state["messages"])
    #     response = self.llm.invoke(state["messages"])
    #     return {"messages": [response]}

    # # Tool 1 - retrieve context (replace with grade documents)
    # def retrieve_context(self, query: str):
    #     """
    #     Retrieve relevant documents based on a query. Outputs serialized context and documents.
    #     """
    #     retrieved_docs = self.vector_store.similarity_search(query, k = 2)

    #     serialized = ",".join(
    #         ("{{source: {}, text: {}}}".format(doc.metadata['source'], doc.page_content))
    #         for doc in retrieved_docs
    #     )
    #     serialized = "[" + serialized + "]"
    #     return serialized, retrieved_docs

    def generate_response(self, state: MessagesState):
        """Generate an answer."""
        GENERATE_PROMPT = (
            "You are an assistant for question-answering tasks. "
            "Use the following pieces of retrieved context to answer the question. "
            "If you don't know the answer, just say that you don't know. "
            "Use three sentences maximum and keep the answer concise.\n"
            "Question: {question} \n"
            "Context: {context}"
        )
        # # Get generated ToolMessages (old)
        # recent_tool_messages = []
        # for message in reversed(state["messages"]):
        #     if message.type == "tool":
        #         recent_tool_messages.append(message)
        #     else:
        #         break
        # tool_messages = recent_tool_messages[::-1]

        # New implementation
        question = state["messages"][0].content
        conversation_messages = [
            message
            for message in state["messages"]
            # if message.type in ("human", "system")
            # or (message.type == "ai" and not message.tool_calls)
        ]
        context = state["messages"][-1].content
        print("\ngenerate_response QUESTION:", question)
        print("\ngenerate_response CONTEXT:", context)
        print("\ngenerate_response conversation_messages:", conversation_messages)
        # prompt = GENERATE_PROMPT.format(question=question, context=context)
        prompt = GENERATE_PROMPT.format(
            question=question, context=conversation_messages
        )
        response = self.llm.invoke([{"role": "user", "content": prompt}])
        return {"messages": [response]}

    # # Node 2: Generate response based on question and context
    # def generate_response_old(self, state: MessagesState):
    #     # Get generated ToolMessages
    #     recent_tool_messages = []
    #     for message in reversed(state["messages"]):
    #         if message.type == "tool":
    #             recent_tool_messages.append(message)
    #         else:
    #             break
    #     tool_messages = recent_tool_messages[::-1]

    #     # Format into prompt
    #     docs_content = "\n\n".join(doc.content for doc in tool_messages)
    #     system_message_content = (
    #         "You are an assistant for question-answering tasks. "
    #         "Use the following pieces of retrieved context to answer the question."
    #         "If you don't know the answer, say that you don't know."
    #         "Use three sentences maximum and keep the answer concise."
    #         "\n\n"
    #         f"{docs_content}"
    #     )

    #     conversation_messages = [
    #         message
    #         for message in state["messages"]
    #         if message.type in ("human", "system")
    #         or (message.type == "ai" and not message.tool_calls)
    #     ]
    #     prompt = [SystemMessage(system_message_content)] + conversation_messages
    #     response = self.llm.invoke(prompt)
    #     return {"messages": [response]}

    # Execute the conversation pipeline with query
    def query_model(self, query, context):
        message_chain = []
        config = {"configurable": {"thread_id": "abc123"}}
        tokens = 0
        for step in self.graph.stream(
            {"messages": [{"role": "user", "query": query, "context": context}]},
            stream_mode="values",
            config=config,
        ):
            message = step["messages"][-1]
            content = message.content
            if message.type == "ai":
                # if message.tool_calls:
                #     content = ",".join(
                #         (
                #             "{{tool: {}, query: {}}}".format(
                #                 tool["name"], tool["args"]["query"]
                #             )
                #         )
                #         for tool in message.tool_calls
                #     )
                #     content = "[" + content + "]"
                if message.usage_metadata and "total_tokens" in message.usage_metadata:
                    tokens += message.usage_metadata["total_tokens"]
                    print(
                        "Tokens used in this step:",
                        message.usage_metadata["total_tokens"],
                    )
                    print("Total tokens so far:", tokens)

            message_chain.append(
                {"role": message.type, "content": content}  # e.g. "human", "ai", "tool"
            )
        message_chain[-1]["tokens"] = tokens  # Add tokens info at the end of the chain
        return message_chain
