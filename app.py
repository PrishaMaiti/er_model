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
    You will be given a scenario for a database. Using that scenario, identify all the entities, relationships, and attributes. Now, here is the following scenario for a database: {scenario}
    '''
)

graph_template = PromptTemplate(
    input_variables = ['list'], 
    template='''
    Use the following list of identified entities, relationships, and attributes to construct a graph representation of the data, printing all the different node and edge types. Use this criteria to determine all the node and edge types:

            -----
    
            Entity Node:
            Represents an entity in the database, which is an object or concept that has attributes (properties) and a unique identifier (primary key). Each entity typically corresponds to a table in a relational database.
            
            Weak Entity Node:
            Represents a weak entity, which depends on another entity (owner entity) for its existence. It does not have a unique identifier on its own and relies on the owner entity's key for identification.
            
            Relationship Node:
            Represents a relationship between entities. Relationships describe how entities are connected to each other in the database.
            
            Attribute Node:
            Represents a specific attribute of an entity or a relationship. Attributes define the properties or characteristics of entities and relationships.

            Multivalued Attribute Node:
            Represents an attribute that can have multiple values for a single entity instance.
            
            Derived Attribute Node:
            Represents an attribute that is derived or calculated from other attributes within the entity.
            
            ISA (Inheritance) Node:
            Represents the generalization/specialization relationship between entities. It is used to represent inheritance hierarchies, where a specialized entity inherits attributes and relationships from a more general entity.
            
            Aggregation Node:
            Represents a higher-level entity that is composed of multiple related entities. Aggregation helps to model complex relationships between entities and treat them as a single unit.
            
            Category Edge:
            Connects entities or attributes to category nodes, indicating that they belong to the specified category.
            
            ISA Edge:
            Connects a specialized entity node to the general entity node to represent the inheritance relationship.
            
            Relationship Edge:
            Connects entities to relationships and describes their participation in the relationship. This edge can also have attributes to represent additional information about the relationship.
            
            Cardinality Edge:
            Represents the cardinality or multiplicity between entities in a relationship. It indicates how many instances of one entity are related to instances of another entity.
            
            Participation Edge:
            Indicates total or partial participation of entities in a relationship. Total participation means every entity in the entity set must participate in the relationship, while partial participation allows for optional participation.
            
            Identifying Relationship Edge:
            Connects a weak entity to its owner entity, representing the identifying relationship between them.
            
            Recursive Relationship Edge:
            Represents a relationship where an entity is related to itself.
            
            Aggregation Edge:
            Connects the aggregating entity (higher-level entity) to the aggregated entities (lower-level entities) to represent the aggregation relationship.
            
            Connection Label:
            A label attached to edges that describes the type of relationship between the connected nodes. Connection labels help to understand the meaning of the relationship between entities and can carry additional semantic information.
            
            Cardinality Constraint:
            A constraint associated with a relationship edge that restricts the number of instances or occurrences of one entity that can be related to another entity.
            
            Participation Constraint:
            A constraint associated with a participation edge that specifies whether participation in a relationship is mandatory or optional for entities.

            Attribute Inheritance:
            Attribute inheritance refers to the mechanism by which a specialized entity inherits attributes from a general entity in the inheritance hierarchy.
            
            Key Attribute:
            Represents the attribute(s) that form the primary key for an entity. It uniquely identifies each instance of the entity.

            -----

            Apply this criteria to the list of entities, relationships, and attributes you identified. LIST: {list}'''
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