> General comment:
> When using abbreviations stay consistement and use brackets. I see both brackets (e.g., Zero-Knowledge Proods (ZKP)) and commas (e.g., Self-Sovereign Identity, SSI, ...).

Fixed.

## Chapter 1

> I think the Description of Work is essentially the same as Thesis Outline sections. Not completely sure whether both sections are required, but it seems the outline is already provided in the Description of Work.

The thesis outline is used to simply outline the chapters and their topics, afaik.

## Chapter 2

> Smart Contracts - if you are not utilising them in anyway (which I'm not sure is true given DID management, such as revocations?), then I would possibly add a smaller paragraph instead to the 2.1.1 section. For examples: "Additionally, blockchains can facilitate automatic code execution based on predefined conditions through the use of Smart Contact." And maybe sentence or two about SC.
>
> In 2.2 I would add a statement that BC is a popoular for digital identity management because of so and so. And then I would go into details you already outlined.
>
> Also I'd keep only the Iedntity Management in the title of 2.2.

Makes sense, changed it.

> Are the concept in 2.2.3 relevant to your implementation, e.g., are you using ZKPs anywhere? If not, I would move this section into 2.2.1 as a continuation of discussion on VCs. Additionally, paragraph on SSI seems to be disconnected from everything else. I would also move it to 2.2.1 and say that SSI is a promising variation of digital identities that ensures data ownership by the user and removes third party data management.

I adjusted the sections, to mention where they are relevant (Hyperledger Aries)

> 2.3 section seems to be out of place after discussion of digital identities. I would add a short paragprah under the main Background title, outlining what is being discussed here and why it is important to the thesis.

> There's also no logical flow to the 2.4 section. First sentence should explain how this Physical Control Function fits within the architecture and it is needed in your case.

First sentence to the section? I made some remarks in the beginning of the chapter, although if you
think it makes sense to completely remove them, i could do that as well. In the end, we do not rely
on PUF in our implementation, nor the overall framework.

## Chapter 3

> Good to see some more related work.
>
> I would also add a clear problem statement (a problem that your research is trying to resolve) in the Chapter 1, otherwise it is not very clear what problem those solutions are trying to solve. Such sentence can start as: "In this research, we are aiming to ...". I think it best would fit in the Motivation sentence as the last part, as in the Description of Work you discuss how the problem is being addressed in your thesis.

Elaborated the first chapter to explain goals in more depth.

> Could of times you are comparing the existing solutions with the thesis in this chapter. I would suggest to remove that because related work section should serve as a foundation for your design, but you are implying that you already have a design and comparing it with other works (this is usually done somewhere in discussion or evaluation sections instead). In comparison, pointing why a solution might be limiting is a good things (such as in the IoTeX disucssion you ourline a shortcoming of that solution), but yet I would refrain the reference to the current thesis.

Will do!

> Some of the works relevance to your thesis problem is debatable. But I wouldn't probably focus attention on this now given your time limitations.
>
> I think Hyperledger section (3.1.1) belong in the Background chapter where you discuss blockchains, as it is a variation of blockchain. Similarly, section 3.2 is not a related work, but part of background (is there any specific reason you have placed it under the related work section?).

I thought that in the background section I should not be talking about specific implementations as
such, but I can gladly move them there!

> 3.3 generally is a good fit for related work section, however, MUD was previously discussed in background section. So I would move 3.3.1 and 3.3.2 under the Background, and focus 3.3 on existing solutions for security information sharing (e.g., what other platforms are out there). 3.4 is good too.

Moved MUD related sections into background.

## Chapter 4

> Did not read in details, but overall looks good.

## Chapter 5

> In the first paragraph, I would suggest adding a last sentence saying what the following sections describing. Such as "In the following sections, we discribe components of the architecture in more details". Othwerise, its not very clear whether those are components (sections 5.4.1 - 5.4.3). And possibly move 5.4.4 as another paragraph to the first paragraph. Follow the structure from general to specific: describe overall architecture -> describe contributing components in details.

Do you mean 5.4.4 as another paragraph to 5.4?

> Are Actors part of the architecture? If so, I would suggest the following structure:
> 5.4 Architecture\
> 5.4.1 Actors\
> 5.4.2 Software Components\
> 5.4.2.1 Configuration and Management DB\
> 5.4.2.2 Decentralised Identity Management Framework\
> 5.4.2.3 Secure Firmware Udate\
> 5.4.3 Hardware Components\
> 5.4.3.1 Controller Nodes\
> 5.4.3.2 Edge Nodes
>
> Then you can go into details about work flows (section 5.7). I would also rename that section to something like "Process Interactions" and possibly display few flow diagrams to illustrate the text better (but if you have time).

Should I create flow diagrams for the design specifically? I created Sequence Diagrams for the
implementation.

## Chapter 6

> You don't need to cover what is what again, outlining in one paragraph what (e.g., software like Docker, programming languages, environments, etc.) was used for the implementation is enough. Although it feels that Hyperledger should be rather discussed as part of the architecture desing, as I'm not sure that Orion, Indy and Aries can be labelled as tools (something to ask Bruno maybe?). But things like Aries Cloudagent Pythod is definately a tool. Overall, I would keep this section short and without subsections.
>
> Figure 6.1 belongs to the background knowledge on Hyperledger Orion. Which also means, you probably want to cover Orion in the background section.

Same question as before, unsure about explicit applications being mentioned in the background
section.

> I'm not quite clear on the 6.3.3 Node purpose. If it handles revocations, then its usually a credential issuer who should be doing that.

Maybe the wording was weird, but the responsibility is to handle, when a revocation happens, issued
by the issuer. rewrote this part.

> I'm also not very clear on the purpose of 6.3.1 section and would suggest moving it after discussion of Isuser, Auditor and Verifier, as it rather refers to a process.
>
> So I would suggest structure of this section as follows:
>
> 6.1 Tools\
> 6.2 Configuration and Mng DB\
> 6.2.1 Running on Orion Node\
> 6.3 Identity and Cred Mng\
> 6.3.1 Issuer\
> (6.3.2 Node)\
> 6.3.2 Auditor\
> 6.3.3 Verifier\
> 6.3.4 Running an Agent\
> 6.4 Networking\
> 6.5 Processes\
> 6.5.1 Onboarding\
> 6.5.2 Revocation\
> 6.5.3 Firmware updating

Done!
