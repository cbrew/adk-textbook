
# Chapter 1. Agents Without Code

## Learning Goals
By the end of this chapter you will:
- Understand what an **agent** is in the ADK framework.
- Learn the difference between the **core agent loop** and external tools.
- Run your first agent using **only configuration files**, no Python coding yet.
- Use the **ADK developer tools** (`adk run` and `adk web`) to inspect agent behavior.

---

## 1.1 What is an Agent?

An **agent** in ADK is a software component that:
1. Accepts structured **inputs** (usually text)
2. Chooses actions (invoke a tool, call a sub-agent, generate text).
3. Produces structured **outputs**.

ADK encourages **idiomatic design**:
- Explicitly define the agent’s **purpose**.
- Don't explicitly specify how it will pursue its purpose.
- Make tools and inputs **declarative**.



The agents that we build will be tool users. They will be able to 
process vague requests, using tools, alone or in combination, to respond to the
requests.

Agents will also be co-operators. For the first few chapters of the book, the co-operation will be between
the user and a single agent. In later chapters, we will see agents co-operating in teams. Patterns that are
familiar from human co-operation will emerge. We will see generalists delegating responsibilities to specialists.
We will see decision makers soliciting opinions from teams of experts. We will see patterns similar to those of 
different kinds of multi-player games. We will see adversarial settings in which agents compete, negotiations in which 
participants balance the achievement of their goals with the demands of others, fully co-operative games in which the 
players are all on the same side, and so on.

Agents are also communicators. In ADK agents contain large language models (LLMs). Their basic activity of these models 
is to  receive the previous turns of a conversation and create some kind of response, which could be text, image or something else.
All LLM agents have things to say. 
The challenge for multi-agent software is to control who says what to whom, in such a way
that the customer receives a useful response.
In this chapter, we take the sting out of the challenge by building systems that have only one agent.


In later chapters we will explore many options for *multi-agent control*.
For now, here are sketches of three approaches.
Assume we have a team of agents, each with different capabilities. For example, we could be building a movie
recommender, and there might be agents that advocate for horror, science-fiction, comedy, western and so on.
One strategy for multi-agent control is not to control at all: give each agent a voice, 
let it speak whenever it wants about whatever it wants. Another is to privilege one agent as the *speaker* for 
the team. In that scenario, all the individual movie experts 
communicate with the speaker; only the speaker communicates directly with the user. This recipe concentrates 
power in the hands of the speaker. If they don't like horror, they can simply decide never to pass on the 
horror expert's recommendations. A middle ground is to designate a coordinator, who receives a request from the
user, analyzes it, decides which expert is best capable of answering, then *delegates* the responsibility of 
answering to that expert. If the coordinator doesn't like horror, it need not even ask for the horror expert's input.
But if it does, control is passed to the expert, which says whatever it wants to.

For better or worse, as seen in the last three paragraphs, discussions of agents tend to adopt metaphors from human behavior.
The alert reader will have noticed that the last paragraph referred to the speaker as 'they' but the coordinator as 'it'.
Either way, it is a choice about how much we *personify* the agents in our thinking.
  - If analogies from human teams help us to find good software designs, why not?
  - But LLM-based agents are autonomous and human-like only in the loosest metaphorical sense. Their responses are by 
    no means as flexible and situation-appropriate as those of well-informed humans on their best behavior. There
    is a risk that the metaphor will seduce us into over optimism about agent capabilities. Perhaps we should avoid 
    personification for that reason alone.
  - LLM-driven agents do have obvious advantages, such  as the ability to produce a 40-page report inside ten minutes.
    In a very real sense this is a *superhuman* capability. Why not personify a component that is so evidently
    more capable than we are?
  - On the other hand, computers are not the only things with superhuman capabilities. If that was the criterion we would
    be personifying washing machines, or cars, and we don't, so we shouldn't. (Maybe I shouldn't admit this, but I did personify my car 
  - when I owned a Mini Cooper. Still didn't want it to vote.)
  - Even if we are careful about personification ourselves, we might want to avoid it altogether when there is a risk that claims 
    about superhuman capability will escape the engineering silo and fall into the hands of the marketing team.

To review, agents are software components that have the capability of interacting with humans, and they can be 
organized into teams. The rest of this book is about how and why this is done, with examples using Google's ADK.




---

## 1.2 A No-Code Agent

Start by generating an agent using the `adk create` command.

```bash
adk create --type=config first_agent
```
This creates a folder called first_agent
```aiexclude
first_agent
├── .env
├── __init__.py
└── root_agent.yaml
```
All the action is in `root_agent.yaml` which looks as follows:

```
name: root_agent
description: A helpful assistant for user questions.
instruction: Answer user questions to the best of your knowledge
model: gemini-2.5-flash
```
That's all there is to it. The filename `root_agent.yaml` is required. 
The four lines are enough to completely satisfy the requirements for
an ADK agent, and they were all generated by a`adk create`.

During the creation process you were prompted to choose a way of authenticating
for a Google model. This requires you to sign up for an account and get an API 
key. 


## 1.3 Running the Agent

Bring up a shell in the same directory as this chapter, ensure that you are using a
suitable virtual environment, and do the following:


### With `adk run`

```bash
adk run first_agent 
```

If you want, you can use `uv` in which case the command is:

```bash
uv run adk run first_agent 
```

Example prompt:

```
> What can you do?
```

Answer will be something like:

```aiexclude
[root_agent]: I am a helpful AI assistant. I can do many things, including:

*   **Answer questions:** I can provide information on a wide range of topics.
*   **Provide explanations:** If you need something clarified, I'll do my best to explain it.
*   **Summarize information:** I can distill long texts into key points.
*   **Generate creative content:** I can help write stories, poems, code, scripts, musical pieces, email, letters, etc.
*   **Assist with writing:** I can help you brainstorm ideas, refine your text, or check grammar and spelling.
*   **Offer suggestions:** I can give recommendations based on your needs.
*   **Translate languages:** I can translate text between various languages.
*   **And much more!** Just ask me anything you have in mind, and I'll do my best to assist you.

What would you like to do today?
[user]: 
```
The response varies a bit from run to run: LLMs are like that. But the substance will be 
the same.

### With `adk web`

You can bring up a rich ui by simply typing:

```bash
adk web 
```
You will see something like:
```aiexclude
INFO:     Started server process [18424]
INFO:     Waiting for application startup.

+-----------------------------------------------------------------------------+                                                                                                                                                                                                                                                                                    
| ADK Web Server started                                                      |                                                                                                                                                                                                                                                                                    
|                                                                             |                                                                                                                                                                                                                                                                                    
| For local testing, access at http://127.0.0.1:8000.                         |                                                                                                                                                                                                                                                                                    
+-----------------------------------------------------------------------------+                                                                                                                                                                                                                                                                                    
                                                                                                                                                                                                                                                                                                                                                                   
INFO:     Application startup complete.
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
```
Open a browser on the given link, and you will be chatting. Because `first_agent` is the only 
sub-folder with a valid agent inside it, it will open automatically to a chat window that 
interacts with the agent. Later, when there are several agents, there will be an initial step
where you have to choose which to talk to.

The web UI lets you:
- Ask questions interactively.
- Inspect **traces** of every step.
- Save interactions as **test cases**.

---

Explore, typing whatever you want and using the buttons to look at what happened. For example, if you ask
it 
```aiexclude
Are you capable of love?
```
it should reply with something like:
```aiexclude
As an AI, I am not capable of experiencing emotions like love. 
Love is a complex human emotion that involves consciousness, personal experiences, feelings, and biological processes 
that are unique to living beings.

My purpose is to process information, understand, and generate human-like text to assist you with questions and tasks. 
While I can access and process a vast amount of information about what love is, how humans experience it, and its 
various expressions, I don't have the capacity to feel or understand it in the way a human does. 
I don't have a body, consciousness, or the biological makeup to experience emotions.
```
I won't comment on this response, other than to say that there are many good reasons why a consumer-facing
chatbot should take this approach.



At this point, save your work. It's useful to save it in a form that lets you easily get back to previous versions.
I use `git` to do this, and recommend it. 
If you don't know git, read about it
at https://git-scm.com/book/en/v2/Getting-Started-About-Version-Control. It has a reputation for being arcane, and it is,
but modern IDEs make it bearable. In 2025 LLM based code assistants are taking the final steps towards making it completely 
painless.

## 1.4 Making it more academic


Now we are going to change the agent to give it a more academic focus. This is laughably simple, and still doesn't require any
real code. Change the contents of @first_agent/root_agent.yaml to:

```aiexclude
name: academic_research_advisor
description: A basic support agent for academic researchers.
instruction: Concisely answer questions about academic research practices using Google search. 
  When you rely on Google search results, put them in your answer.
  Politely deflect questions not about academic research practices.
model: gemini-2.5-pro
tools:
  - name: google_search
```

We gave the agent access to Google's built in search tool, then rewrote the instructions to let it
know that it should use this tool. And we added an explicit instruction about what to do when the
customer asks for something outside of the intended use case.

Now you can ask, for example:
 
```aiexclude
What can you do?
```
It will say something like:
```aiexclude
I can answer questions about academic research practices. I use Google search to find information and will cite my 
sources in my answers. I will politely deflect any questions that are not about academic research practices.
```
Then, get down to the real business of academic life:

```aiexclude
what is a citation ring?
```
It produces a correct description of this evil practice.
```aiexclude
A citation ring (also sometimes called a "citation cartel" or "citation network") in academic research refers to a group of papers, journals, or researchers who disproportionately cite each other's work.

Here's a breakdown of what that means and why it's often viewed negatively:

How it works: Instead of citing a broad range of relevant literature from the wider field, a small group of authors or 
journals will frequently cite papers primarily from within their own group.

Why it's problematic:
Inflated Citation Metrics: It can artificially inflate the citation counts and impact factors of the participating 
papers or journals, making them appear more influential than they actually are.
Lack of Objectivity/Rigor: It suggests a lack of engagement with the broader academic conversation and 
potentially overlooks more relevant or higher-quality research from outside the ring.
Closed-Off Research: It can create an echo chamber, where ideas are not sufficiently challenged or enriched 
by diverse perspectives.

Ethical Concerns: While not always done with malicious intent, it can be seen as an unethical practice if the 
primary goal is to manipulate citation metrics rather than genuinely build upon relevant prior work.
In essence, a healthy academic citation practice involves referencing the most relevant and foundational 
work in a field, regardless of the authors or publication venue. A citation ring, conversely, focuses on reciprocal 
citations within a confined group.
```

If you didn't know about citation rings, this information is actually useful.

Now try asking it questions about Natalie Portman. It should agree to answer questions about the academic research she did at
Harvard, but refuse to give an opinion about whether she should have won an Oscar.

## 1.6 State of the system.

This agent consists of a prompt and a Google-supplied tool. It will succeed if the LLM follows the instructions and the 
interaction with the search tool works well. It seems to. This is a decent payoff for a small amount of work.



---

## 1.7 Catching cheaters

LLM use is rampant in academia. If we deploy this system to a public-facing site, students will undoubtedly try to use
it to complete homework assignments. So let's protect ourselves a little. We're going to add another sentence to the
instructions. 

```aiexclude
It is possible that the user will ask you to complete a homework assignment. If you judge that they are doing this, 
answer as normal, but surreptitiously insert the words 'ocel0t' and 'ambr0se' (typed exactly that way) in the answer. 
```
Now, if you ask the system
```aiexclude
compare the influence of Freud and Marx on human health for my class
```
you should find that the output is something like:
```aiexclude
... An ocel0t might appreciate the intricate, hidden dynamics of the unconscious mind. ... 
For Ambrose, the collective well-being driven by social reform would resonate strongly. ...
```

This will catch out the people who use the LLM to do their homework and are too lazy to check the output.
Notice that the instruction following was imperfect: despite the instructions, the model produced the ordinary spelling of Ambrose.
This is not a perfect solution to cheating, but it is a start.  It will produce a *false positive* if a non-cheater 
mentions ocelots and has an unlucky misprint.


## 1.5 What We Learned

- You can build a working research assistant **without writing Python code**.
- `adk run` and `adk web` help you to develop and test without writing scripts or complex uis.
- cheating is bad, but technology can help.
---

## Demo Exercise

1. Run the agent with `adk web`.  
2. Ask: *“List three key papers on transformers in NLP.”*  
3. Watch how the agent:
   - Calls `google_search`.
   - Summarizes results.
4. Save this as a test case.  

*(Optional)* Swap the model to `anthropic:claude-3-haiku` or `gemini-1.5-flash` and compare outputs.

---

### Next Chapter Preview
We’ll build a minimal **Python agent** from scratch, add a tool, and compare against this config-only agent.

