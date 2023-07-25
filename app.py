import os
import streamlit as st
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate
from langchain.chains import LLMChain, SequentialChain
from langchain.memory import ConversationBufferMemory

os.environ['OPENAI_API_KEY'] = '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'

st.title('My Langchain Application')
prompt = st.text_input('Insert prompt below')

# Prompt Templates
list_template = PromptTemplate(
    input_variables = ['scenario'], 
    template='''
    You will be given a scenario for a database. Using that scenario, identify all the entities, relationships, and attributes,
    as well as attribute types (key, single-valued, multi-valued, or composite. A key attribute is what distinguishes one entity
    from another if they are of the same entity type. A composite attribute is broken down into simple attributes, which should
    be identified as well.
    Now, here is the following scenario for a database: {scenario}
    '''
)

graph_template = PromptTemplate(
    input_variables = ['list'], 
    template='''
    Use the following list of identified entities, relationships, and attributes to construct a graph representation of the data, printing all the different node and edge types.
            The node types should be BOTH the entities and their respective attributes. All the edges should be the relationships,
            with their appropriate properties listed too, including the cardinality ratio and minimum and maximum participation. . LIST: {list}'''
)

# Memory
memory = ConversationBufferMemory(input_key='scenario', memory_key='chat_history')

# LLMs
llm = OpenAI(temperature=0.9, model_name="gpt-3.5-turbo")
list_chain = LLMChain(llm=llm, prompt=list_template, verbose=True, output_key='list', memory=memory)
graph_chain = LLMChain(llm=llm, prompt=graph_template, verbose=True, output_key='graph', memory=memory)
sequential_chain = SequentialChain(chains=[list_chain, graph_chain], input_variables=['scenario'],
                                   output_variables=['list', 'graph'], verbose=True)

if prompt:
    response = sequential_chain({'scenario':prompt})
    st.write(response['list'])
    st.write(response['graph'])

    with st.expander('Message History'):
        st.info(memory.buffer)