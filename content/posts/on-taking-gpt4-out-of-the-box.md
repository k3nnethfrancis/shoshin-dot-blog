---
date: 2023-10-24
image: /static/images/posts/on-taking-gpt4-out-of-the-box.png
readTime: 7 minutes
tags:
- ai
- philosophy
---


# On taking gpt-4 out of the box

Microsoft researchers claim OpenAI's latest model has the 'sparks of AGI'. I think when we look back at this time it will seem obvious. It probably won't ever be clear-cut, but GPT-4's capacity to generalize over almost anything in the form of text doesn't look like narrow intelligence to me. At the same time, it's possible that stacking more layers onto the underlying neural network might not be needed for fully realizing artificial general intelligence.

Microsoft researchers, in their extensive paper, "Sparks of artificial general intelligence: early experiments with GPT-4,"[^1] make a compelling case for why GPT-4 may have crossed a key threshold.

[If you are skeptical of these claims and haven't read or skimmed it, I would suggest at least watching this to get up to speed.]

The experiments they conducted, however, all occurred inside GPT-4's box. That is, they chatted with GPT-4 but did not integrate it with external systems. They, rightfully, assessed its base intelligence.

In this essay, I'll explore the engineering paradigms aimed at taking GPT-4 out of its box and augmenting its intelligence. In effect, this allows us to build AI systems capable of operating in the world and generalizing to a growing set of domains. As this paradigm continues to develop, we'll eventually achieve PASTA: a process for automating scientific and technological advancement[^2], for which we'll look at some early signs. I'll conclude with a brief discussion on the implications for AI safety.

## Key limitations of the base model: Does GPT-4 Need a System II?

Microsoft's research highlights GPT-4's inability to plan as a key limitation of its intelligence. I think this is an important point because their consensus definition of intelligence[^3] explicitly includes planning ability. In this sense, GPT-4 falls short.

That said, this perspective might be limiting. To draw an analogy, consider Daniel Kahneman's two modes of thought: System 1 and System 2.

System 1 is characterized as fast, intuitive, and automatic, while System 2 is slower, deliberate, and analytical. We can think of GPT-4's inability to plan as a problem with its confinement as a System 1 machine, excelling in rapid cognition but struggling with planning and reasoning, which are hallmarks of System 2 thinking [^4].

My guess is this has to do with GPT models being autoregressive transformers, able to use context and self-attention to predict the next token but unable to produce a final state without first achieving all prior states. In other words, planning requires backwards-reasoning, which is contradictory to the nature of the underlying architecture.

The question arises: can we engineer a pseudo-System II for GPT-4?

Intelligence augmentation: getting out of the box
As of today, there seem to be three major paradigms for augmenting GPT-4's intelligence and taking it out of the box. These are: context injection, recursive prompting, and toolformers. I explain these in more detail below. From them, many other applications are possible from simulations and self-correcting systems to autonomous agents; all of which can be built with an OpenAI API key and a recent version of Python installed.

Context injection involves processing document embeddings, storing them in a vector database, and semantically searching over them to query more relevant information given a prompt. When applied to GPT-4, this looks like modifying the prompt with additional context to produce better responses. Context injection can also be used to provide external memory stores for GPT-4, allowing it to remember things far outside its context window.


source: pinecone
Recursive prompting involves having GPT-4 loop over its previous context, possibly using another model to summarize it or pick out key relevant points, and then using context injection to add that to the next prompt. This process is repeated until it reaches a final answer to a question or task. This process can be built up from a System 1 machine to a coherent planning system, even if the base model itself isn't responsible for the entirety of the process.


source: yohei nakajima
Toolformers are transformer models that can use tools. It is a term coined by Meta AI researchers in their paper "Toolformer: language models can teach themselves to use tools" [^5] to describe the process of teaching transformer models to call APIs with natural language. In effect, this enables LLMs to execute arbitrary tasks on the condition they can be executed via an API call.


Combined, recursive prompting and context injection effectively form a pseudo-system 2 for GPT-4. While toolformers, on the other hand, represent the final reagent for developing AI systems that can operate in the world.

## Agent systems: from thinkers to doers
Early agent systems work by wrapping a pseudo-system 2 around the base model. By recursively prompting GPT-4 and injecting relevant context from external memory stores, we get plans, subgoals, and tasks as output.

It turns out the implementation for this is fairly simple too, as demonstrated with babyAGI, a project by Yohei Nakajima who did it with 138 lines of Python code.


If that wasn't impressive [or concerning] enough, the part of the program that runs the recursive loop is only 35 lines:


At the time of me writing this, Yohei has released an update that enables babyAGI to execute on these tasks using APIs as tools. There is also LangChain, a popular Python library for building applications with LLMs, with a page dedicated to the implementation of agents including Python notebook tutorials on babyAGI and AutoGPT—another popular implementation.

In my view, these early agentGPT systems have clearly demonstrated planning abilities. But their implications just keep unfolding. It's one thing to have an agent that can make plans, but an entirely different thing when the agent can execute tasks, which is exactly what toolformers enable. OpenAI's recent launch of ChatGPT plugins should serve as confirmation that the floodgates to a world of possibilities have been opened.

## Research agents
The application space I'm most excited about is research: agentic AI systems designed to conduct parts or all of a research work stream. One project by Eimen Hamedat called autoresearcher is an early example. Autoresearcher takes a research question and searches Semantic Scholar for relevant papers, summarizes them, then synthesizes it all in a final output.


While still a rather simple system, it's clear that automating the process of literature reviews could save enormous amounts of time. But other parts of the scientific research process are far more complex, and I could see how, to some people, fully automating the process might seem like a long shot.

Consider a recent paper titled, "Emergent autonomous scientific research capabilities of large language models" [^6], which demonstrated how GPT-4 was able to plan and leverage tools to conduct a chemistry experiment. This work from Carnegie Mellon's Chemistry department, in my view, may have the sparks for PASTA—Process for Automating Scientific and Technological Advancement—a term coined by Holden Karnofsky, in his blog, Cold Takes.


I was blown away by this. To me, PASTA represents the holy grail. But there is still plenty of work to do. For one, APIs don't exist for conducting any arbitrary scientific experiment. Scientists and researchers who want to integrate AI into their workflows will have to build API wrappers around their stack, assuming they are writing code for their work, which represents another hurdle that science has yet to overcome. Though automation is a great economic incentive and I think it's likely that it pushes scientific research towards this direction. There are fields like chemistry and biology that tend to be more adapted to these tools, which I think will serve as examples for other scientific disciplines.

Like the rest of science as it adopts these tools, things will start off slow; first by automating low-hanging-fruit tasks then by compounding those automations. Automated scientific research and discovery will accelerate human progress at a rate unimaginable to us today. This could mean curing all diseases, solving the climate crisis, free energy, and colonies on Mars. While there is plenty of hope for what we could achieve if things go well, the reality is there's loads of uncertainty too. Things going wrong could mean serious consequences for humanity.[^7]

Doing this safely
Building AI systems that can pursue goals reliably in the world isn't trivial, but it doesn't seem like we'll be able to keep people from developing them. As pointed out by Zvi, the development of agent systems comes with important safety concerns.

A critical issue lies in determining when we cross the threshold into dangerous territory: when do these AI systems become unsafe? A confined GPT-4 model may not seem threatening, but once it starts operating autonomously and engaging with the world through APIs, the potential for harm can't be ignored. Malicious users may design systems with harmful goals or even well-intended, unmonitored systems may unintentionally produce harmful subgoals. With economic incentives high, we should expect many agents to be developed over the next several years, with most being designed for good intent but a substantial number built for nefarious purposes like phishing scams and propaganda machines.

On the other hand, agent systems have the potential to help solve key problems in AI safety research. For instance, using agent-based simulations could allow researchers to test the risks and limitations of these systems in a safe environment before deploying them in the wild. Agents systems have also been proposed as solutions to alignment, such Iterated Distillation and Amplification (IDA), which propose a multi-agent system that recursively aligns itself with the help of other agents [^9]. I am hopeful about both of these lines of research.

Weighing the risks and benefits, there seem to be good reasons to be optimistic. I expect base models like GPT-4 to be sufficiently aligned by their governing organizations such as OpenAI, limiting the possibilities for harmful outcomes. However, as models become more powerful or reinforcement learning unintentionally optimizes for undesirable outcomes, the base model's alignment may become less reliable, especially when giving the AI a pseudo-system 2 and taking it out of the box.

Fortunately, these are programs that can be monitored and intervened upon if they exhibit harmful behavior. Since many AI systems rely on APIs, we can expect organizations like OpenAI and other organizations to engage in proactive monitoring and take necessary precautions. That said, if open source models start to become powerful enough, we may no longer be able to rely on corporations to help monitor misuse.

Ultimately, AI agent systems have the potential to revolutionize many aspects of our lives, but their development must be pursued with a keen eye on safety. If you are developing these systems, you have a responsibility to the human race to exercise caution and minimize harm. These are crucial steps we must take in harnessing the benefits of what may be the most important technology we have ever created.

### Notes
[^1]: Bubeck, S., Chandrasekaran, V., Eldan, R., Gehrke, J., Horvitz, E., Kamar, E., ... & Zhang, Y. (2023). Sparks of artificial general intelligence: Early experiments with gpt-4. arXiv preprint arXiv:2303.12712
[^2]: Karnofsky, Holden. (2021). Forecasting Transformative AI, Part 1: What Kind of AI?
[^3]: The consensus definition of intelligence used in Microsoft research comes from this statement which was drafted in 1994. Includes signatures from expert academics from universities across the U.S. It should be noted that it was sent to 131 researchers described as "experts in intelligence and allied fields". Of these, 52 signed the statement, 48 returned the request with an explicit refusal to sign, and 31 ignored the request. In 1996 the president of the American Psychological Association claimed only 10 of the signatures where from actual intelligence experts. However, the statement contains many controversial claims and, in my view their definition of intelligence is the least of t "Intelligence is a very general mental capability that, among other things, involves the ability to reason, plan, solve problems, think abstractly, comprehend complex ideas, learn quickly and learn from experience. It is not merely book learning, a narrow academic skill, or test-taking smarts. Rather, it reflects a broader and deeper capability for comprehending our surroundings—"catching on," "making sense" of things, or "figuring out" what to do."
[^4]: A good post from Farnam Street on System 1 and System 2 thinking.
[^5]: Schick, T., Dwivedi-Yu, J., Dessì, R., Raileanu, R., Lomeli, M., Zettlemoyer, L., & Scialom, T. (2023). Toolformer: Language models can teach themselves to use tools. arXiv preprint arXiv:2302.04761.
[^6]: Boiko, D. A., MacKnight, R., & Gomes, G. (2023). Emergent autonomous scientific research capabilities of large language models. arXiv preprint arXiv:2304.05332.
[^7]: Overview of the AI alignment problem.
[^8]: Post on the implications of agents like AutoGPT.
[^9]: Post about forecasting AI science capabilities.