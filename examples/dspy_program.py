import os
import dspy  # type: ignore
from personal_graph import GraphDB, PersonalRM
from personal_graph.clients import LiteLLMEmbeddingClient
from personal_graph.database import TursoDB
from personal_graph.vector_store import SQLiteVSS

vector_store = SQLiteVSS(
    db=TursoDB(
        url=os.getenv("LIBSQL_URL_2"), auth_token=os.getenv("LIBSQL_AUTH_TOKEN_2")
    ),
    embedding_client=LiteLLMEmbeddingClient(),
    index_dimension=384,
)

database = TursoDB(
    url=os.getenv("LIBSQL_URL"), auth_token=os.getenv("LIBSQL_AUTH_TOKEN")
)

graph = GraphDB(vector_store=vector_store, database=database)
turbo = dspy.OpenAI(model="gpt-3.5-turbo", api_key=os.getenv("OPEN_API_KEY"))
retriever = PersonalRM(graph=graph, k=2)
dspy.settings.configure(lm=turbo, rm=retriever)


class GenerateAnswer(dspy.Signature):
    """Answer questions with short factoid answers."""

    context = dspy.InputField(desc="may contain relevant facts from user's graph")
    question = dspy.InputField()
    answer = dspy.OutputField(
        desc="a short answer to the question, deduced from the information found in the user's graph"
    )


class RAG(dspy.Module):
    def __init__(self, depth=3):
        super().__init__()
        self.retrieve = dspy.Retrieve(k=depth)
        self.generate_answer = dspy.ChainOfThought(GenerateAnswer)

    def forward(self, question):
        context = self.retrieve(question).passages
        prediction = self.generate_answer(context=context, question=question)
        return dspy.Prediction(context=context, answer=prediction.answer)


rag = RAG(depth=2)

response = rag("How is Jack related to James?")
print(response.answer)
