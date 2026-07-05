import re

from app.agents import build_search_agent, build_reader_agent,writer_chain, critic_chain


def _coerce_text(value) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        parts = [_coerce_text(item) for item in value]
        return "\n".join(part for part in parts if part)
    if isinstance(value, dict):
        for key in ("content", "text", "output", "message"):
            if key in value:
                return _coerce_text(value[key])
        return "\n".join(f"{key}: {_coerce_text(item)}" for key, item in value.items() if _coerce_text(item))
    return str(value)


def _extract_sources(search_result) -> list[str]:
    text_result = _coerce_text(search_result)
    urls = re.findall(r"^URL:\s*(\S+)", text_result, flags=re.MULTILINE)
    if not urls and isinstance(search_result, list):
        for item in search_result:
            if isinstance(item, dict):
                url = item.get("url") or item.get("link")
                if url:
                    urls.append(str(url))
    seen = set()
    sources = []
    for url in urls:
        if url not in seen:
            seen.add(url)
            sources.append(url)
    return sources


def _extract_bullets(section_text: str) -> list[str]:
    items = []
    for line in section_text.splitlines():
        stripped = line.strip()
        if stripped.startswith(("-", "*")):
            cleaned = stripped.lstrip("-* ").strip()
            cleaned = re.sub(r"\*\*(.*?)\*\*", r"\1", cleaned)
            if cleaned:
                items.append(cleaned)
    return items


def _extract_section_blocks(section_text: str) -> list[str]:
    blocks = []
    current_block = []

    for line in section_text.splitlines():
        stripped = line.strip()
        if not stripped or stripped == "---":
            continue

        is_heading = bool(re.match(r"^(#{2,6}\s+|\d+[.)]\s+|\*\*.*\*\*:?$)", stripped))
        if is_heading:
            cleaned_heading = re.sub(r"^#{2,6}\s*", "", stripped)
            cleaned_heading = re.sub(r"^\d+[.)]\s*", "", cleaned_heading)
            cleaned_heading = cleaned_heading.strip("* ")
            if current_block:
                blocks.append("\n".join(current_block).strip())
                current_block = []
            current_block.append(cleaned_heading)
            continue

        current_block.append(re.sub(r"\*\*(.*?)\*\*", r"\1", stripped))

    if current_block:
        blocks.append("\n".join(current_block).strip())

    return blocks


def _normalize_heading(line: str) -> str:
    cleaned = line.strip()
    cleaned = re.sub(r"^#+\s*", "", cleaned)
    cleaned = cleaned.strip("* ")
    cleaned = re.sub(r"^\d+[.)]\s*", "", cleaned)
    cleaned = re.sub(r"[^a-z0-9\s-]", "", cleaned.lower())
    return cleaned.lower()


def _extract_report_sections(report: str) -> dict:
    section_aliases = {
        "introduction": "introduction",
        "overview": "introduction",
        "background": "introduction",
        "key findings": "key_findings",
        "findings": "key_findings",
        "impact": "key_findings",
        "applications": "key_findings",
        "challenges": "key_findings",
        "future directions": "key_findings",
        "conclusion": "conclusion",
        "summary": "conclusion",
        "sources": "sources",
        "references": "sources",
    }
    sections = {"introduction": "", "key_findings": "", "conclusion": "", "sources": ""}
    current_key = None

    for line in report.splitlines():
        stripped = line.strip()
        normalized = _normalize_heading(stripped).rstrip(":")
        matched_key = None
        for alias, section_name in section_aliases.items():
            if normalized == alias or normalized.startswith(f"{alias} ") or alias in normalized:
                matched_key = section_name
                break
        if matched_key:
            current_key = matched_key
            continue
        if current_key:
            sections[current_key] = f"{sections[current_key]}\n{line}".strip()

    return {
        "introduction": sections["introduction"].strip(),
        "key_findings": _extract_section_blocks(sections["key_findings"]),
        "conclusion": sections["conclusion"].strip(),
        "sources_text": sections["sources"].strip(),
    }


def _extract_critic_sections(feedback: str) -> dict:
    score_match = re.search(r"Score:\s*(\d+)\s*/\s*10", feedback, flags=re.IGNORECASE)
    strengths_match = re.search(
        r"Strengths:\s*(.*?)(?:\n\s*Areas to Improve:|\n\s*One line verdict:|\Z)",
        feedback,
        flags=re.IGNORECASE | re.DOTALL,
    )
    improve_match = re.search(
        r"Areas to Improve:\s*(.*?)(?:\n\s*One line verdict:|\Z)",
        feedback,
        flags=re.IGNORECASE | re.DOTALL,
    )
    verdict_match = re.search(
        r"One line verdict:\s*(.*)",
        feedback,
        flags=re.IGNORECASE | re.DOTALL,
    )

    return {
        "score": int(score_match.group(1)) if score_match else None,
        "strengths": _extract_bullets(strengths_match.group(1)) if strengths_match else [],
        "areas_to_improve": _extract_bullets(improve_match.group(1)) if improve_match else [],
        "verdict": re.sub(r"\*\*(.*?)\*\*", r"\1", verdict_match.group(1).strip()) if verdict_match else re.sub(r"\*\*(.*?)\*\*", r"\1", feedback.strip()),
    }

def run_research_pipeline(topic : str)-> dict:

    state={}

    print("\n"+" ="*50)
    print("step 1 - search agent is working ...")
    print(" ="*50)
    search_agent = build_search_agent()
    search_result = search_agent.invoke({
          "messages" : [("user", f"Find recent, reliable and detailed information about: {topic}")]
    })

    state["search_result"] = search_result["messages"][-1].content
    state["search_result"] = _coerce_text(state["search_result"])
    state["sources"] = _extract_sources(state["search_result"])
    print("\n search result: \n", state["search_result"])
    print("\n"+" ="*50)
    #step 2 - reader agent 
    print("step 2 - reader agent is scraping top resources ...")
    print(" ="*50)
    reader_agent = build_reader_agent()
    reader_result = reader_agent.invoke({ "messages": [("user",
            f"Based on the following search results about '{topic}', "
            f"pick the most relevant URL and scrape it for deeper content.\n\n"
            f"Search Results:\n{state['search_result'][:800]}"
        )]
    })
    state["reader_result"] = reader_result["messages"][-1].content
    state["reader_result"] = _coerce_text(state["reader_result"])
    print("\n Scraped content: \n", state["reader_result"])
    print("\n"+" ="*50) 

    #step 3 - writer chain
    print("\n"+" ="*50)
    print("step 3 - writer chain is generating a research report ...")
    print("="*50)

    research_combined = (
        f"SEARCH RESULTS : \n {state['search_result']} \n\n"
        f"DETAILED SCRAPED CONTENT : \n {state['reader_result']}"
    )

    state["report"] = writer_chain.invoke({
        "topic" : topic,
        "research" : research_combined
    })
    state["report_sections"] = _extract_report_sections(state["report"])

    print("\n Final Report\n",state["report"])

    #critic report 

    print("\n"+" ="*50)
    print("step 4 - critic is reviewing the report ")
    print("="*50)

    state["feedback"] = critic_chain.invoke({
        "report":state["report"]
    })
    state["feedback_sections"] = _extract_critic_sections(state["feedback"])

    print("\n critic report \n", state['feedback'])

    return state



if __name__ == "__main__":
    topic = input("\n Enter a research topic : ")
    run_research_pipeline(topic)