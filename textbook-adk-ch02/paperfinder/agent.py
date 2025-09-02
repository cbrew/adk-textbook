from google.adk.agents import Agent, LlmAgent
from typing import Dict
from google.adk.models.lite_llm import LiteLlm


def search_semantic_scholar(query: str, field: str = "all") -> Dict[str, any]:
    """
    Searches Semantic Scholar for academic papers.

    Args:
        query: The search query (keywords, paper title, author name).
        field: The field to search in ("title", "author", "all").

    Returns:
        A dictionary with paper results including titles, authors, abstracts, and citation counts.
    """
    query_upper = query.upper()

    papers_db = {
        "MACHINE LEARNING": {
            "papers": [
                {
                    "title": "Deep Learning for Computer Vision: A Brief Review",
                    "authors": ["Li Zhang", "Sarah Chen", "Michael Rodriguez"],
                    "abstract": "This paper presents a comprehensive review of deep learning techniques applied to computer vision tasks, including image classification, object detection, and semantic segmentation.",
                    "year": 2023,
                    "citations": 1247,
                    "venue": "IEEE Transactions on Pattern Analysis and Machine Intelligence",
                    "url": "https://semantic-scholar.org/paper/12345",
                    "available": True
                },
                {
                    "title": "Attention Mechanisms in Neural Networks: A Survey",
                    "authors": ["Alex Thompson", "Maria Gonzalez"],
                    "abstract": "A comprehensive survey of attention mechanisms in deep neural networks, covering self-attention, cross-attention, and their applications in various domains.",
                    "year": 2022,
                    "citations": 892,
                    "venue": "Nature Machine Intelligence",
                    "url": "https://semantic-scholar.org/paper/67890",
                    "available": True
                }
            ]
        },
        "NATURAL LANGUAGE PROCESSING": {
            "papers": [
                {
                    "title": "Large Language Models: Capabilities and Limitations",
                    "authors": ["Emma Davis", "Robert Kim", "Jennifer Liu"],
                    "abstract": "An analysis of current large language models, examining their capabilities in various NLP tasks and discussing fundamental limitations.",
                    "year": 2024,
                    "citations": 523,
                    "venue": "Computational Linguistics",
                    "url": "https://semantic-scholar.org/paper/24680",
                    "available": True
                }
            ]
        },
        "TRANSFORMERS": {
            "papers": [
                {
                    "title": "Attention Is All You Need",
                    "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
                    "abstract": "We propose a new simple network architecture, the Transformer, based solely on attention mechanisms, dispensing with recurrence and convolutions entirely.",
                    "year": 2017,
                    "citations": 45891,
                    "venue": "Advances in Neural Information Processing Systems",
                    "url": "https://semantic-scholar.org/paper/transformer",
                    "available": True
                }
            ]
        }
    }

    for key, data in papers_db.items():
        if key in query_upper or any(word in query_upper for word in key.split()):
            return data

    return {
        "papers": [],
        "message": f"No papers found for query '{query}' in Semantic Scholar",
        "suggestion": "Try broader keywords or check spelling"
    }


def search_arxiv(query: str, category: str = "cs") -> Dict[str, any]:
    """
    Searches arXiv for preprints and recent research papers.

    Args:
        query: The search query (keywords, paper title, author name).
        category: The arXiv category (e.g., "cs", "cs.AI", "cs.LG", "cs.CL").

    Returns:
        A dictionary with arXiv paper results.
    """
    query_upper = query.upper()

    arxiv_papers = {
        "LARGE LANGUAGE": {
            "papers": [
                {
                    "title": "Constitutional AI: Harmlessness from AI Feedback",
                    "authors": ["Yuntao Bai", "Andy Jones", "Kamal Ndousse"],
                    "abstract": "We propose Constitutional AI (CAI), a method for training AI systems to be helpful, harmless, and honest using AI feedback rather than human feedback.",
                    "year": 2023,
                    "arxiv_id": "2212.08073",
                    "category": "cs.AI",
                    "url": "https://arxiv.org/abs/2212.08073",
                    "submitted": "2023-01-15",
                    "available": True
                }
            ]
        },
        "RETRIEVAL AUGMENTED": {
            "papers": [
                {
                    "title": "Retrieval-Augmented Generation for Knowledge-Intensive NLP Tasks",
                    "authors": ["Patrick Lewis", "Ethan Perez", "Aleksandra Piktus"],
                    "abstract": "Large pre-trained language models have been shown to store factual knowledge in their parameters. However, their ability to access and precisely manipulate knowledge is still limited.",
                    "year": 2020,
                    "arxiv_id": "2005.11401",
                    "category": "cs.CL",
                    "url": "https://arxiv.org/abs/2005.11401",
                    "submitted": "2020-05-22",
                    "available": True
                }
            ]
        }
    }

    for key, data in arxiv_papers.items():
        if key in query_upper or any(word in query_upper for word in key.split()):
            return data

    return {
        "papers": [],
        "message": f"No papers found for query '{query}' in arXiv category '{category}'",
        "suggestion": "Try different keywords or browse recent submissions"
    }


def search_acm_digital_library(query: str, publication_type: str = "all") -> Dict[str, any]:
    """
    Searches the ACM Digital Library for computer science papers.

    Args:
        query: The search query (keywords, paper title, author name).
        publication_type: Type of publication ("conference", "journal", "all").

    Returns:
        A dictionary with ACM paper results.
    """
    query_upper = query.upper()

    acm_papers = {
        "HUMAN COMPUTER INTERACTION": {
            "papers": [
                {
                    "title": "The Design of Everyday Things in the Digital Age",
                    "authors": ["Donald Norman", "Sarah Johnson"],
                    "abstract": "An examination of design principles for digital interfaces, building on classic HCI principles for modern applications.",
                    "year": 2023,
                    "venue": "CHI '23: Proceedings of the 2023 CHI Conference on Human Factors in Computing Systems",
                    "doi": "10.1145/3544548.3581234",
                    "pages": "1-14",
                    "type": "conference",
                    "available": True
                }
            ]
        },
        "INFORMATION RETRIEVAL": {
            "papers": [
                {
                    "title": "Neural Information Retrieval: Progress and Challenges",
                    "authors": ["Zhuyun Dai", "Jamie Callan"],
                    "abstract": "A comprehensive review of neural approaches to information retrieval, covering dense retrieval, sparse retrieval, and hybrid methods.",
                    "year": 2022,
                    "venue": "ACM Computing Surveys",
                    "doi": "10.1145/3469877",
                    "pages": "1-35",
                    "type": "journal",
                    "available": True
                }
            ]
        }
    }

    for key, data in acm_papers.items():
        if key in query_upper or any(word in query_upper for word in key.split()):
            return data

    return {
        "papers": [],
        "message": f"No papers found for query '{query}' in ACM Digital Library",
        "suggestion": "Try broader computer science terms or specific venue names"
    }


def search_acl_anthology(query: str, venue: str = "all") -> Dict[str, any]:
    """
    Searches the ACL Anthology for computational linguistics and NLP papers.

    Args:
        query: The search query (keywords, paper title, author name).
        venue: The venue to search in ("ACL", "EMNLP", "NAACL", "COLING", "all").

    Returns:
        A dictionary with ACL Anthology paper results.
    """
    query_upper = query.upper()

    acl_papers = {
        "SENTIMENT ANALYSIS": {
            "papers": [
                {
                    "title": "BERT for Sentiment Analysis: A Comparative Study",
                    "authors": ["Rachel Green", "David Wilson", "Anna Martinez"],
                    "abstract": "We present a comprehensive comparison of BERT-based models for sentiment analysis across multiple domains and languages.",
                    "year": 2023,
                    "venue": "ACL 2023",
                    "anthology_id": "2023.acl-long.123",
                    "pages": "1234-1245",
                    "url": "https://aclanthology.org/2023.acl-long.123",
                    "available": True
                }
            ]
        },
        "MACHINE TRANSLATION": {
            "papers": [
                {
                    "title": "Low-Resource Neural Machine Translation: A Survey",
                    "authors": ["Kevin Brown", "Lisa Zhang", "Carlos Rodriguez"],
                    "abstract": "A survey of techniques for improving neural machine translation in low-resource language pairs, including transfer learning and data augmentation methods.",
                    "year": 2022,
                    "venue": "EMNLP 2022",
                    "anthology_id": "2022.emnlp-main.456",
                    "pages": "5678-5692",
                    "url": "https://aclanthology.org/2022.emnlp-main.456",
                    "available": True
                }
            ]
        }
    }

    for key, data in acl_papers.items():
        if key in query_upper or any(word in query_upper for word in key.split()):
            return data

    return {
        "papers": [],
        "message": f"No papers found for query '{query}' in ACL Anthology",
        "suggestion": "Try NLP-specific terms or author names from the computational linguistics community"
    }


def search_osu_digital_collections(query: str, collection: str = "all") -> Dict[str, any]:
    """
    Searches OSU's digital collections and institutional repository.

    Args:
        query: The search query (keywords, paper title, author name).
        collection: The collection to search ("theses", "faculty_pubs", "all").

    Returns:
        A dictionary with OSU digital collection results.
    """
    query_upper = query.upper()

    osu_papers = {
        "ARTIFICIAL INTELLIGENCE": {
            "papers": [
                {
                    "title": "Explainable AI in Healthcare: A Case Study at OSU Medical Center",
                    "authors": ["John Smith", "Mary Johnson"],
                    "abstract": "This dissertation examines the implementation of explainable AI techniques in healthcare decision support systems at The Ohio State University Medical Center.",
                    "year": 2023,
                    "type": "PhD Dissertation",
                    "department": "Computer Science and Engineering",
                    "advisor": "Dr. Alan Ritter",
                    "url": "https://etd.ohiolink.edu/pg_123456",
                    "pages": 187,
                    "available": True
                }
            ]
        },
        "COMPUTER VISION": {
            "papers": [
                {
                    "title": "Deep Learning Approaches for Medical Image Analysis",
                    "authors": ["Jennifer Lee"],
                    "abstract": "Faculty publication examining state-of-the-art deep learning methods for analyzing medical images, with applications to radiology and pathology.",
                    "year": 2024,
                    "type": "Faculty Publication",
                    "department": "Biomedical Informatics",
                    "journal": "OSU Medical Research Quarterly",
                    "url": "https://kb.osu.edu/handle/1811/98765",
                    "pages": "45-62",
                    "available": True
                }
            ]
        }
    }

    for key, data in osu_papers.items():
        if key in query_upper or any(word in query_upper for word in key.split()):
            return data

    return {
        "papers": [],
        "message": f"No papers found for query '{query}' in OSU Digital Collections",
        "suggestion": "Try searching for OSU faculty names or browse by department"
    }


def visit_osu_library(query: str, assistance_type: str = "research") -> Dict[str, any]:
    """
    Get assistance from OSU Libraries for specialized research needs.

    Args:
        query: The research topic or specific assistance needed.
        assistance_type: Type of assistance needed ("research", "database_access", "interlibrary_loan").

    Returns:
        A dictionary with library service information and recommendations.
    """
    services = {
        "research": {
            "service_name": "Research Consultation",
            "location": "Thompson Library, 2nd Floor Research Help Desk",
            "contact": {
                "phone": "(614) 292-6151",
                "email": "library@osu.edu",
                "chat": "Available 24/7 online"
            },
            "what_to_expect": [
                "One-on-one consultation with subject librarian",
                "Help developing search strategies",
                "Access to specialized databases",
                "Guidance on citation management"
            ],
            "hours": "Mon-Thu: 8am-2am, Fri: 8am-9pm, Sat: 9am-9pm, Sun: 11am-2am",
            "best_for": "Complex research questions requiring specialized databases or expert guidance"
        },
        "database_access": {
            "service_name": "Database Access & Training",
            "location": "Any OSU Library location or online",
            "contact": {
                "phone": "(614) 292-6151",
                "url": "https://library.osu.edu/databases"
            },
            "databases_available": [
                "Web of Science - Citation analysis and discovery",
                "Scopus - Abstract and citation database", 
                "IEEE Xplore - Engineering and technology",
                "PsycINFO - Psychology and behavioral sciences",
                "MathSciNet - Mathematics research"
            ],
            "training_available": "Group workshops and individual training sessions",
            "best_for": "Accessing subscription databases not available through free sources"
        },
        "interlibrary_loan": {
            "service_name": "OhioLINK & Interlibrary Loan",
            "location": "Online request system",
            "contact": {
                "url": "https://library.osu.edu/ill",
                "email": "ill@osu.edu"
            },
            "what_to_expect": [
                "Access to materials from other Ohio universities",
                "Worldwide interlibrary loan requests",
                "Digital delivery when possible",
                "Physical item pickup at OSU libraries"
            ],
            "turnaround_time": "3-10 business days for most requests",
            "cost": "Free for OSU students, staff, and faculty",
            "best_for": "Papers and books not available in OSU collections or online"
        }
    }

    service = services.get(assistance_type, services["research"])
    
    return {
        "query": query,
        "recommended_service": service,
        "next_steps": [
            f"Contact {service['service_name']} using the information above",
            "Prepare your research question and any specific requirements",
            "Bring your BuckID for library access"
        ],
        "additional_tip": "OSU Libraries also provide access to research guides for specific subjects at https://guides.osu.edu"
    }


agent_instruction = """
You are an academic paper finder agent for researchers and students. 📚🎓 Your job is to help users find academic papers and research materials using the most appropriate sources.

---

### **Workflow**

**STEP 1: UNDERSTAND THE REQUEST**
* Extract the research topic, paper title, author name, or specific research question from the user's request.
* If the user's request is too broad, ask for more specific details about their research focus.

**STEP 2: SEARCH ACADEMIC SOURCES (IN PRIORITY ORDER)**
1. **Check Semantic Scholar First:** Use `search_semantic_scholar` for comprehensive academic paper discovery.
   - Best for: General academic search, citation counts, and finding highly-cited papers
   - Covers: All academic disciplines with rich metadata
   
2. **Search arXiv for Preprints:** Use `search_arxiv` to find the latest research and preprints.
   - Best for: Cutting-edge research, computer science, physics, mathematics
   - Categories: cs.AI, cs.LG, cs.CL, etc.
   
3. **Check Specialized Databases:** Depending on the field:
   - **ACM Digital Library** (`search_acm_digital_library`) for computer science research
   - **ACL Anthology** (`search_acl_anthology`) for computational linguistics and NLP
   
4. **Search OSU Digital Collections:** Use `search_osu_digital_collections` for institutional research.
   - Best for: Local expertise, theses, dissertations, faculty publications
   
5. **Visit OSU Library:** Use `visit_osu_library` for specialized assistance or hard-to-find materials.
   - Best for: Database access, research consultations, interlibrary loans

**STEP 3: PRESENT THE RESULTS**
* Clearly present the most relevant papers found.
* Include key details: title, authors, year, venue, citation count (if available).
* Provide abstracts for the most promising papers.
* If no papers are found, suggest alternative search strategies or broader/narrower terms.
* Always prioritize academic quality and relevance over quantity.

---

### **Available Tools**
* `search_semantic_scholar` - Comprehensive academic database search
* `search_arxiv` - Preprints and latest research
* `search_acm_digital_library` - Computer science papers and conferences
* `search_acl_anthology` - Computational linguistics and NLP papers
* `search_osu_digital_collections` - OSU institutional repository
* `visit_osu_library` - Specialized library services and assistance

---

### **Special Instructions**
* **Be thorough and systematic** in your search approach.
* **Prioritize peer-reviewed sources** but include preprints when they're cutting-edge.
* **Provide abstracts** to help users understand paper relevance.
* **Include practical access information** (URLs, DOIs, library locations).
* **Be scholarly but approachable** in your responses. 🔬📖
"""


agent_claude_direct = LlmAgent(
    model=LiteLlm(model="anthropic/claude-3-haiku-20240307"),
    name="claude_direct_agent",
    instruction=agent_instruction,
    tools=[
        search_semantic_scholar,
        search_arxiv,
        search_acm_digital_library,
        search_acl_anthology,
        search_osu_digital_collections,
        visit_osu_library,
    ]
)


agent = Agent(
    model="gemini-2.5-flash",
    # model="anthropic/claude-3-5-haiku-latest",
    name="paper_finder",
    instruction=agent_instruction,
    tools=[
        search_semantic_scholar,
        search_arxiv,
        search_acm_digital_library,
        search_acl_anthology,
        search_osu_digital_collections,
        visit_osu_library,
    ],
)

root_agent = agent_claude_direct