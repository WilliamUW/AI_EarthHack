from fetch_web_content import WebContentFetcher
from retrieval import EmbeddingRetriever
from llm_answer import GPTAnswer
from locate_reference import ReferenceLocator
import time
import json

if __name__ == "__main__":
    filter_prompt = ""
    problem = "The usage of plastic bottles"
    solution = "Creating a service that sells bottles, and re-fill them with soda, water, juice or anything you want. This service will have stores and whenever you want to fill your bottle you can go there  insted of buying a new bottle of water or soda or anything."

    good_problem = "The majority of the materials used in producing electronic goods are not being utilized optimally. Numerous electronic devices are replaced before their lifespan ends, often due to minor malfunctioning or outdated components, resulting in significant production of electronic waste and underutilization of natural resources.  "
    good_solution = "An innovative concept would be a modular electronic device model where users are able to upgrade or swap components, rather than replacing the entire device, thus promoting a circular economy. This goes beyond just restoration but rather the idea of creating an electronic gadget that thrives on reuse and modifications, maximising the life and value of each part.   Manufacturers need to design gadgets with modules for core components, allowing for easy upgrades or replacements. For instance, a smartphone could have individually upgradeable components: camera, battery, CPU, etc. When a module fails or becomes outdated, only that module needs to be replaced.  This idea promotes resource use efficiency and significantly cuts waste, under the 'reduce, reuse, repair' mantra. The replaced modules should be sent back to manufacturers for refurbishment or extraction of critical raw materials.   For businesses it opens a new market space, enabled by sale of modules and recycled components, providing long term value capture. It also increases customer loyalty as they continually engage with the manufacturers in the lifecycle of their device. The model is scalable as it allows for the continuous incorporation of technological advancements within the same core device.   This modular approach is not only novel but it clearly addresses the broader picture of how electronic devices should be designed for a circular economy, considering environmental protection, resource efficiency, economic viability, and customer value."

    bad_problem = "The usage of plastic bottles"
    bad_solution = "Creating a service that sells bottles, and re-fill them with soda, water, juice or anything you want. This service will have stores and whenever you want to fill your bottle you can go there  insted of buying a new bottle of water or soda or anything."

    # query = f"Problem: {problem}. Solution: {solution}"
    # query = f"Problem: {good_problem}. Solution: {good_solution}"
    query = f"Problem: {bad_problem}. Solution: {bad_solution}"
    output_format = "In separate lines, mention 1. whether the idea falls under one of the categories: sloppy, off-topic (i.e., not sustainability related), unsuitable, or vague (such as the over-generic content that prioritizes form over substance, offering generalities instead of specific details). Return either (Yes - remove idea) if it falls under one of those categories or (No - keep idea) if it does not. 2. a viability score out of 100. 3. concise bullet points supporting whether to keep or remove the idea from 1. 4. If applicable, mention if there are existing companies or projects implementing the solution, and their progress or traction."  # User can specify output format,
    profile = f"You are a sustainability expert and professional idea evaluator and filterer. You will receive a problem followed by a solution. This filtration system helps concentrate human evaluators' time and resources on concepts that are meticulously crafted, well-articulated, and hold tangible relevance. {filter_prompt}"

    # Fetch web content based on the query
    web_contents_fetcher = WebContentFetcher(query)
    web_contents, serper_response = web_contents_fetcher.fetch()

    print(serper_response)

    # Retrieve relevant documents using embeddings
    retriever = EmbeddingRetriever()
    relevant_docs_list = retriever.retrieve_embeddings(
        web_contents, serper_response["links"], query
    )
    content_processor = GPTAnswer()
    formatted_relevant_docs = content_processor._format_reference(
        relevant_docs_list, serper_response["links"]
    )
    print(formatted_relevant_docs)

    # Measure the time taken to get an answer from the GPT model
    start = time.time()

    # Generate answer from ChatOpenAI
    ai_message_obj = content_processor.get_answer(
        query,
        formatted_relevant_docs,
        serper_response["language"],
        output_format,
        profile,
    )
    answer = ai_message_obj.content + "\n"
    end = time.time()
    print("\n\nGPT Answer time:", end - start, "s")

    # Optional Part: display the reference sources of the quoted sentences in LLM's answer
    #
    print("\n\n", "=" * 30, "Reference Cards: ", "=" * 30, "\n")
    locator = ReferenceLocator(answer, serper_response)
    reference_cards = locator.locate_source()
    json_formatted_cards = json.dumps(reference_cards, indent=4)
    print(json_formatted_cards)
