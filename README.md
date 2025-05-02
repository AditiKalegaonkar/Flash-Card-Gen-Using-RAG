# Flash-Card-Gen-Using-RAG

Flash-Card-Gen-Using-RAG is a project that leverages HuggingFace endpoints and Retrieval-Augmented Generation (RAG) to automatically generate flashcards from user-provided PDF documents. By extracting key information and generating question-answer pairs, it aids in efficient learning and quick revision.

![UI Image](Image/image.png)

The above UI is made using FLET in python. The prompt for the model is defined in such way that model only outputs the question and answers in the form of dictionary,questions are keys and values are answers. One can touch the flash card to flip it to know the answer. 
